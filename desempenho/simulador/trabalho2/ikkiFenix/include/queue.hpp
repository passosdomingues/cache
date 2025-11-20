#ifndef QUEUE_HPP
#define QUEUE_HPP

#include "measurement_window.hpp"
#include "littles_law.hpp"
#include <vector>
#include <string>

/**
 * @brief Discard policy types
 */
enum class DiscardPolicy {
    DROP_TAIL,    // Reject new arrivals when queue is full
    DROP_OLDEST   // Remove oldest packet when queue is full
};

/**
 * @brief Queue state container with exact field preservation
 */
class QueueState {
private:
    // Core queue state (preserved from original C struct)
    unsigned long currentQueueLength;
    std::vector<double> packetArrivalTimes;
    unsigned long maxObservedQueueLength;
    unsigned long queueCapacity;
    
    // Measurement and analytics
    CircularMeasurementWindow measurementWindow;
    LittlesLawTracker numberInSystemTracker;
    LittlesLawTracker waitingTimeArrivalTracker;
    LittlesLawTracker waitingTimeDepartureTracker;
    
    // Performance statistics
    double totalServiceTime;
    unsigned long totalServedRequests;
    
    // Configuration
    DiscardPolicy discardPolicy;
    unsigned long maxQueueSize;

public:
    /**
     * @brief Construct a new Queue State object
     * @param capacity Initial queue capacity
     * @param discardPolicy Queue discard policy
     * @param maxSize Maximum queue size
     */
    QueueState(unsigned long capacity = 100, 
               DiscardPolicy discardPolicy = DiscardPolicy::DROP_TAIL,
               unsigned long maxSize = 1000);
    
    /**
     * @brief Add packet to queue
     * @param arrivalTime Packet arrival timestamp
     * @return bool True if packet was enqueued successfully
     */
    bool enqueuePacket(double arrivalTime);
    
    /**
     * @brief Remove packet from head of queue
     * @return double Arrival time of dequeued packet
     */
    double dequeuePacket();
    
    /**
     * @brief Get waiting time of head packet
     * @param currentTime Current simulation time
     * @return double Waiting time of head packet
     */
    double peekHeadWaitingTime(double currentTime) const;
    
    // Getters
    unsigned long getCurrentQueueLength() const { return currentQueueLength; }
    unsigned long getMaxObservedQueueLength() const { return maxObservedQueueLength; }
    unsigned long getTotalServedRequests() const { return totalServedRequests; }
    double getTotalServiceTime() const { return totalServiceTime; }
    
    // Trackers access
    const CircularMeasurementWindow& getMeasurementWindow() const { return measurementWindow; }
    const LittlesLawTracker& getNumberInSystemTracker() const { return numberInSystemTracker; }
    const LittlesLawTracker& getWaitingTimeArrivalTracker() const { return waitingTimeArrivalTracker; }
    const LittlesLawTracker& getWaitingTimeDepartureTracker() const { return waitingTimeDepartureTracker; }
    
    // Update methods for trackers
    void updateNumberInSystemTracker(double currentTime, int change);
    void updateWaitingTimeArrivalTracker(double currentTime, int change);
    void updateWaitingTimeDepartureTracker(double currentTime, int change);
    
    /**
     * @brief Reset queue to initial state
     */
    void reset();
};

#endif // QUEUE_HPP