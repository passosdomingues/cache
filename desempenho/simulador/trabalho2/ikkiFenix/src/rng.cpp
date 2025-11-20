#include "../include/rng.hpp"
#include <stdexcept>

bool RNG::seeded = false;

void RNG::setSeed(unsigned long seed) {
    if (!seeded) {
        srand(seed);
        seeded = true;
    }
}

double RNG::generateUniformRandom() {
    if (!seeded) {
        throw std::runtime_error("RNG not seeded. Call setSeed() first.");
    }
    
    double uniformRandom = rand() / ((double) RAND_MAX + 1);
    // Ensure we don't return 0.0 to avoid log(0) in exponential generation
    uniformRandom = 1.0 - uniformRandom;
    return uniformRandom;
}

double RNG::generateExponentialRandom(double rateParameter) {
    if (rateParameter <= 0) {
        throw std::invalid_argument("Rate parameter must be positive");
    }
    
    double uniform = generateUniformRandom();
    return (-1.0 / rateParameter) * log(uniform);
}