/**
 * @file queue.hpp
 * @brief Queue state container with performance tracking
 * 
 * Maintains queue state including:
 * - Current and maximum queue lengths
 * - Packet arrival timestamps
 * - Performance metrics and trackers
 * - Configuration parameters
 */

#ifndef QUEUE_HPP
#define QUEUE_HPP

#include "measurement_window.hpp"
#include "littles_law.hpp"
#include <vector>
#include <string>

/**
 * @brief Packet discard policy types
 */
enum class DiscardPolicy {
    DROP_TAIL,    ///< Reject new arrivals when queue is full
    DROP_OLDEST   ///< Remove oldest packet when queue is full
};

/**
 * @brief Queue state container with performance tracking
 */
class QueueState {
private:
    // Core queue state
    unsigned long currentQueueLength;        ///< Current number of packets in queue
    std::vector<double> packetArrivalTimes;  ///< Timestamps of packet arrivals
    unsigned long maxObservedQueueLength;    ///< Maximum observed queue length
    unsigned long queueCapacity;             ///< Maximum queue capacity
    
    // Measurement and analytics
    CircularMeasurementWindow measurementWindow;  ///< Sliding window for measurements
    LittlesLawTracker numberInSystemTracker;      ///< Tracks number in system for Little's Law
    LittlesLawTracker waitingTimeArrivalTracker;  ///< Tracks waiting times at arrival
    LittlesLawTracker waitingTimeDepartureTracker;///< Tracks waiting times at departure
    
    // Performance statistics
    double totalServiceTime;                 ///< Cumulative service time
    unsigned long totalServedRequests;       ///< Total packets served
    
    // Configuration
    DiscardPolicy discardPolicy;             ///< Packet discard policy
    unsigned long maxQueueSize;              ///< Maximum queue size
    double weight;                           ///< Queue weight for weighted policies
    int utilityType;                         ///< Utility type (0: Best Effort, 1: Voice, 2: Video, etc.)

public:
    /**
     * @brief Construct a new Queue State object
     * @param capacity Initial queue capacity
     * @param policy Queue discard policy
     * @param maxSize Maximum queue size
     * @param weight Queue weight for weighted policies
     * @param utilityType Utility type for utility-based policies
     */
    QueueState(unsigned long capacity = 100, 
               DiscardPolicy policy = DiscardPolicy::DROP_TAIL,
               unsigned long maxSize = 1000,
               double weight = 1.0,
               int utilityType = 0);
    
    /**
     * @brief Add packet to queue
     * @param arrivalTime Packet arrival timestamp
     * @return bool True if packet was enqueued successfully
     */
    bool enqueuePacket(double arrivalTime);
    
    /**
     * @brief Remove packet from head of queue
     * @return double Arrival time of dequeued packet
     * @throws std::runtime_error if queue is empty
     */
    double dequeuePacket();
    
    /**
     * @brief Get waiting time of head packet
     * @param currentTime Current simulation time
     * @return double Waiting time of head packet
     */
    double peekHeadWaitingTime(double currentTime) const;
    
    /**
     * @brief Get current queue length
     * @return unsigned long Current number of packets in queue
     */
    unsigned long getCurrentQueueLength() const { return currentQueueLength; }
    
    /**
     * @brief Get maximum observed queue length
     * @return unsigned long Maximum observed length
     */
    unsigned long getMaxObservedQueueLength() const { return maxObservedQueueLength; }
    
    /**
     * @brief Get total served requests
     * @return unsigned long Total packets served
     */
    unsigned long getTotalServedRequests() const { return totalServedRequests; }
    
    /**
     * @brief Get total service time
     * @return double Cumulative service time
     */
    double getTotalServiceTime() const { return totalServiceTime; }
    
    /**
     * @brief Get queue weight
     * @return double Queue weight for weighted policies
     */
    double getWeight() const { return weight; }
    
    /**
     * @brief Get utility type
     * @return int Utility type identifier
     */
    int getUtilityType() const { return utilityType; }
    
    /**
     * @brief Set queue weight
     * @param weight New weight value
     */
    void setWeight(double weight) { this->weight = weight; }
    
    /**
     * @brief Set utility type
     * @param utilityType New utility type
     */
    void setUtilityType(int utilityType) { this->utilityType = utilityType; }
    
    /**
     * @brief Get measurement window reference
     * @return const CircularMeasurementWindow& Measurement window
     */
    const CircularMeasurementWindow& getMeasurementWindow() const { return measurementWindow; }
    
    /**
     * @brief Get number in system tracker
     * @return const LittlesLawTracker& Number in system tracker
     */
    const LittlesLawTracker& getNumberInSystemTracker() const { return numberInSystemTracker; }
    
    /**
     * @brief Get waiting time arrival tracker
     * @return const LittlesLawTracker& Waiting time arrival tracker
     */
    const LittlesLawTracker& getWaitingTimeArrivalTracker() const { return waitingTimeArrivalTracker; }
    
    /**
     * @brief Get waiting time departure tracker
     * @return const LittlesLawTracker& Waiting time departure tracker
     */
    const LittlesLawTracker& getWaitingTimeDepartureTracker() const { return waitingTimeDepartureTracker; }
    
    /**
     * @brief Update number in system tracker
     * @param currentTime Current simulation time
     * @param change Change in number of requests (+1 for arrival, -1 for departure)
     */
    void updateNumberInSystemTracker(double currentTime, int change);
    
    /**
     * @brief Update waiting time tracker at arrival
     * @param currentTime Current simulation time
     * @param change Change indicator
     */
    void updateWaitingTimeArrivalTracker(double currentTime, int change);
    
    /**
     * @brief Update waiting time tracker at departure
     * @param currentTime Current simulation time
     * @param change Change indicator
     */
    void updateWaitingTimeDepartureTracker(double currentTime, int change);
    
    /**
     * @brief Reset queue to initial state
     */
    void reset();
};

#endif // QUEUE_HPP