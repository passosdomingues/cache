/**
 * @file test_policies.cpp
 * @brief Comprehensive test suite for all scheduling policies
 * @details Tests various scheduling policies including Longest Queue, 
 *          Max Average Wait, Oldest Packet, Salles Utility, cMu Rule,
 *          Weighted Round Robin, Whittle Index, Markov Switching, 
 *          and Policy Orchestrator
 */

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

/**
 * @brief Test the Longest Queue scheduling policy
 * @details Verifies that the policy correctly selects the queue with the most packets
 */
void testLongestQueuePolicy() {
    std::cout << "Testing Longest Queue policy...";
    std::vector<Queue*> queues;
    
    // Create test queues with proper namespace qualification
    Queue* queue1 = new Queue(0, 100, 1.0, DiscardPolicy::DROP_TAIL);
    Queue* queue2 = new Queue(1, 100, 1.0, DiscardPolicy::DROP_TAIL);
    Queue* queue3 = new Queue(2, 100, 1.0, DiscardPolicy::DROP_TAIL);
    
    queues.push_back(queue1);
    queues.push_back(queue2);
    queues.push_back(queue3);
    
    SystemState systemState;
    systemState.queues = queues;
    systemState.currentTime = 0.0;
    systemState.globalArrivalRateEstimate = 1.0;
    
    // All queues empty - should return -1
    LongestQueuePolicy policy;
    int result = policy.selectQueue(systemState);
    assert(result == -1);
    
    // queue1 has 1 packet
    Packet packet1(1, 1.0, 1.0);
    queue1->tryEnqueue(packet1);
    
    // queue2 has 2 packets
    Packet packet2(2, 1.0, 1.0);
    Packet packet3(3, 1.0, 1.0);
    queue2->tryEnqueue(packet2);
    queue2->tryEnqueue(packet3);
    
    // queue3 has 0 packets
    result = policy.selectQueue(systemState);
    assert(result == 1); // queue2 has most packets
    
    // Cleanup
    for (auto queue : queues) {
        delete queue;
    }
    std::cout << " PASSED\n";
}

/**
 * @brief Test the Max Average Wait scheduling policy
 * @details Verifies that the policy correctly selects the queue with the highest average wait time
 */
void testMaxAverageWaitPolicy() {
    std::cout << "Testing Max Average Wait policy...";
    std::vector<Queue*> queues;
    
    Queue* queue1 = new Queue(0, 100, 1.0, DiscardPolicy::DROP_TAIL);
    Queue* queue2 = new Queue(1, 100, 1.0, DiscardPolicy::DROP_TAIL);
    
    queues.push_back(queue1);
    queues.push_back(queue2);
    
    SystemState systemState;
    systemState.queues = queues;
    systemState.currentTime = 0.0;
    systemState.globalArrivalRateEstimate = 1.0;
    
    // Inject statistics for average wait time calculation
    // queue1: average wait 10.0
    queue1->registerDepartureStats(10.0, 100.0);
    
    // queue2: average wait 20.0
    queue2->registerDepartureStats(20.0, 100.0);
    queue2->registerDepartureStats(20.0, 100.0);
    
    // Queues must be non-empty to be selectable
    Packet packet(1, 0.0, 1.0);
    queue1->tryEnqueue(packet);
    queue2->tryEnqueue(packet);
    
    MaxAverageWaitPolicy policy;
    int result = policy.selectQueue(systemState);
    assert(result == 1); // queue2 has higher average wait time
    
    // Cleanup
    for (auto queue : queues) {
        delete queue;
    }
    std::cout << " PASSED\n";
}

/**
 * @brief Test the Oldest Packet scheduling policy
 * @details Verifies that the policy correctly selects the queue with the oldest packet
 */
void testOldestPacketPolicy() {
    std::cout << "Testing Oldest Packet policy...";
    std::vector<Queue*> queues;
    
    Queue* queue1 = new Queue(0, 100, 1.0, DiscardPolicy::DROP_TAIL);
    Queue* queue2 = new Queue(1, 100, 1.0, DiscardPolicy::DROP_TAIL);
    
    queues.push_back(queue1);
    queues.push_back(queue2);
    
    SystemState systemState;
    systemState.queues = queues;
    systemState.currentTime = 100.0;
    systemState.globalArrivalRateEstimate = 1.0;
    
    // queue1: packet arrived at 90.0 (wait time 10.0)
    Packet packet1(1, 90.0, 1.0);
    queue1->tryEnqueue(packet1);
    
    // queue2: packet arrived at 80.0 (wait time 20.0)
    Packet packet2(2, 80.0, 1.0);
    queue2->tryEnqueue(packet2);
    
    OldestPacketPolicy policy;
    int result = policy.selectQueue(systemState);
    assert(result == 1); // queue2 has oldest packet (longest wait time)
    
    // Cleanup
    for (auto queue : queues) {
        delete queue;
    }
    std::cout << " PASSED\n";
}

/**
 * @brief Test the Salles Utility scheduling policy
 * @details Verifies that the policy correctly calculates utility loss and selects appropriate queue
 */
void testSallesUtilityPolicy() {
    std::cout << "Testing Salles Utility policy...";
    std::vector<Queue*> queues;
    
    // Create queues with different utility types:
    // Type 0: Best Effort (Linear), Type 1: Voice (Exponential), Type 2: Video (Quadratic)
    Queue* queue1 = new Queue(0, 100, 1.0, DiscardPolicy::DROP_TAIL, 1.0, 0);
    Queue* queue2 = new Queue(1, 100, 1.0, DiscardPolicy::DROP_TAIL, 1.0, 1);
    Queue* queue3 = new Queue(2, 100, 1.0, DiscardPolicy::DROP_TAIL, 1.0, 2);
    
    queues.push_back(queue1);
    queues.push_back(queue2);
    queues.push_back(queue3);
    
    SystemState systemState;
    systemState.queues = queues;
    systemState.currentTime = 10.0;
    
    // queue1 (Best Effort): wait 5.0 -> Loss = 1.0
    Packet packet1(1, 5.0, 1.0);
    queue1->tryEnqueue(packet1);
    
    // queue2 (Voice): wait 5.0 -> Loss = exp(0.1 * 5.0) = 1.648
    Packet packet2(2, 5.0, 1.0);
    queue2->tryEnqueue(packet2);
    
    // queue3 (Video): wait 2.0 -> Loss = 2.0^2 = 4.0
    Packet packet3(3, 8.0, 1.0);
    queue3->tryEnqueue(packet3);
    
    // Should select queue3 (highest loss 4.0)
    auto policy = PolicyOrchestrator::createPolicy("SALLES_UTILITY");
    int result = policy->selectQueue(systemState);
    assert(result == 2);
    
    for (auto queue : queues) {
        delete queue;
    }
    std::cout << " PASSED\n";
}

/**
 * @brief Test the cMu Rule scheduling policy
 * @details Verifies that the policy correctly calculates c*mu product and selects appropriate queue
 */
void testCMuRulePolicy() {
    std::cout << "Testing cMu Rule policy...";
    std::vector<Queue*> queues;
    
    // queue1: weight 1.0, service rate 1.0 -> index 1.0
    Queue* queue1 = new Queue(0, 100, 1.0, DiscardPolicy::DROP_TAIL, 1.0, 0);
    // queue2: weight 2.0, service rate 2.0 -> index 4.0
    Queue* queue2 = new Queue(1, 100, 2.0, DiscardPolicy::DROP_TAIL, 2.0, 0);
    
    queues.push_back(queue1);
    queues.push_back(queue2);
    
    SystemState systemState;
    systemState.queues = queues;
    
    Packet packet(1, 0.0, 1.0);
    queue1->tryEnqueue(packet);
    queue2->tryEnqueue(packet);
    
    auto policy = PolicyOrchestrator::createPolicy("C_MU_RULE");
    int result = policy->selectQueue(systemState);
    assert(result == 1); // queue2 has higher index
    
    for (auto queue : queues) {
        delete queue;
    }
    std::cout << " PASSED\n";
}

/**
 * @brief Test the Weighted Round Robin scheduling policy
 * @details Verifies that the policy correctly rotates through queues according to their weights
 */
void testWeightedRoundRobinPolicy() {
    std::cout << "Testing Weighted Round Robin policy...";
    std::vector<Queue*> queues;
    
    // queue1: weight 2.0 -> quantum 2
    Queue* queue1 = new Queue(0, 100, 1.0, DiscardPolicy::DROP_TAIL, 2.0, 0);
    // queue2: weight 1.0 -> quantum 1
    Queue* queue2 = new Queue(1, 100, 1.0, DiscardPolicy::DROP_TAIL, 1.0, 0);
    
    queues.push_back(queue1);
    queues.push_back(queue2);
    
    SystemState systemState;
    systemState.queues = queues;
    
    // Fill queues with packets
    Packet packet(1, 0.0, 1.0);
    for (int i = 0; i < 5; ++i) {
        queue1->tryEnqueue(packet);
        queue2->tryEnqueue(packet);
    }
    
    auto policy = PolicyOrchestrator::createPolicy("WEIGHTED_ROUND_ROBIN");
    
    // Expected sequence: queue1, queue1, queue2, queue1, queue1, queue2...
    assert(policy->selectQueue(systemState) == 0);
    assert(policy->selectQueue(systemState) == 0);
    assert(policy->selectQueue(systemState) == 1);
    assert(policy->selectQueue(systemState) == 0);
    
    for (auto queue : queues) {
        delete queue;
    }
    std::cout << " PASSED\n";
}

/**
 * @brief Test the Whittle Index scheduling policy
 * @details Verifies that the policy correctly calculates Whittle indices and selects appropriate queue
 */
void testWhittleIndexPolicy() {
    std::cout << "Testing Whittle Index policy...";
    std::vector<Queue*> queues;
    
    // queue1: length 10, service rate 1.0 -> Index = 10*1 / 11 ≈ 0.909
    Queue* queue1 = new Queue(0, 100, 1.0, DiscardPolicy::DROP_TAIL);
    // queue2: length 5, service rate 3.0 -> Index = 5*3 / 6 = 2.5
    Queue* queue2 = new Queue(1, 100, 3.0, DiscardPolicy::DROP_TAIL);
    
    queues.push_back(queue1);
    queues.push_back(queue2);
    
    SystemState systemState;
    systemState.queues = queues;
    
    Packet packet(1, 0.0, 1.0);
    for (int i = 0; i < 10; ++i) {
        queue1->tryEnqueue(packet);
    }
    for (int i = 0; i < 5; ++i) {
        queue2->tryEnqueue(packet);
    }
    
    auto policy = PolicyOrchestrator::createPolicy("WHITTLE_INDEX");
    int result = policy->selectQueue(systemState);
    assert(result == 1); // queue2 has higher Whittle index
    
    for (auto queue : queues) {
        delete queue;
    }
    std::cout << " PASSED\n";
}

/**
 * @brief Test the Markov Switching scheduling policy
 * @details Verifies that the policy correctly switches between policies based on system state
 */
void testMarkovSwitchingPolicy() {
    std::cout << "Testing Markov Switching policy...";
    std::vector<Queue*> queues;
    
    // Create 3 test queues
    Queue* queue1 = new Queue(0, 100, 1.0, DiscardPolicy::DROP_TAIL);
    Queue* queue2 = new Queue(1, 100, 1.0, DiscardPolicy::DROP_TAIL);
    Queue* queue3 = new Queue(2, 100, 1.0, DiscardPolicy::DROP_TAIL);
    
    queues.push_back(queue1);
    queues.push_back(queue2);
    queues.push_back(queue3);
    
    SystemState systemState;
    systemState.queues = queues;
    
    // Test various system states and verify policy switching behavior
    auto policy = PolicyOrchestrator::createPolicy("MARKOV_SWITCHING");
    
    // Case 1: queue1=10 packets, queue2=1 packet, queue3=0 packets
    // Should trigger Shortest Queue policy and select queue2
    Packet packet(1, 0.0, 1.0);
    for (int i = 0; i < 10; ++i) {
        queue1->tryEnqueue(packet);
    }
    queue2->tryEnqueue(packet);
    
    int result = policy->selectQueue(systemState);
    assert(result == 1); // Shortest non-empty is queue2
    
    // Case 2: All queues have equal packets
    // Should trigger tie-breaking behavior
    for (int i = 0; i < 10; ++i) {
        queue3->tryEnqueue(packet);
    }
    
    result = policy->selectQueue(systemState);
    // Verify reasonable selection based on Markov state
    assert(result >= 0 && result < 3);
    
    for (auto queue : queues) {
        delete queue;
    }
    std::cout << " PASSED\n";
}

/**
 * @brief Test the policy factory functionality
 * @details Verifies that policies can be correctly created by name and handle unknown names gracefully
 */
void testPolicyFactory() {
    std::cout << "Testing policy retrieval by name..." << std::endl;
    
    // Test valid policy creation
    auto policy = PolicyOrchestrator::createPolicy("LONGEST_QUEUE");
    assert(policy->getName() == "LONGEST_QUEUE");
    
    // Test default policy for unknown name
    auto defaultPolicy = PolicyOrchestrator::createPolicy("UNKNOWN_POLICY");
    assert(defaultPolicy->getName() == "LONGEST_QUEUE"); // Default fallback
    
    std::cout << " PASSED" << std::endl;
}

/**
 * @brief Test the Policy Orchestrator (Min-Heap based)
 * @details Verifies that the orchestrator correctly selects the queue based on minimum heap criteria
 */
void testPolicyOrchestrator() {
    std::cout << "Testing Policy Orchestrator (Min-Heap)...";
    std::vector<Queue*> queues;
    
    Queue* queue1 = new Queue(0, 100, 1.0, DiscardPolicy::DROP_TAIL);
    Queue* queue2 = new Queue(1, 100, 1.0, DiscardPolicy::DROP_TAIL);
    
    queues.push_back(queue1);
    queues.push_back(queue2);
    
    SystemState systemState;
    systemState.queues = queues;
    
    // queue1 has 10 packets, queue2 has 5 packets
    Packet packet(1, 0.0, 1.0);
    for (int i = 0; i < 10; ++i) {
        queue1->tryEnqueue(packet);
    }
    for (int i = 0; i < 5; ++i) {
        queue2->tryEnqueue(packet);
    }
    
    auto policy = PolicyOrchestrator::createPolicy("POLICY_ORCHESTRATOR");
    int result = policy->selectQueue(systemState);
    
    // Should pick queue2 (length 5 < 10) based on min-heap
    assert(result == 1);
    
    for (auto queue : queues) {
        delete queue;
    }
    std::cout << " PASSED\n";
}

/**
 * @brief Main test runner function
 * @details Executes all policy tests and reports results
 * @return int Returns 0 if all tests pass, non-zero otherwise
 */
int main() {
    std::cout << "Starting Policy Tests...\n" << std::endl;
    
    testLongestQueuePolicy();
    testMaxAverageWaitPolicy();
    testOldestPacketPolicy();
    testSallesUtilityPolicy();
    testCMuRulePolicy();
    testWeightedRoundRobinPolicy();
    testWhittleIndexPolicy();
    testMarkovSwitchingPolicy();
    testPolicyOrchestrator();
    testPolicyFactory();
    
    std::cout << "\nAll Policies tests passed!\n";
    return 0;
}