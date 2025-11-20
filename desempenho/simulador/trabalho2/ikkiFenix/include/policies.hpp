#ifndef POLICIES_HPP
#define POLICIES_HPP

#include "queue.hpp"
#include <vector>
#include <functional>

// Forward declaration
class SimulationState;

/**
 * @brief Policy function type for queue selection
 */
using QueueSelectionPolicy = std::function<int(
    const std::vector<QueueState*>& queues, 
    double currentTime,
    const SimulationState* simulationState
)>;

/**
 * @brief Policy implementations
 */
class SchedulingPolicies {
public:
    /**
     * @brief Round Robin policy - cycles through queues
     */
    static int selectRoundRobin(
        const std::vector<QueueState*>& queues,
        double currentTime,
        const SimulationState* simulationState
    );
    
    /**
     * @brief Waiting Time Priority - selects queue with longest head waiting time
     */
    static int selectWaitingTimePriority(
        const std::vector<QueueState*>& queues,
        double currentTime, 
        const SimulationState* simulationState
    );
    
    /**
     * @brief Utility Based - uses measurement window for average delay
     */
    static int selectUtilityBased(
        const std::vector<QueueState*>& queues,
        double currentTime,
        const SimulationState* simulationState
    );
    
    /**
     * @brief Largest Queue - selects queue with most packets
     */
    static int selectLargestQueue(
        const std::vector<QueueState*>& queues,
        double currentTime,
        const SimulationState* simulationState
    );
    
    /**
     * @brief Get policy by name
     * @param policyName Name of the policy
     * @return QueueSelectionPolicy Function pointer to policy
     */
    static QueueSelectionPolicy getPolicyByName(const std::string& policyName);
};

#endif // POLICIES_HPP