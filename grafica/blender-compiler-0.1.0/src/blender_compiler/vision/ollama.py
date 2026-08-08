"""Backend de visão específico para Ollama local (ex: Qwen2.5-VL / Moondream).

Especializa o HttpVisionBackend fornecendo prompts estruturados para decomposição
de imagens em primitivas low-poly (cubos, esferas, cilindros, extrusões de silhueta).
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import urllib.request
from blender_compiler.vision.http_backend import HttpVisionBackend

logger = logging.getLogger("blender_compiler.vision.ollama")

_OLLAMA_SYSTEM_PROMPT = """Você é um especialista em visão computacional e reconstrução 3D low-poly.
Analise a imagem e identifique a estrutura exata do objeto/personagem (asas, coroa, silhueta principal, membros, acessórios).
Responda APENAS em JSON válido no formato:
{
  "regions": [
    {"label": "main_silhouette", "bbox": [0.1, 0.05, 0.8, 0.9], "confidence": 0.95, "notes": "corpo principal com contornos"},
    {"label": "left_wing", "bbox": [0.0, 0.2, 0.35, 0.5], "confidence": 0.9, "notes": "asa esquerda"},
    {"label": "right_wing", "bbox": [0.65, 0.2, 0.35, 0.5], "confidence": 0.9, "notes": "asa direita"},
    {"label": "head_crown", "bbox": [0.35, 0.05, 0.3, 0.2], "confidence": 0.85, "notes": "cabeça e coroa"}
  ]
}
Bbox normalizada de [0,0] (topo esquerdo) a [1,1] (inferior direito)."""


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
        self._ensure_server_running()

    def _ensure_server_running(self) -> None:
        """Verifica se o servidor Ollama está respondendo. Se não, tenta iniciar via `ollama serve`."""
        try:
            req = urllib.request.Request(f"{self.endpoint}/api/tags")
            with urllib.request.urlopen(req, timeout=2):
                logger.info(f"Ollama server respondendo em {self.endpoint}")
                return
        except Exception:
            logger.info("Servidor Ollama não respondeu. Tentando iniciar 'ollama serve'...")

        ollama_bin = shutil.which("ollama")
        if ollama_bin:
            try:
                subprocess.Popen(
                    [ollama_bin, "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                logger.info("Iniciado 'ollama serve' em segundo plano.")
            except Exception as e:
                logger.warning(f"Não foi possível auto-iniciar Ollama serve: {e}")

    def _build_payload(self, image_b64: str, object_hint: str) -> dict:
        prompt = _OLLAMA_SYSTEM_PROMPT
        if object_hint:
            prompt += f"\nContexto adicional: objeto do tipo '{object_hint}'."
        return {
            "model": self.model_name,
            "prompt": prompt,
            "images": [image_b64],
            "stream": False,
            "format": "json",
        }
