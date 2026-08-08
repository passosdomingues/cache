#include "engine/render/image_payload.hpp"

#include <cstring>
#include <stdexcept>

namespace engine::render {

namespace {
std::uint32_t read_u32(const std::vector<unsigned char>& data, std::size_t& cursor) {
    if (cursor + 4 > data.size()) {
        throw std::runtime_error("payload truncado ao ler u32");
    }
    std::uint32_t value = 0;
    std::memcpy(&value, data.data() + cursor, sizeof(value));
    cursor += 4;
    return value;
}
} // namespace

DecodedImage read_image_payload_mip0(const std::vector<unsigned char>& payload) {
    std::size_t cursor = 0;
    std::uint32_t mip_count = read_u32(payload, cursor);
    if (mip_count == 0) {
        throw std::runtime_error("payload de imagem sem mips");
    }

    DecodedImage image;
    image.width = read_u32(payload, cursor);
    image.height = read_u32(payload, cursor);

    std::size_t pixel_bytes = static_cast<std::size_t>(image.width) * image.height * 4;
    if (cursor + pixel_bytes > payload.size()) {
        throw std::runtime_error("payload de imagem truncado");
    }
    image.rgba8.assign(payload.begin() + static_cast<std::ptrdiff_t>(cursor),
                        payload.begin() + static_cast<std::ptrdiff_t>(cursor + pixel_bytes));
    return image;
}

DecodedAtlas read_atlas_payload_mip0(const std::vector<unsigned char>& payload) {
    std::size_t cursor = 0;
    DecodedAtlas atlas;
    atlas.width = read_u32(payload, cursor);
    atlas.height = read_u32(payload, cursor);
    std::uint32_t mip_count = read_u32(payload, cursor);
    if (mip_count == 0) {
        throw std::runtime_error("payload de atlas sem mips");
    }
    std::uint32_t sprite_count = read_u32(payload, cursor);

    atlas.sprites.reserve(sprite_count);
    for (std::uint32_t i = 0; i < sprite_count; ++i) {
        std::uint32_t id_len = read_u32(payload, cursor);
        if (cursor + id_len > payload.size()) {
            throw std::runtime_error("payload de atlas truncado (id do sprite)");
        }
        AtlasSprite sprite;
        sprite.id.assign(reinterpret_cast<const char*>(payload.data() + cursor), id_len);
        cursor += id_len;

        sprite.x = read_u32(payload, cursor);
        sprite.y = read_u32(payload, cursor);
        sprite.w = read_u32(payload, cursor);
        sprite.h = read_u32(payload, cursor);
        atlas.sprites.push_back(std::move(sprite));
    }

    std::size_t pixel_bytes = static_cast<std::size_t>(atlas.width) * atlas.height * 4;
    if (cursor + pixel_bytes > payload.size()) {
        throw std::runtime_error("payload de atlas truncado (pixels)");
    }
    atlas.rgba8.assign(payload.begin() + static_cast<std::ptrdiff_t>(cursor),
                        payload.begin() + static_cast<std::ptrdiff_t>(cursor + pixel_bytes));
    return atlas;
}

} // namespace engine::render
