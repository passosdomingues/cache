#ifndef RNG_H
#define RNG_H

/**
 * @file rng.h
 * @brief Header for the random number generation functions.
 *
 * Project: M/M/1 Multi-Queue Simulator
 * Author: Rafael Passos Domingues
 * Last Update: 2025 Sep 25 14h36
 *
 * Purpose:
 * This file provides the function prototypes for the random number
 * generator. It includes a uniform random number generator (`aleatorio`)
 * and an exponential variate generator (`exponencial`) which are core
 * to simulating Poisson arrivals and exponential service times.
 */

/**
 * @brief Seeds the random number generator.
 * @param s The seed value.
 */
void seedRNG(long s);

/**
 * @brief Generates a pseudo-random double between (0, 1).
 *
 * This function uses a Lehmer linear congruential generator (LCG)
 * with parameters used in `glibc`. This ensures a long period and good
 * statistical properties for simulation.
 *
 * @return A double value in the exclusive range (0.0, 1.0).
 */
double aleatorio();

/**
 * @brief Generates a random variate from an exponential distribution.
 *
 * Uses the inverse transform method on a uniform random variate.
 *
 * @param rate The rate parameter (lambda) of the exponential distribution.
 * @return A non-negative double representing a sample from the distribution.
 */
double exponencial(double rate);

#endif // RNG_H
