/**
 * @file rng.c
 * @brief Implementation of the random number generation functions.
 *
 * Project: M/M/1 Multi-Queue Simulator
 * Author: Rafael Passos Domingues
 * Last Update: 2025 Sep 25 14h36
 *
 * Purpose:
 * This file provides the implementation for a Lehmer random number generator
 * (`aleatorio`) and an exponential distribution variate generator (`exponencial`).
 * The RNG properties are chosen to be simple, efficient, and reproducible, which
 * is critical for simulation work. The semantics are preserved to match
 * common academic simulators.
 */
#include "../include/rng.h"
#include <math.h>

// Lehmer LCG parameters
#define A 16807
#define M 2147483647
#define Q (M / A)
#define R (M % A)

static long seed = 1; // Default seed

/**
 * @brief Seeds the random number generator.
 * @param s The seed value. Must be non-zero.
 */
void seedRNG(long s) {
    if (s == 0) {
        seed = 1; // Avoid seed 0
    } else {
        seed = s;
    }
}

/**
 * @brief Generates a pseudo-random double between (0, 1).
 *
 * Implements a Park-Miller LCG with Schrage's algorithm to prevent overflow.
 *
 * @return A double value in the exclusive range (0.0, 1.0).
 */
double aleatorio() {
    long hi = seed / Q;
    long lo = seed % Q;
    long test = A * lo - R * hi;

    if (test > 0) {
        seed = test;
    } else {
        seed = test + M;
    }
    return (double)seed / M;
}

/**
 * @brief Generates a random variate from an exponential distribution.
 *
 * Uses the inverse transform method on a uniform random variate from `aleatorio()`.
 *
 * @param rate The rate parameter (lambda) of the exponential distribution.
 * @return A non-negative double representing a sample from the distribution.
 */
double exponencial(double rate) {
    // We call aleatorio() to get a U~(0,1) random number.
    // The inverse of the CDF of an exponential distribution is -ln(1-U)/lambda.
    // Since (1-U) is also uniform on (0,1), we can simplify to -ln(U)/lambda.
    return -log(aleatorio()) / rate;
}
