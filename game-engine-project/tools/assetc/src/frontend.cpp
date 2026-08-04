#include "engine/assetc/frontend.hpp"
#include "engine/platform/filesystem.hpp"

#include <stdexcept>

namespace engine::assetc {

namespace {
AssetIRNode compile_raw(const SourceAsset& asset) {
    auto content = platform::fs::read_text_file(asset.source_path);
    if (!content) {
        throw std::runtime_error("asset '" + asset.id + "': nao foi possivel ler " + asset.source_path.string());
    }
    AssetIRNode node;
    node.id = asset.id;
    node.type = asset.type;
    node.source_path = asset.source_path.string();
    node.dependencies = asset.dependencies;
    node.payload.assign(content->begin(), content->end());
    return node;
}
} // namespace

FrontendRegistry& FrontendRegistry::instance() {
    static FrontendRegistry registry;
    return registry;
}

FrontendRegistry::FrontendRegistry() {
    // Front-end "raw": copia o arquivo fonte para o IR sem transformação.
    // Front-ends de Image (Sprint 4) e Audio (Sprint 5) se registram aqui
    // do mesmo jeito, sem o núcleo do asset compiler precisar mudar.
    register_frontend("raw", FrontendInfo{compile_raw, 1});
}

void FrontendRegistry::register_frontend(const std::string& type, FrontendInfo info) {
    frontends_[type] = std::move(info);
}

const FrontendInfo* FrontendRegistry::find(const std::string& type) const {
    auto it = frontends_.find(type);
    return it == frontends_.end() ? nullptr : &it->second;
}

} // namespace engine::assetc
