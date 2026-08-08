"""Módulo de pré-processamento via ImageMagick CLI (`convert` / `magick`).

Oferece suporte a operações de imagem via ferramentas do ImageMagick:
- Thresholding e extração de silhueta/máscara
- Detecção de bordas (`-edge`)
- Redução de paleta/quantização de cores
- Montagem de grade multi-visão (`montage`)
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger("blender_compiler.preprocessing.imagemagick")


class ImageMagickPreprocessor:
    def __init__(self, executable: str = "convert"):
        self.executable = executable if shutil.which(executable) else "convert"

    def is_available(self) -> bool:
        return bool(shutil.which(self.executable))

    def generate_mask(self, input_path: Path, output_path: Path, threshold_pct: int = 50) -> bool:
        """Gera máscara binária preto e branco usando ImageMagick."""
        cmd = [
            self.executable,
            str(input_path),
            "-colorspace", "Gray",
            "-threshold", f"{threshold_pct}%",
            "-negate",
            str(output_path),
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logger.warning(f"Erro ao executar ImageMagick mask em {input_path}: {e}")
            return False

    def generate_edges(self, input_path: Path, output_path: Path, radius: int = 2) -> bool:
        """Extrai bordas da imagem usando `-edge`."""
        cmd = [
            self.executable,
            str(input_path),
            "-colorspace", "Gray",
            "-edge", str(radius),
            "-negate",
            str(output_path),
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logger.warning(f"Erro ao executar ImageMagick edge em {input_path}: {e}")
            return False

    def create_montage(
        self, image_paths: list[Path], output_path: Path, tile: str = "2x2", geometry: str = "512x512>+2+2"
    ) -> bool:
        """Cria um mosaico/montagem combinando múltiplas vistas em uma só imagem (útil para Vision LLMs)."""
        montage_cmd = shutil.which("montage") or "montage"
        cmd = [
            montage_cmd,
            *[str(p) for p in image_paths],
            "-tile", tile,
            "-geometry", geometry,
            str(output_path),
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logger.warning(f"Erro ao criar montagem ImageMagick: {e}")
            return False
