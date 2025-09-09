/*
 * Event-Driven Simulation Skeleton
 *
 * This program implements an event-driven simulation using OOP in C++.
 * Each event has a scheduled time and an execute() method that performs
 * the action of the event. The simulation loop removes the next event
 * from the event list, advances the simulation clock to the event's time,
 * and executes the event.
 *
 * Features:
 * - Base class Event with a virtual destructor for safe polymorphism.
 * - Derived events: ArrivalEvent and DepartureEvent.
 * - EventDrivenSimulation class that maintains the event list and runs
 *   the main simulation loop.
 *
 * Usage:
 * Compile using the provided Makefile and run ./main.
 * New events can be dynamically added during the simulation.
 */

#include <iostream>
#include <vector>
#include <algorithm>

/* Base class for all events */
class Event {
public:
    double eventTime;

    Event(double time) : eventTime(time) {}

    virtual ~Event() {}  // virtual destructor for polymorphism

    virtual void execute() {
        std::cout << "Executing generic event at " << eventTime << std::endl;
    }
};

/* Arrival event */
class ArrivalEvent : public Event {
public:
    ArrivalEvent(double time) : Event(time) {}

    void execute() override {
        std::cout << "Arrival event at " << eventTime << std::endl;
    }
};

/* Departure event */
class DepartureEvent : public Event {
public:
    DepartureEvent(double time) : Event(time) {}

    void execute() override {
        std::cout << "Departure event at " << eventTime << std::endl;
    }
};

/* Event-driven simulation class */
class EventDrivenSimulation {
private:
    double simClock;
    std::vector<Event*> eventList;

    static bool compareEvents(Event* a, Event* b) {
        return a->eventTime < b->eventTime;
    }

public:
    EventDrivenSimulation() : simClock(0.0) {}

    ~EventDrivenSimulation() {
        for (Event* e : eventList) delete e;
    }

    void addEvent(Event* e) {
        eventList.push_back(e);
        std::sort(eventList.begin(), eventList.end(), compareEvents);
    }

    void runSimulation() {
        while (!eventList.empty()) {
            Event* currentEvent = eventList.front();
            eventList.erase(eventList.begin());

            simClock = currentEvent->eventTime;
            currentEvent->execute();

            delete currentEvent;
        }
    }

    double getSimClock() const { return simClock; }
};

int main() {
    EventDrivenSimulation simulation;

    // Add sample events
    simulation.addEvent(new ArrivalEvent(2.0));
    simulation.addEvent(new DepartureEvent(4.5));
    simulation.addEvent(new ArrivalEvent(7.0));

    simulation.runSimulation();

    return 0;
}
