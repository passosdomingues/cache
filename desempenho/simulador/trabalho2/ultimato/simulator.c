/**
 * @file simulator.c
 * @author Rafael Passos Domingues
 * @brief Implementation of advanced queueing system simulator with multiple scheduling policies
 * 
 * This simulator implements a discrete-event simulation of a multi-queue system
 * with configurable scheduling policies. It collects comprehensive metadata
 * using circular buffers as described in Salles' utility-based scheduling paper.
 */

#include "simulator.h"

// ============================================================================
// RANDOM NUMBER GENERATION
// ============================================================================

/**
 * @brief Generates a uniform random number in (0,1]
 * 
 * Uses the standard rand() function but ensures the value is in (0,1]
 * to avoid issues with logarithmic transformations in exponential distribution
 * 
 * @return double Random number in range (0,1]
 */
double generateUniformRandom(void) {
    double uniformRandom = rand() / ((double) RAND_MAX + 1);
    // Ensure we don't return 0.0 to avoid log(0) in exponential generation
    uniformRandom = 1.0 - uniformRandom;
    return uniformRandom;
}

/**
 * @brief Generates an exponentially distributed random number
 * 
 * Uses the inverse transform method: F^{-1}(u) = -ln(1-u)/λ
 * where u is uniform(0,1] and λ is the rate parameter
 * 
 * @param rateParameter λ - Rate parameter of exponential distribution
 * @return double Exponentially distributed random variate
 */
double generateExponentialRandom(double rateParameter) {
    double uniform = generateUniformRandom();
    return (-1.0 / rateParameter) * log(uniform);
}

// ============================================================================
// CIRCULAR MEASUREMENT WINDOW IMPLEMENTATION
// ============================================================================

/**
 * @brief Initializes a circular measurement window for metadata collection
 * 
 * Implements the measurement window concept from Salles' paper using
 * a circular buffer to store the most recent packet statistics
 * 
 * @param window Pointer to the measurement window to initialize
 * @param size Maximum capacity of the circular buffer
 */
void initializeMeasurementWindow(CircularMeasurementWindow* window, int size) {
    window->arrivalTimestamps = malloc(size * sizeof(double));
    window->departureTimestamps = malloc(size * sizeof(double));
    window->waitingTimes = malloc(size * sizeof(double));
    
    if (window->arrivalTimestamps == NULL || 
        window->departureTimestamps == NULL || 
        window->waitingTimes == NULL) {
        fprintf(stderr, "Memory allocation failed for measurement window\n");
        exit(EXIT_FAILURE);
    }
    
    // Initialize all values to 0 and set pointers
    for (int i = 0; i < size; i++) {
        window->arrivalTimestamps[i] = 0.0;
        window->departureTimestamps[i] = 0.0;
        window->waitingTimes[i] = 0.0;
    }
    
    window->headIndex = 0;
    window->tailIndex = 0;
    window->currentSize = 0;
    window->maxSize = size;
    window->sumArrivalTimestamps = 0.0;
    window->sumWaitingTimes = 0.0;
    window->totalPacketsInWindow = 0;
}

/**
 * @brief Adds packet metadata to the circular measurement window
 * 
 * Maintains the sliding window of recent packets and updates
 * aggregate statistics for efficient average delay calculation
 * 
 * @param window Pointer to the measurement window
 * @param arrivalTime Packet arrival timestamp
 * @param departureTime Packet departure timestamp  
 * @param waitingTime Calculated packet waiting time
 */
void addPacketToMeasurementWindow(CircularMeasurementWindow* window, 
                                 double arrivalTime, double departureTime, double waitingTime) {
    
    // If buffer is full, remove oldest element before adding new one
    if (window->currentSize == window->maxSize) {
        // Remove head element from aggregates
        window->sumArrivalTimestamps -= window->arrivalTimestamps[window->headIndex];
        window->sumWaitingTimes -= window->waitingTimes[window->headIndex];
        window->totalPacketsInWindow--;
        
        // Move head forward (circularly)
        window->headIndex = (window->headIndex + 1) % window->maxSize;
        window->currentSize--;
    }
    
    // Add new element at tail position
    window->arrivalTimestamps[window->tailIndex] = arrivalTime;
    window->departureTimestamps[window->tailIndex] = departureTime;
    window->waitingTimes[window->tailIndex] = waitingTime;
    
    // Update aggregates
    window->sumArrivalTimestamps += arrivalTime;
    window->sumWaitingTimes += waitingTime;
    window->totalPacketsInWindow++;
    
    // Move tail forward (circularly)
    window->tailIndex = (window->tailIndex + 1) % window->maxSize;
    window->currentSize++;
}

/**
 * @brief Releases resources allocated for a measurement window
 * 
 * @param window Pointer to the measurement window to clean up
 */
void cleanupMeasurementWindow(CircularMeasurementWindow* window) {
    free(window->arrivalTimestamps);
    free(window->departureTimestamps);
    free(window->waitingTimes);
    
    window->arrivalTimestamps = NULL;
    window->departureTimestamps = NULL;
    window->waitingTimes = NULL;
    window->currentSize = 0;
    window->maxSize = 0;
}

// ============================================================================
// SCHEDULING POLICY IMPLEMENTATIONS
// ============================================================================

/**
 * @brief Round Robin scheduling policy
 * 
 * Cycles through queues in fixed order, serving one packet from each
 * non-empty queue in sequence. Provides basic fairness but may be
 * inefficient under varying load conditions.
 * 
 * @param queueLengths Array of current queue lengths
 * @param waitingTimes Array of head-of-line waiting times (unused in RR)
 * @param simulationState Complete simulation state (used to track last served queue)
 * @param numQueues Number of queues in system
 * @return int Index of selected queue, -1 if all queues empty
 */
int selectRoundRobinPolicy(double queueLengths[], double waitingTimes[], 
                          SimulationState* simulationState, int numQueues) {
    // Static variable to maintain state between calls
    static int lastServedQueue = -1;
    
    // Find next non-empty queue starting from last served
    for (int attempts = 0; attempts < numQueues; attempts++) {
        lastServedQueue = (lastServedQueue + 1) % numQueues;
        
        if (queueLengths[lastServedQueue] > 0) {
            return lastServedQueue;
        }
    }
    
    // No non-empty queues found
    return -1;
}

/**
 * @brief Waiting Time Priority scheduling policy
 * 
 * Selects the queue with the packet that has been waiting the longest.
 * This policy minimizes maximum waiting time but may cause starvation
 * for queues with lower arrival rates.
 * 
 * @param queueLengths Array of current queue lengths
 * @param waitingTimes Array of head-of-line waiting times
 * @param simulationState Complete simulation state
 * @param numQueues Number of queues in system
 * @return int Index of queue with longest waiting packet, -1 if all empty
 */
int selectWaitingTimePriorityPolicy(double queueLengths[], double waitingTimes[], 
                                   SimulationState* simulationState, int numQueues) {
    int selectedQueue = -1;
    double maxWaitingTime = -1.0;
    
    for (int i = 0; i < numQueues; i++) {
        // Only consider non-empty queues with valid waiting times
        if (queueLengths[i] > 0 && waitingTimes[i] > maxWaitingTime) {
            maxWaitingTime = waitingTimes[i];
            selectedQueue = i;
        }
    }
    
    return selectedQueue;
}

/**
 * @brief Utility-Based scheduling policy based on Salles' paper
 * 
 * Uses the average delay formula from the measurement window to
 * calculate current performance and select the queue with the
 * highest delay (lowest utility). Implements the utility maximin
 * fairness criterion described in the paper.
 * 
 * @param queueLengths Array of current queue lengths
 * @param waitingTimes Array of head-of-line waiting times
 * @param simulationState Complete simulation state for delay calculation
 * @param numQueues Number of queues in system
 * @return int Index of queue with highest average delay, -1 if all empty
 */
int selectUtilityBasedPolicy(double queueLengths[], double waitingTimes[], 
                            SimulationState* simulationState, int numQueues) {
    int selectedQueue = -1;
    double maxAverageDelay = -1.0;
    
    for (int i = 0; i < numQueues; i++) {
        if (queueLengths[i] > 0) {
            double currentDelay = calculateCurrentAverageDelay(simulationState, i);
            
            if (currentDelay > maxAverageDelay) {
                maxAverageDelay = currentDelay;
                selectedQueue = i;
            }
        }
    }
    
    return selectedQueue;
}

// ============================================================================
// CORE SIMULATION ENGINE
// ============================================================================

/**
 * @brief Initializes the complete simulation state
 * 
 * Sets up all queues, measurement windows, and initial events
 * for a new simulation run. Allocates all necessary memory
 * and establishes initial conditions.
 * 
 * @param state Pointer to simulation state to initialize
 * @param arrivalRates Array of arrival rates for each queue
 * @param serviceRates Array of service rates for each queue
 */
void initializeSimulationState(SimulationState* state, double arrivalRates[], double serviceRates[]) {
    // Mark serviceRates as unused to suppress compiler warning
    // Service rates are currently fixed at 1.0 in this implementation
    (void)serviceRates;
    
    // Initialize global simulation state
    state->currentSimulationTime = 0.0;
    state->currentlyServingQueue = -1;  // Server starts idle
    state->nextServiceCompletionTime = INFINITY;
    state->lastSampleTime = 0.0;
    state->sampleCounter = 0;
    state->totalProcessedRequests = 0;
    state->totalServerBusyTime = 0.0;
    
    // Initialize each queue individually
    for (int i = 0; i < NUM_QUEUES; i++) {
        QueueState* queue = &state->queues[i];
        
        // Core queue state
        queue->currentQueueLength = 0;
        queue->maxObservedQueueLength = 0;
        queue->queueCapacity = 100;  // Initial capacity
        queue->totalServiceTime = 0.0;
        queue->totalServedRequests = 0;
        
        // Allocate memory for arrival times array
        queue->packetArrivalTimes = malloc(queue->queueCapacity * sizeof(double));
        if (queue->packetArrivalTimes == NULL) {
            fprintf(stderr, "Memory allocation failed for queue %d arrival times\n", i);
            exit(EXIT_FAILURE);
        }
        
        // Initialize measurement window for metadata collection
        initializeMeasurementWindow(&queue->measurementWindow, MEASUREMENT_WINDOW_SIZE);
        
        // Initialize Little's Law trackers
        queue->numberInSystemTracker.previousMeasurementTime = 0.0;
        queue->numberInSystemTracker.currentRequestCount = 0;
        queue->numberInSystemTracker.accumulatedArea = 0.0;
        queue->numberInSystemTracker.totalArrivals = 0;
        queue->numberInSystemTracker.totalWaitingTime = 0.0;
        
        queue->waitingTimeArrivalTracker.previousMeasurementTime = 0.0;
        queue->waitingTimeArrivalTracker.currentRequestCount = 0;
        queue->waitingTimeArrivalTracker.accumulatedArea = 0.0;
        queue->waitingTimeArrivalTracker.totalArrivals = 0;
        queue->waitingTimeArrivalTracker.totalWaitingTime = 0.0;
        
        queue->waitingTimeDepartureTracker.previousMeasurementTime = 0.0;
        queue->waitingTimeDepartureTracker.currentRequestCount = 0;
        queue->waitingTimeDepartureTracker.accumulatedArea = 0.0;
        
        // Schedule first arrival for this queue
        state->nextArrivalTimes[i] = generateExponentialRandom(arrivalRates[i]);
    }
}

/**
 * @brief Processes an arrival event for a specific queue
 * 
 * Handles the complete logic for a new packet arrival including:
 * - Queue state updates
 * - Measurement window updates
 * - Little's Law tracking
 * - Server activation if idle
 * 
 * @param state Pointer to simulation state
 * @param queueIndex Index of queue receiving the arrival
 */
void processArrivalEvent(SimulationState* state, int queueIndex) {
    QueueState* queue = &state->queues[queueIndex];
    double currentTime = state->currentSimulationTime;
    
    // Update queue length and track maximum
    queue->currentQueueLength++;
    if (queue->currentQueueLength > queue->maxObservedQueueLength) {
        queue->maxObservedQueueLength = queue->currentQueueLength;
    }
    
    // Dynamically resize arrival times array if needed
    if (queue->currentQueueLength > queue->queueCapacity) {
        queue->queueCapacity *= 2;
        double* newArrivalTimes = realloc(queue->packetArrivalTimes, 
                                         queue->queueCapacity * sizeof(double));
        if (newArrivalTimes == NULL) {
            fprintf(stderr, "Memory reallocation failed for queue %d\n", queueIndex);
            exit(EXIT_FAILURE);
        }
        queue->packetArrivalTimes = newArrivalTimes;
    }
    
    // Store arrival time for the new packet (at end of queue)
    queue->packetArrivalTimes[queue->currentQueueLength - 1] = currentTime;
    
    // Update E[N] measurement (Number in System)
    LittlesLawTracker* enTracker = &queue->numberInSystemTracker;
    enTracker->accumulatedArea += (currentTime - enTracker->previousMeasurementTime) 
                                * enTracker->currentRequestCount;
    enTracker->currentRequestCount++;
    enTracker->previousMeasurementTime = currentTime;
    enTracker->totalArrivals++;
    
    // Update E[W] arrival measurement (Waiting Time from arrival perspective)
    LittlesLawTracker* ewArrivalTracker = &queue->waitingTimeArrivalTracker;
    ewArrivalTracker->accumulatedArea += (currentTime - ewArrivalTracker->previousMeasurementTime) 
                                       * ewArrivalTracker->currentRequestCount;
    ewArrivalTracker->currentRequestCount++;
    ewArrivalTracker->previousMeasurementTime = currentTime;
    ewArrivalTracker->totalArrivals++;
    
    // Start service if server is idle
    if (state->currentlyServingQueue == -1) {
        state->currentlyServingQueue = queueIndex;
        state->nextServiceCompletionTime = currentTime + generateExponentialRandom(1.0);
    }
    
    // Schedule next arrival for this queue
    state->nextArrivalTimes[queueIndex] = currentTime + generateExponentialRandom(1.0);
    state->totalProcessedRequests++;
}

/**
 * @brief Processes a departure (service completion) event
 * 
 * Handles packet departure logic including:
 * - Waiting time calculation
 * - Measurement window updates
 * - Queue state management
 * - Scheduling of next service
 * 
 * @param state Pointer to simulation state
 * @param policy Queue selection policy function for scheduling next service
 */
void processDepartureEvent(SimulationState* state, QueueSelectionPolicy policy) {
    int queueIndex = state->currentlyServingQueue;
    QueueState* queue = &state->queues[queueIndex];
    double currentTime = state->currentSimulationTime;
    
    if (queue->currentQueueLength > 0) {
        // Calculate waiting time for the departing packet (head of queue)
        double arrivalTime = queue->packetArrivalTimes[0];
        double waitingTime = currentTime - arrivalTime;
        
        // Add to measurement window for average delay calculation
        addPacketToMeasurementWindow(&queue->measurementWindow, 
                                   arrivalTime, currentTime, waitingTime);
        
        // Update waiting time statistics
        queue->waitingTimeArrivalTracker.totalWaitingTime += waitingTime;
        queue->totalServedRequests++;
        
        // Remove served packet from queue (shift remaining packets)
        queue->currentQueueLength--;
        for (unsigned long i = 1; i <= queue->currentQueueLength; i++) {
            queue->packetArrivalTimes[i - 1] = queue->packetArrivalTimes[i];
        }
        
        // Update E[N] measurement (Number in System)
        LittlesLawTracker* enTracker = &queue->numberInSystemTracker;
        enTracker->accumulatedArea += (currentTime - enTracker->previousMeasurementTime) 
                                    * enTracker->currentRequestCount;
        enTracker->currentRequestCount--;
        enTracker->previousMeasurementTime = currentTime;
        
        // Update E[W] departure measurement (Waiting Time from departure perspective)
        LittlesLawTracker* ewDepartureTracker = &queue->waitingTimeDepartureTracker;
        ewDepartureTracker->accumulatedArea += (currentTime - ewDepartureTracker->previousMeasurementTime) 
                                            * ewDepartureTracker->currentRequestCount;
        ewDepartureTracker->currentRequestCount++;
        ewDepartureTracker->previousMeasurementTime = currentTime;
    }
    
    // Find next queue to serve using the specified policy
    state->currentlyServingQueue = -1;
    state->nextServiceCompletionTime = INFINITY;
    
    // Prepare data for scheduling decision
    double queueLengths[NUM_QUEUES];
    double waitingTimes[NUM_QUEUES];
    
    for (int i = 0; i < NUM_QUEUES; i++) {
        queueLengths[i] = state->queues[i].currentQueueLength;
        
        // Calculate head-of-line waiting time for each queue
        waitingTimes[i] = 0.0;
        if (state->queues[i].currentQueueLength > 0) {
            waitingTimes[i] = currentTime - state->queues[i].packetArrivalTimes[0];
        }
    }
    
    // Use policy to select next queue for service
    int nextQueue = policy(queueLengths, waitingTimes, state, NUM_QUEUES);
    if (nextQueue != -1) {
        state->currentlyServingQueue = nextQueue;
        state->nextServiceCompletionTime = currentTime + generateExponentialRandom(1.0);
    }
}

/**
 * @brief Calculates the average delay for a queue using measurement window
 * 
 * Implements the formula from Salles' paper:
 * D_j(t) = (1/T_j) * (n_j * t - S_j + D_j)
 * where:
 *   T_j = total packets in measurement window
 *   n_j = current queue length
 *   t   = current time
 *   S_j = sum of arrival times in window
 *   D_j = sum of waiting times in window
 * 
 * @param state Pointer to simulation state
 * @param queueIndex Index of queue to calculate delay for
 * @return double Current average delay for the queue
 */
double calculateCurrentAverageDelay(SimulationState* state, int queueIndex) {
    QueueState* queue = &state->queues[queueIndex];
    CircularMeasurementWindow* window = &queue->measurementWindow;
    
    // Use measurement window data for calculation
    if (window->totalPacketsInWindow == 0) {
        return 0.0;
    }
    
    double currentTime = state->currentSimulationTime;
    double n_t = queue->currentQueueLength * currentTime;
    
    // Apply formula from Salles' paper
    return (1.0 / window->totalPacketsInWindow) * 
           (n_t - window->sumArrivalTimestamps + window->sumWaitingTimes);
}

/**
 * @brief Determines the time of the next simulation event
 * 
 * Scans all scheduled events (arrivals and service completions)
 * and returns the earliest event time to advance the simulation
 * 
 * @param state Pointer to simulation state
 * @return double Time of next event (or INFINITY if no events)
 */
double calculateNextEventTime(SimulationState* state) {
    double nextEventTime = state->nextArrivalTimes[0];
    
    // Find earliest arrival time
    for (int i = 1; i < NUM_QUEUES; i++) {
        if (state->nextArrivalTimes[i] < nextEventTime) {
            nextEventTime = state->nextArrivalTimes[i];
        }
    }
    
    // Check if service completion is earlier
    if (state->nextServiceCompletionTime < nextEventTime) {
        nextEventTime = state->nextServiceCompletionTime;
    }
    
    return nextEventTime;
}

/**
 * @brief Collects comprehensive system performance sample
 * 
 * Captures current state of all queues and calculates
 * performance metrics for analysis and visualization
 * 
 * @param state Pointer to simulation state
 * @param sample Pointer to sample data structure to populate
 */
void collectSystemSample(SimulationState* state, SampleData* sample) {
    sample->timestamp = state->currentSimulationTime;
    sample->sampleIndex = state->sampleCounter;
    
    double totalNumberInSystem = 0.0;
    double totalWaitingTime = 0.0;
    double totalArrivals = 0.0;
    double totalCumulativeWaitingTime = 0.0;
    
    // Calculate metrics for each queue
    for (int i = 0; i < NUM_QUEUES; i++) {
        QueueState* queue = &state->queues[i];
        
        // Finalize area calculations for current interval
        queue->numberInSystemTracker.accumulatedArea += 
            (state->currentSimulationTime - queue->numberInSystemTracker.previousMeasurementTime) 
            * queue->numberInSystemTracker.currentRequestCount;
            
        queue->waitingTimeArrivalTracker.accumulatedArea += 
            (state->currentSimulationTime - queue->waitingTimeArrivalTracker.previousMeasurementTime) 
            * queue->waitingTimeArrivalTracker.currentRequestCount;
            
        queue->waitingTimeDepartureTracker.accumulatedArea += 
            (state->currentSimulationTime - queue->waitingTimeDepartureTracker.previousMeasurementTime) 
            * queue->waitingTimeDepartureTracker.currentRequestCount;
        
        // Calculate E[N] for this queue (time-average)
        double numberInSystem = (state->currentSimulationTime > 0) ? 
            queue->numberInSystemTracker.accumulatedArea / state->currentSimulationTime : 0.0;
        totalNumberInSystem += numberInSystem;
        
        // Calculate E[W] for this queue (sample average)
        double waitingTime = 0.0;
        if (queue->waitingTimeArrivalTracker.totalArrivals > 0) {
            waitingTime = queue->waitingTimeArrivalTracker.totalWaitingTime / 
                         queue->waitingTimeArrivalTracker.totalArrivals;
        }
        totalWaitingTime += waitingTime;
        
        // Store queue-specific data
        sample->queueSizes[i] = queue->currentQueueLength;
        totalArrivals += queue->waitingTimeArrivalTracker.totalArrivals;
        totalCumulativeWaitingTime += queue->waitingTimeArrivalTracker.totalWaitingTime;
        
        // Reset trackers for next interval
        queue->numberInSystemTracker.previousMeasurementTime = state->currentSimulationTime;
        queue->waitingTimeArrivalTracker.previousMeasurementTime = state->currentSimulationTime;
        queue->waitingTimeDepartureTracker.previousMeasurementTime = state->currentSimulationTime;
    }
    
    // Calculate system-wide metrics
    sample->averageNumberInSystem = totalNumberInSystem / NUM_QUEUES;
    sample->averageWaitingTime = totalWaitingTime / NUM_QUEUES;
    sample->measuredArrivalRate = (state->currentSimulationTime > 0) ? 
        totalArrivals / state->currentSimulationTime : 0.0;
    sample->measuredOccupancy = (state->currentSimulationTime > 0) ? 
        state->totalServerBusyTime / state->currentSimulationTime : 0.0;
    
    // Validate Little's Law: E[N] = λ * E[W]
    sample->littlesLawError = sample->averageNumberInSystem - 
                             (sample->measuredArrivalRate * sample->averageWaitingTime);
    
    state->sampleCounter++;
}

/**
 * @brief Writes sample data to CSV file for post-processing
 * 
 * @param file Pointer to open CSV file
 * @param sample Sample data to write
 */
void writeSampleToCSV(FILE* file, SampleData sample) {
    fprintf(file, "%.6f,%lu,%.6f,%.6f,%lu,%lu,%lu,%.6f,%.6f,%.6f\n",
            sample.timestamp, sample.sampleIndex, sample.averageNumberInSystem, 
            sample.averageWaitingTime, sample.queueSizes[0], sample.queueSizes[1], 
            sample.queueSizes[2], sample.measuredArrivalRate, sample.measuredOccupancy, 
            sample.littlesLawError);
}

/**
 * @brief Releases all allocated memory and cleans up simulation state
 * 
 * @param state Pointer to simulation state to clean up
 */
void cleanupSimulationState(SimulationState* state) {
    for (int i = 0; i < NUM_QUEUES; i++) {
        free(state->queues[i].packetArrivalTimes);
        cleanupMeasurementWindow(&state->queues[i].measurementWindow);
    }
}

// ============================================================================
// EXPERIMENTAL EXECUTION
// ============================================================================

/**
 * @brief Executes a single simulation run with specified configuration
 * 
 * @param config Simulation configuration parameters
 * @param outputFilename Name of file to write results to
 */
void executeSingleSimulation(SimulationConfig config, const char* outputFilename) {
    printf("Starting simulation: %s\n", config.scenarioName);
    
    SimulationState state;
    double arrivalRates[NUM_QUEUES];
    
    // Calculate arrival rates based on target occupancy and service rates
    // Using the relation: λ = ρ * μ (for each queue)
    for (int i = 0; i < NUM_QUEUES; i++) {
        arrivalRates[i] = config.targetOccupancy * config.serviceRates[i];
    }
    
    // Set random seed for reproducible results
    srand(config.randomSeed);
    
    // Initialize simulation
    initializeSimulationState(&state, arrivalRates, config.serviceRates);
    
    // Create results directory
    mkdir("results", 0755);
    
    // Open output file
    FILE* outputFile = fopen(outputFilename, "w");
    if (outputFile == NULL) {
        printf("Error opening output file: %s\n", outputFilename);
        return;
    }
    
    // Write CSV header
    fprintf(outputFile, "timestamp,sampleIndex,averageNumberInSystem,averageWaitingTime,queueSize1,queueSize2,queueSize3,measuredArrivalRate,measuredOccupancy,littlesLawError\n");
    
    unsigned long sampleCounter = 0;
    double nextSampleTime = 0.0;
    
    // Main simulation loop - run for 24 hours (86400 seconds)
    while (state.currentSimulationTime < SIMULATION_TIME) {
        double nextEventTime = calculateNextEventTime(&state);
        
        // Process all samples until next event
        while (nextSampleTime <= nextEventTime && nextSampleTime <= SIMULATION_TIME) {
            state.currentSimulationTime = nextSampleTime;
            
            // Update busy time for current sampling interval
            if (state.currentlyServingQueue != -1) {
                double timeDelta = state.currentSimulationTime - state.lastSampleTime;
                if (timeDelta > 0) {
                    state.totalServerBusyTime += timeDelta;
                }
            }
            
            // Collect and write sample
            SampleData sample;
            collectSystemSample(&state, &sample);
            writeSampleToCSV(outputFile, sample);
            
            sampleCounter++;
            nextSampleTime = sampleCounter * SAMPLING_INTERVAL;
            state.lastSampleTime = state.currentSimulationTime;
        }
        
        // Advance to next event
        state.currentSimulationTime = nextEventTime;
        
        // Update busy time for event processing
        if (state.currentlyServingQueue != -1) {
            double timeDelta = state.currentSimulationTime - state.lastSampleTime;
            if (timeDelta > 0) {
                state.totalServerBusyTime += timeDelta;
            }
        }
        state.lastSampleTime = state.currentSimulationTime;
        
        // Process events occurring at current time
        for (int i = 0; i < NUM_QUEUES; i++) {
            if (fabs(state.currentSimulationTime - state.nextArrivalTimes[i]) < 1e-10) {
                processArrivalEvent(&state, i);
            }
        }
        
        if (fabs(state.currentSimulationTime - state.nextServiceCompletionTime) < 1e-10) {
            processDepartureEvent(&state, config.schedulingPolicy);
        }
        
        // Progress indicator
        if (sampleCounter % 100 == 0) {
            printf("  Progress: %.1f%% (Time: %.1f/%.1f)\n", 
                   (state.currentSimulationTime / SIMULATION_TIME) * 100.0,
                   state.currentSimulationTime, SIMULATION_TIME);
        }
    }
    
    // Take final sample at simulation end
    if (state.currentSimulationTime >= SIMULATION_TIME) {
        state.currentSimulationTime = SIMULATION_TIME;
        SampleData finalSample;
        collectSystemSample(&state, &finalSample);
        writeSampleToCSV(outputFile, finalSample);
    }
    
    fclose(outputFile);
    cleanupSimulationState(&state);
    
    printf("Simulation completed: %s (%lu samples)\n", outputFilename, sampleCounter);
}

/**
 * @brief Executes batch simulations for all occupancy scenarios and policies
 * 
 * Runs comprehensive experiments comparing all scheduling policies
 * across different traffic intensity levels
 */
void executeBatchSimulations(void) {
    printf("Executing batch simulations for multiple occupancy scenarios and policies...\n");
    
    // Define traffic intensity scenarios
    double occupancyScenarios[] = {0.800, 0.900, 0.950, 0.999};
    int numScenarios = sizeof(occupancyScenarios) / sizeof(occupancyScenarios[0]);
    
    // Define scheduling policies
    QueueSelectionPolicy policies[] = {
        selectRoundRobinPolicy,
        selectWaitingTimePriorityPolicy, 
        selectUtilityBasedPolicy
    };
    
    const char* policyNames[] = {
        "RoundRobin",
        "WaitingTimePriority", 
        "UtilityBased"
    };
    
    int numPolicies = sizeof(policies) / sizeof(policies[0]);
    
    // Fixed random seed for reproducibility
    unsigned long seed = 42;
    
    // Service rates (μ = 1.0 for all queues - standard M/M/3 system)
    double serviceRates[NUM_QUEUES] = {1.0, 1.0, 1.0};
    
    // Create results directory
    mkdir("results", 0755);
    
    // Execute all policy-scenario combinations
    for (int p = 0; p < numPolicies; p++) {
        for (int s = 0; s < numScenarios; s++) {
            SimulationConfig config;
            config.targetOccupancy = occupancyScenarios[s];
            
            for (int i = 0; i < NUM_QUEUES; i++) {
                config.serviceRates[i] = serviceRates[i];
            }
            
            config.schedulingPolicy = policies[p];
            config.randomSeed = seed;
            
            snprintf(config.scenarioName, sizeof(config.scenarioName), 
                    "%s_rho_%.3f", policyNames[p], config.targetOccupancy);
            
            char filename[100];
            snprintf(filename, sizeof(filename), 
                    "results/queue_data_%s_occupancy_%.3f.csv", 
                    policyNames[p], config.targetOccupancy);
            
            executeSingleSimulation(config, filename);
        }
    }
    
    printf("\nBatch simulations completed successfully!\n");
    printf("Generated %d files (3 policies × 4 scenarios):\n", numPolicies * numScenarios);
    
    for (int p = 0; p < numPolicies; p++) {
        for (int s = 0; s < numScenarios; s++) {
            printf("  - queue_data_%s_occupancy_%.3f.csv\n", 
                   policyNames[p], occupancyScenarios[s]);
        }
    }
}

/**
 * @brief Main program entry point
 * 
 * @param argc Argument count
 * @param argv Argument vector
 * @return int Program exit status
 */
int main(int argc, char* argv[]) {
    printf("Advanced Queueing System Simulator - Multi-Policy Comparison\n");
    printf("============================================================\n");
    
    if (argc > 1 && strcmp(argv[1], "--batch") == 0) {
        executeBatchSimulations();
    } else {
        printf("Usage: ./simulator --batch\n");
        printf("This will execute all scheduling policies across 4 occupancy scenarios.\n");
        printf("Generated CSV files will be saved in the 'results/' directory.\n");
    }
    
    return EXIT_SUCCESS;
}