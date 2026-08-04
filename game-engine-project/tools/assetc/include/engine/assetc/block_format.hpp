#pragma once
#include <string>
#include <utility>
#include <vector>

namespace engine::assetc {

// Formato de texto simples em blocos:
//   [nome]
//   chave=valor
//   outra_chave=outro_valor
//
// Usado tanto para o manifesto de build (o que compilar, escrito à mão)
// quanto para o manifesto de cache (o que já foi compilado — RFC 02,
// seção "Cache e build incremental").
struct Block {
    std::string name;
    std::vector<std::pair<std::string, std::string>> fields; // preserva ordem

    std::string get(const std::string& key, const std::string& fallback = "") const;
};

std::vector<Block> parse_blocks(const std::string& content);
std::string serialize_blocks(const std::vector<Block>& blocks);

} // namespace engine::assetc
