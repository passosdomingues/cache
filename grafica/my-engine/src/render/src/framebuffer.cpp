#include "engine/render/framebuffer.hpp"

#include <stdexcept>

namespace engine::render {

Framebuffer::Framebuffer(std::uint32_t width, std::uint32_t height) : width_(width), height_(height) {
    color_texture_ = std::make_unique<Texture2D>(width, height, nullptr);

    gl::GenFramebuffers(1, &fbo_);
    gl::BindFramebuffer(GL_FRAMEBUFFER, fbo_);
    gl::FramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D,
                              color_texture_->native_handle(), 0);

    GLenum status = gl::CheckFramebufferStatus(GL_FRAMEBUFFER);
    gl::BindFramebuffer(GL_FRAMEBUFFER, 0);

    if (status != GL_FRAMEBUFFER_COMPLETE) {
        throw std::runtime_error("framebuffer incompleto (status 0x" + std::to_string(status) + ")");
    }
}

Framebuffer::~Framebuffer() {
    if (fbo_) gl::DeleteFramebuffers(1, &fbo_);
}

void Framebuffer::bind() const {
    gl::BindFramebuffer(GL_FRAMEBUFFER, fbo_);
}

void Framebuffer::unbind() {
    gl::BindFramebuffer(GL_FRAMEBUFFER, 0);
}

} // namespace engine::render
