#!/usr/bin/env python3
# run_analysis.py

import sys
from pathlib import Path
import logging
import pandas as pd

# Add local lib to path
BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from lib.loader import LogParser
from lib.stats import StatsEngine
from lib.viz import PlotterFactory
# Assuming MLAnalyzer and ComparativeAnalyzer are in lib.ml and lib.comparative

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Orchestrator")

def main():
    # 1. Setup Paths
    raw_dir = BASE_DIR.parent / "results" / "raw"
    plots_dir = BASE_DIR / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    # 2. Load Data
    logger.info("Phase 1: Ingesting Data...")
    loader = LogParser(raw_dir)
    full_df = loader.loadAllScenarios()
    
    if full_df.empty:
        logger.error("No data found. Exiting.")
        return

    # 3. Statistical Analysis
    logger.info("Phase 2: Computing Statistics...")
    stats_engine = StatsEngine()
    
    # Aggregated metrics
    metrics_df = stats_engine.calculateMetrics(full_df)
    metrics_df.to_csv(plots_dir / "summary_metrics.csv", index=False)
    
    # Convergence check
    convergence_df = stats_engine.checkConvergence(full_df)
    convergence_df.to_csv(plots_dir / "convergence_report.csv", index=False)
    
    # Correlation matrix
    corr_matrix = stats_engine.getCorrelationMatrix(full_df)
    print("\nGlobal Correlation Matrix:\n", corr_matrix)

    # 4. Visualization
    logger.info("Phase 3: Generating Visualizations (RafaPlots Style)...")
    plotter = PlotterFactory(plots_dir)
    
    # A. Time Series Analysis (High Load)
    plotter.plotTimeSeries(full_df, rho_target=0.99)
    
    # B. Heatmaps
    plotter.plotHeatmap(metrics_df)
    
    # C. Distributions
    plotter.plotViolinDistributions(full_df)
    
    # D. Diagnostic Scatter
    plotter.plotLittleErrorScatter(full_df)

    logger.info(f"Analysis Complete. Artifacts saved to {plots_dir}")

if __name__ == "__main__":
    main()