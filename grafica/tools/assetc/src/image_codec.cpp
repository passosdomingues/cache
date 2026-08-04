#include "engine/assetc/image_codec.hpp"

#include <algorithm>
#include <array>
#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <unistd.h>

namespace engine::assetc {

namespace {

std::string shell_quote(const std::string& s) {
    std::string out = "'";
    for (char c : s) {
        if (c == '\'') out += "'\\''";
        else out += c;
    }
    out += "'";
    return out;
}

bool tool_available(const std::string& name) {
    std::string cmd = "command -v " + name + " > /dev/null 2>&1";
    return std::system(cmd.c_str()) == 0;
}

int run_command(const std::string& cmd) {
    return std::system(cmd.c_str());
}

std::vector<unsigned char> run_capture_binary(const std::string& command) {
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(command.c_str(), "r"), pclose);
    if (!pipe) {
        throw std::runtime_error("falha ao executar: " + command);
    }
    std::vector<unsigned char> output;
    std::array<unsigned char, 65536> buffer{};
    std::size_t n = 0;
    while ((n = std::fread(buffer.data(), 1, buffer.size(), pipe.get())) > 0) {
        output.insert(output.end(), buffer.begin(), buffer.begin() + static_cast<long>(n));
    }
    return output;
}

std::filesystem::path make_temp_path(const std::string& suffix) {
    static std::atomic<int> counter{0};
    auto dir = std::filesystem::temp_directory_path();
    return dir / ("assetc_" + std::to_string(::getpid()) + "_" + std::to_string(counter++) + suffix);
}

} // namespace

ImageBuffer load_and_transform_image(const std::filesystem::path& source, const ImageTransform& transform) {
    if (!tool_available("convert") || !tool_available("identify")) {
        throw std::runtime_error(
            "ImageMagick nao encontrado (comandos 'convert'/'identify'). "
            "Instale com: sudo apt install imagemagick");
    }
    if (!std::filesystem::exists(source)) {
        throw std::runtime_error("arquivo de imagem nao encontrado: " + source.string());
    }

    std::ostringstream transform_args;
    if (!transform.resize.empty()) {
        transform_args << " -resize " << shell_quote(transform.resize);
    }
    if (!transform.crop.empty()) {
        transform_args << " -crop " << shell_quote(transform.crop) << " +repage";
    }
    if (transform.pad > 0) {
        transform_args << " -bordercolor none -border " << transform.pad;
    }

    auto tmp_png = make_temp_path(".png");

    // Passo 1: aplica as transformacoes e materializa um PNG intermediario
    // (mais simples e confiavel do que tentar extrair dimensoes de um
    // stream cru sem cabecalho).
    std::string convert_cmd = "convert " + shell_quote(source.string()) + transform_args.str() +
                               " " + shell_quote(tmp_png.string()) + " 2>/dev/null";
    if (run_command(convert_cmd) != 0) {
        throw std::runtime_error("falha ao transformar imagem (convert): " + source.string());
    }

    // Passo 2: dimensoes finais (pos-transformacao).
    std::string identify_cmd = "identify -format '%w %h' " + shell_quote(tmp_png.string());
    auto dims_bytes = run_capture_binary(identify_cmd);
    std::string dims_text(dims_bytes.begin(), dims_bytes.end());
    std::istringstream dims_stream(dims_text);
    std::uint32_t width = 0, height = 0;
    dims_stream >> width >> height;
    if (width == 0 || height == 0) {
        std::filesystem::remove(tmp_png);
        throw std::runtime_error("nao foi possivel obter dimensoes da imagem: " + source.string());
    }

    // Passo 3: pixels RGBA8 crus.
    std::string raw_cmd = "convert " + shell_quote(tmp_png.string()) + " -depth 8 RGBA:-";
    auto pixels = run_capture_binary(raw_cmd);
    std::filesystem::remove(tmp_png);

    std::size_t expected = static_cast<std::size_t>(width) * height * 4;
    if (pixels.size() != expected) {
        throw std::runtime_error("tamanho de pixels inesperado para " + source.string() +
                                  " (esperado " + std::to_string(expected) +
                                  ", obtido " + std::to_string(pixels.size()) + ")");
    }

    ImageBuffer result;
    result.width = width;
    result.height = height;
    result.channels = 4;
    result.pixels = std::move(pixels);
    return result;
}

std::vector<ImageBuffer> generate_mipmaps(const ImageBuffer& base, unsigned max_levels) {
    std::vector<ImageBuffer> levels;
    levels.push_back(base);

    while (true) {
        if (max_levels != 0 && levels.size() >= max_levels) break;
        const ImageBuffer& prev = levels.back();
        if (prev.width <= 1 && prev.height <= 1) break;

        std::uint32_t next_w = std::max<std::uint32_t>(1, prev.width / 2);
        std::uint32_t next_h = std::max<std::uint32_t>(1, prev.height / 2);

        ImageBuffer next;
        next.width = next_w;
        next.height = next_h;
        next.channels = prev.channels;
        next.pixels.resize(static_cast<std::size_t>(next_w) * next_h * next.channels);

        for (std::uint32_t y = 0; y < next_h; ++y) {
            for (std::uint32_t x = 0; x < next_w; ++x) {
                std::uint32_t sx0 = std::min(prev.width - 1, x * 2);
                std::uint32_t sx1 = std::min(prev.width - 1, x * 2 + 1);
                std::uint32_t sy0 = std::min(prev.height - 1, y * 2);
                std::uint32_t sy1 = std::min(prev.height - 1, y * 2 + 1);

                for (std::uint32_t c = 0; c < next.channels; ++c) {
                    auto sample = [&](std::uint32_t sx, std::uint32_t sy) -> unsigned {
                        return prev.pixels[(static_cast<std::size_t>(sy) * prev.width + sx) * prev.channels + c];
                    };
                    unsigned sum = sample(sx0, sy0) + sample(sx1, sy0) + sample(sx0, sy1) + sample(sx1, sy1);
                    next.pixels[(static_cast<std::size_t>(y) * next_w + x) * next.channels + c] =
                        static_cast<unsigned char>(sum / 4);
                }
            }
        }

        levels.push_back(std::move(next));
    }
    return levels;
}

} // namespace engine::assetc
