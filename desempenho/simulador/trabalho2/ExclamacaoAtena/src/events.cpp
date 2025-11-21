/**
 * @file events.cpp
 * @brief Implementation of event queue management
 */

#include "../include/events.hpp"
#include <stdexcept>

/**
 * @brief Push event into the queue
 * @param event Event to push
 */
void EventQueue::pushEvent(const Event& event) {
    heap.push_back(event);
    heapifyUp(static_cast<int>(heap.size() - 1));
}

/**
 * @brief Pop event from the queue
 * @return Event The earliest event
 * @throws std::runtime_error if queue is empty
 */
Event EventQueue::popEvent() {
    if (heap.empty()) {
        throw std::runtime_error("Cannot pop from empty event queue");
    }
    
    Event topEvent = heap[0];
    heap[0] = heap.back();
    heap.pop_back();
    
    if (!heap.empty()) {
        heapifyDown(0);
    }
    
    return topEvent;
}

/**
 * @brief Peek at the earliest event without removing it
 * @return Event The earliest event
 * @throws std::runtime_error if queue is empty
 */
Event EventQueue::peekEvent() const {
    if (heap.empty()) {
        throw std::runtime_error("Cannot peek empty event queue");
    }
    return heap[0];
}

/**
 * @brief Heapify up operation for maintaining heap property
 * @param index Starting index for heapify up
 */
void EventQueue::heapifyUp(int index) {
    while (index > 0 && heap[parent(index)] > heap[index]) {
        std::swap(heap[index], heap[parent(index)]);
        index = parent(index);
    }
}

/**
 * @brief Heapify down operation for maintaining heap property
 * @param index Starting index for heapify down
 */
void EventQueue::heapifyDown(int index) {
    int smallest = index;
    int left = leftChild(index);
    int right = rightChild(index);
    
    if (left < static_cast<int>(heap.size()) && heap[smallest] > heap[left]) {
        smallest = left;
    }
    
    if (right < static_cast<int>(heap.size()) && heap[smallest] > heap[right]) {
        smallest = right;
    }
    
    if (smallest != index) {
        std::swap(heap[index], heap[smallest]);
        heapifyDown(smallest);
    }
}