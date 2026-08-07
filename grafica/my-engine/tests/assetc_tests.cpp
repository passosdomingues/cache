#include "test_framework.hpp"

#include "engine/assetc/atlas_packer.hpp"
#include "engine/assetc/block_format.hpp"
#include "engine/assetc/compiler.hpp"
#include "engine/assetc/hash.hpp"
#include "engine/pkg/compression.hpp"
#include "engine/pkg/format.hpp"
#include "engine/platform/filesystem.hpp"

#include <array>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <stdexcept>
#include <string>

using namespace engine::assetc;
using namespace engine::pkg;
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

void write_solid_png(const fs::path& path, unsigned width, unsigned height, const std::string& color) {
    std::string cmd = "convert -size " + std::to_string(width) + "x" + std::to_string(height) +
                       " xc:" + color + " " + path.string() + " 2>/dev/null";
    if (std::system(cmd.c_str()) != 0) {
        throw std::runtime_error("falha ao gerar PNG de teste (ImageMagick instalado? sudo apt install imagemagick)");
    }
}

void write_test_tone(const fs::path& path, double duration_seconds, double frequency = 440.0) {
    std::string cmd = "ffmpeg -y -f lavfi -i \"sine=frequency=" + std::to_string(frequency) +
                       ":duration=" + std::to_string(duration_seconds) + "\" " + path.string() + " 2>/dev/null";
    if (std::system(cmd.c_str()) != 0) {
        throw std::runtime_error("falha ao gerar audio de teste (FFmpeg instalado? sudo apt install ffmpeg)");
    }
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
    manifest.assets.push_back(SourceAsset{"atlas", "raw", "atlas.json", {"hero"}, {}});
    manifest.assets.push_back(SourceAsset{"hero", "raw", "hero.png", {}, {}});

    auto ordered = topological_order(manifest);
    CHECK(ordered.size() == 2);
    if (ordered.size() == 2) {
        CHECK(ordered[0].id == "hero");
        CHECK(ordered[1].id == "atlas");
    }
}

TEST_CASE(topological_order_detects_cycle) {
    AssetManifest manifest;
    manifest.assets.push_back(SourceAsset{"a", "raw", "a.bin", {"b"}, {}});
    manifest.assets.push_back(SourceAsset{"b", "raw", "b.bin", {"a"}, {}});

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

TEST_CASE(compression_round_trip) {
    std::vector<unsigned char> original = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 10, 10, 10};
    auto compressed = deflate_compress(original);
    auto restored = inflate_decompress(compressed, original.size());
    CHECK(restored == original);
}

TEST_CASE(atlas_packer_places_sprites_without_overlap) {
    std::vector<SpriteInput> sprites = {
        {"a", 10, 10}, {"b", 8, 12}, {"c", 20, 4}, {"d", 6, 6},
    };
    auto layout = pack_shelves(sprites, 32, 1);
    CHECK(layout.placements.size() == sprites.size());

    auto overlaps = [](const SpritePlacement& a, const SpritePlacement& b) {
        return a.x < b.x + b.width && b.x < a.x + a.width &&
               a.y < b.y + b.height && b.y < a.y + a.height;
    };
    for (std::size_t i = 0; i < layout.placements.size(); ++i) {
        for (std::size_t j = i + 1; j < layout.placements.size(); ++j) {
            CHECK(!overlaps(layout.placements[i], layout.placements[j]));
        }
        CHECK(layout.placements[i].x + layout.placements[i].width <= layout.width);
        CHECK(layout.placements[i].y + layout.placements[i].height <= layout.height);
    }
}

TEST_CASE(image_frontend_decodes_metadata) {
    auto dir = make_temp_dir("image_frontend");
    write_solid_png(dir / "solid.png", 4, 3, "red");
    write_file(dir / "manifest.dat", "[solid]\ntype=image\npath=solid.png\n");

    BuildOptions options;
    options.manifest_path = dir / "manifest.dat";
    options.output_path = dir / "out.pkg";
    options.cache_dir = dir / "cache";
    options.force = true;
    build(options);

    auto info = read_package_info(options.output_path);
    CHECK(info.assets.size() == 1);
    if (info.assets.empty()) return;

    const auto& asset = info.assets[0];
    CHECK(asset.type == "image");

    bool has_width = false, has_height = false;
    for (const auto& [k, v] : asset.metadata) {
        if (k == "width") { has_width = true; CHECK(v == "4"); }
        if (k == "height") { has_height = true; CHECK(v == "3"); }
    }
    CHECK(has_width);
    CHECK(has_height);
}

TEST_CASE(atlas_frontend_packs_sprites_and_preserves_pixels) {
    auto dir = make_temp_dir("atlas_frontend");
    write_solid_png(dir / "body.png", 4, 4, "blue");
    write_solid_png(dir / "head.png", 2, 2, "red");
    write_file(dir / "manifest.dat",
        "[body]\ntype=image\npath=body.png\n\n"
        "[head]\ntype=image\npath=head.png\n\n"
        "[hero_atlas]\ntype=atlas\ndepends=body,head\nmax_width=16\npadding=1\n");

    BuildOptions options;
    options.manifest_path = dir / "manifest.dat";
    options.output_path = dir / "out.pkg";
    options.cache_dir = dir / "cache";
    options.force = true;
    build(options);

    auto info = read_package_info(options.output_path);
    const PackageAssetInfo* atlas_info = nullptr;
    for (const auto& asset : info.assets) {
        if (asset.id == "hero_atlas") atlas_info = &asset;
    }
    CHECK(atlas_info != nullptr);
    if (!atlas_info) return;

    CHECK(atlas_info->dependencies.size() == 2);

    std::string sprite_count_str, uncompressed_size_str;
    for (const auto& [k, v] : atlas_info->metadata) {
        if (k == "sprite_count") sprite_count_str = v;
        if (k == "uncompressed_size") uncompressed_size_str = v;
    }
    CHECK(sprite_count_str == "2");

    auto compressed = read_package_payload(options.output_path, "hero_atlas");
    auto raw = inflate_decompress(compressed, static_cast<std::size_t>(std::stoul(uncompressed_size_str)));

    std::uint32_t atlas_w = 0, atlas_h = 0, mip_count = 0, placement_count = 0;
    std::memcpy(&atlas_w, raw.data() + 0, 4);
    std::memcpy(&atlas_h, raw.data() + 4, 4);
    std::memcpy(&mip_count, raw.data() + 8, 4);
    std::memcpy(&placement_count, raw.data() + 12, 4);
    CHECK(placement_count == 2);
    (void)mip_count;

    struct ParsedPlacement { std::string id; std::uint32_t x, y, w, h; };
    std::vector<ParsedPlacement> placements;
    std::size_t cursor = 16;
    for (std::uint32_t i = 0; i < placement_count; ++i) {
        std::uint32_t id_len = 0;
        std::memcpy(&id_len, raw.data() + cursor, 4);
        cursor += 4;
        std::string id(reinterpret_cast<const char*>(raw.data() + cursor), id_len);
        cursor += id_len;
        std::uint32_t x = 0, y = 0, w = 0, h = 0;
        std::memcpy(&x, raw.data() + cursor, 4); cursor += 4;
        std::memcpy(&y, raw.data() + cursor, 4); cursor += 4;
        std::memcpy(&w, raw.data() + cursor, 4); cursor += 4;
        std::memcpy(&h, raw.data() + cursor, 4); cursor += 4;
        placements.push_back({id, x, y, w, h});
    }

    auto pixel_at = [&](std::uint32_t px, std::uint32_t py) -> std::array<unsigned char, 4> {
        std::size_t idx = cursor + (static_cast<std::size_t>(py) * atlas_w + px) * 4;
        return {raw[idx], raw[idx + 1], raw[idx + 2], raw[idx + 3]};
    };

    bool checked_body = false, checked_head = false;
    for (const auto& p : placements) {
        auto color = pixel_at(p.x, p.y);
        if (p.id == "body") {
            checked_body = true;
            CHECK(color[0] == 0);
            CHECK(color[2] == 255);
        }
        if (p.id == "head") {
            checked_head = true;
            CHECK(color[0] == 255);
            CHECK(color[2] == 0);
        }
    }
    CHECK(checked_body);
    CHECK(checked_head);
}

TEST_CASE(audio_frontend_decodes_metadata) {
    auto dir = make_temp_dir("audio_frontend");
    write_test_tone(dir / "tone.wav", 1.0);
    write_file(dir / "manifest.dat",
        "[tone]\ntype=audio\npath=tone.wav\nsample_rate=8000\nchannels=1\n");

    BuildOptions options;
    options.manifest_path = dir / "manifest.dat";
    options.output_path = dir / "out.pkg";
    options.cache_dir = dir / "cache";
    options.force = true;
    build(options);

    auto info = read_package_info(options.output_path);
    CHECK(info.assets.size() == 1);
    if (info.assets.empty()) return;

    const auto& asset = info.assets[0];
    CHECK(asset.type == "audio");

    bool has_rate = false, has_channels = false, has_frames = false;
    for (const auto& [k, v] : asset.metadata) {
        if (k == "sample_rate") { has_rate = true; CHECK(v == "8000"); }
        if (k == "channels") { has_channels = true; CHECK(v == "1"); }
        if (k == "frame_count") { has_frames = true; CHECK(v == "8000"); } // 1s @ 8000Hz
    }
    CHECK(has_rate);
    CHECK(has_channels);
    CHECK(has_frames);
}

TEST_CASE(audio_frontend_trim_and_loop_flag) {
    auto dir = make_temp_dir("audio_trim");
    write_test_tone(dir / "tone.wav", 3.0);
    write_file(dir / "manifest.dat",
        "[tone]\ntype=audio\npath=tone.wav\nsample_rate=8000\nchannels=1\n"
        "trim_duration=1.0\nloop=true\n");

    BuildOptions options;
    options.manifest_path = dir / "manifest.dat";
    options.output_path = dir / "out.pkg";
    options.cache_dir = dir / "cache";
    options.force = true;
    build(options);

    auto info = read_package_info(options.output_path);
    CHECK(info.assets.size() == 1);
    if (info.assets.empty()) return;

    bool has_frames = false, has_loop = false;
    for (const auto& [k, v] : info.assets[0].metadata) {
        if (k == "frame_count") { has_frames = true; CHECK(v == "8000"); } // 1.0s trim @ 8000Hz
        if (k == "loop") { has_loop = true; CHECK(v == "true"); }
    }
    CHECK(has_frames);
    CHECK(has_loop);
}

TEST_CASE(audio_frontend_cache_invalidates_on_param_change) {
    auto dir = make_temp_dir("audio_cache");
    write_test_tone(dir / "tone.wav", 1.0);
    write_file(dir / "manifest.dat", "[tone]\ntype=audio\npath=tone.wav\nfade_out=0.1\n");

    BuildOptions options;
    options.manifest_path = dir / "manifest.dat";
    options.output_path = dir / "out.pkg";
    options.cache_dir = dir / "cache";
    options.force = true;

    auto stats1 = build(options);
    CHECK(stats1.compiled == 1);

    options.force = false;
    auto stats2 = build(options);
    CHECK(stats2.cache_hits == 1);
    CHECK(stats2.compiled == 0);

    // Muda so um parametro do manifesto (nao o arquivo fonte): deve invalidar.
    write_file(dir / "manifest.dat", "[tone]\ntype=audio\npath=tone.wav\nfade_out=0.5\n");
    auto stats3 = build(options);
    CHECK(stats3.compiled == 1);
    CHECK(stats3.cache_hits == 0);
}

int main() {
    return engine::testing::run_all();
}
