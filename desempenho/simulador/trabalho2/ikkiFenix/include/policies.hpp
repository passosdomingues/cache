/**
 * @file policies.hpp
 * @brief Definition of queue selection policies for the shared server.
 */

#ifndef POLICIES_HPP
#define POLICIES_HPP

#include <vector>
#include <functional>
#include "components.hpp"

// Forward declaration
class Queue;

typedef std::function<int(const std::vector<Queue*>&, double)> PolicyFunction;
using QueueSelectionPolicy = PolicyFunction;

namespace Policies {
    /**
     * @brief Selects the queue with the largest number of items.
     */
    int LongestQueue(const std::vector<Queue*>& queues, double currentTime);

    /**
     * @brief Selects the queue with the highest average waiting time (from measurement window).
     */
    int MaxAverageWait(const std::vector<Queue*>& queues, double currentTime);

    /**
     * @brief Selects the queue containing the packet that has waited the longest (Head-Of-Line).
     */
    int OldestPacket(const std::vector<Queue*>& queues, double currentTime);
    
    /**
     * @brief Helper to get policy by name string.
     */
    PolicyFunction getPolicyByName(const std::string& name);
}

#endif // POLICIES_HPP