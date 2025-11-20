/**
 * @file policies.cpp
 * @brief Implementation of policy logic.
 */

#include "../include/policies.hpp"
#include <limits>
#include <iostream>

namespace Policies {

    int LongestQueue(const std::vector<Queue*>& queues, double /*currentTime*/) {
        int selectedId = -1;
        int maxLen = -1;

        for (Queue* q : queues) {
            if (q->isEmpty()) continue;
            
            int len = q->getLength();
            if (len > maxLen) {
                maxLen = len;
                selectedId = q->getId();
            }
        }
        return selectedId;
    }

    int MaxAverageWait(const std::vector<Queue*>& queues, double /*currentTime*/) {
        int selectedId = -1;
        double maxAvg = -1.0;

        for (Queue* q : queues) {
            if (q->isEmpty()) continue;

            double avg = q->getAverageWaitingTime();
            if (avg > maxAvg) {
                maxAvg = avg;
                selectedId = q->getId();
            }
        }
        return selectedId;
    }

    int OldestPacket(const std::vector<Queue*>& queues, double currentTime) {
        int selectedId = -1;
        double maxWait = -1.0;

        for (Queue* q : queues) {
            if (q->isEmpty()) continue;

            double wait = q->getHeadWaitingTime(currentTime);
            if (wait > maxWait) {
                maxWait = wait;
                selectedId = q->getId();
            }
        }
        return selectedId;
    }

    PolicyFunction getPolicyByName(const std::string& name) {
        if (name == "LONGEST_QUEUE") return LongestQueue;
        if (name == "MAX_AVG_WAIT") return MaxAverageWait;
        if (name == "OLDEST_PACKET") return OldestPacket;
        
        std::cerr << "Warning: Unknown policy '" << name << "'. Defaulting to LONGEST_QUEUE." << std::endl;
        return LongestQueue;
    }
}