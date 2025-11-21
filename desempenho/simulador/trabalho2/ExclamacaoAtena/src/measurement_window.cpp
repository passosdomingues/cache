/**
 * @file measurement_window.cpp
 * @brief Implementation of circular measurement window
 */

#include "../include/measurement_window.hpp"
#include <stdexcept>

/**
 * @brief Construct a new Circular Measurement Window object
 */
CircularMeasurementWindow::CircularMeasurementWindow()
    : headIndex(0), tailIndex(0), currentSize(0), maxSize(0),
      sumArrivalTimestamps(0.0), sumWaitingTimes(0.0), totalPacketsInWindow(0) {
}

/**
 * @brief Initialize measurement window
 * @param size Maximum window size
 */
void CircularMeasurementWindow::initialize(int size) {
    maxSize = size;
    arrivalTimestamps.resize(maxSize, 0.0);
    departureTimestamps.resize(maxSize, 0.0);
    waitingTimes.resize(maxSize, 0.0);
    
    headIndex = 0;
    tailIndex = 0;
    currentSize = 0;
    sumArrivalTimestamps = 0.0;
    sumWaitingTimes = 0.0;
    totalPacketsInWindow = 0;
}

/**
 * @brief Add packet metadata to window
 * @param arrivalTime Packet arrival timestamp
 * @param departureTime Packet departure timestamp
 * @param waitingTime Calculated waiting time
 */
void CircularMeasurementWindow::addPacket(double arrivalTime, double departureTime, double waitingTime) {
    // If buffer is full, remove oldest element
    if (currentSize == maxSize) {
        sumArrivalTimestamps -= arrivalTimestamps[headIndex];
        sumWaitingTimes -= waitingTimes[headIndex];
        totalPacketsInWindow--;
        
        headIndex = (headIndex + 1) % maxSize;
        currentSize--;
    }
    
    // Add new element
    arrivalTimestamps[tailIndex] = arrivalTime;
    departureTimestamps[tailIndex] = departureTime;
    waitingTimes[tailIndex] = waitingTime;
    
    sumArrivalTimestamps += arrivalTime;
    sumWaitingTimes += waitingTime;
    totalPacketsInWindow++;
    
    tailIndex = (tailIndex + 1) % maxSize;
    currentSize++;
}

/**
 * @brief Compute average waiting time in window
 * @return double Average waiting time
 */
double CircularMeasurementWindow::computeWindowAverageWaitingTime() const {
    if (totalPacketsInWindow == 0) return 0.0;
    return sumWaitingTimes / static_cast<double>(totalPacketsInWindow);
}

/**
 * @brief Compute average arrival time in window
 * @return double Average arrival time
 */
double CircularMeasurementWindow::computeWindowAverageArrivalTime() const {
    if (totalPacketsInWindow == 0) return 0.0;
    return sumArrivalTimestamps / static_cast<double>(totalPacketsInWindow);
}

/**
 * @brief Clear all window data
 */
void CircularMeasurementWindow::clear() {
    initialize(maxSize);
}