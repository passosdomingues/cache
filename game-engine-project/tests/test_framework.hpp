#pragma once
#include <cstdio>
#include <functional>
#include <string>
#include <vector>

// Framework de testes minimalista — sem dependências externas, coerente
// com a filosofia de nenhuma biblioteca de terceiros no core (RFC 00).
// Suficiente para os critérios de aceite de Platform Tests (Sprint 1);
// pode ser substituído por algo mais robusto quando fizer sentido.
namespace engine::testing {

struct TestCase {
    std::string name;
    std::function<void()> fn;
};

inline std::vector<TestCase>& registry() {
    static std::vector<TestCase> cases;
    return cases;
}

struct Registrar {
    Registrar(std::string name, std::function<void()> fn) {
        registry().push_back({std::move(name), std::move(fn)});
    }
};

inline int g_failures = 0;
inline std::string g_current_test;

inline void check(bool condition, const char* expr, const char* file, int line) {
    if (!condition) {
        std::fprintf(stderr, "  [FALHOU] %s (%s:%d) em %s\n", expr, file, line, g_current_test.c_str());
        ++g_failures;
    }
}

inline int run_all() {
    int total = 0;
    for (auto& tc : registry()) {
        g_current_test = tc.name;
        int failures_before = g_failures;
        std::printf("[TESTE] %s\n", tc.name.c_str());
        tc.fn();
        ++total;
        if (g_failures == failures_before) {
            std::printf("  OK\n");
        }
    }
    std::printf("\n%d testes executados, %d falhas.\n", total, g_failures);
    return g_failures == 0 ? 0 : 1;
}

} // namespace engine::testing

#define TEST_CASE(name) \
    void name(); \
    static ::engine::testing::Registrar registrar_##name(#name, name); \
    void name()

#define CHECK(expr) ::engine::testing::check((expr), #expr, __FILE__, __LINE__)
