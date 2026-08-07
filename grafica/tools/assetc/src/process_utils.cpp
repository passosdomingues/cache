#include "process_utils.hpp"

#include <array>
#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <memory>
#include <stdexcept>
#include <unistd.h>

namespace engine::assetc::detail {

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

} // namespace engine::assetc::detail
