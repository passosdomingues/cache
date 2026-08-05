/**
 * @file Lessons.hpp
 * @brief Contains interactive, educational modules based on the professor's notebook.
 */

#pragma once

#include "MPILearningFramework.hpp"

namespace DidacticMPI {

/**
 * @brief Class containing OOP implementations of all notebook lessons & exercises.
 */
class Lessons {
public:
    /**
     * @brief Lesson 1: Hello World & Process Identification (Section 2 of notebook).
     * Demonstrates MPI_Init, MPI_Comm_rank, MPI_Comm_size, and MPI_Get_processor_name.
     */
    static void runHelloWorld(const MPILearningFramework& env);

    /**
     * @brief Lesson 2: Point-to-Point Communication (Section 3 of notebook).
     * Demonstrates MPI_Send and MPI_Recv between rank 0 and rank 1.
     */
    static void runPointToPoint(const MPILearningFramework& env);

    /**
     * @brief Lesson 3 / Exercise 1: Greetings Gathering & Rank Squared Sum.
     * Non-zero ranks calculate rank^2 and send to rank 0, which sums them up.
     */
    static void runGreetingsAndRankSquaredSum(const MPILearningFramework& env);

    /**
     * @brief Lesson 4 / Exercise 2: Vector Processing & Ring Echo.
     * Rank 0 sends a 10-element vector to Rank 1; Rank 1 sums elements and returns result.
     */
    static void runVectorProcessingAndEcho(const MPILearningFramework& env);

    /**
     * @brief Lesson 5: Broadcast Configuration (Section 4 of notebook).
     * Demonstrates collective communication with MPI_Bcast.
     */
    static void runBroadcastConfig(const MPILearningFramework& env);
};

} // namespace DidacticMPI
