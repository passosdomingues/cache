/**
 * @file littles_law.cpp
 * @brief Implementation of Little's Law tracker for performance validation
 */

#include "../include/littles_law.hpp"

/**
 * @brief Construct a new Littles Law Tracker object
 */
LittlesLawTracker::LittlesLawTracker()
    : previousMeasurementTime(0.0), currentRequestCount(0), 
      accumulatedArea(0.0), totalArrivals(0), totalWaitingTime(0.0) {
}

/**
 * @brief Initialize tracker to initial state
 */
void LittlesLawTracker::initialize() {
    previousMeasurementTime = 0.0;
    currentRequestCount = 0;
    accumulatedArea = 0.0;
    totalArrivals = 0;
    totalWaitingTime = 0.0;
}

/**
 * @brief Update area under curve based on current state
 * @param currentTime Current simulation time
 */
void LittlesLawTracker::updateArea(double currentTime) {
    double timeDelta = currentTime - previousMeasurementTime;
    if (timeDelta > 0) {
        accumulatedArea += timeDelta * static_cast<double>(currentRequestCount);
    }
    previousMeasurementTime = currentTime;
}

/**
 * @brief Register arrival event
 * @param currentTime Arrival timestamp
 */
void LittlesLawTracker::registerArrival(double currentTime) {
    updateArea(currentTime);
    currentRequestCount++;
    totalArrivals++;
}

/**
 * @brief Register departure event
 * @param currentTime Departure timestamp
 * @param waitingTime Waiting time of departed packet
 */
void LittlesLawTracker::registerDeparture(double currentTime, double waitingTime) {
    updateArea(currentTime);
    if (currentRequestCount > 0) {
        currentRequestCount--;
    }
    totalWaitingTime += waitingTime;
}

/**
 * @brief Compute E[N] (average number in system)
 * @param currentTime Current simulation time
 * @return double E[N] = accumulatedArea / currentTime
 */
double LittlesLawTracker::computeEN(double currentTime) const {
    if (currentTime <= 0) return 0.0;
    return accumulatedArea / currentTime;
}

/**
 * @brief Compute E[W] (average waiting time)
 * @return double E[W] = totalWaitingTime / totalArrivals
 */
double LittlesLawTracker::computeEW() const {
    if (totalArrivals == 0) return 0.0;
    return totalWaitingTime / static_cast<double>(totalArrivals);
}