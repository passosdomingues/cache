/**
 * @file events.hpp
 * @brief Event system for discrete event simulation
 */

#ifndef EVENTS_HPP
#define EVENTS_HPP

#include <vector>
#include <functional>
#include <algorithm>

/**
 * @brief Event types in the simulation
 */
enum class EventType {
    ARRIVAL,    ///< Packet arrival event
    DEPARTURE,  ///< Packet departure event 
    SAMPLE      ///< Statistics sampling event
};

/**
 * @brief Event structure for discrete event simulation
 */
struct Event {
    double timestamp;        ///< Event timestamp
    EventType type;          ///< Event type
    int queueId;             ///< Queue identifier (-1 for system-wide events)
    unsigned long packetId;  ///< Packet identifier for tracking specific packets

    /**
     * @brief Construct a new Event object
     * @param eventTimestamp Event timestamp
     * @param eventType Event type
     * @param eventQueueId Queue identifier (-1 for system-wide events)
     * @param eventPacketId Packet identifier
     */
    Event(double eventTimestamp, EventType eventType, int eventQueueId = -1, unsigned long eventPacketId = 0) 
        : timestamp(eventTimestamp), type(eventType), queueId(eventQueueId), packetId(eventPacketId) {}
    
    /**
     * @brief Comparison operator for min-heap (earliest timestamp first)
     * @param other Event to compare with
     * @return bool True if this event has greater timestamp than other
     */
    bool operator>(const Event& other) const {
        return timestamp > other.timestamp;
    }
};

/**
 * @brief Min-heap based event queue for efficient event management
 */
class EventQueue {
private:
    std::vector<Event> heap;  ///< Underlying heap storage

    /**
     * @brief Heapify up operation for maintaining heap property
     * @param index Starting index for heapify up
     */
    void heapifyUp(int index);
    
    /**
     * @brief Heapify down operation for maintaining heap property
     * @param index Starting index for heapify down
     */
    void heapifyDown(int index);
    
    /**
     * @brief Get parent index
     * @param index Current index
     * @return int Parent index
     */
    int parent(int index) const { return (index - 1) / 2; }
    
    /**
     * @brief Get left child index
     * @param index Current index
     * @return int Left child index
     */
    int leftChild(int index) const { return 2 * index + 1; }
    
    /**
     * @brief Get right child index
     * @param index Current index
     * @return int Right child index
     */
    int rightChild(int index) const { return 2 * index + 2; }

public:
    /**
     * @brief Construct a new Event Queue object
     */
    EventQueue() = default;
    
    /**
     * @brief Push event into the queue
     * @param event Event to push
     */
    void pushEvent(const Event& event);
    
    /**
     * @brief Pop event from the queue
     * @return Event The earliest event
     * @throws std::runtime_error if queue is empty
     */
    Event popEvent();
    
    /**
     * @brief Peek at the earliest event without removing it
     * @return Event The earliest event
     * @throws std::runtime_error if queue is empty
     */
    Event peekEvent() const;
    
    /**
     * @brief Check if event queue is empty
     * @return bool True if empty
     */
    bool isEmpty() const { return heap.empty(); }
    
    /**
     * @brief Get number of events in queue
     * @return size_t Event count
     */
    size_t size() const { return heap.size(); }
    
    /**
     * @brief Clear all events from queue
     */
    void clear() { heap.clear(); }
};

#endif // EVENTS_HPP