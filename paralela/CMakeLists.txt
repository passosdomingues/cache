cmake_minimum_required(VERSION 3.20)

# ─────────────────────────────────────────────────────────────────────────────
# Project declaration
# ─────────────────────────────────────────────────────────────────────────────
project(AGN_Simulation
    VERSION     1.0.0
    DESCRIPTION "Parallel N-Body AGN Simulation using MPI"
    LANGUAGES   CXX
)

set(CMAKE_CXX_STANDARD          17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS        OFF)

# ─────────────────────────────────────────────────────────────────────────────
# Build type defaults
# ─────────────────────────────────────────────────────────────────────────────
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")

# ─────────────────────────────────────────────────────────────────────────────
# Compiler flags — squeeze every cycle for the i7-8565U (AVX2 + FMA)
# ─────────────────────────────────────────────────────────────────────────────
set(CMAKE_CXX_FLAGS_RELEASE
    "-O3 -march=native -ffast-math -funroll-loops -fno-omit-frame-pointer"
    CACHE STRING "Release flags" FORCE
)
set(CMAKE_CXX_FLAGS_DEBUG
    "-g3 -fsanitize=address,undefined -fno-omit-frame-pointer"
    CACHE STRING "Debug flags" FORCE
)

# ─────────────────────────────────────────────────────────────────────────────
# Dependencies
# ─────────────────────────────────────────────────────────────────────────────
find_package(MPI REQUIRED)

message(STATUS "MPI include: ${MPI_CXX_INCLUDE_DIRS}")
message(STATUS "MPI libs:    ${MPI_CXX_LIBRARIES}")
message(STATUS "Compiler:    ${CMAKE_CXX_COMPILER_ID} ${CMAKE_CXX_COMPILER_VERSION}")

# ─────────────────────────────────────────────────────────────────────────────
# Source files
# ─────────────────────────────────────────────────────────────────────────────
file(GLOB_RECURSE SOURCES "src/*.cpp")

add_executable(agn_simulation ${SOURCES})

target_include_directories(agn_simulation
    PRIVATE
        include
        ${MPI_CXX_INCLUDE_DIRS}
)

target_link_libraries(agn_simulation
    PRIVATE
        MPI::MPI_CXX
)

target_compile_features(agn_simulation PRIVATE cxx_std_17)

# ─────────────────────────────────────────────────────────────────────────────
# Install
# ─────────────────────────────────────────────────────────────────────────────
install(TARGETS agn_simulation DESTINATION bin)
