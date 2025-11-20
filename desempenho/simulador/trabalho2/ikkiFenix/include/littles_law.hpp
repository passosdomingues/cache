#ifndef LITTLES_LAW_HPP
#define LITTLES_LAW_HPP

/**
 * @brief Tracks Little's Law components for performance validation
 */
class LittlesLawTracker {
private:
    double previousMeasurementTime;
    unsigned long currentRequestCount;
    double accumulatedArea;
    unsigned long totalArrivals;
    double totalWaitingTime;

public:
    LittlesLawTracker();
    
    /**
     * @brief Initialize tracker
     */
    void initialize();
    
    /**
     * @brief Update area under curve
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
     * @return double E[N] value
     */
    double computeEN(double currentTime) const;
    
    /**
     * @brief Compute E[W] (average waiting time)
     * @return double E[W] value
     */
    double computeEW() const;
    
    // Getters
    unsigned long getTotalArrivals() const { return totalArrivals; }
    double getTotalWaitingTime() const { return totalWaitingTime; }
    unsigned long getCurrentRequestCount() const { return currentRequestCount; }
    double getAccumulatedArea() const { return accumulatedArea; }
};

#endif // LITTLES_LAW_HPP