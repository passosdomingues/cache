#include "engine/assetc/package.hpp"

#include <cstring>
#include <fstream>
#include <stdexcept>
#include <unordered_map>

namespace engine::assetc {

namespace {
constexpr char kMagic[8] = {'A', 'S', 'S', 'E', 'T', 'P', 'K', '2'};

void write_u32(std::ofstream& out, std::uint32_t value) {
    out.write(reinterpret_cast<const char*>(&value), sizeof(value));
}
void write_u64(std::ofstream& out, std::uint64_t value) {
    out.write(reinterpret_cast<const char*>(&value), sizeof(value));
}
void write_string(std::ofstream& out, const std::string& value) {
    write_u32(out, static_cast<std::uint32_t>(value.size()));
    out.write(value.data(), static_cast<std::streamsize>(value.size()));
}

std::uint32_t read_u32(std::ifstream& in) {
    std::uint32_t value = 0;
    in.read(reinterpret_cast<char*>(&value), sizeof(value));
    return value;
}
std::uint64_t read_u64(std::ifstream& in) {
    std::uint64_t value = 0;
    in.read(reinterpret_cast<char*>(&value), sizeof(value));
    return value;
}
std::string read_string(std::ifstream& in) {
    std::uint32_t len = read_u32(in);
    std::string value(len, '\0');
    if (len > 0) in.read(value.data(), len);
    return value;
}

void check_magic(std::ifstream& in, const std::filesystem::path& path) {
    char magic[8];
    in.read(magic, sizeof(magic));
    if (std::memcmp(magic, kMagic, sizeof(kMagic)) != 0) {
        throw std::runtime_error("arquivo nao e um game.pkg valido (magic incorreto): " + path.string());
    }
}
} // namespace

void write_package(const std::filesystem::path& out_path, const std::vector<AssetIRNode>& nodes) {
    if (out_path.has_parent_path()) {
        std::filesystem::create_directories(out_path.parent_path());
    }

    std::ofstream out(out_path, std::ios::binary | std::ios::trunc);
    if (!out) {
        throw std::runtime_error("nao foi possivel criar o pacote: " + out_path.string());
    }

    std::unordered_map<std::string, std::uint32_t> index_by_id;
    for (std::uint32_t i = 0; i < nodes.size(); ++i) {
        index_by_id[nodes[i].id] = i;
    }

    out.write(kMagic, sizeof(kMagic));
    write_u32(out, static_cast<std::uint32_t>(nodes.size()));

    std::vector<std::uint64_t> offsets(nodes.size());
    std::uint64_t running_offset = 0;
    for (std::size_t i = 0; i < nodes.size(); ++i) {
        offsets[i] = running_offset;
        running_offset += nodes[i].payload.size();
    }

    for (std::size_t i = 0; i < nodes.size(); ++i) {
        const auto& node = nodes[i];
        write_string(out, node.id);
        write_string(out, node.type);
        write_string(out, node.source_path);
        write_u64(out, node.content_hash);

        write_u32(out, static_cast<std::uint32_t>(node.dependencies.size()));
        for (const auto& dep_id : node.dependencies) {
            auto it = index_by_id.find(dep_id);
            if (it == index_by_id.end()) {
                throw std::runtime_error("dependencia desconhecida ao empacotar '" + node.id + "': " + dep_id);
            }
            write_u32(out, it->second);
        }

        write_u32(out, static_cast<std::uint32_t>(node.metadata.size()));
        for (const auto& [key, value] : node.metadata) {
            write_string(out, key);
            write_string(out, value);
        }

        write_u64(out, offsets[i]);
        write_u64(out, static_cast<std::uint64_t>(node.payload.size()));
    }

    for (const auto& node : nodes) {
        if (!node.payload.empty()) {
            out.write(reinterpret_cast<const char*>(node.payload.data()),
                      static_cast<std::streamsize>(node.payload.size()));
        }
    }
}

PackageInfo read_package_info(const std::filesystem::path& path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) {
        throw std::runtime_error("nao foi possivel abrir o pacote: " + path.string());
    }
    check_magic(in, path);

    std::uint32_t count = read_u32(in);
    PackageInfo info;
    info.assets.resize(count);

    std::vector<std::vector<std::uint32_t>> dep_indices(count);

    for (std::uint32_t i = 0; i < count; ++i) {
        PackageAssetInfo& asset = info.assets[i];
        asset.id = read_string(in);
        asset.type = read_string(in);
        asset.source_path = read_string(in);
        asset.content_hash = read_u64(in);

        std::uint32_t dep_count = read_u32(in);
        dep_indices[i].resize(dep_count);
        for (std::uint32_t d = 0; d < dep_count; ++d) {
            dep_indices[i][d] = read_u32(in);
        }

        std::uint32_t meta_count = read_u32(in);
        for (std::uint32_t m = 0; m < meta_count; ++m) {
            std::string key = read_string(in);
            std::string value = read_string(in);
            asset.metadata.emplace_back(std::move(key), std::move(value));
        }

        read_u64(in); // offset (não necessário para metadados)
        asset.payload_size = read_u64(in);
    }

    for (std::uint32_t i = 0; i < count; ++i) {
        for (auto dep_index : dep_indices[i]) {
            info.assets[i].dependencies.push_back(info.assets[dep_index].id);
        }
    }

    return info;
}

std::vector<unsigned char> read_package_payload(const std::filesystem::path& path, const std::string& asset_id) {
    std::ifstream in(path, std::ios::binary);
    if (!in) {
        throw std::runtime_error("nao foi possivel abrir o pacote: " + path.string());
    }
    check_magic(in, path);

    std::uint32_t count = read_u32(in);
    std::uint64_t found_offset = 0, found_size = 0;
    bool found = false;

    for (std::uint32_t i = 0; i < count; ++i) {
        std::string id = read_string(in);
        read_string(in); // type
        read_string(in); // source_path
        read_u64(in);    // content_hash

        std::uint32_t dep_count = read_u32(in);
        for (std::uint32_t d = 0; d < dep_count; ++d) read_u32(in);

        std::uint32_t meta_count = read_u32(in);
        for (std::uint32_t m = 0; m < meta_count; ++m) {
            read_string(in);
            read_string(in);
        }

        std::uint64_t offset = read_u64(in);
        std::uint64_t size = read_u64(in);

        if (id == asset_id) {
            found = true;
            found_offset = offset;
            found_size = size;
        }
    }

    if (!found) {
        throw std::runtime_error("asset nao encontrado no pacote: " + asset_id);
    }

    auto blob_start = in.tellg();
    in.seekg(static_cast<std::streamoff>(blob_start) + static_cast<std::streamoff>(found_offset));

    std::vector<unsigned char> payload(found_size);
    if (found_size > 0) {
        in.read(reinterpret_cast<char*>(payload.data()), static_cast<std::streamsize>(found_size));
    }
    return payload;
}

} // namespace engine::assetc
