"""Etapa 6 — Geometry Generator (orquestração).

Percorre o `SceneGraphModel` (Etapa 5) e converte cada nó em uma `MeshData`
concreta, escolhendo o builder de primitiva apropriado e aplicando
escala/posição. Não conhece nada de Blender — produz apenas dados de malha
agnósticos de motor 3D.
"""

from __future__ import annotations

import logging

from blender_compiler.config import GeometryConfig
from blender_compiler.geometry.primitives import PRIMITIVE_BUILDERS
from blender_compiler.schemas import GeometryModel, MeshData, SceneGraphModel

logger = logging.getLogger("blender_compiler.geometry")


def generate_geometry(
    scene: SceneGraphModel, cfg: GeometryConfig, is_character: bool = False
) -> GeometryModel:
    meshes: list[MeshData] = []
    edge_by_target = {}
    for node in scene.nodes:
        builder = PRIMITIVE_BUILDERS.get(node.primitive.value)
        if builder is None:
            logger.warning(f"Primitiva desconhecida '{node.primitive}' para nó {node.id}; usando cube.")
            builder = PRIMITIVE_BUILDERS["cube"]

        size = (
            max(node.size.x, 0.05) * cfg.global_scale,
            max(node.size.y, 0.05) * cfg.global_scale,
            max(node.size.z, 0.05) * cfg.global_scale,
        )
        kwargs = _builder_kwargs(node.primitive.value, cfg)
        vertices, faces = builder(size=size, **kwargs)

        meshes.append(
            MeshData(
                node_id=node.id,
                primitive=node.primitive,
                vertices=vertices,
                faces=faces,
                position=node.position,
                material=node.material,
                parent_id=None,
            )
        )

    for edge in scene.edges:
        edge_by_target[edge.target] = edge.source
    for mesh in meshes:
        mesh.parent_id = edge_by_target.get(mesh.node_id)

    return GeometryModel(
        object_name=scene.object_name,
        meshes=meshes,
        is_character=is_character,
        armature_bones=scene.edges if is_character else [],
    )


def _builder_kwargs(primitive: str, cfg: GeometryConfig) -> dict:
    if primitive == "sphere":
        return {"segments": cfg.subdivisions_sphere, "rings": max(cfg.subdivisions_sphere // 2, 4)}
    if primitive in {"cylinder", "cone", "capsule"}:
        return {"segments": cfg.subdivisions_cylinder}
    if primitive == "torus":
        return {
            "major_segments": cfg.subdivisions_cylinder,
            "minor_segments": max(cfg.subdivisions_cylinder // 2, 6),
        }
    return {}
