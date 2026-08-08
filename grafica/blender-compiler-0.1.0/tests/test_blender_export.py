import shutil

import pytest

from blender_compiler.blender_export.fallback_obj import export_obj_fallback
from blender_compiler.blender_export.pipeline import export_geometry
from blender_compiler.config import BlenderConfig, RigConfig
from blender_compiler.geometry.primitives import build_cube
from blender_compiler.schemas import GeometryModel, MeshData, PartMaterial, PrimitiveType, Vec3


def _simple_geometry(is_character: bool = False) -> GeometryModel:
    vertices, faces = build_cube(size=(1, 1, 1))
    mesh = MeshData(
        node_id="body",
        primitive=PrimitiveType.CUBE,
        vertices=vertices,
        faces=faces,
        position=Vec3(x=0, y=0, z=0),
        material=PartMaterial(color_rgb=(200, 50, 50), name="mat_body"),
    )
    return GeometryModel(object_name="test_obj", meshes=[mesh], is_character=is_character)


def test_export_obj_fallback_writes_valid_obj(tmp_path):
    geometry = _simple_geometry()
    obj_path = export_obj_fallback(geometry, tmp_path)

    assert obj_path.exists()
    content = obj_path.read_text()
    assert "o body" in content
    assert content.count("v ") == 8  # cubo tem 8 vértices
    mtl_path = tmp_path / "test_obj.mtl"
    assert mtl_path.exists()
    assert "mat_body" in mtl_path.read_text()


def test_export_geometry_uses_fallback_when_blender_missing(tmp_path):
    geometry = _simple_geometry()
    cfg = BlenderConfig(executable="blender_binary_that_does_not_exist_xyz")
    result = export_geometry(geometry, tmp_path, cfg, RigConfig())

    assert result.used_blender is False
    assert result.obj_path is not None
    assert result.warnings


@pytest.mark.skipif(shutil.which("blender") is None, reason="Blender não instalado neste ambiente")
def test_export_geometry_with_real_blender(tmp_path):
    geometry = _simple_geometry(is_character=False)
    cfg = BlenderConfig(export_gltf=True, export_obj=True, export_fbx=False)
    result = export_geometry(geometry, tmp_path, cfg, RigConfig())

    assert result.used_blender is True
    assert result.blend_path is not None
    from pathlib import Path

    assert Path(result.blend_path).exists()
