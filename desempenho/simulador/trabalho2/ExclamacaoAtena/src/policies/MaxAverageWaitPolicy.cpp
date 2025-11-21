#include "../../include/policies/MaxAverageWaitPolicy.hpp"
#include "../../include/components.hpp"

int MaxAverageWaitPolicy::selectQueue(const SystemState& state) {
    int selectedId = -1;
    double maxWait = -1.0;

    for (Queue* q : state.queues) {
        if (q->isEmpty()) continue;
        
        double wait = q->getAverageWaitingTime();
        if (wait > maxWait || (wait == maxWait && (selectedId == -1 || q->getId() < selectedId))) {
            maxWait = wait;
            selectedId = q->getId();
        }
    }
    return selectedId;
}
