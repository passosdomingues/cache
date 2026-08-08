"""Módulo de exportação para OpenSCAD (.scad) e STL (.stl).

Converte a estrutura de primitivas geométricas do GeometryModel em um script
OpenSCAD determinístico e limpo.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

from blender_compiler.config import OpenSCADConfig
from blender_compiler.schemas import GeometryModel, MeshData, PrimitiveType

logger = logging.getLogger("blender_compiler.blender_export.openscad")


class OpenSCADExporter:
    def __init__(self, config: OpenSCADConfig | None = None):
        self.cfg = config or OpenSCADConfig()
        self.executable = self.cfg.executable if shutil.which(self.cfg.executable) else "openscad"

    def is_available(self) -> bool:
        return bool(shutil.which(self.executable))

    def generate_scad_code(self, geometry: GeometryModel) -> str:
        lines = [
            f"// OpenSCAD CSG Model: {geometry.object_name}",
            "// Gerado automaticamente por Blender Compiler",
            f"$fn = {self.cfg.fn};",
            "",
            f"module {geometry.object_name}() {{",
            "    union() {",
        ]

        for mesh in geometry.meshes:
            mesh_scad = self._mesh_to_scad(mesh)
            for line in mesh_scad.splitlines():
                lines.append(f"        {line}")

        lines.append("    }")
        lines.append("}")
        lines.append("")
        lines.append(f"{geometry.object_name}();")
        return "\n".join(lines)

    def _mesh_to_scad(self, mesh: MeshData) -> str:
        pos = mesh.position
        rot = mesh.rotation_euler
        sc = mesh.scale
        color = mesh.material.color_rgb
        r, g, b = color[0] / 255.0, color[1] / 255.0, color[2] / 255.0

        primitive_code = self._primitive_scad(mesh)

        scad_obj = f"color([{r:.2f}, {g:.2f}, {b:.2f}]) translate([{pos.x:.3f}, {pos.y:.3f}, {pos.z:.3f}]) rotate([{rot.x:.1f}, {rot.y:.1f}, {rot.z:.1f}]) scale([{sc.x:.3f}, {sc.y:.3f}, {sc.z:.3f}]) {primitive_code};"
        return scad_obj

    def _primitive_scad(self, mesh: MeshData) -> str:
        p = mesh.primitive
        if p == PrimitiveType.EXTRUDED_SILHOUETTE and mesh.vertices and mesh.faces:
            pts = ", ".join([f"[{v[0]:.3f}, {v[1]:.3f}, {v[2]:.3f}]" for v in mesh.vertices])
            fcs = ", ".join([f"[{', '.join(map(str, f))}]" for f in mesh.faces])
            return f"polyhedron(points=[{pts}], faces=[{fcs}])"
        elif p == PrimitiveType.SPHERE:
            return "sphere(r=0.5)"
        elif p == PrimitiveType.CYLINDER:
            return "cylinder(h=1.0, r=0.5, center=true)"
        elif p == PrimitiveType.CONE:
            return "cylinder(h=1.0, r1=0.5, r2=0.0, center=true)"
        elif p == PrimitiveType.CAPSULE:
            return "union() { cylinder(h=1.0, r=0.4, center=true); translate([0,0,0.5]) sphere(r=0.4); translate([0,0,-0.5]) sphere(r=0.4); }"
        else:  # CUBE / PLANE / fallback
            return "cube([1.0, 1.0, 1.0], center=true)"

    def export_scad(self, geometry: GeometryModel, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        scad_path = output_dir / f"{geometry.object_name}.scad"
        code = self.generate_scad_code(geometry)
        scad_path.write_text(code, encoding="utf-8")
        logger.info(f"OpenSCAD gerado em: {scad_path}")

        if self.cfg.render_stl and self.is_available():
            stl_path = output_dir / f"{geometry.object_name}.stl"
            self.render_stl(scad_path, stl_path)

        return scad_path

    def render_stl(self, scad_path: Path, stl_path: Path) -> bool:
        cmd = [self.executable, "-o", str(stl_path), str(scad_path)]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
            logger.info(f"STL renderizado via OpenSCAD em: {stl_path}")
            return True
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logger.warning(f"Falha ao renderizar STL via OpenSCAD: {e}")
            return False
