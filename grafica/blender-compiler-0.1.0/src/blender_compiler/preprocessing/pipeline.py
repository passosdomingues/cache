"""Etapa 2 — Pre Processing.

Responsabilidade única: transformar imagens brutas em um conjunto de
artefatos normalizados (máscara, silhueta, bordas, hint de profundidade).
Esta camada NUNCA interpreta semântica — apenas visão computacional clássica.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import cv2
import numpy as np

from blender_compiler.config import PreprocessingConfig
from blender_compiler.schemas import PreprocessedView, PreprocessingResult, ViewAngle

logger = logging.getLogger("blender_compiler.preprocessing")

_ANGLE_PATTERNS = {
    ViewAngle.FRONT: r"front",
    ViewAngle.BACK: r"back",
    ViewAngle.FORTY_FIVE_LEFT: r"45.?left",
    ViewAngle.FORTY_FIVE_RIGHT: r"45.?right",
    ViewAngle.LEFT: r"^left|_left",
    ViewAngle.RIGHT: r"^right|_right",
    ViewAngle.TOP: r"top",
    ViewAngle.BOTTOM: r"bottom",
}


def infer_view_angle(filename: str) -> ViewAngle:
    stem = Path(filename).stem.lower()
    for angle, pattern in _ANGLE_PATTERNS.items():
        if re.search(pattern, stem):
            return angle
    return ViewAngle.UNKNOWN


def _remove_background(img: np.ndarray, method: str) -> np.ndarray:
    """Retorna uma máscara binária (255 = objeto, 0 = fundo)."""
    h, w = img.shape[:2]
    if method == "imagemagick":
        from blender_compiler.preprocessing.imagemagick import ImageMagickPreprocessor
        im = ImageMagickPreprocessor()
        if im.is_available():
            # cria arquivo temp de mascara via convert
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = Path(tmp.name)
            tmp_in = Path(tmp_path.parent / f"tmp_in_{tmp_path.name}")
            cv2.imwrite(str(tmp_in), img)
            if im.generate_mask(tmp_in, tmp_path):
                mask = cv2.imread(str(tmp_path), cv2.IMREAD_GRAYSCALE)
                tmp_in.unlink(missing_ok=True)
                tmp_path.unlink(missing_ok=True)
                if mask is not None:
                    return mask
            tmp_in.unlink(missing_ok=True)
            tmp_path.unlink(missing_ok=True)

    if method == "threshold":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        return mask

    if method == "chroma_key":
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # assume fundo verde/branco puro nos cantos
        corner_samples = np.concatenate([hsv[0:10, 0:10].reshape(-1, 3), hsv[0:10, -10:].reshape(-1, 3)])
        bg_color = np.median(corner_samples, axis=0)
        lower = np.clip(bg_color - np.array([15, 60, 60]), 0, 255)
        upper = np.clip(bg_color + np.array([15, 60, 60]), 0, 255)
        bg_mask = cv2.inRange(hsv, lower, upper)
        return cv2.bitwise_not(bg_mask)

    # default: grabcut
    mask = np.zeros((h, w), np.uint8)
    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    margin = int(min(h, w) * 0.04)
    rect = (margin, margin, w - 2 * margin, h - 2 * margin)
    try:
        cv2.grabCut(img, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
    except cv2.error:
        # fallback se a imagem for pequena/degenerada demais para grabcut
        return _remove_background(img, "threshold")
    binary = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype("uint8")
    return binary


def _clean_mask(mask: np.ndarray) -> np.ndarray:
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        biggest = max(contours, key=cv2.contourArea)
        clean = np.zeros_like(mask)
        cv2.drawContours(clean, [biggest], -1, 255, thickness=cv2.FILLED)
        return clean
    return mask


def _depth_hint(gray: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Heurística simples de profundidade: distância euclidiana ao contorno
    da silhueta (objetos "mais grossos" no meio => mais próximos da câmera).
    Não é reconstrução 3D real — apenas um sinal auxiliar para a camada
    Semantic estimar espessura relativa das partes.
    """
    dist = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
    if dist.max() > 0:
        dist = (dist / dist.max() * 255).astype("uint8")
    else:
        dist = dist.astype("uint8")
    return dist


def preprocess_image(
    image_path: Path,
    out_dir: Path,
    cfg: PreprocessingConfig,
) -> PreprocessedView:
    img = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Não foi possível ler a imagem: {image_path}")

    h, w = img.shape[:2]
    scale = cfg.target_size / max(h, w)
    if scale != 1.0:
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    h, w = img.shape[:2]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if cfg.equalize_histogram:
        gray = cv2.equalizeHist(gray)

    mask = _remove_background(img, cfg.background_removal_method)
    mask = _clean_mask(mask)

    silhouette = cv2.bitwise_and(img, img, mask=mask)
    edges = cv2.Canny(gray, cfg.canny_threshold1, cfg.canny_threshold2)
    depth_hint = _depth_hint(gray, mask)

    ys, xs = np.where(mask > 0)
    if len(xs) > 0:
        bbox = (int(xs.min()), int(ys.min()), int(xs.max() - xs.min()), int(ys.max() - ys.min()))
    else:
        bbox = (0, 0, w, h)
    fill_ratio = float((mask > 0).sum() / (h * w))

    view_angle = infer_view_angle(image_path.name)
    stem = image_path.stem
    view_dir = out_dir / stem
    view_dir.mkdir(parents=True, exist_ok=True)

    normalized_path = view_dir / "normalized.png"
    mask_path = view_dir / "mask.png"
    silhouette_path = view_dir / "silhouette.png"
    edges_path = view_dir / "edges.png"
    depth_path = view_dir / "depth_hint.png"

    if cfg.save_intermediates:
        cv2.imwrite(str(normalized_path), img)
        cv2.imwrite(str(mask_path), mask)
        cv2.imwrite(str(silhouette_path), silhouette)
        cv2.imwrite(str(edges_path), edges)
        cv2.imwrite(str(depth_path), depth_hint)

    logger.debug(f"{image_path.name}: view={view_angle.value} bbox={bbox} fill={fill_ratio:.2f}")

    return PreprocessedView(
        view_angle=view_angle,
        source_path=str(image_path),
        normalized_path=str(normalized_path),
        mask_path=str(mask_path),
        silhouette_path=str(silhouette_path),
        edges_path=str(edges_path),
        depth_hint_path=str(depth_path),
        width=w,
        height=h,
        bbox=bbox,
        fill_ratio=fill_ratio,
    )


def run_preprocessing(
    input_dir: Path,
    output_dir: Path,
    cfg: PreprocessingConfig,
    object_name: str = "object",
) -> PreprocessingResult:
    image_paths = sorted(
        p for p in input_dir.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    )
    if not image_paths:
        raise FileNotFoundError(f"Nenhuma imagem encontrada em {input_dir}")

    out_dir = output_dir / "01_preprocessing"
    out_dir.mkdir(parents=True, exist_ok=True)

    views = [preprocess_image(p, out_dir, cfg) for p in image_paths]
    return PreprocessingResult(object_name=object_name, views=views)
