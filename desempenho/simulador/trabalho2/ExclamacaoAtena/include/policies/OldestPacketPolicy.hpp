#ifndef OLDEST_PACKET_POLICY_HPP
#define OLDEST_PACKET_POLICY_HPP

#include "SchedulingPolicy.hpp"

/**
 * @brief Oldest Packet policy - selects queue with packet that has waited longest.
 */
class OldestPacketPolicy : public SchedulingPolicy {
public:
    int selectQueue(const SystemState& state) override;
    std::string getName() const override { return "OLDEST_PACKET"; }
};

#endif // OLDEST_PACKET_POLICY_HPP
