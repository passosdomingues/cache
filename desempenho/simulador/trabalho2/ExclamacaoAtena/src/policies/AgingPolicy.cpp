#include "../../include/policies/AgingPolicy.hpp"
#include "../../include/components.hpp"

int AgingPolicy::selectQueue(const SystemState& state) {
    int selectedId = -1;
    double maxPriority = -1.0;

    for (Queue* q : state.queues) {
        if (q->isEmpty()) continue;
        
        double wait = q->getHeadWaitingTime(state.currentTime);
        double priority = (double)q->getLength();
        
        // Boost priority if wait time exceeds threshold
        if (wait > agingThreshold) {
            priority += (wait - agingThreshold) * 10.0; // Boost factor
        }
        
        if (priority > maxPriority || (priority == maxPriority && (selectedId == -1 || q->getId() < selectedId))) {
            maxPriority = priority;
            selectedId = q->getId();
        }
    }
    return selectedId;
}
