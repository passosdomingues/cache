#pragma once

namespace engine::core {

struct Version {
    int major;
    int minor;
    int patch;
};

// Corresponde à versão do Sprint 0 (ver CHANGELOG.md).
inline constexpr Version kEngineVersion{0, 0, 1};

} // namespace engine::core
