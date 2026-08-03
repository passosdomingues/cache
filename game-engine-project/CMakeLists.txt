cmake_minimum_required(VERSION 3.20)

project(GameEngineProject
    VERSION 0.0.1
    DESCRIPTION "Engine de jogos organizada como um compilador de assets"
    LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

# Flags de aviso rigorosas — falhas de arquitetura devem aparecer cedo.
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Compilation database para tooling (clangd, etc.)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

enable_testing()

add_subdirectory(src/core)
add_subdirectory(src/platform)
add_subdirectory(tests)

message(STATUS "GameEngineProject ${PROJECT_VERSION} — C++${CMAKE_CXX_STANDARD} — build type: ${CMAKE_BUILD_TYPE}")
