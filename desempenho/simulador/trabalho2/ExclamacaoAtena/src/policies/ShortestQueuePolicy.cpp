#include "../../include/policies/ShortestQueuePolicy.hpp"
#include "../../include/components.hpp"
#include <limits>

int ShortestQueuePolicy::selectQueue(const SystemState& state) {
    int selectedId = -1;
    int minLen = std::numeric_limits<int>::max();

    for (Queue* q : state.queues) {
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
