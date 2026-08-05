/**
 * @file Vector3D.cpp
 * @brief Implementation of the Vector3D stream output operator.
 */

#include "Vector3D.hpp"
#include <ostream>
#include <iomanip>

std::ostream& operator<<(std::ostream& os, const Vector3D& v) {
    os << std::fixed << std::setprecision(6)
       << "(" << v.x << ", " << v.y << ", " << v.z << ")";
    return os;
}
