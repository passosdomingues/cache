/**
 * @file littles_law.hpp
 * @brief Tracks components for Little's Law validation
 * 
 * Maintains running calculations for:
 * - E[N]: Average number of requests in system
 * - E[W]: Average waiting time
 * - Lambda: Arrival rate
 * Used to validate Little's Law: E[N] = Lambda * E[W]
 */

#ifndef LITTLES_LAW_HPP
#define LITTLES_LAW_HPP

class LittlesLawTracker {
private:
    double previousMeasurementTime;        ///< Last time measurement was taken
    unsigned long currentRequestCount;     ///< Current number of requests in system
    double accumulatedArea;                ///< Integrated area under queue length curve
    unsigned long totalArrivals;           ///< Total number of arrivals
    double totalWaitingTime;               ///< Cumulative waiting time of all requests

public:
    /**
     * @brief Construct a new Littles Law Tracker object
     */
    LittlesLawTracker();
    
    /**
     * @brief Initialize tracker to initial state
     */
    void initialize();
    
    /**
     * @brief Update area under curve based on current state
     * @param currentTime Current simulation time
     */
    void updateArea(double currentTime);
    
    /**
     * @brief Register arrival event
     * @param currentTime Arrival timestamp
     */
    void registerArrival(double currentTime);
    
    /**
     * @brief Register departure event
     * @param currentTime Departure timestamp
     * @param waitingTime Waiting time of departed packet
     */
    void registerDeparture(double currentTime, double waitingTime = 0.0);
    
    /**
     * @brief Compute E[N] (average number in system)
     * @param currentTime Current simulation time
     * @return double E[N] = accumulatedArea / currentTime
     */
    double computeEN(double currentTime) const;
    
    /**
     * @brief Compute E[W] (average waiting time)
     * @return double E[W] = totalWaitingTime / totalArrivals
     */
    double computeEW() const;
    
    /**
     * @brief Get total number of arrivals
     * @return unsigned long Total arrivals count
     */
    unsigned long getTotalArrivals() const { return totalArrivals; }
    
    /**
     * @brief Get total waiting time
     * @return double Cumulative waiting time
     */
    double getTotalWaitingTime() const { return totalWaitingTime; }
    
    /**
     * @brief Get current request count
     * @return unsigned long Current number of requests in system
     */
    unsigned long getCurrentRequestCount() const { return currentRequestCount; }
    
    /**
     * @brief Get accumulated area under curve
     * @return double Total accumulated area
     */
    double getAccumulatedArea() const { return accumulatedArea; }
};

#endif // LITTLES_LAW_HPP