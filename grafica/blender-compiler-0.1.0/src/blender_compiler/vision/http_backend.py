"""Backend HTTP genérico para servidores de Vision LLM locais/remotos
(Ollama, vLLM, LM Studio, servidores OpenAI-compatíveis, etc).

Qwen-VL, Llama-Vision, MiniCPM-V e Moondream reaproveitam esta mesma classe,
diferindo apenas no `model_name` e no prompt de sistema — por isso nenhuma
lógica nova é necessária para "adicionar um modelo": basta apontar
`vision.model_name` na configuração.
"""

from __future__ import annotations

import base64
import json
import logging
import os
import urllib.error
import urllib.request

from blender_compiler.schemas import DetectedRegion, PreprocessedView, VisionViewAnalysis
from blender_compiler.vision.base import VisionBackend
from blender_compiler.vision.mock_backend import MockVisionBackend

logger = logging.getLogger("blender_compiler.vision.http")

_SYSTEM_PROMPT = """Você é um analisador de geometria de objetos/personagens a partir de imagens.
Responda APENAS em JSON válido, no formato:
{"regions": [{"label": "head", "bbox": [x, y, w, h], "confidence": 0.9, "notes": "..."}]}
Coordenadas do bbox são normalizadas entre 0 e 1 (origem no canto superior esquerdo).
Use labels como: head, torso, left_arm, right_arm, left_leg, right_leg, body, base, wheel, etc,
conforme o que for visível na imagem. Nunca gere vértices ou malhas — apenas regiões 2D."""


class HttpVisionBackend(VisionBackend):
    """Cliente HTTP para um servidor de inferência multimodal compatível com a
    API `/api/generate` (Ollama) ou `/v1/chat/completions` (OpenAI-like).
    """

    name = "http_generic"

    def __init__(
        self,
        endpoint: str,
        model_name: str,
        timeout_seconds: int = 60,
        api_key_env: str | None = None,
    ) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds
        self.api_key = os.environ.get(api_key_env) if api_key_env else None
        self._fallback = MockVisionBackend()

    def analyze_view(self, view: PreprocessedView, object_hint: str = "") -> VisionViewAnalysis:
        try:
            image_b64 = _encode_image(view.normalized_path)
            payload = self._build_payload(image_b64, object_hint)
            response = self._request(payload)
            regions = _parse_regions(response)
            return VisionViewAnalysis(
                view_angle=view.view_angle,
                regions=regions,
                raw_backend_output={"model": self.model_name},
            )
        except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            logger.warning(
                f"Backend HTTP '{self.model_name}' indisponível ({exc}). "
                f"Usando fallback heurístico (mock) para {view.view_angle.value}."
            )
            return self._fallback.analyze_view(view, object_hint=object_hint)

    def _build_payload(self, image_b64: str, object_hint: str) -> dict:
        prompt = _SYSTEM_PROMPT
        if object_hint:
            prompt += f"\nContexto adicional: o objeto é do tipo '{object_hint}'."
        return {
            "model": self.model_name,
            "prompt": prompt,
            "images": [image_b64],
            "stream": False,
            "format": "json",
        }

    def _request(self, payload: dict) -> str:
        url = f"{self.endpoint}/api/generate"
        data = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return body.get("response", "{}")


def _encode_image(path: str) -> str:
    with open(path, "rb") as fh:
        return base64.b64encode(fh.read()).decode("ascii")


def _parse_regions(raw_json: str) -> list[DetectedRegion]:
    data = json.loads(raw_json)
    regions = []
    for r in data.get("regions", []):
        bbox = tuple(r.get("bbox", [0, 0, 1, 1]))
        regions.append(
            DetectedRegion(
                label=r.get("label", "part"),
                bbox=bbox,  # type: ignore[arg-type]
                confidence=float(r.get("confidence", 0.5)),
                notes=r.get("notes", ""),
            )
        )
    return regions


# Aliases nomeados: cada "modelo suportado" é apenas uma pré-configuração
# desta mesma classe genérica, cumprindo o requisito de nunca depender de
# um modelo específico. Novos modelos = nova entrada aqui, zero lógica nova.
KNOWN_MODEL_DEFAULTS: dict[str, dict[str, str]] = {
    "qwen_vl": {"model_name": "qwen2.5-vl"},
    "llama_vision": {"model_name": "llama3.2-vision"},
    "minicpm": {"model_name": "minicpm-v"},
    "moondream": {"model_name": "moondream"},
}
