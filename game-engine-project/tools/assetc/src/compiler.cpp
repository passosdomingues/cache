#include "engine/assetc/compiler.hpp"
#include "engine/assetc/build_cache.hpp"
#include "engine/assetc/frontend.hpp"
#include "engine/assetc/hash.hpp"
#include "engine/assetc/package.hpp"
#include "engine/platform/logger.hpp"

#include <functional>
#include <stdexcept>
#include <unordered_map>
#include <unordered_set>

namespace engine::assetc {

std::vector<SourceAsset> topological_order(const AssetManifest& manifest) {
    std::unordered_map<std::string, const SourceAsset*> by_id;
    for (const auto& asset : manifest.assets) {
        if (by_id.count(asset.id)) {
            throw std::runtime_error("asset id duplicado no manifesto: " + asset.id);
        }
        by_id[asset.id] = &asset;
    }
    for (const auto& asset : manifest.assets) {
        for (const auto& dep : asset.dependencies) {
            if (!by_id.count(dep)) {
                throw std::runtime_error("asset '" + asset.id + "' depende de id desconhecido: " + dep);
            }
        }
    }

    std::vector<SourceAsset> ordered;
    ordered.reserve(manifest.assets.size());

    enum class Mark { Unvisited, Visiting, Done };
    std::unordered_map<std::string, Mark> marks;
    for (const auto& asset : manifest.assets) marks[asset.id] = Mark::Unvisited;

    std::function<void(const SourceAsset&)> visit = [&](const SourceAsset& asset) {
        Mark& mark = marks[asset.id];
        if (mark == Mark::Done) return;
        if (mark == Mark::Visiting) {
            throw std::runtime_error("ciclo de dependencias detectado envolvendo: " + asset.id);
        }
        mark = Mark::Visiting;
        for (const auto& dep_id : asset.dependencies) {
            visit(*by_id.at(dep_id));
        }
        mark = Mark::Done;
        ordered.push_back(asset);
    };

    for (const auto& asset : manifest.assets) {
        visit(asset);
    }
    return ordered;
}

BuildStats build(const BuildOptions& options) {
    AssetManifest manifest = load_manifest(options.manifest_path);
    std::vector<SourceAsset> ordered = topological_order(manifest);

    BuildCache cache(options.cache_dir);
    if (!options.force) {
        cache.load();
    }
    std::filesystem::create_directories(options.cache_dir / "objects");

    std::vector<AssetIRNode> nodes;
    nodes.reserve(ordered.size());

    // Ids recompilados nesta rodada — usado para propagar invalidação de
    // cache pelo grafo de dependências: se uma dependência foi
    // recompilada, quem depende dela também é, mesmo que o próprio
    // arquivo fonte não tenha mudado (necessário para front-ends futuros
    // cujo resultado depende do conteúdo das dependências, ex.: atlas).
    std::unordered_set<std::string> dirty_ids;

    BuildStats stats;
    stats.total = static_cast<int>(ordered.size());

    for (const auto& source : ordered) {
        const FrontendInfo* frontend = FrontendRegistry::instance().find(source.type);
        if (!frontend) {
            throw std::runtime_error("asset '" + source.id + "': tipo desconhecido '" + source.type + "'");
        }

        std::uint64_t source_hash = hash_file(source.source_path);
        std::string frontend_tag = source.type + "@" + std::to_string(frontend->version);

        bool deps_dirty = false;
        for (const auto& dep_id : source.dependencies) {
            if (dirty_ids.count(dep_id)) {
                deps_dirty = true;
                break;
            }
        }

        const CacheEntry* cached = options.force ? nullptr : cache.find(source.id);
        bool cache_hit = !deps_dirty && cached != nullptr
            && cached->source_hash == source_hash
            && cached->frontend == frontend_tag
            && cached->dependencies == source.dependencies;

        AssetIRNode node;
        node.id = source.id;
        node.type = source.type;
        node.source_path = source.source_path.string();
        node.dependencies = source.dependencies;
        node.content_hash = source_hash;

        if (cache_hit) {
            auto payload = cache.load_object(cached->output_hash);
            if (payload) {
                node.payload = std::move(*payload);
                stats.cache_hits++;
                ENGINE_LOG_DEBUG("assetc", "cache hit: " + source.id);
            } else {
                cache_hit = false; // objeto sumiu do cache; recompila
            }
        }

        if (!cache_hit) {
            node = frontend->compile(source);
            node.content_hash = source_hash;

            std::uint64_t output_hash = fnv1a_64(node.payload.data(), node.payload.size());
            cache.store_object(output_hash, node.payload);
            cache.put(source.id, CacheEntry{
                source.type, source.source_path.string(), source_hash,
                frontend_tag, source.dependencies, output_hash,
            });

            dirty_ids.insert(source.id);
            stats.compiled++;
            ENGINE_LOG_DEBUG("assetc", "compilado: " + source.id);
        }

        nodes.push_back(std::move(node));
    }

    write_package(options.output_path, nodes);
    cache.save();

    return stats;
}

} // namespace engine::assetc
