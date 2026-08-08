#pragma once
#include "engine/render/gl.hpp"

#include <cstdint>
#include <vector>

namespace engine::render {

// Textura 2D RGBA8. Recebe pixels crus (ex.: já descomprimidos pelo
// ResourceManager, Sprint 6, do payload de um asset "image"/"atlas").
class Texture2D {
public:
    Texture2D(std::uint32_t width, std::uint32_t height, const unsigned char* rgba8_pixels);
    ~Texture2D();

    Texture2D(const Texture2D&) = delete;
    Texture2D& operator=(const Texture2D&) = delete;

    void bind(unsigned int texture_unit = 0) const;

    std::uint32_t width() const { return width_; }
    std::uint32_t height() const { return height_; }
    GLuint native_handle() const { return id_; }

private:
    GLuint id_ = 0;
    std::uint32_t width_ = 0;
    std::uint32_t height_ = 0;
};

} // namespace engine::render
