#include "../include/config.hpp"
#include "../include/rng.hpp"
#include "../include/policies/PolicyOrchestrator.hpp"
#include <fstream>
#include <sstream>
#include <iostream>

SimulationConfig::SimulationConfig() 
    : targetOccupancy(0.8), randomSeed(42), simulationTime(86400.0), 
      samplingInterval(10.0), numQueues(3), discardPolicy("drop_tail"),
      maxQueueSize(1000) {
    serviceRates = {1.0, 1.0, 1.0};
    calculateArrivalRates();
    schedulingPolicy = PolicyOrchestrator::createPolicy("LONGEST_QUEUE");
    scenarioName = "default_scenario";
}

void SimulationConfig::calculateArrivalRates() {
    arrivalRates.clear();
    for (double rate : serviceRates) {
        arrivalRates.push_back(targetOccupancy * rate);
    }
}

void SimulationConfig::validate() const {
    if (targetOccupancy <= 0 || targetOccupancy >= 1.0) {
        throw std::invalid_argument("Target occupancy must be in (0, 1)");
    }
    
    if (serviceRates.size() != (size_t)numQueues) {
        throw std::invalid_argument("Service rates count must match number of queues");
    }
    
    for (double rate : serviceRates) {
        if (rate <= 0) {
            throw std::invalid_argument("Service rates must be positive");
        }
    }
    
    if (simulationTime <= 0) {
        throw std::invalid_argument("Simulation time must be positive");
    }
    
    if (samplingInterval <= 0) {
        throw std::invalid_argument("Sampling interval must be positive");
    }
}

SimulationConfig ConfigManager::loadFromFile(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Cannot open config file: " + filename);
    }
    
    SimulationConfig config;
    std::string line;
    
    while (std::getline(file, line)) {
        // Skip comments and empty lines
        if (line.empty() || line[0] == '#') continue;
        
        std::istringstream iss(line);
        std::string key, value;
        
        if (std::getline(iss, key, '=') && std::getline(iss, value)) {
            configMap[key] = value;
        }
    }
    
    // Parse values (simplified - you'd want more robust parsing)
    if (configMap.count("target_occupancy")) {
        config.targetOccupancy = std::stod(configMap["target_occupancy"]);
    }
    
    if (configMap.count("random_seed")) {
        config.randomSeed = std::stoul(configMap["random_seed"]);
    }
    
    if (configMap.count("simulation_time")) {
        config.simulationTime = std::stod(configMap["simulation_time"]);
    }
    
    if (configMap.count("policy")) {
        config.schedulingPolicy = PolicyOrchestrator::createPolicy(configMap["policy"]);
    }
    
    config.calculateArrivalRates();
    config.validate();
    
    return config;
}

SimulationConfig ConfigManager::loadFromCommandLine(int argc, char* argv[]) {
    SimulationConfig config = generateDefault();
    
    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];
        
        if (arg == "--batch") {
            // Batch mode - use default settings
        } else if (arg == "--config" && i + 1 < argc) {
            return loadFromFile(argv[++i]);
        } else if (arg == "--seed" && i + 1 < argc) {
            config.randomSeed = std::stoul(argv[++i]);
        } else if (arg == "--occupancy" && i + 1 < argc) {
            config.targetOccupancy = std::stod(argv[++i]);
        }
    }
    
    config.calculateArrivalRates();
    config.validate();
    
    return config;
}

void ConfigManager::saveToFile(const SimulationConfig& config, const std::string& filename) {
    std::ofstream file(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Cannot create config file: " + filename);
    }
    
    file << "# Simulation Configuration\n";
    file << "target_occupancy=" << config.targetOccupancy << "\n";
    file << "random_seed=" << config.randomSeed << "\n";
    file << "simulation_time=" << config.simulationTime << "\n";
    file << "sampling_interval=" << config.samplingInterval << "\n";
    file << "num_queues=" << config.numQueues << "\n";
    file << "discard_policy=" << config.discardPolicy << "\n";
    
    file.close();
}

SimulationConfig ConfigManager::generateDefault() {
    return SimulationConfig();
}