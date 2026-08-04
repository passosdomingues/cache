add_library(jobs STATIC
    src/job_system.cpp
)

target_include_directories(jobs PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_compile_features(jobs PUBLIC cxx_std_20)
target_link_libraries(jobs PUBLIC platform)

add_executable(job-benchmark benchmark/main.cpp)
target_link_libraries(job-benchmark PRIVATE jobs)
