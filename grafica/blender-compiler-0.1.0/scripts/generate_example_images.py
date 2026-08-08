#!/usr/bin/env python3
"""Gera um conjunto de imagens sintéticas (silhueta humanoide simplificada,
6 ângulos) em examples/input/, para permitir rodar a demo sem depender de
fotos reais. Útil também como fixture reprodutível para CI.

Uso:
    python3 scripts/generate_example_images.py [--out examples/input]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


def draw_humanoid_silhouette(width: int = 400, height: int = 600) -> np.ndarray:
    img = np.full((height, width, 3), 255, np.uint8)
    cx = width // 2
    color = (60, 90, 200)  # BGR

    cv2.circle(img, (cx, 90), 55, color, -1)  # cabeça
    cv2.rectangle(img, (cx - 70, 150), (cx + 70, 360), color, -1)  # torso
    cv2.rectangle(img, (cx - 120, 160), (cx - 70, 340), color, -1)  # braço esquerdo
    cv2.rectangle(img, (cx + 70, 160), (cx + 120, 340), color, -1)  # braço direito
    cv2.rectangle(img, (cx - 65, 360), (cx - 8, 580), color, -1)  # perna esquerda
    cv2.rectangle(img, (cx + 8, 360), (cx + 65, 580), color, -1)  # perna direita
    return img


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="examples/input", help="Diretório de saída")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    for name in ["front", "back", "left", "right", "45_left", "45_right"]:
        img = draw_humanoid_silhouette()
        cv2.imwrite(str(out_dir / f"{name}.png"), img)
        print(f"  gerado: {out_dir / f'{name}.png'}")

    print(f"OK — imagens de exemplo geradas em {out_dir}")


if __name__ == "__main__":
    main()
