#include "../../include/policies/WhittleIndexPolicy.hpp"
#include "../../include/components.hpp"
#include <limits>

int WhittleIndexPolicy::selectQueue(const SystemState& state) {
    int selectedId = -1;
    double maxIndex = -std::numeric_limits<double>::infinity();

    for (Queue* q : state.queues) {
        if (q->isEmpty()) continue;

        // Whittle Index Heuristic for Restless Bandits
        // A simplified index: W = (QueueLength * mu) / (1 + QueueLength)
        // This represents the "rate of clearing congestion"
        // For M/M/1, index ~ mu * (1 - 1/(L+1))
        
        double L = (double)q->getLength();
        double mu = q->getServiceRate();
        
        double index = (L * mu) / (1.0 + L);
        
        if (index > maxIndex || (index == maxIndex && (selectedId == -1 || q->getId() < selectedId))) {
            maxIndex = index;
            selectedId = q->getId();
        }
    }
    return selectedId;
}
