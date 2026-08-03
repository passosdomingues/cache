#include "engine/platform/cli.hpp"

namespace engine::platform {

void CommandLineParser::parse(int argc, char** argv) {
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg.rfind("--", 0) == 0) {
            std::string body = arg.substr(2);
            auto eq = body.find('=');
            if (eq == std::string::npos) {
                flags_.push_back(body);
            } else {
                options_[body.substr(0, eq)] = body.substr(eq + 1);
            }
        } else {
            positional_.push_back(arg);
        }
    }
}

bool CommandLineParser::has_flag(const std::string& name) const {
    for (const auto& f : flags_) {
        if (f == name) return true;
    }
    return options_.find(name) != options_.end();
}

std::optional<std::string> CommandLineParser::get_option(const std::string& name) const {
    auto it = options_.find(name);
    if (it == options_.end()) return std::nullopt;
    return it->second;
}

std::string CommandLineParser::get_option(const std::string& name, const std::string& fallback) const {
    auto it = options_.find(name);
    return it == options_.end() ? fallback : it->second;
}

} // namespace engine::platform
