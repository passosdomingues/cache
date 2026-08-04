#include "engine/platform/filesystem.hpp"

#include <fstream>
#include <sstream>

namespace engine::platform::fs {

bool exists(const stdfs::path& path) {
    std::error_code ec;
    return stdfs::exists(path, ec);
}

bool create_directories(const stdfs::path& path) {
    std::error_code ec;
    stdfs::create_directories(path, ec);
    return !ec;
}

std::optional<std::string> read_text_file(const stdfs::path& path) {
    std::ifstream file(path, std::ios::in | std::ios::binary);
    if (!file) return std::nullopt;
    std::ostringstream ss;
    ss << file.rdbuf();
    return ss.str();
}

bool write_text_file(const stdfs::path& path, const std::string& content) {
    if (path.has_parent_path()) {
        std::error_code ec;
        stdfs::create_directories(path.parent_path(), ec);
    }
    std::ofstream file(path, std::ios::out | std::ios::binary | std::ios::trunc);
    if (!file) return false;
    file << content;
    return static_cast<bool>(file);
}

std::optional<std::uintmax_t> file_size(const stdfs::path& path) {
    std::error_code ec;
    auto size = stdfs::file_size(path, ec);
    if (ec) return std::nullopt;
    return size;
}

std::vector<stdfs::path> list_directory(const stdfs::path& path) {
    std::vector<stdfs::path> entries;
    std::error_code ec;
    if (!stdfs::exists(path, ec) || !stdfs::is_directory(path, ec)) return entries;
    for (const auto& entry : stdfs::directory_iterator(path, ec)) {
        entries.push_back(entry.path());
    }
    return entries;
}

bool remove(const stdfs::path& path) {
    std::error_code ec;
    return stdfs::remove(path, ec);
}

} // namespace engine::platform::fs
