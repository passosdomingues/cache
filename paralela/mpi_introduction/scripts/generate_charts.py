#!/usr/bin/env python3
"""
generate_charts.py
==================
Plotting script for the Didactic MPI C++ Framework benchmarks.
Generates charts for MPI Ping-Pong Latency and Bandwidth.
"""

import os
import sys
from pathlib import Path

try:
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError as e:
    print(f"[ERROR] Missing dependency: {e}")
    sys.exit(1)

plt.rcParams.update({
    "figure.facecolor": "#0d1117",
    "axes.facecolor": "#161b22",
    "axes.edgecolor": "#30363d",
    "axes.labelcolor": "#c9d1d9",
    "xtick.color": "#8b949e",
    "ytick.color": "#8b949e",
    "text.color": "#c9d1d9",
    "grid.color": "#21262d",
    "grid.linewidth": 0.5,
    "font.family": "monospace",
    "figure.dpi": 150,
})

def main():
    data_file = "data/output/pingpong_benchmark.csv"
    out_dir = "plots"
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    if not os.path.exists(data_file):
        print(f"[WARN] {data_file} not found. Skipping plot generation.")
        return

    data = np.genfromtxt(data_file, delimiter=',', names=True, dtype=float)
    if data.ndim == 0 or len(data) == 0:
        return

    sizes = data['size_bytes']
    latency = data['latency_us']
    bandwidth = data['bandwidth_mbps']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Latency Plot
    ax1.plot(sizes, latency, marker='o', color='#58a6ff', linewidth=2, label='Latência (µs)')
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_xlabel('Tamanho da Mensagem (Bytes)')
    ax1.set_ylabel('Latência Média (µs)')
    ax1.set_title(' Latência MPI (Ping-Pong)')
    ax1.grid(True, which="both", linestyle="--", alpha=0.3)
    ax1.legend()

    # Bandwidth Plot
    ax2.plot(sizes, bandwidth, marker='s', color='#3fb950', linewidth=2, label='Banda (MB/s)')
    ax2.set_xscale('log')
    ax2.set_xlabel('Tamanho da Mensagem (Bytes)')
    ax2.set_ylabel('Vazão / Banda (MB/s)')
    ax2.set_title(' Banda de Comunicação MPI')
    ax2.grid(True, which="both", linestyle="--", alpha=0.3)
    ax2.legend()

    plt.tight_layout()
    out_file = os.path.join(out_dir, "mpi_performance.png")
    fig.savefig(out_file, dpi=150, bbox_inches='tight')
    plt.close(fig)

    print(f"✔  Gráfico de desempenho MPI gerado: {out_file}")

if __name__ == "__main__":
    main()
