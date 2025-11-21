#include "../include/policies/SchedulingPolicy.hpp"
#include "../include/policies/LongestQueuePolicy.hpp"
#include "../include/policies/ShortestQueuePolicy.hpp"
#include "../include/policies/RoundRobinPolicy.hpp"
#include "../include/policies/StrictPriorityPolicy.hpp"
#include "../include/policies/MaxAverageWaitPolicy.hpp"
#include "../include/policies/OldestPacketPolicy.hpp"
#include "../include/policies/SallesUtilityPolicy.hpp"
#include "../include/policies/CMuRulePolicy.hpp"
#include "../include/policies/WeightedRoundRobinPolicy.hpp"
#include "../include/policies/WhittleIndexPolicy.hpp"
#include "../include/policies/MarkovSwitchingPolicy.hpp"
#include "../include/policies/PolicyOrchestrator.hpp"
#include "../include/components.hpp"
#include <cassert>
#include <iostream>
#include <vector>
#include <cmath>
#include <memory>

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
    
    SystemState state;
    state.queues = queues;
    state.currentTime = 0.0;
    state.globalArrivalRateEstimate = 1.0;
    
    // All queues empty - should return -1
    LongestQueuePolicy policy;
    int result = policy.selectQueue(state);
    assert(result == -1);
    
    // q1 has 1 packet
    Packet p1(1, 1.0, 1.0);
    q1->tryEnqueue(p1);
    
    // q2 has 2 packets
    Packet p2(2, 1.0, 1.0);
    Packet p3(3, 1.0, 1.0);
    q2->tryEnqueue(p2);
    q2->tryEnqueue(p3);
    
    // q3 has 0 packets
    
    result = policy.selectQueue(state);
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
    
    SystemState state;
    state.queues = queues;
    state.currentTime = 0.0;
    state.globalArrivalRateEstimate = 1.0;
    
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
    Packet p(1, 0.0, 1.0);
    q1->tryEnqueue(p);
    q2->tryEnqueue(p);
    
    MaxAverageWaitPolicy policy;
    int result = policy.selectQueue(state);
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
    
    SystemState state;
    state.queues = queues;
    state.currentTime = 100.0;
    state.globalArrivalRateEstimate = 1.0;
    
    // q1: packet arrived at 90.0 (wait 10)
    Packet p1(1, 90.0, 1.0);
    q1->tryEnqueue(p1);
    
    // q2: packet arrived at 80.0 (wait 20)
    Packet p2(2, 80.0, 1.0);
    q2->tryEnqueue(p2);
    
    OldestPacketPolicy policy;
    int result = policy.selectQueue(state);
    assert(result == 1); // q2 has oldest packet (longest wait)
    
    // Cleanup
    for (auto q : queues) delete q;
    std::cout << " PASSED\n";
}

void testSallesUtilityPolicy() {
    std::cout << "Testing Salles Utility policy...";
    std::vector<Queue*> queues;
    
    // Type 0: Best Effort (Linear), Type 1: Voice (Exp), Type 2: Video (Quad)
    Queue* q1 = new Queue(0, 100, 1.0, Queue::DiscardPolicy::DROP_TAIL, 1000, 1.0, 0);
    Queue* q2 = new Queue(1, 100, 1.0, Queue::DiscardPolicy::DROP_TAIL, 1000, 1.0, 1);
    Queue* q3 = new Queue(2, 100, 1.0, Queue::DiscardPolicy::DROP_TAIL, 1000, 1.0, 2);
    
    queues.push_back(q1);
    queues.push_back(q2);
    queues.push_back(q3);
    
    SystemState state;
    state.queues = queues;
    state.currentTime = 10.0;
    
    // q1 (Best Effort): wait 5.0 -> Loss = 1.0
    Packet p1(1, 5.0, 1.0);
    q1->tryEnqueue(p1);
    
    // q2 (Voice): wait 5.0 -> Loss = exp(0.1 * 5.0) = 1.648
    Packet p2(2, 5.0, 1.0);
    q2->tryEnqueue(p2);
    
    // q3 (Video): wait 2.0 -> Loss = 2.0^2 = 4.0
    Packet p3(3, 8.0, 1.0);
    q3->tryEnqueue(p3);
    
    // Should select q3 (highest loss 4.0)
    auto policy = PolicyOrchestrator::createPolicy("SALLES_UTILITY");
    int result = policy->selectQueue(state);
    assert(result == 2);
    
    for (auto q : queues) delete q;
    std::cout << " PASSED\n";
}

void testCMuRulePolicy() {
    std::cout << "Testing cMu Rule policy...";
    std::vector<Queue*> queues;
    
    // q1: weight 1.0, mu 1.0 -> index 1.0
    Queue* q1 = new Queue(0, 100, 1.0, Queue::DiscardPolicy::DROP_TAIL, 1000, 1.0, 0);
    // q2: weight 2.0, mu 2.0 -> index 4.0
    Queue* q2 = new Queue(1, 100, 2.0, Queue::DiscardPolicy::DROP_TAIL, 1000, 2.0, 0);
    
    queues.push_back(q1);
    queues.push_back(q2);
    
    SystemState state;
    state.queues = queues;
    
    Packet p(1, 0.0, 1.0);
    q1->tryEnqueue(p);
    q2->tryEnqueue(p);
    
    auto policy = PolicyOrchestrator::createPolicy("C_MU_RULE");
    int result = policy->selectQueue(state);
    assert(result == 1); // q2 has higher index
    
    for (auto q : queues) delete q;
    std::cout << " PASSED\n";
}

void testWeightedRoundRobinPolicy() {
    std::cout << "Testing Weighted Round Robin policy...";
    std::vector<Queue*> queues;
    
    // q1: weight 2.0 -> quantum 2
    Queue* q1 = new Queue(0, 100, 1.0, Queue::DiscardPolicy::DROP_TAIL, 1000, 2.0, 0);
    // q2: weight 1.0 -> quantum 1
    Queue* q2 = new Queue(1, 100, 1.0, Queue::DiscardPolicy::DROP_TAIL, 1000, 1.0, 0);
    
    queues.push_back(q1);
    queues.push_back(q2);
    
    SystemState state;
    state.queues = queues;
    
    // Fill queues
    Packet p(1, 0.0, 1.0);
    for(int i=0; i<5; ++i) {
        q1->tryEnqueue(p);
        q2->tryEnqueue(p);
    }
    
    auto policy = PolicyOrchestrator::createPolicy("WEIGHTED_ROUND_ROBIN");
    
    // Sequence should be: q1, q1, q2, q1, q1, q2...
    assert(policy->selectQueue(state) == 0);
    assert(policy->selectQueue(state) == 0);
    assert(policy->selectQueue(state) == 1);
    assert(policy->selectQueue(state) == 0);
    
    for (auto q : queues) delete q;
    std::cout << " PASSED\n";
}

void testWhittleIndexPolicy() {
    std::cout << "Testing Whittle Index policy...";
    std::vector<Queue*> queues;
    
    // q1: L=10, mu=1.0 -> Index = 10*1 / 11 = 0.909
    Queue* q1 = new Queue(0, 100, 1.0, Queue::DiscardPolicy::DROP_TAIL);
    // q2: L=5, mu=3.0 -> Index = 5*3 / 6 = 2.5
    Queue* q2 = new Queue(1, 100, 3.0, Queue::DiscardPolicy::DROP_TAIL);
    
    queues.push_back(q1);
    queues.push_back(q2);
    
    SystemState state;
    state.queues = queues;
    
    Packet p(1, 0.0, 1.0);
    for (int i = 0; i < 5; ++i) q1->tryEnqueue(p);
    for (int i = 0; i < 10; ++i) q2->tryEnqueue(p);
    
    auto policy = PolicyOrchestrator::createPolicy("WHITTLE_INDEX");
    int result = policy->selectQueue(state);
    assert(result == 1); // q2 has higher index
    
    for (auto q : queues) delete q;
    std::cout << " PASSED\n";
}

void testMarkovSwitchingPolicy() {
    std::cout << "Testing Markov Switching policy...";
    std::vector<Queue*> queues;
    
    // 3 queues
    Queue* q1 = new Queue(0, 100, 1.0, Queue::DiscardPolicy::DROP_TAIL);
    Queue* q2 = new Queue(1, 100, 1.0, Queue::DiscardPolicy::DROP_TAIL);
    Queue* q3 = new Queue(2, 100, 1.0, Queue::DiscardPolicy::DROP_TAIL);
    
    queues.push_back(q1);
    queues.push_back(q2);
    queues.push_back(q3);
    
    SystemState state;
    state.queues = queues;
    
    // Test State 13: (1, 1, 1) -> Bin(1)=0, Bin(1)=0, Bin(1)=0 -> ID 0?
    // Wait, logic: ID = bin(q0) + 3*bin(q1) + 9*bin(q2)
    // Bin: <=5 -> 0, <=20 -> 1, >20 -> 2
    
    // Case 1: All empty -> ID 0. Matrix says Policy 0 (LongestQueue).
    // q1=0, q2=0, q3=0. Longest -> q0 (tie break).
    auto policy = PolicyOrchestrator::createPolicy("MARKOV_SWITCHING");
    // (Assuming policy_matrix.csv is loaded from current dir)
    
    // Case 2: q0=10 (Bin 1), q1=1 (Bin 0), q2=0 (Bin 0) -> ID = 1 + 0 + 0 = 1.
    // Matrix says Policy 1 (ShortestQueue).
    // q0=10, q1=1, q2=0. Shortest non-empty -> q1.
    
    Packet p(1, 0.0, 1.0);
    for(int i=0; i<10; ++i) q1->tryEnqueue(p);
    q2->tryEnqueue(p); // q1 has 1 packet
    
    int result = policy->selectQueue(state);
    assert(result == 1); // Shortest non-empty is q1
    
    // Case 3: q0=10 (Bin 1), q1=10 (Bin 1), q2=0 (Bin 0) -> ID = 1 + 3 + 0 = 4.
    // Matrix says Policy 4 (MaxAverageWait).
    for(int i=0; i<10; ++i) q2->tryEnqueue(p);
    // q0 wait time > q2 wait time? (q0 enqueued first)
    // q0 head wait time is large. q2 head wait time is large but smaller than q0?
    // Actually we didn't set arrival times. All 0.0.
    // So wait times are equal (currentTime - 0.0).
    // MaxAvgWait -> Tie break?
    
    // Let's try State 13: 1 + 3*1 + 9*1 = 13.
    // q0=10 (Bin 1), q1=10 (Bin 1), q2=10 (Bin 1).
    // Matrix says Policy 1 (ShortestQueue).
    for(int i=0; i<10; ++i) q3->tryEnqueue(p);
    // All length 10. Shortest -> q0 (tie break).
    
    result = policy->selectQueue(state);
    assert(result == 1); // Longest is q1 (length 11)
    
    for (auto q : queues) delete q;
    std::cout << " PASSED\n";
}

void testPolicyFactory() {
    std::cout << "Testing policy retrieval by name..." << std::endl;
    
    auto policy = PolicyOrchestrator::createPolicy("LONGEST_QUEUE");
    assert(policy->getName() == "LONGEST_QUEUE");
    
    auto p2 = PolicyOrchestrator::createPolicy("UNKNOWN_POLICY");
    assert(p2->getName() == "LONGEST_QUEUE"); // Default
    
    std::cout << " PASSED" << std::endl;
}

void testPolicyOrchestrator() {
    std::cout << "Testing Policy Orchestrator (Min-Heap)...";
    std::vector<Queue*> queues;
    Queue* q1 = new Queue(0, 100, 1.0, Queue::DiscardPolicy::DROP_TAIL);
    Queue* q2 = new Queue(1, 100, 1.0, Queue::DiscardPolicy::DROP_TAIL);
    queues.push_back(q1);
    queues.push_back(q2);
    
    SystemState state;
    state.queues = queues;
    
    // q1 has 10 packets, q2 has 5 packets
    Packet p(1, 0.0, 1.0);
    for(int i=0; i<10; ++i) q1->tryEnqueue(p);
    for(int i=0; i<5; ++i) q2->tryEnqueue(p);
    
    auto policy = PolicyOrchestrator::createPolicy("POLICY_ORCHESTRATOR");
    int result = policy->selectQueue(state);
    
    // Should pick q2 (length 5 < 10)
    assert(result == 1);
    
    for (auto q : queues) delete q;
    std::cout << " PASSED\n";
}

int main() {
    testLongestQueuePolicy();
    // testShortestQueuePolicy();
    // testRoundRobinPolicy();
    // testStrictPriorityPolicy();
    testMaxAverageWaitPolicy();
    testOldestPacketPolicy();
    // testAgingPolicy();
    testSallesUtilityPolicy();
    testCMuRulePolicy();
    testWeightedRoundRobinPolicy();
    testWhittleIndexPolicy();
    testMarkovSwitchingPolicy();
    testPolicyOrchestrator();
    testPolicyFactory();
    
    std::cout << "All Policies tests passed!\n";
    return 0;
}