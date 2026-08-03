#pragma once
#include <string>
#include <string_view>

namespace engine::platform {

enum class LogLevel { Debug = 0, Info = 1, Warn = 2, Error = 3 };

class Logger {
public:
    static Logger& instance();

    void set_min_level(LogLevel level);
    void log(LogLevel level, std::string_view tag, std::string_view message);

private:
    LogLevel min_level_ = LogLevel::Info;
};

} // namespace engine::platform

#define ENGINE_LOG_DEBUG(tag, msg) ::engine::platform::Logger::instance().log(::engine::platform::LogLevel::Debug, tag, msg)
#define ENGINE_LOG_INFO(tag, msg)  ::engine::platform::Logger::instance().log(::engine::platform::LogLevel::Info, tag, msg)
#define ENGINE_LOG_WARN(tag, msg)  ::engine::platform::Logger::instance().log(::engine::platform::LogLevel::Warn, tag, msg)
#define ENGINE_LOG_ERROR(tag, msg) ::engine::platform::Logger::instance().log(::engine::platform::LogLevel::Error, tag, msg)
