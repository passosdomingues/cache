#ifndef MAX_AVERAGE_WAIT_POLICY_HPP
#define MAX_AVERAGE_WAIT_POLICY_HPP

#include "SchedulingPolicy.hpp"

/**
 * @brief Max Average Wait policy - selects queue with highest average waiting time.
 */
class MaxAverageWaitPolicy : public SchedulingPolicy {
public:
    int selectQueue(const SystemState& state) override;
    std::string getName() const override { return "MAX_AVG_WAIT"; }
};

#endif // MAX_AVERAGE_WAIT_POLICY_HPP
