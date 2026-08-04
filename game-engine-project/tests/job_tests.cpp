#include "test_framework.hpp"

#include "engine/jobs/job_system.hpp"
#include "engine/platform/sync.hpp"

#include <atomic>
#include <chrono>
#include <mutex>
#include <thread>
#include <vector>

using namespace engine::jobs;

TEST_CASE(jobs_basic_execution) {
    JobSystem js(2);
    std::atomic<int> counter{0};
    auto handle = js.submit([&counter](CancellationToken&) { counter.fetch_add(1); });
    js.wait(handle);
    CHECK(counter.load() == 1);
    CHECK(js.is_finished(handle));
}

TEST_CASE(jobs_respects_dependencies) {
    JobSystem js(4);
    std::mutex order_mutex;
    std::vector<int> order;

    auto first = js.submit([&](CancellationToken&) {
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
        std::lock_guard<std::mutex> lock(order_mutex);
        order.push_back(1);
    });
    auto second = js.submit([&](CancellationToken&) {
        std::lock_guard<std::mutex> lock(order_mutex);
        order.push_back(2);
    }, {first});

    js.wait(second);
    CHECK(order.size() == 2);
    if (order.size() == 2) {
        CHECK(order[0] == 1);
        CHECK(order[1] == 2);
    }
}

TEST_CASE(jobs_future_returns_value) {
    JobSystem js(2);
    auto future = js.submit_with_result([](CancellationToken&) { return 21 * 2; });
    CHECK(future.get() == 42);
}

TEST_CASE(jobs_cancellation_is_observed) {
    JobSystem js(1);
    std::atomic<bool> ran_to_completion{false};

    auto handle = js.submit([&](CancellationToken& token) {
        for (int i = 0; i < 100 && !token.is_cancelled(); ++i) {
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
        }
        if (!token.is_cancelled()) {
            ran_to_completion = true;
        }
    });
    js.cancel(handle);
    js.wait(handle);

    CHECK(!ran_to_completion.load());
}

TEST_CASE(jobs_wait_all_completes_everything) {
    JobSystem js(4);
    engine::platform::AtomicCounter counter;
    for (int i = 0; i < 500; ++i) {
        js.submit([&counter](CancellationToken&) { counter.increment(); });
    }
    js.wait_all();
    CHECK(counter.load() == 500);
}

TEST_CASE(jobs_priority_queues_do_not_starve) {
    JobSystem js(1);
    std::atomic<int> background_count{0};
    std::atomic<int> critical_count{0};

    // Satura a fila de background antes de submeter um job crítico.
    std::vector<JobHandle> handles;
    for (int i = 0; i < 20; ++i) {
        handles.push_back(js.submit(
            [&background_count](CancellationToken&) {
                std::this_thread::sleep_for(std::chrono::milliseconds(1));
                background_count.fetch_add(1);
            },
            {}, Priority::Background));
    }
    handles.push_back(js.submit(
        [&critical_count](CancellationToken&) { critical_count.fetch_add(1); },
        {}, Priority::Critical));

    for (auto& h : handles) js.wait(h);

    CHECK(critical_count.load() == 1);
    CHECK(background_count.load() == 20);
}

int main() {
    return engine::testing::run_all();
}
