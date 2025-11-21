#include "../../include/policies/MarkovSwitchingPolicy.hpp"
#include "../../include/policies/LongestQueuePolicy.hpp"
#include "../../include/policies/ShortestQueuePolicy.hpp"
#include "../../include/policies/RoundRobinPolicy.hpp"
#include "../../include/policies/StrictPriorityPolicy.hpp"
#include "../../include/policies/MaxAverageWaitPolicy.hpp"
#include "../../include/components.hpp"
#include <fstream>
#include <iostream>

MarkovSwitchingPolicy::MarkovSwitchingPolicy(const std::string& matrixFile) {
    // Initialize available sub-policies
    subPolicies.push_back(std::make_unique<LongestQueuePolicy>());      // 0
    subPolicies.push_back(std::make_unique<ShortestQueuePolicy>());     // 1
    subPolicies.push_back(std::make_unique<RoundRobinPolicy>());        // 2
    subPolicies.push_back(std::make_unique<StrictPriorityPolicy>());    // 3
    subPolicies.push_back(std::make_unique<MaxAverageWaitPolicy>());    // 4
    
    // Load matrix
    loadPolicyMatrix(matrixFile);
}

void MarkovSwitchingPolicy::loadPolicyMatrix(const std::string& filename) {
    // Default: Map all states to LongestQueue (Index 0)
    stateToPolicyMap.assign(10000, 0); 
    
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Warning: Could not open policy matrix '" << filename << "'. Using default policy." << std::endl;
        return;
    }
    
    std::string line;
    // Skip header
    std::getline(file, line);
    
    while (std::getline(file, line)) {
        // Format: state_id,policy_id
        size_t commaPos = line.find(',');
        if (commaPos != std::string::npos) {
            int stateId = std::stoi(line.substr(0, commaPos));
            int policyId = std::stoi(line.substr(commaPos + 1));
            
            if (stateId >= 0 && stateId < (int)stateToPolicyMap.size()) {
                if (policyId >= 0 && policyId < (int)subPolicies.size()) {
                    stateToPolicyMap[stateId] = policyId;
                }
            }
        }
    }
    std::cout << "Loaded Markov Policy Matrix from " << filename << std::endl;
}

int MarkovSwitchingPolicy::discretizeState(const SystemState& state) {
    auto getBin = [](int len) {
        if (len <= 5) return 0;
        if (len <= 20) return 1;
        return 2;
    };
    
    int id = 0;
    int multiplier = 1;
    
    for (Queue* q : state.queues) {
        id += getBin(q->getLength()) * multiplier;
        multiplier *= 3;
    }
    
    return id;
}

int MarkovSwitchingPolicy::selectQueue(const SystemState& state) {
    int stateId = discretizeState(state);
    
    int policyIdx = defaultPolicyIndex;
    if (stateId >= 0 && stateId < (int)stateToPolicyMap.size()) {
        policyIdx = stateToPolicyMap[stateId];
    }
    
    return subPolicies[policyIdx]->selectQueue(state);
}
