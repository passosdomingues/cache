/**
 * @file rng.cpp
 * @brief Implementation of Singleton RNG with fixed seed 42 for deterministic simulations.
 */

#include "rng.hpp"
#include <stdexcept>
#include <cmath>
#include <cstdlib>

// Initialize static instance pointer
RNG* RNG::instance = nullptr;

/**
 * @brief Private constructor - automatically sets seed to 42 for determinism.
 */
RNG::RNG() {
    std::srand(42);  // HARDCODED SEED 42 - DO NOT CHANGE
}

/**
 * @brief Get singleton instance (lazy initialization).
 */
RNG& RNG::getInstance() {
    if (instance == nullptr) {
        instance = new RNG();
    }
    return *instance;
}

double RNG::generateUniformRandom() {
    // Exact mapping from original C code
    double u = std::rand() / ((double) RAND_MAX + 1.0);
    // Ensure (0,1] range to avoid log(0)
    return 1.0 - u;
}

double RNG::generateExponentialRandom(double rateParameter) {
    if (rateParameter <= 0.0) {
        throw std::invalid_argument("Rate parameter must be positive");
    }
    double u = generateUniformRandom();
    return -std::log(u) / rateParameter;
}