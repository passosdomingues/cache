#ifndef STRICT_PRIORITY_POLICY_HPP
#define STRICT_PRIORITY_POLICY_HPP

#include "SchedulingPolicy.hpp"

/**
 * @brief Strict Priority policy - Queue 0 > Queue 1 > Queue 2 (strict QoS).
 */
class StrictPriorityPolicy : public SchedulingPolicy {
public:
    int selectQueue(const SystemState& state) override;
    std::string getName() const override { return "STRICT_PRIORITY"; }
};

#endif // STRICT_PRIORITY_POLICY_HPP
