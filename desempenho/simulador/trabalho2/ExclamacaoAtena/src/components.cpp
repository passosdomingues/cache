/**
 * @file components.cpp
 * @brief Implementation of modular simulation components.
 */

#include "../include/components.hpp"
#include <numeric>
#include <iostream>

// MeasurementWindow and LittlesLawTracker are implemented in their own files.

// ============================================================================
// QUEUE
// ============================================================================

Queue::Queue(int id_, int capacity_, double mu, DiscardPolicy policy, unsigned long maxSize, double weight_, int utilityType_)
    : id(id_), capacity(capacity_), serviceRate(mu), discardPolicy(policy), weight(weight_), utilityType(utilityType_) {
    measurementWindow.initialize(1000); // Default window size
}

bool Queue::tryEnqueue(Packet p) {
    if (buffer.size() < (size_t)capacity) {
        buffer.push_back(p);
        littlesLaw.registerArrival(p.arrivalTime);
        return true;
    }
    
    // Discard logic
    if (discardPolicy == DiscardPolicy::DROP_TAIL) {
        return false; // Reject new packet
    } else if (discardPolicy == DiscardPolicy::DROP_HEAD) {
        // Drop oldest, accept new
        if (!buffer.empty()) {
            // Note: Dropped packet doesn't count as departure for Little's Law W calc typically,
            // but we must adjust occupancy.
            buffer.pop_front(); 
            // Re-add new
            buffer.push_back(p);
            // Note: Little's Law tracking in lossy systems is complex; 
            // simplistic approach: ignore dropped for stats or count as 0 wait?
            // For this sim, we just swap the buffer item.
            return true;
        }
    }
    return false;
}

Packet Queue::dequeue() {
    if (buffer.empty()) return {};
    Packet p = buffer.front();
    buffer.pop_front();
    return p;
}

Packet Queue::peek() const {
    if (buffer.empty()) return {};
    return buffer.front();
}

bool Queue::isEmpty() const {
    return buffer.empty();
}

int Queue::getLength() const {
    return (int)buffer.size();
}

double Queue::getHeadWaitingTime(double currentTime) const {
    if (buffer.empty()) return 0.0;
    return currentTime - buffer.front().arrivalTime;
}

double Queue::getAverageWaitingTime() const {
    return measurementWindow.computeWindowAverageWaitingTime();
}

void Queue::updateStats(double currentTime) {
    littlesLaw.updateArea(currentTime);
}

void Queue::registerDepartureStats(double waitTime, double currentTime) {
    measurementWindow.addPacket(currentTime - waitTime, currentTime, waitTime); 
    littlesLaw.registerDeparture(currentTime, waitTime);
}

void Queue::reset() {
    buffer.clear();
    measurementWindow.clear();
    littlesLaw.initialize();
}