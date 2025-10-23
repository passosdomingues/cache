/**
 * @file simulator.h
 * @author Rafael Passos Domingues
 * @brief Advanced event-driven queueing system simulator with multiple scheduling policies
 * 
 * Features:
 * - Multiple queue scheduling policies (Round Robin, Waiting Time Priority, Utility-Based)
 * - Circular buffer measurement windows for metadata collection
 * - Real-time performance metrics calculation
 * - Configurable traffic intensity scenarios
 */

#ifndef SIMULATOR_H
#define SIMULATOR_H

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <string.h>
#include <sys/stat.h>

// ============================================================================
// SIMULATION CONSTANTS
// ============================================================================

#define NUM_QUEUES 3                    // Number of parallel queues in the system
#define SIMULATION_TIME 86400.0         // 24 hours simulation (in seconds)
#define SAMPLING_INTERVAL 10.0          // Metrics sampling interval (10 seconds)
#define MEASUREMENT_WINDOW_SIZE 1000    // Size of circular buffer for metadata

// ============================================================================
// DATA STRUCTURES
// ============================================================================

/**
 * @brief Circular buffer for storing packet metadata and measurement history
 * 
 * Implements the measurement window concept from Salles' paper using
 * a circular list to store recent arrival/departure statistics
 */
typedef struct {
    double* arrivalTimestamps;           // Circular buffer of packet arrival times
    double* departureTimestamps;         // Circular buffer of packet departure times  
    double* waitingTimes;                // Circular buffer of calculated waiting times
    int headIndex;                       // Current head position (oldest element)
    int tailIndex;                       // Current tail position (newest element)
    int currentSize;                     // Current number of elements in buffer
    int maxSize;                         // Maximum capacity of circular buffer
    
    // Real-time metadata aggregates (for performance optimization)
    double sumArrivalTimestamps;         // S_j: Sum of arrival times in current window
    double sumWaitingTimes;              // D_j: Sum of waiting times in current window
    int totalPacketsInWindow;            // T_j: Total packets in measurement window
} CircularMeasurementWindow;

/**
 * @brief Little's Law measurement components for queue performance analysis
 * 
 * Tracks area under curve for E[N] and E[W] calculations
 * using the time-averaging method for stochastic processes
 */
typedef struct {
    double previousMeasurementTime;      // Last time metrics were updated
    unsigned long currentRequestCount;   // Current number of requests in system
    double accumulatedArea;              // Integral of request count over time
    unsigned long totalArrivals;         // Lifetime total arrivals for this queue
    double totalWaitingTime;             // Lifetime total waiting time
} LittlesLawTracker;

/**
 * @brief Complete state of a single queue in the system
 * 
 * Maintains both real-time state and historical metadata
 * for performance analysis and scheduling decisions
 */
typedef struct {
    // Core queue state
    unsigned long currentQueueLength;    // Instantaneous number of packets in queue
    double* packetArrivalTimes;          // Array of arrival times for queued packets
    unsigned long maxObservedQueueLength;// Peak queue length observed during simulation
    unsigned long queueCapacity;         // Current allocated capacity of arrivalTimes array
    
    // Measurement and analytics
    CircularMeasurementWindow measurementWindow; // Circular buffer for recent packets
    LittlesLawTracker numberInSystemTracker;     // Tracks E[N] - number in system
    LittlesLawTracker waitingTimeArrivalTracker; // Tracks E[W] from arrival perspective
    LittlesLawTracker waitingTimeDepartureTracker; // Tracks E[W] from departure perspective
    
    // Performance statistics
    double totalServiceTime;             // Aggregate service time for completed packets
    unsigned long totalServedRequests;   // Count of successfully served packets
} QueueState;

/**
 * @brief Complete simulation state container
 * 
 * Orchestrates the entire simulation including all queues,
 * event scheduling, and global performance tracking
 */
typedef struct {
    QueueState queues[NUM_QUEUES];           // Array of all queues in the system
    
    // Event management
    int currentlyServingQueue;               // Index of queue currently being served (-1 if idle)
    double nextServiceCompletionTime;        // Time when current service will complete
    
    // Arrival process management  
    double nextArrivalTimes[NUM_QUEUES];     // Scheduled arrival times for each queue
    
    // Simulation clock and statistics
    double currentSimulationTime;            // Global simulation clock
    unsigned long totalProcessedRequests;    // All-time total requests across all queues
    double totalServerBusyTime;              // Cumulative time server was busy
    
    // Sampling and data collection
    double lastSampleTime;                   // Time when last sample was taken
    unsigned long sampleCounter;             // Total number of samples taken
} SimulationState;

/**
 * @brief Container for sampled performance metrics
 * 
 * Captures system state at regular intervals for
 * post-simulation analysis and visualization
 */
typedef struct {
    double timestamp;                        // Simulation time when sample was taken
    unsigned long sampleIndex;               // Sequential sample identifier
    double averageNumberInSystem;            // E[N] - Average number in system
    double averageWaitingTime;               // E[W] - Average waiting time
    unsigned long queueSizes[NUM_QUEUES];    // Instantaneous sizes of all queues
    double measuredArrivalRate;              // λ - Measured arrival rate
    double measuredOccupancy;                // ρ - Server occupancy/utilization
    double littlesLawError;                  // Validation: E[N] - λ * E[W]
} SampleData;

/**
 * @brief Policy function pointer type for queue selection algorithms
 * 
 * All scheduling policies must conform to this signature:
 * @param queueLengths Array of current queue lengths
 * @param waitingTimes Array of head-of-line waiting times  
 * @param simulationState Complete simulation state for advanced policies
 * @param numQueues Number of queues in system
 * @return Index of selected queue for service, -1 if no suitable queue
 */
typedef int (*QueueSelectionPolicy)(
    double queueLengths[], 
    double waitingTimes[], 
    SimulationState* simulationState, 
    int numQueues
);

/**
 * @brief Complete simulation configuration
 * 
 * Parameterizes all aspects of simulation execution
 * for reproducible experimental scenarios
 */
typedef struct {
    double targetOccupancy;                  // ρ - Target traffic intensity
    double serviceRates[NUM_QUEUES];         // μ - Service rates for each queue
    double arrivalRates[NUM_QUEUES];         // λ - Arrival rates (calculated from ρ and μ)
    QueueSelectionPolicy schedulingPolicy;   // Pointer to queue selection algorithm
    unsigned long randomSeed;                // Seed for reproducible random number generation
    char scenarioName[50];                   // Descriptive name for this scenario
} SimulationConfig;

// ============================================================================
// SCHEDULING POLICY IMPLEMENTATIONS
// ============================================================================

int selectRoundRobinPolicy(double queueLengths[], double waitingTimes[], 
                          SimulationState* simulationState, int numQueues);
int selectWaitingTimePriorityPolicy(double queueLengths[], double waitingTimes[], 
                                   SimulationState* simulationState, int numQueues);
int selectUtilityBasedPolicy(double queueLengths[], double waitingTimes[], 
                            SimulationState* simulationState, int numQueues);

// ============================================================================
// CORE SIMULATION FUNCTIONS
// ============================================================================

// Random number generation
double generateUniformRandom(void);
double generateExponentialRandom(double rateParameter);

// Simulation lifecycle management
void initializeSimulationState(SimulationState* state, double arrivalRates[], double serviceRates[]);
void cleanupSimulationState(SimulationState* state);
void processArrivalEvent(SimulationState* state, int queueIndex);
void processDepartureEvent(SimulationState* state, QueueSelectionPolicy policy);
double calculateNextEventTime(SimulationState* state);

// Metrics collection and analysis
void collectSystemSample(SimulationState* state, SampleData* sample);
void writeSampleToCSV(FILE* file, SampleData sample);
double calculateCurrentAverageDelay(SimulationState* state, int queueIndex);

// Circular buffer operations for measurement window
void initializeMeasurementWindow(CircularMeasurementWindow* window, int size);
void addPacketToMeasurementWindow(CircularMeasurementWindow* window, 
                                 double arrivalTime, double departureTime, double waitingTime);
void cleanupMeasurementWindow(CircularMeasurementWindow* window);

// Experimental execution
void executeSingleSimulation(SimulationConfig config, const char* outputFilename);
void executeBatchSimulations(void);

#endif /* SIMULATOR_H */