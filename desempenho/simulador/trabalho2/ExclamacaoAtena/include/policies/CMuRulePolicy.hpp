#ifndef C_MU_RULE_POLICY_HPP
#define C_MU_RULE_POLICY_HPP

#include "SchedulingPolicy.hpp"

/**
 * @brief cμ-Rule Policy (The Optimality Standard)
 * Minimizes total system cost: prioritize queue with highest (Cost * μ).
 */
class CMuRulePolicy : public SchedulingPolicy {
private:
    std::vector<double> costs_;
    
public:
    int selectQueue(const SystemState& state) override;
    std::string getName() const override { return "C_MU_RULE"; }
    
    void setCosts(const std::vector<double>& costs) {
        costs_ = costs;
    }
};

#endif // C_MU_RULE_POLICY_HPP
