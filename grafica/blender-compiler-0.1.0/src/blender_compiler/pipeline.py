"""Orquestrador do pipeline completo: liga as 8 camadas em sequência.

images -> Pre Processing -> Vision -> Semantic Reconstruction -> Scene Graph
-> Geometry Generator -> Blender bpy -> .blend

Cada etapa é uma função independente importada de seu próprio módulo;
este arquivo apenas ORQUESTRA, sem conter lógica de domínio.
"""

from __future__ import annotations

import logging
from pathlib import Path

from blender_compiler.blender_export.pipeline import export_geometry
from blender_compiler.config import PipelineConfig
from blender_compiler.geometry.pipeline import generate_geometry
from blender_compiler.preprocessing.pipeline import run_preprocessing
from blender_compiler.scenegraph.pipeline import build_scene_graph, save_scene_graph, to_scene_graph_model
from blender_compiler.schemas import ExportResult
from blender_compiler.semantic.pipeline import reconstruct_semantics
from blender_compiler.utils.logging_utils import stage
from blender_compiler.vision.pipeline import run_vision

logger = logging.getLogger("blender_compiler.pipeline")


def compile_object(
    input_dir: Path,
    output_dir: Path,
    cfg: PipelineConfig,
    object_name: str = "object",
) -> ExportResult:
    output_dir.mkdir(parents=True, exist_ok=True)

    with stage(logger, "1/7 Pre Processing"):
        preprocessing_result = run_preprocessing(input_dir, output_dir, cfg.preprocessing, object_name)
        logger.info(f"{len(preprocessing_result.views)} views processadas.")

    with stage(logger, "2/7 Vision"):
        object_hint = cfg.semantic.default_object_class
        vision_result = run_vision(preprocessing_result, cfg.vision, object_hint=object_hint)
        (output_dir / "02_vision").mkdir(parents=True, exist_ok=True)
        (output_dir / "02_vision" / "analysis.json").write_text(
            vision_result.model_dump_json(indent=2), encoding="utf-8"
        )

    with stage(logger, "3/7 Semantic Reconstruction"):
        semantic_model = reconstruct_semantics(vision_result, cfg.semantic, object_name)
        (output_dir / "02_vision").parent.mkdir(parents=True, exist_ok=True)
        semantic_dir = output_dir / "02b_semantic"
        semantic_dir.mkdir(parents=True, exist_ok=True)
        (semantic_dir / "semantic_model.json").write_text(
            semantic_model.model_dump_json(indent=2), encoding="utf-8"
        )
        logger.info(
            f"{len(semantic_model.parts)} partes reconstruídas | classe={semantic_model.object_class}"
        )

    with stage(logger, "4/7 Scene Graph"):
        graph = build_scene_graph(semantic_model)
        save_scene_graph(graph, output_dir / "03_scenegraph")
        scene_graph_model = to_scene_graph_model(graph)
        logger.info(f"{len(scene_graph_model.nodes)} nós, {len(scene_graph_model.edges)} arestas.")

    with stage(logger, "5/7 Geometry Generator"):
        geometry_model = generate_geometry(
            scene_graph_model, cfg.geometry, is_character=semantic_model.is_character
        )
        total_verts = sum(len(m.vertices) for m in geometry_model.meshes)
        logger.info(f"{len(geometry_model.meshes)} meshes geradas | {total_verts} vértices totais.")

    with stage(logger, "6/7 Blender Export"):
        export_result = export_geometry(geometry_model, output_dir, cfg.blender, cfg.rig)
        if export_result.used_blender:
            logger.info(f"[bold green]Arquivo .blend gerado:[/bold green] {export_result.blend_path}")
        else:
            logger.warning("Blender indisponível — apenas OBJ de fallback foi gerado.")

    with stage(logger, "7/7 Finalização"):
        result_path = output_dir / "export_result.json"
        result_path.write_text(export_result.model_dump_json(indent=2), encoding="utf-8")

    return export_result
