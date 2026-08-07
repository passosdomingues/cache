#include "engine/resources/resource_manager.hpp"
#include "engine/pkg/compression.hpp"

#include <stdexcept>

namespace engine::resources {

ResourceManager::ResourceManager(std::filesystem::path package_path, jobs::JobSystem* job_system)
    : package_path_(std::move(package_path)), job_system_(job_system) {
    load_package();
}

void ResourceManager::load_package() {
    pkg::PackageInfo info = pkg::read_package_info(package_path_);

    platform::ScopedLock lock(mutex_);
    for (auto& asset : info.assets) {
        auto it = index_by_id_.find(asset.id);
        if (it == index_by_id_.end()) {
            Slot slot;
            slot.id = asset.id;
            slot.generation = 1;
            slot.info = asset;
            index_by_id_[asset.id] = static_cast<std::uint32_t>(slots_.size());
            slots_.push_back(std::move(slot));
        } else {
            // Recurso já conhecido: atualiza a metadata, mas não mexe em
            // residência/refcount aqui — isso é responsabilidade de
            // poll_hot_reload() para recursos já residentes.
            slots_[it->second].info = asset;
        }
    }
}

std::vector<std::string> ResourceManager::asset_ids() const {
    platform::ScopedLock lock(mutex_);
    std::vector<std::string> ids;
    ids.reserve(slots_.size());
    for (const auto& slot : slots_) {
        ids.push_back(slot.id);
    }
    return ids;
}

std::vector<unsigned char> ResourceManager::load_and_decompress(const pkg::PackageAssetInfo& info) const {
    auto raw = pkg::read_package_payload(package_path_, info.id);

    std::string uncompressed_size_str = info.get("uncompressed_size");
    if (uncompressed_size_str.empty()) {
        // Assets sem essa metadata (ex.: front-end "raw", Sprint 3) não
        // são comprimidos pelo asset compiler — payload já é o final.
        return raw;
    }

    std::size_t uncompressed_size = static_cast<std::size_t>(std::stoull(uncompressed_size_str));
    return pkg::inflate_decompress(raw, uncompressed_size);
}

ResourceHandle ResourceManager::acquire(const std::string& asset_id) {
    platform::ScopedLock lock(mutex_);
    auto it = index_by_id_.find(asset_id);
    if (it == index_by_id_.end()) {
        return kInvalidHandle;
    }

    Slot& slot = slots_[it->second];
    ++slot.ref_count;
    if (!slot.resident) {
        // Nota: a descompressão roda com o mutex retido (ver comentário
        // de thread-safety no header) — simplicidade em vez de paralelismo
        // fino entre acquires concorrentes de assets diferentes.
        slot.bytes = load_and_decompress(slot.info);
        slot.resident = true;
    }

    return ResourceHandle{it->second, slot.generation};
}

jobs::Future<ResourceHandle> ResourceManager::acquire_async(const std::string& asset_id) {
    if (!job_system_) {
        throw std::runtime_error("ResourceManager::acquire_async requer um JobSystem valido");
    }
    return job_system_->submit_with_result(
        [this, asset_id](jobs::CancellationToken&) { return acquire(asset_id); });
}

void ResourceManager::release(ResourceHandle handle) {
    platform::ScopedLock lock(mutex_);
    Slot* slot = find_slot_unlocked(handle);
    if (!slot) return;

    if (slot->ref_count > 0) {
        --slot->ref_count;
    }
    if (slot->ref_count == 0 && slot->resident) {
        slot->bytes.clear();
        slot->bytes.shrink_to_fit();
        slot->resident = false;
    }
}

ResourceManager::Slot* ResourceManager::find_slot_unlocked(ResourceHandle handle) {
    if (!handle.valid() || handle.index >= slots_.size()) return nullptr;
    Slot& slot = slots_[handle.index];
    if (slot.generation != handle.generation) return nullptr; // handle stale
    return &slot;
}

const ResourceManager::Slot* ResourceManager::find_slot_unlocked(ResourceHandle handle) const {
    return const_cast<ResourceManager*>(this)->find_slot_unlocked(handle);
}

bool ResourceManager::is_resident(ResourceHandle handle) const {
    platform::ScopedLock lock(mutex_);
    const Slot* slot = find_slot_unlocked(handle);
    return slot && slot->resident;
}

int ResourceManager::ref_count(ResourceHandle handle) const {
    platform::ScopedLock lock(mutex_);
    const Slot* slot = find_slot_unlocked(handle);
    return slot ? slot->ref_count : 0;
}

const std::vector<unsigned char>* ResourceManager::data(ResourceHandle handle) const {
    platform::ScopedLock lock(mutex_);
    const Slot* slot = find_slot_unlocked(handle);
    if (!slot || !slot->resident) return nullptr;
    return &slot->bytes;
}

std::string ResourceManager::type_of(ResourceHandle handle) const {
    platform::ScopedLock lock(mutex_);
    const Slot* slot = find_slot_unlocked(handle);
    return slot ? slot->info.type : std::string();
}

std::string ResourceManager::metadata(ResourceHandle handle, const std::string& key, const std::string& fallback) const {
    platform::ScopedLock lock(mutex_);
    const Slot* slot = find_slot_unlocked(handle);
    return slot ? slot->info.get(key, fallback) : fallback;
}

int ResourceManager::poll_hot_reload() {
    pkg::PackageInfo fresh = pkg::read_package_info(package_path_);

    platform::ScopedLock lock(mutex_);
    int reloaded = 0;

    for (auto& asset : fresh.assets) {
        auto it = index_by_id_.find(asset.id);
        if (it == index_by_id_.end()) {
            // Asset novo desde o último load — registra o slot, mas não
            // carrega o payload (streaming: só no próximo acquire()).
            Slot slot;
            slot.id = asset.id;
            slot.generation = 1;
            slot.info = asset;
            index_by_id_[asset.id] = static_cast<std::uint32_t>(slots_.size());
            slots_.push_back(std::move(slot));
            continue;
        }

        Slot& slot = slots_[it->second];
        if (slot.resident && slot.info.content_hash != asset.content_hash) {
            slot.info = asset;
            slot.bytes = load_and_decompress(slot.info);
            ++reloaded;
        } else {
            slot.info = asset; // atualiza metadata mesmo sem estar residente
        }
    }

    return reloaded;
}

} // namespace engine::resources
