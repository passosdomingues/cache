#include "../include/measurement_window.hpp"
#include <stdexcept>

CircularMeasurementWindow::CircularMeasurementWindow()
    : headIndex(0), tailIndex(0), currentSize(0), maxSize(0),
      sumArrivalTimestamps(0.0), sumWaitingTimes(0.0), totalPacketsInWindow(0) {
}

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

double CircularMeasurementWindow::computeWindowAverageWaitingTime() const {
    if (totalPacketsInWindow == 0) return 0.0;
    return sumWaitingTimes / totalPacketsInWindow;
}

double CircularMeasurementWindow::computeWindowAverageArrivalTime() const {
    if (totalPacketsInWindow == 0) return 0.0;
    return sumArrivalTimestamps / totalPacketsInWindow;
}

void CircularMeasurementWindow::clear() {
    initialize(maxSize);
}