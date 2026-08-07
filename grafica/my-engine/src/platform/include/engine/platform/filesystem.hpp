#pragma once
#include <cstdint>
#include <filesystem>
#include <optional>
#include <string>
#include <vector>

namespace engine::platform::fs {

namespace stdfs = std::filesystem;

bool exists(const stdfs::path& path);
bool create_directories(const stdfs::path& path);
std::optional<std::string> read_text_file(const stdfs::path& path);
bool write_text_file(const stdfs::path& path, const std::string& content);
std::optional<std::uintmax_t> file_size(const stdfs::path& path);
std::vector<stdfs::path> list_directory(const stdfs::path& path);
bool remove(const stdfs::path& path);

} // namespace engine::platform::fs
