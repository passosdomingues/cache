/**
 * @file simulator.cpp
 * @brief Implementation of the event-driven simulation engine
 */

#include "../include/simulator.hpp"
#include "../include/policies/PolicyOrchestrator.hpp"
#include "../include/policies/SallesUtilityPolicy.hpp"
#include "../include/policies/CMuRulePolicy.hpp"
#include "../include/policies/MarkovSwitchingPolicy.hpp"

#include <iostream>
#include <iomanip>
#include <numeric>
#include <cmath>
#include <sys/stat.h>
#include <cassert>

/**
 * @brief Helper function to discretize system state for logging
 * @param queues Vector of queue pointers
 * @return int Discretized state identifier
 */
static int getSystemStateId(const std::vector<std::unique_ptr<Queue>>& queues) {
    assert(queues.size() == 3 && "System must have exactly 3 queues");
    
    auto getBin = [](int len) {
        if (len <= 5) return 0;
        if (len <= 20) return 1;
        return 2;
    };
    
    int id = 0;
    int multiplier = 1;
    
    for (const auto& q : queues) {
        id += getBin(q->getLength()) * multiplier;
        multiplier *= 3;
    }
    return id;
}

Simulator::Simulator(SimConfig cfg) 
    : config(cfg), 
      currentTime(0.0), 
      serverBusy(false), 
      globalArrivalRateEstimate(0.0), 
      packetIdCounter(0)
{
    // Validate exactly 3 queues configuration
    if (config.arrivalRates.size() != 3 || config.serviceRates.size() != 3) {
        throw std::invalid_argument("Simulator requires exactly 3 arrival rates and 3 service rates");
    }

    // Create polymorphic policy object
    policyPtr = PolicyOrchestrator::createPolicy(config.policyName);

    // Initialize exactly 3 Queues
    for (int i = 0; i < 3; ++i) {
        // Create queues
        queues.push_back(std::make_unique<Queue>(i, config.queueCapacity, config.serviceRates[i]));
        
        // Setup initial arrival events
        if (config.arrivalRates[i] > 0) {
            double interarrival = -log(1.0 - (double)rand()/RAND_MAX) / config.arrivalRates[i];
            scheduleEvent(interarrival, EventType::ARRIVAL, i);
            globalArrivalRateEstimate += config.arrivalRates[i];
        }
    }

    // Configure policy-specific parameters
    if (auto p = std::dynamic_pointer_cast<SallesUtilityPolicy>(policyPtr)) {
        if (config.sallesCoeffs.size() >= 2) {
            p->setCoefficients(config.sallesCoeffs[0], config.sallesCoeffs[1]);
        }
    }
    
    if (auto p = std::dynamic_pointer_cast<CMuRulePolicy>(policyPtr)) {
        p->setCosts(config.cMuCosts);
    }
    
    if (auto p = std::dynamic_pointer_cast<MarkovSwitchingPolicy>(policyPtr)) {
        if (!config.matrixPath.empty()) {
            p->loadPolicyMatrix(config.matrixPath);
        }
    }

    // Schedule first sampling event
    scheduleEvent(config.samplingInterval, EventType::SAMPLE);
}

Simulator::~Simulator() {
    if (sampleFile.is_open()) {
        sampleFile.close();
    }
}

/**
 * @brief Initialize CSV file for logging results
 */
void Simulator::initializeCSV() {
    std::string csvPath = config.outputDir + "/" + config.filePrefix + ".csv";
    
    sampleFile.open(csvPath);
    if (!sampleFile.is_open()) {
        std::cerr << "Error: Cannot open file " << csvPath << std::endl;
        return;
    }
    
    /**
     * CSV Header with Little's Law metrics for 3 queues:
     * - Basic: time, sample_idx, total_occupancy, arrival_rate_est
     * - Queue lengths: q0_len, q1_len, q2_len
     * - Server: server_busy
     * - Little's Law per queue: q0_EN, q0_EW, q0_lambda, q1_EN, q1_EW, q1_lambda, q2_EN, q2_EW, q2_lambda
     * - System-wide Little's Law: system_EN, system_EW, system_lambda, little_error
     * - State: system_state_id, active_policy
     */
    sampleFile << "time,sample_idx,total_occupancy,arrival_rate_est,"
               << "q0_len,q1_len,q2_len,server_busy,"
               << "q0_EN,q0_EW,q0_lambda,"
               << "q1_EN,q1_EW,q1_lambda,"
               << "q2_EN,q2_EW,q2_lambda,"
               << "system_EN,system_EW,system_lambda,little_error,"
               << "system_state_id,active_policy\n";
}

/**
 * @brief Schedule a new event in the event queue
 * @param time Event timestamp
 * @param type Type of event
 * @param queueId Associated queue ID (0, 1, or 2 for arrivals)
 */
void Simulator::scheduleEvent(double time, EventType type, int queueId) {
    if (type == EventType::ARRIVAL && (queueId < 0 || queueId > 2)) {
        throw std::invalid_argument("Queue ID must be 0, 1, or 2 for arrival events");
    }
    eventQueue.push(Event(time, type, queueId));
}

/**
 * @brief Process packet arrival event
 * @param queueId ID of queue where arrival occurs (0, 1, or 2)
 */
void Simulator::processArrival(int queueId) {
    // Validate queue ID for 3-queue system
    if (queueId < 0 || queueId > 2) {
        throw std::out_of_range("Queue ID must be between 0 and 2");
    }
    
    // Schedule next arrival for this specific queue
    double interarrival = -log(1.0 - (double)rand()/RAND_MAX) / config.arrivalRates[queueId];
    scheduleEvent(currentTime + interarrival, EventType::ARRIVAL, queueId);
    
    // Create Packet
    Packet pkt(packetIdCounter++, currentTime, config.serviceRates[queueId]);
    
    // Enqueue to the specific queue
    bool enqueued = queues[queueId]->tryEnqueue(pkt);
    
    if (enqueued && !serverBusy) {
        // If server idle, schedule immediate departure check
        serverBusy = true;
        scheduleEvent(currentTime, EventType::DEPARTURE); 
    }
}

/**
 * @brief Process packet departure event
 */
void Simulator::processDeparture() {
    // Build SystemState with exactly 3 queues
    std::vector<Queue*> queuePtrs;
    for (const auto& q : queues) {
        queuePtrs.push_back(q.get());
    }
    
    SystemState state{queuePtrs, globalArrivalRateEstimate, currentTime};

    // Ask Policy which of the 3 queues to serve
    int qIndex = policyPtr->selectQueue(state);
    
    if (qIndex >= 0 && qIndex <= 2) {  // Valid queue index for 3-queue system
        serverBusy = true;
        // Remove packet from queue (result not used but operation is necessary)
        queues[qIndex]->dequeue();
        
        // Generate service time (Exponential distribution)
        double serviceTime = -log(1.0 - (double)rand()/RAND_MAX) / config.serviceRates[qIndex];
        
        // Schedule Departure Event
        scheduleEvent(currentTime + serviceTime, EventType::DEPARTURE);
    } else {
        serverBusy = false;
    }
}

/**
 * @brief Process sampling event
 * @param sampleIdx Sampling index
 */
void Simulator::processSample(int sampleIdx) {
    writeSampleRow(sampleIdx);
    
    if (currentTime + config.samplingInterval <= config.simulationTime) {
        scheduleEvent(currentTime + config.samplingInterval, EventType::SAMPLE);
    }
}

/**
 * @brief Write sample row to CSV file with performance metrics for 3 queues
 * @param sampleIdx Sampling index
 */
void Simulator::writeSampleRow(int sampleIdx) {
    if (!sampleFile.is_open()) return;

    // Validate we have exactly 3 queues
    if (queues.size() != 3) {
        std::cerr << "Error: Expected 3 queues but found " << queues.size() << std::endl;
        return;
    }

    // Extract metrics from each of the 3 queues
    const auto& tracker0 = queues[0]->getTracker();
    const auto& tracker1 = queues[1]->getTracker();
    const auto& tracker2 = queues[2]->getTracker();
    
    double q0_EN = tracker0.computeEN(currentTime);
    double q0_EW = tracker0.computeEW();
    double q0_lambda = (currentTime > 0.0) ? (static_cast<double>(tracker0.getTotalArrivals()) / currentTime) : 0.0;
    
    double q1_EN = tracker1.computeEN(currentTime);
    double q1_EW = tracker1.computeEW();
    double q1_lambda = (currentTime > 0.0) ? (static_cast<double>(tracker1.getTotalArrivals()) / currentTime) : 0.0;
    
    double q2_EN = tracker2.computeEN(currentTime);
    double q2_EW = tracker2.computeEW();
    double q2_lambda = (currentTime > 0.0) ? (static_cast<double>(tracker2.getTotalArrivals()) / currentTime) : 0.0;
    
    // System-wide metrics for 3 queues
    double systemEN = q0_EN + q1_EN + q2_EN;
    double systemLambda = q0_lambda + q1_lambda + q2_lambda;
    double weightedW = (q0_EW * q0_lambda) + (q1_EW * q1_lambda) + (q2_EW * q2_lambda);
    double systemEW = (systemLambda > 0.0) ? (weightedW / systemLambda) : 0.0;
    
    // Little's Law validation: error = |E[N] - λE[W]|
    double littleError = std::abs(systemEN - systemLambda * systemEW);
    
    // Instantaneous occupancy for state tracking (sum of 3 queues)
    int totalOccupancy = queues[0]->getLength() + queues[1]->getLength() + queues[2]->getLength();

    int stateId = getSystemStateId(queues);
    int activePolicyId = 0; 

    // Write CSV row with data from all 3 queues
    sampleFile << std::fixed << std::setprecision(4)
               << currentTime << ","
               << sampleIdx << ","
               << totalOccupancy << ","
               << globalArrivalRateEstimate << ","
               << queues[0]->getLength() << ","
               << queues[1]->getLength() << ","
               << queues[2]->getLength() << ","
               << (serverBusy ? 1 : 0) << ","
               << q0_EN << "," << q0_EW << "," << q0_lambda << ","
               << q1_EN << "," << q1_EW << "," << q1_lambda << ","
               << q2_EN << "," << q2_EW << "," << q2_lambda << ","
               << systemEN << "," << systemEW << "," << systemLambda << "," << littleError << ","
               << stateId << ","
               << activePolicyId << "\n";

    // Ensure data is written to file
    sampleFile.flush();
}

/**
 * @brief Run the main simulation loop
 */
void Simulator::run() {
    // Validate 3-queue configuration before starting
    if (queues.size() != 3) {
        throw std::runtime_error("Simulator must be initialized with exactly 3 queues");
    }
    
    initializeCSV();
    
    while (!eventQueue.empty() && currentTime <= config.simulationTime) {
        Event e = eventQueue.top();
        eventQueue.pop();
        
        currentTime = e.timestamp;
        
        switch (e.type) {
            case EventType::ARRIVAL:
                processArrival(e.queueId);
                break;
            case EventType::DEPARTURE:
                processDeparture();
                break;
            case EventType::SAMPLE:
                int idx = static_cast<int>(currentTime / config.samplingInterval);
                processSample(idx);
                break;
        }
    }
}