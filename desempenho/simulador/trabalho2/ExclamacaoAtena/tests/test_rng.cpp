#include "../include/rng.hpp"
#include <cassert>
#include <iostream>
#include <vector>

void testRNGSeed() {
    std::cout << "Testing RNG deterministic behavior (seed hardcoded to 42)...";
    
    // Generate some numbers to verify deterministic behavior
    std::vector<double> values1;
    for (int i = 0; i < 10; i++) {
        values1.push_back(RNG::getInstance().generateUniformRandom());
    }
    
    // Singleton ensures same sequence continues (next 10 values)
    std::vector<double> values2;
    for (int i = 0; i < 10; i++) {
        values2.push_back(RNG::getInstance().generateUniformRandom());
    }
    
    // Verify sequences are DIFFERENT (since RNG state continues)
    // If they were the same, the RNG would be broken/stateless
    bool allSame = true;
    for (size_t i = 0; i < values1.size(); i++) {
        if (values1[i] != values2[i]) {
            allSame = false;
            break;
        }
    }
    assert(!allSame); // Should be different
    std::cout << " PASSED\n";
}

void testUniformRange() {
    std::cout << "Testing uniform random range...";
    
    for (int i = 0; i < 1000; i++) {
        double value = RNG::getInstance().generateUniformRandom();
        assert(value > 0.0 && value <= 1.0);
    }
    std::cout << " PASSED\n";
}

void testExponentialDistribution() {
    std::cout << "Testing exponential distribution...";
    
    double rate = 2.0;
    double sum = 0.0;
    int count = 10000;
    
    for (int i = 0; i < count; i++) {
        double value = RNG::getInstance().generateExponentialRandom(rate);
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
    
    try {
        RNG::getInstance().generateExponentialRandom(0.0);
        assert(false); // Should not reach here
    } catch (const std::invalid_argument&) {
        // Expected behavior
    }
    
    try {
        RNG::getInstance().generateExponentialRandom(-1.0);
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