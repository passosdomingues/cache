#pragma once
#include "engine/jobs/job_system.hpp"
#include "engine/pkg/format.hpp"
#include "engine/platform/sync.hpp"
#include "engine/resources/handle.hpp"

#include <cstdint>
#include <filesystem>
#include <string>
#include <unordered_map>
#include <vector>

namespace engine::resources {

// Gerencia recursos carregados de um game.pkg (RFC 03 — Runtime):
//
//   - Streaming: o payload de um asset só é descomprimido no primeiro
//     acquire() — carregar o pacote (load_package) só lê a tabela de
//     metadados, nunca os blobs.
//   - Cache + Reference Counting: acquire() incrementa um contador;
//     release() decrementa e, ao chegar a zero, libera o payload da
//     memória (mas mantém a metadata — pode ser readquirido depois).
//   - Handle: índice + geração, para detectar uso de um handle "stale"
//     (ex.: após o slot ser reciclado).
//   - Hot Reload: poll_hot_reload() relê a tabela do .pkg em disco e
//     substitui o payload de recursos residentes cujo content_hash mudou.
//
// Thread-safety: todos os métodos públicos são protegidos por um mutex
// interno. A descompressão de um asset acontece com o mutex retido —
// simplifica a implementação às custas de paralelismo entre acquires
// concorrentes de assets diferentes (ver comentário em `acquire`).
class ResourceManager {
public:
    // job_system pode ser nullptr se o chamador só for usar acquire()
    // síncrono; acquire_async() exige um JobSystem válido.
    explicit ResourceManager(std::filesystem::path package_path, jobs::JobSystem* job_system = nullptr);

    // Relê a tabela de metadados do pacote (não carrega payloads). Já é
    // chamado uma vez pelo construtor.
    void load_package();

    std::vector<std::string> asset_ids() const;

    // Adquire um recurso pelo id do asset: incrementa o refcount; se
    // ainda não residente, descomprime o payload (síncrono, bloqueia a
    // chamada). Retorna kInvalidHandle se o id não existir no pacote.
    ResourceHandle acquire(const std::string& asset_id);

    // Como acquire(), mas a descompressão roda em uma job do Job System
    // (Sprint 2) — o Future resolve quando o recurso já está residente.
    // Requer que o ResourceManager tenha sido construído com um
    // JobSystem válido.
    jobs::Future<ResourceHandle> acquire_async(const std::string& asset_id);

    // Decrementa o refcount; ao chegar a zero, libera o payload da
    // memória (mantém metadata, pode ser adquirido de novo depois).
    void release(ResourceHandle handle);

    bool is_resident(ResourceHandle handle) const;
    int ref_count(ResourceHandle handle) const;

    // Bytes descomprimidos do recurso — só significativo enquanto
    // residente (ref_count > 0). Retorna nullptr se o handle for
    // inválido/stale ou o recurso não estiver residente.
    const std::vector<unsigned char>* data(ResourceHandle handle) const;

    std::string type_of(ResourceHandle handle) const;
    std::string metadata(ResourceHandle handle, const std::string& key, const std::string& fallback = "") const;

    // Relê a tabela do .pkg em disco; para cada recurso RESIDENTE cujo
    // content_hash mudou, descomprime o novo payload e substitui (o
    // handle continua válido — só o conteúdo muda). Ids novos no
    // arquivo ganham um slot (não residente); remoção de um id
    // existente não é tratada especialmente nesta versão (o slot antigo
    // fica órfão, mas seguro — uma tentativa de recarregá-lo lançaria
    // uma exceção normal de "asset não encontrado"). Retorna quantos
    // recursos foram efetivamente recarregados.
    int poll_hot_reload();

private:
    struct Slot {
        std::string id;
        std::uint32_t generation = 0;
        int ref_count = 0;
        bool resident = false;
        pkg::PackageAssetInfo info;
        std::vector<unsigned char> bytes;
    };

    Slot* find_slot_unlocked(ResourceHandle handle);
    const Slot* find_slot_unlocked(ResourceHandle handle) const;
    std::vector<unsigned char> load_and_decompress(const pkg::PackageAssetInfo& info) const;

    std::filesystem::path package_path_;
    jobs::JobSystem* job_system_ = nullptr;

    mutable platform::Mutex mutex_;
    std::vector<Slot> slots_;
    std::unordered_map<std::string, std::uint32_t> index_by_id_;
};

} // namespace engine::resources
