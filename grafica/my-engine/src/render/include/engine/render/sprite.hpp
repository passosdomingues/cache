#pragma once
#include "engine/render/math.hpp"
#include "engine/render/texture.hpp"

namespace engine::render {

// Retângulo de UV dentro de uma textura/atlas, em coordenadas
// normalizadas [0,1] — o que o Sprite Compiler (Sprint 4) calcula a
// partir da posição de cada sprite dentro do atlas.
struct UVRect {
    float u0 = 0.0f, v0 = 0.0f, u1 = 1.0f, v1 = 1.0f;
};

struct Sprite {
    Vec2 position{};              // centro do sprite, em coordenadas de mundo
    Vec2 size{32.0f, 32.0f};
    UVRect uv{};
    float r = 1.0f, g = 1.0f, b = 1.0f, a = 1.0f; // tint multiplicativo
    const Texture2D* texture = nullptr;
};

} // namespace engine::render
