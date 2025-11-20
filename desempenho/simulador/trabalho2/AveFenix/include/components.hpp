/**
 * @file components.hpp
 * @brief Core simulation data structures: MeasurementWindow, LittlesLawTracker, and Queue.
 */

#ifndef COMPONENTS_HPP
#define COMPONENTS_HPP

#include <vector>
#include <deque>
#include <cmath>
#include <string>
#include "rng.hpp"

// ============================================================================
// DATA STRUCTURES
// ============================================================================

struct Packet {
    unsigned long id;
    double arrivalTime;
    double serviceStartTime;
    double departureTime;
};

#include "measurement_window.hpp"
#include "littles_law.hpp"

// ============================================================================
// DATA STRUCTURES
// ============================================================================

/**
 * @brief Represents a single queue with drop-tail logic and statistics.
 */
class Queue {
public:
    enum class DiscardPolicy { DROP_TAIL, DROP_HEAD };

private:
    int id;
    int capacity;
    double serviceRate; // mu
    DiscardPolicy discardPolicy;
    
    std::deque<Packet> buffer;
    CircularMeasurementWindow measurementWindow;
    LittlesLawTracker littlesLaw;

public:
    Queue(int id, int capacity, double mu, DiscardPolicy policy = DiscardPolicy::DROP_TAIL);

    // Core Operations
    bool tryEnqueue(Packet p);
    Packet dequeue();
    Packet peek() const;
    
    // State Queries
    bool isEmpty() const;
    int getLength() const;
    double getHeadWaitingTime(double currentTime) const;
    double getAverageWaitingTime() const; // From Window
    
    // Helpers
    void updateStats(double currentTime); // Call on events
    void registerDepartureStats(double waitTime, double currentTime);
    
    // Getters
    int getId() const { return id; }
    double getServiceRate() const { return serviceRate; }
    const LittlesLawTracker& getTracker() const { return littlesLaw; }
    
    void reset();
};

#endif // COMPONENTS_HPP