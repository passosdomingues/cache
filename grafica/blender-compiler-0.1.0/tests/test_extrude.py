"""Testes unitários para gerador de extrusão 3D de contorno."""

import pytest
from blender_compiler.geometry.extrude import create_extruded_polygon_mesh


def test_create_extruded_polygon_mesh_basic():
    # Triângulo
    poly = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
    verts, faces = create_extruded_polygon_mesh(poly, depth=0.5)

    # 3 vértices na frente + 3 atrás = 6 vértices
    assert len(verts) == 6
    # 3 quads laterais + 2 tampas (frente e trás) = 5 faces
    assert len(faces) == 5

    # Checa posições Z
    z_coords = [v[2] for v in verts]
    assert min(z_coords) == pytest.approx(-0.25)
    assert max(z_coords) == pytest.approx(0.25)


def test_create_extruded_polygon_mesh_degenerate():
    # Menos de 3 pontos
    poly = [(0.0, 0.0), (1.0, 1.0)]
    verts, faces = create_extruded_polygon_mesh(poly, depth=0.2)

    # Retorna cubo fallback
    assert len(verts) == 8
    assert len(faces) == 6
