#include "test_framework.hpp"

#include "engine/assetc/block_format.hpp"
#include "engine/assetc/compiler.hpp"
#include "engine/assetc/hash.hpp"
#include "engine/assetc/package.hpp"
#include "engine/platform/filesystem.hpp"

#include <filesystem>
#include <stdexcept>
#include <string>

using namespace engine::assetc;
namespace fs = std::filesystem;

namespace {

fs::path make_temp_dir(const std::string& name) {
    auto dir = fs::temp_directory_path() / "engine_assetc_tests" / name;
    std::error_code ec;
    fs::remove_all(dir, ec);
    fs::create_directories(dir);
    return dir;
}

void write_file(const fs::path& path, const std::string& content) {
    engine::platform::fs::write_text_file(path, content);
}

} // namespace

TEST_CASE(hash_is_deterministic_and_sensitive_to_content) {
    auto h1 = fnv1a_64(std::string_view("engine de jogos"));
    auto h2 = fnv1a_64(std::string_view("engine de jogos"));
    auto h3 = fnv1a_64(std::string_view("engine de jogos!"));
    CHECK(h1 == h2);
    CHECK(h1 != h3);
}

TEST_CASE(block_format_round_trip) {
    std::string text =
        "[hero]\n"
        "type=raw\n"
        "path=hero.png\n"
        "\n"
        "[atlas]\n"
        "type=raw\n"
        "path=atlas.json\n"
        "depends=hero\n";

    auto blocks = parse_blocks(text);
    CHECK(blocks.size() == 2);
    if (blocks.size() == 2) {
        CHECK(blocks[0].name == "hero");
        CHECK(blocks[0].get("type") == "raw");
        CHECK(blocks[1].get("depends") == "hero");
    }

    auto reparsed = parse_blocks(serialize_blocks(blocks));
    CHECK(reparsed.size() == blocks.size());
}

TEST_CASE(topological_order_orders_dependencies_first) {
    AssetManifest manifest;
    manifest.assets.push_back(SourceAsset{"atlas", "raw", "atlas.json", {"hero"}});
    manifest.assets.push_back(SourceAsset{"hero", "raw", "hero.png", {}});

    auto ordered = topological_order(manifest);
    CHECK(ordered.size() == 2);
    if (ordered.size() == 2) {
        CHECK(ordered[0].id == "hero");
        CHECK(ordered[1].id == "atlas");
    }
}

TEST_CASE(topological_order_detects_cycle) {
    AssetManifest manifest;
    manifest.assets.push_back(SourceAsset{"a", "raw", "a.bin", {"b"}});
    manifest.assets.push_back(SourceAsset{"b", "raw", "b.bin", {"a"}});

    bool threw = false;
    try {
        topological_order(manifest);
    } catch (const std::runtime_error&) {
        threw = true;
    }
    CHECK(threw);
}

TEST_CASE(build_produces_deterministic_package) {
    auto dir = make_temp_dir("deterministic");
    write_file(dir / "hero.png", "conteudo-fake-de-imagem");
    write_file(dir / "hero.dat", "[hero]\ntype=raw\npath=hero.png\n");

    BuildOptions options;
    options.manifest_path = dir / "hero.dat";
    options.output_path = dir / "out1.pkg";
    options.cache_dir = dir / "cache";
    options.force = true;
    build(options);

    BuildOptions options2 = options;
    options2.output_path = dir / "out2.pkg";
    options2.force = false; // usa o cache recem-criado

    auto stats2 = build(options2);
    CHECK(stats2.cache_hits == 1);
    CHECK(stats2.compiled == 0);

    auto bytes1 = engine::platform::fs::read_text_file(options.output_path);
    auto bytes2 = engine::platform::fs::read_text_file(options2.output_path);
    CHECK(bytes1.has_value());
    CHECK(bytes2.has_value());
    if (bytes1 && bytes2) {
        CHECK(*bytes1 == *bytes2);
    }
}

TEST_CASE(dependency_invalidation_propagates) {
    auto dir = make_temp_dir("dep_invalidation");
    write_file(dir / "b.bin", "conteudo-b-v1");
    write_file(dir / "a.bin", "conteudo-a");
    write_file(dir / "manifest.dat",
        "[b]\ntype=raw\npath=b.bin\n\n"
        "[a]\ntype=raw\npath=a.bin\ndepends=b\n");

    BuildOptions options;
    options.manifest_path = dir / "manifest.dat";
    options.output_path = dir / "out.pkg";
    options.cache_dir = dir / "cache";
    options.force = true;

    auto stats1 = build(options);
    CHECK(stats1.compiled == 2);

    // Rebuild sem mudar nada: os dois devem vir do cache.
    options.force = false;
    auto stats2 = build(options);
    CHECK(stats2.cache_hits == 2);
    CHECK(stats2.compiled == 0);

    // Muda so a dependencia (b); 'a' nao muda seu proprio arquivo, mas
    // deve ser recompilado porque sua dependencia mudou.
    write_file(dir / "b.bin", "conteudo-b-v2");
    auto stats3 = build(options);
    CHECK(stats3.compiled == 2);
    CHECK(stats3.cache_hits == 0);
}

TEST_CASE(inspect_reads_back_metadata) {
    auto dir = make_temp_dir("inspect");
    write_file(dir / "hero.png", "bytes-do-heroi");
    write_file(dir / "meta.json", "{}");
    write_file(dir / "manifest.dat",
        "[hero]\ntype=raw\npath=hero.png\n\n"
        "[hero_meta]\ntype=raw\npath=meta.json\ndepends=hero\n");

    BuildOptions options;
    options.manifest_path = dir / "manifest.dat";
    options.output_path = dir / "out.pkg";
    options.cache_dir = dir / "cache";
    options.force = true;
    build(options);

    auto info = read_package_info(options.output_path);
    CHECK(info.assets.size() == 2);

    bool found_hero = false, found_meta = false;
    for (const auto& asset : info.assets) {
        if (asset.id == "hero") {
            found_hero = true;
            CHECK(asset.type == "raw");
            CHECK(asset.payload_size == std::string("bytes-do-heroi").size());
            CHECK(asset.dependencies.empty());
        }
        if (asset.id == "hero_meta") {
            found_meta = true;
            CHECK(asset.dependencies.size() == 1);
            if (!asset.dependencies.empty()) {
                CHECK(asset.dependencies[0] == "hero");
            }
        }
    }
    CHECK(found_hero);
    CHECK(found_meta);
}

int main() {
    return engine::testing::run_all();
}
