#pragma once
#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

namespace engine::platform {

// Parser de linha de comando minimalista: opções no formato
// --chave=valor ou --flag (booleana), mais argumentos posicionais.
class CommandLineParser {
public:
    void parse(int argc, char** argv);

    bool has_flag(const std::string& name) const;
    std::optional<std::string> get_option(const std::string& name) const;
    std::string get_option(const std::string& name, const std::string& fallback) const;
    const std::vector<std::string>& positional_args() const { return positional_; }

private:
    std::unordered_map<std::string, std::string> options_;
    std::vector<std::string> flags_;
    std::vector<std::string> positional_;
};

} // namespace engine::platform
