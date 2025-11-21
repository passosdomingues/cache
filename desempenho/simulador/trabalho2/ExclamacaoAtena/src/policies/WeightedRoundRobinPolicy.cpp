#include "../../include/policies/WeightedRoundRobinPolicy.hpp"
#include "../../include/components.hpp"

int WeightedRoundRobinPolicy::selectQueue(const SystemState& state) {
    if (state.queues.empty()) return -1;
    
    int numQueues = static_cast<int>(state.queues.size());
    
    // Initialize quantums if needed
    if (currentQuantum.size() != state.queues.size()) {
        currentQuantum.assign(numQueues, 0);
        for (int i = 0; i < numQueues; ++i) {
            currentQuantum[i] = static_cast<int>(state.queues[i]->getWeight() * baseQuantum);
        }
    }
    
    // 1. Try to continue serving lastSelectedQueue if it has quantum and packets
    if (lastSelectedQueue != -1 && currentQuantum[lastSelectedQueue] > 0 && !state.queues[lastSelectedQueue]->isEmpty()) {
        currentQuantum[lastSelectedQueue]--;
        return state.queues[lastSelectedQueue]->getId();
    }

    // 2. If not, search for next queue starting from (last + 1)
    int startIdx = (lastSelectedQueue + 1) % numQueues;
    
    // Search for next queue with available quantum and packets
    for (int i = 0; i < numQueues; ++i) {
        int idx = (startIdx + i) % numQueues;
        
        if (!state.queues[idx]->isEmpty()) {
            if (currentQuantum[idx] > 0) {
                currentQuantum[idx]--;
                lastSelectedQueue = idx;
                return state.queues[idx]->getId();
            }
        }
    }
    
    // If all quantums exhausted or empty, reset quantums and try again
    bool allEmpty = true;
    for (auto* q : state.queues) {
        if (!q->isEmpty()) {
            allEmpty = false;
            break;
        }
    }
    if (allEmpty) return -1;

    // Reset quantums
    for (int i = 0; i < numQueues; ++i) {
        currentQuantum[i] = static_cast<int>(state.queues[i]->getWeight() * baseQuantum);
    }
    
    // Try again from the same startIdx (next after the last selected)
    for (int i = 0; i < numQueues; ++i) {
        int idx = (startIdx + i) % numQueues;
        if (!state.queues[idx]->isEmpty()) {
             currentQuantum[idx]--;
             lastSelectedQueue = idx;
             return state.queues[idx]->getId();
        }
    }
    
    return -1;
}
