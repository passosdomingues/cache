#include "engine/assetc/asset_manifest.hpp"
#include "engine/assetc/block_format.hpp"
#include "engine/platform/filesystem.hpp"

#include <sstream>
#include <stdexcept>

namespace engine::assetc {

namespace {
std::vector<std::string> split_csv(const std::string& value) {
    std::vector<std::string> parts;
    std::istringstream stream(value);
    std::string item;
    while (std::getline(stream, item, ',')) {
        auto start = item.find_first_not_of(" \t");
        if (start == std::string::npos) continue;
        auto end = item.find_last_not_of(" \t");
        parts.push_back(item.substr(start, end - start + 1));
    }
    return parts;
}
} // namespace

AssetManifest parse_manifest(const std::string& content, const std::filesystem::path& base_dir) {
    AssetManifest manifest;
    for (const auto& block : parse_blocks(content)) {
        SourceAsset asset;
        asset.id = block.name;
        asset.type = block.get("type", "raw");
        std::string path_str = block.get("path");
        if (path_str.empty()) {
            throw std::runtime_error("asset '" + asset.id + "' sem campo 'path'");
        }
        asset.source_path = base_dir / path_str;
        std::string deps = block.get("depends");
        if (!deps.empty()) {
            asset.dependencies = split_csv(deps);
        }
        manifest.assets.push_back(std::move(asset));
    }
    return manifest;
}

AssetManifest load_manifest(const std::filesystem::path& manifest_path) {
    auto content = platform::fs::read_text_file(manifest_path);
    if (!content) {
        throw std::runtime_error("nao foi possivel ler o manifesto: " + manifest_path.string());
    }
    return parse_manifest(*content, manifest_path.parent_path());
}

} // namespace engine::assetc
