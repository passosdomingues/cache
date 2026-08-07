#pragma once
#include <cstdint>
#include <filesystem>
#include <string>
#include <vector>

namespace engine::assetc {

struct ImageBuffer {
    std::uint32_t width = 0;
    std::uint32_t height = 0;
    std::uint32_t channels = 4; // sempre RGBA8 nesta versao do front-end
    std::vector<unsigned char> pixels; // width*height*channels bytes
};

struct ImageTransform {
    std::string resize; // geometria ImageMagick, ex.: "64x64" (vazio = sem resize)
    std::string crop;   // geometria ImageMagick, ex.: "32x32+0+0" (vazio = sem crop)
    unsigned pad = 0;    // padding transparente uniforme, em pixels
};

// Decodifica e transforma uma imagem via ImageMagick (`convert`/`identify`),
// retornando pixels RGBA8 crus. Lanca std::runtime_error se o ImageMagick
// nao estiver instalado ou se a conversao falhar.
ImageBuffer load_and_transform_image(const std::filesystem::path& source, const ImageTransform& transform);

// Gera uma cadeia de mipmaps por filtro de caixa (media 2x2), a partir do
// nivel 0 (mip_levels[0] == a propria imagem). Para quando ambas as
// dimensoes chegam a 1, ou ao atingir max_levels (0 = sem limite).
std::vector<ImageBuffer> generate_mipmaps(const ImageBuffer& base, unsigned max_levels = 0);

} // namespace engine::assetc
