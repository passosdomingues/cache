#pragma once
#include <string>
#include <thread>
#include <utility>

namespace engine::platform {

// Wrapper fino sobre std::thread que carrega um nome (útil para
// profiling/log no Job System, Sprint 2) e garante join() no destrutor
// se o chamador não o fizer explicitamente.
class Thread {
public:
    Thread() = default;

    template <typename Fn, typename... Args>
    explicit Thread(std::string name, Fn&& fn, Args&&... args)
        : name_(std::move(name)),
          thread_(std::forward<Fn>(fn), std::forward<Args>(args)...) {}

    Thread(const Thread&) = delete;
    Thread& operator=(const Thread&) = delete;
    Thread(Thread&&) noexcept = default;
    Thread& operator=(Thread&&) noexcept = default;

    ~Thread() {
        if (thread_.joinable()) {
            thread_.join();
        }
    }

    void join() { if (thread_.joinable()) thread_.join(); }
    bool joinable() const { return thread_.joinable(); }
    const std::string& name() const { return name_; }

private:
    std::string name_;
    std::thread thread_;
};

} // namespace engine::platform
