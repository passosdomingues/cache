#pragma once
#include <cstddef>
#include <cstdint>
#include <memory>

namespace engine::platform {

// Alocador em arena (bump allocator): aloca sequencialmente de um bloco
// fixo, sem liberação individual — apenas reset() completo. Pensado para
// alocações de curta duração dentro de um frame ou de uma compilação de
// asset (RFC 02), evitando `new`/`malloc` no caminho crítico.
class ArenaAllocator {
public:
    explicit ArenaAllocator(std::size_t capacity_bytes);

    void* allocate(std::size_t size, std::size_t alignment = alignof(std::max_align_t));
    void reset();

    std::size_t capacity() const { return capacity_; }
    std::size_t used() const { return offset_; }

private:
    std::unique_ptr<std::byte[]> buffer_;
    std::size_t capacity_;
    std::size_t offset_ = 0;
};

// Alocador de pool para blocos de tamanho fixo (ex.: componentes ECS no
// Sprint 8). Blocos livres encadeados em uma free-list intrusiva.
class PoolAllocator {
public:
    PoolAllocator(std::size_t block_size, std::size_t block_count);

    void* allocate();
    void deallocate(void* ptr);

    std::size_t block_size() const { return block_size_; }
    std::size_t block_count() const { return block_count_; }
    std::size_t free_count() const;

private:
    std::unique_ptr<std::byte[]> buffer_;
    std::size_t block_size_;
    std::size_t block_count_;
    void* free_list_ = nullptr;
};

} // namespace engine::platform
