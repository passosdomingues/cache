"""Backend de visão específico para Ollama local (ex: Qwen2.5-VL / LLaMA3.2-Vision).

Especializa o HttpVisionBackend fornecendo prompts estruturados para decomposição
de imagens em primitivas low-poly (cubos, esferas, cilindros).
"""

from __future__ import annotations

import logging
from blender_compiler.vision.http_backend import HttpVisionBackend

logger = logging.getLogger("blender_compiler.vision.ollama")


class OllamaVisionBackend(HttpVisionBackend):
    """Backend de visão conectado ao servidor Ollama local (default: http://localhost:11434)."""

    name = "ollama"

    def __init__(
        self,
        endpoint: str = "http://localhost:11434",
        model_name: str = "qwen2.5-vl",
        timeout_seconds: int = 60,
    ) -> None:
        super().__init__(
            endpoint=endpoint,
            model_name=model_name,
            timeout_seconds=timeout_seconds,
        )
