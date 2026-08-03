#pragma once
#include <atomic>
#include <cstdint>
#include <limits>
#include <mutex>
#include <semaphore>

namespace engine::platform {

using Mutex = std::mutex;
using ScopedLock = std::lock_guard<std::mutex>;

// Semáforo contável — alias sobre a implementação padrão de C++20.
template <std::ptrdiff_t LeastMaxValue = std::numeric_limits<std::ptrdiff_t>::max()>
using CountingSemaphore = std::counting_semaphore<LeastMaxValue>;
using BinarySemaphore = std::binary_semaphore;

// Contador atômico simples, para métricas e sincronização básica
// (ex.: jobs concluídos no Job System do Sprint 2).
class AtomicCounter {
public:
    explicit AtomicCounter(std::int64_t initial = 0) : value_(initial) {}

    std::int64_t increment(std::int64_t by = 1) { return value_.fetch_add(by, std::memory_order_relaxed) + by; }
    std::int64_t decrement(std::int64_t by = 1) { return value_.fetch_sub(by, std::memory_order_relaxed) - by; }
    std::int64_t load() const { return value_.load(std::memory_order_relaxed); }
    void store(std::int64_t v) { value_.store(v, std::memory_order_relaxed); }

private:
    std::atomic<std::int64_t> value_;
};

} // namespace engine::platform
