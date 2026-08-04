#pragma once
#include <cstdint>
#include <string>
#include <vector>

namespace engine::assetc {

// Nó do Asset IR (RFC 02): saída de um front-end, antes do linker de
// assets. Independente do formato de origem.
struct AssetIRNode {
    std::string id;
    std::string type;
    std::string source_path;        // metadado de origem (rastreabilidade)
    std::uint64_t content_hash = 0;  // hash do arquivo fonte
    std::vector<std::string> dependencies;
    std::vector<unsigned char> payload;
};

} // namespace engine::assetc
