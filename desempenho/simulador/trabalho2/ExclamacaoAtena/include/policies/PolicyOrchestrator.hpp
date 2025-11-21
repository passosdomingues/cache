#ifndef POLICY_ORCHESTRATOR_HPP
#define POLICY_ORCHESTRATOR_HPP

#include "SchedulingPolicy.hpp"
#include <memory>
#include <string>
#include <vector>
#include <queue>
#include <map>

/**
 * @brief Orchestrator for managing and selecting policies.
 * 
 * Implements a Min-Heap (Priority Queue) to rank policies or queues 
 * based on specific criteria, serving as a central decision reference.
 */
class PolicyOrchestrator : public SchedulingPolicy {
private:
    std::map<std::string, std::unique_ptr<SchedulingPolicy>> policies;
    std::unique_ptr<SchedulingPolicy> activePolicy;

public:
    PolicyOrchestrator();
    
    // Policy Management
    void registerPolicy(std::unique_ptr<SchedulingPolicy> policy);
    void setActivePolicy(const std::string& name);
    SchedulingPolicy* getActivePolicy() const;
    
    // Factory Method
    static std::unique_ptr<SchedulingPolicy> createPolicy(const std::string& name);
    
    // Decision Making
    int selectQueue(const SystemState& state) override;
    std::string getName() const override { return "POLICY_ORCHESTRATOR"; }
};

#endif // POLICY_ORCHESTRATOR_HPP
