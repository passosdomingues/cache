#include "engine/assetc/block_format.hpp"

#include <sstream>

namespace engine::assetc {

namespace {
std::string trim(const std::string& s) {
    auto start = s.find_first_not_of(" \t\r\n");
    if (start == std::string::npos) return "";
    auto end = s.find_last_not_of(" \t\r\n");
    return s.substr(start, end - start + 1);
}
} // namespace

std::string Block::get(const std::string& key, const std::string& fallback) const {
    for (const auto& [k, v] : fields) {
        if (k == key) return v;
    }
    return fallback;
}

std::vector<Block> parse_blocks(const std::string& content) {
    std::vector<Block> blocks;
    std::istringstream stream(content);
    std::string line;
    Block* current = nullptr;

    while (std::getline(stream, line)) {
        std::string trimmed = trim(line);
        if (trimmed.empty() || trimmed[0] == '#') continue;

        if (trimmed.front() == '[' && trimmed.back() == ']' && trimmed.size() >= 2) {
            blocks.push_back(Block{trimmed.substr(1, trimmed.size() - 2), {}});
            current = &blocks.back();
            continue;
        }

        auto eq = trimmed.find('=');
        if (eq == std::string::npos || current == nullptr) continue;

        std::string key = trim(trimmed.substr(0, eq));
        std::string value = trim(trimmed.substr(eq + 1));
        if (!key.empty()) {
            current->fields.emplace_back(key, value);
        }
    }
    return blocks;
}

std::string serialize_blocks(const std::vector<Block>& blocks) {
    std::ostringstream out;
    for (const auto& block : blocks) {
        out << "[" << block.name << "]\n";
        for (const auto& [k, v] : block.fields) {
            out << k << "=" << v << "\n";
        }
        out << "\n";
    }
    return out.str();
}

} // namespace engine::assetc
