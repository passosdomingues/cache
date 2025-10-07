/**
 * @file main.c
 * @brief Main entry point for the M/M/1 Multi-Queue Simulator.
 *
 * Project: M/M/1 Multi-Queue Simulator
 * Author: Rafael Passos Domingues
 * Last Update: 2025 Sep 25 14h36
 *
 * Purpose:
 * This file contains the main function that parses command-line arguments
 * and initiates the simulation process. It serves as the primary interface
 * for running single simulations or batches. It extracts parameters such as
 * service rates, policy ID, occupancy, and seed, then calls the core
 * simulation engine.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../include/simulator.h"

/**
 * @brief Main entry point of the simulator.
 *
 * Parses command-line arguments and launches the simulation.
 *
 * @param argc Number of command-line arguments.
 * @param argv Array of command-line argument strings.
 * @return 0 on success, 1 on error.
 */
int main(int argc, char* argv[]) {
    if (argc != 7) {
        fprintf(stderr, "Usage: %s <mu1> <mu2> <mu3> <policy_id> <rho> <seed>\n", argv[0]);
        fprintf(stderr, "  mu1, mu2, mu3: Service rates for queues 1, 2, 3 (e.g., 1.0)\n");
        fprintf(stderr, "  policy_id: 1 (Longest), 2 (Highest Avg Wait), 3 (Oldest Cust)\n");
        fprintf(stderr, "  rho: Target system occupancy (e.g., 0.80)\n");
        fprintf(stderr, "  seed: Integer seed for RNG (e.g., 12345)\n");
        return 1;
    }

    // Parse command line arguments
    double mu1 = atof(argv[1]);
    double mu2 = atof(argv[2]);
    double mu3 = atof(argv[3]);
    int policyId = atoi(argv[4]);
    double rho = atof(argv[5]);
    long seed = atol(argv[6]);

    // Validate inputs
    if (mu1 <= 0 || mu2 <= 0 || mu3 <= 0) {
        fprintf(stderr, "Error: Service rates (mu) must be positive.\n");
        return 1;
    }
    if (policyId < 1 || policyId > 3) {
        fprintf(stderr, "Error: Invalid policy_id. Must be 1, 2, or 3.\n");
        return 1;
    }
    if (rho <= 0 || rho >= 1) {
        fprintf(stderr, "Error: Occupancy (rho) must be between 0 and 1.\n");
        return 1;
    }

    printf("Starting simulation with parameters:\n");
    printf("  - mu1=%.2f, mu2=%.2f, mu3=%.2f\n", mu1, mu2, mu3);
    printf("  - Policy ID: %d\n", policyId);
    printf("  - Rho: %.4f\n", rho);
    printf("  - Seed: %ld\n", seed);

    // Call the main simulation function
    runSimulation(mu1, mu2, mu3, policyId, rho, seed);

    printf("Simulation finished successfully.\n");

    return 0;
}
