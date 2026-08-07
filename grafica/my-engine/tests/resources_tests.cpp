#include "test_framework.hpp"

#include "engine/jobs/job_system.hpp"
#include "engine/pkg/compression.hpp"
#include "engine/pkg/format.hpp"
#include "engine/resources/resource_manager.hpp"

#include <filesystem>
#include <functional>
#include <string>

using namespace engine::resources;
using namespace engine::pkg;
namespace fs = std::filesystem;

namespace {

fs::path make_temp_dir(const std::string& name) {
    auto dir = fs::temp_directory_path() / "engine_resources_tests" / name;
    std::error_code ec;
    fs::remove_all(dir, ec);
    fs::create_directories(dir);
    return dir;
}

// Constrói um game.pkg minimo diretamente via engine::pkg (sem depender
// do assetc): um asset "raw" (payload cru, sem metadata de compressão) e
// um asset "compressed" (simulando o que image/atlas/audio produzem).
void write_test_package(const fs::path& path, const std::string& raw_content, const std::string& compressed_source) {
    std::vector<unsigned char> raw_bytes(raw_content.begin(), raw_content.end());

    std::vector<unsigned char> source_bytes(compressed_source.begin(), compressed_source.end());
    auto compressed_bytes = deflate_compress(source_bytes);

    // Hash derivado do conteúdo real (não fixo!) — senão poll_hot_reload
    // nunca detecta mudança entre duas chamadas com conteúdos diferentes.
    std::uint64_t raw_hash = static_cast<std::uint64_t>(std::hash<std::string>{}(raw_content));
    std::uint64_t packed_hash = static_cast<std::uint64_t>(std::hash<std::string>{}(compressed_source));

    std::vector<PackageEntry> entries;
    entries.push_back(PackageEntry{
        "plain", "raw", "", raw_hash, {}, {}, raw_bytes,
    });
    entries.push_back(PackageEntry{
        "packed", "image", "", packed_hash, {},
        {{"uncompressed_size", std::to_string(source_bytes.size())}},
        compressed_bytes,
    });

    write_package(path, entries);
}

} // namespace

TEST_CASE(resource_manager_lists_asset_ids) {
    auto dir = make_temp_dir("list_ids");
    write_test_package(dir / "test.pkg", "conteudo cru", "conteudo comprimido");

    ResourceManager manager(dir / "test.pkg");
    auto ids = manager.asset_ids();
    CHECK(ids.size() == 2);
}

TEST_CASE(resource_manager_acquire_decompresses_and_release_evicts) {
    auto dir = make_temp_dir("acquire_release");
    write_test_package(dir / "test.pkg", "conteudo cru", "ola engine descomprimida");

    ResourceManager manager(dir / "test.pkg");

    auto handle = manager.acquire("packed");
    CHECK(handle.valid());
    CHECK(manager.is_resident(handle));
    CHECK(manager.ref_count(handle) == 1);

    auto* data = manager.data(handle);
    CHECK(data != nullptr);
    if (data) {
        std::string text(data->begin(), data->end());
        CHECK(text == "ola engine descomprimida");
    }

    manager.release(handle);
    CHECK(!manager.is_resident(handle));
    CHECK(manager.ref_count(handle) == 0);
}

TEST_CASE(resource_manager_raw_asset_passes_through_without_decompression) {
    auto dir = make_temp_dir("raw_passthrough");
    write_test_package(dir / "test.pkg", "bytes crus sem compressao", "irrelevante");

    ResourceManager manager(dir / "test.pkg");
    auto handle = manager.acquire("plain");
    auto* data = manager.data(handle);
    CHECK(data != nullptr);
    if (data) {
        std::string text(data->begin(), data->end());
        CHECK(text == "bytes crus sem compressao");
    }
}

TEST_CASE(resource_manager_reference_counting_shares_handle) {
    auto dir = make_temp_dir("refcounting");
    write_test_package(dir / "test.pkg", "raw", "compressed content here");

    ResourceManager manager(dir / "test.pkg");
    auto h1 = manager.acquire("packed");
    auto h2 = manager.acquire("packed");
    CHECK(h1 == h2);
    CHECK(manager.ref_count(h1) == 2);

    manager.release(h1);
    CHECK(manager.is_resident(h2)); // ainda residente, refcount == 1
    manager.release(h2);
    CHECK(!manager.is_resident(h2));
}

TEST_CASE(resource_manager_invalid_and_stale_handles) {
    auto dir = make_temp_dir("stale_handles");
    write_test_package(dir / "test.pkg", "raw", "compressed content");

    ResourceManager manager(dir / "test.pkg");

    auto missing = manager.acquire("nao_existe");
    CHECK(!missing.valid());
    CHECK(manager.data(missing) == nullptr);

    ResourceHandle fake{999, 1};
    CHECK(manager.data(fake) == nullptr);
    CHECK(!manager.is_resident(fake));
}

TEST_CASE(resource_manager_acquire_async_via_job_system) {
    auto dir = make_temp_dir("async_acquire");
    write_test_package(dir / "test.pkg", "raw", "conteudo assincrono");

    engine::jobs::JobSystem job_system(2);
    ResourceManager manager(dir / "test.pkg", &job_system);

    auto future = manager.acquire_async("packed");
    auto handle = future.get();
    CHECK(handle.valid());
    CHECK(manager.is_resident(handle));

    auto* data = manager.data(handle);
    CHECK(data != nullptr);
    if (data) {
        std::string text(data->begin(), data->end());
        CHECK(text == "conteudo assincrono");
    }
}

TEST_CASE(resource_manager_hot_reload_updates_resident_payload) {
    auto dir = make_temp_dir("hot_reload");
    auto pkg_path = dir / "test.pkg";
    write_test_package(pkg_path, "raw", "versao 1 do conteudo");

    ResourceManager manager(pkg_path);
    auto handle = manager.acquire("packed");

    auto* data_v1 = manager.data(handle);
    CHECK(data_v1 != nullptr);
    if (data_v1) {
        CHECK(std::string(data_v1->begin(), data_v1->end()) == "versao 1 do conteudo");
    }

    // Reescreve o mesmo pacote no disco com conteudo diferente (mesmo id,
    // hash diferente) — simula uma recompilacao do assetc em background.
    write_test_package(pkg_path, "raw", "versao 2, atualizada!");

    int reloaded = manager.poll_hot_reload();
    CHECK(reloaded == 1); // so 'packed' estava residente; 'plain' nao conta

    auto* data_v2 = manager.data(handle); // mesmo handle, conteudo novo
    CHECK(data_v2 != nullptr);
    if (data_v2) {
        CHECK(std::string(data_v2->begin(), data_v2->end()) == "versao 2, atualizada!");
    }
}

TEST_CASE(resource_manager_hot_reload_ignores_non_resident_changes) {
    auto dir = make_temp_dir("hot_reload_non_resident");
    auto pkg_path = dir / "test.pkg";
    write_test_package(pkg_path, "raw", "conteudo original");

    ResourceManager manager(pkg_path); // nada adquirido ainda

    write_test_package(pkg_path, "raw", "conteudo mudou mas ninguem tinha adquirido");
    int reloaded = manager.poll_hot_reload();
    CHECK(reloaded == 0); // nada residente para recarregar
}

int main() {
    return engine::testing::run_all();
}
