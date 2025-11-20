#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PlotterFactory Module
=====================
Scientific Visualization Generator.
Handles high-resolution plotting for time-series, heatmaps, and radar charts.
"""

# --- CORREÇÃO CRÍTICA: PREVINE O ERRO DE WEBVIEW/SERVICE WORKER ---
import matplotlib
# Força o backend não-interativo (Headless). 
# Isso impede que o script tente abrir janelas ou usar o visualizador do IDE que está travando.
matplotlib.use('Agg') 

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from math import pi
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class PlotterFactory:
    """
    @brief Factory class for generating publication-quality visualizations.
    """

    def __init__(self, outputDir: Path):
        """
        @brief Constructor for PlotterFactory.
        @param outputDir Path object where images will be saved.
        """
        self.outputDir = outputDir
        # Set style preferences
        plt.style.use('ggplot') 
        sns.set_context("paper", font_scale=1.4)
        self.dpi = 300

    def generateHeatmap(self, metricsDf: pd.DataFrame):
        """
        @brief Generates a heatmap of System Occupancy across Policy vs Rho.
        @param metricsDf Aggregated statistics DataFrame.
        """
        try:
            logger.info("Generating Heatmap...")
            pivot = metricsDf.pivot(index='policy', columns='rho', values='occupancyMean')
            
            plt.figure(figsize=(12, 8))
            sns.heatmap(pivot, annot=True, fmt=".1f", cmap="turbo", linewidths=.5)
            plt.title("Global System Occupancy Heatmap")
            plt.tight_layout()
            
            savePath = self.outputDir / "01_heatmap_occupancy.png"
            plt.savefig(savePath, dpi=self.dpi, bbox_inches='tight')
            # CRÍTICO: Fecha a memória gráfica para não travar o IDE
            plt.close() 
        except Exception as e:
            logger.error(f"Failed to generate Heatmap: {e}")

    def generateTimeSeriesComparison(self, rawDf: pd.DataFrame, targetRho: float):
        """
        @brief Plots the temporal evolution of occupancy (Rolling Mean).
        @param rawDf The raw simulation data with timestamps.
        @param targetRho The load factor to analyze.
        """
        try:
            logger.info(f"Generating Time Series for Rho={targetRho}...")
            subset = rawDf[rawDf['rho'] == targetRho].copy()
            
            if subset.empty:
                logger.warning(f"No data found for rho={targetRho} in time series analysis.")
                return

            plt.figure(figsize=(15, 7))
            
            # Smoothing window size
            windowSize = 100 
            
            policies = subset['policy'].unique()
            
            for policy in policies:
                # Sort by time to ensure correct line plotting
                policyData = subset[subset['policy'] == policy].sort_values('timestamp')
                
                # Calculate rolling mean to reduce noise
                smoothed = policyData['system_occupancy'].rolling(window=windowSize).mean()
                
                plt.plot(policyData['timestamp'], smoothed, label=str(policy), linewidth=2, alpha=0.8)

            plt.title(f"Temporal Dynamics: System Occupancy (Rho={targetRho})")
            plt.xlabel("Simulation Time (s)")
            plt.ylabel(f"Occupancy (Rolling Mean w={windowSize})")
            plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            savePath = self.outputDir / f"02_timeseries_rho{targetRho}.png"
            plt.savefig(savePath, dpi=self.dpi, bbox_inches='tight')
            plt.close()
        except Exception as e:
            logger.error(f"Failed to generate Time Series: {e}")

    def generateRadarChart(self, metricsDf: pd.DataFrame, targetRho: float):
        """
        @brief Generates a Radar Chart (Spider Plot) for multi-criteria comparison.
        @param metricsDf Aggregated statistics DataFrame.
        @param targetRho The load factor to analyze.
        """
        try:
            logger.info("Generating Radar Chart...")
            subset = metricsDf[metricsDf['rho'] == targetRho].copy()
            if subset.empty:
                return

            # Define metrics (Axes of the radar)
            categories = ['occupancyMean', 'occupancyStd', 'littleError', 'utilization', 'q0Mean']
            N = len(categories)
            
            # Normalize data [0, 1]
            normalized = subset.copy()
            for col in categories:
                minVal = subset[col].min()
                maxVal = subset[col].max()
                if maxVal - minVal != 0:
                    normalized[col] = (subset[col] - minVal) / (maxVal - minVal)
                else:
                    normalized[col] = 0.5

            # Invert 'Negative' metrics (Lower is better -> Higher score)
            # We want the graph to show "Bigger Area = Better Performance"
            for col in ['occupancyMean', 'occupancyStd', 'littleError', 'q0Mean']:
                normalized[col] = 1 - normalized[col]

            # Calculate angles
            angles = [n / float(N) * 2 * pi for n in range(N)]
            angles += angles[:1] # Close the loop

            plt.figure(figsize=(10, 10))
            ax = plt.subplot(111, polar=True)
            
            # Setup axis labels
            plt.xticks(angles[:-1], categories, color='black', size=10)
            ax.set_rlabel_position(0)
            plt.yticks([0.25, 0.5, 0.75], ["0.25", "0.5", "0.75"], color="grey", size=7)
            plt.ylim(0, 1)

            # Plot each policy
            colors = sns.color_palette("bright", n_colors=len(subset))
            
            for i, (idx, row) in enumerate(normalized.iterrows()):
                values = row[categories].values.flatten().tolist()
                values += values[:1] # Close the loop
                
                policyName = str(row['policy'])
                ax.plot(angles, values, linewidth=2, linestyle='solid', label=policyName, color=colors[i])
                ax.fill(angles, values, color=colors[i], alpha=0.05)

            plt.title(f"Multi-Criteria Comparison (Rho={targetRho})\n(Outer Edge = Superior Performance)", y=1.08)
            plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
            
            savePath = self.outputDir / f"03_radar_comparison_rho{targetRho}.png"
            plt.savefig(savePath, dpi=self.dpi, bbox_inches='tight')
            plt.close()
        except Exception as e:
            logger.error(f"Failed to generate Radar Chart: {e}")

    def generateScatterMatrix(self, rawDf: pd.DataFrame, targetRho: float):
        """
        @brief Generates a Scatter Plot correlating Occupancy vs Little's Law Error.
        @param rawDf Raw simulation data.
        @param targetRho The load factor to analyze.
        """
        try:
            logger.info("Generating Scatter Matrix...")
            subset = rawDf[rawDf['rho'] == targetRho]
            if subset.empty: return

            # Downsample for performance (Plotting 200k dots makes the file huge and slow)
            sampleSize = min(2000, len(subset))
            sample = subset.sample(n=sampleSize, random_state=42)

            plt.figure(figsize=(10, 8))
            sns.scatterplot(
                data=sample, 
                x='system_occupancy', 
                y='little_error', 
                hue='policy', 
                style='server_busy',
                alpha=0.7,
                s=60
            )
            plt.title(f"Little's Law Validation: Error vs Occupancy (Rho={targetRho})")
            plt.yscale('log') 
            plt.ylabel("Little's Law Error (Log Scale)")
            plt.tight_layout()
            
            savePath = self.outputDir / "04_scatter_error_vs_occupancy.png"
            plt.savefig(savePath, dpi=self.dpi, bbox_inches='tight')
            plt.close()
        except Exception as e:
            logger.error(f"Failed to generate Scatter Matrix: {e}")