"""Gerador de malha 3D por extrusão de contornos poligonais 2D.

Recebe um conjunto de pontos 2D (normalizados ou em coordenadas de imagem)
e constrói uma malha 3D (vértices e faces) extrudando o contorno ao longo do eixo Z.
"""

from __future__ import annotations

import logging
from typing import List, Tuple

logger = logging.getLogger("blender_compiler.geometry.extrude")


def create_extruded_polygon_mesh(
    polygon_2d: List[Tuple[float, float]],
    depth: float = 0.4,
) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, ...]]]:
    """Cria vértices e faces para um polígono 2D extrudado em Z.

    Args:
        polygon_2d: Lista de (x, y) formando o contorno fechado em sentido anti-horário ou horário.
        depth: Espessura da extrusão (profundidade em Z).

    Returns:
        (vertices, faces)
        vertices: Lista de (x, y, z)
        faces: Lista de tuplas de índices de vértices.
    """
    n = len(polygon_2d)
    if n < 3:
        # Fallback para cubo simples se contorno degenerado
        return [
            (-0.5, -0.5, -depth / 2), (0.5, -0.5, -depth / 2),
            (0.5, 0.5, -depth / 2), (-0.5, 0.5, -depth / 2),
            (-0.5, -0.5, depth / 2), (0.5, -0.5, depth / 2),
            (0.5, 0.5, depth / 2), (-0.5, 0.5, depth / 2),
        ], [
            (0, 1, 2, 3), (4, 7, 6, 5),
            (0, 4, 5, 1), (1, 5, 6, 2),
            (2, 6, 7, 3), (3, 7, 4, 0),
        ]

    half_depth = depth / 2.0
    vertices: List[Tuple[float, float, float]] = []

    # Vértices da tampa frontal (z = -half_depth)
    for x, y in polygon_2d:
        vertices.append((float(x), float(y), -half_depth))

    # Vértices da tampa traseira (z = +half_depth)
    for x, y in polygon_2d:
        vertices.append((float(x), float(y), half_depth))

    faces: List[Tuple[int, ...]] = []

    # Faces laterais (quads conectando i e (i+1)%n)
    for i in range(n):
        next_i = (i + 1) % n
        v0 = i
        v1 = next_i
        v2 = next_i + n
        v3 = i + n
        faces.append((v0, v1, v2, v3))

    # Tampa frontal (face 0 até n-1 invertida para normal externa)
    front_face = tuple(range(n - 1, -1, -1))
    faces.append(front_face)

    # Tampa traseira (face n até 2n-1)
    back_face = tuple(range(n, 2 * n))
    faces.append(back_face)

    return vertices, faces
