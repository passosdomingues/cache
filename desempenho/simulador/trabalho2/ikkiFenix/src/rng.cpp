/**
 * @file rng.cpp
 * @brief Implementation of RNG logic.
 */

#include "rng.hpp"
#include <stdexcept>
#include <cmath>
#include <cstdlib>

void RNG::setSeed(unsigned int seed) {
    std::srand(seed);
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