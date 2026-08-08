#include "engine/render/gl.hpp"

#include <GLFW/glfw3.h>

namespace engine::render::gl {

void (*GenVertexArrays)(GLsizei, GLuint*) = nullptr;
void (*BindVertexArray)(GLuint) = nullptr;
void (*DeleteVertexArrays)(GLsizei, const GLuint*) = nullptr;

void (*GenBuffers)(GLsizei, GLuint*) = nullptr;
void (*BindBuffer)(GLenum, GLuint) = nullptr;
void (*BufferData)(GLenum, GLsizeiptr, const void*, GLenum) = nullptr;
void (*BufferSubData)(GLenum, GLintptr, GLsizeiptr, const void*) = nullptr;
void (*DeleteBuffers)(GLsizei, const GLuint*) = nullptr;

void (*VertexAttribPointer)(GLuint, GLint, GLenum, GLboolean, GLsizei, const void*) = nullptr;
void (*EnableVertexAttribArray)(GLuint) = nullptr;
void (*DisableVertexAttribArray)(GLuint) = nullptr;

GLuint (*CreateShader)(GLenum) = nullptr;
void (*ShaderSource)(GLuint, GLsizei, const GLchar* const*, const GLint*) = nullptr;
void (*CompileShader)(GLuint) = nullptr;
void (*GetShaderiv)(GLuint, GLenum, GLint*) = nullptr;
void (*GetShaderInfoLog)(GLuint, GLsizei, GLsizei*, GLchar*) = nullptr;
void (*DeleteShader)(GLuint) = nullptr;

GLuint (*CreateProgram)() = nullptr;
void (*AttachShader)(GLuint, GLuint) = nullptr;
void (*LinkProgram)(GLuint) = nullptr;
void (*GetProgramiv)(GLuint, GLenum, GLint*) = nullptr;
void (*GetProgramInfoLog)(GLuint, GLsizei, GLsizei*, GLchar*) = nullptr;
void (*UseProgram)(GLuint) = nullptr;
void (*DeleteProgram)(GLuint) = nullptr;

GLint (*GetUniformLocation)(GLuint, const GLchar*) = nullptr;
void (*UniformMatrix4fv)(GLint, GLsizei, GLboolean, const GLfloat*) = nullptr;
void (*Uniform1i)(GLint, GLint) = nullptr;
void (*Uniform1f)(GLint, GLfloat) = nullptr;
void (*Uniform2f)(GLint, GLfloat, GLfloat) = nullptr;
void (*Uniform4f)(GLint, GLfloat, GLfloat, GLfloat, GLfloat) = nullptr;

void (*ActiveTexture)(GLenum) = nullptr;
void (*GenerateMipmap)(GLenum) = nullptr;

void (*GenFramebuffers)(GLsizei, GLuint*) = nullptr;
void (*BindFramebuffer)(GLenum, GLuint) = nullptr;
void (*FramebufferTexture2D)(GLenum, GLenum, GLenum, GLuint, GLint) = nullptr;
GLenum (*CheckFramebufferStatus)(GLenum) = nullptr;
void (*DeleteFramebuffers)(GLsizei, const GLuint*) = nullptr;

namespace {
template <typename Fn>
bool load(Fn& out, const char* name) {
    out = reinterpret_cast<Fn>(glfwGetProcAddress(name));
    return out != nullptr;
}
} // namespace

bool load_functions() {
    bool ok = true;
    ok &= load(GenVertexArrays, "glGenVertexArrays");
    ok &= load(BindVertexArray, "glBindVertexArray");
    ok &= load(DeleteVertexArrays, "glDeleteVertexArrays");

    ok &= load(GenBuffers, "glGenBuffers");
    ok &= load(BindBuffer, "glBindBuffer");
    ok &= load(BufferData, "glBufferData");
    ok &= load(BufferSubData, "glBufferSubData");
    ok &= load(DeleteBuffers, "glDeleteBuffers");

    ok &= load(VertexAttribPointer, "glVertexAttribPointer");
    ok &= load(EnableVertexAttribArray, "glEnableVertexAttribArray");
    ok &= load(DisableVertexAttribArray, "glDisableVertexAttribArray");

    ok &= load(CreateShader, "glCreateShader");
    ok &= load(ShaderSource, "glShaderSource");
    ok &= load(CompileShader, "glCompileShader");
    ok &= load(GetShaderiv, "glGetShaderiv");
    ok &= load(GetShaderInfoLog, "glGetShaderInfoLog");
    ok &= load(DeleteShader, "glDeleteShader");

    ok &= load(CreateProgram, "glCreateProgram");
    ok &= load(AttachShader, "glAttachShader");
    ok &= load(LinkProgram, "glLinkProgram");
    ok &= load(GetProgramiv, "glGetProgramiv");
    ok &= load(GetProgramInfoLog, "glGetProgramInfoLog");
    ok &= load(UseProgram, "glUseProgram");
    ok &= load(DeleteProgram, "glDeleteProgram");

    ok &= load(GetUniformLocation, "glGetUniformLocation");
    ok &= load(UniformMatrix4fv, "glUniformMatrix4fv");
    ok &= load(Uniform1i, "glUniform1i");
    ok &= load(Uniform1f, "glUniform1f");
    ok &= load(Uniform2f, "glUniform2f");
    ok &= load(Uniform4f, "glUniform4f");

    ok &= load(ActiveTexture, "glActiveTexture");
    ok &= load(GenerateMipmap, "glGenerateMipmap");

    ok &= load(GenFramebuffers, "glGenFramebuffers");
    ok &= load(BindFramebuffer, "glBindFramebuffer");
    ok &= load(FramebufferTexture2D, "glFramebufferTexture2D");
    ok &= load(CheckFramebufferStatus, "glCheckFramebufferStatus");
    ok &= load(DeleteFramebuffers, "glDeleteFramebuffers");

    return ok;
}

} // namespace engine::render::gl
