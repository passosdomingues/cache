#ifndef SHORTEST_QUEUE_POLICY_HPP
#define SHORTEST_QUEUE_POLICY_HPP

#include "SchedulingPolicy.hpp"

/**
 * @brief Shortest Queue policy - selects queue with minimum length.
 */
class ShortestQueuePolicy : public SchedulingPolicy {
public:
    int selectQueue(const SystemState& state) override;
    std::string getName() const override { return "SHORTEST_QUEUE"; }
};

#endif // SHORTEST_QUEUE_POLICY_HPP
