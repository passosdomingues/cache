#ifndef AGING_POLICY_HPP
#define AGING_POLICY_HPP

#include "SchedulingPolicy.hpp"

/**
 * @brief Aging policy - prevents starvation by boosting priority of old packets.
 */
class AgingPolicy : public SchedulingPolicy {
private:
    double agingThreshold;  // Time threshold for priority boost
public:
    explicit AgingPolicy(double threshold = 10.0) : agingThreshold(threshold) {}
    int selectQueue(const SystemState& state) override;
    std::string getName() const override { return "AGING"; }
};

#endif // AGING_POLICY_HPP
