#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
run_analysis.py
===============
Main Orchestrator for Discrete Event Simulation Analysis.
"""

import sys
import logging
from pathlib import Path
import pandas as pd

# Ensure local lib is visible
BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from lib.loader import LogParser
from lib.stats import StatsEngine
from lib.ml import MLAnalyzer
from lib.viz import PlotterFactory
from lib.comparative import ComparativeAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """
    @brief Main entry point for the analysis pipeline.
    """
    try:
        logger.info("Initializing Analysis Pipeline v3.1 (Scientific Edition)...")
        
        # 1. Setup Directories
        rawDir = BASE_DIR.parent / "results" / "raw"
        outDir = BASE_DIR / "plots"
        
        # Ensure output directory exists before any file operation
        outDir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory set to: {outDir}")
        
        # 2. Data Ingestion
        parser = LogParser(dataDir=rawDir)
        df = parser.loadAllScenarios()
        
        # 3. Preprocessing (Warm-up Removal)
        logger.info("Removing transient warm-up phase (15%)...")
        
        def removeWarmup(group):
            cutoff = int(len(group) * 0.15)
            return group.iloc[cutoff:]

        # Grouping by scenario to remove initial transient state
        cleanDf = df.groupby(['policy', 'rho', 'seed'], group_keys=False).apply(removeWarmup)
        
        # 4. Statistical Analysis
        statsEngine = StatsEngine()
        metricsDf = statsEngine.calculateMetrics(cleanDf)
        
        # Save violations immediately
        violations = statsEngine.verifyLittlesLaw(metricsDf)
        if not violations.empty:
            logger.warning(f"Saving {len(violations)} Little's Law violations to CSV.")
            violations.to_csv(outDir / "littles_law_violations.csv")
        
        # 5. Comparative Analysis
        compAnalyzer = ComparativeAnalyzer()
        winner = compAnalyzer.getBestHighLoadPolicy(metricsDf)
        
        if winner is not None:
            print("\n" + "="*50)
            print(f"PERFORMANCE LEADER (Rho=0.999): {winner['policy']}")
            print(f"   Occupancy Mean: {winner['occupancyMean']:.4f}")
            print(f"   Stability (Std): {winner['occupancyStd']:.4f}")
            print("="*50 + "\n")

        # 6. Machine Learning (PCA & Clustering)
        logger.info("Running ML algorithms (PCA Projection & Clustering)...")
        mlAnalyzer = MLAnalyzer(cleanDf)
        
        # We perform clustering on the dataset
        mlDf = mlAnalyzer.performClustering(nClusters=3) 
        mlDf = mlAnalyzer.performPCA()
        
        # 7. Visualization Generation
        logger.info("Generating Scientific Visualizations (300 DPI)...")
        plotter = PlotterFactory(outputDir=outDir)
        
        # A. Global Heatmap
        plotter.generateHeatmap(metricsDf)
        
        # B. Temporal Dynamics (Time Series)
        # Using rho=0.999 as it is the stress test case
        plotter.generateTimeSeriesComparison(cleanDf, targetRho=0.999)
        
        # C. Multi-Criteria Comparison (Radar Chart)
        plotter.generateRadarChart(metricsDf, targetRho=0.999)
        
        # D. Correlation Analysis (Scatter)
        plotter.generateScatterMatrix(cleanDf, targetRho=0.95)
        
        # 8. Final Data Export
        finalReportPath = outDir / "final_metrics_report.csv"
        metricsDf.to_csv(finalReportPath, index=False)
        logger.info(f"Analysis pipeline completed. Data saved to: {finalReportPath}")

    except Exception as e:
        logger.exception(f"CRITICAL FAILURE IN PIPELINE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()