#include "engine/render/shader.hpp"

#include <stdexcept>
#include <vector>

namespace engine::render {

namespace {
GLuint compile(GLenum type, const std::string& source) {
    GLuint shader = gl::CreateShader(type);
    const char* src = source.c_str();
    GLint len = static_cast<GLint>(source.size());
    gl::ShaderSource(shader, 1, &src, &len);
    gl::CompileShader(shader);

    GLint success = 0;
    gl::GetShaderiv(shader, GL_COMPILE_STATUS, &success);
    if (!success) {
        GLint log_len = 0;
        gl::GetShaderiv(shader, GL_INFO_LOG_LENGTH, &log_len);
        std::vector<char> log(static_cast<std::size_t>(log_len) + 1, '\0');
        gl::GetShaderInfoLog(shader, log_len, nullptr, log.data());
        gl::DeleteShader(shader);
        throw std::runtime_error(std::string("falha ao compilar shader: ") + log.data());
    }
    return shader;
}
} // namespace

ShaderProgram::ShaderProgram(const std::string& vertex_source, const std::string& fragment_source) {
    GLuint vertex = compile(GL_VERTEX_SHADER, vertex_source);
    GLuint fragment = compile(GL_FRAGMENT_SHADER, fragment_source);

    program_ = gl::CreateProgram();
    gl::AttachShader(program_, vertex);
    gl::AttachShader(program_, fragment);
    gl::LinkProgram(program_);

    GLint success = 0;
    gl::GetProgramiv(program_, GL_LINK_STATUS, &success);
    if (!success) {
        GLint log_len = 0;
        gl::GetProgramiv(program_, GL_INFO_LOG_LENGTH, &log_len);
        std::vector<char> log(static_cast<std::size_t>(log_len) + 1, '\0');
        gl::GetProgramInfoLog(program_, log_len, nullptr, log.data());
        gl::DeleteShader(vertex);
        gl::DeleteShader(fragment);
        gl::DeleteProgram(program_);
        throw std::runtime_error(std::string("falha ao linkar programa de shader: ") + log.data());
    }

    gl::DeleteShader(vertex);
    gl::DeleteShader(fragment);
}

ShaderProgram::~ShaderProgram() {
    if (program_) gl::DeleteProgram(program_);
}

void ShaderProgram::use() const {
    gl::UseProgram(program_);
}

GLint ShaderProgram::uniform_location(const std::string& name) const {
    return gl::GetUniformLocation(program_, name.c_str());
}

void ShaderProgram::set_mat4(const std::string& name, const Mat4& value) const {
    gl::UniformMatrix4fv(uniform_location(name), 1, GL_FALSE, value.m);
}
void ShaderProgram::set_int(const std::string& name, int value) const {
    gl::Uniform1i(uniform_location(name), value);
}
void ShaderProgram::set_float(const std::string& name, float value) const {
    gl::Uniform1f(uniform_location(name), value);
}
void ShaderProgram::set_vec2(const std::string& name, float x, float y) const {
    gl::Uniform2f(uniform_location(name), x, y);
}
void ShaderProgram::set_vec4(const std::string& name, float x, float y, float z, float w) const {
    gl::Uniform4f(uniform_location(name), x, y, z, w);
}

} // namespace engine::render
