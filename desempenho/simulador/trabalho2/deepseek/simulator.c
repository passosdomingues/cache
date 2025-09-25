/**
 * @file simulator.c
 * @author Rafael Passos Domingues
 * @last_update 2025 Sep 25 16h12
 * 
 * @brief Event-driven queueing system simulator with 4 occupancy scenarios
 */

#include "simulator.h"
#include <sys/stat.h>

// ============================================================================
// RANDOM NUMBER GENERATION
// ============================================================================

double randomUniform(void) {
    double u = rand() / ((double) RAND_MAX + 1);
    u = 1.0 - u;
    return u;
}

double exponentialRandom(double rate) {
    return (-1.0 / rate) * log(randomUniform());
}

// ============================================================================
// QUEUE SELECTION POLICIES
// ============================================================================

int selectLargestQueuePolicy(double queueLengths[], double avgWaitTimes[], double longestWaits[], int numQueues) {
    (void)avgWaitTimes;
    (void)longestWaits;
    
    int selected = -1;
    double maxLength = -1.0;
    
    for (int i = 0; i < numQueues; i++) {
        if (queueLengths[i] > maxLength) {
            maxLength = queueLengths[i];
            selected = i;
        }
    }
    
    return selected;
}

// ============================================================================
// SIMULATION CORE FUNCTIONS
// ============================================================================

void initializeSimulationState(SimulationState* state, double arrivalRates[], double serviceRates[]) {
    (void)serviceRates;  // Mark as unused to suppress warning
    
    state->currentTime = 0.0;
    state->currentlyServingQueue = -1;
    state->serviceCompletionTime = INFINITY;
    state->lastSampleTime = 0.0;
    state->sampleCount = 0;
    state->totalRequests = 0;
    state->totalBusyTime = 0.0;
    
    for (int i = 0; i < NUM_QUEUES; i++) {
        state->queues[i].queueLength = 0;
        state->queues[i].maxQueueLength = 0;
        state->queues[i].capacity = 100;
        state->queues[i].arrivalTimes = malloc(state->queues[i].capacity * sizeof(double));
        if (state->queues[i].arrivalTimes == NULL) {
            fprintf(stderr, "Memory allocation failed for queue %d\n", i);
            exit(EXIT_FAILURE);
        }
        state->queues[i].totalServiceTime = 0.0;
        state->queues[i].servedRequests = 0;
        
        // Initialize Little's Law measurements
        state->queues[i].EN.previousTime = 0.0;
        state->queues[i].EN.requestCount = 0;
        state->queues[i].EN.areaSum = 0.0;
        state->queues[i].EN.totalArrivals = 0;
        state->queues[i].EN.totalWaitingTime = 0.0;
        
        state->queues[i].EWArrivals.previousTime = 0.0;
        state->queues[i].EWArrivals.requestCount = 0;
        state->queues[i].EWArrivals.areaSum = 0.0;
        state->queues[i].EWArrivals.totalArrivals = 0;
        state->queues[i].EWArrivals.totalWaitingTime = 0.0;
        
        state->queues[i].EWDepartures.previousTime = 0.0;
        state->queues[i].EWDepartures.requestCount = 0;
        state->queues[i].EWDepartures.areaSum = 0.0;
        
        // Schedule first arrival
        state->nextArrivalTimes[i] = exponentialRandom(arrivalRates[i]);
    }
}

void processArrivalEvent(SimulationState* state, int queueIndex) {
    QueueState* queue = &state->queues[queueIndex];
    
    queue->queueLength++;
    if (queue->queueLength > queue->maxQueueLength) {
        queue->maxQueueLength = queue->queueLength;
    }
    
    // Check capacity
    if (queue->queueLength > queue->capacity) {
        queue->capacity *= 2;
        double* newArrivalTimes = realloc(queue->arrivalTimes, queue->capacity * sizeof(double));
        if (newArrivalTimes == NULL) {
            fprintf(stderr, "Memory reallocation failed for queue %d\n", queueIndex);
            exit(EXIT_FAILURE);
        }
        queue->arrivalTimes = newArrivalTimes;
    }
    
    queue->arrivalTimes[queue->queueLength - 1] = state->currentTime;
    
    // Update E[N] measurement
    queue->EN.areaSum += (state->currentTime - queue->EN.previousTime) * queue->EN.requestCount;
    queue->EN.requestCount++;
    queue->EN.previousTime = state->currentTime;
    queue->EN.totalArrivals++;
    
    // Update E[W] arrival measurement
    queue->EWArrivals.areaSum += (state->currentTime - queue->EWArrivals.previousTime) * queue->EWArrivals.requestCount;
    queue->EWArrivals.requestCount++;
    queue->EWArrivals.previousTime = state->currentTime;
    queue->EWArrivals.totalArrivals++;
    
    // Start service if server is idle
    if (state->currentlyServingQueue == -1) {
        state->currentlyServingQueue = queueIndex;
        state->serviceCompletionTime = state->currentTime + exponentialRandom(1.0);
    }
    
    // Schedule next arrival
    state->nextArrivalTimes[queueIndex] = state->currentTime + exponentialRandom(1.0);
    state->totalRequests++;
}

void processDepartureEvent(SimulationState* state) {
    int queueIndex = state->currentlyServingQueue;
    QueueState* queue = &state->queues[queueIndex];
    
    if (queue->queueLength > 0) {
        // Calculate waiting time for departing customer
        double arrivalTime = queue->arrivalTimes[0];
        double waitingTime = state->currentTime - arrivalTime;
        queue->EWArrivals.totalWaitingTime += waitingTime;
        
        queue->queueLength--;
        
        // Update E[N] measurement
        queue->EN.areaSum += (state->currentTime - queue->EN.previousTime) * queue->EN.requestCount;
        queue->EN.requestCount--;
        queue->EN.previousTime = state->currentTime;
        
        // Update E[W] departure measurement
        queue->EWDepartures.areaSum += (state->currentTime - queue->EWDepartures.previousTime) * queue->EWDepartures.requestCount;
        queue->EWDepartures.requestCount++;
        queue->EWDepartures.previousTime = state->currentTime;
        
        // Shift remaining customers
        for (unsigned long int i = 1; i <= queue->queueLength; i++) {
            queue->arrivalTimes[i - 1] = queue->arrivalTimes[i];
        }
    }
    
    // Find next queue to serve
    state->currentlyServingQueue = -1;
    state->serviceCompletionTime = INFINITY;
    
    double queueLengths[NUM_QUEUES];
    double avgWaitTimes[NUM_QUEUES];
    double longestWaits[NUM_QUEUES];
    
    for (int i = 0; i < NUM_QUEUES; i++) {
        queueLengths[i] = state->queues[i].queueLength;
        avgWaitTimes[i] = 0.0;
        longestWaits[i] = 0.0;
        
        if (state->queues[i].queueLength > 0) {
            longestWaits[i] = state->currentTime - state->queues[i].arrivalTimes[0];
        }
    }
    
    int nextQueue = selectLargestQueuePolicy(queueLengths, avgWaitTimes, longestWaits, NUM_QUEUES);
    if (nextQueue != -1) {
        state->currentlyServingQueue = nextQueue;
        state->serviceCompletionTime = state->currentTime + exponentialRandom(1.0);
    }
}

double calculateMinimumEventTime(SimulationState* state) {
    double minTime = state->nextArrivalTimes[0];
    
    for (int i = 1; i < NUM_QUEUES; i++) {
        if (state->nextArrivalTimes[i] < minTime) {
            minTime = state->nextArrivalTimes[i];
        }
    }
    
    if (state->serviceCompletionTime < minTime) {
        minTime = state->serviceCompletionTime;
    }
    
    return minTime;
}

void takeSample(SimulationState* state, SampleData* sample) {
    sample->timestamp = state->currentTime;
    sample->sampleIndex = state->sampleCount;
    
    double totalEN = 0.0;
    double totalEW = 0.0;
    double totalArrivals = 0.0;
    double totalWaitingTime = 0.0;
    
    for (int i = 0; i < NUM_QUEUES; i++) {
        QueueState* queue = &state->queues[i];  // Declare queue variable
        
        // Finalize area calculations for current interval
        queue->EN.areaSum += (state->currentTime - queue->EN.previousTime) * queue->EN.requestCount;
        queue->EWArrivals.areaSum += (state->currentTime - queue->EWArrivals.previousTime) * queue->EWArrivals.requestCount;
        queue->EWDepartures.areaSum += (state->currentTime - queue->EWDepartures.previousTime) * queue->EWDepartures.requestCount;
        
        // Calculate E[N] for this queue
        double enQueue = (state->currentTime > 0) ? queue->EN.areaSum / state->currentTime : 0.0;
        totalEN += enQueue;
        
        // Calculate E[W] for this queue
        double ewQueue = 0.0;
        if (queue->EWArrivals.totalArrivals > 0) {
            ewQueue = queue->EWArrivals.totalWaitingTime / queue->EWArrivals.totalArrivals;
        }
        totalEW += ewQueue;
        
        sample->queueSizes[i] = queue->queueLength;
        totalArrivals += queue->EWArrivals.totalArrivals;
        totalWaitingTime += queue->EWArrivals.totalWaitingTime;
        
        // Reset for next interval
        queue->EN.previousTime = state->currentTime;
        queue->EWArrivals.previousTime = state->currentTime;
        queue->EWDepartures.previousTime = state->currentTime;
    }
    
    sample->EN = totalEN / NUM_QUEUES;
    sample->EW = totalEW / NUM_QUEUES;
    sample->measuredLambda = (state->currentTime > 0) ? totalArrivals / state->currentTime : 0.0;
    sample->measuredOccupancy = (state->currentTime > 0) ? state->totalBusyTime / state->currentTime : 0.0;
    sample->littleError = sample->EN - (sample->measuredLambda * sample->EW);
    
    state->sampleCount++;
}

void writeSampleToCSV(FILE* file, SampleData sample) {
    fprintf(file, "%.6f,%lu,%.6f,%.6f,%lu,%lu,%lu,%.6f,%.6f,%.6f\n",
            sample.timestamp, sample.sampleIndex, sample.EN, sample.EW,
            sample.queueSizes[0], sample.queueSizes[1], sample.queueSizes[2],
            sample.measuredLambda, sample.measuredOccupancy, sample.littleError);
}

void cleanupSimulationState(SimulationState* state) {
    for (int i = 0; i < NUM_QUEUES; i++) {
        free(state->queues[i].arrivalTimes);
    }
}

void runSingleSimulation(ScenarioConfig config, const char* outputFilename) {
    printf("Starting simulation for %s\n", config.scenarioName);
    
    SimulationState state;
    double arrivalRates[NUM_QUEUES];
    
    // Calculate arrival rates: lambda = rho * mu
    for (int i = 0; i < NUM_QUEUES; i++) {
        arrivalRates[i] = config.targetRho * config.serviceRates[i];
    }
    
    // Fixed seed for reproducibility
    srand(42);
    
    initializeSimulationState(&state, arrivalRates, config.serviceRates);
    
    // Create results directory
    mkdir("results", 0755);
    
    FILE* outputFile = fopen(outputFilename, "w");
    if (outputFile == NULL) {
        printf("Error opening output file: %s\n", outputFilename);
        return;
    }
    
    // Write CSV header
    fprintf(outputFile, "timestamp,sampleIndex,EN,EW,queueSize1,queueSize2,queueSize3,measuredLambda,measuredOccupancy,littleError\n");
    
    unsigned long sampleCounter = 0;
    double nextSampleTime = 0.0;
    
    // Main simulation loop - 24 hours = 86400 seconds
    while (state.currentTime < SIMULATION_TIME) {
        double nextEventTime = calculateMinimumEventTime(&state);
        
        // Process all samples until next event
        while (nextSampleTime <= nextEventTime && nextSampleTime <= SIMULATION_TIME) {
            state.currentTime = nextSampleTime;
            
            // Update busy time for sampling interval
            if (state.currentlyServingQueue != -1) {
                double timeDelta = state.currentTime - state.lastSampleTime;
                if (timeDelta > 0) {
                    state.totalBusyTime += timeDelta;
                }
            }
            
            // Take sample
            SampleData sample;
            takeSample(&state, &sample);
            writeSampleToCSV(outputFile, sample);
            
            sampleCounter++;
            nextSampleTime = sampleCounter * SAMPLING_INTERVAL;
            state.lastSampleTime = state.currentTime;
        }
        
        // Advance to next event
        state.currentTime = nextEventTime;
        
        // Update busy time for event processing
        if (state.currentlyServingQueue != -1) {
            double timeDelta = state.currentTime - state.lastSampleTime;
            if (timeDelta > 0) {
                state.totalBusyTime += timeDelta;
            }
        }
        state.lastSampleTime = state.currentTime;
        
        // Process events at current time
        for (int i = 0; i < NUM_QUEUES; i++) {
            if (fabs(state.currentTime - state.nextArrivalTimes[i]) < 1e-10) {
                processArrivalEvent(&state, i);
            }
        }
        
        if (fabs(state.currentTime - state.serviceCompletionTime) < 1e-10) {
            processDepartureEvent(&state);
        }
        
        // Progress indicator
        if (sampleCounter % 100 == 0) {
            printf("  Progress: %.1f%% (Time: %.1f/%.1f)\n", 
                   (state.currentTime / SIMULATION_TIME) * 100.0,
                   state.currentTime, SIMULATION_TIME);
        }
    }
    
    // Final sample at exactly 86400 seconds if needed
    if (state.currentTime >= SIMULATION_TIME) {
        state.currentTime = SIMULATION_TIME;
        SampleData finalSample;
        takeSample(&state, &finalSample);
        writeSampleToCSV(outputFile, finalSample);
    }
    
    fclose(outputFile);
    cleanupSimulationState(&state);
    
    printf("Simulation completed: %s (%lu samples)\n", outputFilename, sampleCounter);
}

void runBatchSimulations(void) {
    printf("Running batch simulations for 4 occupancy scenarios...\n");
    
    // All 4 occupancy scenarios
    double rhoValues[] = {0.800, 0.900, 0.950, 0.999};
    int numScenarios = sizeof(rhoValues) / sizeof(rhoValues[0]);
    
    // Single fixed seed for reproducibility
    unsigned long int seed = 42;
    
    // Service rates (mu = 1.0 for all queues)
    double serviceRates[NUM_QUEUES] = {1.0, 1.0, 1.0};
    
    // Create results directory
    mkdir("results", 0755);
    
    for (int s = 0; s < numScenarios; s++) {
        ScenarioConfig config;
        config.targetRho = rhoValues[s];
        for (int i = 0; i < NUM_QUEUES; i++) {
            config.serviceRates[i] = serviceRates[i];
        }
        config.policy = selectLargestQueuePolicy;
        config.seed = seed;
        snprintf(config.scenarioName, sizeof(config.scenarioName), "rho_%.3f", config.targetRho);
        
        char filename[100];
        snprintf(filename, sizeof(filename), "results/dados_ocupacao_%.3f.csv", config.targetRho);
        
        runSingleSimulation(config, filename);
    }
    
    printf("\nBatch simulations completed successfully!\n");
    printf("Generated files for 4 scenarios:\n");
    printf("  - dados_ocupacao_0.800.csv\n");
    printf("  - dados_ocupacao_0.900.csv\n");
    printf("  - dados_ocupacao_0.950.csv\n");
    printf("  - dados_ocupacao_0.999.csv\n");
}

int main(int argc, char* argv[]) {
    printf("Queueing System Simulator - 4 Scenarios\n");
    
    if (argc > 1 && strcmp(argv[1], "--batch") == 0) {
        runBatchSimulations();
    } else {
        printf("Usage: ./simulator --batch\n");
        printf("This will run all 4 occupancy scenarios.\n");
    }
    
    return EXIT_SUCCESS;
}
