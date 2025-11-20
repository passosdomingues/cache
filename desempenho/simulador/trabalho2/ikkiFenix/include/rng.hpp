/**
 * @file rng.hpp
 * @brief Encapsulated Random Number Generator preserving exact C-style semantics.
 * * Maintains strict numerical reproducibility with the original C implementation
 * by using the same rand() scaling and log transformation techniques.
 */

#ifndef RNG_HPP
#define RNG_HPP

#include <cstdlib>
#include <cmath>

class RNG {
public:
    /**
     * @brief Initializes the random seed.
     * @param seed The integer seed (default 42).
     */
    static void setSeed(unsigned int seed);

    /**
     * @brief Generates a uniform random number in (0, 1].
     * * Replicates the logic: rand() / (RAND_MAX + 1), then inverted to (0,1].
     * @return double Uniform random value.
     */
    static double generateUniformRandom();

    /**
     * @brief Generates an exponentially distributed random variable.
     * * Uses Inverse Transform Sampling: -ln(u) / lambda.
     * @param rateParameter The rate (lambda).
     * @return double Exponential random value.
     */
    static double generateExponentialRandom(double rateParameter);
};

#endif // RNG_HPP