"""Backend 'mock': não usa nenhum modelo de IA. Usa heurísticas clássicas de
visão computacional (contornos, proporções da bounding box) para estimar
regiões plausíveis de um humanoide/objeto genérico a partir da silhueta.

Serve para: desenvolvimento sem GPU, testes automatizados determinísticos,
e como fallback quando nenhum servidor de Vision LLM está disponível.
"""

from __future__ import annotations

import cv2

from blender_compiler.schemas import DetectedRegion, PreprocessedView, VisionViewAnalysis
from blender_compiler.vision.base import VisionBackend


class MockVisionBackend(VisionBackend):
    name = "mock"

    def analyze_view(self, view: PreprocessedView, object_hint: str = "") -> VisionViewAnalysis:
        mask = cv2.imread(view.mask_path, cv2.IMREAD_GRAYSCALE)
        regions: list[DetectedRegion] = []

        if mask is None or mask.sum() == 0:
            return VisionViewAnalysis(view_angle=view.view_angle, regions=[], is_symmetrical_guess=True)

        h, w = mask.shape
        x, y, bw, bh = view.bbox
        aspect = bh / max(bw, 1)

        if object_hint == "humanoid" or aspect > 1.4:
            # Heurística proporcional de figura humana: cabeça ~15% da altura
            # do corpo, com largura própria (não a largura total do corpo),
            # torso ~35%, pernas ~40%, braços ao lado do torso.
            head_w = bw * 0.4
            regions.append(_region("head", x + (bw - head_w) / 2, y, head_w, bh * 0.15, w, h))
            torso_w = bw * 0.56
            regions.append(_region("torso", x + (bw - torso_w) / 2, y + bh * 0.15, torso_w, bh * 0.35, w, h))
            regions.append(_region("left_arm", x, y + bh * 0.17, bw * 0.22, bh * 0.33, w, h))
            regions.append(_region("right_arm", x + bw * 0.78, y + bh * 0.17, bw * 0.22, bh * 0.33, w, h))
            regions.append(_region("left_leg", x, y + bh * 0.55, bw * 0.45, bh * 0.45, w, h))
            regions.append(_region("right_leg", x + bw * 0.55, y + bh * 0.55, bw * 0.45, bh * 0.45, w, h))
        else:
            # Objeto genérico: divide a silhueta em uma única região "body"
            regions.append(_region("body", x, y, bw, bh, w, h))

        for r in regions:
            r.dominant_color_rgb = _dominant_color(view.normalized_path, r.bbox, w, h)

        return VisionViewAnalysis(
            view_angle=view.view_angle,
            regions=regions,
            is_symmetrical_guess=True,
            raw_backend_output={"heuristic": "bbox_proportions", "aspect_ratio": aspect},
        )


def _region(label: str, x: float, y: float, w: float, h: float, img_w: int, img_h: int) -> DetectedRegion:
    return DetectedRegion(
        label=label,
        bbox=(x / img_w, y / img_h, w / img_w, h / img_h),
        confidence=0.55,
        notes="estimado por heurística geométrica (mock backend)",
    )


def _dominant_color(image_path: str, bbox_norm, img_w: int, img_h: int) -> tuple[int, int, int]:
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        return (180, 180, 180)
    x, y, w, h = bbox_norm
    x0, y0 = int(x * img_w), int(y * img_h)
    x1, y1 = int((x + w) * img_w), int((y + h) * img_h)
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(img_w, max(x1, x0 + 1)), min(img_h, max(y1, y0 + 1))
    crop = img[y0:y1, x0:x1]
    if crop.size == 0:
        return (180, 180, 180)
    mean_bgr = crop.reshape(-1, 3).mean(axis=0)
    b, g, r = mean_bgr
    return (int(r), int(g), int(b))
