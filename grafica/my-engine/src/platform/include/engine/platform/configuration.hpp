#pragma once
#include <filesystem>
#include <optional>
#include <string>
#include <unordered_map>

namespace engine::platform {

// Configuração simples baseada em pares chave=valor (uma por linha,
// '#' inicia comentário). Não é o formato de dados de jogo (RFC 02) —
// serve para configuração de baixo nível da engine/toolchain.
class Configuration {
public:
    bool load_from_file(const std::filesystem::path& path);
    void load_from_string(const std::string& content);

    std::optional<std::string> get_string(const std::string& key) const;
    std::string get_string(const std::string& key, const std::string& fallback) const;
    int get_int(const std::string& key, int fallback) const;
    bool get_bool(const std::string& key, bool fallback) const;

    void set(const std::string& key, const std::string& value);
    std::size_t size() const { return values_.size(); }

private:
    std::unordered_map<std::string, std::string> values_;
};

} // namespace engine::platform
