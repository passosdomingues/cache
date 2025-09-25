/**
 * @file simulator.h
 * @author Rafael Passos Domingues
 * @last_update 2025 Sep 25 16h07
 * 
 * @brief Event-driven queueing system simulator with multiple queues
 */

#ifndef SIMULATOR_H
#define SIMULATOR_H

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <string.h>

#define NUM_QUEUES 3
#define SIMULATION_TIME 86400.0  // 24 hours
#define SAMPLING_INTERVAL 10.0   // 10 seconds

typedef int (*QueueSelectionPolicy)(double*, double*, double*, int);

typedef struct {
    double previousTime;
    unsigned long int requestCount;
    double areaSum;
    unsigned long int totalArrivals;
    double totalWaitingTime;
} LittleMeasurement;

typedef struct {
    unsigned long int queueLength;
    double* arrivalTimes;
    unsigned long int maxQueueLength;
    unsigned long int capacity;
    
    LittleMeasurement EN;
    LittleMeasurement EWArrivals;
    LittleMeasurement EWDepartures;
    
    double totalServiceTime;
    unsigned long int servedRequests;
} QueueState;

typedef struct {
    QueueState queues[NUM_QUEUES];
    
    int currentlyServingQueue;
    double serviceCompletionTime;
    
    double nextArrivalTimes[NUM_QUEUES];
    double currentTime;
    
    unsigned long int totalRequests;
    double totalBusyTime;
    
    double lastSampleTime;
    unsigned long int sampleCount;
} SimulationState;

typedef struct {
    double timestamp;
    unsigned long int sampleIndex;
    double EN;
    double EW;
    unsigned long int queueSizes[NUM_QUEUES];
    double measuredLambda;
    double measuredOccupancy;
    double littleError;
} SampleData;

typedef struct {
    double targetRho;
    double serviceRates[NUM_QUEUES];
    double arrivalRates[NUM_QUEUES];
    QueueSelectionPolicy policy;
    unsigned long int seed;
    char scenarioName[50];
} ScenarioConfig;

// Function declarations
double randomUniform(void);
double exponentialRandom(double rate);
int selectLargestQueuePolicy(double queueLengths[], double avgWaitTimes[], double longestWaits[], int numQueues);

void initializeSimulationState(SimulationState* state, double arrivalRates[], double serviceRates[]);
void processArrivalEvent(SimulationState* state, int queueIndex);
void processDepartureEvent(SimulationState* state);
double calculateMinimumEventTime(SimulationState* state);
void takeSample(SimulationState* state, SampleData* sample);
void writeSampleToCSV(FILE* file, SampleData sample);
void cleanupSimulationState(SimulationState* state);

void runSingleSimulation(ScenarioConfig config, const char* outputFilename);
void runBatchSimulations(void);

#endif /* SIMULATOR_H */
