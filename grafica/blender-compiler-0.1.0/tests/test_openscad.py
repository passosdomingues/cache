"""Testes unitários para o gerador e exportador OpenSCAD."""

import pytest
from pathlib import Path
from blender_compiler.blender_export.openscad import OpenSCADExporter
from blender_compiler.config import OpenSCADConfig
from blender_compiler.schemas import GeometryModel, MeshData, PartMaterial, PrimitiveType, Vec3


def test_openscad_code_generation():
    mesh = MeshData(
        node_id="cube_1",
        primitive=PrimitiveType.CUBE,
        vertices=[],
        faces=[],
        position=Vec3(x=0, y=0, z=1.0),
        material=PartMaterial(color_rgb=(255, 0, 0)),
    )
    geometry = GeometryModel(object_name="test_box", meshes=[mesh])

    exporter = OpenSCADExporter(OpenSCADConfig(fn=12))
    scad_code = exporter.generate_scad_code(geometry)

    assert "module test_box()" in scad_code
    assert "color([1.00, 0.00, 0.00])" in scad_code
    assert "cube([1.0, 1.0, 1.0]" in scad_code
    assert "$fn = 12;" in scad_code


def test_openscad_export_file(tmp_path: Path):
    mesh = MeshData(
        node_id="sphere_1",
        primitive=PrimitiveType.SPHERE,
        vertices=[],
        faces=[],
        position=Vec3(x=1, y=2, z=3),
        material=PartMaterial(),
    )
    geometry = GeometryModel(object_name="sphere_obj", meshes=[mesh])

    exporter = OpenSCADExporter(OpenSCADConfig())
    scad_file = exporter.export_scad(geometry, tmp_path)

    assert scad_file.exists()
    assert scad_file.name == "sphere_obj.scad"
    content = scad_file.read_text(encoding="utf-8")
    assert "sphere(r=0.5)" in content
