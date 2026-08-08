"""Fallback sem Blender: escreve um .obj (+ .mtl) puro-Python a partir do
GeometryModel. Usado quando o executável `blender` não está no PATH (ex:
ambiente de desenvolvimento sem Blender instalado) para que o pipeline
continue produzindo uma saída 3D válida e inspecionável, mesmo sem gerar
o `.blend` final. Em produção (Docker), o Blender real é usado e este
fallback não é acionado.
"""

from __future__ import annotations

from pathlib import Path

from blender_compiler.schemas import GeometryModel


def export_obj_fallback(geometry: GeometryModel, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    obj_path = out_dir / f"{geometry.object_name}.obj"
    mtl_path = out_dir / f"{geometry.object_name}.mtl"

    obj_lines = [f"mtllib {mtl_path.name}"]
    mtl_lines = []
    vertex_offset = 1  # OBJ é 1-indexado

    for mesh in geometry.meshes:
        if not mesh.faces:
            continue
        mat_name = mesh.material.name or f"mat_{mesh.node_id}"
        obj_lines.append(f"o {mesh.node_id}")
        obj_lines.append(f"usemtl {mat_name}")
        for vx, vy, vz in mesh.vertices:
            wx = vx + mesh.position.x
            wy = vy + mesh.position.y
            wz = vz + mesh.position.z
            obj_lines.append(f"v {wx:.6f} {wy:.6f} {wz:.6f}")
        for face in mesh.faces:
            idx = " ".join(str(i + vertex_offset) for i in face)
            obj_lines.append(f"f {idx}")
        vertex_offset += len(mesh.vertices)

        r, g, b = mesh.material.color_rgb
        mtl_lines.append(f"newmtl {mat_name}")
        mtl_lines.append(f"Kd {r/255:.4f} {g/255:.4f} {b/255:.4f}")
        mtl_lines.append(f"Pr {mesh.material.roughness:.4f}")
        mtl_lines.append("")

    obj_path.write_text("\n".join(obj_lines), encoding="utf-8")
    mtl_path.write_text("\n".join(mtl_lines), encoding="utf-8")
    return obj_path
