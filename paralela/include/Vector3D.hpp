/**
 * @file Vector3D.hpp
 * @brief Three-dimensional double-precision vector with SIMD-friendly memory layout.
 *
 * @details
 * This header defines the Vector3D struct used throughout the simulation for
 * positions, velocities, and forces. The struct is declared with alignas(32)
 * to ensure 32-byte alignment, which enables the compiler to emit 256-bit AVX2
 * instructions in tight loops (e.g., the O(N²) gravitational force computation).
 *
 * A 4th padding double is included so that the total size is exactly 32 bytes
 * (4 × 8 bytes), allowing arrays of Vector3D to remain aligned end-to-end.
 *
 * All arithmetic methods are inlined to eliminate function-call overhead in
 * the hot force-calculation path.
 */

#pragma once

#include <cmath>
#include <iosfwd>

// ─────────────────────────────────────────────────────────────────────────────

/**
 * @brief Immutable-friendly 3D vector type, memory-aligned for AVX2 SIMD.
 *
 * @note The padding member `_pad` is internal and should not be used directly.
 *       It exists purely to bring the struct size to 32 bytes so that an array
 *       of Vector3D maintains 32-byte alignment throughout (stride = 32 bytes).
 */
struct alignas(32) Vector3D {

    double x{0.0}; ///< X component
    double y{0.0}; ///< Y component
    double z{0.0}; ///< Z component
    double _pad{0.0}; ///< Padding to reach 32 bytes — do not use directly

    // ── Constructors ─────────────────────────────────────────────────────────

    Vector3D() = default;

    /**
     * @brief Constructs a vector from explicit components.
     * @param x X component.
     * @param y Y component.
     * @param z Z component.
     */
    constexpr Vector3D(double x, double y, double z) noexcept
        : x(x), y(y), z(z), _pad(0.0) {}

    // ── Arithmetic operators ──────────────────────────────────────────────────

    /**
     * @brief Component-wise addition.
     * @param o The right-hand vector.
     * @return New vector (this + o).
     */
    [[nodiscard]] Vector3D operator+(const Vector3D& o) const noexcept {
        return {x + o.x, y + o.y, z + o.z};
    }

    /**
     * @brief Component-wise subtraction.
     * @param o The right-hand vector.
     * @return New vector (this - o).
     */
    [[nodiscard]] Vector3D operator-(const Vector3D& o) const noexcept {
        return {x - o.x, y - o.y, z - o.z};
    }

    /**
     * @brief Scalar multiplication.
     * @param s Scalar multiplier.
     * @return New vector (this * s).
     */
    [[nodiscard]] Vector3D operator*(double s) const noexcept {
        return {x * s, y * s, z * s};
    }

    /**
     * @brief Scalar division.
     * @param s Scalar divisor (must be != 0).
     * @return New vector (this / s).
     */
    [[nodiscard]] Vector3D operator/(double s) const noexcept {
        return {x / s, y / s, z / s};
    }

    /**
     * @brief Negation.
     * @return New vector (-this).
     */
    [[nodiscard]] Vector3D operator-() const noexcept {
        return {-x, -y, -z};
    }

    /**
     * @brief In-place addition.
     * @param o Vector to add.
     * @return Reference to this.
     */
    Vector3D& operator+=(const Vector3D& o) noexcept {
        x += o.x; y += o.y; z += o.z; return *this;
    }

    /**
     * @brief In-place subtraction.
     * @param o Vector to subtract.
     * @return Reference to this.
     */
    Vector3D& operator-=(const Vector3D& o) noexcept {
        x -= o.x; y -= o.y; z -= o.z; return *this;
    }

    /**
     * @brief In-place scalar multiplication.
     * @param s Scalar multiplier.
     * @return Reference to this.
     */
    Vector3D& operator*=(double s) noexcept {
        x *= s; y *= s; z *= s; return *this;
    }

    // ── Geometric operations ──────────────────────────────────────────────────

    /**
     * @brief Squared Euclidean magnitude.
     * @details Avoids the sqrt call when only comparisons are needed.
     * @return x² + y² + z².
     */
    [[nodiscard]] double normSquared() const noexcept {
        return x * x + y * y + z * z;
    }

    /**
     * @brief Euclidean magnitude (L2 norm).
     * @return sqrt(x² + y² + z²).
     */
    [[nodiscard]] double norm() const noexcept {
        return std::sqrt(normSquared());
    }

    /**
     * @brief Dot product with another vector.
     * @param o The other vector.
     * @return Scalar dot product (this · o).
     */
    [[nodiscard]] double dot(const Vector3D& o) const noexcept {
        return x * o.x + y * o.y + z * o.z;
    }

    /**
     * @brief Cross product with another vector.
     * @param o The other vector.
     * @return New vector (this × o).
     */
    [[nodiscard]] Vector3D cross(const Vector3D& o) const noexcept {
        return {
            y * o.z - z * o.y,
            z * o.x - x * o.z,
            x * o.y - y * o.x
        };
    }

    /**
     * @brief Returns a unit vector (normalized).
     * @details Undefined if norm() == 0.
     * @return this / |this|.
     */
    [[nodiscard]] Vector3D normalized() const noexcept {
        return *this / norm();
    }

    /**
     * @brief Sets all components to zero in-place.
     */
    void zero() noexcept { x = 0.0; y = 0.0; z = 0.0; }

    /**
     * @brief Checks whether all components are exactly zero.
     * @return true if x == y == z == 0.
     */
    [[nodiscard]] bool isZero() const noexcept {
        return x == 0.0 && y == 0.0 && z == 0.0;
    }

    // ── Stream output ─────────────────────────────────────────────────────────
    friend std::ostream& operator<<(std::ostream& os, const Vector3D& v);
};

// ── Free-function scalar × vector ─────────────────────────────────────────────

/**
 * @brief Scalar-on-left multiplication: s * v.
 * @param s Scalar.
 * @param v Vector.
 * @return New vector (s * v).
 */
[[nodiscard]] inline Vector3D operator*(double s, const Vector3D& v) noexcept {
    return v * s;
}
