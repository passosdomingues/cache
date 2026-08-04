#pragma once
#include "engine/assetc/asset_manifest.hpp"

#include <filesystem>
#include <vector>

namespace engine::assetc {

struct BuildStats {
    int total = 0;
    int cache_hits = 0;
    int compiled = 0;
};

struct BuildOptions {
    std::filesystem::path manifest_path;
    std::filesystem::path output_path;
    std::filesystem::path cache_dir = ".assetc-cache";
    bool force = false; // ignora o cache, recompila tudo
};

// Ordena os assets do manifesto topologicamente (dependências antes de
// quem depende delas) e detecta ciclos. Lança std::runtime_error em caso
// de dependência desconhecida ou ciclo.
std::vector<SourceAsset> topological_order(const AssetManifest& manifest);

// Executa o pipeline completo: manifesto -> front-ends (com cache
// incremental, propagando invalidação pelo grafo de dependências) ->
// game.pkg. Retorna estatísticas do build.
BuildStats build(const BuildOptions& options);

} // namespace engine::assetc
