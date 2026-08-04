#include "engine/jobs/job_system.hpp"

#include <atomic>
#include <chrono>
#include <cstdio>
#include <vector>

using namespace engine::jobs;

// Entrega do Sprint 2: sustentar 100.000 jobs sem deadlock, com um
// benchmark simples de throughput. Parte dos jobs é submetida em cadeias
// de dependência (job N+1 depende de job N) para exercitar o Dependency
// Graph, não só a fila plana.
int main() {
    constexpr int kJobCount = 100000;
    constexpr int kChainLength = 4;

    JobSystem js;
    std::atomic<long long> counter{0};

    const auto start = std::chrono::steady_clock::now();

    int submitted = 0;
    while (submitted < kJobCount) {
        std::vector<JobHandle> deps;
        for (int i = 0; i < kChainLength && submitted < kJobCount; ++i, ++submitted) {
            JobHandle handle = js.submit(
                [&counter](CancellationToken&) {
                    counter.fetch_add(1, std::memory_order_relaxed);
                },
                deps);
            deps = {handle};
        }
    }

    js.wait_all();

    const auto end = std::chrono::steady_clock::now();
    const double elapsed = std::chrono::duration<double>(end - start).count();

    std::printf("job-benchmark: %d jobs em %.3f s (%.0f jobs/s)\n",
                kJobCount, elapsed, kJobCount / elapsed);
    std::printf("contador final = %lld\n", counter.load());

    if (counter.load() != kJobCount) {
        std::fprintf(stderr, "FALHA: esperado %d, obtido %lld\n", kJobCount, counter.load());
        return 1;
    }

    std::printf("OK — 100.000 jobs concluidos com sucesso (com cadeias de dependencia).\n");
    return 0;
}
