#ifndef WEIGHTED_ROUND_ROBIN_POLICY_HPP
#define WEIGHTED_ROUND_ROBIN_POLICY_HPP

#include "SchedulingPolicy.hpp"

/**
 * @brief Weighted Round Robin Policy (Robustness)
 * Prevents starvation using quantum counters.
 */
class WeightedRoundRobinPolicy : public SchedulingPolicy {
private:
    mutable int lastSelectedQueue = -1;
    mutable std::vector<int> currentQuantum;
    const int baseQuantum = 1;
public:
    int selectQueue(const SystemState& state) override;
    std::string getName() const override { return "WEIGHTED_ROUND_ROBIN"; }
};

#endif // WEIGHTED_ROUND_ROBIN_POLICY_HPP
