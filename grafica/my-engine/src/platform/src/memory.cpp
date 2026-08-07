#include "engine/platform/memory.hpp"

#include <cstdint>

namespace engine::platform {

ArenaAllocator::ArenaAllocator(std::size_t capacity_bytes)
    : buffer_(std::make_unique<std::byte[]>(capacity_bytes)),
      capacity_(capacity_bytes) {}

void* ArenaAllocator::allocate(std::size_t size, std::size_t alignment) {
    auto current = reinterpret_cast<std::uintptr_t>(buffer_.get()) + offset_;
    auto aligned = (current + (alignment - 1)) & ~(alignment - 1);
    std::size_t adjustment = static_cast<std::size_t>(aligned - current);

    if (offset_ + adjustment + size > capacity_) {
        return nullptr;
    }
    offset_ += adjustment + size;
    return reinterpret_cast<void*>(aligned);
}

void ArenaAllocator::reset() {
    offset_ = 0;
}

PoolAllocator::PoolAllocator(std::size_t block_size, std::size_t block_count)
    : block_size_(block_size < sizeof(void*) ? sizeof(void*) : block_size),
      block_count_(block_count) {
    buffer_ = std::make_unique<std::byte[]>(block_size_ * block_count_);
    for (std::size_t i = 0; i < block_count_; ++i) {
        std::byte* block = buffer_.get() + i * block_size_;
        *reinterpret_cast<void**>(block) = free_list_;
        free_list_ = block;
    }
}

void* PoolAllocator::allocate() {
    if (!free_list_) return nullptr;
    void* block = free_list_;
    free_list_ = *reinterpret_cast<void**>(block);
    return block;
}

void PoolAllocator::deallocate(void* ptr) {
    if (!ptr) return;
    *reinterpret_cast<void**>(ptr) = free_list_;
    free_list_ = ptr;
}

std::size_t PoolAllocator::free_count() const {
    std::size_t count = 0;
    void* cur = free_list_;
    while (cur) {
        ++count;
        cur = *reinterpret_cast<void**>(cur);
    }
    return count;
}

} // namespace engine::platform
