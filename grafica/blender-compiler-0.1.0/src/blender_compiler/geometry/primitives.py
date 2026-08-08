"""Etapa 6 — Geometry Generator (primitivas).

Cada função retorna (vertices, faces) em coordenadas locais centradas na
origem, unidade = 1.0. Escala/posição/rotação são aplicadas depois pela
camada que monta a MeshData. Novas primitivas são adicionadas registrando
uma função aqui e uma entrada em `PRIMITIVE_BUILDERS` — nenhuma outra
camada precisa mudar (Open/Closed Principle).
"""

from __future__ import annotations

import math
from collections.abc import Callable

Vertex = tuple[float, float, float]
Face = tuple[int, ...]


def build_cube(size: tuple[float, float, float] = (1, 1, 1)) -> tuple[list[Vertex], list[Face]]:
    sx, sy, sz = (s / 2 for s in size)
    vertices: list[Vertex] = [
        (-sx, -sy, -sz),
        (sx, -sy, -sz),
        (sx, sy, -sz),
        (-sx, sy, -sz),
        (-sx, -sy, sz),
        (sx, -sy, sz),
        (sx, sy, sz),
        (-sx, sy, sz),
    ]
    faces: list[Face] = [
        (0, 1, 2, 3),
        (4, 7, 6, 5),
        (0, 4, 5, 1),
        (1, 5, 6, 2),
        (2, 6, 7, 3),
        (3, 7, 4, 0),
    ]
    return vertices, faces


def build_plane(size: tuple[float, float, float] = (1, 1, 1)) -> tuple[list[Vertex], list[Face]]:
    sx, sy = size[0] / 2, size[1] / 2
    vertices: list[Vertex] = [(-sx, -sy, 0), (sx, -sy, 0), (sx, sy, 0), (-sx, sy, 0)]
    faces: list[Face] = [(0, 1, 2, 3)]
    return vertices, faces


def build_uv_sphere(
    size: tuple[float, float, float] = (1, 1, 1), segments: int = 16, rings: int = 8
) -> tuple[list[Vertex], list[Face]]:
    rx, ry, rz = (s / 2 for s in size)
    vertices: list[Vertex] = []
    for ring in range(rings + 1):
        theta = math.pi * ring / rings  # 0..pi
        for seg in range(segments):
            phi = 2 * math.pi * seg / segments
            x = rx * math.sin(theta) * math.cos(phi)
            y = ry * math.sin(theta) * math.sin(phi)
            z = rz * math.cos(theta)
            vertices.append((x, y, z))

    faces: list[Face] = []
    for ring in range(rings):
        for seg in range(segments):
            a = ring * segments + seg
            b = ring * segments + (seg + 1) % segments
            c = (ring + 1) * segments + (seg + 1) % segments
            d = (ring + 1) * segments + seg
            if ring == 0:
                faces.append((a, c, d))
            elif ring == rings - 1:
                faces.append((a, b, c))
            else:
                faces.append((a, b, c, d))
    return vertices, faces


def build_cylinder(
    size: tuple[float, float, float] = (1, 1, 1), segments: int = 12
) -> tuple[list[Vertex], list[Face]]:
    rx, ry, rz = size[0] / 2, size[1] / 2, size[2]
    vertices: list[Vertex] = []
    for cap_z in (-rz / 2, rz / 2):
        for seg in range(segments):
            phi = 2 * math.pi * seg / segments
            vertices.append((rx * math.cos(phi), ry * math.sin(phi), cap_z))
    bottom_center = len(vertices)
    vertices.append((0, 0, -rz / 2))
    top_center = len(vertices)
    vertices.append((0, 0, rz / 2))

    faces: list[Face] = []
    for seg in range(segments):
        b0, b1 = seg, (seg + 1) % segments
        t0, t1 = segments + seg, segments + (seg + 1) % segments
        faces.append((b0, b1, t1, t0))
        faces.append((bottom_center, b1, b0))
        faces.append((top_center, t0, t1))
    return vertices, faces


def build_cone(
    size: tuple[float, float, float] = (1, 1, 1), segments: int = 12
) -> tuple[list[Vertex], list[Face]]:
    rx, ry, rz = size[0] / 2, size[1] / 2, size[2]
    vertices: list[Vertex] = []
    for seg in range(segments):
        phi = 2 * math.pi * seg / segments
        vertices.append((rx * math.cos(phi), ry * math.sin(phi), -rz / 2))
    apex = len(vertices)
    vertices.append((0, 0, rz / 2))
    base_center = len(vertices)
    vertices.append((0, 0, -rz / 2))

    faces: list[Face] = []
    for seg in range(segments):
        b0, b1 = seg, (seg + 1) % segments
        faces.append((b0, b1, apex))
        faces.append((base_center, b1, b0))
    return vertices, faces


def build_capsule(
    size: tuple[float, float, float] = (1, 1, 1), segments: int = 12, rings: int = 4
) -> tuple[list[Vertex], list[Face]]:
    """Cilindro com hemisférios nas duas pontas — ideal para membros
    (braços/pernas) de personagens low poly."""
    radius = min(size[0], size[1]) / 2
    total_height = size[2]
    cyl_height = max(total_height - 2 * radius, radius * 0.2)

    vertices: list[Vertex] = []
    ring_indices: list[list[int]] = []

    def add_ring(z: float, r: float) -> list[int]:
        idx = []
        for seg in range(segments):
            phi = 2 * math.pi * seg / segments
            vertices.append((r * math.cos(phi), r * math.sin(phi), z))
            idx.append(len(vertices) - 1)
        return idx

    # hemisfério inferior (rings anéis, de baixo pra cima)
    for i in range(rings + 1):
        theta = math.pi / 2 * (i / rings)  # 0 (polo) .. pi/2 (equador)
        z = -cyl_height / 2 - radius * math.cos(theta)
        r = radius * math.sin(theta)
        ring_indices.append(add_ring(z, max(r, 1e-6)))

    # topo do cilindro (mesmo raio do equador)
    ring_indices.append(add_ring(cyl_height / 2, radius))

    # hemisfério superior
    for i in range(1, rings + 1):
        theta = math.pi / 2 * (i / rings)
        z = cyl_height / 2 + radius * math.sin(theta)
        r = radius * math.cos(theta)
        ring_indices.append(add_ring(z, max(r, 1e-6)))

    faces: list[Face] = []
    for r0, r1 in zip(ring_indices, ring_indices[1:]):
        for seg in range(segments):
            a, b = r0[seg], r0[(seg + 1) % segments]
            c, d = r1[(seg + 1) % segments], r1[seg]
            faces.append((a, b, c, d))
    return vertices, faces


def build_torus(
    size: tuple[float, float, float] = (1, 1, 1),
    major_segments: int = 16,
    minor_segments: int = 8,
) -> tuple[list[Vertex], list[Face]]:
    major_r = size[0] / 2
    minor_r = size[2] / 2
    vertices: list[Vertex] = []
    for i in range(major_segments):
        phi = 2 * math.pi * i / major_segments
        for j in range(minor_segments):
            theta = 2 * math.pi * j / minor_segments
            x = (major_r + minor_r * math.cos(theta)) * math.cos(phi)
            y = (major_r + minor_r * math.cos(theta)) * math.sin(phi)
            z = minor_r * math.sin(theta)
            vertices.append((x, y, z))

    faces: list[Face] = []
    for i in range(major_segments):
        for j in range(minor_segments):
            a = i * minor_segments + j
            b = ((i + 1) % major_segments) * minor_segments + j
            c = ((i + 1) % major_segments) * minor_segments + (j + 1) % minor_segments
            d = i * minor_segments + (j + 1) % minor_segments
            faces.append((a, b, c, d))
    return vertices, faces


def build_bezier_curve_points(
    size: tuple[float, float, float] = (1, 1, 1), resolution: int = 12
) -> tuple[list[Vertex], list[Face]]:
    """Retorna pontos de controle de uma curva Bézier cúbica simples (não é
    uma malha fechada — usada para elementos tipo cabo/haste/cauda)."""
    sx, sy, sz = size
    p0 = (-sx / 2, 0, -sz / 2)
    p1 = (-sx / 4, sy / 2, 0)
    p2 = (sx / 4, -sy / 2, 0)
    p3 = (sx / 2, 0, sz / 2)

    points: list[Vertex] = []
    for i in range(resolution + 1):
        t = i / resolution
        mt = 1 - t
        x = mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0] + t**3 * p3[0]
        y = mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1] + t**3 * p3[1]
        z = mt**3 * p0[2] + 3 * mt**2 * t * p1[2] + 3 * mt * t**2 * p2[2] + t**3 * p3[2]
        points.append((x, y, z))
    # sem faces — consumidor (blender_export) decide como tratar (curve object)
    return points, []


PRIMITIVE_BUILDERS: dict[str, Callable[..., tuple[list[Vertex], list[Face]]]] = {
    "cube": build_cube,
    "plane": build_plane,
    "sphere": build_uv_sphere,
    "cylinder": build_cylinder,
    "cone": build_cone,
    "capsule": build_capsule,
    "torus": build_torus,
    "bezier": build_bezier_curve_points,
    "curve": build_bezier_curve_points,
}
