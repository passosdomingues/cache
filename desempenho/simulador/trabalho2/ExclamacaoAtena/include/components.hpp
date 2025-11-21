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
    double serviceRate; // Adicionado para suportar o argumento do simulador
    double serviceStartTime;
    double departureTime;

    // Default Constructor
    Packet() : id(0), arrivalTime(0), serviceRate(0), serviceStartTime(0), departureTime(0) {}

    // Parameterized Constructor (Corrigindo o erro de no matching function)
    Packet(unsigned long id_, double arrTime, double sRate) 
        : id(id_), arrivalTime(arrTime), serviceRate(sRate), serviceStartTime(0), departureTime(0) {}
};

#include "measurement_window.hpp"
#include "littles_law.hpp"

// ============================================================================
// QUEUE CLASS
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
    double weight;
    int utilityType;
    
    std::deque<Packet> buffer;
    CircularMeasurementWindow measurementWindow;
    LittlesLawTracker littlesLaw;

public:
    Queue(int id_, int capacity_, double mu, DiscardPolicy policy = DiscardPolicy::DROP_TAIL, 
          unsigned long maxSize = 1000, double weight_ = 1.0, int utilityType_ = 0);

    // Core Operations
    bool tryEnqueue(Packet p); // Renomeado/Verificado: é tryEnqueue, não enqueue
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
    double getWeight() const { return weight; }
    int getUtilityType() const { return utilityType; }
    const LittlesLawTracker& getTracker() const { return littlesLaw; }
    
    void reset();
};

#endif // COMPONENTS_HPP