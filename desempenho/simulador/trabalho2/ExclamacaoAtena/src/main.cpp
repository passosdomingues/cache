/**
 * @file main.cpp
 * @brief CLI interface and Batch harness with config file support
 */

#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <filesystem>
#include <fstream>
#include <algorithm>
#include <cctype>
#include "../include/simulator.hpp"

namespace fs = std::filesystem;

/**
 * @brief Batch configuration structure
 */
struct BatchConfig {
    std::vector<unsigned int> seeds;    ///< Random seeds for simulation runs
    std::vector<double> rhos;           ///< Utilization factors to test
    std::vector<std::string> policies;  ///< Scheduling policies to evaluate
    double mu;                          ///< Service rate
    double simulationTime;              ///< Simulation time per run
    double samplingInterval;            ///< Sampling interval
    std::vector<double> cMuCosts;       ///< Cost parameters for c-mu rule
    std::vector<double> sallesCoeffs;   ///< Coefficients for Salles utility
    std::string matrixPath;             ///< Path to policy matrix file
};

/**
 * @brief Trim whitespace from string
 * @param str Input string
 * @return std::string Trimmed string
 */
std::string trim(const std::string& str) {
    size_t start = str.find_first_not_of(" \t\n\r");
    if (start == std::string::npos) return "";
    size_t end = str.find_last_not_of(" \t\n\r");
    return str.substr(start, end - start + 1);
}

/**
 * @brief Parse comma-separated double values
 * @param str Input string
 * @return std::vector<double> Parsed double values
 */
std::vector<double> parseDoubleCSV(const std::string& str) {
    std::vector<double> result;
    std::stringstream ss(str);
    std::string item;
    
    while (std::getline(ss, item, ',')) {
        item = trim(item);
        if (!item.empty()) {
            try {
                result.push_back(std::stod(item));
            } catch (const std::exception& e) {
                std::cerr << "Warning: Could not parse double value: " << item << std::endl;
            }
        }
    }
    return result;
}

/**
 * @brief Parse comma-separated string values
 * @param str Input string
 * @return std::vector<std::string> Parsed string values
 */
std::vector<std::string> parseStringCSV(const std::string& str) {
    std::vector<std::string> result;
    std::stringstream ss(str);
    std::string item;
    
    while (std::getline(ss, item, ',')) {
        item = trim(item);
        if (!item.empty()) {
            result.push_back(item);
        }
    }
    return result;
}

/**
 * @brief Read configuration from file
 * @param configPath Path to configuration file
 * @return BatchConfig Batch configuration parameters
 */
BatchConfig readConfig(const std::string& configPath = "config/simulator.cfg") {
    BatchConfig config;
    
    // Default values as fallback
    config.seeds = {42};
    config.rhos = {0.800, 0.900, 0.950, 0.999};
    config.policies = {"LONGEST_QUEUE", "SHORTEST_QUEUE", "ROUND_ROBIN", "STRICT_PRIORITY",
                      "MAX_AVG_WAIT", "OLDEST_PACKET", "AGING",
                      "SALLES_UTILITY", "C_MU_RULE", "WEIGHTED_ROUND_ROBIN", "WHITTLE_INDEX"};
    config.mu = 1.0;
    config.simulationTime = 86400.0;
    config.samplingInterval = 10.0;
    config.cMuCosts = {1.0, 5.0, 10.0};
    config.sallesCoeffs = {0.5, 2.0};
    config.matrixPath = "analysis/policy_matrix.csv";
    
    std::ifstream file(configPath);
    if (!file.is_open()) {
        std::cout << "Config file not found: " << configPath << " - using defaults" << std::endl;
        return config;
    }
    
    std::string line;
    std::string currentSection;
    
    while (std::getline(file, line)) {
        line = trim(line);
        
        // Skip empty lines and comments
        if (line.empty() || line[0] == '#' || line[0] == ';') {
            continue;
        }
        
        // Section header
        if (line[0] == '[' && line.back() == ']') {
            currentSection = line.substr(1, line.length() - 2);
            continue;
        }
        
        // Key-value pair
        size_t delimiterPos = line.find('=');
        if (delimiterPos != std::string::npos) {
            std::string key = trim(line.substr(0, delimiterPos));
            std::string value = trim(line.substr(delimiterPos + 1));
            
            if (currentSection == "Global") {
                if (key == "simulation_time") {
                    config.simulationTime = std::stod(value);
                } else if (key == "sampling_interval") {
                    config.samplingInterval = std::stod(value);
                } else if (key == "random_seed") {
                    // Parse single seed or comma-separated seeds
                    auto seedValues = parseDoubleCSV(value);
                    config.seeds.clear();
                    for (double seed : seedValues) {
                        config.seeds.push_back(static_cast<unsigned int>(seed));
                    }
                }
            } else if (currentSection == "Traffic") {
                if (key == "rhos") {
                    config.rhos = parseDoubleCSV(value);
                } else if (key == "service_rate_mu") {
                    config.mu = std::stod(value);
                }
            } else if (currentSection == "Policies") {
                if (key == "c_mu_costs") {
                    config.cMuCosts = parseDoubleCSV(value);
                } else if (key == "salles_coeffs") {
                    config.sallesCoeffs = parseDoubleCSV(value);
                }
            } else if (currentSection == "Orchestrator") {
                if (key == "matrix_path") {
                    config.matrixPath = value;
                }
            }
        }
    }
    
    std::cout << "Loaded configuration from: " << configPath << std::endl;
    return config;
}

/**
 * @brief Run batch simulation with given configuration
 * @param batch Batch configuration parameters
 */
void runBatch(const BatchConfig& batch) {
    fs::create_directories("results/raw");

    int totalRuns = (int)(batch.seeds.size() * batch.rhos.size() * batch.policies.size());
    int currentRun = 0;

    std::cout << "Starting Batch Simulation: " << totalRuns << " total runs." << std::endl;
    std::cout << "Simulation Time: " << batch.simulationTime << "s" << std::endl;
    std::cout << "Sampling Interval: " << batch.samplingInterval << "s" << std::endl;
    std::cout << "Service Rate μ: " << batch.mu << std::endl;

    for (const auto& policy : batch.policies) {
        for (double rho : batch.rhos) {
            for (unsigned int seed : batch.seeds) {
                currentRun++;
                
                SimConfig conf;
                conf.seed = seed;
                conf.simulationTime = batch.simulationTime;
                conf.samplingInterval = batch.samplingInterval;
                conf.policyName = policy;
                conf.queueCapacity = 1000;
                conf.outputDir = "results/raw";
                
                // Pass policy-specific parameters from config
                conf.cMuCosts = batch.cMuCosts;
                conf.sallesCoeffs = batch.sallesCoeffs;
                conf.matrixPath = batch.matrixPath;
                
                // Setup 3 symmetric queues
                double lambda = rho * batch.mu;
                for(int i = 0; i < 3; i++) {
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

/**
 * @brief Main function
 * @param argc Argument count
 * @param argv Argument vector
 * @return int Exit status
 */
int main(int argc, char* argv[]) {
    if (argc > 1 && std::string(argv[1]) == "--batch") {
        BatchConfig batch = readConfig();
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