/**
 * @file simulator.hpp
 * @brief Core event-driven simulation engine using a Min-Heap priority queue.
 */

#ifndef SIMULATOR_HPP
#define SIMULATOR_HPP

#include <vector>
#include <queue>
#include <string>
#include <fstream>
#include <memory>
#include "components.hpp"
#include "policies.hpp"

#include "events.hpp"

struct SimConfig {
    unsigned int seed;
    double simulationTime;
    double samplingInterval;
    std::vector<double> arrivalRates; // lambdas (rho * mu)
    std::vector<double> serviceRates; // mus
    std::string policyName;
    int queueCapacity;
    std::string outputDir;
    std::string filePrefix;
};

class Simulator {
private:
    SimConfig config;
    double currentTime;
    bool serverBusy;
    
    std::vector<std::unique_ptr<Queue>> queues;
    std::priority_queue<Event, std::vector<Event>, std::greater<Event>> eventQueue;
    std::unique_ptr<SchedulingPolicy> policyPtr;  // Polymorphic policy object
    
    unsigned long packetIdCounter;
    
    // File handles
    std::ofstream sampleFile;

public:
    Simulator(SimConfig config);
    ~Simulator();

    void run();
    
private:
    void scheduleEvent(double time, EventType type, int queueId = -1);
    void processArrival(int queueId);
    void processDeparture();
    void processSample(int sampleIdx);
    
    void initializeCSV();
    void writeSampleRow(int sampleIdx);
};

#endif // SIMULATOR_HPP