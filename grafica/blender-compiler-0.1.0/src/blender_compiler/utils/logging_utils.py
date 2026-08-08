"""Logging centralizado com Rich: console colorido + arquivo de log por execução."""

from __future__ import annotations

import logging
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

console = Console()

try:
    import psutil

    _HAS_PSUTIL = True
except ImportError:  # pragma: no cover
    _HAS_PSUTIL = False


def _memory_mb() -> float | None:
    if not _HAS_PSUTIL:
        return None
    return psutil.Process().memory_info().rss / (1024 * 1024)


def setup_logging(log_dir: str = "logs", level: str = "INFO") -> logging.Logger:
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    log_file = log_path / f"run_{time.strftime('%Y%m%d_%H%M%S')}.log"

    logger = logging.getLogger("blender_compiler")
    logger.setLevel(level)
    logger.handlers.clear()

    rich_handler = RichHandler(console=console, show_time=True, rich_tracebacks=True, markup=True)
    rich_handler.setLevel(level)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"))
    file_handler.setLevel(level)

    logger.addHandler(rich_handler)
    logger.addHandler(file_handler)
    logger.propagate = False
    logger.info(f"Log iniciado em {log_file}")
    return logger


@contextmanager
def stage(logger: logging.Logger, name: str) -> Iterator[None]:
    """Context manager que mede tempo/memória de uma etapa do pipeline."""
    start = time.perf_counter()
    mem_before = _memory_mb()
    logger.info(f"[bold cyan]▶ Iniciando etapa:[/bold cyan] {name}")
    try:
        yield
    except Exception:
        logger.exception(f"[bold red]✗ Falhou na etapa:[/bold red] {name}")
        raise
    else:
        elapsed = time.perf_counter() - start
        mem_after = _memory_mb()
        mem_str = ""
        if mem_before is not None and mem_after is not None:
            mem_str = f" | mem: {mem_after:.1f}MB (Δ{mem_after - mem_before:+.1f}MB)"
        logger.info(f"[bold green]✓ Concluída:[/bold green] {name} " f"| tempo: {elapsed:.2f}s{mem_str}")


def make_progress() -> Progress:
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console,
    )
