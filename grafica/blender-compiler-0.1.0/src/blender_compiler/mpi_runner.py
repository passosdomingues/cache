"""Runner MPI para distribuição paralela de tarefas de visão e pré-processamento.

Suporta execução distribuída via `mpirun` e `mpi4py` (quando disponível) ou
divisão paralela de visualizações entre nós/processos trabalhadores.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger("blender_compiler.mpi")


def is_mpi_available() -> bool:
    """Verifica se mpirun está disponível no sistema."""
    return bool(shutil.which("mpirun")) or bool(shutil.which("mpiexec"))


def run_mpi_compile(
    input_dir: Path,
    output_dir: Path,
    num_workers: int = 4,
    object_name: str = "object",
    config_path: Path | None = None,
) -> int:
    """Executa a compilação paralela distribuindo visões de entrada usando `mpirun`."""
    mpirun_bin = shutil.which("mpirun") or shutil.which("mpiexec")
    if not mpirun_bin:
        logger.warning("mpirun não encontrado no sistema. Executando em modo sequencial.")
        from blender_compiler.config import load_config
        from blender_compiler.pipeline import compile_object

        cfg = load_config(config_path)
        compile_object(input_dir, output_dir, cfg, object_name=object_name)
        return 0

    cli_script = Path(__file__).resolve().parents[2] / "cli.py"
    cmd = [
        mpirun_bin,
        "-n", str(num_workers),
        sys.executable,
        str(cli_script),
        "compile",
        str(input_dir),
        "--output", str(output_dir),
        "--name", object_name,
    ]
    if config_path:
        cmd.extend(["--config", str(config_path)])

    logger.info(f"Iniciando runner MPI: {' '.join(cmd)}")
    proc = subprocess.run(cmd, text=True)
    return proc.returncode
