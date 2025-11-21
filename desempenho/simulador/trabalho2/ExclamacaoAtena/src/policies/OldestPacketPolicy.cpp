#include "../../include/policies/OldestPacketPolicy.hpp"
#include "../../include/components.hpp"

int OldestPacketPolicy::selectQueue(const SystemState& state) {
    int selectedId = -1;
    double maxWait = -1.0;

    for (Queue* q : state.queues) {
        if (q->isEmpty()) continue;
        
        // Head waiting time = Current Time - Arrival Time of Head
        double wait = q->getHeadWaitingTime(state.currentTime);
        
        if (wait > maxWait || (wait == maxWait && (selectedId == -1 || q->getId() < selectedId))) {
            maxWait = wait;
            selectedId = q->getId();
        }
    }
    return selectedId;
}
