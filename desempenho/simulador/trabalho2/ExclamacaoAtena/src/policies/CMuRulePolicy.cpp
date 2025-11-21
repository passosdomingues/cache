#include "../../include/policies/CMuRulePolicy.hpp"
#include "../../include/components.hpp"

int CMuRulePolicy::selectQueue(const SystemState& state) {
    int selectedId = -1;
    double maxIndex = -1.0;

    for (Queue* q : state.queues) {
        if (q->isEmpty()) continue;

        // Index = Cost * mu
        // Cost is represented by queue weight
        double index = q->getWeight() * q->getServiceRate();
        
        if (index > maxIndex || (index == maxIndex && (selectedId == -1 || q->getId() < selectedId))) {
            maxIndex = index;
            selectedId = q->getId();
        }
    }
    return selectedId;
}
