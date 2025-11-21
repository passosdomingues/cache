/**
 * @file test_queue.cpp
 * @brief Unit tests for queue state management
 */

#include "../include/queue.hpp"
#include <cassert>
#include <iostream>

/**
 * @brief Test queue initialization
 */
void testQueueInitialization() {
    std::cout << "Testing queue initialization...";
    QueueState queue(50, DiscardPolicy::DROP_TAIL, 100);
    
    assert(queue.getCurrentQueueLength() == 0);
    assert(queue.getMaxObservedQueueLength() == 0);
    assert(queue.getTotalServedRequests() == 0);
    assert(queue.getTotalServiceTime() == 0.0);
    std::cout << " PASSED\n";
}

/**
 * @brief Test enqueue/dequeue operations
 */
void testEnqueueDequeue() {
    std::cout << "Testing enqueue/dequeue operations...";
    QueueState queue;
    
    // Test basic enqueue
    assert(queue.enqueuePacket(1.0) == true);
    assert(queue.getCurrentQueueLength() == 1);
    assert(queue.getMaxObservedQueueLength() == 1);
    
    assert(queue.enqueuePacket(2.0) == true);
    assert(queue.getCurrentQueueLength() == 2);
    assert(queue.getMaxObservedQueueLength() == 2);
    
    // Test dequeue
    double arrival1 = queue.dequeuePacket();
    assert(arrival1 == 1.0);
    assert(queue.getCurrentQueueLength() == 1);
    assert(queue.getTotalServedRequests() == 1);
    
    double arrival2 = queue.dequeuePacket();
    assert(arrival2 == 2.0);
    assert(queue.getCurrentQueueLength() == 0);
    assert(queue.getTotalServedRequests() == 2);
    std::cout << " PASSED\n";
}

/**
 * @brief Test head waiting time calculation
 */
void testHeadWaitingTime() {
    std::cout << "Testing head waiting time calculation...";
    QueueState queue;
    
    // Empty queue should return 0
    assert(queue.peekHeadWaitingTime(5.0) == 0.0);
    
    queue.enqueuePacket(2.0);
    assert(queue.peekHeadWaitingTime(5.0) == 3.0);
    
    queue.enqueuePacket(3.0);
    assert(queue.peekHeadWaitingTime(6.0) == 4.0); // Still first packet
    std::cout << " PASSED\n";
}

/**
 * @brief Test drop-tail policy
 */
void testDropTailPolicy() {
    std::cout << "Testing drop-tail policy...";
    QueueState queue(10, DiscardPolicy::DROP_TAIL, 2); // Small capacity for testing
    
    assert(queue.enqueuePacket(1.0) == true);
    assert(queue.enqueuePacket(2.0) == true);
    assert(queue.enqueuePacket(3.0) == false); // Should be rejected
    assert(queue.getCurrentQueueLength() == 2);
    std::cout << " PASSED\n";
}

/**
 * @brief Test drop-oldest policy
 */
void testDropOldestPolicy() {
    std::cout << "Testing drop-oldest policy...";
    QueueState queue(10, DiscardPolicy::DROP_OLDEST, 2);
    
    assert(queue.enqueuePacket(1.0) == true);
    assert(queue.enqueuePacket(2.0) == true);
    assert(queue.enqueuePacket(3.0) == true); // Should remove oldest (1.0)
    
    assert(queue.getCurrentQueueLength() == 2);
    double head = queue.dequeuePacket();
    assert(head == 2.0); // 1.0 was removed, 2.0 is now head
    std::cout << " PASSED\n";
}

/**
 * @brief Test queue reset
 */
void testQueueReset() {
    std::cout << "Testing queue reset...";
    QueueState queue;
    
    queue.enqueuePacket(1.0);
    queue.enqueuePacket(2.0);
    queue.dequeuePacket();
    
    queue.reset();
    
    assert(queue.getCurrentQueueLength() == 0);
    assert(queue.getMaxObservedQueueLength() == 0);
    assert(queue.getTotalServedRequests() == 0);
    assert(queue.getTotalServiceTime() == 0.0);
    std::cout << " PASSED\n";
}

/**
 * @brief Main function for queue tests
 * @return int Exit status
 */
int main() {
    std::cout << "Running Queue tests...\n";
    
    testQueueInitialization();
    testEnqueueDequeue();
    testHeadWaitingTime();
    testDropTailPolicy();
    testDropOldestPolicy();
    testQueueReset();
    
    std::cout << "All Queue tests passed!\n";
    return 0;
}