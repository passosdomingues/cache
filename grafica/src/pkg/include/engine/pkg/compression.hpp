#pragma once
#include <cstddef>
#include <vector>

namespace engine::pkg {

// Compressão sem perdas (zlib/deflate) do payload de um asset. zlib é a
// única dependência externa permitida no runtime (ver ADR 0004) —
// diferente de ImageMagick/FFmpeg, que ficam restritos à Toolchain.
std::vector<unsigned char> deflate_compress(const std::vector<unsigned char>& input);
std::vector<unsigned char> inflate_decompress(const std::vector<unsigned char>& input, std::size_t expected_size);

} // namespace engine::pkg
