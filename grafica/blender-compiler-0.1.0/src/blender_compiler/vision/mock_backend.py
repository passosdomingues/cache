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

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            c = max(contours, key=cv2.contourArea)
            x_c, y_c, w_c, h_c = cv2.boundingRect(c)

            # Região principal do contorno como objeto extrudado fiel
            regions.append(_region("main_silhouette", x_c, y_c, w_c, h_c, w, h))

            if object_hint == "humanoid":
                head_w = bw * 0.4
                regions.append(_region("head", x + (bw - head_w) / 2, y, head_w, bh * 0.15, w, h))
                torso_w = bw * 0.56
                regions.append(_region("torso", x + (bw - torso_w) / 2, y + bh * 0.15, torso_w, bh * 0.35, w, h))
                regions.append(_region("left_arm", x, y + bh * 0.17, bw * 0.22, bh * 0.33, w, h))
                regions.append(_region("right_arm", x + bw * 0.78, y + bh * 0.17, bw * 0.22, bh * 0.33, w, h))
                regions.append(_region("left_leg", x, y + bh * 0.55, bw * 0.45, bh * 0.45, w, h))
                regions.append(_region("right_leg", x + bw * 0.55, y + bh * 0.55, bw * 0.45, bh * 0.45, w, h))
            else:
                # Se o contorno for amplo nas laterais em relação à altura, adiciona regiões de asas/extensões
                if w_c > h_c * 0.6:
                    wings_y = y_c + h_c * 0.2
                    wings_h = h_c * 0.5
                    regions.append(_region("left_wing", x_c, wings_y, w_c * 0.35, wings_h, w, h))
                    regions.append(_region("right_wing", x_c + w_c * 0.65, wings_y, w_c * 0.35, wings_h, w, h))

                head_h = h_c * 0.25
                head_w = w_c * 0.4
                regions.append(_region("head", x_c + (w_c - head_w) / 2, y_c, head_w, head_h, w, h))

                torso_y = y_c + head_h
                torso_h = h_c * 0.45
                regions.append(_region("torso", x_c + w_c * 0.2, torso_y, w_c * 0.6, torso_h, w, h))

                base_y = torso_y + torso_h
                base_h = h_c - (head_h + torso_h)
                if base_h > 0:
                    regions.append(_region("base", x_c + w_c * 0.15, base_y, w_c * 0.7, base_h, w, h))
        else:
            regions.append(_region("body", x, y, bw, bh, w, h))

        for r in regions:
            r.dominant_color_rgb = _dominant_color(view.normalized_path, r.bbox, w, h)

        return VisionViewAnalysis(
            view_angle=view.view_angle,
            regions=regions,
            is_symmetrical_guess=True,
            raw_backend_output={"heuristic": "contour_decomposition", "aspect_ratio": aspect},
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
