#include "../../include/policies/SallesUtilityPolicy.hpp"
#include "../../include/components.hpp"
#include <cmath>

int SallesUtilityPolicy::selectQueue(const SystemState& state) {
    int selectedId = -1;
    double maxMarginalLoss = -1.0;

    for (Queue* q : state.queues) {
        if (q->isEmpty()) continue;

        // Calculate marginal loss of utility U'(t)
        // Heuristic: U(t) depends on utility type
        // Type 0 (Best Effort): U(t) = -t (Linear decay) -> U'(t) = -1 (Constant loss)
        // Type 1 (Voice): U(t) = Step function at delay constraint -> High loss near deadline
        // Type 2 (Video): U(t) = Sigmoid
        
        double wait = q->getHeadWaitingTime(state.currentTime);
        double loss = 0.0;
        
        switch (q->getUtilityType()) {
            case 0: // Best Effort - Linear penalty
                loss = 1.0; 
                break;
            case 1: // Voice - Exponential penalty (simulating deadline)
                loss = std::exp(0.1 * wait); 
                break;
            case 2: // Video - Quadratic penalty
                loss = wait * wait;
                break;
            default:
                loss = 1.0;
        }
        
        if (loss > maxMarginalLoss || (loss == maxMarginalLoss && (selectedId == -1 || q->getId() < selectedId))) {
            maxMarginalLoss = loss;
            selectedId = q->getId();
        }
    }
    return selectedId;
}
