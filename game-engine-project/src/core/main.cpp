#include <atomic>
#include <chrono>
#include <cstdio>
#include <thread>
#include <vector>

#include "version.hpp"

namespace {

// Benchmark inicial do Sprint 0: mede o custo de "acordar" N threads e
// fazê-las incrementar um contador atômico. Não mede nada sofisticado —
// serve apenas como baseline documentado, para comparação com o
// benchmark do Job System real (Sprint 2).
long long benchmark_thread_wakeup(unsigned thread_count) {
    using clock = std::chrono::steady_clock;

    std::atomic<long long> counter{0};
    std::vector<std::thread> threads;
    threads.reserve(thread_count);

    const auto start = clock::now();

    for (unsigned i = 0; i < thread_count; ++i) {
        threads.emplace_back([&counter] {
            counter.fetch_add(1, std::memory_order_relaxed);
        });
    }
    for (auto& t : threads) {
        t.join();
    }

    const auto end = clock::now();
    const auto elapsed_us =
        std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();

    std::printf("[benchmark] %u threads, contador final = %lld, tempo = %lld us\n",
                thread_count, counter.load(), static_cast<long long>(elapsed_us));

    return elapsed_us;
}

} // namespace

int main() {
    const auto v = engine::core::kEngineVersion;
    std::printf("hello-engine v%d.%d.%d\n", v.major, v.minor, v.patch);
    std::printf("Sprint 0 — Fundamentos. A engine compila e roda.\n");

    const unsigned hw_threads = std::thread::hardware_concurrency();
    std::printf("hardware_concurrency() = %u\n", hw_threads);

    benchmark_thread_wakeup(hw_threads > 0 ? hw_threads : 4);

    return 0;
}
