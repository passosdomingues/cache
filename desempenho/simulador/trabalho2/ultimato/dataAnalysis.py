#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
Advanced Queueing Simulation Performance Analysis Toolkit (v4.0)
================================================================================
Author: Rafael Passos Domingues (Refactored by Gemini)
Date: October 24, 2025

Description:
This script performs a comprehensive, multi-methodological analysis of queueing
system simulation data. It is designed to load and process data from all 12
scenarios (3 policies x 4 occupancy levels), enriching the data with
internal variability and fairness metrics.

The analysis is structured to "go beyond" simple aggregate comparisons by:
1.  Enriching data with per-timestamp fairness metrics (imbalance, spread).
2.  Generating cross-matrix comparative plots for all policies and scenarios.
3.  Analyzing the *distribution* and *dynamics* of queue behavior, not just
    the averages.
4.  Applying a suite of advanced machine learning techniques for deep insights:
    -   PCA (Principal Component Analysis) for dimensionality reduction.
    -   GMM (Gaussian Mixture Models) for probabilistic clustering.
    -   Isolation Forest for detecting anomalous/unstable states.
    -   Random Forest + SHAP for "atomic" and "recursive" feature insights.

All plots are saved in "article-ready" format at 300 DPI.
"""

# --- Standard Library Imports ---
import sys
import re
import warnings
from pathlib import Path
from typing import Dict, List, Any, Tuple

# --- Third-Party Imports ---
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import shap
from glob import glob

# --- Scikit-learn Imports ---
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.metrics import silhouette_score, r2_score

# --- Global Configuration ---
warnings.filterwarnings('ignore')
plt.rcParams['figure.max_open_warning'] = 50


# =============================================================================
# CONFIGURATION CLASSES
# =============================================================================

class AnalysisConfiguration:
    """
    Encapsulates all static configuration parameters for the analysis pipeline.
    """

    def __init__(self):
        """Initializes the configuration parameters."""

        # --- Data I/O Configuration ---
        self.dataDirectory = Path("results")
        self.outputDirectory = Path("results/analysis_plots")

        # --- File Naming Convention ---
        # Matches: queue_data_[PolicyName]_occupancy_[rho].csv
        self.filePattern = "queue_data_*_occupancy_*.csv"
        self.fileNameRegex = re.compile(r"queue_data_(.*?)_occupancy_(.*?).csv")

        # --- Experiment Dimensions ---
        self.policies = ["RoundRobin", "WaitingTimePriority", "UtilityBased"]
        self.rhos = ['0.800', '0.900', '0.950', '0.999']

        # --- CSV Column Names ---
        self.colTimestamp = "timestamp"
        self.colAggEN = "averageNumberInSystem"  # Global Average N
        self.colAggEW = "averageWaitingTime"  # Global Average W
        self.colQueues = ['queueSize1', 'queueSize2', 'queueSize3']
        self.colOccupancy = "measuredOccupancy"
        self.colArrivalRate = "measuredArrivalRate"

        # --- Steady-State Detection Parameters ---
        self.stabilizationWindow = 100
        self.stabilizationThreshold = 0.02  # 2% relative change
        self.stabilizationPatience = 5
        self.transientFallback = 0.15  # Discard 15% if detection fails


class VisualizationConfiguration:
    """
    Encapsulates all configuration parameters for plotting.
    Ensures all outputs are 300 DPI and article-ready.
    """

    def __init__(self):
        """Initializes the visualization parameters."""
        self.dpi = 300  # CRUCIAL: Article-quality resolution
        self.palette = {
            "RoundRobin": "#0072B2",  # Colorblind-safe Blue
            "WaitingTimePriority": "#E69F00",  # Colorblind-safe Orange
            "UtilityBased": "#009E73"  # Colorblind-safe Green
        }
        self.context = "paper"  # Use 'paper' context for legible fonts
        self.style = "whitegrid"
        sns.set_theme(context=self.context, style=self.style)


# =============================================================================
# MAIN ANALYSIS PIPELINE CLASS
# =============================================================================

class SimulationAnalysisPipeline:
    """
    Orchestrates the entire end-to-end analysis pipeline, from loading
    and enriching data to generating advanced ML insights and plots.
    """

    def __init__(self):
        """Initializes the pipeline and configuration objects."""
        print("=================================================================")
        print("  Advanced Simulation Analysis Pipeline (v4.0) Initializing")
        print("  (Focus: Cross-Matrix Analysis, Advanced ML, 300 DPI Output)")
        print("=================================================================")

        self.config = AnalysisConfiguration()
        self.visConfig = VisualizationConfiguration()

        # --- Data Attributes ---
        self.masterDataFrame: pd.DataFrame = pd.DataFrame()
        self.steadyStateFrame: pd.DataFrame = pd.DataFrame()
        self.summaryFrame: pd.DataFrame = pd.DataFrame()

        # --- ML Model Attributes ---
        self.mlModels: Dict[str, Any] = {}
        self.mlFeatures: List[str] = []
        self.mlTarget: str = self.config.colAggEW
        self.X_scaled: np.ndarray = np.array([])
        self.shapValues: np.ndarray = np.array([])

        # --- Setup ---
        self.config.outputDirectory.mkdir(exist_ok=True)
        print(f"Data Source:      {self.config.dataDirectory}")
        print(f"Plot Output:      {self.config.outputDirectory} (at {self.visConfig.dpi} DPI)")
        print(f"Policies to Find: {self.config.policies}")
        print(f"Scenarios to Find: {self.config.rhos}")

    def runFullPipeline(self):
        """
        Executes the entire analysis pipeline from start to finish.
        """
        try:
            print("\n--- [PHASE 1/5] Data Loading and Enrichment ---")
            self._loadAndEnrichData()

            print("\n--- [PHASE 2/5] Performance Summary Generation ---")
            self._generatePerformanceSummary()

            print("\n--- [PHASE 3/5] Advanced ML Analytics ---")
            self._runAdvancedAnalytics()

            print("\n--- [PHASE 4/5] Visualization Generation ---")
            self._generateVisualizations()

            print("\n--- [PHASE 5/5] SHAP Insights Generation ---")
            self._generateShapInsights()

            print("\n=================================================================")
            print("  Pipeline Execution Completed Successfully.")
            print(f"  All plots saved to: {self.config.outputDirectory}")
            print("=================================================================")

        except Exception as e:
            print(f"\n[FATAL ERROR] Pipeline failed: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            sys.exit(1)

    # -------------------------------------------------------------------------
    # [PHASE 1] Data Loading and Enrichment
    # -------------------------------------------------------------------------

    def _loadAndEnrichData(self):
        """
        Loads all 12 CSVs, performs steady-state detection, and enriches
        the data with internal fairness/variability metrics.
        """
        filePaths = glob(str(self.config.dataDirectory / self.config.filePattern))
        if not filePaths:
            raise FileNotFoundError(
                f"No files found matching pattern '{self.config.filePattern}' in '{self.config.dataDirectory}'")

        print(f"  Found {len(filePaths)} files. Processing...")
        allDataFrames = []
        for filePath in filePaths:
            match = self.config.fileNameRegex.search(Path(filePath).name)
            if not match:
                print(f"  [Warning] Skipping file with non-matching name: {filePath}")
                continue

            policy, rhoStr = match.group(1), match.group(2)
            if policy not in self.config.policies or rhoStr not in self.config.rhos:
                print(f"  [Warning] Skipping file with unknown policy/rho: {filePath}")
                continue

            try:
                df = self._loadSingleFile(filePath, policy, rhoStr)
                allDataFrames.append(df)
            except Exception as e:
                print(f"  [Error] Failed to load or process {filePath}: {e}")

        if len(allDataFrames) != 12:
            print(f"  [Warning] Expected 12 files (3 policies x 4 rhos), but found {len(allDataFrames)}.")
            if len(allDataFrames) == 0:
                raise ValueError("No valid data was loaded. Check file names and content.")

        self.masterDataFrame = pd.concat(allDataFrames, ignore_index=True)
        print(f"  Loaded {len(allDataFrames)} files into Master DataFrame ({len(self.masterDataFrame)} total samples).")

        print("  Applying steady-state detection and data enrichment...")
        self.steadyStateFrame = (
            self.masterDataFrame.groupby(['policy', 'rho'])
            .apply(self._applySteadyStateAndEnrich)
            .reset_index(drop=True)
        )
        print(f"  Created Steady-State DataFrame ({len(self.steadyStateFrame)} samples).")

    def _loadSingleFile(self, filePath: str, policy: str, rho: str) -> pd.DataFrame:
        """Loads and tags a single CSV file."""
        df = pd.read_csv(filePath)
        df['policy'] = policy
        df['rho'] = rho
        return df

    def _findStabilizationPoint(self, data: pd.Series) -> int:
        """Finds the steady-state start index using a moving window."""
        rollingMean = data.rolling(window=self.config.stabilizationWindow, min_periods=1).mean()
        relativeChange = rollingMean.pct_change()

        patienceCounter = 0
        for i in range(self.config.stabilizationWindow, len(relativeChange)):
            change = relativeChange.iloc[i]
            if pd.notna(change) and not np.isinf(change):
                if abs(change) < self.config.stabilizationThreshold:
                    patienceCounter += 1
                    if patienceCounter >= self.config.stabilizationPatience:
                        return i - self.config.stabilizationWindow
                else:
                    patienceCounter = 0  # Reset on fluctuation

        # Fallback if no stable point is found
        print("  [Note] Stabilization point not auto-detected, using fallback.")
        return int(len(data) * self.config.transientFallback)

    def _applySteadyStateAndEnrich(self, group: pd.DataFrame) -> pd.DataFrame:
        """
        Applies steady-state detection and calculates new metrics
        for a single data group (one policy at one rho).
        """
        startIndex = self._findStabilizationPoint(group[self.config.colAggEW])
        steadyData = group.iloc[startIndex:].copy()

        # --- Data Enrichment (The "Atomic Insights") ---
        queueData = steadyData[self.config.colQueues]

        # Metric 1: Imbalance (Standard Deviation between queues)
        steadyData['queueImbalance'] = queueData.std(axis=1)

        # Metric 2: Spread (Difference between max and min queue)
        steadyData['queueSpread'] = queueData.max(axis=1) - queueData.min(axis=1)

        # Metric 3: Mean (Average queue size at that instant)
        steadyData['queueMean'] = queueData.mean(axis=1)

        return steadyData

    # -------------------------------------------------------------------------
    # [PHASE 2] Performance Summary
    # -------------------------------------------------------------------------

    def _generatePerformanceSummary(self):
        """
        Creates a summary DataFrame by aggregating the steady-state data.
        This summary is the source for many plots.
        """
        if self.steadyStateFrame.empty:
            raise ValueError("Steady-state frame is empty. Cannot generate summary.")

        # Define aggregations
        def quantile_95(x):
            return x.quantile(0.95)

        quantile_95.__name__ = 'p95'

        aggFunctions = ['mean', 'median', quantile_95]

        metricsToAgg = {
            self.config.colAggEN: aggFunctions,
            self.config.colAggEW: aggFunctions,
            'queueImbalance': aggFunctions,
            'queueSpread': aggFunctions,
            'queueMean': aggFunctions
        }

        self.summaryFrame = (
            self.steadyStateFrame
            .groupby(['policy', 'rho'])
            .agg(metricsToAgg)
            .reset_index()
        )

        # Flatten MultiIndex columns
        self.summaryFrame.columns = ['_'.join(col).strip('_') for col in self.summaryFrame.columns.values]

        print("  Performance Summary Generated:")
        print(self.summaryFrame.to_string(float_format="%.3f"))

    # -------------------------------------------------------------------------
    # [PHASE 3] Advanced ML Analytics
    # -------------------------------------------------------------------------

    def _runAdvancedAnalytics(self):
        """
        Runs the full suite of ML models: PCA, GMM, Isolation Forest, and RF.
        """
        if self.steadyStateFrame.empty:
            raise ValueError("Steady-state frame is empty. Cannot run ML analytics.")

        self.mlFeatures = [
                              self.config.colAggEN, self.config.colAggEW,
                              self.config.colArrivalRate, self.config.colOccupancy,
                              'queueImbalance', 'queueSpread', 'queueMean'
                          ] + self.config.colQueues

        # Prepare data
        mlData = self.steadyStateFrame[self.mlFeatures + ['policy']].dropna()
        X = mlData[self.mlFeatures]
        y = self.steadyStateFrame.loc[X.index, self.mlTarget]

        scaler = StandardScaler()
        self.X_scaled = scaler.fit_transform(X)
        self.mlModels['scaler'] = scaler

        print(f"  Running ML analytics on {len(X)} steady-state samples.")

        # --- 1. PCA ---
        pca = PCA(n_components=2, random_state=42)
        X_pca = pca.fit_transform(self.X_scaled)
        self.mlModels['pca'] = pca
        self.mlModels['X_pca'] = X_pca
        print(f"  PCA: 2 components explain {pca.explained_variance_ratio_.sum() * 100:.2f}% of variance.")

        # --- 2. GMM (Gaussian Mixture Models) ---
        gmm = GaussianMixture(n_components=3, random_state=42, n_init=10)
        gmm_clusters = gmm.fit_predict(self.X_scaled)
        self.mlModels['gmm'] = gmm
        self.mlModels['gmm_clusters'] = gmm_clusters
        if len(np.unique(gmm_clusters)) > 1:
            self.mlModels['gmm_silhouette'] = silhouette_score(self.X_scaled, gmm_clusters)
        else:
            self.mlModels['gmm_silhouette'] = -1
        print(f"  GMM: 3 clusters fitted (Silhouette: {self.mlModels['gmm_silhouette']:.3f}).")

        # --- 3. Isolation Forest (Anomaly Detection) ---
        isoForest = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        anomalies = isoForest.fit_predict(self.X_scaled)
        self.mlModels['anomalies'] = anomalies  # -1 for anomaly, 1 for inlier

        mlData['anomaly'] = anomalies
        anomalyRates = mlData.groupby('policy')['anomaly'].apply(lambda x: (x == -1).mean() * 100)
        self.mlModels['anomaly_rates'] = anomalyRates
        print("  Isolation Forest: Anomaly rates per policy (%):")
        print(anomalyRates.to_string())

        # --- 4. Random Forest + SHAP ---
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1, max_depth=10)
        rf.fit(X_train, y_train)

        self.mlModels['rf_model'] = rf
        self.mlModels['X_test'] = X_test
        self.mlModels['feature_names'] = X.columns
        rf_score = r2_score(y_test, rf.predict(X_test))
        print(f"  Random Forest: Model trained to predict '{self.mlTarget}' (R²: {rf_score:.4f}).")

        print("  Calculating SHAP values for model explainability...")
        X_shap_sample = shap.sample(X_test, 1000) if len(X_test) > 1000 else X_test
        explainer = shap.TreeExplainer(rf)
        self.shapValues = explainer(X_shap_sample)
        self.mlModels['X_shap_sample'] = X_shap_sample
        print("  SHAP values calculated.")

    # -------------------------------------------------------------------------
    # [PHASE 4 & 5] Visualization (300 DPI Article-Ready Plots)
    # -------------------------------------------------------------------------

    def _savePlot(self, fig: plt.Figure, filename: str):
        """
        Helper function to save plots with consistent 300 DPI and formatting.
        """
        path = self.config.outputDirectory / filename
        fig.savefig(path, dpi=self.visConfig.dpi, bbox_inches='tight')
        plt.close(fig)
        print(f"    Saved: {filename}")

    def _generateVisualizations(self):
        """
        Orchestrator for all standard (non-SHAP) plots.
        """
        if self.steadyStateFrame.empty or self.summaryFrame.empty:
            raise ValueError("Data frames are empty. Cannot generate plots.")

        print("  Generating Plot 1: Performance Dashboard (Cross-Matrix)...")
        self._plotPerformanceDashboard()

        print("  Generating Plot 2: The Core Story (Aggregate vs. Fairness)...")
        self._plotTheStoryLineplot()

        print("  Generating Plot 3: Distribution Analysis (Violin Plots)...")
        self._plotDistributionViolins()

        print("  Generating Plot 4: Time Series Dynamics...")
        self._plotFairnessDynamics()

        print("  Generating Plot 5: Correlation Heatmaps...")
        self._plotCorrelationHeatmaps()

        print("  Generating Plot 6: ML - GMM Clustering...")
        self._plotClusterAnalysis()

        print("  Generating Plot 7: ML - Anomaly Detection...")
        self._plotAnomalyAnalysis()

        print("  Generating Plot 8: Methodology (Steady State)...")
        self._plotSteadyStateExample()

        print("  Generating Plot 9: Cross-Matrix Dynamics (Advanced)...")
        self._plotCrossMatrixDynamics()

    def _generateShapInsights(self):
        """Orchestrator for SHAP plots (requires special handling)."""
        if self.shapValues.shape[0] == 0:
            print("  [Warning] No SHAP values found. Skipping SHAP plots.")
            return

        print("  Generating Plot 10: SHAP Summary (Beeswarm)...")
        self._plotShapSummary()

        print("  Generating Plot 11: SHAP Dependence Plots...")
        self._plotShapDependence()

    # --- PLOTTING FUNCTIONS ---

    def _plotPerformanceDashboard(self):
        """
        PLOT 1: (THE MATRIX)
        A 2x2 dashboard showing the 4 key metrics vs. rho.
        This replaces the misleading 1x1 plot.
        """
        try:
            fig, axes = plt.subplots(2, 2, figsize=(16, 10))
            fig.suptitle('Performance Dashboard: Aggregate vs. Internal Fairness',
                         fontsize=18, fontweight='bold', y=1.03)

            metrics = [
                ('averageWaitingTime_mean', 'Global E[W] (Mean)', axes[0, 0]),
                ('averageNumberInSystem_mean', 'Global E[N] (Mean)', axes[0, 1]),
                ('queueImbalance_mean', 'Queue Imbalance (Mean StdDev)', axes[1, 0]),
                ('queueSpread_mean', 'Queue Spread (Mean Max-Min)', axes[1, 1])
            ]

            for metric, title, ax in metrics:
                for policy in self.config.policies:
                    policy_data = self.summaryFrame[self.summaryFrame['policy'] == policy]
                    if not policy_data.empty:
                        ax.plot(policy_data['rho'], policy_data[metric],
                                label=policy, marker='o', linewidth=2.5,
                                color=self.visConfig.palette[policy])

                ax.set_title(title, fontsize=14, fontweight='bold')
                ax.set_ylabel('Metric Value')
                ax.set_xlabel('System Occupancy (ρ)')
                ax.grid(True, which="both", ls="--", alpha=0.5)
                ax.tick_params(axis='x', rotation=45)

            handles, labels = axes[0, 0].get_legend_handles_labels()
            fig.legend(handles, labels, loc='upper center',
                       bbox_to_anchor=(0.5, 0.98), ncol=3, title="Policy")

            plt.tight_layout(rect=[0, 0, 1, 0.95])
            self._savePlot(fig, "1_Performance_Dashboard.png")

        except Exception as e:
            print(f"  [Error] Plot 1 failed: {e}")

    def _plotTheStoryLineplot(self):
        """
        PLOT 2: (THE NARRATIVE)
        A 1x2 plot showing the core story:
        Left: Global E[W] (they look the same)
        Right: Queue Imbalance (they are vastly different)
        """
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
            fig.suptitle('The Core Story: Aggregate Performance vs. Internal Fairness',
                         fontsize=16, fontweight='bold', y=1.02)

            # --- Left Plot: The "Misleading" Aggregate Metric ---
            for policy in self.config.policies:
                policy_data = self.summaryFrame[self.summaryFrame['policy'] == policy]
                if not policy_data.empty:
                    ax1.plot(policy_data['rho'], policy_data['averageWaitingTime_mean'],
                             label=policy, marker='o', linewidth=2.5,
                             color=self.visConfig.palette[policy])

            ax1.set_title('Finding 1: Global Performance is Near-Identical', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Global E[W] (Mean Wait Time)')
            ax1.set_xlabel('System Occupancy (ρ)')
            ax1.legend().set_visible(False)
            ax1.grid(True, which="both", ls="--", alpha=0.5)
            ax1.tick_params(axis='x', rotation=45)

            # --- Right Plot: The "True Story" Fairness Metric ---
            for policy in self.config.policies:
                policy_data = self.summaryFrame[self.summaryFrame['policy'] == policy]
                if not policy_data.empty:
                    ax2.plot(policy_data['rho'], policy_data['queueImbalance_mean'],
                             label=policy, marker='o', linewidth=2.5,
                             color=self.visConfig.palette[policy])

            ax2.set_title('Finding 2: Internal Fairness is Radically Different', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Mean Queue Imbalance (StdDev)')
            ax2.set_xlabel('System Occupancy (ρ)')
            ax2.legend().set_visible(False)
            ax2.grid(True, which="both", ls="--", alpha=0.5)
            ax2.tick_params(axis='x', rotation=45)

            handles, labels = ax1.get_legend_handles_labels()
            fig.legend(handles, labels, loc='upper center',
                       bbox_to_anchor=(0.5, 0.95), ncol=3, title="Policy")

            plt.tight_layout(rect=[0, 0, 1, 0.93])
            self._savePlot(fig, "2_The_Story_Aggregate_vs_Fairness.png")

        except Exception as e:
            print(f"  [Error] Plot 2 failed: {e}")

    def _plotDistributionViolins(self):
        """
        PLOT 3: (THE VISUAL PROOF)
        Violin plots showing the distribution of Q1, Q2, Q3 for each policy
        at the highest load.
        """
        try:
            rhoHigh = '0.999'
            plotData = self.steadyStateFrame[self.steadyStateFrame['rho'] == rhoHigh]

            if plotData.empty:
                print("  [Warning] No data for rho=0.999, skipping Plot 3.")
                return

            # Melt data for seaborn
            dfMelted = plotData.melt(
                id_vars=['policy'],
                value_vars=self.config.colQueues,
                var_name='queueID',
                value_name='queueSize'
            )

            fig, ax = plt.subplots(figsize=(18, 8))

            sns.violinplot(
                data=dfMelted,
                x='policy',
                y='queueSize',
                hue='queueID',
                split=True,
                inner='quartile',
                palette='pastel',
                ax=ax
            )

            ax.set_title(f'Distribution of Individual Queue Sizes at High Load (ρ={rhoHigh})',
                         fontsize=16, fontweight='bold', y=1.03)
            ax.set_xlabel('Scheduling Policy')
            ax.set_ylabel('Queue Size (Distribution)')
            ax.legend(title='Queue ID', loc='upper left')

            plt.tight_layout()
            self._savePlot(fig, "3_Distribution_ViolinPlots.png")

        except Exception as e:
            print(f"  [Error] Plot 3 failed: {e}")

    def _plotFairnessDynamics(self):
        """
        PLOT 4: (THE DYNAMICS)
        Time series of queue imbalance, faceted by rho.
        Shows *how* UB suppresses imbalance.
        """
        try:
            # Use a random sample to make plotting faster
            plotData = self.steadyStateFrame.sample(n=min(50000, len(self.steadyStateFrame)),
                                                    random_state=42)

            g = sns.FacetGrid(
                plotData,
                col='rho',
                hue='policy',
                palette=self.visConfig.palette,
                height=5,
                aspect=1.2,
                sharey=False  # Imbalance scale changes drastically with rho
            )

            # Plot a smoothed line (rolling mean)
            g.map_dataframe(
                lambda data, color: sns.lineplot(
                    x=data['timestamp'],
                    y=data['queueImbalance'].rolling(window=50, min_periods=1).mean(),
                    color=color,
                    lw=1.5
                )
            )

            g.add_legend(title='Policy')
            g.set_axis_labels('Simulation Time (s)', 'Queue Imbalance')
            g.set_titles(col_template="ρ = {col_name}")

            plt.subplots_adjust(top=0.85)
            g.fig.suptitle('Time Series Dynamics of Queue Imbalance',
                           fontsize=16, fontweight='bold')

            self._savePlot(g.fig, "4_Fairness_Dynamics_TimeSeries.png")

        except Exception as e:
            print(f"  [Error] Plot 4 failed: {e}")

    def _plotCorrelationHeatmaps(self):
        """
        PLOT 5: (THE MECHANISM)
        Heatmaps of correlation between Q1, Q2, Q3 for each policy
        at high load.
        """
        try:
            rhoHigh = '0.999'
            plotData = self.steadyStateFrame[self.steadyStateFrame['rho'] == rhoHigh]

            if plotData.empty:
                print("  [Warning] No data for rho=0.999, skipping Plot 5.")
                return

            fig, axes = plt.subplots(1, 3, figsize=(20, 7), sharey=True)
            fig.suptitle(f'Inter-Queue Correlation at High Load (ρ={rhoHigh})',
                         fontsize=16, fontweight='bold', y=1.0)

            cbar_ax = fig.add_axes([.93, .3, .02, .4])  # Global color bar

            for i, policy in enumerate(self.config.policies):
                ax = axes[i]
                policyData = plotData[plotData['policy'] == policy]
                if policyData.empty:
                    ax.set_title(f'Policy: {policy}\n(No Data)')
                    continue

                corrMatrix = policyData[self.config.colQueues].corr()

                sns.heatmap(
                    corrMatrix,
                    annot=True,
                    fmt='.2f',
                    cmap='coolwarm',
                    vmin=0.8, vmax=1.0,  # Force scale to highlight differences
                    ax=ax,
                    square=True,
                    linewidths=.5,
                    cbar=i == 0,
                    cbar_ax=None if i != 0 else cbar_ax
                )
                ax.set_title(f'Policy: {policy}', fontweight='bold')

            plt.tight_layout(rect=[0, 0, 0.9, 0.95])
            self._savePlot(fig, "5_Correlation_Heatmaps.png")

        except Exception as e:
            print(f"  [Error] Plot 5 failed: {e}")

    def _plotClusterAnalysis(self):
        """
        PLOT 6: (ML - CLUSTERING)
        PCA plot colored by GMM cluster.
        """
        try:
            if 'X_pca' not in self.mlModels:
                print("  [Warning] No PCA data found, skipping Plot 6.")
                return

            pcaData = pd.DataFrame(self.mlModels['X_pca'], columns=['PC1', 'PC2'])
            pcaData['cluster'] = self.mlModels['gmm_clusters'].astype(str)

            fig, ax = plt.subplots(figsize=(10, 7))

            sns.scatterplot(
                data=pcaData.sample(n=min(10000, len(pcaData)), random_state=42),
                x='PC1', y='PC2', hue='cluster',
                alpha=0.4, s=20, ax=ax, palette='viridis'
            )

            varExp = self.mlModels['pca'].explained_variance_ratio_
            title = (f"ML: Probabilistic Clustering of System States (GMM, k=3)\n"
                     f"Silhouette Score: {self.mlModels['gmm_silhouette']:.3f}")
            ax.set_title(title, fontsize=16, fontweight='bold', y=1.02)
            ax.set_xlabel(f'Principal Component 1 ({varExp[0] * 100:.1f}%)')
            ax.set_ylabel(f'Principal Component 2 ({varExp[1] * 100:.1f}%)')
            ax.legend(title='Probabilistic Cluster')

            plt.tight_layout()
            self._savePlot(fig, "6_ML_GMM_Clustering.png")

        except Exception as e:
            print(f"  [Error] Plot 6 failed: {e}")

    def _plotAnomalyAnalysis(self):
        """
        PLOT 7: (ML - ANOMALIES)
        PCA plot highlighting anomalies, and a bar chart of anomaly rates.
        """
        try:
            if 'anomalies' not in self.mlModels:
                print("  [Warning] No anomaly data found, skipping Plot 7.")
                return

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7),
                                           gridspec_kw={'width_ratios': [2, 1]})
            fig.suptitle('ML: Anomaly Detection (Isolation Forest)',
                         fontsize=16, fontweight='bold', y=1.02)

            # --- Left Plot: PCA scatter of anomalies ---
            pcaData = pd.DataFrame(self.mlModels['X_pca'], columns=['PC1', 'PC2'])
            pcaData['anomaly'] = self.mlModels['anomalies'].astype(str)
            pcaData['anomaly'] = pcaData['anomaly'].map({'-1': 'Anomaly', '1': 'Inlier'})

            sns.scatterplot(
                data=pcaData.sample(n=min(10000, len(pcaData)), random_state=42),
                x='PC1', y='PC2', hue='anomaly',
                style='anomaly', markers={'Inlier': '.', 'Anomaly': 'X'},
                s=50, alpha=0.5, ax=ax1,
                palette={'Inlier': 'gray', 'Anomaly': 'red'}
            )
            ax1.set_title('Anomalous System States (e.g., Extreme Imbalance)', fontweight='bold')
            ax1.set_xlabel('Principal Component 1')
            ax1.set_ylabel('Principal Component 2')

            # --- Right Plot: Bar chart of rates ---
            anomalyRates = self.mlModels['anomaly_rates']
            anomalyRates.plot(kind='bar', ax=ax2, color=[self.visConfig.palette[p] for p in anomalyRates.index])
            ax2.set_title('Anomaly Rate by Policy', fontweight='bold')
            ax2.set_ylabel('Anomalous States (%)')
            ax2.set_xlabel('Policy')
            ax2.tick_params(axis='x', rotation=0)

            plt.tight_layout(rect=[0, 0, 1, 0.95])
            self._savePlot(fig, "7_ML_Anomaly_Detection.png")

        except Exception as e:
            print(f"  [Error] Plot 7 failed: {e}")

    def _plotSteadyStateExample(self):
        """
        PLOT 8: (METHODOLOGY)
        Example of steady-state detection.
        """
        try:
            # Find a high-load scenario for demonstration
            high_load_data = self.masterDataFrame[
                (self.masterDataFrame['rho'] == '0.999') &
                (self.masterDataFrame['policy'] == self.config.policies[0])
                ]

            if high_load_data.empty:
                high_load_data = self.masterDataFrame[
                    self.masterDataFrame['policy'] == self.config.policies[0]
                    ].iloc[0:1]
                if high_load_data.empty:
                    print("  [Warning] No data found for steady-state example.")
                    return

            dfFull = high_load_data
            idx = self._findStabilizationPoint(dfFull[self.config.colAggEW])

            fig, ax1 = plt.subplots(figsize=(14, 7))
            ax2 = ax1.twinx()

            policy = dfFull['policy'].iloc[0]
            rho = dfFull['rho'].iloc[0]

            ax1.plot(dfFull[self.config.colTimestamp], dfFull[self.config.colAggEW],
                     label='E[W] (Transient)', color='lightblue', alpha=0.8, zorder=1)
            ax1.plot(dfFull[self.config.colTimestamp].iloc[idx:], dfFull[self.config.colAggEW].iloc[idx:],
                     label='E[W] (Steady-State)', color=self.visConfig.palette[policy], zorder=2)

            rollingMean = dfFull[self.config.colAggEW].rolling(
                window=self.config.stabilizationWindow, min_periods=1).mean()
            ax2.plot(dfFull[self.config.colTimestamp], rollingMean,
                     label=f'Moving Average (window={self.config.stabilizationWindow})',
                     color='red', linestyle='--', zorder=3)

            ax1.axvline(dfFull[self.config.colTimestamp].iloc[idx],
                        label=f'Steady-State Detected ({dfFull[self.config.colTimestamp].iloc[idx]:.0f}s)',
                        color='green', linestyle=':', linewidth=3, zorder=4)

            ax1.set_xlabel('Simulation Time (s)', fontsize=12)
            ax1.set_ylabel('E[W] (s)', color=self.visConfig.palette[policy], fontsize=12)
            ax2.set_ylabel('Moving Average (s)', color='red', fontsize=12)

            fig.legend(loc='upper center', bbox_to_anchor=(0.5, 0.96), ncol=4, fontsize=10)
            fig.suptitle(f'Methodology: Steady-State Detection (Example: {policy}, ρ={rho})',
                         fontsize=16, fontweight='bold', y=1.03)
            plt.tight_layout(rect=[0, 0, 1, 0.9])
            self._savePlot(fig, "8_Methodology_Steady_State.png")

        except Exception as e:
            print(f"  [Error] Plot 8 failed: {e}")

    def _plotCrossMatrixDynamics(self):
        """
        PLOT 9: (THE CROSS-MATRIX DYNAMIC)
        A 3x4 (Policy x Rho) grid of time series plots showing Q1, Q2, Q3.
        """
        try:
            # Melt the full steady-state frame
            dfMelted = self.steadyStateFrame.melt(
                id_vars=['policy', 'rho', self.config.colTimestamp],
                value_vars=self.config.colQueues,
                var_name='queueID',
                value_name='queueSize'
            )

            # Sample for performance
            dfSampled = dfMelted.sample(n=min(100000, len(dfMelted)), random_state=42)

            g = sns.FacetGrid(
                dfSampled,
                col='rho',
                row='policy',
                hue='queueID',
                height=4,
                aspect=1.5,
                margin_titles=True,
                palette='muted'
            )

            g.map(sns.lineplot, 'timestamp', 'queueSize', lw=1, alpha=0.7)

            g.add_legend(title='Queue ID')
            g.set_axis_labels('Simulation Time (s)', 'Queue Size')
            g.set_titles(col_template="ρ = {col_name}", row_template="{row_name}")

            plt.subplots_adjust(top=0.92)
            g.fig.suptitle('Cross-Matrix Dynamics: Individual Queue Behavior by Policy and Scenario',
                           fontsize=16, fontweight='bold')

            self._savePlot(g.fig, "9_CrossMatrix_Dynamics_TimeSeries.png")

        except Exception as e:
            print(f"  [Error] Plot 9 failed: {e}")

    def _plotShapSummary(self):
        """
        PLOT 10: (ML - ATOMIC INSIGHTS)
        SHAP summary beeswarm plot.
        """
        try:
            fig, ax = plt.subplots(figsize=(12, 8))

            shap.summary_plot(
                self.shapValues.values,
                self.mlModels['X_shap_sample'],
                feature_names=self.mlModels['feature_names'],
                show=False,
                plot_type='dot',  # beeswarm
                ax=ax
            )

            ax.set_title('ML Insight: SHAP Feature Importance for Predicting E[W]',
                         fontsize=16, fontweight='bold', y=1.03)

            plt.tight_layout()
            self._savePlot(fig, "10_ML_SHAP_Summary.png")

        except Exception as e:
            print(f"  [Error] Plot 10 failed: {e}")

    def _plotShapDependence(self):
        """
        PLOT 11: (ML - RECURSIVE INSIGHTS)
        SHAP dependence plots for the top 4 features in a 2x2 grid.
        """
        try:
            if self.shapValues.shape[0] == 0:
                print("  [Warning] No SHAP values for dependence plots.")
                return

            # Get top features by mean absolute SHAP value
            shap_abs_mean = np.abs(self.shapValues.values).mean(0)
            top_indices = np.argsort(shap_abs_mean)[::-1][:4]
            topFeatures = [self.mlModels['feature_names'][i] for i in top_indices]

            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('ML Insight: SHAP Dependence Plots (Impact on E[W])',
                         fontsize=16, fontweight='bold', y=1.02)

            axes_flat = axes.flatten()

            for i, feature in enumerate(topFeatures):
                ax = axes_flat[i]

                shap.dependence_plot(
                    feature,
                    self.shapValues.values,
                    self.mlModels['X_shap_sample'],
                    ax=ax,
                    show=False
                )
                ax.set_title(f'Impact of {feature}', fontweight='bold')

            # Remove empty subplots if we have less than 4 features
            for i in range(len(topFeatures), 4):
                fig.delaxes(axes_flat[i])

            plt.tight_layout(rect=[0, 0, 1, 0.95])
            self._savePlot(fig, "11_ML_SHAP_Dependence.png")

        except Exception as e:
            print(f"  [Error] Plot 11 failed: {e}")


# =============================================================================
# SCRIPT EXECUTION
# =============================================================================

if __name__ == "__main__":
    """
    Main entry point for the script.
    """
    pipeline = SimulationAnalysisPipeline()
    pipeline.runFullPipeline()