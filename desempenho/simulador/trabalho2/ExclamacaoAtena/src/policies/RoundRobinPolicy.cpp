#include "../../include/policies/RoundRobinPolicy.hpp"
#include "../../include/components.hpp"

int RoundRobinPolicy::selectQueue(const SystemState& state) {
    if (state.queues.empty()) return -1;
    
    int numQueues = static_cast<int>(state.queues.size());
    int startIdx = (lastSelectedQueue + 1) % numQueues;
    
    for (int i = 0; i < numQueues; ++i) {
        int idx = (startIdx + i) % numQueues;
        if (!state.queues[idx]->isEmpty()) {
            lastSelectedQueue = idx;
            return state.queues[idx]->getId();
        }
    }
    return -1;
}
