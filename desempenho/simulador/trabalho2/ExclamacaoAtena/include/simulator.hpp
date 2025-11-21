/**
 * @file simulator.hpp
 * @brief Core event-driven simulation engine using a Min-Heap priority queue
 * 
 * Implements discrete-event simulation with:
 * - Event-driven architecture using priority queue
 * - Multiple queues with configurable parameters
 * - Polymorphic scheduling policies
 * - Comprehensive performance metrics
 * - Support for exactly 3 queues system
 */

#ifndef SIMULATOR_HPP
#define SIMULATOR_HPP

#include <vector>
#include <queue>
#include <string>
#include <fstream>
#include <memory>

// Local includes
#include "components.hpp"
#include "config.hpp"
#include "events.hpp"
#include "policies/SchedulingPolicy.hpp"

/**
 * @brief Configuration structure holding all simulation parameters
 */
struct SimConfig {
    unsigned int seed;                  ///< Random number generator seed
    double simulationTime;              ///< Total simulation time
    double samplingInterval;            ///< Sampling interval for statistics
    
    std::vector<double> arrivalRates;   ///< Arrival rates for each queue (exactly 3 required)
    std::vector<double> serviceRates;   ///< Service rates for each queue (exactly 3 required)
    
    std::string policyName;             ///< Scheduling policy name
    int queueCapacity;                  ///< Queue capacity
    
    std::string outputDir;              ///< Output directory for results
    std::string filePrefix;             ///< File prefix for output files
    
    std::vector<double> cMuCosts;       ///< Cost parameters for c-mu rule
    std::vector<double> sallesCoeffs;   ///< Coefficients for Salles utility policy
    std::string matrixPath;             ///< Path to policy matrix file
};

/**
 * @brief Main Simulator Class
 */
class Simulator {
private:
    SimConfig config;                           ///< Simulation configuration
    double currentTime;                         ///< Current simulation clock
    bool serverBusy;                            ///< Server state flag
    double globalArrivalRateEstimate;           ///< Estimation for SystemState calculations
    unsigned long packetIdCounter;              ///< Unique packet ID generator
    
    std::vector<std::unique_ptr<Queue>> queues; ///< Container for exactly 3 Queue objects
    
    // Event Queue (Min-Heap based on event time)
    std::priority_queue<Event, std::vector<Event>, std::greater<Event>> eventQueue;
    
    std::shared_ptr<SchedulingPolicy> policyPtr; ///< Polymorphic pointer to active policy
    
    std::ofstream sampleFile;                   ///< CSV file handle for logging

public:
    /**
     * @brief Construct a new Simulator object
     * @param cfg Simulation configuration parameters
     * @throws std::invalid_argument if configuration doesn't specify exactly 3 queues
     */
    Simulator(SimConfig cfg);
    
    /**
     * @brief Destroy the Simulator object
     */
    ~Simulator();
    
    /**
     * @brief Run the simulation
     * @throws std::runtime_error if simulator not initialized with exactly 3 queues
     */
    void run();
    
private:
    /**
     * @brief Schedule a new event in the event queue
     * @param time Event timestamp
     * @param type Type of event
     * @param queueId Associated queue ID (0, 1, or 2 for arrivals)
     * @throws std::invalid_argument for invalid queue IDs
     */
    void scheduleEvent(double time, EventType type, int queueId = -1);
    
    /**
     * @brief Process packet arrival event
     * @param queueId ID of queue where arrival occurs (must be 0, 1, or 2)
     * @throws std::out_of_range for invalid queue IDs
     */
    void processArrival(int queueId);
    
    /**
     * @brief Process packet departure event
     */
    void processDeparture();
    
    /**
     * @brief Initialize CSV file for logging results
     */
    void initializeCSV();
    
    /**
     * @brief Process sampling event
     * @param sampleIdx Sampling index
     */
    void processSample(int sampleIdx);
    
    /**
     * @brief Write sample row to CSV file with performance metrics for 3 queues
     * @param sampleIdx Sampling index
     */
    void writeSampleRow(int sampleIdx);
};

#endif // SIMULATOR_HPP