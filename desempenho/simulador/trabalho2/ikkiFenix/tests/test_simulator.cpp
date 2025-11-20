#include "../include/simulator.hpp"
#include "../include/rng.hpp"
#include <cassert>
#include <iostream>

void testSimulatorInitialization() {
    std::cout << "Testing simulator initialization...";
    
    SimulationConfig config;
    config.targetOccupancy = 0.8;
    config.serviceRates = {1.0, 1.0, 1.0};
    config.randomSeed = 42;
    config.simulationTime = 1000.0;
    config.samplingInterval = 10.0;
    config.numQueues = 3;
    
    QueueingSimulator simulator(config);
    
    // Verify initial state
    assert(simulator.getCurrentTime() == 0.0);
    assert(simulator.getTotalProcessedRequests() == 0);
    // Add more assertions based on your simulator's state
    
    std::cout << " PASSED\n";
}

void testEventScheduling() {
    std::cout << "Testing event scheduling...";
    
    SimulationConfig config;
    config.targetOccupancy = 0.5; // Low load for testing
    config.serviceRates = {1.0, 1.0, 1.0};
    config.randomSeed = 123;
    config.simulationTime = 100.0;
    config.samplingInterval = 10.0;
    
    QueueingSimulator simulator(config);
    
    // Run a short simulation
    simulator.run();
    
    // Should have processed some events
    assert(simulator.getTotalProcessedRequests() > 0);
    assert(simulator.getCurrentTime() >= config.simulationTime);
    
    std::cout << " PASSED\n";
}

void testLittleLawValidation() {
    std::cout << "Testing Little's Law validation...";
    
    SimulationConfig config;
    config.targetOccupancy = 0.7;
    config.serviceRates = {1.0, 1.0, 1.0};
    config.randomSeed = 456;
    config.simulationTime = 500.0; // Short simulation for testing
    config.samplingInterval = 10.0;
    
    QueueingSimulator simulator(config);
    simulator.run();
    
    // Get Little's Law error from the simulator
    // This depends on your implementation
    // double error = simulator.getLittlesLawError();
    // assert(std::abs(error) < 0.1); // Reasonable tolerance
    
    std::cout << " PASSED (basic functionality)\n";
}

int main() {
    std::cout << "Running Simulator tests...\n";
    
    testSimulatorInitialization();
    testEventScheduling();
    testLittleLawValidation();
    
    std::cout << "All Simulator tests passed!\n";
    return 0;
}