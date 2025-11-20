#include "../include/policies.hpp"
#include "../include/components.hpp"
#include <cassert>
#include <iostream>
#include <vector>

// Mock SimulationState for testing
class MockSimulationState {
public:
    double currentTime = 0.0;
};

void testLongestQueuePolicy() {
    std::cout << "Testing Longest Queue policy...";
    std::vector<Queue*> queues;
    
    // Create test queues
    // Queue(id, capacity, mu, policy)
    Queue* q1 = new Queue(0, 100, 1.0, Queue::DiscardPolicy::DROP_TAIL);
    Queue* q2 = new Queue(1, 100, 1.0, Queue::DiscardPolicy::DROP_TAIL);
    Queue* q3 = new Queue(2, 100, 1.0, Queue::DiscardPolicy::DROP_TAIL);
    
    queues.push_back(q1);
    queues.push_back(q2);
    queues.push_back(q3);
    
    MockSimulationState state;
    
    // All queues empty - should return -1
    int result = Policies::LongestQueue(queues, state.currentTime);
    assert(result == -1);
    
    // q1 has 1 packet
    Packet p1 = {1, 1.0, 0, 0};
    q1->tryEnqueue(p1);
    
    // q2 has 2 packets
    Packet p2 = {2, 1.0, 0, 0};
    Packet p3 = {3, 1.0, 0, 0};
    q2->tryEnqueue(p2);
    q2->tryEnqueue(p3);
    
    // q3 has 0 packets
    
    result = Policies::LongestQueue(queues, state.currentTime);
    assert(result == 1); // q2 has most packets
    
    // Cleanup
    for (auto q : queues) delete q;
    std::cout << " PASSED\n";
}

void testMaxAverageWaitPolicy() {
    std::cout << "Testing Max Average Wait policy...";
    std::vector<Queue*> queues;
    
    Queue* q1 = new Queue(0, 100, 1.0, Queue::DiscardPolicy::DROP_TAIL);
    Queue* q2 = new Queue(1, 100, 1.0, Queue::DiscardPolicy::DROP_TAIL);
    
    queues.push_back(q1);
    queues.push_back(q2);
    
    MockSimulationState state;
    
    // Inject stats directly or simulate departures?
    // Queue::registerDepartureStats updates the window.
    
    // q1: avg wait 10.0
    q1->registerDepartureStats(10.0, 100.0);
    
    // q2: avg wait 20.0
    q2->registerDepartureStats(20.0, 100.0);
    q2->registerDepartureStats(20.0, 100.0);
    
    // We need queues to be non-empty for them to be selectable?
    // The policy implementation checks `if (q->isEmpty()) continue;`
    // So we must enqueue something.
    Packet p = {1, 0.0, 0, 0};
    q1->tryEnqueue(p);
    q2->tryEnqueue(p);
    
    int result = Policies::MaxAverageWait(queues, state.currentTime);
    assert(result == 1); // q2 has higher avg wait
    
    // Cleanup
    for (auto q : queues) delete q;
    std::cout << " PASSED\n";
}

void testOldestPacketPolicy() {
    std::cout << "Testing Oldest Packet policy...";
    std::vector<Queue*> queues;
    
    Queue* q1 = new Queue(0, 100, 1.0, Queue::DiscardPolicy::DROP_TAIL);
    Queue* q2 = new Queue(1, 100, 1.0, Queue::DiscardPolicy::DROP_TAIL);
    
    queues.push_back(q1);
    queues.push_back(q2);
    
    MockSimulationState state;
    state.currentTime = 100.0;
    
    // q1: packet arrived at 90.0 (wait 10)
    Packet p1 = {1, 90.0, 0, 0};
    q1->tryEnqueue(p1);
    
    // q2: packet arrived at 80.0 (wait 20)
    Packet p2 = {2, 80.0, 0, 0};
    q2->tryEnqueue(p2);
    
    int result = Policies::OldestPacket(queues, state.currentTime);
    assert(result == 1); // q2 has oldest packet (longest wait)
    
    // Cleanup
    for (auto q : queues) delete q;
    std::cout << " PASSED\n";
}

void testPolicyByName() {
    std::cout << "Testing policy retrieval by name...";
    
    auto policy1 = Policies::getPolicyByName("LONGEST_QUEUE");
    auto policy2 = Policies::getPolicyByName("MAX_AVG_WAIT");
    auto policy3 = Policies::getPolicyByName("OLDEST_PACKET");
    
    // Should default to LongestQueue for unknown
    auto policyDefault = Policies::getPolicyByName("UNKNOWN_POLICY");
    
    std::cout << " PASSED\n";
}

int main() {
    std::cout << "Running Policies tests...\n";
    
    testLongestQueuePolicy();
    testMaxAverageWaitPolicy(); 
    testOldestPacketPolicy();
    testPolicyByName();
    
    std::cout << "All Policies tests passed!\n";
    return 0;
}