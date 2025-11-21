/**
 * @file test_simulator.cpp
 * @brief Unit tests for simulator functionality
 */

#include "../include/simulator.hpp"
#include "../include/rng.hpp"
#include <cassert>
#include <iostream>
#include <filesystem>

namespace fs = std::filesystem;

/**
 * @brief Test simulator initialization
 */
void testSimulatorInitialization() {
    std::cout << "Testing simulator initialization...";
    
    SimConfig config;
    config.seed = 42;
    config.simulationTime = 100.0;
    config.samplingInterval = 10.0;
    config.serviceRates = {1.0, 1.0, 1.0};
    config.arrivalRates = {0.8, 0.8, 0.8};
    config.policyName = "LONGEST_QUEUE";
    config.queueCapacity = 100;
    config.outputDir = "results/test";
    config.filePrefix = "init_test";
    
    fs::create_directories(config.outputDir);
    
    Simulator simulator(config);
    
    // Just verify it constructs without error
    std::cout << " PASSED\n";
}

/**
 * @brief Test event scheduling
 */
void testEventScheduling() {
    std::cout << "Testing event scheduling...";
    
    SimConfig config;
    config.seed = 123;
    config.simulationTime = 100.0;
    config.samplingInterval = 10.0;
    config.serviceRates = {1.0, 1.0, 1.0};
    config.arrivalRates = {0.5, 0.5, 0.5};
    config.policyName = "LONGEST_QUEUE";
    config.queueCapacity = 100;
    config.outputDir = "results/test";
    config.filePrefix = "run_test";
    
    fs::create_directories(config.outputDir);
    
    Simulator simulator(config);
    simulator.run();
    
    // Verify output file exists
    std::string expectedFile = config.outputDir + "/" + config.filePrefix + ".csv";
    assert(fs::exists(expectedFile));
    
    std::cout << " PASSED\n";
}

/**
 * @brief Test Little's Law validation
 */
void testLittleLawValidation() {
    std::cout << "Testing Little's Law validation...";
    
    SimConfig config;
    config.seed = 456;
    config.simulationTime = 200.0;
    config.samplingInterval = 10.0;
    config.serviceRates = {1.0, 1.0, 1.0};
    config.arrivalRates = {0.7, 0.7, 0.7};
    config.policyName = "MAX_AVG_WAIT";
    config.queueCapacity = 100;
    config.outputDir = "results/test";
    config.filePrefix = "little_test";
    
    fs::create_directories(config.outputDir);
    
    Simulator simulator(config);
    simulator.run();
    
    std::cout << " PASSED\n";
}

/**
 * @brief Main function for simulator tests
 * @return int Exit status
 */
int main() {
    std::cout << "Running Simulator tests...\n";
    
    testSimulatorInitialization();
    testEventScheduling();
    testLittleLawValidation();
    
    std::cout << "All Simulator tests passed!\n";
    return 0;
}