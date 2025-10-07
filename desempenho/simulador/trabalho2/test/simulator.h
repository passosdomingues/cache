/**
 * @file simulator.h
 * @author Rafael Passos Domingues
 * @last_update 2025 Sep 25 14h36
 * 
 * @brief Low-level event-driven queueing system simulator for three queues with configurable scheduling policies.
 *        Simulates M/M/1 queue systems with different occupancy scenarios and produces detailed metrics
 *        for validation against Little's Law. Outputs CSV files for Python analysis.
 * 
 * Expected outputs:
 * - CSV files with timestamped samples of E[N], E[W], queue sizes, measured lambda, occupancy, and Little's Law error
 * - Proof files validating Little's Law across multiple seeds and scenarios
 * - Batch execution for rho = 0.80, 0.90, 0.95, 0.999 with configurable service rates
 */

#ifndef SIMULATOR_H
#define SIMULATOR_H

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <string.h>

#define NUM_QUEUES 3
#define SIMULATION_TIME 86400.0
#define SAMPLING_INTERVAL 10.0
#define MAX_SEEDS 10
#define DEFAULT_TOLERANCE 1e-3

/**
 * @brief Queue selection policy function pointer type
 * @param queueLengths Array of current queue lengths
 * @param avgWaitTimes Array of average waiting times per queue
 * @param longestWaits Array of longest waiting times per queue
 * @param numQueues Number of queues in system
 * @return Index of selected queue, -1 if no queue selected
 */
typedef int (*QueueSelectionPolicy)(double queueLengths[], double avgWaitTimes[], double longestWaits[], int numQueues);

/**
 * @brief Measurement structure for Little's Law calculations using area under curve method
 */
typedef struct {
    double previousTime;              /**< Last update time for area calculation */
    unsigned long int requestCount;   /**< Current number of requests in system */
    double areaSum;                   /**< Cumulative area under curve */
    unsigned long int totalArrivals;  /**< Total arrivals for lambda calculation */
    double totalWaitingTime;          /**< Total waiting time for E[W] calculation */
} LittleMeasurement;

/**
 * @brief Queue state structure containing dynamic state and statistics
 */
typedef struct {
    unsigned long int queueLength;    /**< Current number of customers in queue */
    double* arrivalTimes;             /**< Array of customer arrival timestamps */
    unsigned long int maxQueueLength; /**< Maximum observed queue length */
    unsigned long int capacity;       /**< Current capacity of arrivalTimes array */
    
    LittleMeasurement EN;             /**< E[N] measurement for this queue */
    LittleMeasurement EWArrivals;     /**< E[W] measurement from arrival perspective */
    LittleMeasurement EWDepartures;   /**< E[W] measurement from departure perspective */
    
    double totalServiceTime;          /**< Cumulative service time for this queue */
    unsigned long int servedRequests; /**< Number of served requests */
} QueueState;

/**
 * @brief Main simulation state structure
 */
typedef struct {
    QueueState queues[NUM_QUEUES];    /**< Array of queue states */
    
    int currentlyServingQueue;        /**< Index of queue currently being served, -1 if idle */
    double serviceCompletionTime;     /**< Time of next service completion */
    
    double nextArrivalTimes[NUM_QUEUES]; /**< Array of next arrival times for each queue */
    double currentTime;               /**< Current simulation time */
    
    unsigned long int totalRequests;  /**< Total requests across all queues */
    double totalBusyTime;             /**< Cumulative time server was busy */
    
    double lastSampleTime;            /**< Time of last sample */
    unsigned long int sampleCount;    /**< Number of samples taken */
    
    QueueSelectionPolicy policy;      /**< Current queue selection policy function */
} SimulationState;

/**
 * @brief Sample data structure for recording metrics at sampling intervals
 */
typedef struct {
    double timestamp;                 /**< Simulation time of sample */
    unsigned long int sampleIndex;    /**< Sequential sample index */
    double EN;                        /**< System-wide E[N] */
    double EW;                        /**< System-wide E[W] */
    unsigned long int queueSizes[NUM_QUEUES]; /**< Individual queue sizes */
    double measuredLambda;            /**< Measured arrival rate */
    double measuredOccupancy;         /**< Measured server occupancy */
    double littleError;               /**< Little's Law error: EN - lambda * EW */
} SampleData;

/**
 * @brief Scenario configuration structure
 */
typedef struct {
    double targetRho;                 /**< Target occupancy factor rho */
    double serviceRates[NUM_QUEUES];  /**< Service rates mu for each queue */
    double arrivalRates[NUM_QUEUES];  /**< Computed arrival rates lambda = rho * mu */
    QueueSelectionPolicy policy;      /**< Queue selection policy to use */
    unsigned long int seed;           /**< Random seed for reproducibility */
    char scenarioName[50];            /**< Descriptive scenario name */
} ScenarioConfig;

/**
 * @brief Batch configuration structure
 */
typedef struct {
    double rhoValues[4];              /**< Target rho values: 0.80, 0.90, 0.95, 0.999 */
    double serviceRates[NUM_QUEUES];  /**< Per-queue service rates */
    unsigned long int seeds[MAX_SEEDS]; /**< Array of random seeds */
    int numSeeds;                     /**< Number of seeds in array */
    char outputDirectory[100];        /**< Output directory for results */
} BatchConfig;

// Random number generation functions
double randomUniform(void);
double exponentialRandom(double rate);

// Queue selection policies
int selectLargestQueuePolicy(double queueLengths[], double avgWaitTimes[], double longestWaits[], int numQueues);
int selectAverageWaitTimePolicy(double queueLengths[], double avgWaitTimes[], double longestWaits[], int numQueues);
int selectLongestWaitTimePolicy(double queueLengths[], double avgWaitTimes[], double longestWaits[], int numQueues);

// Core simulation functions
void initializeSimulationState(SimulationState* state, double arrivalRates[], double serviceRates[], QueueSelectionPolicy policy);
void processArrivalEvent(SimulationState* state, int queueIndex);
void processDepartureEvent(SimulationState* state);
double calculateMinimumEventTime(SimulationState* state);
void takeSample(SimulationState* state, SampleData* sample);
void writeSampleToCSV(FILE* file, SampleData sample);
void cleanupSimulationState(SimulationState* state);

// Batch execution functions
void runSingleSimulation(ScenarioConfig config, const char* outputFilename);
void runBatchSimulations(BatchConfig batchConfig);
void validateLittleLaw(const char* scenarioName, const char* resultsDirectory, double tolerance);

// Utility functions
void createDirectoryIfNotExists(const char* directory);
double calculateMean(double values[], int count);
double calculateMedian(double values[], int count);
double calculateStdDev(double values[], int count, double mean);

#endif /* SIMULATOR_H */
