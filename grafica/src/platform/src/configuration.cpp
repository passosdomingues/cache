#include "engine/platform/configuration.hpp"
#include "engine/platform/filesystem.hpp"

#include <algorithm>
#include <cctype>
#include <sstream>

namespace engine::platform {

namespace {
std::string trim(const std::string& s) {
    auto start = s.find_first_not_of(" \t\r\n");
    if (start == std::string::npos) return "";
    auto end = s.find_last_not_of(" \t\r\n");
    return s.substr(start, end - start + 1);
}
} // namespace

bool Configuration::load_from_file(const std::filesystem::path& path) {
    auto content = fs::read_text_file(path);
    if (!content) return false;
    load_from_string(*content);
    return true;
}

void Configuration::load_from_string(const std::string& content) {
    std::istringstream stream(content);
    std::string line;
    while (std::getline(stream, line)) {
        std::string trimmed = trim(line);
        if (trimmed.empty() || trimmed[0] == '#') continue;
        auto eq = trimmed.find('=');
        if (eq == std::string::npos) continue;
        std::string key = trim(trimmed.substr(0, eq));
        std::string value = trim(trimmed.substr(eq + 1));
        if (!key.empty()) {
            values_[key] = value;
        }
    }
}

std::optional<std::string> Configuration::get_string(const std::string& key) const {
    auto it = values_.find(key);
    if (it == values_.end()) return std::nullopt;
    return it->second;
}

std::string Configuration::get_string(const std::string& key, const std::string& fallback) const {
    auto it = values_.find(key);
    return it == values_.end() ? fallback : it->second;
}

int Configuration::get_int(const std::string& key, int fallback) const {
    auto it = values_.find(key);
    if (it == values_.end()) return fallback;
    try {
        return std::stoi(it->second);
    } catch (...) {
        return fallback;
    }
}

bool Configuration::get_bool(const std::string& key, bool fallback) const {
    auto it = values_.find(key);
    if (it == values_.end()) return fallback;
    std::string v = it->second;
    std::transform(v.begin(), v.end(), v.begin(), [](unsigned char c) { return std::tolower(c); });
    if (v == "true" || v == "1" || v == "yes") return true;
    if (v == "false" || v == "0" || v == "no") return false;
    return fallback;
}

void Configuration::set(const std::string& key, const std::string& value) {
    values_[key] = value;
}

} // namespace engine::platform
