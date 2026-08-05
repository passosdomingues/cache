/**
 * @file MPILearningFramework.cpp
 * @brief Implementation of the OOP MPI Framework.
 */

#include "MPILearningFramework.hpp"
#include <stdexcept>

namespace DidacticMPI {

MPILearningFramework::MPILearningFramework(int& argc, char**& argv) {
    int initialized = 0;
    MPI_Initialized(&initialized);
    if (!initialized) {
        MPI_Init(&argc, &argv);
    }
    MPI_Comm_rank(MPI_COMM_WORLD, &m_rank);
    MPI_Comm_size(MPI_COMM_WORLD, &m_size);
}

MPILearningFramework::~MPILearningFramework() {
    int finalized = 0;
    MPI_Finalized(&finalized);
    if (!finalized) {
        MPI_Finalize();
    }
}

std::string MPILearningFramework::getProcessorName() const {
    char name[MPI_MAX_PROCESSOR_NAME];
    int len = 0;
    MPI_Get_processor_name(name, &len);
    return std::string(name, len);
}

void MPILearningFramework::barrier() const noexcept {
    MPI_Barrier(MPI_COMM_WORLD);
}

double MPILearningFramework::getWtime() noexcept {
    return MPI_Wtime();
}

} // namespace DidacticMPI
