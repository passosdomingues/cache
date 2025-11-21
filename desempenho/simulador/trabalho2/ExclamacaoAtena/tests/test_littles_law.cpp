/**
 * @file test_littles_law.cpp
 * @brief Unit tests for Little's Law tracker implementation
 */

#include "../include/littles_law.hpp"
#include <cassert>
#include <iostream>
#include <cmath>

/**
 * @brief Test Little's Law tracker initialization
 */
void testInitialization() {
    std::cout << "Testing Little's Law tracker initialization...";
    LittlesLawTracker tracker;
    tracker.initialize();
    
    assert(tracker.getTotalArrivals() == 0);
    assert(tracker.getTotalWaitingTime() == 0.0);
    assert(tracker.getCurrentRequestCount() == 0);
    assert(tracker.getAccumulatedArea() == 0.0);
    std::cout << " PASSED\n";
}

/**
 * @brief Test arrival and departure tracking
 */
void testArrivalDeparture() {
    std::cout << "Testing arrival and departure tracking...";
    LittlesLawTracker tracker;
    tracker.initialize();
    
    tracker.registerArrival(1.0);
    assert(tracker.getCurrentRequestCount() == 1);
    assert(tracker.getTotalArrivals() == 1);
    
    tracker.registerArrival(2.0);
    assert(tracker.getCurrentRequestCount() == 2);
    assert(tracker.getTotalArrivals() == 2);
    
    tracker.registerDeparture(3.0, 2.0);
    assert(tracker.getCurrentRequestCount() == 1);
    assert(tracker.getTotalWaitingTime() == 2.0);
    
    tracker.registerDeparture(4.0, 1.5);
    assert(tracker.getCurrentRequestCount() == 0);
    assert(tracker.getTotalWaitingTime() == 3.5);
    std::cout << " PASSED\n";
}

/**
 * @brief Test area under curve calculation
 */
void testAreaCalculation() {
    std::cout << "Testing area under curve calculation...";
    LittlesLawTracker tracker;
    tracker.initialize();
    
    // Start with one request
    tracker.registerArrival(0.0);
    
    // Update area at time 2.0 (1 request for 2 time units)
    tracker.updateArea(2.0);
    assert(std::abs(tracker.getAccumulatedArea() - 2.0) < 1e-10);
    
    // Add another request
    tracker.registerArrival(2.0);
    
    // Update area at time 4.0 (2 requests for 2 time units)
    tracker.updateArea(4.0);
    assert(std::abs(tracker.getAccumulatedArea() - 6.0) < 1e-10); // 2 + 2*2 = 6
    
    // Remove one request
    tracker.registerDeparture(4.0, 2.0);
    
    // Update area at time 5.0 (1 request for 1 time unit)
    tracker.updateArea(5.0);
    assert(std::abs(tracker.getAccumulatedArea() - 7.0) < 1e-10); // 6 + 1 = 7
    std::cout << " PASSED\n";
}

/**
 * @brief Test E[N] calculation
 */
void testENCalculation() {
    std::cout << "Testing E[N] calculation...";
    LittlesLawTracker tracker;
    tracker.initialize();
    
    tracker.registerArrival(0.0);
    tracker.updateArea(2.0); // 1 request for 2 time units
    
    double en = tracker.computeEN(2.0);
    assert(std::abs(en - 1.0) < 1e-10); // Area = 2, Time = 2 -> E[N] = 1
    
    tracker.registerArrival(2.0);
    tracker.updateArea(4.0); // Now 2 requests for 2 time units
    
    en = tracker.computeEN(4.0);
    assert(std::abs(en - 1.5) < 1e-10); // Area = 6, Time = 4 -> E[N] = 1.5
    std::cout << " PASSED\n";
}

/**
 * @brief Test E[W] calculation
 */
void testEWCalculation() {
    std::cout << "Testing E[W] calculation...";
    LittlesLawTracker tracker;
    tracker.initialize();
    
    tracker.registerArrival(0.0);
    tracker.registerDeparture(2.0, 2.0);
    
    tracker.registerArrival(1.0);
    tracker.registerDeparture(3.0, 2.0);
    
    tracker.registerArrival(2.0);
    tracker.registerDeparture(5.0, 3.0);
    
    double ew = tracker.computeEW();
    assert(std::abs(ew - (2.0 + 2.0 + 3.0) / 3) < 1e-10);
    std::cout << " PASSED\n";
}

/**
 * @brief Test behavior with no arrivals
 */
void testNoArrivals() {
    std::cout << "Testing behavior with no arrivals...";
    LittlesLawTracker tracker;
    tracker.initialize();
    
    assert(tracker.computeEN(10.0) == 0.0);
    assert(tracker.computeEW() == 0.0);
    std::cout << " PASSED\n";
}

/**
 * @brief Main function for Little's Law tests
 * @return int Exit status
 */
int main() {
    std::cout << "Running Little's Law tests...\n";
    
    testInitialization();
    testArrivalDeparture();
    testAreaCalculation();
    testENCalculation();
    testEWCalculation();
    testNoArrivals();
    
    std::cout << "All Little's Law tests passed!\n";
    return 0;
}