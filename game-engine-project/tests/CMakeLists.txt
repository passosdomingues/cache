add_executable(platform-tests platform_tests.cpp)
target_include_directories(platform-tests PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(platform-tests PRIVATE platform)

add_test(NAME platform-tests COMMAND platform-tests)
