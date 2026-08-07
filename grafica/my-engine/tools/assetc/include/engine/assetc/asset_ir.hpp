#pragma once
#include <cstdint>
#include <string>
#include <utility>
#include <vector>

namespace engine::assetc {

// Nó do Asset IR (RFC 02): saída de um front-end, antes do linker de
// assets. Independente do formato de origem.
struct AssetIRNode {
    std::string id;
    std::string type;
    std::string source_path;         // metadado de origem (rastreabilidade)
    std::uint64_t content_hash = 0;  // hash do arquivo fonte + parâmetros do manifesto
    std::vector<std::string> dependencies;

    // Metadados estruturados do asset (ex.: width/height/channels de uma
    // imagem) — front-ends de agregação, como o atlas, leem os metadados
    // das suas dependências através do FrontendContext (frontend.hpp).
    std::vector<std::pair<std::string, std::string>> metadata;

    std::vector<unsigned char> payload;

    std::string get(const std::string& key, const std::string& fallback = "") const {
        for (const auto& [k, v] : metadata) {
            if (k == key) return v;
        }
        return fallback;
    }
};

} // namespace engine::assetc
