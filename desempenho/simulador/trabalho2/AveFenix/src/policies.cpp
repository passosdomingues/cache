/**
 * @file policies.cpp
 * @brief Implementation of all scheduling policies.
 */

#include "../include/policies.hpp"
#include <limits>
#include <iostream>
#include <algorithm>

// ============================================================================
// LONGEST QUEUE POLICY
// ============================================================================

int LongestQueuePolicy::selectQueue(const std::vector<Queue*>& queues, double /*currentTime*/) {
    int selectedId = -1;
    int maxLen = -1;

    for (Queue* q : queues) {
        if (q->isEmpty()) continue;
        
        int len = q->getLength();
        if (len > maxLen || (len == maxLen && (selectedId == -1 || q->getId() < selectedId))) {
            maxLen = len;
            selectedId = q->getId();
        }
    }
    return selectedId;
}

// ============================================================================
// MAX AVERAGE WAIT POLICY
// ============================================================================

int MaxAverageWaitPolicy::selectQueue(const std::vector<Queue*>& queues, double /*currentTime*/) {
    int selectedId = -1;
    double maxAvg = -1.0;

    for (Queue* q : queues) {
        if (q->isEmpty()) continue;

        double avg = q->getAverageWaitingTime();
        if (avg > maxAvg || (avg == maxAvg && (selectedId == -1 || q->getId() < selectedId))) {
            maxAvg = avg;
            selectedId = q->getId();
        }
    }
    return selectedId;
}

// ============================================================================
// OLDEST PACKET POLICY
// ============================================================================

int OldestPacketPolicy::selectQueue(const std::vector<Queue*>& queues, double currentTime) {
    int selectedId = -1;
    double maxWait = -1.0;

    for (Queue* q : queues) {
        if (q->isEmpty()) continue;

        double wait = q->getHeadWaitingTime(currentTime);
        if (wait > maxWait || (wait == maxWait && (selectedId == -1 || q->getId() < selectedId))) {
            maxWait = wait;
            selectedId = q->getId();
        }
    }
    return selectedId;
}

// ============================================================================
// ROUND ROBIN POLICY (NEW - JOB-06)
// ============================================================================

int RoundRobinPolicy::selectQueue(const std::vector<Queue*>& queues, double /*currentTime*/) {
    if (queues.empty()) return -1;
    
    int numQueues = static_cast<int>(queues.size());
    int startIdx = (lastSelectedQueue + 1) % numQueues;
    
    // Search from next queue in round-robin order
    for (int i = 0; i < numQueues; ++i) {
        int idx = (startIdx + i) % numQueues;
        if (!queues[idx]->isEmpty()) {
            lastSelectedQueue = idx;
            return queues[idx]->getId();
        }
    }
    
    return -1;  // All queues empty
}

// ============================================================================
// STRICT PRIORITY POLICY (NEW - JOB-07)
// ============================================================================

int StrictPriorityPolicy::selectQueue(const std::vector<Queue*>& queues, double /*currentTime*/) {
    // Queue 0 has absolute priority, then Queue 1, then Queue 2
    for (Queue* q : queues) {
        if (!q->isEmpty()) {
            return q->getId();
        }
    }
    return -1;  // All queues empty
}

// ============================================================================
// SHORTEST QUEUE POLICY (NEW - JOB-08)
// ============================================================================

int ShortestQueuePolicy::selectQueue(const std::vector<Queue*>& queues, double /*currentTime*/) {
    int selectedId = -1;
    int minLen = std::numeric_limits<int>::max();

    for (Queue* q : queues) {
        if (q->isEmpty()) continue;
        
        int len = q->getLength();
        // Deterministic tie-breaking: prefer lower queue ID
        if (len < minLen || (len == minLen && (selectedId == -1 || q->getId() < selectedId))) {
            minLen = len;
            selectedId = q->getId();
        }
    }
    return selectedId;
}

// ============================================================================
// AGING POLICY (NEW - JOB-09)
// ============================================================================

int AgingPolicy::selectQueue(const std::vector<Queue*>& queues, double currentTime) {
    int selectedId = -1;
    double maxWait = -1.0;
    bool foundAgedPacket = false;

    // First pass: Check for packets exceeding aging threshold
    for (Queue* q : queues) {
        if (q->isEmpty()) continue;

        double wait = q->getHeadWaitingTime(currentTime);
        
        // If packet has aged beyond threshold, prioritize it
        if (wait >= agingThreshold) {
            if (!foundAgedPacket || wait > maxWait) {
                foundAgedPacket = true;
                maxWait = wait;
                selectedId = q->getId();
            } else if (wait == maxWait && q->getId() < selectedId) {
                // Tie-breaking: prefer lower queue ID
                selectedId = q->getId();
            }
        }
    }
    
    // If aged packet found, serve it
    if (foundAgedPacket) {
        return selectedId;
    }
    
    // Otherwise, fall back to longest queue policy
    int maxLen = -1;
    for (Queue* q : queues) {
        if (q->isEmpty()) continue;
        
        int len = q->getLength();
        if (len > maxLen || (len == maxLen && (selectedId == -1 || q->getId() < selectedId))) {
            maxLen = len;
            selectedId = q->getId();
        }
    }
    
    return selectedId;
}

// ============================================================================
// FACTORY METHOD
// ============================================================================

namespace Policies {

std::unique_ptr<SchedulingPolicy> createPolicy(const std::string& name) {
    if (name == "LONGEST_QUEUE") return std::make_unique<LongestQueuePolicy>();
    if (name == "MAX_AVG_WAIT") return std::make_unique<MaxAverageWaitPolicy>();
    if (name == "OLDEST_PACKET") return std::make_unique<OldestPacketPolicy>();
    if (name == "ROUND_ROBIN") return std::make_unique<RoundRobinPolicy>();
    if (name == "STRICT_PRIORITY") return std::make_unique<StrictPriorityPolicy>();
    if (name == "SHORTEST_QUEUE") return std::make_unique<ShortestQueuePolicy>();
    if (name == "AGING") return std::make_unique<AgingPolicy>();
    
    std::cerr << "Warning: Unknown policy '" << name << "'. Defaulting to LONGEST_QUEUE." << std::endl;
    return std::make_unique<LongestQueuePolicy>();
}

// ============================================================================
// LEGACY FUNCTION-BASED POLICIES (Backward Compatibility)
// ============================================================================

int LongestQueue(const std::vector<Queue*>& queues, double currentTime) {
    LongestQueuePolicy policy;
    return policy.selectQueue(queues, currentTime);
}

int MaxAverageWait(const std::vector<Queue*>& queues, double currentTime) {
    MaxAverageWaitPolicy policy;
    return policy.selectQueue(queues, currentTime);
}

int OldestPacket(const std::vector<Queue*>& queues, double currentTime) {
    OldestPacketPolicy policy;
    return policy.selectQueue(queues, currentTime);
}

PolicyFunction getPolicyByName(const std::string& name) {
    if (name == "LONGEST_QUEUE") return LongestQueue;
    if (name == "MAX_AVG_WAIT") return MaxAverageWait;
    if (name == "OLDEST_PACKET") return OldestPacket;
    
    std::cerr << "Warning: Unknown policy '" << name << "'. Defaulting to LONGEST_QUEUE." << std::endl;
    return LongestQueue;
}

} // namespace Policies