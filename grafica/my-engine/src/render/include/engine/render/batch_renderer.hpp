#pragma once
#include "engine/render/camera.hpp"
#include "engine/render/gl.hpp"
#include "engine/render/shader.hpp"
#include "engine/render/sprite.hpp"

#include <cstddef>
#include <vector>

namespace engine::render {

// Acumula sprites submetidos entre begin()/end() e os desenha em lotes
// (batches), agrupando por textura para minimizar troca de estado de
// GPU. Nesse contexto 2D, essa fila de sprites agrupada por textura —
// resolvida em flush() — É a Render Queue do Sprint 7: não existe uma
// estrutura de "fila" separada, o próprio batching cumpre esse papel.
class SpriteBatch {
public:
    SpriteBatch();
    ~SpriteBatch();

    SpriteBatch(const SpriteBatch&) = delete;
    SpriteBatch& operator=(const SpriteBatch&) = delete;

    void begin(const OrthographicCamera2D& camera);
    void submit(const Sprite& sprite);
    void end(); // flush do que ainda estiver pendente

    int draw_call_count() const { return draw_calls_; }

private:
    struct Vertex {
        float x, y;
        float u, v;
        float r, g, b, a;
    };

    void flush();

    ShaderProgram shader_;
    GLuint vao_ = 0;
    GLuint vbo_ = 0;
    GLuint ebo_ = 0;

    Mat4 view_projection_ = Mat4::identity();
    std::vector<Vertex> vertices_;
    const Texture2D* current_texture_ = nullptr;
    int draw_calls_ = 0;

    static constexpr std::size_t kMaxSpritesPerBatch = 1000;
};

} // namespace engine::render
