#ifndef LONGEST_QUEUE_POLICY_HPP
#define LONGEST_QUEUE_POLICY_HPP

#include "SchedulingPolicy.hpp"

/**
 * @brief Longest Queue policy - selects queue with maximum length.
 */
class LongestQueuePolicy : public SchedulingPolicy {
public:
    int selectQueue(const SystemState& state) override;
    std::string getName() const override { return "LONGEST_QUEUE"; }
};

#endif // LONGEST_QUEUE_POLICY_HPP
