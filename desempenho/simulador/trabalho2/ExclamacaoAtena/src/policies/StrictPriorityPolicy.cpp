#include "../../include/policies/StrictPriorityPolicy.hpp"
#include "../../include/components.hpp"

int StrictPriorityPolicy::selectQueue(const SystemState& state) {
    // Assumes queues are sorted by priority (0 is highest)
    for (Queue* q : state.queues) {
        if (!q->isEmpty()) {
            return q->getId();
        }
    }
    return -1;
}
