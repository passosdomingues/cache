/**
 * @file policies.c
 * @brief Implementation of the server's queue selection policies.
 *
 * Project: M/M/1 Multi-Queue Simulator
 * Author: Rafael Passos Domingues
 * Last Update: 2025 Sep 25 14h36
 *
 * Purpose:
 * This file implements the decision logic for the server. Each function
 * represents a distinct policy for choosing which queue to serve when the
 * server is free and customers are waiting. These functions are designed
 * to be called via a function pointer from the main simulator engine,
 * allowing for flexible and extensible scheduling behavior.
 */
#include "../include/policies.h"
#include <float.h>

/**
 * @brief Policy 1: Selects the queue with the largest number of waiting customers.
 * Ties are broken by choosing the lowest queue index.
 * @param state Pointer to the current simulator state.
 * @return The index (0, 1, or 2) of the selected queue.
 */
int policyOneSelectLargestQueue(SimulatorState* state) {
    int maxCount = -1;
    int selectedQueue = -1;
    for (int i = 0; i < 3; i++) {
        if (state->queues[i].customerCount > maxCount) {
            maxCount = state->queues[i].customerCount;
            selectedQueue = i;
        }
    }
    return selectedQueue;
}

/**
 * @brief Policy 2: Selects the queue with the largest average waiting time so far.
 * Average wait time is calculated as total wait time divided by total arrivals for that queue.
 * @param state Pointer to the current simulator state.
 * @return The index (0, 1, or 2) of the selected queue.
 */
int policyTwoSelectHighestAverageWait(SimulatorState* state) {
    double maxAvgWait = -1.0;
    int selectedQueue = -1;
    for (int i = 0; i < 3; i++) {
        if (state->queues[i].customerCount > 0) { // Only consider non-empty queues
            double avgWait = 0.0;
            if (state->queues[i].totalArrivals > 0) {
                avgWait = state->queues[i].totalWaitTime / state->queues[i].totalArrivals;
            }
            if (avgWait > maxAvgWait) {
                maxAvgWait = avgWait;
                selectedQueue = i;
            }
        }
    }
    // Fallback if all non-empty queues have 0 avg wait (e.g., no departures yet)
    if (selectedQueue == -1) {
       for (int i = 0; i < 3; i++) {
            if (state->queues[i].customerCount > 0) return i;
       }
    }
    return selectedQueue;
}

/**
 * @brief Policy 3: Selects the queue containing the customer who has waited the longest globally.
 * This implements a global First-In, First-Out (FIFO) discipline.
 * @param state Pointer to the current simulator state.
 * @return The index (0, 1, or 2) of the selected queue.
 */
int policyThreeSelectOldestCustomer(SimulatorState* state) {
    double earliestArrivalTime = DBL_MAX;
    int selectedQueue = -1;
    for (int i = 0; i < 3; i++) {
        if (state->queues[i].head != NULL) { // Check if queue is not empty
            if (state->queues[i].head->arrivalTime < earliestArrivalTime) {
                earliestArrivalTime = state->queues[i].head->arrivalTime;
                selectedQueue = i;
            }
        }
    }
    return selectedQueue;
}
