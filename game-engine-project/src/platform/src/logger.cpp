#include "engine/platform/logger.hpp"

#include <chrono>
#include <cstdio>
#include <ctime>
#include <mutex>

namespace engine::platform {

namespace {
std::mutex g_log_mutex;

const char* level_name(LogLevel level) {
    switch (level) {
        case LogLevel::Debug: return "DEBUG";
        case LogLevel::Info:  return "INFO";
        case LogLevel::Warn:  return "WARN";
        case LogLevel::Error: return "ERROR";
    }
    return "?";
}
} // namespace

Logger& Logger::instance() {
    static Logger logger;
    return logger;
}

void Logger::set_min_level(LogLevel level) {
    min_level_ = level;
}

void Logger::log(LogLevel level, std::string_view tag, std::string_view message) {
    if (static_cast<int>(level) < static_cast<int>(min_level_)) return;

    std::lock_guard<std::mutex> lock(g_log_mutex);
    const auto now = std::chrono::system_clock::now();
    const auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
                        now.time_since_epoch()).count() % 1000;
    const std::time_t t = std::chrono::system_clock::to_time_t(now);
    std::tm tm{};
    localtime_r(&t, &tm);

    std::fprintf(stdout, "[%02d:%02d:%02d.%03lld][%s][%.*s] %.*s\n",
                 tm.tm_hour, tm.tm_min, tm.tm_sec, static_cast<long long>(ms),
                 level_name(level),
                 static_cast<int>(tag.size()), tag.data(),
                 static_cast<int>(message.size()), message.data());
}

} // namespace engine::platform
