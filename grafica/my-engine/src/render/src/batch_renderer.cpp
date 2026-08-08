#include "engine/render/batch_renderer.hpp"

namespace engine::render {

namespace {
const char* kVertexShaderSrc = R"GLSL(
#version 330 core
layout(location = 0) in vec2 a_pos;
layout(location = 1) in vec2 a_uv;
layout(location = 2) in vec4 a_color;

uniform mat4 u_view_projection;

out vec2 v_uv;
out vec4 v_color;

void main() {
    v_uv = a_uv;
    v_color = a_color;
    gl_Position = u_view_projection * vec4(a_pos, 0.0, 1.0);
}
)GLSL";

const char* kFragmentShaderSrc = R"GLSL(
#version 330 core
in vec2 v_uv;
in vec4 v_color;
out vec4 frag_color;

uniform sampler2D u_texture;

void main() {
    frag_color = texture(u_texture, v_uv) * v_color;
}
)GLSL";
} // namespace

SpriteBatch::SpriteBatch() : shader_(kVertexShaderSrc, kFragmentShaderSrc) {
    vertices_.reserve(kMaxSpritesPerBatch * 4);

    gl::GenVertexArrays(1, &vao_);
    gl::BindVertexArray(vao_);

    gl::GenBuffers(1, &vbo_);
    gl::BindBuffer(GL_ARRAY_BUFFER, vbo_);
    gl::BufferData(GL_ARRAY_BUFFER,
                    static_cast<gl::GLsizeiptr>(kMaxSpritesPerBatch * 4 * sizeof(Vertex)),
                    nullptr, GL_DYNAMIC_DRAW);

    gl::EnableVertexAttribArray(0);
    gl::VertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, sizeof(Vertex),
                             reinterpret_cast<void*>(offsetof(Vertex, x)));
    gl::EnableVertexAttribArray(1);
    gl::VertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, sizeof(Vertex),
                             reinterpret_cast<void*>(offsetof(Vertex, u)));
    gl::EnableVertexAttribArray(2);
    gl::VertexAttribPointer(2, 4, GL_FLOAT, GL_FALSE, sizeof(Vertex),
                             reinterpret_cast<void*>(offsetof(Vertex, r)));

    std::vector<GLuint> indices(kMaxSpritesPerBatch * 6);
    for (std::size_t i = 0; i < kMaxSpritesPerBatch; ++i) {
        GLuint base = static_cast<GLuint>(i * 4);
        indices[i * 6 + 0] = base + 0;
        indices[i * 6 + 1] = base + 1;
        indices[i * 6 + 2] = base + 2;
        indices[i * 6 + 3] = base + 2;
        indices[i * 6 + 4] = base + 3;
        indices[i * 6 + 5] = base + 0;
    }
    gl::GenBuffers(1, &ebo_);
    gl::BindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo_);
    gl::BufferData(GL_ELEMENT_ARRAY_BUFFER,
                    static_cast<gl::GLsizeiptr>(indices.size() * sizeof(GLuint)),
                    indices.data(), GL_STATIC_DRAW);

    gl::BindVertexArray(0);
}

SpriteBatch::~SpriteBatch() {
    gl::DeleteBuffers(1, &ebo_);
    gl::DeleteBuffers(1, &vbo_);
    gl::DeleteVertexArrays(1, &vao_);
}

void SpriteBatch::begin(const OrthographicCamera2D& camera) {
    view_projection_ = camera.view_projection();
    vertices_.clear();
    current_texture_ = nullptr;
    draw_calls_ = 0;
}

void SpriteBatch::submit(const Sprite& sprite) {
    if (current_texture_ != nullptr && sprite.texture != current_texture_) {
        flush();
    }
    current_texture_ = sprite.texture;

    if (vertices_.size() + 4 > kMaxSpritesPerBatch * 4) {
        flush();
        current_texture_ = sprite.texture;
    }

    float hw = sprite.size.x * 0.5f;
    float hh = sprite.size.y * 0.5f;
    float x = sprite.position.x;
    float y = sprite.position.y;

    // Ordem: bottom-left, bottom-right, top-right, top-left — casa com o
    // padrão de índices (0,1,2, 2,3,0) montado no construtor.
    vertices_.push_back({x - hw, y - hh, sprite.uv.u0, sprite.uv.v1, sprite.r, sprite.g, sprite.b, sprite.a});
    vertices_.push_back({x + hw, y - hh, sprite.uv.u1, sprite.uv.v1, sprite.r, sprite.g, sprite.b, sprite.a});
    vertices_.push_back({x + hw, y + hh, sprite.uv.u1, sprite.uv.v0, sprite.r, sprite.g, sprite.b, sprite.a});
    vertices_.push_back({x - hw, y + hh, sprite.uv.u0, sprite.uv.v0, sprite.r, sprite.g, sprite.b, sprite.a});
}

void SpriteBatch::end() {
    flush();
}

void SpriteBatch::flush() {
    if (vertices_.empty() || current_texture_ == nullptr) return;

    shader_.use();
    shader_.set_mat4("u_view_projection", view_projection_);
    current_texture_->bind(0);
    shader_.set_int("u_texture", 0);

    gl::BindVertexArray(vao_);
    gl::BindBuffer(GL_ARRAY_BUFFER, vbo_);
    gl::BufferSubData(GL_ARRAY_BUFFER, 0,
                       static_cast<gl::GLsizeiptr>(vertices_.size() * sizeof(Vertex)), vertices_.data());
    gl::BindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo_);

    GLsizei index_count = static_cast<GLsizei>((vertices_.size() / 4) * 6);
    glDrawElements(GL_TRIANGLES, index_count, GL_UNSIGNED_INT, nullptr);

    gl::BindVertexArray(0);
    ++draw_calls_;
    vertices_.clear();
    current_texture_ = nullptr;
}

} // namespace engine::render
