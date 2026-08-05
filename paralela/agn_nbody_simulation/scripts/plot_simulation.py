#!/usr/bin/env python3
"""
plot_simulation.py
==================
Visualisation for the AGN N-Body MPI Simulation.

Generates three publication-quality plots saved to plots/:
  1. galaxy_evolution.png  — XY disk snapshots at several timesteps
  2. energy_conservation.png — KE / PE / Total energy over time
  3. speedup_analysis.png  — MPI parallel speedup on the i7-8565U

Usage
-----
    # After running:  make run NP=4 N=1000 STEPS=500
    python3 scripts/plot_simulation.py

    # Optional: custom paths
    python3 scripts/plot_simulation.py --data data/output --plots plots
"""

import sys
import os
import glob
import argparse
from pathlib import Path

# ── Dependency check ──────────────────────────────────────────────────────────
try:
    import numpy as np
    import matplotlib
    matplotlib.use("Agg")   # non-interactive backend (no display needed)
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    from matplotlib.colors import Normalize
    from matplotlib.cm import ScalarMappable
    from matplotlib.patches import Circle
    from matplotlib.gridspec import GridSpec
except ImportError as e:
    print(f"\n[ERROR] Missing dependency: {e}")
    print("Install with:  pip install matplotlib numpy\n")
    sys.exit(1)

# ── Colour palette ────────────────────────────────────────────────────────────
BG_DARK   = "#080c14"
BG_PANEL  = "#0d1220"
ACCENT    = "#00d4ff"
GOLD      = "#ffd700"
STAR_CMAP = "plasma"

plt.rcParams.update({
    "figure.facecolor":  BG_DARK,
    "axes.facecolor":    BG_PANEL,
    "axes.edgecolor":    "#2a3550",
    "axes.labelcolor":   "#c0cce0",
    "xtick.color":       "#8090b0",
    "ytick.color":       "#8090b0",
    "text.color":        "#c0cce0",
    "grid.color":        "#1e2a40",
    "grid.linewidth":    0.5,
    "font.family":       "monospace",
    "figure.dpi":        150,
})

# ─────────────────────────────────────────────────────────────────────────────
# 1.  GALAXY EVOLUTION
# ─────────────────────────────────────────────────────────────────────────────

def load_snapshot(csv_path: str):
    """
    Loads a snapshot CSV and returns (ids, types, x, y, z, mass) arrays.

    @param csv_path  Path to snap_step######.csv produced by main.cpp.
    @return Tuple of numpy arrays: (ids, types, x, y, z, mass).
    """
    data = np.genfromtxt(csv_path, delimiter=',', names=True, dtype=None,
                          encoding='utf-8')
    ids   = data['id'].astype(int)
    types = data['type'].astype(str)
    x     = data['x'].astype(float)
    y     = data['y'].astype(float)
    z     = data['z'].astype(float)
    mass  = data['mass'].astype(float)
    return ids, types, x, y, z, mass


def plot_galaxy_evolution(data_dir: str, out_path: str) -> bool:
    """
    Plots a grid of XY position snapshots showing the disk rotating.

    @param data_dir  Directory containing snap_step*.csv files.
    @param out_path  Output PNG path.
    @return True if successful, False if no snapshots found.
    """
    snap_files = sorted(glob.glob(os.path.join(data_dir, "snap_step*.csv")))
    if not snap_files:
        print(f"  [SKIP] No snapshots in {data_dir}/snap_step*.csv")
        return False

    # Pick at most 6 evenly-spaced snapshots
    n_panels = min(6, len(snap_files))
    indices  = np.linspace(0, len(snap_files) - 1, n_panels, dtype=int)
    selected = [snap_files[i] for i in indices]

    ncols = 3
    nrows = (n_panels + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols,
                              figsize=(5 * ncols, 4.5 * nrows),
                              facecolor=BG_DARK)
    axes = np.array(axes).flatten()

    # ── Get radial extent from first snapshot ────────────────────────────────
    ids0, types0, x0, y0, z0, mass0 = load_snapshot(selected[0])
    star_mask0 = (types0 == 'STAR')
    r_max = np.percentile(np.sqrt(x0[star_mask0]**2 + y0[star_mask0]**2), 98) * 1.15

    norm = Normalize(vmin=0, vmax=r_max)
    cmap = plt.get_cmap(STAR_CMAP)

    for ax_idx, csv_path in enumerate(selected):
        ax = axes[ax_idx]
        ids, types, x, y, z, mass = load_snapshot(csv_path)

        star_mask = (types == 'STAR')
        bh_mask   = (types == 'BH')

        # Compute orbital radius for colour mapping
        r_star = np.sqrt(x[star_mask]**2 + y[star_mask]**2)
        colors = cmap(norm(r_star))

        # Draw faint guide circles
        for r_ring in np.linspace(r_max * 0.25, r_max * 0.9, 4):
            circle = Circle((0, 0), r_ring, fill=False,
                             color='white', alpha=0.06, linewidth=0.7, linestyle='--')
            ax.add_patch(circle)

        # Stars
        ax.scatter(x[star_mask], y[star_mask],
                   c=r_star, cmap=STAR_CMAP, norm=norm,
                   s=4, alpha=0.75, linewidths=0, rasterized=True)

        # Black hole — golden star marker
        if np.any(bh_mask):
            ax.scatter(x[bh_mask], y[bh_mask],
                       c=GOLD, s=200, marker='*', zorder=10,
                       edgecolors='white', linewidths=0.5)

        # Extract step number from filename
        step_str = Path(csv_path).stem.replace('snap_step', '')
        try:
            step_num = int(step_str)
        except ValueError:
            step_num = ax_idx

        ax.set_xlim(-r_max, r_max)
        ax.set_ylim(-r_max, r_max)
        ax.set_aspect('equal')
        ax.set_title(f"Step {step_num:,}", color=ACCENT, fontsize=10, pad=6)
        ax.set_xlabel("x [L]", fontsize=8)
        ax.set_ylabel("y [L]", fontsize=8)
        ax.grid(True, linewidth=0.4, alpha=0.4)

    # Hide unused panels
    for ax_idx in range(len(selected), len(axes)):
        axes[ax_idx].set_visible(False)

    # ── Colourbar ────────────────────────────────────────────────────────────
    sm = ScalarMappable(cmap=STAR_CMAP, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=axes[:len(selected)], orientation='vertical',
                        fraction=0.015, pad=0.02, shrink=0.7)
    cbar.set_label("Orbital radius [L]", color="#c0cce0", fontsize=9)
    cbar.ax.yaxis.set_tick_params(color="#8090b0")

    fig.suptitle("🌌  AGN N-Body — Galaxy Disk Evolution",
                 color='white', fontsize=14, fontweight='bold', y=1.01)

    plt.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches='tight',
                facecolor=BG_DARK, edgecolor='none')
    plt.close(fig)
    print(f"  ✔  Saved: {out_path}")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# 2.  ENERGY CONSERVATION
# ─────────────────────────────────────────────────────────────────────────────

def plot_energy_conservation(data_dir: str, out_path: str) -> bool:
    """
    Plots kinetic energy, potential energy, and total energy over time.
    Also shows the relative energy drift on a secondary axis.

    @param data_dir  Directory containing energy_log.csv.
    @param out_path  Output PNG path.
    @return True if successful, False if log not found.
    """
    log_path = os.path.join(data_dir, "energy_log.csv")
    if not os.path.exists(log_path):
        print(f"  [SKIP] energy_log.csv not found in {data_dir}")
        return False

    data = np.genfromtxt(log_path, delimiter=',', names=True, dtype=float)
    if data.ndim == 0 or len(data) < 2:
        print("  [SKIP] energy_log.csv has insufficient data")
        return False

    steps  = data['step']
    time   = data['time']
    ke     = data['kinetic_energy']
    pe     = data['potential_energy']
    total  = data['total_energy']
    drift  = data['drift_pct']

    # Normalize energies relative to |E0| for better comparison
    e0_abs = np.abs(total[0]) if total[0] != 0 else 1.0
    ke_n   = ke    / e0_abs
    pe_n   = pe    / e0_abs
    tot_n  = total / e0_abs

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7),
                                    facecolor=BG_DARK, sharex=True,
                                    gridspec_kw={'height_ratios': [3, 1], 'hspace': 0.08})

    # ── Energy panel ─────────────────────────────────────────────────────────
    ax1.plot(time, ke_n,  color='#ff8c00', linewidth=1.8, label='Kinetic Energy',  alpha=0.9)
    ax1.plot(time, pe_n,  color='#4488ff', linewidth=1.8, label='Potential Energy', alpha=0.9)
    ax1.plot(time, tot_n, color='#00e5cc', linewidth=2.2, label='Total Energy',
             linestyle='-', zorder=5)

    # Shade the total energy band to show drift
    ax1.fill_between(time, tot_n, tot_n[0],
                     color='#00e5cc', alpha=0.08)

    ax1.axhline(tot_n[0], color='white', linewidth=0.8, linestyle='--',
                alpha=0.4, label=f'E₀ = {total[0]:.3e}')

    ax1.set_ylabel("Energy / |E₀|", fontsize=11)
    ax1.legend(loc='upper right', framealpha=0.2, fontsize=9)
    ax1.grid(True, linewidth=0.4, alpha=0.5)
    ax1.set_title("🔋  Energy Conservation — Leapfrog/KDK Integrator",
                  color='white', fontsize=12, fontweight='bold', pad=10)

    # ── Drift panel ───────────────────────────────────────────────────────────
    drift_color = np.where(drift < 0.1, '#00c853',
                   np.where(drift < 1.0, '#ffab00', '#ff3d00'))
    ax2.bar(time, drift, width=(time[1] - time[0]) * 0.8 if len(time) > 1 else 0.1,
            color='#00c853', alpha=0.7, label='Drift (%)')

    # Colour bars by threshold
    for i, (t, d) in enumerate(zip(time, drift)):
        bar_color = '#00c853' if d < 0.1 else ('#ffab00' if d < 1.0 else '#ff3d00')
        ax2.bar(t, d, width=(time[1] - time[0]) * 0.8 if len(time) > 1 else 0.1,
                color=bar_color, alpha=0.8)

    ax2.axhline(0.1, color='#ffab00', linewidth=0.8, linestyle='--', alpha=0.7,
                label='0.1% threshold')
    ax2.axhline(1.0, color='#ff3d00', linewidth=0.8, linestyle='--', alpha=0.7,
                label='1.0% threshold')
    ax2.set_ylabel("Drift (%)", fontsize=9)
    ax2.set_xlabel("Simulation time [T]", fontsize=11)
    ax2.legend(loc='upper left', framealpha=0.2, fontsize=8)
    ax2.grid(True, linewidth=0.4, alpha=0.5)

    # Annotate final drift
    ax2.annotate(f"Final drift: {drift[-1]:.4f}%",
                 xy=(time[-1], drift[-1]),
                 xytext=(-60, 10), textcoords='offset points',
                 color='white', fontsize=8,
                 arrowprops=dict(arrowstyle='->', color='white', lw=0.8))

    plt.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches='tight',
                facecolor=BG_DARK, edgecolor='none')
    plt.close(fig)
    print(f"  ✔  Saved: {out_path}")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# 3.  MPI SPEEDUP ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

def plot_speedup_analysis(out_path: str,
                           np_list:   list,
                           times:     list) -> bool:
    """
    Plots parallel speedup vs number of MPI processes.

    @param out_path  Output PNG path.
    @param np_list   List of process counts (e.g., [1, 2, 4, 8]).
    @param times     Corresponding wall-clock times in seconds.
    @return True always.
    """
    np_arr     = np.array(np_list, dtype=float)
    times_arr  = np.array(times,   dtype=float)
    t1         = times_arr[0]          # serial baseline
    speedup    = t1 / times_arr
    efficiency = speedup / np_arr * 100.0

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), facecolor=BG_DARK)

    # ── Speedup plot ──────────────────────────────────────────────────────────
    x_ideal = np.linspace(1, np_arr[-1], 100)
    ax1.plot(x_ideal, x_ideal, '--', color='#405070', linewidth=1.5,
             label='Ideal (linear)', alpha=0.8)

    bar_colors = ['#00b4d8', '#48cae4', '#90e0ef', '#caf0f8']
    bars = ax1.bar(np_arr, speedup, color=bar_colors[:len(np_arr)],
                   alpha=0.85, width=0.6, zorder=3)

    # Annotate bars
    for bar, sp, t in zip(bars, speedup, times_arr):
        ax1.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 0.05,
                 f'{sp:.2f}×\n({t:.2f}s)',
                 ha='center', va='bottom', color='white', fontsize=8)

    ax1.set_xlabel("MPI Processes (NP)", fontsize=11)
    ax1.set_ylabel("Speedup (T₁ / Tₙ)", fontsize=11)
    ax1.set_title("🚀  Parallel Speedup — i7-8565U\n4 physical cores / 8 HT threads",
                  color='white', fontsize=11, fontweight='bold')
    ax1.set_xticks(np_arr)
    ax1.set_xticklabels([f"NP={int(n)}" for n in np_arr])
    ax1.legend(fontsize=9, framealpha=0.2)
    ax1.grid(True, axis='y', linewidth=0.4, alpha=0.5)
    ax1.set_ylim(0, max(np_arr[-1] + 0.5, speedup.max() + 0.5))

    # ── Efficiency plot ───────────────────────────────────────────────────────
    eff_colors = ['#38b000', '#70e000', '#ccff33', '#ffaa00']
    bars2 = ax2.bar(np_arr, efficiency, color=eff_colors[:len(np_arr)],
                    alpha=0.85, width=0.6, zorder=3)

    ax2.axhline(100, color='white', linewidth=0.8, linestyle='--',
                alpha=0.4, label='100% efficiency')
    ax2.axhline(80,  color='#ffaa00', linewidth=0.8, linestyle=':',
                alpha=0.6, label='80% threshold')

    for bar, eff in zip(bars2, efficiency):
        ax2.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 1,
                 f'{eff:.1f}%',
                 ha='center', va='bottom', color='white', fontsize=9)

    ax2.set_xlabel("MPI Processes (NP)", fontsize=11)
    ax2.set_ylabel("Parallel Efficiency (%)", fontsize=11)
    ax2.set_title("⚡  Parallel Efficiency\nOverhead: MPI_Allgather (3 × N × 8 bytes/step)",
                  color='white', fontsize=11, fontweight='bold')
    ax2.set_xticks(np_arr)
    ax2.set_xticklabels([f"NP={int(n)}" for n in np_arr])
    ax2.set_ylim(0, 115)
    ax2.legend(fontsize=9, framealpha=0.2)
    ax2.grid(True, axis='y', linewidth=0.4, alpha=0.5)

    # ── Amdahl annotation ─────────────────────────────────────────────────────
    fig.text(0.5, -0.04,
             "Amdahl's Law: speedup limited by serial fraction (MPI_Allgather overhead)\n"
             "Sweet spot for this hardware: NP=4 (4 physical cores)",
             ha='center', color='#8090b0', fontsize=8)

    plt.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches='tight',
                facecolor=BG_DARK, edgecolor='none')
    plt.close(fig)
    print(f"  ✔  Saved: {out_path}")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="AGN Simulation Plotter")
    p.add_argument("--data",   default="data/output", help="Simulation output directory")
    p.add_argument("--plots",  default="plots",       help="Output plot directory")
    p.add_argument("--skip-benchmark", action="store_true",
                   help="Skip speedup plot (use cached results)")
    return p.parse_args()


def main():
    args   = parse_args()
    data   = args.data
    outdir = args.plots

    print("\n🌌  AGN Simulation — Generating Plots")
    print(f"   Data : {data}")
    print(f"   Plots: {outdir}")
    print("─" * 50)

    # ── Plot 1: Galaxy Evolution ──────────────────────────────────────────────
    print("\n[1/3] Galaxy disk evolution snapshots...")
    plot_galaxy_evolution(data, f"{outdir}/galaxy_evolution.png")

    # ── Plot 2: Energy Conservation ───────────────────────────────────────────
    print("\n[2/3] Energy conservation analysis...")
    plot_energy_conservation(data, f"{outdir}/energy_conservation.png")

    # ── Plot 3: Speedup (hardcoded from benchmark or let user update) ─────────
    print("\n[3/3] MPI speedup analysis...")
    # Update these values after running:  make benchmark N=3000
    # Format: (NP, wall_time_seconds)
    benchmark_results = [
        (1, 2.869),   # NP=1
        (2, 1.759),   # NP=2
        (4, 1.118),   # NP=4 ← sweet spot
        (8, 1.150),   # NP=8
    ]
    np_list = [r[0] for r in benchmark_results]
    times   = [r[1] for r in benchmark_results]
    plot_speedup_analysis(f"{outdir}/speedup_analysis.png", np_list, times)

    print(f"\n✔  All plots saved in {outdir}/")
    print("   Open them with your image viewer or:")
    print(f"   xdg-open {outdir}/galaxy_evolution.png\n")


if __name__ == "__main__":
    main()
