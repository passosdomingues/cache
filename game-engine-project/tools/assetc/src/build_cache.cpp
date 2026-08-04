#include "engine/assetc/build_cache.hpp"
#include "engine/assetc/block_format.hpp"
#include "engine/assetc/hash.hpp"
#include "engine/platform/filesystem.hpp"

#include <algorithm>
#include <sstream>

namespace engine::assetc {

namespace {
std::string join_csv(const std::vector<std::string>& items) {
    std::string out;
    for (std::size_t i = 0; i < items.size(); ++i) {
        if (i > 0) out += ",";
        out += items[i];
    }
    return out;
}

std::vector<std::string> split_csv_simple(const std::string& value) {
    std::vector<std::string> parts;
    std::istringstream stream(value);
    std::string item;
    while (std::getline(stream, item, ',')) {
        if (!item.empty()) parts.push_back(item);
    }
    return parts;
}
} // namespace

BuildCache::BuildCache(std::filesystem::path cache_dir) : cache_dir_(std::move(cache_dir)) {}

void BuildCache::load() {
    entries_.clear();
    auto manifest_path = cache_dir_ / "manifest.txt";
    auto content = platform::fs::read_text_file(manifest_path);
    if (!content) return; // primeiro build: ainda não há cache

    for (const auto& block : parse_blocks(*content)) {
        CacheEntry entry;
        entry.type = block.get("type");
        entry.source_path = block.get("source");
        entry.source_hash = std::stoull(block.get("source_hash", "0"), nullptr, 16);
        entry.frontend = block.get("frontend");
        entry.dependencies = split_csv_simple(block.get("dependencies"));
        entry.output_hash = std::stoull(block.get("output_hash", "0"), nullptr, 16);
        entries_[block.name] = std::move(entry);
    }
}

void BuildCache::save() const {
    std::vector<std::string> ids;
    ids.reserve(entries_.size());
    for (const auto& [id, entry] : entries_) ids.push_back(id);
    std::sort(ids.begin(), ids.end()); // saída estável, boa para diffs humanos

    std::vector<Block> blocks;
    blocks.reserve(ids.size());
    for (const auto& id : ids) {
        const auto& entry = entries_.at(id);
        Block block;
        block.name = id;
        block.fields = {
            {"type", entry.type},
            {"source", entry.source_path},
            {"source_hash", to_hex(entry.source_hash)},
            {"frontend", entry.frontend},
            {"dependencies", join_csv(entry.dependencies)},
            {"output_hash", to_hex(entry.output_hash)},
        };
        blocks.push_back(std::move(block));
    }
    platform::fs::write_text_file(cache_dir_ / "manifest.txt", serialize_blocks(blocks));
}

const CacheEntry* BuildCache::find(const std::string& asset_id) const {
    auto it = entries_.find(asset_id);
    return it == entries_.end() ? nullptr : &it->second;
}

void BuildCache::put(const std::string& asset_id, CacheEntry entry) {
    entries_[asset_id] = std::move(entry);
}

std::optional<std::vector<unsigned char>> BuildCache::load_object(std::uint64_t hash) const {
    auto path = cache_dir_ / "objects" / to_hex(hash);
    auto content = platform::fs::read_text_file(path);
    if (!content) return std::nullopt;
    return std::vector<unsigned char>(content->begin(), content->end());
}

void BuildCache::store_object(std::uint64_t hash, const std::vector<unsigned char>& payload) const {
    auto path = cache_dir_ / "objects" / to_hex(hash);
    std::string content(payload.begin(), payload.end());
    platform::fs::write_text_file(path, content);
}

} // namespace engine::assetc
