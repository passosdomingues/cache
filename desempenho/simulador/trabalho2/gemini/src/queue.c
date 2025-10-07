/**
 * @file queue.c
 * @brief Implementation of a simple linked-list queue.
 *
 * Project: M/M/1 Multi-Queue Simulator
 * Author: Rafael Passos Domingues
 * Last Update: 2025 Sep 25 14h36
 *
 * Purpose:
 * This file provides the concrete implementation for the queue data structure
 * declared in `queue.h`. It includes functions to initialize a queue,
 * add (enqueue) and remove (dequeue) customers, and free all associated
 * memory. It is a fundamental component for managing waiting customers.
 */
#include "../include/queue.h"
#include <stdio.h>

/**
 * @brief Initializes a queue structure to a default empty state.
 * @param q Pointer to the Queue to initialize.
 */
void initializeQueue(Queue* q) {
    q->head = NULL;
    q->tail = NULL;
    q->customerCount = 0;
    q->totalArrivals = 0;
    q->totalWaitTime = 0.0;
    q->areaNq = 0.0;
}

/**
 * @brief Adds a customer to the back of the queue.
 * @param q Pointer to the Queue.
 * @param arrivalTime The arrival time of the new customer.
 */
void enqueue(Queue* q, double arrivalTime) {
    CustomerNode* newNode = (CustomerNode*)malloc(sizeof(CustomerNode));
    if (!newNode) {
        perror("Failed to allocate memory for new customer");
        exit(1);
    }
    newNode->arrivalTime = arrivalTime;
    newNode->next = NULL;

    if (q->tail == NULL) { // Queue is empty
        q->head = newNode;
        q->tail = newNode;
    } else { // Queue is not empty
        q->tail->next = newNode;
        q->tail = newNode;
    }
    q->customerCount++;
}

/**
 * @brief Removes and returns the customer from the front of the queue.
 * @param q Pointer to the Queue.
 * @return The CustomerNode from the front of the queue. Returns NULL if empty.
 */
CustomerNode* dequeue(Queue* q) {
    if (q->head == NULL) {
        return NULL; // Queue is empty
    }

    CustomerNode* temp = q->head;
    q->head = q->head->next;

    if (q->head == NULL) { // Queue is now empty
        q->tail = NULL;
    }

    q->customerCount--;
    return temp;
}

/**
 * @brief Frees all memory associated with remaining customers in a queue.
 * @param q Pointer to the Queue to destroy.
 */
void destroyQueue(Queue* q) {
    CustomerNode* current = q->head;
    while (current != NULL) {
        CustomerNode* next = current->next;
        free(current);
        current = next;
    }
    q->head = NULL;
    q->tail = NULL;
    q->customerCount = 0;
}
