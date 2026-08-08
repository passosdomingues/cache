#pragma once
#include <GL/gl.h>

// GL/gl.h do sistema (Mesa/libglvnd) só declara OpenGL ~1.4. As
// constantes e funções abaixo (buffers, shaders, framebuffers, VAOs)
// são de OpenGL 1.5-3.0 e precisam ser carregadas em tempo de execução
// via glfwGetProcAddress — não têm protótipo estático disponível.
// Guardado com #ifndef para não colidir caso algum sistema já as tenha.

#ifndef GL_ARRAY_BUFFER
#define GL_ARRAY_BUFFER 0x8892
#endif
#ifndef GL_ELEMENT_ARRAY_BUFFER
#define GL_ELEMENT_ARRAY_BUFFER 0x8893
#endif
#ifndef GL_STATIC_DRAW
#define GL_STATIC_DRAW 0x88E4
#endif
#ifndef GL_DYNAMIC_DRAW
#define GL_DYNAMIC_DRAW 0x88E8
#endif
#ifndef GL_VERTEX_SHADER
#define GL_VERTEX_SHADER 0x8B31
#endif
#ifndef GL_FRAGMENT_SHADER
#define GL_FRAGMENT_SHADER 0x8B30
#endif
#ifndef GL_COMPILE_STATUS
#define GL_COMPILE_STATUS 0x8B81
#endif
#ifndef GL_LINK_STATUS
#define GL_LINK_STATUS 0x8B82
#endif
#ifndef GL_INFO_LOG_LENGTH
#define GL_INFO_LOG_LENGTH 0x8B84
#endif
#ifndef GL_FRAMEBUFFER
#define GL_FRAMEBUFFER 0x8D40
#endif
#ifndef GL_COLOR_ATTACHMENT0
#define GL_COLOR_ATTACHMENT0 0x8CE0
#endif
#ifndef GL_FRAMEBUFFER_COMPLETE
#define GL_FRAMEBUFFER_COMPLETE 0x8CD5
#endif

namespace engine::render::gl {

using GLchar = char;
using GLsizeiptr = long;
using GLintptr = long;

// Carrega os ponteiros de função abaixo via glfwGetProcAddress. Deve ser
// chamado uma vez, com um contexto GL já corrente (depois de
// glfwMakeContextCurrent). Retorna false se alguma função essencial não
// puder ser resolvida.
bool load_functions();

extern void (*GenVertexArrays)(GLsizei, GLuint*);
extern void (*BindVertexArray)(GLuint);
extern void (*DeleteVertexArrays)(GLsizei, const GLuint*);

extern void (*GenBuffers)(GLsizei, GLuint*);
extern void (*BindBuffer)(GLenum, GLuint);
extern void (*BufferData)(GLenum, GLsizeiptr, const void*, GLenum);
extern void (*BufferSubData)(GLenum, GLintptr, GLsizeiptr, const void*);
extern void (*DeleteBuffers)(GLsizei, const GLuint*);

extern void (*VertexAttribPointer)(GLuint, GLint, GLenum, GLboolean, GLsizei, const void*);
extern void (*EnableVertexAttribArray)(GLuint);
extern void (*DisableVertexAttribArray)(GLuint);

extern GLuint (*CreateShader)(GLenum);
extern void (*ShaderSource)(GLuint, GLsizei, const GLchar* const*, const GLint*);
extern void (*CompileShader)(GLuint);
extern void (*GetShaderiv)(GLuint, GLenum, GLint*);
extern void (*GetShaderInfoLog)(GLuint, GLsizei, GLsizei*, GLchar*);
extern void (*DeleteShader)(GLuint);

extern GLuint (*CreateProgram)();
extern void (*AttachShader)(GLuint, GLuint);
extern void (*LinkProgram)(GLuint);
extern void (*GetProgramiv)(GLuint, GLenum, GLint*);
extern void (*GetProgramInfoLog)(GLuint, GLsizei, GLsizei*, GLchar*);
extern void (*UseProgram)(GLuint);
extern void (*DeleteProgram)(GLuint);

extern GLint (*GetUniformLocation)(GLuint, const GLchar*);
extern void (*UniformMatrix4fv)(GLint, GLsizei, GLboolean, const GLfloat*);
extern void (*Uniform1i)(GLint, GLint);
extern void (*Uniform1f)(GLint, GLfloat);
extern void (*Uniform2f)(GLint, GLfloat, GLfloat);
extern void (*Uniform4f)(GLint, GLfloat, GLfloat, GLfloat, GLfloat);

extern void (*ActiveTexture)(GLenum);
extern void (*GenerateMipmap)(GLenum);

extern void (*GenFramebuffers)(GLsizei, GLuint*);
extern void (*BindFramebuffer)(GLenum, GLuint);
extern void (*FramebufferTexture2D)(GLenum, GLenum, GLenum, GLuint, GLint);
extern GLenum (*CheckFramebufferStatus)(GLenum);
extern void (*DeleteFramebuffers)(GLsizei, const GLuint*);

} // namespace engine::render::gl
