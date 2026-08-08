#pragma once
#include "engine/render/gl.hpp"
#include "engine/render/math.hpp"

#include <string>

namespace engine::render {

// Programa de shader (vertex + fragment) compilado e linkado. Lança
// std::runtime_error com o log de compilação/linkagem em caso de erro —
// falhas de shader são sempre um bug do programador, não algo para
// silenciar.
class ShaderProgram {
public:
    ShaderProgram(const std::string& vertex_source, const std::string& fragment_source);
    ~ShaderProgram();

    ShaderProgram(const ShaderProgram&) = delete;
    ShaderProgram& operator=(const ShaderProgram&) = delete;

    void use() const;

    void set_mat4(const std::string& name, const Mat4& value) const;
    void set_int(const std::string& name, int value) const;
    void set_float(const std::string& name, float value) const;
    void set_vec2(const std::string& name, float x, float y) const;
    void set_vec4(const std::string& name, float x, float y, float z, float w) const;

private:
    GLint uniform_location(const std::string& name) const;

    GLuint program_ = 0;
};

} // namespace engine::render
