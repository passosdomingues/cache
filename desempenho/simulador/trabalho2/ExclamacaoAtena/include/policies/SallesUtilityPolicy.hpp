#ifndef SALLES_UTILITY_POLICY_HPP
#define SALLES_UTILITY_POLICY_HPP

#include "SchedulingPolicy.hpp"

/**
 * @brief Salles Utility-Based Policy (Adaptive)
 * Serves packet with highest marginal loss of utility.
 */
class SallesUtilityPolicy : public SchedulingPolicy {
private:
    double alpha_ = 1.0;
    double beta_ = 0.1;
    
public:
    int selectQueue(const SystemState& state) override;
    std::string getName() const override { return "SALLES_UTILITY"; }
    
    void setCoefficients(double alpha, double beta) {
        alpha_ = alpha;
        beta_ = beta;
    }
};

#endif // SALLES_UTILITY_POLICY_HPP
