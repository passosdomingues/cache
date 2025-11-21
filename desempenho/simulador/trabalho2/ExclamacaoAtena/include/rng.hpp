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

/**
 * @brief Singleton Random Number Generator with fixed seed for deterministic simulations.
 * 
 * This class enforces determinism by using a hardcoded seed of 42.
 * The Singleton pattern ensures only one RNG instance exists throughout the simulation.
 */
class RNG {
private:
    static RNG* instance;
    
    /**
     * @brief Private constructor - initializes RNG with fixed seed 42.
     */
    RNG();
    
    // Delete copy constructor and assignment operator
    RNG(const RNG&) = delete;
    RNG& operator=(const RNG&) = delete;

public:
    /**
     * @brief Get the singleton instance of RNG.
     * @return RNG& Reference to the singleton instance.
     */
    static RNG& getInstance();

    /**
     * @brief Generates a uniform random number in (0, 1].
     * * Replicates the logic: rand() / (RAND_MAX + 1), then inverted to (0,1].
     * @return double Uniform random value.
     */
    double generateUniformRandom();

    /**
     * @brief Generates an exponentially distributed random variable.
     * * Uses Inverse Transform Sampling: -ln(u) / lambda.
     * @param rateParameter The rate (lambda).
     * @return double Exponential random value.
     */
    double generateExponentialRandom(double rateParameter);
};

#endif // RNG_HPP