#!/usr/bin/env python3
"""
@file orchestrator.py
@brief Unified entry point for Project Chronos analysis pipeline
@author Project Chronos
"""

import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Add lib to path
BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

from lib.loader import LogParser
from lib.stats import StatsEngine
from lib.ml import MLAnalyzer
from lib.viz import PlotterFactory
from lib.policy_learner import PolicyLearner
from lib.littles_validator import LittlesLawValidator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AnalysisOrchestrator:
    """
    @brief Central coordinator for simulation analysis pipeline
    
    Orchestrates the complete analysis workflow from raw CSV ingestion
    to final visualization and reporting.
    """
    
    def __init__(self, rawDir: Path, outDir: Path, warmupFraction: float = 0.15):
        """
        @brief Constructor for AnalysisOrchestrator
        @param rawDir Directory containing raw CSV simulation logs
        @param outDir Directory for output artifacts (plots, reports, matrices)
        @param warmupFraction Fraction of samples to discard as warmup (default 15%)
        """
        self.rawDir = rawDir
        self.outDir = outDir
        self.warmupFraction = warmupFraction
        
        # Create output directory
        self.outDir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.parser = LogParser(dataDir=rawDir)
        self.statsEngine = StatsEngine()
        self.validator = LittlesLawValidator(errorThreshold=0.05)
        self.learner = PolicyLearner()
        self.plotter = PlotterFactory(outputDir=outDir)
        
        logger.info(f"Initialized AnalysisOrchestrator:")
        logger.info(f"  Raw data: {rawDir}")
        logger.info(f"  Output: {outDir}")
        logger.info(f"  Warmup fraction: {warmupFraction}")
    
    def runFullPipeline(self):
        """
        @brief Execute complete analysis workflow
        
        Pipeline stages:
        1. Load and parse raw CSV files
        2. Remove warmup transient
        3. Validate Little's Law compliance
        4. Calculate advanced statistics
        5. Train optimal policy matrix
        6. Analyze policy performance
        7. Generate visualizations
        8. Export markdown report
        """
        logger.info("="*60)
        logger.info("Starting Project Chronos Analysis Pipeline")
        logger.info("="*60)
        
        try:
            # Stage 1: Data Ingestion
            logger.info("[1/8] Loading raw simulation data...")
            rawDf = self.parser.loadAllScenarios()
            logger.info(f"  Loaded {len(rawDf)} total samples")
            
            # Stage 2: Warmup Removal
            logger.info(f"[2/8] Removing warmup transient ({self.warmupFraction*100:.0f}%)...")
            cleanDf = self._removeWarmup(rawDf)
            logger.info(f"  Retained {len(cleanDf)} steady-state samples")
            
            # Stage 3: Little's Law Validation
            logger.info("[3/8] Validating Little's Law compliance...")
            littlesMetrics = self.validator.extractMetrics(cleanDf)
            littlesMetrics.to_csv(self.outDir / "littles_law_metrics.csv", index=False)
            logger.info(f"  Saved Little's Law metrics")
            
            # Stage 4: Advanced Statistics
            logger.info("[4/8] Calculating advanced statistics...")
            advancedMetrics = self.statsEngine.calculateMetrics(cleanDf)
            advancedMetrics.to_csv(self.outDir / "advanced_metrics.csv", index=False)
            logger.info(f"  Saved advanced metrics")
            
            # Stage 5: Optimal Policy Matrix
            logger.info("[5/8] Training optimal policy matrix...")
            policyMatrix = self.learner.trainOptimalMatrix(
                cleanDf, 
                self.outDir / "optimized_policy_matrix.csv"
            )
            logger.info(f"  Generated matrix covering {len(policyMatrix)} states")
            
            # Stage 6: Policy Performance Analysis
            logger.info("[6/8] Analyzing policy performance...")
            policyRankings = self.learner.analyzePolicyPerformance(cleanDf)
            policyRankings.to_csv(self.outDir / "policy_rankings.csv", index=False)
            logger.info(f"  Ranked {len(policyRankings)} policy-rho combinations")
            
            # Stage 7: Visualizations
            logger.info("[7/8] Generating visualizations...")
            self.plotter.generateHeatmap(advancedMetrics)
            self.plotter.generateTimeSeries(cleanDf, targetRho=0.999)
            self.plotter.generateScatterPhaseSpace(cleanDf, targetRho=0.999)
            logger.info(f"  Generated plots in {self.outDir}")
            
            # Stage 8: Report Generation
            logger.info("[8/8] Generating analysis report...")
            reportPath = self.generateReport(littlesMetrics, advancedMetrics, policyRankings)
            logger.info(f"  Report saved to {reportPath}")
            
            logger.info("="*60)
            logger.info("Analysis Pipeline Complete!")
            logger.info("="*60)
            
        except Exception as e:
            logger.exception("Pipeline failed with critical error")
            raise
    
    def _removeWarmup(self, df):
        """
        @brief Remove warmup transient from raw data
        @param df Raw DataFrame
        @return Clean DataFrame with warmup removed
        """
        def removeWarmupGroup(g):
            cutoff = int(len(g) * self.warmupFraction)
            return g.iloc[cutoff:]
        
        return df.groupby(
            ['scenarioPolicy', 'rho', 'seed'], 
            observed=True, 
            group_keys=False
        ).apply(removeWarmupGroup, include_groups=False)
    
    def generateReport(self, littlesMetrics, advancedMetrics, policyRankings) -> Path:
        """
        @brief Create comprehensive markdown analysis report
        @param littlesMetrics DataFrame from Little's Law validation
        @param advancedMetrics DataFrame from stats engine
        @param policyRankings DataFrame from policy learner
        @return Path to generated report file
        """
        reportPath = self.outDir / "analysis_report.md"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(reportPath, 'w') as f:
            f.write("# Project Chronos: Simulation Analysis Report\n\n")
            f.write(f"**Generated**: {timestamp}\n\n")
            f.write(f"**Raw Data**: `{self.rawDir}`\n\n")
            f.write(f"**Output Directory**: `{self.outDir}`\n\n")
            f.write("---\n\n")
            
            # Little's Law Summary
            f.write("## Little's Law Validation\n\n")
            totalScenarios = len(littlesMetrics)
            compliantCount = littlesMetrics['isCompliant'].sum()
            complianceRate = (compliantCount / totalScenarios * 100) if totalScenarios > 0 else 0
            
            f.write(f"- **Total scenarios**: {totalScenarios}\n")
            f.write(f"- **Compliant**: {compliantCount} ({complianceRate:.1f}%)\n")
            f.write(f"- **Error threshold**: 5%\n\n")
            
            violations = littlesMetrics[~littlesMetrics['isCompliant']]
            if len(violations) > 0:
                f.write("### Violations\n\n")
                f.write("| Policy | Rho | Relative Error | E[N] | Lambda | E[W] |\n")
                f.write("|--------|-----|----------------|------|--------|------|\n")
                for _, row in violations.iterrows():
                    f.write(f"| {row['scenarioPolicy']} | {row['rho']:.3f} | "
                           f"{row['relativeError']:.4f} | {row['expectedN']:.2f} | "
                           f"{row['lambda']:.4f} | {row['expectedW']:.4f} |\n")
                f.write("\n")
            else:
                f.write("No Little's Law violations detected.\n\n")
            
            # Policy Rankings
            f.write("## Top Policies by Load Factor\n\n")
            for rho in sorted(policyRankings['rho'].unique()):
                f.write(f"### Rho = {rho}\n\n")
                topPolicies = policyRankings[policyRankings['rho'] == rho].head(5)
                f.write("| Rank | Policy | Mean Occupancy | P99 | Stability (Std) | Fairness |\n")
                f.write("|------|--------|----------------|-----|-----------------|----------|\n")
                for idx, row in enumerate(topPolicies.itertuples(), 1):
                    f.write(f"| {idx} | {row.scenarioPolicy} | {row.occupancyMean:.2f} | "
                           f"{row.occupancyP99:.2f} | {row.occupancyStd:.2f} | "
                           f"{row.fairnessScore:.2f} |\n")
                f.write("\n")
            
            # Artifacts
            f.write("## Generated Artifacts\n\n")
            f.write("- `advanced_metrics.csv` - Statistical summaries per policy/rho\n")
            f.write("- `littles_law_metrics.csv` - Little's Law validation results\n")
            f.write("- `optimized_policy_matrix.csv` - State-optimal policy mapping\n")
            f.write("- `policy_rankings.csv` - Multi-criteria policy rankings\n")
            f.write("- `*.png` - Visualizations (heatmaps, time series, phase space)\n")
            f.write("\n")
            
            f.write("---\n\n")
            f.write("*Report generated by Project Chronos AnalysisOrchestrator*\n")
        
        return reportPath


def main():
    """
    @brief Main entry point with CLI argument parsing
    """
    parser = argparse.ArgumentParser(
        description="Project Chronos: Queueing Simulation Analysis Pipeline",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--raw',
        type=Path,
        default=BASE_DIR.parent / "results" / "raw",
        help="Directory containing raw CSV simulation logs"
    )
    
    parser.add_argument(
        '--out',
        type=Path,
        default=BASE_DIR / "plots",
        help="Output directory for analysis artifacts"
    )
    
    parser.add_argument(
        '--warmup',
        type=float,
        default=0.15,
        help="Warmup fraction to discard (0.0 - 1.0)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.raw.exists():
        logger.error(f"Raw data directory not found: {args.raw}")
        sys.exit(1)
    
    if not (0.0 <= args.warmup <= 1.0):
        logger.error(f"Invalid warmup fraction: {args.warmup} (must be 0.0-1.0)")
        sys.exit(1)
    
    # Run pipeline
    orchestrator = AnalysisOrchestrator(
        rawDir=args.raw,
        outDir=args.out,
        warmupFraction=args.warmup
    )
    
    orchestrator.runFullPipeline()


if __name__ == "__main__":
    main()
