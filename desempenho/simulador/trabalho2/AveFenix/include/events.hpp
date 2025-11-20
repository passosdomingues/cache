#ifndef EVENTS_HPP
#define EVENTS_HPP

#include <vector>
#include <functional>
#include <algorithm>

/**
 * @brief Event types in the simulation
 */
enum class EventType {
    ARRIVAL,
    DEPARTURE, 
    SAMPLE
};

/**
 * @brief Event structure for discrete event simulation
 */
struct Event {
    double timestamp;
    EventType type;
    int queueId; // -1 for system-wide events
    unsigned long packetId; // For tracking specific packets

    Event(double ts, EventType t, int qid = -1, unsigned long pid = 0) 
        : timestamp(ts), type(t), queueId(qid), packetId(pid) {}
    
    // Comparison for min-heap (earliest timestamp first)
    bool operator>(const Event& other) const {
        return timestamp > other.timestamp;
    }
};

/**
 * @brief Min-heap based event queue for efficient event management
 */
class EventQueue {
private:
    std::vector<Event> heap;

    void heapifyUp(int index);
    void heapifyDown(int index);
    int parent(int index) const { return (index - 1) / 2; }
    int leftChild(int index) const { return 2 * index + 1; }
    int rightChild(int index) const { return 2 * index + 2; }

public:
    EventQueue() = default;
    
    /**
     * @brief Push event into the queue
     * @param event Event to push
     */
    void pushEvent(const Event& event);
    
    /**
     * @brief Pop event from the queue
     * @return Event The earliest event
     */
    Event popEvent();
    
    /**
     * @brief Peek at the earliest event without removing it
     * @return Event The earliest event
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