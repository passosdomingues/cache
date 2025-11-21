#include "../../include/policies/LongestQueuePolicy.hpp"
#include "../../include/components.hpp"

int LongestQueuePolicy::selectQueue(const SystemState& state) {
    int selectedId = -1;
    unsigned long maxLen = 0;
    
    for (Queue* q : state.queues) {
        if (q->isEmpty()) continue;
        
        if (q->getLength() > (int)maxLen || (q->getLength() == (int)maxLen && (selectedId == -1 || q->getId() < selectedId))) {
            maxLen = q->getLength();
            selectedId = q->getId();
        }
    }
    return selectedId;
}
