#include "engine/jobs/job_system.hpp"

#include <thread>

namespace engine::jobs {

JobSystem::JobSystem(unsigned thread_count) {
    unsigned n = thread_count == 0 ? std::thread::hardware_concurrency() : thread_count;
    if (n == 0) n = 1;

    workers_.reserve(n);
    for (unsigned i = 0; i < n; ++i) {
        workers_.emplace_back("job-worker-" + std::to_string(i), [this] { worker_loop(); });
    }
}

JobSystem::~JobSystem() {
    stop_.store(true, std::memory_order_relaxed);
    queue_cv_.notify_all();
    // Threads (Platform Layer) já dão join() no próprio destrutor caso
    // necessário, mas fazemos explicitamente aqui para deixar claro o
    // ponto de sincronização.
    for (auto& worker : workers_) {
        worker.join();
    }
}

JobHandle JobSystem::submit(JobFn fn, std::vector<JobHandle> dependencies, Priority priority) {
    auto record = std::make_shared<JobRecord>();
    record->id = next_id_.fetch_add(1, std::memory_order_relaxed);
    record->fn = std::move(fn);
    record->priority = priority;
    record->stats.submitted_at = std::chrono::steady_clock::now();

    std::int64_t pending_deps = 0;
    {
        platform::ScopedLock lock(jobs_mutex_);
        // Para cada dependência ainda não concluída, registra este job
        // como "dependente" dela — quem termina por último decide quem
        // dispara o enqueue (ver on_job_finished).
        for (const auto& dep_handle : dependencies) {
            auto it = jobs_.find(dep_handle.id());
            if (it == jobs_.end()) continue; // dependência desconhecida: ignora
            auto& dep_record = it->second;
            if (dep_record->finished.load(std::memory_order_acquire)) continue;
            dep_record->dependents.push_back(record->id);
            ++pending_deps;
        }
        record->remaining_dependencies.store(pending_deps);
        jobs_.emplace(record->id, record);
    }

    JobHandle handle(record->id);

    if (pending_deps == 0) {
        enqueue_ready(record);
    }
    return handle;
}

void JobSystem::enqueue_ready(const std::shared_ptr<JobRecord>& record) {
    {
        platform::ScopedLock lock(queue_mutex_);
        switch (record->priority) {
            case Priority::Critical:   queue_critical_.push_back(record->id);   break;
            case Priority::Normal:     queue_normal_.push_back(record->id);     break;
            case Priority::Background: queue_background_.push_back(record->id); break;
        }
    }
    queue_cv_.notify_one();
}

void JobSystem::worker_loop() {
    while (true) {
        JobId id = 0;
        {
            std::unique_lock<platform::Mutex> lock(queue_mutex_);
            queue_cv_.wait(lock, [this] {
                return stop_.load(std::memory_order_relaxed) ||
                       !queue_critical_.empty() || !queue_normal_.empty() || !queue_background_.empty();
            });

            const bool queues_empty =
                queue_critical_.empty() && queue_normal_.empty() && queue_background_.empty();
            if (stop_.load(std::memory_order_relaxed) && queues_empty) {
                return;
            }
            if (queues_empty) continue; // acordado só pelo stop_, mas outra thread já esvaziou

            if (!queue_critical_.empty()) {
                id = queue_critical_.front(); queue_critical_.pop_front();
            } else if (!queue_normal_.empty()) {
                id = queue_normal_.front(); queue_normal_.pop_front();
            } else {
                id = queue_background_.front(); queue_background_.pop_front();
            }
        }

        auto record = find(id);
        if (!record) continue;

        record->stats.started_at = std::chrono::steady_clock::now();
        if (!record->cancellation.is_cancelled()) {
            record->fn(record->cancellation);
        }
        record->stats.finished_at = std::chrono::steady_clock::now();

        on_job_finished(record);
    }
}

void JobSystem::on_job_finished(const std::shared_ptr<JobRecord>& record) {
    std::vector<JobId> dependents_copy;
    {
        platform::ScopedLock lock(jobs_mutex_);
        record->finished.store(true, std::memory_order_release);
        dependents_copy = std::move(record->dependents);
    }
    completed_.increment();

    {
        // Garante que qualquer thread já bloqueada em wait() veja a
        // atualização antes do notify.
        std::lock_guard<std::mutex> lock(record->finish_mutex);
    }
    record->finish_cv.notify_all();

    for (JobId dep_id : dependents_copy) {
        auto dependent = find(dep_id);
        if (!dependent) continue;
        if (dependent->remaining_dependencies.decrement() == 0) {
            enqueue_ready(dependent);
        }
    }
}

std::shared_ptr<JobSystem::JobRecord> JobSystem::find(JobId id) const {
    platform::ScopedLock lock(jobs_mutex_);
    auto it = jobs_.find(id);
    return it == jobs_.end() ? nullptr : it->second;
}

void JobSystem::wait(const JobHandle& handle) const {
    auto record = find(handle.id());
    if (!record) return;
    std::unique_lock<std::mutex> lock(record->finish_mutex);
    record->finish_cv.wait(lock, [&record] { return record->finished.load(std::memory_order_acquire); });
}

void JobSystem::wait_all() {
    // Espera por um snapshot dos jobs conhecidos no momento da chamada.
    // Pensado para o padrão "submeter tudo, depois esperar" (ex.: o
    // job-benchmark do Sprint 2) — jobs submetidos depois desta chamada
    // não são cobertos por esta espera específica.
    std::vector<std::shared_ptr<JobRecord>> snapshot;
    {
        platform::ScopedLock lock(jobs_mutex_);
        snapshot.reserve(jobs_.size());
        for (auto& [id, record] : jobs_) {
            snapshot.push_back(record);
        }
    }
    for (auto& record : snapshot) {
        std::unique_lock<std::mutex> lock(record->finish_mutex);
        record->finish_cv.wait(lock, [&record] { return record->finished.load(std::memory_order_acquire); });
    }
}

void JobSystem::cancel(const JobHandle& handle) {
    auto record = find(handle.id());
    if (record) record->cancellation.cancel();
}

bool JobSystem::is_finished(const JobHandle& handle) const {
    auto record = find(handle.id());
    return record ? record->finished.load(std::memory_order_acquire) : true;
}

JobStats JobSystem::stats_for(const JobHandle& handle) const {
    auto record = find(handle.id());
    return record ? record->stats : JobStats{};
}

std::size_t JobSystem::pending_count() const {
    platform::ScopedLock lock(jobs_mutex_);
    std::size_t count = 0;
    for (auto& [id, record] : jobs_) {
        if (!record->finished.load(std::memory_order_acquire)) ++count;
    }
    return count;
}

std::int64_t JobSystem::completed_count() const {
    return completed_.load();
}

} // namespace engine::jobs
