#pragma once

#include "engine/platform/sync.hpp"
#include "engine/platform/thread.hpp"

#include <chrono>
#include <condition_variable>
#include <cstdint>
#include <deque>
#include <functional>
#include <future>
#include <memory>
#include <mutex>
#include <type_traits>
#include <unordered_map>
#include <vector>

namespace engine::jobs {

// Prioridade de escalonamento. Filas separadas por prioridade — um job
// Critical nunca espera atrás de um Background.
enum class Priority { Critical = 0, Normal = 1, Background = 2 };

using JobId = std::uint64_t;

// Handle opaco para um job submetido. Usado para expressar dependências
// (RFC 01 — Modelo de Execução) e para esperar/cancelar um job específico.
class JobHandle {
public:
    JobHandle() = default;
    explicit JobHandle(JobId id) : id_(id) {}

    JobId id() const { return id_; }
    bool valid() const { return id_ != 0; }

private:
    JobId id_ = 0;
};

// Cancelamento cooperativo: o corpo do job deve checar is_cancelled()
// periodicamente. Não há preempção — um job que nunca checa o token
// nunca é interrompido de fato.
class CancellationToken {
public:
    void cancel() { cancelled_.store(true, std::memory_order_relaxed); }
    bool is_cancelled() const { return cancelled_.load(std::memory_order_relaxed); }

private:
    std::atomic<bool> cancelled_{false};
};

// Estatísticas simples de profiling por job: tempo em fila vs. tempo de
// execução. Leitura recomendada apenas após confirmar que o job terminou
// (JobSystem::is_finished) — os timestamps não têm sincronização própria
// além da relação de acontece-antes estabelecida pela flag de "finished".
struct JobStats {
    std::chrono::steady_clock::time_point submitted_at{};
    std::chrono::steady_clock::time_point started_at{};
    std::chrono::steady_clock::time_point finished_at{};

    double queue_time_seconds() const {
        return std::chrono::duration<double>(started_at - submitted_at).count();
    }
    double execution_time_seconds() const {
        return std::chrono::duration<double>(finished_at - started_at).count();
    }
};

// Handle para o resultado assíncrono de um job (ver JobSystem::submit_with_result).
template <typename T>
class Future {
public:
    Future() = default;
    Future(std::shared_future<T> future, JobHandle job)
        : future_(std::move(future)), job_(job) {}

    T get() const { return future_.get(); }
    bool valid() const { return future_.valid(); }
    JobHandle job() const { return job_; }

private:
    std::shared_future<T> future_;
    JobHandle job_;
};

// Job System: thread pool + fila de jobs + escalonador que resolve um
// grafo de dependências antes de despachar cada job. Construído sobre a
// Platform Layer (Sprint 1) — Thread, Mutex, Atomic — nunca sobre
// primitivas de SO diretamente (RFC 05).
class JobSystem {
public:
    using JobFn = std::function<void(CancellationToken&)>;

    // thread_count == 0 usa std::thread::hardware_concurrency().
    explicit JobSystem(unsigned thread_count = 0);
    ~JobSystem();

    JobSystem(const JobSystem&) = delete;
    JobSystem& operator=(const JobSystem&) = delete;

    // Submete um job. Se `dependencies` não estiver vazio, o job só entra
    // na fila quando todas as dependências tiverem terminado.
    JobHandle submit(JobFn fn, std::vector<JobHandle> dependencies = {},
                      Priority priority = Priority::Normal);

    // Como submit(), mas o job retorna um valor, acessível via Future<T>::get().
    template <typename Fn>
    auto submit_with_result(Fn&& fn, std::vector<JobHandle> dependencies = {},
                             Priority priority = Priority::Normal) {
        using Result = std::invoke_result_t<Fn, CancellationToken&>;
        auto promise = std::make_shared<std::promise<Result>>();
        std::shared_future<Result> shared_future = promise->get_future().share();

        JobHandle handle = submit(
            [fn = std::forward<Fn>(fn), promise](CancellationToken& token) mutable {
                if constexpr (std::is_void_v<Result>) {
                    fn(token);
                    promise->set_value();
                } else {
                    promise->set_value(fn(token));
                }
            },
            std::move(dependencies), priority);

        return Future<Result>(std::move(shared_future), handle);
    }

    void wait(const JobHandle& handle) const;
    void wait_all();
    void cancel(const JobHandle& handle);

    bool is_finished(const JobHandle& handle) const;
    JobStats stats_for(const JobHandle& handle) const;

    std::size_t pending_count() const;
    std::int64_t completed_count() const;

private:
    struct JobRecord {
        JobId id = 0;
        JobFn fn;
        Priority priority = Priority::Normal;
        platform::AtomicCounter remaining_dependencies{0};
        std::vector<JobId> dependents;
        CancellationToken cancellation;
        std::atomic<bool> finished{false};
        JobStats stats;
        mutable std::mutex finish_mutex;
        mutable std::condition_variable finish_cv;
    };

    void worker_loop();
    void enqueue_ready(const std::shared_ptr<JobRecord>& record);
    void on_job_finished(const std::shared_ptr<JobRecord>& record);
    std::shared_ptr<JobRecord> find(JobId id) const;

    std::vector<platform::Thread> workers_;
    std::atomic<bool> stop_{false};
    std::atomic<JobId> next_id_{1};
    platform::AtomicCounter completed_{0};

    mutable platform::Mutex jobs_mutex_;
    std::unordered_map<JobId, std::shared_ptr<JobRecord>> jobs_;

    platform::Mutex queue_mutex_;
    std::condition_variable queue_cv_;
    std::deque<JobId> queue_critical_;
    std::deque<JobId> queue_normal_;
    std::deque<JobId> queue_background_;
};

} // namespace engine::jobs
