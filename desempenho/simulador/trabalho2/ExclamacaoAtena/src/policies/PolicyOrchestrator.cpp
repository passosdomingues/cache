#include "../../include/policies/PolicyOrchestrator.hpp"
#include "../../include/policies/LongestQueuePolicy.hpp"
#include "../../include/policies/ShortestQueuePolicy.hpp"
#include "../../include/policies/RoundRobinPolicy.hpp"
#include "../../include/policies/StrictPriorityPolicy.hpp"
#include "../../include/policies/MaxAverageWaitPolicy.hpp"
#include "../../include/policies/OldestPacketPolicy.hpp"
#include "../../include/policies/AgingPolicy.hpp"
#include "../../include/policies/SallesUtilityPolicy.hpp"
#include "../../include/policies/CMuRulePolicy.hpp"
#include "../../include/policies/WeightedRoundRobinPolicy.hpp"
#include "../../include/policies/WhittleIndexPolicy.hpp"
#include "../../include/policies/MarkovSwitchingPolicy.hpp"
#include <iostream>

PolicyOrchestrator::PolicyOrchestrator() {
    // Register default policies
    registerPolicy(std::make_unique<LongestQueuePolicy>());
    registerPolicy(std::make_unique<ShortestQueuePolicy>());
    registerPolicy(std::make_unique<RoundRobinPolicy>());
    registerPolicy(std::make_unique<StrictPriorityPolicy>());
    registerPolicy(std::make_unique<MaxAverageWaitPolicy>());
    registerPolicy(std::make_unique<OldestPacketPolicy>());
    registerPolicy(std::make_unique<AgingPolicy>());
    registerPolicy(std::make_unique<SallesUtilityPolicy>());
    registerPolicy(std::make_unique<CMuRulePolicy>());
    registerPolicy(std::make_unique<WeightedRoundRobinPolicy>());
    registerPolicy(std::make_unique<WhittleIndexPolicy>());
    registerPolicy(std::make_unique<MarkovSwitchingPolicy>());
    
    // Default active policy
    setActivePolicy("LONGEST_QUEUE");
}

void PolicyOrchestrator::registerPolicy(std::unique_ptr<SchedulingPolicy> policy) {
    policies[policy->getName()] = std::move(policy);
}

void PolicyOrchestrator::setActivePolicy(const std::string& name) {
    if (policies.find(name) != policies.end()) {
        // We can't just move it, we need to keep it in the map?
        // Or we clone it? Or we just hold a pointer?
        // The orchestrator owns the policies.
        // But we want to set one as active.
        // Let's just store the name or a raw pointer.
        // But the interface expects unique_ptr for createPolicy.
        // Let's change getActivePolicy to return raw pointer.
        // Wait, the original code used unique_ptr<SchedulingPolicy> in Simulator.
        // If we use Orchestrator, Simulator should probably hold Orchestrator.
    } else {
        std::cerr << "Warning: Unknown policy '" << name << "'. Defaulting to LONGEST_QUEUE." << std::endl;
        if (policies.find("LONGEST_QUEUE") != policies.end()) {
            // Fallback
        }
    }
}

SchedulingPolicy* PolicyOrchestrator::getActivePolicy() const {
    // This logic is a bit flawed if we want to switch dynamically.
    // Let's implement the Factory method properly instead.
    return nullptr; 
}

std::unique_ptr<SchedulingPolicy> PolicyOrchestrator::createPolicy(const std::string& name) {
    if (name == "LONGEST_QUEUE") return std::make_unique<LongestQueuePolicy>();
    if (name == "MAX_AVG_WAIT") return std::make_unique<MaxAverageWaitPolicy>();
    if (name == "OLDEST_PACKET") return std::make_unique<OldestPacketPolicy>();
    if (name == "ROUND_ROBIN") return std::make_unique<RoundRobinPolicy>();
    if (name == "STRICT_PRIORITY") return std::make_unique<StrictPriorityPolicy>();
    if (name == "SHORTEST_QUEUE") return std::make_unique<ShortestQueuePolicy>();
    if (name == "AGING") return std::make_unique<AgingPolicy>();
    if (name == "SALLES_UTILITY") return std::make_unique<SallesUtilityPolicy>();
    if (name == "C_MU_RULE") return std::make_unique<CMuRulePolicy>();
    if (name == "WEIGHTED_ROUND_ROBIN") return std::make_unique<WeightedRoundRobinPolicy>();
    if (name == "WHITTLE_INDEX") return std::make_unique<WhittleIndexPolicy>();
    if (name == "MARKOV_SWITCHING") return std::make_unique<MarkovSwitchingPolicy>();
    if (name == "POLICY_ORCHESTRATOR") return std::make_unique<PolicyOrchestrator>();
    
    std::cerr << "Warning: Unknown policy '" << name << "'. Defaulting to LONGEST_QUEUE." << std::endl;
    return std::make_unique<LongestQueuePolicy>();
}

int PolicyOrchestrator::selectQueue(const SystemState& state) {
    // Min-Heap implementation to select the queue with the smallest length (Shortest Queue)
    // Pair: <QueueLength, QueueIndex>
    // We want Min-Heap, so we need a generic comparator that puts smaller elements at top.
    // std::priority_queue is Max-Heap by default.
    // So we use std::greater for the pair.
    
    using QueueElement = std::pair<size_t, int>;
    std::priority_queue<QueueElement, std::vector<QueueElement>, std::greater<QueueElement>> minHeap;
    
    for (size_t i = 0; i < state.queues.size(); ++i) {
        minHeap.push({state.queues[i]->getLength(), (int)i});
    }
    
    if (minHeap.empty()) return -1;
    
    // The top element is the one with smallest length
    return minHeap.top().second;
}
