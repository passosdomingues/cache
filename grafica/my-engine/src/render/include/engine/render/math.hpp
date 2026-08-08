#pragma once

namespace engine::render {

struct Vec2 {
    float x = 0.0f;
    float y = 0.0f;
};

// Matriz 4x4 column-major (convenção OpenGL/GLSL), armazenada como
// float[16]. Mínima o suficiente para uma câmera ortográfica 2D — não é
// uma biblioteca de matemática de propósito geral.
struct Mat4 {
    float m[16] = {
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1,
    };

    static Mat4 identity() { return Mat4{}; }

    static Mat4 ortho(float left, float right, float bottom, float top, float near_, float far_) {
        Mat4 r{};
        for (float& v : r.m) v = 0.0f;
        r.m[0] = 2.0f / (right - left);
        r.m[5] = 2.0f / (top - bottom);
        r.m[10] = -2.0f / (far_ - near_);
        r.m[12] = -(right + left) / (right - left);
        r.m[13] = -(top + bottom) / (top - bottom);
        r.m[14] = -(far_ + near_) / (far_ - near_);
        r.m[15] = 1.0f;
        return r;
    }

    static Mat4 translate(float x, float y) {
        Mat4 r = identity();
        r.m[12] = x;
        r.m[13] = y;
        return r;
    }

    static Mat4 scale(float sx, float sy) {
        Mat4 r = identity();
        r.m[0] = sx;
        r.m[5] = sy;
        return r;
    }

    // r = a * b (aplica b primeiro, depois a — convenção coluna-major).
    static Mat4 multiply(const Mat4& a, const Mat4& b) {
        Mat4 r{};
        for (int col = 0; col < 4; ++col) {
            for (int row = 0; row < 4; ++row) {
                float sum = 0.0f;
                for (int k = 0; k < 4; ++k) {
                    sum += a.m[k * 4 + row] * b.m[col * 4 + k];
                }
                r.m[col * 4 + row] = sum;
            }
        }
        return r;
    }
};

} // namespace engine::render
