add_library(platform STATIC
    src/logger.cpp
    src/filesystem.cpp
    src/configuration.cpp
    src/socket.cpp
    src/cli.cpp
    src/memory.cpp
)

target_include_directories(platform PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_compile_features(platform PUBLIC cxx_std_20)

find_package(Threads REQUIRED)
target_link_libraries(platform PUBLIC Threads::Threads)
