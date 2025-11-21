# lib/viz.py
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

class PlotterFactory:
    """
    @brief Visualization engine matching 'rafaPlots' style.
    """
    
    def __init__(self, outputDir: Path):
        self.outDir = outputDir
        self.setupStyle()
        
    def setupStyle(self):
        # Matches rafaPlots.py style configuration
        sns.set(style="whitegrid", palette="husl")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.titlesize'] = 16
        plt.rcParams['axes.labelsize'] = 14
        plt.rcParams['savefig.dpi'] = 300
        plt.rcParams['savefig.bbox'] = 'tight'

    def plotTimeSeries(self, df: pd.DataFrame, rho_target=0.9):
        """
        @brief Evolution of E[N] and E[W] over time for a specific load.
        """
        subset = df[df['rho'] == rho_target]
        if subset.empty: return

        fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        
        sns.lineplot(data=subset, x='time', y='system_EN', hue='policy', ax=axes[0], alpha=0.8)
        axes[0].set_title(f'Evolution of System Size E[N] (Rho={rho_target})')
        axes[0].set_ylabel('E[N]')
        
        sns.lineplot(data=subset, x='time', y='system_EW', hue='policy', ax=axes[1], alpha=0.8)
        axes[1].set_title(f'Evolution of Waiting Time E[W] (Rho={rho_target})')
        axes[1].set_ylabel('E[W]')
        
        plt.tight_layout()
        fig.savefig(self.outDir / f"timeseries_rho{rho_target}.png")
        plt.close(fig)

    def plotHeatmap(self, metricsDf: pd.DataFrame):
        """
        @brief Policy vs Rho Occupancy Heatmap.
        """
        pivot = metricsDf.pivot(index='policy', columns='rho', values='occupancy_mean')
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(pivot, annot=True, fmt=".2f", cmap="YlOrRd", linewidths=.5)
        plt.title('Mean System Occupancy Heatmap')
        plt.tight_layout()
        plt.savefig(self.outDir / "heatmap_occupancy.png")
        plt.close()

    def plotViolinDistributions(self, df: pd.DataFrame):
        """
        @brief Distribution of Occupancy across policies.
        """
        plt.figure(figsize=(14, 8))
        sns.violinplot(x='policy', y='total_occupancy', data=df, scale='width')
        plt.xticks(rotation=45)
        plt.title('Distribution of System Occupancy by Policy')
        plt.tight_layout()
        plt.savefig(self.outDir / "violin_occupancy.png")
        plt.close()

    def plotLittleErrorScatter(self, df: pd.DataFrame):
        """
        @brief Scatter plot of Little's Law Error vs Occupancy.
        """
        plt.figure(figsize=(12, 8))
        sns.scatterplot(data=df, x='total_occupancy', y='little_error', hue='policy', alpha=0.6)
        plt.yscale('log')
        plt.title("Little's Law Error vs System Occupancy")
        plt.ylabel("Little's Law Relative Error (Log Scale)")
        plt.tight_layout()
        plt.savefig(self.outDir / "scatter_little_error.png")
        plt.close()