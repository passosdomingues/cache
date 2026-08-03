#pragma once
#include <chrono>

namespace engine::platform {

// Cronômetro simples de propósito geral (benchmarks, profiling ad-hoc).
class Timer {
public:
    Timer() : start_(Clock::now()) {}

    void reset() { start_ = Clock::now(); }

    double elapsed_seconds() const {
        return std::chrono::duration<double>(Clock::now() - start_).count();
    }

    long long elapsed_microseconds() const {
        return std::chrono::duration_cast<std::chrono::microseconds>(Clock::now() - start_).count();
    }

private:
    using Clock = std::chrono::steady_clock;
    Clock::time_point start_;
};

// Utilitário para delta time entre frames do loop principal (RFC 01).
class DeltaClock {
public:
    DeltaClock() : last_(Clock::now()) {}

    double tick() {
        const auto now = Clock::now();
        const double dt = std::chrono::duration<double>(now - last_).count();
        last_ = now;
        return dt;
    }

private:
    using Clock = std::chrono::steady_clock;
    Clock::time_point last_;
};

} // namespace engine::platform
