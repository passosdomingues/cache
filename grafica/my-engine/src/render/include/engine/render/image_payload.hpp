#pragma once
#include <cstdint>
#include <string>
#include <vector>

namespace engine::render {

// Lê o payload já DESCOMPRIMIDO (ver ResourceManager::data(), Sprint 6)
// de um asset "image" — layout escrito por
// tools/assetc/src/frontend.cpp (compile_image):
//   [u32 mip_count] + por nível [u32 w][u32 h][pixels RGBA8]
// Só o mip 0 (nível base) é lido — streaming de LOD fica para quando o
// renderer realmente precisar disso.
struct DecodedImage {
    std::uint32_t width = 0;
    std::uint32_t height = 0;
    std::vector<unsigned char> rgba8; // width*height*4 bytes
};
DecodedImage read_image_payload_mip0(const std::vector<unsigned char>& uncompressed_payload);

// Lê o payload já descomprimido de um asset "atlas" — layout escrito
// por compile_atlas():
//   [u32 atlas_w][u32 atlas_h][u32 mip_count][u32 sprite_count]
//   por sprite: [u32 id_len][id][u32 x][u32 y][u32 w][u32 h]
//   por nível de mip: pixels RGBA8 (só o mip 0 é lido aqui)
struct AtlasSprite {
    std::string id;
    std::uint32_t x = 0, y = 0, w = 0, h = 0;
};
struct DecodedAtlas {
    std::uint32_t width = 0;
    std::uint32_t height = 0;
    std::vector<AtlasSprite> sprites;
    std::vector<unsigned char> rgba8; // mip 0, width*height*4 bytes
};
DecodedAtlas read_atlas_payload_mip0(const std::vector<unsigned char>& uncompressed_payload);

} // namespace engine::render
