#ifndef SCHEDULING_POLICY_HPP
#define SCHEDULING_POLICY_HPP

#include <vector>
#include <string>
#include <memory>
#include "../components.hpp"

// Forward declaration
class Queue;

/**
 * @brief Snapshot of the system state for policy decisions.
 */
struct SystemState {
    std::vector<Queue*> queues;
    double globalArrivalRateEstimate;
    double currentTime;
    
    // Helper to get a specific queue by ID
    Queue* getQueue(int id) const {
        for (auto* q : queues) {
            if (q->getId() == id) return q;
        }
        return nullptr;
    }
};

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
     * @param state Current system state snapshot
     * @return Queue ID to serve, or -1 if no queue is available
     */
    virtual int selectQueue(const SystemState& state) = 0;
    
    /**
     * @brief Get the policy name for logging/identification.
     * @return Policy name string
     */
    virtual std::string getName() const = 0;
};

#endif // SCHEDULING_POLICY_HPP
