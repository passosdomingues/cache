#ifndef POLICIES_H
#define POLICIES_H

#include "simulator.h"

/**
 * @file policies.h
 * @brief Header for the server's queue selection policies.
 *
 * Project: M/M/1 Multi-Queue Simulator
 * Author: Rafael Passos Domingues
 * Last Update: 2025 Sep 25 14h36
 *
 * Purpose:
 * This file declares the different decision policy functions that the
 * server can use to select the next queue to serve when it becomes available.
 * Each policy is implemented as a function that inspects the simulator's
 * state and returns the index of the chosen queue.
 */

/**
 * @brief Selects the queue with the largest number of waiting customers.
 * @param state Pointer to the current simulator state.
 * @return The index (0, 1, or 2) of the selected queue.
 */
int policyOneSelectLargestQueue(SimulatorState* state);

/**
 * @brief Selects the queue with the largest average waiting time so far.
 * @param state Pointer to the current simulator state.
 * @return The index (0, 1, or 2) of the selected queue.
 */
int policyTwoSelectHighestAverageWait(SimulatorState* state);

/**
 * @brief Selects the queue containing the customer who has waited the longest.
 * @param state Pointer to the current simulator state.
 * @return The index (0, 1, or 2) of the selected queue.
 */
int policyThreeSelectOldestCustomer(SimulatorState* state);

#endif // POLICIES_H
