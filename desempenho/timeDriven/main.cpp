/*
 * Time-Driven Simulation Skeleton
 *
 * This program implements a simple time-driven simulation using OOP in C++.
 * Each event has a scheduled time and an execute() method that performs
 * the event's action. The simulation advances in fixed time steps (Δt)
 * and executes all events that occur within each interval.
 *
 * Features:
 * - Base class Event with virtual destructor for safe polymorphism.
 * - TimeDrivenSimulation class with system clock, stop time, time step,
 *   and event list.
 * - Statistics collection at each time step.
 *
 * Usage:
 * Compile with a Makefile or g++ and run ./main.
 */

#include <iostream>
#include <vector>

/* Base class representing a generic event */
class Event {
public:
    double eventTime;  // Scheduled time of the event

    Event(double time) : eventTime(time) {}

    virtual ~Event() {} // Virtual destructor for polymorphic safety

    virtual void execute() {
        std::cout << "Executing event at time " << eventTime << std::endl;
    }
};

/* Time-driven simulation class */
class TimeDrivenSimulation {
private:
    double simClock;                // Current simulation time
    double stopTime;                // Simulation end time
    double timeStep;                // Fixed time step Δt
    std::vector<Event*> eventList;  // List of all events

public:
    TimeDrivenSimulation(double startTime, double endTime, double step)
        : simClock(startTime), stopTime(endTime), timeStep(step) {}

    ~TimeDrivenSimulation() {
        // Clean up all dynamically allocated events
        for (Event* e : eventList) delete e;
    }

    void addEvent(Event* e) {
        eventList.push_back(e);
    }

    void collectStatistics() {
        std::cout << "Collecting statistics at time " << simClock << std::endl;
    }

    void runSimulation() {
        while (simClock < stopTime) {
            collectStatistics();

            // Execute all events that fall within the current time step
            for (Event* e : eventList) {
                if (e->eventTime >= simClock && e->eventTime < simClock + timeStep) {
                    e->execute();
                }
            }

            simClock += timeStep;  // Advance simulation clock
        }
    }
};

int main() {
    // Initialize simulation: startTime = 0, stopTime = 10, timeStep = 1
    TimeDrivenSimulation simulation(0.0, 10.0, 1.0);

    // Add sample events
    simulation.addEvent(new Event(2.0));
    simulation.addEvent(new Event(4.5));
    simulation.addEvent(new Event(7.0));

    simulation.runSimulation();

    return 0;
}
