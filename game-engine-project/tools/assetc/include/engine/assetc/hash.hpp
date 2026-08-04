#pragma once
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <string>
#include <string_view>

namespace engine::assetc {

// FNV-1a 64 bits — hash de conteúdo simples, determinístico e sem
// dependências externas. Suficiente para endereçamento de cache de build
// (RFC 02 — "cache por hash de conteúdo"); não é criptográfico, não usar
// para verificação de integridade contra adulteração maliciosa.
std::uint64_t fnv1a_64(const void* data, std::size_t size);
std::uint64_t fnv1a_64(std::string_view data);

// Lê o arquivo inteiro e calcula o hash do conteúdo. Retorna 0 se o
// arquivo não puder ser lido (chamador deve validar existência antes).
std::uint64_t hash_file(const std::filesystem::path& path);

std::string to_hex(std::uint64_t value);

} // namespace engine::assetc
