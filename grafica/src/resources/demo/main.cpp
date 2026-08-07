#include "engine/jobs/job_system.hpp"
#include "engine/platform/cli.hpp"
#include "engine/resources/resource_manager.hpp"

#include <cstdio>
#include <exception>

using namespace engine;

// Entrega do Sprint 6: demonstra o Resource Manager completo sobre um
// game.pkg real (produzido pelo assetc) — streaming (payload só carrega
// no primeiro acquire), cache com reference counting, handles com
// geração, carregamento assíncrono via Job System, e o mecanismo de hot
// reload.
int main(int argc, char** argv) {
    platform::CommandLineParser args;
    args.parse(argc, argv);

    auto package_path = args.get_option("package");
    if (!package_path) {
        std::fprintf(stderr, "uso: resource-demo --package=<caminho.pkg>\n");
        return 2;
    }

    try {
        jobs::JobSystem job_system(2);
        resources::ResourceManager manager(*package_path, &job_system);

        std::printf("Pacote carregado: %s\n", package_path->c_str());
        auto ids = manager.asset_ids();
        std::printf("Assets disponiveis (%zu):\n", ids.size());
        for (const auto& id : ids) {
            std::printf("  - %s\n", id.c_str());
        }
        if (ids.empty()) {
            std::printf("(pacote vazio, nada para demonstrar)\n");
            return 0;
        }

        const std::string first = ids.front();

        std::printf("\n== acquire('%s') ==\n", first.c_str());
        auto handle = manager.acquire(first);
        std::printf("handle: index=%u generation=%u\n", handle.index, handle.generation);
        std::printf("residente: %s | refcount: %d | bytes: %zu | tipo: %s\n",
                     manager.is_resident(handle) ? "sim" : "nao",
                     manager.ref_count(handle),
                     manager.data(handle) ? manager.data(handle)->size() : 0,
                     manager.type_of(handle).c_str());

        std::printf("\n== acquire('%s') de novo (refcount sobe, mesmo handle) ==\n", first.c_str());
        auto handle2 = manager.acquire(first);
        std::printf("mesmo handle: %s | refcount: %d\n",
                     (handle == handle2) ? "sim" : "nao", manager.ref_count(handle));

        std::printf("\n== release() uma vez ==\n");
        manager.release(handle);
        std::printf("residente: %s | refcount: %d\n",
                     manager.is_resident(handle2) ? "sim" : "nao", manager.ref_count(handle2));

        std::printf("\n== release() de novo (refcount chega a 0 -> evict) ==\n");
        manager.release(handle2);
        std::printf("residente: %s\n", manager.is_resident(handle2) ? "sim" : "nao");

        std::printf("\n== acquire_async('%s') via Job System ==\n", first.c_str());
        auto future = manager.acquire_async(first);
        auto async_handle = future.get();
        std::printf("carregado via job: residente=%s | bytes=%zu\n",
                     manager.is_resident(async_handle) ? "sim" : "nao",
                     manager.data(async_handle) ? manager.data(async_handle)->size() : 0);
        manager.release(async_handle);

        std::printf("\n== poll_hot_reload() ==\n");
        int reloaded = manager.poll_hot_reload();
        std::printf("%d recurso(s) recarregado(s) (nenhuma mudanca no arquivo desde o load = 0 esperado)\n",
                     reloaded);

        return 0;
    } catch (const std::exception& e) {
        std::fprintf(stderr, "resource-demo: erro: %s\n", e.what());
        return 1;
    }
}
