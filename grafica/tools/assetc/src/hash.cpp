#include "engine/assetc/hash.hpp"
#include "engine/platform/filesystem.hpp"

#include <cstdio>

namespace engine::assetc {

std::uint64_t fnv1a_64(const void* data, std::size_t size) {
    constexpr std::uint64_t kOffsetBasis = 14695981039346656037ULL;
    constexpr std::uint64_t kPrime = 1099511628211ULL;

    std::uint64_t hash = kOffsetBasis;
    const auto* bytes = static_cast<const unsigned char*>(data);
    for (std::size_t i = 0; i < size; ++i) {
        hash ^= bytes[i];
        hash *= kPrime;
    }
    return hash;
}

std::uint64_t fnv1a_64(std::string_view data) {
    return fnv1a_64(data.data(), data.size());
}

std::uint64_t hash_file(const std::filesystem::path& path) {
    // read_text_file lê em modo binário internamente (ver Sprint 1), então
    // arquivos binários também são lidos corretamente — o conteúdo só é
    // guardado em um std::string, que aceita bytes arbitrários.
    auto content = platform::fs::read_text_file(path);
    if (!content) return 0;
    return fnv1a_64(*content);
}

std::string to_hex(std::uint64_t value) {
    char buffer[17];
    std::snprintf(buffer, sizeof(buffer), "%016llx", static_cast<unsigned long long>(value));
    return std::string(buffer);
}

std::uint64_t hash_combine(std::uint64_t seed, std::uint64_t value) {
    return seed ^ (value + 0x9e3779b97f4a7c15ULL + (seed << 6) + (seed >> 2));
}

} // namespace engine::assetc
