cmake_minimum_required(VERSION 3.20)

project(MPI_Didatico_CPP
    VERSION 1.0.0
    DESCRIPTION "Projetinho Didático de MPI em C++ baseada no curso de Computação Paralela"
    LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

find_package(MPI REQUIRED)

file(GLOB_RECURSE SOURCES "src/*.cpp")

add_executable(mpi_didatico ${SOURCES})

target_include_directories(mpi_didatico
    PRIVATE
        include
        ${MPI_CXX_INCLUDE_DIRS}
)

target_link_libraries(mpi_didatico
    PRIVATE
        MPI::MPI_CXX
)

target_compile_options(mpi_didatico PRIVATE -O3 -Wall -Wextra)
