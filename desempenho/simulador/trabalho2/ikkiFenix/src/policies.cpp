#include "../include/policies.hpp"
#include "simulator.hpp"

// Static variable for Round Robin state
static int lastServedQueue = -1;

int SchedulingPolicies::selectRoundRobin(
    const std::vector<QueueState*>& queues,
    double currentTime,
    const SimulationState* simulationState) {
    
    const int numQueues = queues.size();
    
    // Find next non-empty queue starting from last served
    for (int attempts = 0; attempts < numQueues; attempts++) {
        lastServedQueue = (lastServedQueue + 1) % numQueues;
        
        if (queues[lastServedQueue]->getCurrentQueueLength() > 0) {
            return lastServedQueue;
        }
    }
    
    return -1; // No non-empty queues
}

int SchedulingPolicies::selectWaitingTimePriority(
    const std::vector<QueueState*>& queues,
    double currentTime,
    const SimulationState* simulationState) {
    
    int selectedQueue = -1;
    double maxWaitingTime = -1.0;
    
    for (int i = 0; i < (int)queues.size(); i++) {
        if (queues[i]->getCurrentQueueLength() > 0) {
            double waitingTime = queues[i]->peekHeadWaitingTime(currentTime);
            if (waitingTime > maxWaitingTime) {
                maxWaitingTime = waitingTime;
                selectedQueue = i;
            }
        }
    }
    
    return selectedQueue;
}

int SchedulingPolicies::selectUtilityBased(
    const std::vector<QueueState*>& queues,
    double currentTime,
    const SimulationState* simulationState) {
    
    int selectedQueue = -1;
    double maxAverageDelay = -1.0;
    
    for (int i = 0; i < (int)queues.size(); i++) {
        if (queues[i]->getCurrentQueueLength() > 0) {
            // Use measurement window for average delay calculation
            const auto& window = queues[i]->getMeasurementWindow();
            if (window.getTotalPacketsInWindow() > 0) {
                double n_t = queues[i]->getCurrentQueueLength() * currentTime;
                double avgDelay = (1.0 / window.getTotalPacketsInWindow()) * 
                                 (n_t - window.getSumArrivalTimestamps() + window.getSumWaitingTimes());
                
                if (avgDelay > maxAverageDelay) {
                    maxAverageDelay = avgDelay;
                    selectedQueue = i;
                }
            } else {
                // Fallback to head waiting time if no window data
                double waitingTime = queues[i]->peekHeadWaitingTime(currentTime);
                if (waitingTime > maxAverageDelay) {
                    maxAverageDelay = waitingTime;
                    selectedQueue = i;
                }
            }
        }
    }
    
    return selectedQueue;
}

int SchedulingPolicies::selectLargestQueue(
    const std::vector<QueueState*>& queues,
    double currentTime,
    const SimulationState* simulationState) {
    
    int selectedQueue = -1;
    unsigned long maxLength = 0;
    
    for (int i = 0; i < (int)queues.size(); i++) {
        unsigned long length = queues[i]->getCurrentQueueLength();
        if (length > maxLength) {
            maxLength = length;
            selectedQueue = i;
        }
    }
    
    return selectedQueue;
}

QueueSelectionPolicy SchedulingPolicies::getPolicyByName(const std::string& policyName) {
    if (policyName == "RoundRobin") {
        return selectRoundRobin;
    } else if (policyName == "WaitingTimePriority") {
        return selectWaitingTimePriority;
    } else if (policyName == "UtilityBased") {
        return selectUtilityBased;
    } else if (policyName == "LargestQueue") {
        return selectLargestQueue;
    } else {
        throw std::invalid_argument("Unknown policy: " + policyName);
    }
}