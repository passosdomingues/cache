add_executable(platform-tests platform_tests.cpp)
target_include_directories(platform-tests PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(platform-tests PRIVATE platform)

add_test(NAME platform-tests COMMAND platform-tests)

add_executable(job-tests job_tests.cpp)
target_include_directories(job-tests PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(job-tests PRIVATE jobs platform)

add_test(NAME job-tests COMMAND job-tests)

add_executable(assetc-tests assetc_tests.cpp)
target_include_directories(assetc-tests PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(assetc-tests PRIVATE assetc_lib platform)

add_test(NAME assetc-tests COMMAND assetc-tests)

add_executable(resources-tests resources_tests.cpp)
target_include_directories(resources-tests PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(resources-tests PRIVATE resources platform jobs pkg)

add_test(NAME resources-tests COMMAND resources-tests)
