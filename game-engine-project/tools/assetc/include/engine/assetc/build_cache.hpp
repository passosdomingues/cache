#pragma once
#include <cstdint>
#include <filesystem>
#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

namespace engine::assetc {

struct CacheEntry {
    std::string type;
    std::string source_path;
    std::uint64_t source_hash = 0;
    std::string frontend;                   // ex.: "raw@1"
    std::vector<std::string> dependencies;
    std::uint64_t output_hash = 0;          // hash do payload já compilado
};

// Cache de build endereçado por conteúdo (RFC 02 — "cache por hash de
// conteúdo, não por timestamp de arquivo"). Dois níveis:
//   - manifesto: <cache_dir>/manifest.txt — metadados por asset id
//   - object store: <cache_dir>/objects/<hash> — bytes já compilados
class BuildCache {
public:
    explicit BuildCache(std::filesystem::path cache_dir);

    void load();
    void save() const;

    const CacheEntry* find(const std::string& asset_id) const;
    void put(const std::string& asset_id, CacheEntry entry);

    std::optional<std::vector<unsigned char>> load_object(std::uint64_t hash) const;
    void store_object(std::uint64_t hash, const std::vector<unsigned char>& payload) const;

private:
    std::filesystem::path cache_dir_;
    std::unordered_map<std::string, CacheEntry> entries_;
};

} // namespace engine::assetc
