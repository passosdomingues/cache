#include "../include/measurement_window.hpp"
#include <cassert>
#include <iostream>
#include <cmath>

void testInitialization() {
    std::cout << "Testing measurement window initialization...";
    CircularMeasurementWindow window;
    window.initialize(100);
    
    assert(window.getTotalPacketsInWindow() == 0);
    assert(window.getSumArrivalTimestamps() == 0.0);
    assert(window.getSumWaitingTimes() == 0.0);
    std::cout << " PASSED\n";
}

void testAddPackets() {
    std::cout << "Testing packet addition...";
    CircularMeasurementWindow window;
    window.initialize(3); // Small window for testing
    
    window.addPacket(1.0, 2.0, 1.0);
    assert(window.getTotalPacketsInWindow() == 1);
    assert(window.getSumArrivalTimestamps() == 1.0);
    assert(window.getSumWaitingTimes() == 1.0);
    
    window.addPacket(2.0, 4.0, 2.0);
    assert(window.getTotalPacketsInWindow() == 2);
    assert(window.getSumArrivalTimestamps() == 3.0);
    assert(window.getSumWaitingTimes() == 3.0);
    
    window.addPacket(3.0, 6.0, 3.0);
    assert(window.getTotalPacketsInWindow() == 3);
    assert(window.getSumArrivalTimestamps() == 6.0);
    assert(window.getSumWaitingTimes() == 6.0);
    std::cout << " PASSED\n";
}

void testCircularBehavior() {
    std::cout << "Testing circular behavior...";
    CircularMeasurementWindow window;
    window.initialize(3);
    
    // Fill the window
    window.addPacket(1.0, 2.0, 1.0);
    window.addPacket(2.0, 4.0, 2.0);
    window.addPacket(3.0, 6.0, 3.0);
    
    // Add one more - should remove the oldest (1.0)
    window.addPacket(4.0, 8.0, 4.0);
    
    assert(window.getTotalPacketsInWindow() == 3);
    assert(window.getSumArrivalTimestamps() == 9.0); // 2.0 + 3.0 + 4.0
    assert(window.getSumWaitingTimes() == 9.0); // 2.0 + 3.0 + 4.0
    std::cout << " PASSED\n";
}

void testAverageCalculations() {
    std::cout << "Testing average calculations...";
    CircularMeasurementWindow window;
    window.initialize(5);
    
    window.addPacket(1.0, 3.0, 2.0);
    window.addPacket(2.0, 5.0, 3.0);
    window.addPacket(3.0, 6.0, 3.0);
    
    double avgWaiting = window.computeWindowAverageWaitingTime();
    double avgArrival = window.computeWindowAverageArrivalTime();
    
    assert(std::abs(avgWaiting - (2.0 + 3.0 + 3.0) / 3) < 1e-10);
    assert(std::abs(avgArrival - (1.0 + 2.0 + 3.0) / 3) < 1e-10);
    std::cout << " PASSED\n";
}

void testEmptyWindow() {
    std::cout << "Testing empty window behavior...";
    CircularMeasurementWindow window;
    window.initialize(10);
    
    assert(window.computeWindowAverageWaitingTime() == 0.0);
    assert(window.computeWindowAverageArrivalTime() == 0.0);
    std::cout << " PASSED\n";
}

void testClear() {
    std::cout << "Testing window clear...";
    CircularMeasurementWindow window;
    window.initialize(5);
    
    window.addPacket(1.0, 2.0, 1.0);
    window.addPacket(2.0, 4.0, 2.0);
    
    window.clear();
    
    assert(window.getTotalPacketsInWindow() == 0);
    assert(window.getSumArrivalTimestamps() == 0.0);
    assert(window.getSumWaitingTimes() == 0.0);
    std::cout << " PASSED\n";
}

int main() {
    std::cout << "Running Measurement Window tests...\n";
    
    testInitialization();
    testAddPackets();
    testCircularBehavior();
    testAverageCalculations();
    testEmptyWindow();
    testClear();
    
    std::cout << "All Measurement Window tests passed!\n";
    return 0;
}