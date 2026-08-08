#include "engine/render/batch_renderer.hpp"
#include "engine/render/camera.hpp"
#include "engine/render/image_payload.hpp"
#include "engine/render/texture.hpp"
#include "engine/render/window.hpp"

#include "engine/platform/cli.hpp"
#include "engine/platform/timer.hpp"
#include "engine/resources/resource_manager.hpp"

#include <cmath>
#include <cstdio>
#include <cstdint>
#include <exception>
#include <fstream>
#include <memory>
#include <string>
#include <vector>

using namespace engine;

namespace {

// Escreve um PPM (P6) simples a partir do framebuffer atual — sem
// dependência externa, só para provar visualmente que algo foi
// desenhado (usado em validação/CI headless).
void save_screenshot_ppm(const std::string& path, std::uint32_t width, std::uint32_t height) {
    std::vector<unsigned char> pixels(static_cast<std::size_t>(width) * height * 3);
    glReadPixels(0, 0, static_cast<GLsizei>(width), static_cast<GLsizei>(height), GL_RGB, GL_UNSIGNED_BYTE,
                 pixels.data());

    std::ofstream out(path, std::ios::binary);
    out << "P6\n" << width << " " << height << "\n255\n";
    // glReadPixels devolve a imagem de baixo para cima; PPM espera de cima para baixo.
    for (std::uint32_t y = 0; y < height; ++y) {
        std::uint32_t src_row = height - 1 - y;
        out.write(reinterpret_cast<const char*>(pixels.data() + src_row * width * 3), width * 3);
    }
}

} // namespace

// Entrega do Sprint 7: Window + Context + Shader + Texture + Camera +
// Sprite + Batch, tudo junto — um sprite se movendo na tela, carregado
// de um game.pkg real (produzido pelo assetc) via ResourceManager
// (Sprint 6). Se o asset for um "atlas", também exercita a leitura da
// tabela de sprites (Sprint 4) e o recorte de UV correspondente.
int main(int argc, char** argv) {
    platform::CommandLineParser args;
    args.parse(argc, argv);

    auto package_path = args.get_option("package");
    if (!package_path) {
        std::fprintf(stderr,
            "uso: moving-sprite-demo --package=<pacote.pkg> [--asset=<id>] [--sprite=<id>] "
            "[--frames=N] [--headless] [--screenshot=<arquivo.ppm>]\n");
        return 2;
    }

    const int frame_count = std::stoi(args.get_option("frames", "180"));
    const bool headless = args.has_flag("headless");
    auto screenshot_path = args.get_option("screenshot");

    try {
        resources::ResourceManager manager(*package_path);

        std::string asset_id = args.get_option("asset", "");
        if (asset_id.empty()) {
            for (const auto& id : manager.asset_ids()) {
                auto h = manager.acquire(id);
                std::string type = manager.type_of(h);
                manager.release(h);
                if (type == "atlas" || type == "image") {
                    asset_id = id;
                    break;
                }
            }
        }
        if (asset_id.empty()) {
            std::fprintf(stderr, "moving-sprite-demo: nenhum asset image/atlas encontrado em %s\n",
                         package_path->c_str());
            return 1;
        }

        auto handle = manager.acquire(asset_id);
        std::string type = manager.type_of(handle);
        const auto* payload = manager.data(handle);
        if (!payload) {
            std::fprintf(stderr, "moving-sprite-demo: asset '%s' nao residente\n", asset_id.c_str());
            return 1;
        }

        render::WindowConfig config;
        config.title = "Moving Sprite — Sprint 7";
        config.width = 800;
        config.height = 600;
        config.visible = !headless;
        config.vsync = false;

        render::Window window(config);

        render::UVRect uv;
        std::unique_ptr<render::Texture2D> texture;

        if (type == "atlas") {
            auto atlas = render::read_atlas_payload_mip0(*payload);
            texture = std::make_unique<render::Texture2D>(atlas.width, atlas.height, atlas.rgba8.data());

            std::string sprite_id = args.get_option("sprite", "");
            const render::AtlasSprite* chosen = nullptr;
            for (const auto& sprite : atlas.sprites) {
                if (sprite_id.empty() || sprite.id == sprite_id) {
                    chosen = &sprite;
                    break;
                }
            }
            if (!chosen) {
                std::fprintf(stderr, "moving-sprite-demo: sprite nao encontrado no atlas\n");
                return 1;
            }
            uv.u0 = static_cast<float>(chosen->x) / static_cast<float>(atlas.width);
            uv.v0 = static_cast<float>(chosen->y) / static_cast<float>(atlas.height);
            uv.u1 = static_cast<float>(chosen->x + chosen->w) / static_cast<float>(atlas.width);
            uv.v1 = static_cast<float>(chosen->y + chosen->h) / static_cast<float>(atlas.height);
            std::printf("Renderizando sprite '%s' do atlas '%s' (%ux%u em %ux%u)\n",
                        chosen->id.c_str(), asset_id.c_str(), chosen->w, chosen->h, atlas.width, atlas.height);
        } else if (type == "image") {
            auto image = render::read_image_payload_mip0(*payload);
            texture = std::make_unique<render::Texture2D>(image.width, image.height, image.rgba8.data());
            std::printf("Renderizando imagem '%s' (%ux%u)\n", asset_id.c_str(), image.width, image.height);
        } else {
            std::fprintf(stderr, "moving-sprite-demo: asset '%s' tem tipo '%s', nao image/atlas\n",
                         asset_id.c_str(), type.c_str());
            return 1;
        }

        render::OrthographicCamera2D camera(static_cast<float>(config.width), static_cast<float>(config.height));
        render::SpriteBatch batch;
        platform::DeltaClock clock;

        double elapsed = 0.0;
        const float amplitude = static_cast<float>(config.width) * 0.35f;

        for (int frame = 0; frame < frame_count; ++frame) {
            if (!headless && window.should_close()) break;

            double dt = clock.tick();
            elapsed += dt;

            float x = amplitude * static_cast<float>(std::sin(elapsed));

            glClearColor(0.08f, 0.08f, 0.12f, 1.0f);
            glClear(GL_COLOR_BUFFER_BIT);
            glEnable(GL_BLEND);
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

            render::Sprite sprite;
            sprite.position = {x, 0.0f};
            sprite.size = {128.0f, 128.0f};
            sprite.uv = uv;
            sprite.texture = texture.get();

            batch.begin(camera);
            batch.submit(sprite);
            batch.end();

            window.swap_buffers();
            window.poll_events();
        }

        std::printf("Renderizados %d frames (draw calls no ultimo frame: %d)\n", frame_count,
                    batch.draw_call_count());

        if (screenshot_path) {
            save_screenshot_ppm(*screenshot_path, config.width, config.height);
            std::printf("Screenshot salvo em %s\n", screenshot_path->c_str());
        }

        manager.release(handle);
        return 0;
    } catch (const std::exception& e) {
        std::fprintf(stderr, "moving-sprite-demo: erro: %s\n", e.what());
        return 1;
    }
}
