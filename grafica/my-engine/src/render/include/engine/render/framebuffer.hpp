#pragma once
#include "engine/render/gl.hpp"
#include "engine/render/texture.hpp"

#include <cstdint>
#include <memory>

namespace engine::render {

// Framebuffer off-screen com uma textura de cor anexada — base para
// render-to-texture (pós-processamento, picking, etc. em sprints
// futuros). Sprint 7 só demonstra o mecanismo básico: criar, bindar,
// renderizar dentro, ler de volta como textura.
class Framebuffer {
public:
    Framebuffer(std::uint32_t width, std::uint32_t height);
    ~Framebuffer();

    Framebuffer(const Framebuffer&) = delete;
    Framebuffer& operator=(const Framebuffer&) = delete;

    void bind() const;
    static void unbind();

    const Texture2D& color_texture() const { return *color_texture_; }
    std::uint32_t width() const { return width_; }
    std::uint32_t height() const { return height_; }

private:
    GLuint fbo_ = 0;
    std::unique_ptr<Texture2D> color_texture_;
    std::uint32_t width_ = 0;
    std::uint32_t height_ = 0;
};

} // namespace engine::render
