add_library(resources STATIC
    src/resource_manager.cpp
)

target_include_directories(resources PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_compile_features(resources PUBLIC cxx_std_20)
target_link_libraries(resources PUBLIC platform jobs pkg)

add_executable(resource-demo demo/main.cpp)
target_link_libraries(resource-demo PRIVATE resources)
