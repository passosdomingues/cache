/**
 * @file test_events.cpp
 * @brief Unit tests for event system functionality
 */

#include "../include/events.hpp"
#include <cassert>
#include <iostream>
#include <vector>

/**
 * @brief Test event creation and basic properties
 */
void testEventCreation() {
    std::cout << "Testing event creation...";
    Event arrival(1.0, EventType::ARRIVAL, 0);
    Event departure(2.0, EventType::DEPARTURE, 1);
    Event sample(3.0, EventType::SAMPLE);
    
    assert(arrival.timestamp == 1.0);
    assert(arrival.type == EventType::ARRIVAL);
    assert(arrival.queueId == 0);
    
    assert(departure.timestamp == 2.0);
    assert(departure.type == EventType::DEPARTURE);
    assert(departure.queueId == 1);
    
    assert(sample.timestamp == 3.0);
    assert(sample.type == EventType::SAMPLE);
    assert(sample.queueId == -1);
    std::cout << " PASSED\n";
}

/**
 * @brief Test event comparison operations
 */
void testEventComparison() {
    std::cout << "Testing event comparison...";
    Event early(1.0, EventType::ARRIVAL);
    Event late(2.0, EventType::DEPARTURE);
    
    assert((early > late) == false); // early is not greater than late
    assert((late > early) == true);  // late is greater than early
    std::cout << " PASSED\n";
}

/**
 * @brief Test empty queue behavior and error handling
 */
void testEmptyQueue() {
    std::cout << "Testing empty queue behavior...";
    EventQueue queue;
    
    assert(queue.isEmpty() == true);
    assert(queue.size() == 0);
    
    try {
        queue.peekEvent();
        assert(false); // Should not reach here
    } catch (const std::runtime_error&) {
        // Expected behavior
    }
    
    try {
        queue.popEvent();
        assert(false); // Should not reach here
    } catch (const std::runtime_error&) {
        // Expected behavior
    }
    std::cout << " PASSED\n";
}

/**
 * @brief Test single event operations
 */
void testSingleEvent() {
    std::cout << "Testing single event...";
    EventQueue queue;
    Event event(1.0, EventType::ARRIVAL, 0);
    
    queue.pushEvent(event);
    
    assert(queue.isEmpty() == false);
    assert(queue.size() == 1);
    
    Event peeked = queue.peekEvent();
    assert(peeked.timestamp == 1.0);
    assert(peeked.type == EventType::ARRIVAL);
    assert(peeked.queueId == 0);
    
    Event popped = queue.popEvent();
    assert(popped.timestamp == 1.0);
    assert(queue.isEmpty() == true);
    std::cout << " PASSED\n";
}

/**
 * @brief Test multiple events ordering in min-heap
 */
void testMultipleEventsOrder() {
    std::cout << "Testing multiple events ordering...";
    EventQueue queue;
    
    // Push events in random order
    queue.pushEvent(Event(3.0, EventType::SAMPLE));
    queue.pushEvent(Event(1.0, EventType::ARRIVAL, 0));
    queue.pushEvent(Event(2.0, EventType::DEPARTURE, 1));
    queue.pushEvent(Event(0.5, EventType::ARRIVAL, 2));
    
    // Should pop in increasing timestamp order
    Event e1 = queue.popEvent();
    assert(e1.timestamp == 0.5);
    
    Event e2 = queue.popEvent();
    assert(e2.timestamp == 1.0);
    
    Event e3 = queue.popEvent();
    assert(e3.timestamp == 2.0);
    
    Event e4 = queue.popEvent();
    assert(e4.timestamp == 3.0);
    
    assert(queue.isEmpty() == true);
    std::cout << " PASSED\n";
}

/**
 * @brief Test queue clear operation
 */
void testQueueClear() {
    std::cout << "Testing queue clear...";
    EventQueue queue;
    
    queue.pushEvent(Event(1.0, EventType::ARRIVAL));
    queue.pushEvent(Event(2.0, EventType::DEPARTURE));
    
    assert(queue.size() == 2);
    
    queue.clear();
    
    assert(queue.size() == 0);
    assert(queue.isEmpty() == true);
    std::cout << " PASSED\n";
}

/**
 * @brief Main function for events tests
 * @return int Exit status
 */
int main() {
    std::cout << "Running Events tests...\n";
    
    testEventCreation();
    testEventComparison();
    testEmptyQueue();
    testSingleEvent();
    testMultipleEventsOrder();
    testQueueClear();
    
    std::cout << "All Events tests passed!\n";
    return 0;
}