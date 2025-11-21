/**
 * @file components.hpp
 * @brief Core simulation data structures: MeasurementWindow, LittlesLawTracker, and Queue
 */

#ifndef COMPONENTS_HPP
#define COMPONENTS_HPP

#include <vector>
#include <deque>
#include <cmath>
#include <string>
#include "rng.hpp"

// Forward declarations
class CircularMeasurementWindow;
class LittlesLawTracker;

/**
 * @brief Packet structure representing a data packet in the simulation
 */
struct Packet {
    unsigned long id;              ///< Unique packet identifier
    double arrivalTime;            ///< Time when packet arrived
    double serviceRate;            ///< Service rate for the packet
    double serviceStartTime;       ///< Time when service started
    double departureTime;          ///< Time when service completed

    /**
     * @brief Default constructor
     */
    Packet() : id(0), arrivalTime(0), serviceRate(0), serviceStartTime(0), departureTime(0) {}

    /**
     * @brief Parameterized constructor
     * @param packetId Unique packet identifier
     * @param arrivalTime Packet arrival time
     * @param serviceRate Service rate for the packet
     */
    Packet(unsigned long packetId, double arrivalTime, double serviceRate) 
        : id(packetId), arrivalTime(arrivalTime), serviceRate(serviceRate), serviceStartTime(0), departureTime(0) {}
};

#include "measurement_window.hpp"
#include "littles_law.hpp"

/**
 * @brief Packet discard policy types
 */
enum class DiscardPolicy {
    DROP_TAIL,    ///< Reject new arrivals when queue is full
    DROP_HEAD     ///< Remove oldest packet when queue is full
};

/**
 * @brief Represents a single queue with drop-tail logic and statistics
 */
class Queue {
private:
    int id;                        ///< Queue identifier
    int capacity;                  ///< Maximum queue capacity
    double serviceRate;            ///< Service rate (mu)
    DiscardPolicy discardPolicy;   ///< Packet discard policy
    double weight;                 ///< Queue weight for weighted policies
    int utilityType;               ///< Utility type identifier
    
    std::deque<Packet> buffer;     ///< Packet buffer
    CircularMeasurementWindow measurementWindow;  ///< Measurement window for statistics
    LittlesLawTracker littlesLaw;  ///< Little's Law tracker

public:
    /**
     * @brief Construct a new Queue object
     * @param queueId Queue identifier
     * @param queueCapacity Maximum queue capacity
     * @param serviceRate Service rate (mu)
     * @param policy Packet discard policy
     * @param queueWeight Queue weight for weighted policies
     * @param queueUtilityType Utility type identifier
     */
    Queue(int queueId, int queueCapacity, double serviceRate, 
          DiscardPolicy policy = DiscardPolicy::DROP_TAIL, 
          double queueWeight = 1.0, int queueUtilityType = 0);

    /**
     * @brief Attempt to enqueue a packet
     * @param packet Packet to enqueue
     * @return bool True if packet was enqueued successfully
     */
    bool tryEnqueue(Packet packet);
    
    /**
     * @brief Dequeue a packet from the queue
     * @return Packet Dequeued packet
     */
    Packet dequeue();
    
    /**
     * @brief Peek at the front packet without removing it
     * @return Packet Front packet
     */
    Packet peek() const;
    
    /**
     * @brief Check if queue is empty
     * @return bool True if queue is empty
     */
    bool isEmpty() const;
    
    /**
     * @brief Get current queue length
     * @return int Number of packets in queue
     */
    int getLength() const;
    
    /**
     * @brief Get waiting time of head packet
     * @param currentTime Current simulation time
     * @return double Waiting time of head packet
     */
    double getHeadWaitingTime(double currentTime) const;
    
    /**
     * @brief Get average waiting time from measurement window
     * @return double Average waiting time
     */
    double getAverageWaitingTime() const;
    
    /**
     * @brief Update statistics with current time
     * @param currentTime Current simulation time
     */
    void updateStats(double currentTime);
    
    /**
     * @brief Register departure statistics
     * @param waitTime Waiting time of departed packet
     * @param currentTime Current simulation time
     */
    void registerDepartureStats(double waitTime, double currentTime);
    
    /**
     * @brief Get queue identifier
     * @return int Queue ID
     */
    int getId() const { return id; }
    
    /**
     * @brief Get service rate
     * @return double Service rate (mu)
     */
    double getServiceRate() const { return serviceRate; }
    
    /**
     * @brief Get queue weight
     * @return double Queue weight
     */
    double getWeight() const { return weight; }
    
    /**
     * @brief Get utility type
     * @return int Utility type identifier
     */
    int getUtilityType() const { return utilityType; }
    
    /**
     * @brief Get Little's Law tracker
     * @return const LittlesLawTracker& Little's Law tracker reference
     */
    const LittlesLawTracker& getTracker() const { return littlesLaw; }
    
    /**
     * @brief Reset queue to initial state
     */
    void reset();
};

#endif // COMPONENTS_HPP