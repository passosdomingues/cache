#pragma once
#include "engine/render/math.hpp"

namespace engine::render {

// Câmera ortográfica 2D: posição (centro da view) + zoom + tamanho do
// viewport. view_projection() é a matriz que o shader de sprite usa
// para converter coordenadas de mundo em coordenadas de tela.
class OrthographicCamera2D {
public:
    OrthographicCamera2D(float viewport_width, float viewport_height)
        : viewport_width_(viewport_width), viewport_height_(viewport_height) {}

    void set_position(float x, float y) { position_ = {x, y}; }
    Vec2 position() const { return position_; }

    void set_zoom(float zoom) { zoom_ = zoom; }
    float zoom() const { return zoom_; }

    void set_viewport(float width, float height) {
        viewport_width_ = width;
        viewport_height_ = height;
    }

    Mat4 view_projection() const {
        float half_w = (viewport_width_ * 0.5f) / zoom_;
        float half_h = (viewport_height_ * 0.5f) / zoom_;
        Mat4 projection = Mat4::ortho(-half_w, half_w, -half_h, half_h, -1.0f, 1.0f);
        Mat4 view = Mat4::translate(-position_.x, -position_.y);
        return Mat4::multiply(projection, view);
    }

private:
    Vec2 position_{};
    float zoom_ = 1.0f;
    float viewport_width_;
    float viewport_height_;
};

} // namespace engine::render
