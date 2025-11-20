#include "../include/rng.hpp"
#include <cassert>
#include <iostream>
#include <vector>

void testRNGSeed() {
    std::cout << "Testing RNG seed initialization...";
    RNG::setSeed(42);
    
    // Generate some numbers to verify deterministic behavior
    std::vector<double> values1;
    for (int i = 0; i < 10; i++) {
        values1.push_back(RNG::generateUniformRandom());
    }
    
    // Reset seed and generate same sequence
    RNG::setSeed(42);
    std::vector<double> values2;
    for (int i = 0; i < 10; i++) {
        values2.push_back(RNG::generateUniformRandom());
    }
    
    // Verify sequences are identical
    for (size_t i = 0; i < values1.size(); i++) {
        assert(values1[i] == values2[i]);
    }
    std::cout << " PASSED\n";
}

void testUniformRange() {
    std::cout << "Testing uniform random range...";
    RNG::setSeed(123);
    
    for (int i = 0; i < 1000; i++) {
        double value = RNG::generateUniformRandom();
        assert(value > 0.0 && value <= 1.0);
    }
    std::cout << " PASSED\n";
}

void testExponentialDistribution() {
    std::cout << "Testing exponential distribution...";
    RNG::setSeed(456);
    
    double rate = 2.0;
    double sum = 0.0;
    int count = 10000;
    
    for (int i = 0; i < count; i++) {
        double value = RNG::generateExponentialRandom(rate);
        assert(value > 0.0);
        sum += value;
    }
    
    double mean = sum / count;
    double expectedMean = 1.0 / rate;
    double tolerance = 0.1;
    
    assert(std::abs(mean - expectedMean) < tolerance);
    std::cout << " PASSED\n";
}

void testExponentialInvalidRate() {
    std::cout << "Testing exponential with invalid rate...";
    RNG::setSeed(789);
    
    try {
        RNG::generateExponentialRandom(0.0);
        assert(false); // Should not reach here
    } catch (const std::invalid_argument&) {
        // Expected behavior
    }
    
    try {
        RNG::generateExponentialRandom(-1.0);
        assert(false); // Should not reach here
    } catch (const std::invalid_argument&) {
        // Expected behavior
    }
    std::cout << " PASSED\n";
}

int main() {
    std::cout << "Running RNG tests...\n";
    
    testRNGSeed();
    testUniformRange();
    testExponentialDistribution();
    testExponentialInvalidRate();
    
    std::cout << "All RNG tests passed!\n";
    return 0;
}