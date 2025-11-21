#ifndef WHITTLE_INDEX_POLICY_HPP
#define WHITTLE_INDEX_POLICY_HPP

#include "SchedulingPolicy.hpp"

/**
 * @brief Whittle Index Policy (Restless Bandits)
 * Look-ahead heuristic for potential reduction in future congestion.
 */
class WhittleIndexPolicy : public SchedulingPolicy {
public:
    int selectQueue(const SystemState& state) override;
    std::string getName() const override { return "WHITTLE_INDEX"; }
};

#endif // WHITTLE_INDEX_POLICY_HPP
