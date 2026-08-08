"""Ponto de entrada da Etapa 3 — Vision. Escolhe o backend via config e
executa a análise sobre todas as views pré-processadas."""

from __future__ import annotations

from blender_compiler.config import VisionConfig
from blender_compiler.schemas import PreprocessingResult, VisionAnalysisResult
from blender_compiler.vision.base import VisionBackend
from blender_compiler.vision.http_backend import KNOWN_MODEL_DEFAULTS, HttpVisionBackend
from blender_compiler.vision.mock_backend import MockVisionBackend


def build_backend(cfg: VisionConfig) -> VisionBackend:
    """Factory: instancia o backend de visão configurado. Adicionar um novo
    backend não-HTTP é feito registrando aqui uma nova classe que implementa
    `VisionBackend` — o resto do pipeline não muda."""
    if cfg.backend == "mock":
        return MockVisionBackend()

    if cfg.backend == "ollama":
        from blender_compiler.vision.ollama import OllamaVisionBackend

        return OllamaVisionBackend(
            endpoint=cfg.endpoint or "http://localhost:11434",
            model_name=cfg.model_name or "qwen2.5-vl",
            timeout_seconds=cfg.timeout_seconds,
        )

    if cfg.backend in KNOWN_MODEL_DEFAULTS or cfg.backend == "http_generic":
        defaults = KNOWN_MODEL_DEFAULTS.get(cfg.backend, {})
        model_name = cfg.model_name or defaults.get("model_name", "vision-model")
        return HttpVisionBackend(
            endpoint=cfg.endpoint or "http://localhost:11434",
            model_name=model_name,
            timeout_seconds=cfg.timeout_seconds,
            api_key_env=cfg.api_key_env,
        )

    raise ValueError(
        f"Backend de visão desconhecido: '{cfg.backend}'. "
        f"Opções: mock, http_generic, {', '.join(KNOWN_MODEL_DEFAULTS)}"
    )


def run_vision(
    preprocessing_result: PreprocessingResult,
    cfg: VisionConfig,
    object_hint: str = "",
) -> VisionAnalysisResult:
    backend = build_backend(cfg)
    analyses = backend.analyze_views(preprocessing_result.views, object_hint=object_hint)
    return VisionAnalysisResult(
        object_name=preprocessing_result.object_name,
        backend_name=backend.name if backend.name != "http_generic" else cfg.model_name or "http",
        views=analyses,
    )
