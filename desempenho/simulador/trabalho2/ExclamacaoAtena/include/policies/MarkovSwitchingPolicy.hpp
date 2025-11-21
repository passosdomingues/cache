#ifndef MARKOV_SWITCHING_POLICY_HPP
#define MARKOV_SWITCHING_POLICY_HPP

#include "SchedulingPolicy.hpp"
#include <vector>
#include <memory>
#include <string>

/**
 * @brief Markov Switching Policy (The Python-C++ Link)
 * Selects sub-policy based on discretized state and loaded matrix.
 */
class MarkovSwitchingPolicy : public SchedulingPolicy {
private:
    std::vector<std::unique_ptr<SchedulingPolicy>> subPolicies;
    std::vector<int> stateToPolicyMap; // Index = StateID, Value = PolicyIndex
    int defaultPolicyIndex = 0;
    
    int discretizeState(const SystemState& state);
    
public:
    MarkovSwitchingPolicy(const std::string& matrixFile = "analysis/policy_matrix.csv");
    int selectQueue(const SystemState& state) override;
    std::string getName() const override { return "MARKOV_SWITCHING"; }
    
    void loadPolicyMatrix(const std::string& filename);
};

#endif // MARKOV_SWITCHING_POLICY_HPP
