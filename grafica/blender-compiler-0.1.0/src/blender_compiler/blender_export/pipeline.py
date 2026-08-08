"""Etapa 7 (Blender) e Etapa 8 (Rig opcional) — orquestração.

Estratégia: em vez de depender do pacote pip `bpy` (pesado, versão fixa e
não-oficial), invocamos o executável real do Blender em modo headless via
subprocess, o que é a forma suportada e recomendada de automação do
Blender via CLI. Se o executável não estiver disponível no ambiente
(ex: dev local sem Blender), a camada usa graciosamente um fallback
puro-Python que exporta OBJ, para nunca travar o pipeline.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

from blender_compiler.blender_export.fallback_obj import export_obj_fallback
from blender_compiler.blender_export.openscad import OpenSCADExporter
from blender_compiler.config import BlenderConfig, OpenSCADConfig, RigConfig
from blender_compiler.schemas import ExportResult, GeometryModel

logger = logging.getLogger("blender_compiler.blender_export")

_BUILD_SCRIPT = Path(__file__).resolve().parent / "blender_build_script.py"


def _serialize_scene(geometry: GeometryModel, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    scene_path = out_dir / f"{geometry.object_name}.scene.json"
    scene_path.write_text(geometry.model_dump_json(indent=2), encoding="utf-8")
    return scene_path


def export_geometry(
    geometry: GeometryModel,
    output_dir: Path,
    blender_cfg: BlenderConfig,
    rig_cfg: RigConfig,
    openscad_cfg: OpenSCADConfig | None = None,
) -> ExportResult:
    export_dir = output_dir / "04_export"
    scene_path = _serialize_scene(geometry, output_dir / "03_geometry")

    # Export OpenSCAD se ativado ou disponível
    scad_exporter = OpenSCADExporter(openscad_cfg)
    scad_path = scad_exporter.export_scad(geometry, export_dir)

    blender_bin = blender_cfg.resolve_executable()
    if not blender_bin:
        logger.warning(
            f"Executável '{blender_cfg.executable}' não encontrado. "
            "Usando fallback OBJ puro-Python e OpenSCAD. "
        )
        obj_path = export_obj_fallback(geometry, export_dir)
        return ExportResult(
            object_name=geometry.object_name,
            obj_path=str(obj_path),
            used_blender=False,
            warnings=["Blender não encontrado; .blend/.glb/.fbx não gerados nesta execução."],
        )

    should_rig = geometry.is_character and rig_cfg.enabled_for_characters

    cmd = [
        blender_bin,
        "--background",
        "--factory-startup",
        "--python",
        str(_BUILD_SCRIPT),
        "--",
        "--scene",
        str(scene_path),
        "--out-dir",
        str(export_dir),
        "--object-name",
        geometry.object_name,
    ]
    if blender_cfg.export_gltf:
        cmd.append("--gltf")
    if blender_cfg.export_fbx:
        cmd.append("--fbx")
    if blender_cfg.export_obj:
        cmd.append("--obj")
    if blender_cfg.use_collections:
        cmd.append("--collections")
    if blender_cfg.generate_uv:
        cmd.append("--uv")
    if should_rig:
        cmd.append("--rig")

    logger.info(f"Executando Blender headless: {' '.join(cmd)}")
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    logger.debug(proc.stdout)
    if proc.returncode != 0:
        logger.error(proc.stderr)
        raise RuntimeError(f"Blender falhou (código {proc.returncode}). Ver logs para stderr completo.")

    blend_path = export_dir / f"{geometry.object_name}.blend"
    result = ExportResult(
        object_name=geometry.object_name,
        blend_path=str(blend_path) if blend_path.exists() else None,
        gltf_path=str(export_dir / f"{geometry.object_name}.glb") if blender_cfg.export_gltf else None,
        fbx_path=str(export_dir / f"{geometry.object_name}.fbx") if blender_cfg.export_fbx else None,
        obj_path=str(export_dir / f"{geometry.object_name}.obj") if blender_cfg.export_obj else None,
        used_blender=True,
        rigged=should_rig,
    )
    return result
