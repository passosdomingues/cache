#ifndef ROUND_ROBIN_POLICY_HPP
#define ROUND_ROBIN_POLICY_HPP

#include "SchedulingPolicy.hpp"

/**
 * @brief Round Robin policy - cycles through non-empty queues.
 */
class RoundRobinPolicy : public SchedulingPolicy {
private:
    mutable int lastSelectedQueue = -1;
public:
    int selectQueue(const SystemState& state) override;
    std::string getName() const override { return "ROUND_ROBIN"; }
};

#endif // ROUND_ROBIN_POLICY_HPP
