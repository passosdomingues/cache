#include "test_framework.hpp"

#include "engine/render/batch_renderer.hpp"
#include "engine/render/camera.hpp"
#include "engine/render/framebuffer.hpp"
#include "engine/render/gl.hpp"
#include "engine/render/image_payload.hpp"
#include "engine/render/shader.hpp"
#include "engine/render/texture.hpp"
#include "engine/render/window.hpp"

#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <vector>

// Testes marcados "(GL)" abaixo precisam de um display X11/Wayland (ou
// Xvfb) — sem isso, glfwInit()/glfwCreateWindow() falha e o teste lança.
// Os testes de payload (image/atlas) são lógica pura, sem GL.

using namespace engine::render;

namespace {
void append_u32(std::vector<unsigned char>& out, std::uint32_t value) {
    const auto* bytes = reinterpret_cast<const unsigned char*>(&value);
    out.insert(out.end(), bytes, bytes + sizeof(value));
}
} // namespace

TEST_CASE(image_payload_parses_metadata_and_pixels) {
    std::vector<unsigned char> payload;
    append_u32(payload, 1); // mip_count
    append_u32(payload, 2); // width
    append_u32(payload, 1); // height
    // 2x1 pixels RGBA8
    unsigned char pixels[8] = {255, 0, 0, 255, 0, 255, 0, 255};
    payload.insert(payload.end(), pixels, pixels + 8);

    auto image = read_image_payload_mip0(payload);
    CHECK(image.width == 2);
    CHECK(image.height == 1);
    CHECK(image.rgba8.size() == 8);
    if (image.rgba8.size() == 8) {
        CHECK(image.rgba8[0] == 255);
        CHECK(image.rgba8[4] == 0);
        CHECK(image.rgba8[5] == 255);
    }
}

TEST_CASE(atlas_payload_parses_sprite_table_and_pixels) {
    std::vector<unsigned char> payload;
    append_u32(payload, 4); // atlas width
    append_u32(payload, 2); // atlas height
    append_u32(payload, 1); // mip_count
    append_u32(payload, 2); // sprite_count

    // sprite "a": x=0,y=0,w=2,h=2
    append_u32(payload, 1);
    payload.push_back('a');
    append_u32(payload, 0);
    append_u32(payload, 0);
    append_u32(payload, 2);
    append_u32(payload, 2);

    // sprite "b": x=2,y=0,w=2,h=2
    append_u32(payload, 1);
    payload.push_back('b');
    append_u32(payload, 2);
    append_u32(payload, 0);
    append_u32(payload, 2);
    append_u32(payload, 2);

    // pixels: 4x2 RGBA8 (32 bytes)
    std::vector<unsigned char> pixels(4 * 2 * 4, 42);
    payload.insert(payload.end(), pixels.begin(), pixels.end());

    auto atlas = read_atlas_payload_mip0(payload);
    CHECK(atlas.width == 4);
    CHECK(atlas.height == 2);
    CHECK(atlas.sprites.size() == 2);
    if (atlas.sprites.size() == 2) {
        CHECK(atlas.sprites[0].id == "a");
        CHECK(atlas.sprites[1].id == "b");
        CHECK(atlas.sprites[1].x == 2);
    }
    CHECK(atlas.rgba8.size() == 32);
}

TEST_CASE(window_creates_hidden_context_and_loads_gl_functions) {
    WindowConfig config;
    config.visible = false;
    config.width = 64;
    config.height = 64;
    Window window(config);

    CHECK(window.width() == 64);
    CHECK(window.height() == 64);
    CHECK(gl::GenBuffers != nullptr);
    CHECK(gl::CreateShader != nullptr);
}

TEST_CASE(shader_compiles_valid_source_and_rejects_invalid) {
    WindowConfig config;
    config.visible = false;
    Window window(config);
    (void)window;

    const char* vs = "#version 330 core\nlayout(location=0) in vec2 p;\nvoid main(){gl_Position=vec4(p,0.0,1.0);}\n";
    const char* fs = "#version 330 core\nout vec4 c;\nvoid main(){c=vec4(1.0);}\n";
    ShaderProgram program(vs, fs); // não deve lançar
    program.use();

    const char* bad_fs = "#version 330 core\nout vec4 c;\nvoid main(){ISTO_NAO_COMPILA;}\n";
    bool threw = false;
    try {
        ShaderProgram broken(vs, bad_fs);
    } catch (const std::runtime_error&) {
        threw = true;
    }
    CHECK(threw);
}

TEST_CASE(texture_uploads_pixels_without_error) {
    WindowConfig config;
    config.visible = false;
    Window window(config);
    (void)window;

    unsigned char pixels[16] = {
        255, 0, 0, 255,  0, 255, 0, 255,
        0, 0, 255, 255,  255, 255, 0, 255,
    };
    Texture2D texture(2, 2, pixels);
    CHECK(texture.width() == 2);
    CHECK(texture.height() == 2);
    texture.bind(0);
    CHECK(glGetError() == GL_NO_ERROR);
}

TEST_CASE(framebuffer_render_to_texture_and_readback) {
    WindowConfig config;
    config.visible = false;
    Window window(config);
    (void)window;

    Framebuffer fb(32, 32);
    fb.bind();
    glViewport(0, 0, 32, 32);
    glClearColor(0.2f, 0.4f, 0.6f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT);

    unsigned char pixel[4] = {0, 0, 0, 0};
    glReadPixels(15, 15, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, pixel);
    Framebuffer::unbind();

    // 0.2*255≈51, 0.4*255≈102, 0.6*255≈153 — tolerância pequena por
    // arredondamento de ponto flutuante.
    CHECK(pixel[0] >= 48 && pixel[0] <= 54);
    CHECK(pixel[1] >= 99 && pixel[1] <= 105);
    CHECK(pixel[2] >= 150 && pixel[2] <= 156);
}

TEST_CASE(sprite_batch_submits_and_flushes_without_gl_errors) {
    WindowConfig config;
    config.visible = false;
    Window window(config);
    (void)window;

    unsigned char pixels[4] = {255, 255, 255, 255};
    Texture2D texture(1, 1, pixels);

    OrthographicCamera2D camera(100.0f, 100.0f);
    SpriteBatch batch;

    Sprite sprite;
    sprite.position = {0.0f, 0.0f};
    sprite.size = {10.0f, 10.0f};
    sprite.texture = &texture;

    batch.begin(camera);
    batch.submit(sprite);
    batch.end();

    CHECK(batch.draw_call_count() == 1);
    CHECK(glGetError() == GL_NO_ERROR);
}

int main() {
    return engine::testing::run_all();
}
