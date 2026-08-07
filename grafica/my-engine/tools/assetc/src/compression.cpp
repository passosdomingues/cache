#include "engine/assetc/compression.hpp"

#include <stdexcept>
#include <zlib.h>

namespace engine::assetc {

std::vector<unsigned char> deflate_compress(const std::vector<unsigned char>& input) {
    uLongf bound = compressBound(static_cast<uLong>(input.size()));
    std::vector<unsigned char> output(bound);
    uLongf out_size = bound;

    const Bytef* src = input.empty() ? nullptr : reinterpret_cast<const Bytef*>(input.data());
    int result = compress2(output.data(), &out_size, src, static_cast<uLong>(input.size()), Z_BEST_COMPRESSION);
    if (result != Z_OK) {
        throw std::runtime_error("falha ao comprimir payload (zlib compress2)");
    }
    output.resize(out_size);
    return output;
}

std::vector<unsigned char> inflate_decompress(const std::vector<unsigned char>& input, std::size_t expected_size) {
    std::vector<unsigned char> output(expected_size);
    uLongf out_size = static_cast<uLongf>(expected_size);

    const Bytef* src = input.empty() ? nullptr : reinterpret_cast<const Bytef*>(input.data());
    int result = uncompress(output.data(), &out_size, src, static_cast<uLong>(input.size()));
    if (result != Z_OK) {
        throw std::runtime_error("falha ao descomprimir payload (zlib uncompress)");
    }
    output.resize(out_size);
    return output;
}

} // namespace engine::assetc
