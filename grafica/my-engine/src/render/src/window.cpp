#include "engine/render/window.hpp"
#include "engine/render/gl.hpp"

#include <GLFW/glfw3.h>

#include <stdexcept>

namespace engine::render {

int Window::instance_count_ = 0;

Window::Window(const WindowConfig& config) : width_(config.width), height_(config.height) {
    if (instance_count_ == 0) {
        if (!glfwInit()) {
            throw std::runtime_error("falha ao inicializar GLFW");
        }
    }
    ++instance_count_;

    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    glfwWindowHint(GLFW_VISIBLE, config.visible ? GLFW_TRUE : GLFW_FALSE);

    handle_ = glfwCreateWindow(static_cast<int>(config.width), static_cast<int>(config.height),
                                config.title.c_str(), nullptr, nullptr);
    if (!handle_) {
        --instance_count_;
        if (instance_count_ == 0) glfwTerminate();
        throw std::runtime_error("falha ao criar janela/contexto GLFW");
    }

    glfwMakeContextCurrent(handle_);
    glfwSwapInterval(config.vsync ? 1 : 0);

    if (!gl::load_functions()) {
        glfwDestroyWindow(handle_);
        --instance_count_;
        if (instance_count_ == 0) glfwTerminate();
        throw std::runtime_error("falha ao carregar funcoes OpenGL (driver nao suporta OpenGL 3.3?)");
    }
}

Window::~Window() {
    if (handle_) {
        glfwDestroyWindow(handle_);
    }
    --instance_count_;
    if (instance_count_ == 0) {
        glfwTerminate();
    }
}

bool Window::should_close() const {
    return glfwWindowShouldClose(handle_);
}

void Window::poll_events() const {
    glfwPollEvents();
}

void Window::swap_buffers() const {
    glfwSwapBuffers(handle_);
}

} // namespace engine::render
