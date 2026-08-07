#pragma once
#include <filesystem>
#include <string>
#include <utility>
#include <vector>

namespace engine::assetc {

// Descreve um asset fonte a compilar. Corresponde à entrada da etapa de
// front-end do RFC 02 — cada SourceAsset vira um nó do Asset IR.
struct SourceAsset {
    std::string id;
    std::string type;                       // ex.: "raw", "image", "atlas"
    std::filesystem::path source_path;      // pode ser vazio para tipos que não lêem um arquivo fonte direto (ex.: atlas)
    std::vector<std::string> dependencies;  // ids de outros SourceAsset no mesmo manifesto

    // Demais campos do bloco, além de type/path/depends — ex.: resize=,
    // crop=, pad=, max_width=, padding=, mips=. Cada front-end decide
    // quais parâmetros lê.
    std::vector<std::pair<std::string, std::string>> params;

    std::string param(const std::string& key, const std::string& fallback = "") const {
        for (const auto& [k, v] : params) {
            if (k == key) return v;
        }
        return fallback;
    }
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
