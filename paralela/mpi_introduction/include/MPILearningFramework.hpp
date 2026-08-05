/**
 * @file MPILearningFramework.hpp
 * @brief OOP Wrapper for MPI Environment & Core Communicator abstractions.
 */

#pragma once

#include <mpi.h>
#include <string>
#include <vector>

namespace DidacticMPI {

/**
 * @brief Object-Oriented manager for the MPI environment.
 * Handles lifecycle (MPI_Init / MPI_Finalize) and provides querying methods.
 */
class MPILearningFramework {
public:
    /**
     * @brief Constructor initializing MPI.
     * @param argc Command line argument count.
     * @param argv Command line argument values.
     */
    MPILearningFramework(int& argc, char**& argv);

    /**
     * @brief Destructor safely finalizing MPI.
     */
    ~MPILearningFramework();

    // Prevent copying
    MPILearningFramework(const MPILearningFramework&) = delete;
    MPILearningFramework& operator=(const MPILearningFramework&) = delete;

    /**
     * @brief Gets current process rank.
     * @return Rank index (0 to size-1).
     */
    [[nodiscard]] int getRank() const noexcept { return m_rank; }

    /**
     * @brief Gets total process count.
     * @return Process size.
     */
    [[nodiscard]] int getSize() const noexcept { return m_size; }

    /**
     * @brief Checks if current process is root (rank 0).
     * @return True if rank == 0.
     */
    [[nodiscard]] bool isRoot() const noexcept { return m_rank == 0; }

    /**
     * @brief Gets host processor name.
     * @return String with processor/hostname.
     */
    [[nodiscard]] std::string getProcessorName() const;

    /**
     * @brief Synchronizes all ranks via barrier.
     */
    void barrier() const noexcept;

    /**
     * @brief Measures current MPI wall time.
     * @return Time in seconds.
     */
    [[nodiscard]] static double getWtime() noexcept;

private:
    int m_rank{0};
    int m_size{1};
};

} // namespace DidacticMPI
