#pragma once
#include <cstdint>

namespace engine::resources {

// Handle opaco para um recurso gerenciado pelo ResourceManager. `index`
// referencia um slot interno; `generation` detecta handles "stale" —
// se o slot for reciclado, a geração muda e um handle antigo passa a
// ser inválido em vez de apontar silenciosamente para outro recurso.
struct ResourceHandle {
    std::uint32_t index = 0;
    std::uint32_t generation = 0;

    bool valid() const { return generation != 0; }

    bool operator==(const ResourceHandle& other) const {
        return index == other.index && generation == other.generation;
    }
    bool operator!=(const ResourceHandle& other) const { return !(*this == other); }
};

inline constexpr ResourceHandle kInvalidHandle{};

} // namespace engine::resources
