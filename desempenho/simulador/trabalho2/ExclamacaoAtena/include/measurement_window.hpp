#ifndef MEASUREMENT_WINDOW_HPP
#define MEASUREMENT_WINDOW_HPP

#include <vector>

#define MEASUREMENT_WINDOW_SIZE 1000

/**
 * @brief Circular buffer for packet metadata (preserves original field names)
 */
class CircularMeasurementWindow {
private:
    std::vector<double> arrivalTimestamps;
    std::vector<double> departureTimestamps;
    std::vector<double> waitingTimes;
    int headIndex;
    int tailIndex;
    int currentSize;
    int maxSize;
    
    // Real-time metadata aggregates
    double sumArrivalTimestamps;
    double sumWaitingTimes;
    int totalPacketsInWindow;

public:
    CircularMeasurementWindow();
    
    /**
     * @brief Initialize measurement window
     * @param size Maximum window size
     */
    void initialize(int size);
    
    /**
     * @brief Add packet metadata to window
     * @param arrivalTime Packet arrival timestamp
     * @param departureTime Packet departure timestamp
     * @param waitingTime Calculated waiting time
     */
    void addPacket(double arrivalTime, double departureTime, double waitingTime);
    
    // Getters (preserve original field names)
    double getSumArrivalTimestamps() const { return sumArrivalTimestamps; }
    double getSumWaitingTimes() const { return sumWaitingTimes; }
    int getTotalPacketsInWindow() const { return totalPacketsInWindow; }
    
    /**
     * @brief Compute average waiting time in window
     * @return double Average waiting time
     */
    double computeWindowAverageWaitingTime() const;
    
    /**
     * @brief Compute average arrival time in window
     * @return double Average arrival time
     */
    double computeWindowAverageArrivalTime() const;
    
    /**
     * @brief Clear all window data
     */
    void clear();
};

#endif // MEASUREMENT_WINDOW_HPP