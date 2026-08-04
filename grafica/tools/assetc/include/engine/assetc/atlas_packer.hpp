#pragma once
#include <cstdint>
#include <string>
#include <vector>

namespace engine::assetc {

struct SpriteInput {
    std::string id;
    std::uint32_t width = 0;
    std::uint32_t height = 0;
};

struct SpritePlacement {
    std::string id;
    std::uint32_t x = 0;
    std::uint32_t y = 0;
    std::uint32_t width = 0;
    std::uint32_t height = 0;
};

struct AtlasLayout {
    std::uint32_t width = 0;
    std::uint32_t height = 0;
    std::vector<SpritePlacement> placements; // mesmo indice/ordem de entrada em `sprites`
};

// Empacotamento por "prateleiras" (shelf packing): simples e
// deterministico — nao e o packing mais denso possivel, mas e previsivel
// e facil de raciocinar, suficiente para o Sprint 4. Ordena internamente
// por altura decrescente (desempate por id) antes de empacotar, mas
// devolve `placements` na mesma ordem de `sprites`.
//
// Limitacao conhecida: um sprite mais largo que `max_width` nao causa
// quebra de prateleira (evitaria loop com prateleiras vazias) — ele so
// extrapola a largura nominal. Escolha `max_width` >= maior sprite.
AtlasLayout pack_shelves(const std::vector<SpriteInput>& sprites, std::uint32_t max_width, std::uint32_t padding);

} // namespace engine::assetc
