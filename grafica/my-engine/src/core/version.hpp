#pragma once

namespace engine::core {

struct Version {
    int major;
    int minor;
    int patch;
};

// Corresponde à versão do CHANGELOG.md — atualizar a cada sprint que
// altera comportamento observável do binário.
inline constexpr Version kEngineVersion{0, 0, 7};

} // namespace engine::core
