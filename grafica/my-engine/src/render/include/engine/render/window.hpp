#pragma once
#include <cstdint>
#include <string>

struct GLFWwindow;

namespace engine::render {

struct WindowConfig {
    std::string title = "engine";
    std::uint32_t width = 800;
    std::uint32_t height = 600;
    bool visible = true;   // false para contexto headless (testes/CI)
    bool vsync = true;
};

// Janela + contexto OpenGL (RFC 03 — Runtime, "Renderização"). Fina
// camada sobre GLFW; carrega os ponteiros de função modernos
// (engine::render::gl::load_functions) assim que o contexto é criado.
class Window {
public:
    explicit Window(const WindowConfig& config);
    ~Window();

    Window(const Window&) = delete;
    Window& operator=(const Window&) = delete;

    bool should_close() const;
    void poll_events() const;
    void swap_buffers() const;

    std::uint32_t width() const { return width_; }
    std::uint32_t height() const { return height_; }

    GLFWwindow* native_handle() const { return handle_; }

private:
    GLFWwindow* handle_ = nullptr;
    std::uint32_t width_ = 0;
    std::uint32_t height_ = 0;
    static int instance_count_;
};

} // namespace engine::render
