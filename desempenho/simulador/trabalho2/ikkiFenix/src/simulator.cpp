/**
 * @file simulator.cpp
 * @brief Implementation of the event loop and file I/O.
 */

#include "../include/simulator.hpp"
#include <iostream>
#include <iomanip>
#include <sys/stat.h>
#include <sys/types.h>

Simulator::Simulator(SimConfig cfg) 
    : config(cfg), currentTime(0.0), serverBusy(false), packetIdCounter(0) {
    
    RNG::setSeed(config.seed);
    policy = Policies::getPolicyByName(config.policyName);

    // Initialize Queues
    for (size_t i = 0; i < config.serviceRates.size(); ++i) {
        queues.push_back(new Queue((int)i, config.queueCapacity, config.serviceRates[i]));
    }

    // Initial Events
    for (size_t i = 0; i < queues.size(); ++i) {
        double firstArrival = RNG::generateExponentialRandom(config.arrivalRates[i]);
        scheduleEvent(firstArrival, EventType::ARRIVAL, (int)i);
    }
    scheduleEvent(config.samplingInterval, EventType::SAMPLE);
}

Simulator::~Simulator() {
    for (auto q : queues) delete q;
    if (sampleFile.is_open()) sampleFile.close();
}

void Simulator::scheduleEvent(double time, EventType type, int queueId) {
    if (time > config.simulationTime && type != EventType::SAMPLE) return;
    Event e = {time, type, queueId, 0};
    eventQueue.push(e);
}

void Simulator::initializeCSV() {
    std::string path = config.outputDir + "/" + config.filePrefix + ".csv";
    sampleFile.open(path);
    sampleFile << "timestamp,sample_idx,system_occupancy,avg_wait_error,q0_len,q1_len,q2_len,server_busy,little_error\n";
}

void Simulator::processArrival(int queueId) {
    // Schedule next arrival for this queue
    double nextInterarrival = RNG::generateExponentialRandom(config.arrivalRates[queueId]);
    scheduleEvent(currentTime + nextInterarrival, EventType::ARRIVAL, queueId);

    // Create packet
    Packet p;
    p.id = ++packetIdCounter;
    p.arrivalTime = currentTime;

    // Update Queue State (Area accumulation)
    queues[queueId]->updateStats(currentTime);

    // Try enqueue
    if (queues[queueId]->tryEnqueue(p)) {
        // If server is free, we don't serve immediately here for M/M/3 logic
        // In a polling system, we need a trigger. 
        // If server is IDLE, we can try to schedule a service immediately via a "Dummy" departure check?
        // Or strictly wait for Departure events.
        // Standard logic: If server idle, pick a queue immediately.
        if (!serverBusy) {
            processDeparture(); // Triggers service start logic
        }
    }
}

void Simulator::processDeparture() {
    // 1. If server was busy, it is now finishing a job.
    // But 'processDeparture' usually means "Service Completed".
    
    // Check who to serve next using Policy
    int bestQueueId = policy(queues, currentTime);

    if (bestQueueId != -1) {
        // Server becomes/stays busy
        serverBusy = true;
        
        // Dequeue
        Queue* q = queues[bestQueueId];
        Packet p = q->dequeue();
        
        // Calculate service time
        double serviceTime = RNG::generateExponentialRandom(q->getServiceRate());
        p.serviceStartTime = currentTime;
        p.departureTime = currentTime + serviceTime;
        
        // Register stats
        double waitTime = currentTime - p.arrivalTime;
        q->registerDepartureStats(waitTime, currentTime);

        // Schedule this packet's departure (server free event)
        scheduleEvent(currentTime + serviceTime, EventType::DEPARTURE);
    } else {
        serverBusy = false;
    }
}

void Simulator::processSample(int sampleIdx) {
    writeSampleRow(sampleIdx);
    scheduleEvent(currentTime + config.samplingInterval, EventType::SAMPLE);
}

void Simulator::writeSampleRow(int sampleIdx) {
    double totalOccupancy = 0;
    double maxLittleError = 0;
    
    for (auto q : queues) {
        // Update tracking to current time before reading
        q->updateStats(currentTime); 
        const auto& tracker = q->getTracker();
        double En = tracker.computeEN(currentTime);
        totalOccupancy += En;
        
        // Calculate Little's Law Error: |E[N] - lambda * E[W]|
        // lambda = arrivals / time
        double Ew = tracker.computeEW();
        double lambda = (currentTime > 0) ? (double)tracker.getTotalArrivals() / currentTime : 0.0;
        double err = std::abs(En - (lambda * Ew));
        
        if (err > maxLittleError) maxLittleError = err;
    }

    if (sampleFile.is_open()) {
        sampleFile << std::fixed << std::setprecision(4)
                   << currentTime << "," 
                   << sampleIdx << ","
                   << totalOccupancy << ","
                   << 0.0 << "," // placeholder
                   << queues[0]->getLength() << ","
                   << queues[1]->getLength() << ","
                   << queues[2]->getLength() << ","
                   << (serverBusy ? 1 : 0) << ","
                   << maxLittleError << "\n";
    }
}

void Simulator::run() {
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
                // Index calculation based on time
                processSample((int)(currentTime / config.samplingInterval));
                break;
        }
    }
}