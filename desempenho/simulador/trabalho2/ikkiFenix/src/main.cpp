/**
 * @file main.cpp
 * @brief CLI interface and Batch harness.
 */

#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <filesystem>
#include "simulator.hpp"

namespace fs = std::filesystem;

struct BatchConfig {
    std::vector<unsigned int> seeds;
    std::vector<double> rhos;
    std::vector<std::string> policies;
    double mu;
};

void runBatch(const BatchConfig& batch) {
    fs::create_directories("results/raw");
    fs::create_directories("results/aggregated");

    int totalRuns = (int)(batch.seeds.size() * batch.rhos.size() * batch.policies.size());
    int currentRun = 0;

    std::cout << "Starting Batch Simulation: " << totalRuns << " total runs." << std::endl;

    for (const auto& policy : batch.policies) {
        for (double rho : batch.rhos) {
            for (unsigned int seed : batch.seeds) {
                currentRun++;
                
                SimConfig conf;
                conf.seed = seed;
                conf.simulationTime = 86400.0;
                conf.samplingInterval = 10.0;
                conf.policyName = policy;
                conf.queueCapacity = 1000;
                conf.outputDir = "results/raw";
                
                // Setup 3 queues
                // Total system load is rho. For 3 queues, how do we split? 
                // Assuming symmetric for now, or rho is per-queue load?
                // Prompt: "Arrival rates derived as lambda = rho * mu"
                double lambda = rho * batch.mu;
                
                // 3 symmetric queues
                for(int i=0; i<3; i++) {
                    conf.serviceRates.push_back(batch.mu);
                    conf.arrivalRates.push_back(lambda); 
                }

                // Filename: policy_rho_seed.csv
                std::stringstream ss;
                ss << policy << "_rho" << std::fixed << std::setprecision(3) << rho 
                   << "_seed" << seed;
                conf.filePrefix = ss.str();

                std::cout << "[" << currentRun << "/" << totalRuns << "] Running: " << conf.filePrefix << std::endl;

                Simulator sim(conf);
                sim.run();
            }
        }
    }
    std::cout << "Batch Complete." << std::endl;
}

int main(int argc, char* argv[]) {
    if (argc > 1 && std::string(argv[1]) == "--batch") {
        BatchConfig batch;
        // Hardcoded batch config per requirements (can be moved to JSON/INI)
        batch.seeds = {42, 101, 123, 999, 2025};
        batch.rhos = {0.80, 0.90, 0.95, 0.999};
        batch.policies = {"LONGEST_QUEUE", "MAX_AVG_WAIT", "OLDEST_PACKET"};
        batch.mu = 1.0; // Default service rate

        runBatch(batch);
    } else {
        std::cout << "Usage: ./simulator --batch" << std::endl;
        std::cout << "Running default single test..." << std::endl;
        
        // Default single run
        SimConfig conf;
        conf.seed = 42;
        conf.simulationTime = 1000.0;
        conf.samplingInterval = 10.0;
        conf.policyName = "LONGEST_QUEUE";
        conf.queueCapacity = 100;
        conf.outputDir = "results";
        conf.filePrefix = "test_run";
        
        conf.serviceRates = {1.0, 1.0, 1.0};
        conf.arrivalRates = {0.8, 0.8, 0.8};
        
        Simulator sim(conf);
        sim.run();
    }
    return 0;
}