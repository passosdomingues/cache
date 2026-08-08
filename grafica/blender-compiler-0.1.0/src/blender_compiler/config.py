"""Carregamento de configuração. Nenhum parâmetro deve ficar hardcoded no
código das camadas — tudo vem de config/default.yaml (ou override do usuário)."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


import shutil

class PreprocessingConfig(BaseModel):
    target_size: int = 1024
    background_removal_method: str = "grabcut"  # grabcut | threshold | chroma_key | imagemagick
    use_imagemagick: bool = False
    convert_executable: str = "convert"
    canny_threshold1: int = 50
    canny_threshold2: int = 150
    equalize_histogram: bool = True
    save_intermediates: bool = True


class VisionConfig(BaseModel):
    backend: str = "mock"  # mock | qwen_vl | llama_vision | minicpm | moondream | http_generic | ollama
    endpoint: str | None = "http://localhost:11434"
    model_name: str | None = "qwen2.5-vl"
    timeout_seconds: int = 60
    api_key_env: str | None = None


class SemanticConfig(BaseModel):
    default_object_class: str = "humanoid"
    enforce_symmetry: bool = True
    min_part_confidence: float = 0.3


class GeometryConfig(BaseModel):
    default_primitive: str = "cube"
    subdivisions_sphere: int = 16
    subdivisions_cylinder: int = 12
    low_poly_bevel_segments: int = 0
    global_scale: float = 1.0


class BlenderConfig(BaseModel):
    executable: str = "/opt/blender-4.5.5-lts/blender"
    export_gltf: bool = True
    export_fbx: bool = False
    export_obj: bool = True
    use_collections: bool = True
    generate_uv: bool = True

    def resolve_executable(self) -> str | None:
        """Retorna o caminho do executável do Blender se encontrado."""
        if shutil.which(self.executable):
            return self.executable
        # Se for o padrão "blender" ou caminho em /opt, tenta localizar em /opt
        if self.executable == "blender" or self.executable.startswith("/opt"):
            opt_candidates = list(Path("/opt").glob("blender*/blender"))
            for candidate in opt_candidates:
                if candidate.is_file() and candidate.stat().st_mode & 0o111:
                    return str(candidate)
        return None


class OpenSCADConfig(BaseModel):
    executable: str = "openscad"
    export_scad: bool = True
    render_stl: bool = False
    fn: int = 16


class MPIConfig(BaseModel):
    enabled: bool = False
    num_workers: int = 4


class RigConfig(BaseModel):
    enabled_for_characters: bool = True
    auto_weights: bool = True
    bone_layer_name: str = "Rig"


class LoggingConfig(BaseModel):
    level: str = "INFO"
    log_dir: str = "logs"
    json_logs: bool = False


class PipelineConfig(BaseModel):
    input_dir: str = "input"
    output_dir: str = "output"
    preprocessing: PreprocessingConfig = Field(default_factory=PreprocessingConfig)
    vision: VisionConfig = Field(default_factory=VisionConfig)
    semantic: SemanticConfig = Field(default_factory=SemanticConfig)
    geometry: GeometryConfig = Field(default_factory=GeometryConfig)
    blender: BlenderConfig = Field(default_factory=BlenderConfig)
    openscad: OpenSCADConfig = Field(default_factory=OpenSCADConfig)
    mpi: MPIConfig = Field(default_factory=MPIConfig)
    rig: RigConfig = Field(default_factory=RigConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)



DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "default.yaml"


def load_config(path: str | Path | None = None) -> PipelineConfig:
    cfg_path = Path(path) if path else DEFAULT_CONFIG_PATH
    if not cfg_path.exists():
        return PipelineConfig()
    with open(cfg_path, encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    return PipelineConfig(**raw)
