/**
 * @file measurement_window.hpp
 * @brief Circular buffer for packet metadata and statistics
 */

#ifndef MEASUREMENT_WINDOW_HPP
#define MEASUREMENT_WINDOW_HPP

#include <vector>

#define MEASUREMENT_WINDOW_SIZE 1000  ///< Default measurement window size

/**
 * @brief Circular buffer for packet metadata and statistics
 */
class CircularMeasurementWindow {
private:
    std::vector<double> arrivalTimestamps;    ///< Packet arrival timestamps
    std::vector<double> departureTimestamps;  ///< Packet departure timestamps
    std::vector<double> waitingTimes;         ///< Packet waiting times
    int headIndex;                            ///< Window head index
    int tailIndex;                            ///< Window tail index
    int currentSize;                          ///< Current window size
    int maxSize;                              ///< Maximum window size
    
    // Real-time metadata aggregates
    double sumArrivalTimestamps;  ///< Sum of arrival timestamps in window
    double sumWaitingTimes;       ///< Sum of waiting times in window
    int totalPacketsInWindow;     ///< Total packets currently in window

public:
    /**
     * @brief Construct a new Circular Measurement Window object
     */
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
    
    /**
     * @brief Get sum of arrival timestamps in window
     * @return double Sum of arrival timestamps
     */
    double getSumArrivalTimestamps() const { return sumArrivalTimestamps; }
    
    /**
     * @brief Get sum of waiting times in window
     * @return double Sum of waiting times
     */
    double getSumWaitingTimes() const { return sumWaitingTimes; }
    
    /**
     * @brief Get total packets currently in window
     * @return int Total packets in window
     */
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