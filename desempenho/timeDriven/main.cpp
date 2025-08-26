#include <iostream>
#include <vector>

/*
 * Class representing a generic Event in the simulation.
 * Each Event has a scheduled time and an execute() method
 * to perform the event's action.
 */
class Event {
public:
    double eventTime;  // Scheduled time of the event

    Event(double time) : eventTime(time) {}

    /*
     * Execute the event.
     * In a real simulation, this would modify the system state.
     */
    virtual void execute() {
        std::cout << "Executing event at time " << eventTime << std::endl;
    }
};

/*
 * Class representing the Simulation system.
 * Holds system state, a list of events, simulation clock,
 * and methods to collect statistics and advance time.
 */
class TimeDrivenSimulation {
private:
    double simClock;                  // Current simulation time
    double stopTime;                  // Simulation end time
    double timeStep;                  // Fixed time step Δt
    std::vector<Event*> eventList;    // List of all events

public:
    /*
     * Constructor initializes the simulation parameters
     * and optionally an initial list of events.
     */
    TimeDrivenSimulation(double startTime, double endTime, double step)
        : simClock(startTime), stopTime(endTime), timeStep(step) {}

    /*
     * Add an event to the simulation.
     */
    void addEvent(Event* e) {
        eventList.push_back(e);
    }

    /*
     * Collect statistics for the current state of the system.
     * In practice, this could record queues, resource usage, etc.
     */
    void collectStatistics() {
        std::cout << "Collecting statistics at time " << simClock << std::endl;
    }

    /*
     * Run the time-driven simulation loop.
     * Advances simClock by fixed time steps and executes
     * all events occurring within each interval.
     */
    void runSimulation() {
        while (simClock < stopTime) {
            collectStatistics();

            for (Event* e : eventList) {
                if (e->eventTime >= simClock && e->eventTime < simClock + timeStep) {
                    e->execute();
                }
            }

            simClock += timeStep;
        }
    }
};

int main() {
    // Initialize simulation: startTime = 0, stopTime = 10, timeStep = 1
    TimeDrivenSimulation simulation(0.0, 10.0, 1.0);

    // Add sample events to the simulation
    simulation.addEvent(new Event(2.0));
    simulation.addEvent(new Event(4.5));
    simulation.addEvent(new Event(7.0));

    // Run the simulation
    simulation.runSimulation();

    return 0;
}
