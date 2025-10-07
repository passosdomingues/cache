/**
 * @file simulator.c
 * @brief Core implementation of the event-driven simulation engine.
 *
 * Project: M/M/1 Multi-Queue Simulator
 * Author: Rafael Passos Domingues
 * Last Update: 2025 Sep 25 14h36
 *
 * Purpose:
 * This file contains the logic for the discrete-event simulation. It initializes
 * the simulator state, runs the main event loop, processes arrivals and
 * departures, updates statistics, and writes sampled data to an output file.
 * The structure is designed to be modular and easily extensible.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <float.h>
#include <sys/stat.h>
#include "../include/simulator.h"
#include "../include/rng.h"
#include "../include/policies.h"

// --- Private Helper Function Prototypes ---
static void initializeState(SimulatorState* state, double mu1, double mu2, double mu3, int policyId, double rho, long seed);
static void processArrival(SimulatorState* state, int queueIndex);
static void processDeparture(SimulatorState* state);
static void updateStatistics(SimulatorState* state, double nextEventTime);
static void sampleMetrics(SimulatorState* state);
static void finalizeSimulation(SimulatorState* state);
static double findNextEventTime(SimulatorState* state, int* nextEventType, int* eventQueueIndex);
static void scheduleNextArrival(SimulatorState* state, int queueIndex);
static void scheduleNextDeparture(SimulatorState* state);

// --- Core Simulation Function ---

void runSimulation(double mu1, double mu2, double mu3, int policyId, double rho, long seed) {
    SimulatorState state;
    initializeState(&state, mu1, mu2, mu3, policyId, rho, seed);

    while (state.currentTime < state.maxTime) {
        int nextEventType = -1; // 0=Arrival, 1=Departure
        int eventQueueIndex = -1;
        double nextEventTime = findNextEventTime(&state, &nextEventType, &eventQueueIndex);

        if (nextEventTime > state.maxTime) {
            nextEventTime = state.maxTime;
        }

        // Process any sampling points before the next event
        while (state.nextSampleTime < nextEventTime) {
            updateStatistics(&state, state.nextSampleTime);
            sampleMetrics(&state);
            state.lastEventTime = state.nextSampleTime;
            state.nextSampleTime += state.samplePeriod;
        }

        updateStatistics(&state, nextEventTime);
        state.currentTime = nextEventTime;
        state.lastEventTime = nextEventTime;

        if (state.currentTime >= state.maxTime) break;

        if (nextEventType == 0) { // Arrival
            processArrival(&state, eventQueueIndex);
        } else if (nextEventType == 1) { // Departure
            processDeparture(&state);
        }
    }

    finalizeSimulation(&state);
}


// --- Helper Function Implementations ---

/**
 * @brief Initializes the simulator state structure at the beginning of a run.
 */
static void initializeState(SimulatorState* state, double mu1, double mu2, double mu3, int policyId, double rho, long seed) {
    memset(state, 0, sizeof(SimulatorState));

    // Time setup
    state->maxTime = 86400.0; // 24 hours
    state->samplePeriod = 10.0;
    state->nextSampleTime = state->samplePeriod;

    // RNG
    state->masterSeed = seed;
    seedRNG(state->masterSeed);

    // Parameters
    state->serviceRate[0] = mu1;
    state->serviceRate[1] = mu2;
    state->serviceRate[2] = mu3;
    double totalMu = mu1 + mu2 + mu3; // Using sum of mu as reference for system capacity
    double totalLambda = rho * totalMu;
    state->arrivalRate[0] = totalLambda / 3.0; // Distribute arrivals evenly
    state->arrivalRate[1] = totalLambda / 3.0;
    state->arrivalRate[2] = totalLambda / 3.0;
    
    // Policy
    switch (policyId) {
        case 1: state->decisionPolicy = policyOneSelectLargestQueue; break;
        case 2: state->decisionPolicy = policyTwoSelectHighestAverageWait; break;
        case 3: state->decisionPolicy = policyThreeSelectOldestCustomer; break;
        default: exit(1); // Should be caught in main
    }

    // Queues and Server
    for (int i = 0; i < 3; i++) {
        initializeQueue(&state->queues[i]);
    }
    state->serverStatus = 0; // IDLE
    state->nextDepartureTime = DBL_MAX;

    // Schedule initial arrivals
    for (int i = 0; i < 3; i++) {
        scheduleNextArrival(state, i);
    }

    // Output file
    char filename[256];
    mkdir("results", 0755);
    sprintf(filename, "results/sim_policy%d_rho%.4f_seed%ld.csv", policyId, rho, seed);
    state->outputFile = fopen(filename, "w");
    if (!state->outputFile) {
        perror("Failed to open output file");
        exit(1);
    }
    fprintf(state->outputFile, "timestamp,sampleIndex,EN,EW,queueSize1,queueSize2,queueSize3,measuredLambda,measuredOccupancy,littleError\n");
}


/**
 * @brief Finds the time and type of the next event.
 */
static double findNextEventTime(SimulatorState* state, int* nextEventType, int* eventQueueIndex) {
    double minTime = state->nextDepartureTime;
    *nextEventType = 1; // Assume departure is next
    *eventQueueIndex = -1;

    for (int i = 0; i < 3; i++) {
        if (state->nextArrivalTime[i] < minTime) {
            minTime = state->nextArrivalTime[i];
            *nextEventType = 0; // It's an arrival
            *eventQueueIndex = i;
        }
    }
    return minTime;
}

/**
 * @brief Updates area-under-curve statistics up to the given time.
 */
static void updateStatistics(SimulatorState* state, double eventTime) {
    double duration = eventTime - state->lastEventTime;
    if (duration < 0) return;

    int totalCustomersInSystem = state->queues[0].customerCount + state->queues[1].customerCount + state->queues[2].customerCount;
    if (state->serverStatus == 1) {
        totalCustomersInSystem++;
    }

    state->areaN += totalCustomersInSystem * duration;
    for(int i = 0; i < 3; ++i) {
        state->queues[i].areaNq += state->queues[i].customerCount * duration;
    }

    if (state->serverStatus == 1) {
        state->totalServerBusyTime += duration;
    }
}


/**
 * @brief Processes an arrival event for a specific queue.
 */
static void processArrival(SimulatorState* state, int queueIndex) {
    state->totalArrivals++;
    state->queues[queueIndex].totalArrivals++;

    if (state->serverStatus == 0) { // Server is IDLE
        state->serverStatus = 1; // Becomes BUSY
        state->queueBeingServed = queueIndex;
        state->serverLastBusyTime = state->currentTime;
        scheduleNextDeparture(state);
    } else { // Server is BUSY
        enqueue(&state->queues[queueIndex], state->currentTime);
    }
    scheduleNextArrival(state, queueIndex);
}

/**
 * @brief Processes a departure event from the server.
 */
static void processDeparture(SimulatorState* state) {
    state->totalDepartures++;

    // Add customer's total time in system to areaW for E[W]
    // The departure time is currentTime, arrival time was stored when service began.
    // A more direct way: sum W_i, which areaW represents.
    
    // Check if any queue has customers waiting
    int totalWaiting = state->queues[0].customerCount + state->queues[1].customerCount + state->queues[2].customerCount;

    if (totalWaiting > 0) {
        int nextQueue = state->decisionPolicy(state);
        state->queueBeingServed = nextQueue;
        
        CustomerNode* servedCustomer = dequeue(&state->queues[nextQueue]);
        if (servedCustomer) {
            double waitTime = state->currentTime - servedCustomer->arrivalTime;
            state->queues[nextQueue].totalWaitTime += waitTime;
            // E[W] is total time in system, so add service time
            double serviceTime = state->currentTime - state->serverLastBusyTime; 
            state->areaW += (waitTime + serviceTime);
            free(servedCustomer);
        }
        
        scheduleNextDeparture(state);
        state->serverLastBusyTime = state->currentTime; // Reset for next customer
    } else {
        state->serverStatus = 0; // Becomes IDLE
        state->queueBeingServed = -1;
        state->nextDepartureTime = DBL_MAX; // No departure scheduled
    }
}

/**
 * @brief Schedules the next arrival for a given queue.
 */
static void scheduleNextArrival(SimulatorState* state, int queueIndex) {
    state->nextArrivalTime[queueIndex] = state->currentTime + exponencial(state->arrivalRate[queueIndex]);
}

/**
 * @brief Schedules the next departure based on the queue being served.
 */
static void scheduleNextDeparture(SimulatorState* state) {
    int qIndex = state->queueBeingServed;
    state->nextDepartureTime = state->currentTime + exponencial(state->serviceRate[qIndex]);
}

/**
 * @brief Samples all relevant metrics and writes a row to the CSV.
 */
static void sampleMetrics(SimulatorState* state) {
    double timeElapsed = state->nextSampleTime;
    if (timeElapsed <= 0) return;

    double EN = state->areaN / timeElapsed;
    double EW = (state->totalDepartures > 0) ? (state->areaW / state->totalDepartures) : 0.0;
    double measuredLambda = state->totalArrivals / timeElapsed;
    double measuredOccupancy = state->totalServerBusyTime / timeElapsed;
    double littleError = EN - (measuredLambda * EW);

    fprintf(state->outputFile, "%.2f,%d,%.6f,%.6f,%d,%d,%d,%.6f,%.6f,%.6f\n",
        timeElapsed,
        state->sampleIndex++,
        EN,
        EW,
        state->queues[0].customerCount,
        state->queues[1].customerCount,
        state->queues[2].customerCount,
        measuredLambda,
        measuredOccupancy,
        littleError);
}


/**
 * @brief Cleans up resources at the end of the simulation.
 */
static void finalizeSimulation(SimulatorState* state) {
    for (int i = 0; i < 3; i++) {
        destroyQueue(&state->queues[i]);
    }
    if (state->outputFile) {
        fclose(state->outputFile);
    }
}
