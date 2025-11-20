#include "../include/littles_law.hpp"

LittlesLawTracker::LittlesLawTracker()
    : previousMeasurementTime(0.0), currentRequestCount(0), 
      accumulatedArea(0.0), totalArrivals(0), totalWaitingTime(0.0) {
}

void LittlesLawTracker::initialize() {
    previousMeasurementTime = 0.0;
    currentRequestCount = 0;
    accumulatedArea = 0.0;
    totalArrivals = 0;
    totalWaitingTime = 0.0;
}

void LittlesLawTracker::updateArea(double currentTime) {
    double timeDelta = currentTime - previousMeasurementTime;
    if (timeDelta > 0) {
        accumulatedArea += timeDelta * currentRequestCount;
    }
    previousMeasurementTime = currentTime;
}

void LittlesLawTracker::registerArrival(double currentTime) {
    updateArea(currentTime);
    currentRequestCount++;
    totalArrivals++;
}

void LittlesLawTracker::registerDeparture(double currentTime, double waitingTime) {
    updateArea(currentTime);
    if (currentRequestCount > 0) {
        currentRequestCount--;
    }
    totalWaitingTime += waitingTime;
}

double LittlesLawTracker::computeEN(double currentTime) const {
    if (currentTime <= 0) return 0.0;
    return accumulatedArea / currentTime;
}

double LittlesLawTracker::computeEW() const {
    if (totalArrivals == 0) return 0.0;
    return totalWaitingTime / totalArrivals;
}