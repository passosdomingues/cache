import sys
from pathlib import Path

import cv2
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


@pytest.fixture()
def synthetic_humanoid_images(tmp_path: Path) -> Path:
    """Gera um pequeno conjunto de imagens sintéticas (silhueta humanoide)
    para usar como fixture determinística em testes de integração."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    def draw(flip_x: bool = False) -> np.ndarray:
        img = np.full((300, 200, 3), 255, np.uint8)
        cx = 100
        color = (60, 90, 200)
        cv2.circle(img, (cx, 40), 25, color, -1)
        cv2.rectangle(img, (cx - 30, 65), (cx + 30, 160), color, -1)
        cv2.rectangle(img, (cx - 50, 70), (cx - 30, 150), color, -1)
        cv2.rectangle(img, (cx + 30, 70), (cx + 50, 150), color, -1)
        cv2.rectangle(img, (cx - 28, 160), (cx - 3, 260), color, -1)
        cv2.rectangle(img, (cx + 3, 160), (cx + 28, 260), color, -1)
        return img

    for name in ["front", "back", "left", "right", "45_left", "45_right"]:
        cv2.imwrite(str(input_dir / f"{name}.png"), draw())

    return input_dir
