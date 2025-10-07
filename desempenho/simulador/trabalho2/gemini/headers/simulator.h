#ifndef SIMULATOR_H
#define SIMULATOR_H

#include <stdio.h>
#include "queue.h"

/**
 * @file simulator.h
 * @brief Header for the core simulation engine.
 *
 * Project: M/M/1 Multi-Queue Simulator
 * Author: Rafael Passos Domingues
 * Last Update: 2025 Sep 25 14h36
 *
 * Purpose:
 * This header defines the main SimulatorState structure and the function
 * prototype for running a complete simulation. The simulator is designed
 * to be event-driven, handling arrivals and departures for three parallel
 * queues served by a single server. It collects detailed statistics for
 * performance analysis.
 */

// Forward declaration of DecisionPolicyType
struct SimulatorState;
typedef int (*DecisionPolicyType)(struct SimulatorState*);

/**
 * @struct SimulatorState
 * @brief Encapsulates the entire state of the simulation.
 */
typedef struct SimulatorState {
    // --- Time Management ---
    double currentTime;             ///< Current simulation time in seconds.
    double maxTime;                 ///< Total simulation duration in seconds.
    double nextSampleTime;          ///< Time of the next statistics sample.
    double samplePeriod;            ///< Interval between samples in seconds.

    // --- Event Scheduling ---
    double nextArrivalTime[3];      ///< Time of the next arrival for each of the 3 queues.
    double nextDepartureTime;       ///< Time of the next departure from the server.

    // --- Server State ---
    int serverStatus;               ///< Server status: 0 for IDLE, 1 for BUSY.
    int queueBeingServed;           ///< Index of the queue currently being served (0, 1, or 2).
    double serverLastBusyTime;      ///< Time when the server last became busy.

    // --- Queues ---
    Queue queues[3];                ///< Array of three queue structures.

    // --- Policy ---
    DecisionPolicyType decisionPolicy; ///< Function pointer to the queue selection policy.

    // --- Input Parameters ---
    double arrivalRate[3];          ///< Per-queue arrival rates (lambda_q).
    double serviceRate[3];          ///< Per-queue service rates (mu_q).
    long masterSeed;                ///< The master seed for this simulation run.

    // --- Global Statistics ---
    long totalArrivals;             ///< Total number of arrivals across all queues.
    long totalDepartures;           ///< Total number of departures from the system.
    double totalServerBusyTime;     ///< Cumulative time the server has been busy.
    double areaN;                   ///< Area under the N(t) curve for E[N] calculation.
    double areaW;                   ///< Cumulative time spent in system by all customers for E[W].
    double lastEventTime;           ///< Time of the last processed event.

    // --- Output ---
    FILE* outputFile;               ///< File pointer for the CSV output.
    int sampleIndex;                ///< Index for the current sample.

} SimulatorState;

/**
 * @brief Runs a complete simulation for a given set of parameters.
 *
 * @param mu1 Service rate for queue 1.
 * @param mu2 Service rate for queue 2.
 * @param mu3 Service rate for queue 3.
 * @param policyId Identifier for the decision policy to use (1, 2, or 3).
 * @param rho The target system occupancy.
 * @param seed The seed for the random number generator.
 */
void runSimulation(double mu1, double mu2, double mu3, int policyId, double rho, long seed);

#endif // SIMULATOR_H
