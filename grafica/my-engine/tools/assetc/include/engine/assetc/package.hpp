#pragma once
#include "engine/assetc/asset_ir.hpp"

#include <cstdint>
#include <filesystem>
#include <string>
#include <utility>
#include <vector>

namespace engine::assetc {

// Formato binário de game.pkg v2 (RFC 02 — "Linker de Assets"):
//   header: magic "ASSETPK2" (8 bytes) + asset_count (u32)
//   tabela: por asset -> id, type, source_path, content_hash,
//           dependências (índices na própria tabela), metadados
//           (pares chave/valor), offset/size do payload
//   blobs: payload de cada asset, nessa ordem
//
// Determinístico por construção: sem timestamps embutidos — mesma
// entrada (mesma ordem + mesmos bytes) sempre produz a mesma saída,
// byte a byte (RFC 00, princípio de builds determinísticos).
void write_package(const std::filesystem::path& out_path, const std::vector<AssetIRNode>& nodes);

struct PackageAssetInfo {
    std::string id;
    std::string type;
    std::string source_path;
    std::uint64_t content_hash = 0;
    std::vector<std::string> dependencies;
    std::vector<std::pair<std::string, std::string>> metadata;
    std::uint64_t payload_size = 0;
};

struct PackageInfo {
    std::vector<PackageAssetInfo> assets;
};

// Lê apenas os metadados do pacote (não carrega os blobs) — usado por
// `assetc inspect` e pelo futuro Package Viewer (Sprint 22).
PackageInfo read_package_info(const std::filesystem::path& path);

// Lê o payload (blob) de um único asset pelo id. Usado por ferramentas
// que precisam do conteúdo real (ex.: um futuro Asset Inspector visual,
// ou os testes automatizados que verificam pixels do atlas).
std::vector<unsigned char> read_package_payload(const std::filesystem::path& path, const std::string& asset_id);

} // namespace engine::assetc
