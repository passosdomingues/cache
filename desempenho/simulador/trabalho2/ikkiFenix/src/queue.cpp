#include "../include/queue.hpp"
#include <stdexcept>
#include <algorithm>

QueueState::QueueState(unsigned long capacity, DiscardPolicy policy, unsigned long maxSize)
    : currentQueueLength(0), maxObservedQueueLength(0), queueCapacity(capacity),
      totalServiceTime(0.0), totalServedRequests(0), 
      discardPolicy(policy), maxQueueSize(maxSize) {
    
    packetArrivalTimes.reserve(queueCapacity);
    measurementWindow.initialize(MEASUREMENT_WINDOW_SIZE);
}

bool QueueState::enqueuePacket(double arrivalTime) {
    // Check if queue is full
    if (currentQueueLength >= maxQueueSize) {
        if (discardPolicy == DiscardPolicy::DROP_TAIL) {
            return false; // Reject new packet
        } else if (discardPolicy == DiscardPolicy::DROP_OLDEST) {
            // Remove oldest packet to make space
            if (currentQueueLength > 0) {
                dequeuePacket(); // Remove head packet
            } else {
                return false; // Should not happen, but safety check
            }
        }
    }
    
    // Resize if needed
    if (currentQueueLength >= packetArrivalTimes.capacity()) {
        packetArrivalTimes.reserve(packetArrivalTimes.capacity() * 2);
    }
    
    // Add packet to end of queue
    packetArrivalTimes.push_back(arrivalTime);
    currentQueueLength++;
    
    // Update max observed length
    if (currentQueueLength > maxObservedQueueLength) {
        maxObservedQueueLength = currentQueueLength;
    }
    
    return true;
}

double QueueState::dequeuePacket() {
    if (currentQueueLength == 0) {
        throw std::runtime_error("Cannot dequeue from empty queue");
    }
    
    double arrivalTime = packetArrivalTimes[0];
    
    // Remove head element by shifting
    for (unsigned long i = 1; i < currentQueueLength; i++) {
        packetArrivalTimes[i - 1] = packetArrivalTimes[i];
    }
    
    packetArrivalTimes.pop_back();
    currentQueueLength--;
    totalServedRequests++;
    
    return arrivalTime;
}

double QueueState::peekHeadWaitingTime(double currentTime) const {
    if (currentQueueLength == 0) {
        return 0.0;
    }
    return currentTime - packetArrivalTimes[0];
}

void QueueState::updateNumberInSystemTracker(double currentTime, int change) {
    numberInSystemTracker.updateArea(currentTime);
    if (change > 0) {
        numberInSystemTracker.registerArrival(currentTime);
    } else if (change < 0) {
        numberInSystemTracker.registerDeparture(currentTime);
    }
}

void QueueState::updateWaitingTimeArrivalTracker(double currentTime, int change) {
    waitingTimeArrivalTracker.updateArea(currentTime);
    if (change > 0) {
        waitingTimeArrivalTracker.registerArrival(currentTime);
    }
}

void QueueState::updateWaitingTimeDepartureTracker(double currentTime, int change) {
    waitingTimeDepartureTracker.updateArea(currentTime);
    if (change > 0) {
        waitingTimeDepartureTracker.registerDeparture(currentTime);
    }
}

void QueueState::reset() {
    currentQueueLength = 0;
    maxObservedQueueLength = 0;
    packetArrivalTimes.clear();
    totalServiceTime = 0.0;
    totalServedRequests = 0;
    
    measurementWindow.initialize(MEASUREMENT_WINDOW_SIZE);
    numberInSystemTracker.initialize();
    waitingTimeArrivalTracker.initialize();
    waitingTimeDepartureTracker.initialize();
}