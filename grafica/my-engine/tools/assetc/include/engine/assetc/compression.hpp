#pragma once
#include <cstddef>
#include <vector>

namespace engine::assetc {

// Compressao sem perdas (zlib/deflate) do payload final de um asset —
// biblioteca de terceiro usada apenas na Toolchain, nunca no runtime
// (RFC 00, restricoes), do mesmo jeito que ImageMagick/FFmpeg.
std::vector<unsigned char> deflate_compress(const std::vector<unsigned char>& input);
std::vector<unsigned char> inflate_decompress(const std::vector<unsigned char>& input, std::size_t expected_size);

} // namespace engine::assetc
