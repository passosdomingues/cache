/**
 * @file policies.hpp
 * @brief Definition of queue selection policies for the shared server.
 */

#ifndef POLICIES_HPP
#define POLICIES_HPP

#include <vector>
#include <functional>
#include <memory>
#include "components.hpp"

// Forward declaration
class Queue;

// ============================================================================
// POLYMORPHIC POLICY INTERFACE (Phase 2)
// ============================================================================

/**
 * @brief Abstract base class for scheduling policies.
 * 
 * All scheduling policies must inherit from this class and implement
 * the selectQueue() method. This enables polymorphic policy injection.
 */
class SchedulingPolicy {
public:
    virtual ~SchedulingPolicy() = default;
    
    /**
     * @brief Select the next queue to serve.
     * @param queues Vector of available queues
     * @param currentTime Current simulation time
     * @return Queue ID to serve, or -1 if no queue is available
     */
    virtual int selectQueue(const std::vector<Queue*>& queues, double currentTime) = 0;
    
    /**
     * @brief Get the policy name for logging/identification.
     * @return Policy name string
     */
    virtual std::string getName() const = 0;
};

// ============================================================================
// CONCRETE POLICY IMPLEMENTATIONS
// ============================================================================

/**
 * @brief Longest Queue policy - selects queue with maximum length.
 */
class LongestQueuePolicy : public SchedulingPolicy {
public:
    int selectQueue(const std::vector<Queue*>& queues, double currentTime) override;
    std::string getName() const override { return "LONGEST_QUEUE"; }
};

/**
 * @brief Max Average Wait policy - selects queue with highest average waiting time.
 */
class MaxAverageWaitPolicy : public SchedulingPolicy {
public:
    int selectQueue(const std::vector<Queue*>& queues, double currentTime) override;
    std::string getName() const override { return "MAX_AVG_WAIT"; }
};

/**
 * @brief Oldest Packet policy - selects queue with packet that has waited longest.
 */
class OldestPacketPolicy : public SchedulingPolicy {
public:
    int selectQueue(const std::vector<Queue*>& queues, double currentTime) override;
    std::string getName() const override { return "OLDEST_PACKET"; }
};

/**
 * @brief Round Robin policy - cycles through non-empty queues.
 */
class RoundRobinPolicy : public SchedulingPolicy {
private:
    mutable int lastSelectedQueue = -1;
public:
    int selectQueue(const std::vector<Queue*>& queues, double currentTime) override;
    std::string getName() const override { return "ROUND_ROBIN"; }
};

/**
 * @brief Strict Priority policy - Queue 0 > Queue 1 > Queue 2 (strict QoS).
 */
class StrictPriorityPolicy : public SchedulingPolicy {
public:
    int selectQueue(const std::vector<Queue*>& queues, double currentTime) override;
    std::string getName() const override { return "STRICT_PRIORITY"; }
};

/**
 * @brief Shortest Queue policy - selects queue with minimum length.
 */
class ShortestQueuePolicy : public SchedulingPolicy {
public:
    int selectQueue(const std::vector<Queue*>& queues, double currentTime) override;
    std::string getName() const override { return "SHORTEST_QUEUE"; }
};

/**
 * @brief Aging policy - prevents starvation by boosting priority of old packets.
 */
class AgingPolicy : public SchedulingPolicy {
private:
    double agingThreshold;  // Time threshold for priority boost
public:
    explicit AgingPolicy(double threshold = 10.0) : agingThreshold(threshold) {}
    int selectQueue(const std::vector<Queue*>& queues, double currentTime) override;
    std::string getName() const override { return "AGING"; }
};

// ============================================================================
// FACTORY AND LEGACY SUPPORT
// ============================================================================

typedef std::function<int(const std::vector<Queue*>&, double)> PolicyFunction;
using QueueSelectionPolicy = PolicyFunction;

namespace Policies {
    /**
     * @brief Factory method to create policy by name.
     * @param name Policy name string
     * @return Unique pointer to policy instance
     */
    std::unique_ptr<SchedulingPolicy> createPolicy(const std::string& name);
    
    // Legacy function-based policies (for backward compatibility)
    int LongestQueue(const std::vector<Queue*>& queues, double currentTime);
    int MaxAverageWait(const std::vector<Queue*>& queues, double currentTime);
    int OldestPacket(const std::vector<Queue*>& queues, double currentTime);
    
    PolicyFunction getPolicyByName(const std::string& name);
}

#endif // POLICIES_HPP