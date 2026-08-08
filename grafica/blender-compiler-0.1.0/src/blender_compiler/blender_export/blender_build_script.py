"""Script de build executado pelo Blender headless.

Uso:
    blender --background --factory-startup --python blender_build_script.py -- \
        --scene <scene.json> --out-dir <dir> --object-name <nome> \
        [--gltf] [--fbx] [--obj] [--collections] [--uv] [--rig]

Este é o ÚNICO arquivo do projeto que importa `bpy`. Ele roda dentro do
processo do Blender (Etapa 7/8), lendo a representação intermediária em
JSON produzida pelas camadas Python "normais" (Etapas 1-6), que rodam fora
do Blender. Isso mantém a Etapa 7 isolada e testável de forma independente.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy  # type: ignore


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--object-name", default="object")
    parser.add_argument("--gltf", action="store_true")
    parser.add_argument("--fbx", action="store_true")
    parser.add_argument("--obj", action="store_true")
    parser.add_argument("--collections", action="store_true")
    parser.add_argument("--uv", action="store_true")
    parser.add_argument("--rig", action="store_true")
    return parser.parse_args(argv)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block_collection in (bpy.data.meshes, bpy.data.materials, bpy.data.armatures):
        for block in list(block_collection):
            if block.users == 0:
                block_collection.remove(block)


def get_or_create_collection(name: str) -> bpy.types.Collection:
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    return coll


def make_material(name: str, color_rgb: list[int], roughness: float, metallic: float):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    r, g, b = (c / 255.0 for c in color_rgb)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (r, g, b, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
    mat.diffuse_color = (r, g, b, 1.0)
    return mat


def build_mesh_object(mesh_data: dict, collection) -> bpy.types.Object:
    name = mesh_data["node_id"]
    verts = [tuple(v) for v in mesh_data["vertices"]]
    faces = [tuple(f) for f in mesh_data["faces"] if len(f) >= 3]

    mesh = bpy.data.meshes.new(f"mesh_{name}")
    mesh.from_pydata(verts, [], faces)
    mesh.update(calc_edges=True)

    obj = bpy.data.objects.new(name, mesh)
    pos = mesh_data["position"]
    obj.location = (pos["x"], pos["y"], pos["z"])
    collection.objects.link(obj)

    mat_info = mesh_data["material"]
    mat_name = mat_info.get("name") or f"mat_{name}"
    mat = make_material(
        mat_name, mat_info["color_rgb"], mat_info.get("roughness", 0.6), mat_info.get("metallic", 0.0)
    )
    obj.data.materials.append(mat)
    return obj


def generate_uvs(obj) -> None:
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")


def build_armature(geometry: dict, objects_by_id: dict) -> bpy.types.Object | None:
    bones = geometry.get("armature_bones", [])
    if not bones:
        return None

    arm_data = bpy.data.armatures.new("Armature")
    arm_obj = bpy.data.objects.new("Armature", arm_data)
    bpy.context.scene.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="EDIT")

    edit_bones = arm_data.edit_bones
    created = {}
    for edge in bones:
        src, tgt = edge["source"], edge["target"]
        if src not in objects_by_id or tgt not in objects_by_id:
            continue
        if src not in created:
            b = edit_bones.new(src)
            b.head = objects_by_id[src].location
            b.tail = objects_by_id[src].location.copy()
            b.tail.z += 0.15
            created[src] = b
        if tgt not in created:
            b = edit_bones.new(tgt)
            b.head = objects_by_id[tgt].location
            b.tail = objects_by_id[tgt].location.copy()
            b.tail.z += 0.15
            b.parent = created[src]
            created[tgt] = b

    bpy.ops.object.mode_set(mode="OBJECT")

    for obj_id, obj in objects_by_id.items():
        if obj_id not in created:
            continue
        obj.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    try:
        bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    except RuntimeError:
        bpy.ops.object.parent_set(type="ARMATURE_NAME")
    bpy.ops.object.select_all(action="DESELECT")
    return arm_obj


def main() -> None:
    args = parse_args()
    clear_scene()

    scene_path = Path(args.scene)
    geometry = json.loads(scene_path.read_text(encoding="utf-8"))

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    collection = (
        get_or_create_collection(args.object_name) if args.collections else bpy.context.scene.collection
    )

    objects_by_id = {}
    for mesh_data in geometry["meshes"]:
        if not mesh_data["faces"]:
            continue  # curvas/bezier sem faces tratadas fora do escopo desta versão do rig
        obj = build_mesh_object(mesh_data, collection)
        objects_by_id[mesh_data["node_id"]] = obj
        if args.uv:
            try:
                generate_uvs(obj)
            except RuntimeError:
                pass

    for mesh_data in geometry["meshes"]:
        parent_id = mesh_data.get("parent_id")
        node_id = mesh_data["node_id"]
        if parent_id and parent_id in objects_by_id and node_id in objects_by_id:
            objects_by_id[node_id].parent = objects_by_id[parent_id]

    if args.rig and geometry.get("is_character"):
        build_armature(geometry, objects_by_id)

    blend_path = out_dir / f"{args.object_name}.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    bpy.ops.object.select_all(action="SELECT")

    if args.gltf:
        bpy.ops.export_scene.gltf(filepath=str(out_dir / f"{args.object_name}.glb"), use_selection=False)
    if args.obj:
        obj_path = out_dir / f"{args.object_name}.obj"
        try:
            bpy.ops.wm.obj_export(filepath=str(obj_path), export_selected_objects=False)
        except AttributeError:
            bpy.ops.export_scene.obj(filepath=str(obj_path), use_selection=False)
    if args.fbx:
        bpy.ops.export_scene.fbx(filepath=str(out_dir / f"{args.object_name}.fbx"), use_selection=False)

    print(f"BLENDER_BUILD_OK:{blend_path}")


if __name__ == "__main__":
    main()
