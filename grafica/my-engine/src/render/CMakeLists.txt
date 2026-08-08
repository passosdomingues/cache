find_package(glfw3 REQUIRED)
find_package(OpenGL REQUIRED)

add_library(render STATIC
    src/gl_loader.cpp
    src/window.cpp
    src/shader.cpp
    src/texture.cpp
    src/framebuffer.cpp
    src/batch_renderer.cpp
    src/image_payload.cpp
)

target_include_directories(render PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_compile_features(render PUBLIC cxx_std_20)
target_link_libraries(render PUBLIC platform glfw OpenGL::GL)

add_executable(moving-sprite-demo demo/main.cpp)
target_link_libraries(moving-sprite-demo PRIVATE render resources jobs)
