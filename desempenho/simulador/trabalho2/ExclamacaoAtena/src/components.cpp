/**
 * @file components.cpp
 * @brief Implementation of modular simulation components
 */

#include "../include/components.hpp"
#include <numeric>
#include <iostream>

/**
 * @brief Construct a new Queue object
 * @param queueId Queue identifier
 * @param queueCapacity Maximum queue capacity
 * @param serviceRate Service rate (mu)
 * @param policy Packet discard policy
 * @param queueWeight Queue weight for weighted policies
 * @param queueUtilityType Utility type identifier
 */
Queue::Queue(int queueId, int queueCapacity, double serviceRate, DiscardPolicy policy, 
             double queueWeight, int queueUtilityType)
    : id(queueId), capacity(queueCapacity), serviceRate(serviceRate), 
      discardPolicy(policy), weight(queueWeight), utilityType(queueUtilityType) {
    measurementWindow.initialize(1000); // Default window size
}

/**
 * @brief Attempt to enqueue a packet
 * @param packet Packet to enqueue
 * @return bool True if packet was enqueued successfully
 */
bool Queue::tryEnqueue(Packet packet) {
    if (buffer.size() < static_cast<size_t>(capacity)) {
        buffer.push_back(packet);
        littlesLaw.registerArrival(packet.arrivalTime);
        return true;
    }
    
    // Discard logic
    if (discardPolicy == DiscardPolicy::DROP_TAIL) {
        return false; // Reject new packet
    } else if (discardPolicy == DiscardPolicy::DROP_HEAD) {
        // Drop oldest, accept new
        if (!buffer.empty()) {
            buffer.pop_front(); 
            buffer.push_back(packet);
            return true;
        }
    }
    return false;
}

/**
 * @brief Dequeue a packet from the queue
 * @return Packet Dequeued packet
 */
Packet Queue::dequeue() {
    if (buffer.empty()) return Packet();
    Packet packet = buffer.front();
    buffer.pop_front();
    return packet;
}

/**
 * @brief Peek at the front packet without removing it
 * @return Packet Front packet
 */
Packet Queue::peek() const {
    if (buffer.empty()) return Packet();
    return buffer.front();
}

/**
 * @brief Check if queue is empty
 * @return bool True if queue is empty
 */
bool Queue::isEmpty() const {
    return buffer.empty();
}

/**
 * @brief Get current queue length
 * @return int Number of packets in queue
 */
int Queue::getLength() const {
    return static_cast<int>(buffer.size());
}

/**
 * @brief Get waiting time of head packet
 * @param currentTime Current simulation time
 * @return double Waiting time of head packet
 */
double Queue::getHeadWaitingTime(double currentTime) const {
    if (buffer.empty()) return 0.0;
    return currentTime - buffer.front().arrivalTime;
}

/**
 * @brief Get average waiting time from measurement window
 * @return double Average waiting time
 */
double Queue::getAverageWaitingTime() const {
    return measurementWindow.computeWindowAverageWaitingTime();
}

/**
 * @brief Update statistics with current time
 * @param currentTime Current simulation time
 */
void Queue::updateStats(double currentTime) {
    littlesLaw.updateArea(currentTime);
}

/**
 * @brief Register departure statistics
 * @param waitTime Waiting time of departed packet
 * @param currentTime Current simulation time
 */
void Queue::registerDepartureStats(double waitTime, double currentTime) {
    measurementWindow.addPacket(currentTime - waitTime, currentTime, waitTime); 
    littlesLaw.registerDeparture(currentTime, waitTime);
}

/**
 * @brief Reset queue to initial state
 */
void Queue::reset() {
    buffer.clear();
    measurementWindow.clear();
    littlesLaw.initialize();
}