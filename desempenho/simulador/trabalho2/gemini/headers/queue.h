#ifndef QUEUE_H
#define QUEUE_H

#include <stdlib.h>

/**
 * @file queue.h
 * @brief Header for the queue data structure and customer nodes.
 *
 * Project: M/M/1 Multi-Queue Simulator
 * Author: Rafael Passos Domingues
 * Last Update: 2025 Sep 25 14h36
 *
 * Purpose:
 * This file defines the data structures for a customer (CustomerNode) and
 * the queue itself (Queue). It provides a simple, low-level linked-list
 * implementation to manage customers waiting for service. It also holds
 * all statistics relevant to a single queue.
 */

/**
 * @struct CustomerNode
 * @brief Represents a single customer in the queue.
 */
typedef struct CustomerNode {
    double arrivalTime;             ///< The simulation time when the customer arrived.
    struct CustomerNode* next;      ///< Pointer to the next customer in the linked list.
} CustomerNode;

/**
 * @struct Queue
 * @brief Represents a single waiting line and its associated statistics.
 */
typedef struct Queue {
    CustomerNode* head;             ///< Pointer to the first customer in the queue.
    CustomerNode* tail;             ///< Pointer to the last customer in the queue.
    int customerCount;              ///< Current number of customers in the queue.

    // --- Statistics ---
    long totalArrivals;             ///< Cumulative number of arrivals to this queue.
    double totalWaitTime;           ///< Cumulative wait time of all served customers from this queue.
    double areaNq;                  ///< Area under this queue's N_q(t) curve.
} Queue;

/**
 * @brief Initializes a queue structure.
 * @param q Pointer to the Queue to initialize.
 */
void initializeQueue(Queue* q);

/**
 * @brief Adds a customer to the back of the queue.
 * @param q Pointer to the Queue.
 * @param arrivalTime The arrival time of the new customer.
 */
void enqueue(Queue* q, double arrivalTime);

/**
 * @brief Removes and returns the customer from the front of the queue.
 * @param q Pointer to the Queue.
 * @return The CustomerNode from the front of the queue. Returns NULL if empty.
 */
CustomerNode* dequeue(Queue* q);

/**
 * @brief Frees all memory associated with a queue.
 * @param q Pointer to the Queue.
 */
void destroyQueue(Queue* q);

#endif // QUEUE_H
