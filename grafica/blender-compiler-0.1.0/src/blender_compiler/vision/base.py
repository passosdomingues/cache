"""Etapa 3 — Vision.

Define o contrato `VisionBackend` que qualquer modelo de Vision LLM deve
implementar. O pipeline nunca depende de um backend específico — apenas
desta interface. Trocar de Qwen-VL para Moondream é uma questão de config
(`vision.backend` em config/default.yaml), não de código.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from blender_compiler.schemas import PreprocessedView, VisionViewAnalysis


class VisionBackend(ABC):
    """Contrato que todo backend de visão (LLM multimodal ou heurístico) implementa."""

    name: str = "base"

    @abstractmethod
    def analyze_view(self, view: PreprocessedView, object_hint: str = "") -> VisionViewAnalysis:
        """Analisa uma única imagem pré-processada e retorna regiões detectadas."""
        raise NotImplementedError

    def analyze_views(self, views: list[PreprocessedView], object_hint: str = "") -> list[VisionViewAnalysis]:
        return [self.analyze_view(v, object_hint=object_hint) for v in views]
