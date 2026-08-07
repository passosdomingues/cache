#pragma once
#include <cstdio>
#include <cstdlib>

namespace engine::platform {

[[noreturn]] inline void assert_fail(const char* expr, const char* file, int line, const char* msg) {
    std::fprintf(stderr, "[ASSERT FAILED] %s\n  em %s:%d\n  %s\n", expr, file, line, msg ? msg : "");
    std::abort();
}

} // namespace engine::platform

// ENGINE_ASSERT é removido em builds de release (NDEBUG definido).
// Use para invariantes internas caras de checar sempre.
#if defined(NDEBUG)
#define ENGINE_ASSERT(expr, msg) ((void)0)
#else
#define ENGINE_ASSERT(expr, msg) \
    do { if (!(expr)) { ::engine::platform::assert_fail(#expr, __FILE__, __LINE__, msg); } } while (0)
#endif

// ENGINE_VERIFY é checado sempre, mesmo em release — para condições que
// nunca podem ser silenciosamente ignoradas (ex.: resultado de I/O).
#define ENGINE_VERIFY(expr, msg) \
    do { if (!(expr)) { ::engine::platform::assert_fail(#expr, __FILE__, __LINE__, msg); } } while (0)
