#pragma once
#include <filesystem>
#include <string>
#include <vector>

namespace engine::assetc {

// Descreve um asset fonte a compilar. Corresponde à entrada da etapa de
// front-end do RFC 02 — cada SourceAsset vira um nó do Asset IR.
struct SourceAsset {
    std::string id;
    std::string type;                       // ex.: "raw" (Sprint 3); "image"/"audio" em sprints futuros
    std::filesystem::path source_path;
    std::vector<std::string> dependencies;  // ids de outros SourceAsset no mesmo manifesto
};

struct AssetManifest {
    std::vector<SourceAsset> assets;
};

// Formato do manifesto (block_format.hpp):
//   [id_do_asset]
//   type=raw
//   path=assets/arquivo.bin
//   depends=outro_id,mais_um_id
AssetManifest parse_manifest(const std::string& content, const std::filesystem::path& base_dir);
AssetManifest load_manifest(const std::filesystem::path& manifest_path);

} // namespace engine::assetc
