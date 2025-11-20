#include "../include/events.h"
#include <stdexcept>

void EventQueue::pushEvent(const Event& event) {
    heap.push_back(event);
    heapifyUp(heap.size() - 1);
}

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

Event EventQueue::peekEvent() const {
    if (heap.empty()) {
        throw std::runtime_error("Cannot peek empty event queue");
    }
    return heap[0];
}

void EventQueue::heapifyUp(int index) {
    while (index > 0 && heap[parent(index)] > heap[index]) {
        std::swap(heap[index], heap[parent(index)]);
        index = parent(index);
    }
}

void EventQueue::heapifyDown(int index) {
    int smallest = index;
    int left = leftChild(index);
    int right = rightChild(index);
    
    if (left < (int)heap.size() && heap[left] > heap[smallest]) {
        smallest = left;
    }
    
    if (right < (int)heap.size() && heap[right] > heap[smallest]) {
        smallest = right;
    }
    
    if (smallest != index) {
        std::swap(heap[index], heap[smallest]);
        heapifyDown(smallest);
    }
}