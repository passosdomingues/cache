#include "engine/assetc/atlas_packer.hpp"

#include <algorithm>

namespace engine::assetc {

AtlasLayout pack_shelves(const std::vector<SpriteInput>& sprites, std::uint32_t max_width, std::uint32_t padding) {
    std::vector<std::size_t> order(sprites.size());
    for (std::size_t i = 0; i < sprites.size(); ++i) order[i] = i;

    std::sort(order.begin(), order.end(), [&](std::size_t a, std::size_t b) {
        if (sprites[a].height != sprites[b].height) return sprites[a].height > sprites[b].height;
        return sprites[a].id < sprites[b].id; // desempate deterministico
    });

    AtlasLayout layout;
    layout.placements.resize(sprites.size());

    std::uint32_t cursor_x = padding;
    std::uint32_t shelf_y = padding;
    std::uint32_t shelf_height = 0;

    for (std::size_t idx : order) {
        const auto& sprite = sprites[idx];

        if (cursor_x > padding && cursor_x + sprite.width + padding > max_width) {
            shelf_y += shelf_height + padding;
            cursor_x = padding;
            shelf_height = 0;
        }

        SpritePlacement placement;
        placement.id = sprite.id;
        placement.x = cursor_x;
        placement.y = shelf_y;
        placement.width = sprite.width;
        placement.height = sprite.height;
        layout.placements[idx] = placement;

        cursor_x += sprite.width + padding;
        shelf_height = std::max(shelf_height, sprite.height);
    }

    layout.width = max_width;
    layout.height = shelf_y + shelf_height + padding;
    return layout;
}

} // namespace engine::assetc
