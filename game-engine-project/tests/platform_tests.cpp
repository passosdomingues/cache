#include "test_framework.hpp"

#include "engine/platform/assert.hpp"
#include "engine/platform/cli.hpp"
#include "engine/platform/configuration.hpp"
#include "engine/platform/filesystem.hpp"
#include "engine/platform/logger.hpp"
#include "engine/platform/memory.hpp"
#include "engine/platform/socket.hpp"
#include "engine/platform/sync.hpp"
#include "engine/platform/thread.hpp"
#include "engine/platform/timer.hpp"

#include <atomic>
#include <chrono>
#include <cstdint>
#include <string>
#include <thread>
#include <vector>

using namespace engine::platform;

TEST_CASE(filesystem_write_read_roundtrip) {
    const auto tmp = std::filesystem::temp_directory_path() / "engine_platform_test.txt";
    CHECK(fs::write_text_file(tmp, "ola engine"));
    CHECK(fs::exists(tmp));
    auto content = fs::read_text_file(tmp);
    CHECK(content.has_value());
    if (content) {
        CHECK(*content == "ola engine");
    }
    fs::remove(tmp);
    CHECK(!fs::exists(tmp));
}

TEST_CASE(timer_measures_elapsed_time) {
    Timer timer;
    std::this_thread::sleep_for(std::chrono::milliseconds(5));
    CHECK(timer.elapsed_seconds() >= 0.0);
    CHECK(timer.elapsed_microseconds() >= 1000);
}

TEST_CASE(logger_does_not_crash) {
    ENGINE_LOG_INFO("test", "mensagem de teste do logger");
    ENGINE_LOG_WARN("test", "outra mensagem");
    CHECK(true);
}

TEST_CASE(configuration_parses_key_value_pairs) {
    Configuration config;
    config.load_from_string(
        "# comentario\n"
        "nome=engine\n"
        "threads=8\n"
        "debug=true\n"
    );
    CHECK(config.size() == 3);
    CHECK(config.get_string("nome", "") == "engine");
    CHECK(config.get_int("threads", 0) == 8);
    CHECK(config.get_bool("debug", false) == true);
    CHECK(config.get_string("inexistente", "fallback") == "fallback");
}

TEST_CASE(sync_atomic_counter_and_mutex) {
    AtomicCounter counter;
    Mutex mutex;
    std::vector<Thread> threads;
    for (int i = 0; i < 4; ++i) {
        threads.emplace_back("worker", [&counter, &mutex] {
            for (int j = 0; j < 1000; ++j) {
                ScopedLock lock(mutex);
                counter.increment();
            }
        });
    }
    for (auto& t : threads) t.join();
    CHECK(counter.load() == 4000);
}

TEST_CASE(sync_binary_semaphore_signals) {
    BinarySemaphore sem{0};
    std::atomic<bool> ran{false};
    Thread worker("signaler", [&sem, &ran] {
        ran = true;
        sem.release();
    });
    sem.acquire();
    CHECK(ran.load());
}

TEST_CASE(memory_arena_allocator) {
    ArenaAllocator arena(1024);
    void* a = arena.allocate(64);
    void* b = arena.allocate(64);
    CHECK(a != nullptr);
    CHECK(b != nullptr);
    CHECK(a != b);
    CHECK(arena.used() >= 128);
    arena.reset();
    CHECK(arena.used() == 0);
}

TEST_CASE(memory_pool_allocator) {
    PoolAllocator pool(sizeof(std::int64_t), 4);
    CHECK(pool.free_count() == 4);
    void* p1 = pool.allocate();
    void* p2 = pool.allocate();
    CHECK(p1 != nullptr);
    CHECK(p2 != nullptr);
    CHECK(pool.free_count() == 2);
    pool.deallocate(p1);
    CHECK(pool.free_count() == 3);
}

TEST_CASE(cli_parses_flags_options_and_positional_args) {
    const char* argv[] = {"prog", "--verbose", "--name=engine", "input.txt"};
    CommandLineParser parser;
    parser.parse(4, const_cast<char**>(argv));
    CHECK(parser.has_flag("verbose"));
    CHECK(parser.get_option("name", "") == "engine");
    CHECK(parser.positional_args().size() == 1);
    CHECK(parser.positional_args()[0] == "input.txt");
}

TEST_CASE(socket_loopback_echo) {
    constexpr std::uint16_t port = 55123;
    TcpSocket server;
    CHECK(server.listen(port));

    std::atomic<bool> server_ok{false};
    Thread server_thread("echo-server", [&server, &server_ok] {
        TcpSocket client;
        if (server.accept(client)) {
            char buffer[64] = {};
            int n = client.receive(buffer, sizeof(buffer) - 1);
            if (n > 0) {
                client.send(buffer, static_cast<std::size_t>(n));
                server_ok = true;
            }
        }
    });

    std::this_thread::sleep_for(std::chrono::milliseconds(20));

    TcpSocket client;
    CHECK(client.connect("127.0.0.1", port));
    const std::string message = "ping";
    CHECK(client.send(message.data(), message.size()) == static_cast<int>(message.size()));

    char reply[64] = {};
    int n = client.receive(reply, sizeof(reply) - 1);
    CHECK(n == static_cast<int>(message.size()));
    if (n > 0) {
        CHECK(std::string(reply, static_cast<std::size_t>(n)) == message);
    }

    server_thread.join();
    CHECK(server_ok.load());
}

int main() {
    return engine::testing::run_all();
}
