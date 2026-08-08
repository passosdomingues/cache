import pytest

from blender_compiler.config import GeometryConfig
from blender_compiler.geometry.pipeline import generate_geometry
from blender_compiler.geometry.primitives import (
    PRIMITIVE_BUILDERS,
    build_capsule,
    build_cone,
    build_cube,
    build_cylinder,
    build_torus,
    build_uv_sphere,
)
from blender_compiler.schemas import (
    PartMaterial,
    PrimitiveType,
    SceneGraphEdge,
    SceneGraphModel,
    SceneGraphNode,
    Vec3,
)


@pytest.mark.parametrize(
    "builder",
    [build_cube, build_uv_sphere, build_cylinder, build_cone, build_capsule, build_torus],
)
def test_primitive_builders_produce_valid_mesh(builder):
    vertices, faces = builder(size=(1.0, 1.0, 1.0))
    assert len(vertices) > 0
    assert len(faces) > 0
    max_index = max(i for face in faces for i in face)
    assert max_index < len(vertices)
    for face in faces:
        assert len(set(face)) == len(face)  # sem vértices repetidos numa face


def test_all_registered_primitives_are_buildable():
    for name, builder in PRIMITIVE_BUILDERS.items():
        vertices, faces = builder(size=(1.0, 1.0, 1.0))
        assert len(vertices) > 0, f"primitiva '{name}' não gerou vértices"


def test_generate_geometry_from_scene_graph():
    scene = SceneGraphModel(
        object_name="test",
        nodes=[
            SceneGraphNode(
                id="torso",
                label="torso",
                primitive=PrimitiveType.CUBE,
                position=Vec3(x=0, y=0, z=0),
                size=Vec3(x=1, y=1, z=1),
                material=PartMaterial(),
            ),
            SceneGraphNode(
                id="head",
                label="head",
                primitive=PrimitiveType.SPHERE,
                position=Vec3(x=0, y=0, z=1),
                size=Vec3(x=0.5, y=0.5, z=0.5),
                material=PartMaterial(),
            ),
        ],
        edges=[SceneGraphEdge(source="torso", target="head")],
    )
    geometry = generate_geometry(scene, GeometryConfig(), is_character=True)

    assert len(geometry.meshes) == 2
    head_mesh = next(m for m in geometry.meshes if m.node_id == "head")
    assert head_mesh.parent_id == "torso"
    assert head_mesh.primitive == PrimitiveType.SPHERE
    assert len(head_mesh.vertices) > 0
