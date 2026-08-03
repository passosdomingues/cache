add_executable(hello-engine
    main.cpp
    version.hpp
)

target_include_directories(hello-engine PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

target_compile_features(hello-engine PRIVATE cxx_std_20)
