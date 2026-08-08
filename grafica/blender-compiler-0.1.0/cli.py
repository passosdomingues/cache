# ruff: noqa: B008  -- typer.Argument()/typer.Option() em defaults é o padrão idiomático do Typer
"""CLI do Blender Compiler.

Exemplos:
    python cli.py compile input/
    python cli.py preprocess input/ --output output/
    python cli.py reconstruct output/
    python cli.py export output/
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import typer
from rich.table import Table

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from blender_compiler.blender_export.openscad import OpenSCADExporter  # noqa: E402
from blender_compiler.blender_export.pipeline import export_geometry  # noqa: E402
from blender_compiler.config import load_config  # noqa: E402
from blender_compiler.geometry.pipeline import generate_geometry  # noqa: E402
from blender_compiler.mpi_runner import run_mpi_compile  # noqa: E402
from blender_compiler.pipeline import compile_object  # noqa: E402
from blender_compiler.preprocessing.pipeline import run_preprocessing  # noqa: E402
from blender_compiler.scenegraph.pipeline import (  # noqa: E402
    build_scene_graph,
    save_scene_graph,
    to_scene_graph_model,
)
from blender_compiler.semantic.pipeline import reconstruct_semantics  # noqa: E402
from blender_compiler.utils.logging_utils import console, setup_logging  # noqa: E402
from blender_compiler.vision.pipeline import run_vision  # noqa: E402

app = typer.Typer(
    name="blender-compiler",
    help="Compilador de geometria procedural: imagens -> .blend / .scad (low poly, 100% CLI/open-source).",
    add_completion=False,
)


@app.command()
def compile(
    input_dir: Path = typer.Argument(
        ..., help="Diretório com as imagens de entrada (front.png, back.png, ...)"
    ),
    output: Path = typer.Option(Path("output"), "--output", "-o", help="Diretório de saída"),
    name: str = typer.Option("object", "--name", "-n", help="Nome do objeto/personagem"),
    config: Path | None = typer.Option(None, "--config", "-c", help="Caminho para YAML de configuração"),
    use_imagemagick: bool = typer.Option(False, "--use-imagemagick", help="Usar ImageMagick no pré-processamento"),
    backend: str | None = typer.Option(None, "--backend", "-b", help="Backend de visão: mock, ollama, qwen_vl, etc"),
    render_stl: bool = typer.Option(False, "--render-stl", help="Renderizar arquivo STL via OpenSCAD"),
) -> None:
    """Executa o pipeline completo: images -> .blend / .scad."""
    cfg = load_config(config)
    if use_imagemagick:
        cfg.preprocessing.background_removal_method = "imagemagick"
        cfg.preprocessing.use_imagemagick = True
    if backend:
        cfg.vision.backend = backend
    if render_stl:
        cfg.openscad.render_stl = True

    setup_logging(cfg.logging.log_dir, cfg.logging.level)
    result = compile_object(input_dir, output, cfg, object_name=name)
    _print_export_summary(result, output, name)


@app.command()
def mpi_compile(
    input_dir: Path = typer.Argument(..., help="Diretório com imagens de entrada"),
    output: Path = typer.Option(Path("output"), "--output", "-o"),
    name: str = typer.Option("object", "--name", "-n"),
    workers: int = typer.Option(4, "--workers", "-w", help="Número de processos trabalhadores MPI"),
    config: Path | None = typer.Option(None, "--config", "-c"),
) -> None:
    """Executa compilação paralela distribuída via MPI."""
    code = run_mpi_compile(input_dir, output, num_workers=workers, object_name=name, config_path=config)
    if code != 0:
        console.print(f"[bold red]Erro:[/bold red] MPI runner finalizou com código {code}")
        raise typer.Exit(code=code)


@app.command()
def openscad_export(
    output: Path = typer.Argument(..., help="Diretório de saída contendo 03_geometry/<nome>.scene.json"),
    name: str = typer.Option("object", "--name", "-n"),
    config: Path | None = typer.Option(None, "--config", "-c"),
    render_stl: bool = typer.Option(False, "--render-stl", help="Renderizar arquivo STL"),
) -> None:
    """Gera script OpenSCAD (.scad) e opcionalmente STL a partir do arquivo de cena."""
    cfg = load_config(config)
    setup_logging(cfg.logging.log_dir, cfg.logging.level)

    scene_path = output / "03_geometry" / f"{name}.scene.json"
    if not scene_path.exists():
        console.print(f"[bold red]Erro:[/bold red] {scene_path} não encontrado.")
        raise typer.Exit(code=1)

    from blender_compiler.schemas import GeometryModel

    geometry = GeometryModel(**json.loads(scene_path.read_text(encoding="utf-8")))
    cfg.openscad.render_stl = render_stl or cfg.openscad.render_stl
    exporter = OpenSCADExporter(cfg.openscad)
    scad_path = exporter.export_scad(geometry, output / "04_export")
    console.print(f"[bold green]OK[/bold green] — OpenSCAD exportado em {scad_path}")


@app.command()
def preprocess(
    input_dir: Path = typer.Argument(..., help="Diretório com as imagens de entrada"),
    output: Path = typer.Option(Path("output"), "--output", "-o"),
    name: str = typer.Option("object", "--name", "-n"),
    config: Path | None = typer.Option(None, "--config", "-c"),
) -> None:
    """Executa apenas a Etapa 2 (Pre Processing)."""
    cfg = load_config(config)
    setup_logging(cfg.logging.log_dir, cfg.logging.level)
    result = run_preprocessing(input_dir, output, cfg.preprocessing, name)
    (output / "01_preprocessing" / "_result.json").write_text(
        result.model_dump_json(indent=2), encoding="utf-8"
    )
    console.print(
        f"[bold green]OK[/bold green] — {len(result.views)} views processadas em {output/'01_preprocessing'}"
    )


@app.command()
def reconstruct(
    output: Path = typer.Argument(..., help="Diretório de saída já contendo 01_preprocessing/"),
    name: str = typer.Option("object", "--name", "-n"),
    config: Path | None = typer.Option(None, "--config", "-c"),
) -> None:
    """Executa Vision + Semantic Reconstruction + Scene Graph (Etapas 3-5) a
    partir de um output/ já pré-processado."""
    cfg = load_config(config)
    setup_logging(cfg.logging.log_dir, cfg.logging.level)

    pre_dir = output / "01_preprocessing"
    result_json = pre_dir / "_result.json"
    if not result_json.exists():
        console.print(f"[bold red]Erro:[/bold red] {result_json} não existe. Rode 'preprocess' primeiro.")
        raise typer.Exit(code=1)

    from blender_compiler.schemas import PreprocessingResult

    preprocessing_result = PreprocessingResult(**json.loads(result_json.read_text(encoding="utf-8")))

    object_hint = cfg.semantic.default_object_class
    vision_result = run_vision(preprocessing_result, cfg.vision, object_hint=object_hint)
    (output / "02_vision").mkdir(parents=True, exist_ok=True)
    (output / "02_vision" / "analysis.json").write_text(
        vision_result.model_dump_json(indent=2), encoding="utf-8"
    )

    semantic_model = reconstruct_semantics(vision_result, cfg.semantic, name)
    semantic_dir = output / "02b_semantic"
    semantic_dir.mkdir(parents=True, exist_ok=True)
    (semantic_dir / "semantic_model.json").write_text(
        semantic_model.model_dump_json(indent=2), encoding="utf-8"
    )

    graph = build_scene_graph(semantic_model)
    save_scene_graph(graph, output / "03_scenegraph")
    scene_graph_model = to_scene_graph_model(graph)

    geometry_model = generate_geometry(
        scene_graph_model, cfg.geometry, is_character=semantic_model.is_character
    )
    geometry_dir = output / "03_geometry"
    geometry_dir.mkdir(parents=True, exist_ok=True)
    (geometry_dir / f"{name}.scene.json").write_text(
        geometry_model.model_dump_json(indent=2), encoding="utf-8"
    )

    console.print(
        f"[bold green]OK[/bold green] — {len(semantic_model.parts)} partes, "
        f"{len(scene_graph_model.nodes)} nós no scene graph, {len(geometry_model.meshes)} meshes geradas."
    )


@app.command()
def export(
    output: Path = typer.Argument(..., help="Diretório de saída já contendo 03_geometry/<nome>.scene.json"),
    name: str = typer.Option("object", "--name", "-n"),
    config: Path | None = typer.Option(None, "--config", "-c"),
) -> None:
    """Executa apenas a Etapa 7/8 (Blender export) a partir de uma geometria já gerada."""
    cfg = load_config(config)
    setup_logging(cfg.logging.log_dir, cfg.logging.level)

    scene_path = output / "03_geometry" / f"{name}.scene.json"
    if not scene_path.exists():
        console.print(f"[bold red]Erro:[/bold red] {scene_path} não encontrado. Rode 'compile' antes.")
        raise typer.Exit(code=1)

    from blender_compiler.schemas import GeometryModel

    geometry = GeometryModel(**json.loads(scene_path.read_text(encoding="utf-8")))
    result = export_geometry(geometry, output, cfg.blender, cfg.rig, openscad_cfg=cfg.openscad)
    _print_export_summary(result, output, name)


def _print_export_summary(result, output_dir: Path | None = None, object_name: str = "object") -> None:
    table = Table(title=f"Export: {result.object_name}")
    table.add_column("Artefato")
    table.add_column("Caminho")

    scad_path = None
    stl_path = None
    if output_dir:
        sp = output_dir / "04_export" / f"{object_name}.scad"
        if sp.exists():
            scad_path = str(sp)
        tp = output_dir / "04_export" / f"{object_name}.stl"
        if tp.exists():
            stl_path = str(tp)

    for label, path in [
        (".blend", result.blend_path),
        (".scad", scad_path),
        (".stl", stl_path),
        ("glTF", result.gltf_path),
        ("FBX", result.fbx_path),
        ("OBJ", result.obj_path),
    ]:
        if path:
            table.add_row(label, path)
    console.print(table)
    console.print(f"Blender usado: {'sim' if result.used_blender else 'não (fallback OBJ/OpenSCAD)'}")
    console.print(f"Rig gerado: {'sim' if result.rigged else 'não'}")
    for w in result.warnings:
        console.print(f"[yellow]⚠ {w}[/yellow]")


if __name__ == "__main__":
    app()

