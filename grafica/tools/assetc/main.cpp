#include "engine/assetc/compiler.hpp"
#include "engine/assetc/hash.hpp"
#include "engine/assetc/package.hpp"
#include "engine/platform/cli.hpp"

#include <cstdio>
#include <exception>
#include <string>

using namespace engine;

namespace {

int run_build(const platform::CommandLineParser& args) {
    auto manifest = args.get_option("manifest");
    auto out = args.get_option("out");
    if (!manifest || !out) {
        std::fprintf(stderr,
            "uso: assetc build --manifest=<arquivo> --out=<pacote.pkg> [--cache=<dir>] [--force]\n");
        return 2;
    }

    assetc::BuildOptions options;
    options.manifest_path = *manifest;
    options.output_path = *out;
    options.cache_dir = args.get_option("cache", ".assetc-cache");
    options.force = args.has_flag("force");

    auto stats = assetc::build(options);
    std::printf("assetc build: %d assets (%d do cache, %d compilados) -> %s\n",
                stats.total, stats.cache_hits, stats.compiled, options.output_path.c_str());
    return 0;
}

int run_inspect(const platform::CommandLineParser& args) {
    const auto& positional = args.positional_args();
    if (positional.empty()) {
        std::fprintf(stderr, "uso: assetc inspect <pacote.pkg>\n");
        return 2;
    }

    auto info = assetc::read_package_info(positional.front());
    std::printf("%-24s %-10s %-16s %10s  origem\n", "id", "tipo", "hash", "bytes");
    for (const auto& asset : info.assets) {
        std::printf("%-24s %-10s %-16s %10llu  %s\n",
                     asset.id.c_str(), asset.type.c_str(),
                     assetc::to_hex(asset.content_hash).c_str(),
                     static_cast<unsigned long long>(asset.payload_size),
                     asset.source_path.c_str());
        if (!asset.dependencies.empty()) {
            std::printf("  depende de: ");
            for (std::size_t i = 0; i < asset.dependencies.size(); ++i) {
                std::printf("%s%s", asset.dependencies[i].c_str(),
                            i + 1 < asset.dependencies.size() ? ", " : "");
            }
            std::printf("\n");
        }
        if (!asset.metadata.empty()) {
            std::printf("  metadata: ");
            for (std::size_t i = 0; i < asset.metadata.size(); ++i) {
                std::printf("%s=%s%s", asset.metadata[i].first.c_str(), asset.metadata[i].second.c_str(),
                            i + 1 < asset.metadata.size() ? ", " : "");
            }
            std::printf("\n");
        }
    }
    return 0;
}

} // namespace

int main(int argc, char** argv) {
    if (argc < 2) {
        std::fprintf(stderr, "uso: assetc <build|inspect> [opcoes]\n");
        return 2;
    }

    const std::string command = argv[1];

    platform::CommandLineParser parser;
    // argv+1/argc-1: o parser sempre pula sua própria posição 0 (nome do
    // programa); aqui usamos essa posição para o subcomando, que já foi
    // capturado acima, então o resto dos argumentos é processado normalmente.
    parser.parse(argc - 1, argv + 1);

    try {
        if (command == "build") return run_build(parser);
        if (command == "inspect") return run_inspect(parser);
    } catch (const std::exception& e) {
        std::fprintf(stderr, "assetc: erro: %s\n", e.what());
        return 1;
    }

    std::fprintf(stderr, "comando desconhecido: %s\n", command.c_str());
    return 2;
}
