#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comprehensive Queueing Simulation Data Analysis
Author: Rafael Passos Domingues
Date: 2025 Sep 25

Complete analysis script for queueing simulation data including stabilization detection,
comprehensive visualizations, and machine learning modeling for M/M/c systems.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Configure plotting style for publication quality
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 9

class QueueDataAnalyzer:
    def __init__(self, data_dir="results"):
        self.data_dir = data_dir
        self.data = {}
        self.stable_points = {}
        self.stable_data = {}
        self.analytical_models = {}
        
    def load_data(self):
        """Load all CSV files from simulation scenarios"""
        print("Loading simulation data...")
        
        scenarios = ['0.800', '0.900', '0.950', '0.999']
        
        for scenario in scenarios:
            filename = f"{self.data_dir}/dados_ocupacao_{scenario}.csv"
            try:
                df = pd.read_csv(filename)
                df['scenario'] = f"ρ = {scenario}"
                df['rho'] = float(scenario)
                self.data[scenario] = df
                print(f"✓ Loaded: {filename} - {len(df)} samples")
            except FileNotFoundError:
                print(f"✗ File not found: {filename}")
                continue
                
        return len(self.data)
    
    def detect_stabilization(self, method='composite', window_size=200):
        """
        Detect stabilization points using multiple methods
        
        Parameters:
        -----------
        method : str
            'composite' - uses multiple methods for robust detection
            'kmeans' - KMeans clustering based approach
            'variance' - sliding window variance method
        window_size : int
            Size of sliding window for variance method
        """
        print("\n" + "="*60)
        print("STABILIZATION POINT DETECTION")
        print("="*60)
        
        for scenario, df in self.data.items():
            print(f"\nAnalyzing scenario ρ = {scenario}:")
            
            if method == 'composite':
                # Use multiple methods and take the most conservative estimate
                kmeans_idx = self._kmeans_stabilization(df)
                variance_idx = self._variance_stabilization(df, window_size)
                conservative_idx = self._conservative_stabilization(df)
                
                # Take the maximum (most conservative) stabilization point
                stable_idx = max(kmeans_idx, variance_idx, conservative_idx)
                
                print(f"  KMeans method: sample {kmeans_idx} ({(kmeans_idx/len(df))*100:.1f}%)")
                print(f"  Variance method: sample {variance_idx} ({(variance_idx/len(df))*100:.1f}%)")
                print(f"  Conservative method: sample {conservative_idx} ({(conservative_idx/len(df))*100:.1f}%)")
                
            elif method == 'kmeans':
                stable_idx = self._kmeans_stabilization(df)
            elif method == 'variance':
                stable_idx = self._variance_stabilization(df, window_size)
            else:
                stable_idx = self._conservative_stabilization(df)
            
            self.stable_points[scenario] = stable_idx
            self.stable_data[scenario] = df.iloc[stable_idx:]
            
            print(f"  → Final stabilization point: sample {stable_idx} ({(stable_idx/len(df))*100:.1f}%)")
            print(f"  → Stable data: {len(self.stable_data[scenario])} samples")
            
        return self.stable_points
    
    def _kmeans_stabilization(self, df, max_clusters=5):
        """Detect stabilization using KMeans elbow method"""
        features = df[['EN', 'EW', 'measuredLambda', 'measuredOccupancy']].values
        
        if len(features) < 10:
            return int(len(df) * 0.25)
        
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Find optimal number of clusters
        silhouette_scores = []
        for i in range(2, min(max_clusters + 1, len(features) - 1)):
            kmeans = KMeans(n_clusters=i, random_state=42, n_init=10)
            labels = kmeans.fit_predict(features_scaled)
            if len(np.unique(labels)) > 1:
                score = silhouette_score(features_scaled, labels)
                silhouette_scores.append(score)
            else:
                silhouette_scores.append(0)
        
        if len(silhouette_scores) > 0:
            optimal_clusters = np.argmax(silhouette_scores) + 2
        else:
            optimal_clusters = 2
        
        # Apply KMeans with optimal clusters
        kmeans = KMeans(n_clusters=optimal_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(features_scaled)
        
        # Find last cluster transition point
        changes = np.where(np.diff(labels) != 0)[0]
        stable_idx = changes[-1] + 1 if len(changes) > 0 else int(len(df) * 0.25)
        
        return min(stable_idx, int(len(df) * 0.8))
    
    def _variance_stabilization(self, df, window_size):
        """Detect stabilization using sliding window variance analysis"""
        if len(df) < window_size * 2:
            return int(len(df) * 0.25)
        
        en_values = df['EN'].values
        ew_values = df['EW'].values
        
        # Calculate rolling variance
        variances = []
        for i in range(window_size, len(en_values)):
            window_en = en_values[i-window_size:i]
            window_ew = ew_values[i-window_size:i]
            var_combined = (np.var(window_en) + np.var(window_ew)) / 2
            variances.append(var_combined)
        
        # Find stabilization point where variance derivative stabilizes
        if len(variances) > 10:
            derivatives = np.diff(variances)
            # Use statistical threshold for stabilization
            threshold = np.std(derivatives) * 0.05
            stable_indices = np.where(np.abs(derivatives) < threshold)[0]
            stable_idx = stable_indices[0] + window_size if len(stable_indices) > 0 else int(len(df) * 0.25)
        else:
            stable_idx = int(len(df) * 0.25)
            
        return stable_idx
    
    def _conservative_stabilization(self, df):
        """Conservative approach: discard first 25% of data"""
        return int(len(df) * 0.25)
    
    def plot_en_ew_vs_time(self):
        """1. EN and EW overlaid on y-axis as function of time on x-axis"""
        print("\nGenerating EN and EW vs Time plots...")
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.ravel()
        
        for idx, (scenario, df) in enumerate(self.data.items()):
            stable_idx = self.stable_points[scenario]
            stable_time = df.iloc[stable_idx]['timestamp']
            
            ax = axes[idx]
            # Plot complete data
            ax.plot(df['timestamp'], df['EN'], label='E[N]', alpha=0.8, linewidth=1.5, color='blue')
            ax.plot(df['timestamp'], df['EW'], label='E[W]', alpha=0.8, linewidth=1.5, color='red')
            
            # Mark stabilization point
            ax.axvline(x=stable_time, color='black', linestyle='--', alpha=0.8, 
                      label=f'Stabilization: {stable_time:.0f}s')
            
            # Shade transient region
            ax.axvspan(0, stable_time, alpha=0.1, color='gray', label='Transient region')
            
            ax.set_title(f'ρ = {scenario}', fontweight='bold')
            ax.set_xlabel('Time (seconds)')
            ax.set_ylabel('E[N] / E[W]')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.suptitle('E[N] and E[W] vs Time for Different Occupancy Scenarios', fontweight='bold', y=0.98)
        plt.tight_layout()
        plt.savefig('en_ew_vs_time.png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print("✓ Saved: en_ew_vs_time.png")
    
    def plot_en_ew_vs_queue_size(self):
        """2. EN and EW vs queue size with temporal gradient"""
        print("\nGenerating EN and EW vs Queue Size plots...")
        
        fig, axes = plt.subplots(3, 4, figsize=(16, 12))
        scenarios = list(self.stable_data.keys())
        
        for col, scenario in enumerate(scenarios):
            df_stable = self.stable_data[scenario]
            
            for row, queue_num in enumerate([1, 2, 3]):
                ax = axes[row, col]
                queue_col = f'queueSize{queue_num}'
                
                # Create scatter plots with temporal gradient
                sc1 = ax.scatter(df_stable[queue_col], df_stable['EN'], 
                               c=df_stable['timestamp'], cmap='viridis', 
                               alpha=0.7, s=15, label='E[N]', marker='o')
                sc2 = ax.scatter(df_stable[queue_col], df_stable['EW'], 
                               c=df_stable['timestamp'], cmap='plasma', 
                               alpha=0.7, s=15, label='E[W]', marker='s')
                
                ax.set_title(f'ρ = {scenario} - Queue {queue_num}', fontweight='bold')
                ax.set_xlabel(f'Queue {queue_num} Size')
                ax.set_ylabel('E[N] / E[W]')
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                # Add colorbars for the first column only to save space
                if col == 0:
                    cbar1 = plt.colorbar(sc1, ax=ax, shrink=0.8)
                    cbar1.set_label('Time (s) - E[N]')
        
        plt.suptitle('E[N] and E[W] vs Queue Size with Temporal Gradient', fontweight='bold', y=0.98)
        plt.tight_layout()
        plt.savefig('en_ew_vs_queue_size.png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print("✓ Saved: en_ew_vs_queue_size.png")
    
    def plot_queues_vs_time(self):
        """3. Queue sizes vs time - individual and overlaid"""
        print("\nGenerating Queue Sizes vs Time plots...")
        
        # Individual queue plots
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        axes = axes.ravel()
        
        for idx, (scenario, df) in enumerate(self.data.items()):
            ax = axes[idx]
            stable_idx = self.stable_points[scenario]
            stable_time = df.iloc[stable_idx]['timestamp']
            
            for queue_num in [1, 2, 3]:
                queue_col = f'queueSize{queue_num}'
                ax.plot(df['timestamp'], df[queue_col], 
                       label=f'Queue {queue_num}', alpha=0.8, linewidth=1.2)
            
            ax.axvline(x=stable_time, color='black', linestyle='--', 
                      label=f'Stabilization: {stable_time:.0f}s')
            ax.axvspan(0, stable_time, alpha=0.1, color='gray')
            
            ax.set_title(f'ρ = {scenario}', fontweight='bold')
            ax.set_xlabel('Time (seconds)')
            ax.set_ylabel('Queue Size')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.suptitle('Individual Queue Sizes vs Time', fontweight='bold', y=0.98)
        plt.tight_layout()
        plt.savefig('queues_individual.png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        # Overlaid total queue size
        plt.figure(figsize=(10, 6))
        for scenario, df in self.data.items():
            total_queue = df['queueSize1'] + df['queueSize2'] + df['queueSize3']
            plt.plot(df['timestamp'], total_queue, label=f'ρ = {scenario}', linewidth=1.5)
        
        plt.xlabel('Time (seconds)')
        plt.ylabel('Total Queue Size (All Queues)')
        plt.title('Total Queue Size vs Time - All Scenarios', fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('queues_total.png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print("✓ Saved: queues_individual.png")
        print("✓ Saved: queues_total.png")
    
    def plot_lambda_vs_occupancy(self):
        """4. Lambda vs Occupancy and their temporal evolution"""
        print("\nGenerating Lambda vs Occupancy analysis plots...")
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Lambda vs Occupancy scatter
        ax1 = axes[0, 0]
        for scenario, df_stable in self.stable_data.items():
            ax1.scatter(df_stable['measuredLambda'], df_stable['measuredOccupancy'],
                       label=f'ρ = {scenario}', alpha=0.7, s=20)
        
        ax1.set_xlabel('Measured Lambda (arrivals/sec)')
        ax1.set_ylabel('Measured Occupancy')
        ax1.set_title('Lambda vs Occupancy', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Lambda vs Time
        ax2 = axes[0, 1]
        for scenario, df in self.data.items():
            stable_idx = self.stable_points[scenario]
            stable_time = df.iloc[stable_idx]['timestamp']
            
            ax2.plot(df['timestamp'], df['measuredLambda'], 
                    label=f'ρ = {scenario}', linewidth=1.2)
            ax2.axvline(x=stable_time, color='black', linestyle='--', alpha=0.5)
        
        ax2.set_xlabel('Time (seconds)')
        ax2.set_ylabel('Measured Lambda')
        ax2.set_title('Lambda vs Time', fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Occupancy vs Time
        ax3 = axes[1, 0]
        for scenario, df in self.data.items():
            stable_idx = self.stable_points[scenario]
            stable_time = df.iloc[stable_idx]['timestamp']
            
            ax3.plot(df['timestamp'], df['measuredOccupancy'], 
                    label=f'ρ = {scenario}', linewidth=1.2)
            ax3.axvline(x=stable_time, color='black', linestyle='--', alpha=0.5)
        
        ax3.set_xlabel('Time (seconds)')
        ax3.set_ylabel('Measured Occupancy')
        ax3.set_title('Occupancy vs Time', fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Little's Law Error vs Time
        ax4 = axes[1, 1]
        for scenario, df in self.data.items():
            stable_idx = self.stable_points[scenario]
            stable_time = df.iloc[stable_idx]['timestamp']
            
            ax4.plot(df['timestamp'], df['littleError'], 
                    label=f'ρ = {scenario}', linewidth=1.2)
            ax4.axvline(x=stable_time, color='black', linestyle='--', alpha=0.5)
            ax4.axhline(y=0, color='red', linestyle='-', alpha=0.3)
        
        ax4.set_xlabel('Time (seconds)')
        ax4.set_ylabel("Little's Law Error")
        ax4.set_title("Little's Law Error vs Time", fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.suptitle('Lambda and Occupancy Analysis', fontweight='bold', y=0.98)
        plt.tight_layout()
        plt.savefig('lambda_occupancy_analysis.png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print("✓ Saved: lambda_occupancy_analysis.png")
    
    def plot_en_ew_vs_lambda_occupancy(self):
        """5. EN and EW vs Lambda and vs Occupancy"""
        print("\nGenerating EN and EW dependency plots...")
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # EN vs Lambda
        ax1 = axes[0, 0]
        for scenario, df_stable in self.stable_data.items():
            ax1.scatter(df_stable['measuredLambda'], df_stable['EN'],
                       label=f'ρ = {scenario}', alpha=0.7, s=20)
        
        ax1.set_xlabel('Measured Lambda')
        ax1.set_ylabel('E[N]')
        ax1.set_title('E[N] vs Lambda', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # EW vs Lambda
        ax2 = axes[0, 1]
        for scenario, df_stable in self.stable_data.items():
            ax2.scatter(df_stable['measuredLambda'], df_stable['EW'],
                       label=f'ρ = {scenario}', alpha=0.7, s=20)
        
        ax2.set_xlabel('Measured Lambda')
        ax2.set_ylabel('E[W]')
        ax2.set_title('E[W] vs Lambda', fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # EN vs Occupancy
        ax3 = axes[1, 0]
        for scenario, df_stable in self.stable_data.items():
            ax3.scatter(df_stable['measuredOccupancy'], df_stable['EN'],
                       label=f'ρ = {scenario}', alpha=0.7, s=20)
        
        ax3.set_xlabel('Measured Occupancy')
        ax3.set_ylabel('E[N]')
        ax3.set_title('E[N] vs Occupancy', fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # EW vs Occupancy
        ax4 = axes[1, 1]
        for scenario, df_stable in self.stable_data.items():
            ax4.scatter(df_stable['measuredOccupancy'], df_stable['EW'],
                       label=f'ρ = {scenario}', alpha=0.7, s=20)
        
        ax4.set_xlabel('Measured Occupancy')
        ax4.set_ylabel('E[W]')
        ax4.set_title('E[W] vs Occupancy', fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.suptitle('E[N] and E[W] Dependency Analysis', fontweight='bold', y=0.98)
        plt.tight_layout()
        plt.savefig('en_ew_dependencies.png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print("✓ Saved: en_ew_dependencies.png")
    
    def plot_statistical_distributions(self):
        """6. Histograms, pairplots, and boxplots"""
        print("\nGenerating statistical distribution plots...")
        
        # Combine all stable data
        all_stable_data = pd.concat([
            df.assign(scenario_label=scenario) 
            for scenario, df in self.stable_data.items()
        ])
        
        # Histograms
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        metrics = ['EN', 'EW', 'measuredLambda', 'measuredOccupancy', 'littleError']
        
        for idx, metric in enumerate(metrics):
            ax = axes[idx//3, idx%3]
            for scenario in self.stable_data.keys():
                data = self.stable_data[scenario][metric]
                ax.hist(data, alpha=0.6, label=f'ρ = {scenario}', bins=30, density=True)
            
            ax.set_xlabel(metric)
            ax.set_ylabel('Probability Density')
            ax.set_title(f'Distribution of {metric}', fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        # Remove empty subplot
        axes[1, 2].set_visible(False)
        
        plt.suptitle('Probability Distributions of Key Metrics', fontweight='bold', y=0.98)
        plt.tight_layout()
        plt.savefig('distributions.png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        # Boxplots
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        for idx, metric in enumerate(metrics):
            ax = axes[idx//3, idx%3]
            data_to_plot = [self.stable_data[scenario][metric] for scenario in self.stable_data.keys()]
            labels = [f'ρ = {scenario}' for scenario in self.stable_data.keys()]
            
            box_plot = ax.boxplot(data_to_plot, labels=labels, patch_artist=True)
            
            # Color the boxes
            colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
            for patch, color in zip(box_plot['boxes'], colors):
                patch.set_facecolor(color)
            
            ax.set_ylabel(metric)
            ax.set_title(f'Boxplot of {metric}', fontweight='bold')
            plt.setp(ax.get_xticklabels(), rotation=45)
            ax.grid(True, alpha=0.3)
        
        axes[1, 2].set_visible(False)
        
        plt.suptitle('Boxplots of Key Metrics Across Scenarios', fontweight='bold', y=0.98)
        plt.tight_layout()
        plt.savefig('boxplots.png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        # Pairplot (simplified version using matplotlib)
        self._create_pairplot(all_stable_data)
        
        print("✓ Saved: distributions.png")
        print("✓ Saved: boxplots.png")
        print("✓ Saved: pairplot.png")
    
    def _create_pairplot(self, data):
        """Create a pairplot using matplotlib subplots"""
        variables = ['EN', 'EW', 'measuredLambda', 'measuredOccupancy', 'rho']
        n_vars = len(variables)
        
        fig, axes = plt.subplots(n_vars, n_vars, figsize=(15, 15))
        
        scenarios = data['scenario_label'].unique()
        colors = plt.cm.tab10(np.linspace(0, 1, len(scenarios)))
        
        for i, var_x in enumerate(variables):
            for j, var_y in enumerate(variables):
                ax = axes[i, j]
                
                if i == j:
                    # Diagonal: histograms
                    for k, scenario in enumerate(scenarios):
                        scenario_data = data[data['scenario_label'] == scenario]
                        ax.hist(scenario_data[var_x], alpha=0.6, 
                               color=colors[k], label=f'ρ = {scenario}', bins=20, density=True)
                    ax.set_ylabel('Density')
                else:
                    # Off-diagonal: scatter plots
                    for k, scenario in enumerate(scenarios):
                        scenario_data = data[data['scenario_label'] == scenario]
                        ax.scatter(scenario_data[var_x], scenario_data[var_y],
                                 alpha=0.6, color=colors[k], s=10, label=f'ρ = {scenario}')
                    ax.set_ylabel(var_y)
                
                ax.set_xlabel(var_x)
                ax.grid(True, alpha=0.3)
                
                # Only show legend for first plot
                if i == 0 and j == 0:
                    ax.legend()
        
        plt.suptitle('Pairplot of Key Variables', fontweight='bold', y=0.98)
        plt.tight_layout()
        plt.savefig('pairplot.png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
    
    def apply_kmeans_and_analytical_models(self):
        """7. Apply KMeans clustering and derive analytical expressions"""
        print("\n" + "="*60)
        print("MACHINE LEARNING ANALYSIS & ANALYTICAL MODELING")
        print("="*60)
        
        # Combine all stable data
        all_data = pd.concat([
            df.assign(scenario_label=scenario, rho_value=float(scenario)) 
            for scenario, df in self.stable_data.items()
        ])
        
        if len(all_data) < 10:
            print("Insufficient data for ML analysis")
            return None, None
        
        # Prepare features for clustering
        feature_columns = ['EN', 'EW', 'measuredLambda', 'measuredOccupancy', 
                          'queueSize1', 'queueSize2', 'queueSize3']
        features = all_data[feature_columns].dropna()
        
        if len(features) < 10:
            print("Not enough features for clustering")
            return None, None
        
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Determine optimal number of clusters
        print("\nDetermining optimal number of clusters...")
        wcss = []
        silhouette_scores = []
        max_clusters = min(8, len(features) - 1)
        
        for i in range(2, max_clusters + 1):
            kmeans = KMeans(n_clusters=i, random_state=42, n_init=10)
            labels = kmeans.fit_predict(features_scaled)
            wcss.append(kmeans.inertia_)
            
            if len(np.unique(labels)) > 1:
                score = silhouette_score(features_scaled, labels)
                silhouette_scores.append(score)
            else:
                silhouette_scores.append(0)
        
        optimal_clusters = np.argmax(silhouette_scores) + 2
        print(f"Optimal number of clusters: {optimal_clusters}")
        print(f"Best silhouette score: {silhouette_scores[optimal_clusters-2]:.4f}")
        
        # Apply final KMeans
        kmeans = KMeans(n_clusters=optimal_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(features_scaled)
        all_data.loc[features.index, 'cluster'] = cluster_labels
        
        # Visualize clusters
        self._visualize_clusters(all_data, features_scaled, kmeans)
        
        # Derive analytical expressions
        self._derive_analytical_expressions(all_data)
        
        return all_data, kmeans
    
    def _visualize_clusters(self, all_data, features_scaled, kmeans):
        """Visualize KMeans clustering results"""
        # PCA for 2D visualization
        pca = PCA(n_components=2)
        features_pca = pca.fit_transform(features_scaled)
        
        plt.figure(figsize=(10, 8))
        scatter = plt.scatter(features_pca[:, 0], features_pca[:, 1], 
                             c=all_data['cluster'].dropna(), cmap='viridis', 
                             alpha=0.7, s=30)
        plt.colorbar(scatter, label='Cluster')
        plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} variance)')
        plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} variance)')
        plt.title('KMeans Clustering Results (PCA Visualization)', fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('kmeans_clusters.png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print("✓ Saved: kmeans_clusters.png")
    
    def _derive_analytical_expressions(self, all_data):
        """Derive analytical expressions for E[N] and E[W]"""
        print("\n" + "-"*40)
        print("DERIVING ANALYTICAL EXPRESSIONS")
        print("-"*40)
        
        # Clean data
        clean_data = all_data.dropna(subset=['EN', 'EW', 'rho_value'])
        
        if len(clean_data) < 10:
            print("Insufficient data for analytical modeling")
            return
        
        rho_values = clean_data['rho_value'].values
        en_values = clean_data['EN'].values
        ew_values = clean_data['EW'].values
        
        # Model 1: Polynomial regression for E[N]
        print("\n1. E[N] as function of ρ:")
        try:
            # Try different polynomial degrees
            best_degree_en = 3
            best_r2_en = 0
            
            for degree in [2, 3, 4]:
                coeffs = np.polyfit(rho_values, en_values, degree)
                poly = np.poly1d(coeffs)
                y_pred = poly(rho_values)
                r2 = 1 - np.sum((en_values - y_pred)**2) / np.sum((en_values - np.mean(en_values))**2)
                
                if r2 > best_r2_en:
                    best_r2_en = r2
                    best_degree_en = degree
                    best_coeffs_en = coeffs
            
            poly_en = np.poly1d(best_coeffs_en)
            self.analytical_models['EN'] = {
                'type': f'polynomial_degree_{best_degree_en}',
                'coefficients': best_coeffs_en,
                'r_squared': best_r2_en,
                'function': poly_en
            }
            
            print(f"   Best model: degree {best_degree_en}")
            print(f"   E[N] ≈ {best_coeffs_en[0]:.6f}·ρ^{best_degree_en} + ... + {best_coeffs_en[-1]:.6f}")
            print(f"   R² = {best_r2_en:.6f}")
            
        except Exception as e:
            print(f"   Error fitting E[N] model: {e}")
        
        # Model 2: Polynomial regression for E[W]
        print("\n2. E[W] as function of ρ:")
        try:
            best_degree_ew = 3
            best_r2_ew = 0
            
            for degree in [2, 3, 4]:
                coeffs = np.polyfit(rho_values, ew_values, degree)
                poly = np.poly1d(coeffs)
                y_pred = poly(rho_values)
                r2 = 1 - np.sum((ew_values - y_pred)**2) / np.sum((ew_values - np.mean(ew_values))**2)
                
                if r2 > best_r2_ew:
                    best_r2_ew = r2
                    best_degree_ew = degree
                    best_coeffs_ew = coeffs
            
            poly_ew = np.poly1d(best_coeffs_ew)
            self.analytical_models['EW'] = {
                'type': f'polynomial_degree_{best_degree_ew}',
                'coefficients': best_coeffs_ew,
                'r_squared': best_r2_ew,
                'function': poly_ew
            }
            
            print(f"   Best model: degree {best_degree_ew}")
            print(f"   E[W] ≈ {best_coeffs_ew[0]:.6f}·ρ^{best_degree_ew} + ... + {best_coeffs_ew[-1]:.6f}")
            print(f"   R² = {best_r2_ew:.6f}")
            
        except Exception as e:
            print(f"   Error fitting E[W] model: {e}")
        
        # Model 3: M/M/c approximation for multiple queues
        print("\n3. M/M/c Approximation for Multiple Queues:")
        print("   For c servers and n queues:")
        print("   E[N] ≈ (ρ/(1-ρ)) · (c² + c)/(2c) · f(n, policy)")
        print("   E[W] ≈ E[N] / (λ · c)")
        print("   where f(n, policy) depends on queue configuration and scheduling policy")
        
        # Plot the fitted models
        self._plot_analytical_models(clean_data)
    
    def _plot_analytical_models(self, data):
        """Plot the fitted analytical models"""
        if 'EN' not in self.analytical_models or 'EW' not in self.analytical_models:
            return
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        rho_range = np.linspace(data['rho_value'].min(), data['rho_value'].max(), 100)
        
        # E[N] model
        poly_en = self.analytical_models['EN']['function']
        ax1.scatter(data['rho_value'], data['EN'], alpha=0.6, s=20, label='Data')
        ax1.plot(rho_range, poly_en(rho_range), 'r-', linewidth=2, 
                label=f'Model (R² = {self.analytical_models["EN"]["r_squared"]:.4f})')
        ax1.set_xlabel('ρ (Occupancy)')
        ax1.set_ylabel('E[N]')
        ax1.set_title('Analytical Model for E[N]', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # E[W] model
        poly_ew = self.analytical_models['EW']['function']
        ax2.scatter(data['rho_value'], data['EW'], alpha=0.6, s=20, label='Data')
        ax2.plot(rho_range, poly_ew(rho_range), 'r-', linewidth=2,
                label=f'Model (R² = {self.analytical_models["EW"]["r_squared"]:.4f})')
        ax2.set_xlabel('ρ (Occupancy)')
        ax2.set_ylabel('E[W]')
        ax2.set_title('Analytical Model for E[W]', fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('analytical_models.png', dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        print("✓ Saved: analytical_models.png")
    
    def generate_comprehensive_report(self):
        """Generate complete analysis report"""
        print("="*70)
        print("COMPREHENSIVE QUEUEING SIMULATION ANALYSIS")
        print("="*70)
        
        # Load data
        num_files = self.load_data()
        if num_files == 0:
            print("Error: No data files found!")
            return None
        
        print(f"\nSuccessfully loaded {num_files} scenario files")
        
        # Detect stabilization points
        self.detect_stabilization(method='composite')
        
        # Generate all visualizations
        print("\n" + "="*70)
        print("GENERATING VISUALIZATIONS")
        print("="*70)
        
        self.plot_en_ew_vs_time()
        self.plot_en_ew_vs_queue_size()
        self.plot_queues_vs_time()
        self.plot_lambda_vs_occupancy()
        self.plot_en_ew_vs_lambda_occupancy()
        self.plot_statistical_distributions()
        
        # Apply machine learning
        print("\n" + "="*70)
        print("MACHINE LEARNING ANALYSIS")
        print("="*70)
        
        results = self.apply_kmeans_and_analytical_models()
        
        # Save processed data
        if results:
            all_data, kmeans = results
            all_data.to_csv('processed_simulation_data.csv', index=False)
            print("✓ Saved: processed_simulation_data.csv")
        
        # Generate summary statistics
        self._generate_summary_statistics()
        
        print("\n" + "="*70)
        print("ANALYSIS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"Scenarios analyzed: {num_files}")
        print(f"Total plots generated: 10 high-resolution PNG files")
        print(f"Processed data saved: processed_simulation_data.csv")
        print("\nGenerated files:")
        print("• en_ew_vs_time.png")
        print("• en_ew_vs_queue_size.png") 
        print("• queues_individual.png, queues_total.png")
        print("• lambda_occupancy_analysis.png")
        print("• en_ew_dependencies.png")
        print("• distributions.png, boxplots.png, pairplot.png")
        print("• kmeans_clusters.png")
        print("• analytical_models.png")
        
        return results
    
    def _generate_summary_statistics(self):
        """Generate summary statistics for the report"""
        print("\n" + "-"*40)
        print("SUMMARY STATISTICS")
        print("-"*40)
        
        for scenario, df_stable in self.stable_data.items():
            print(f"\nScenario ρ = {scenario} (stable region):")
            print(f"  E[N]: mean = {df_stable['EN'].mean():.4f}, std = {df_stable['EN'].std():.4f}")
            print(f"  E[W]: mean = {df_stable['EW'].mean():.4f}, std = {df_stable['EW'].std():.4f}")
            print(f"  Lambda: mean = {df_stable['measuredLambda'].mean():.4f}")
            print(f"  Occupancy: mean = {df_stable['measuredOccupancy'].mean():.4f}")
            print(f"  Little's Error: mean = {df_stable['littleError'].mean():.6f}")

def main():
    """Main execution function"""
    analyzer = QueueDataAnalyzer()
    results = analyzer.generate_comprehensive_report()
    
    if results:
        print("\nAnalysis completed successfully!")
    else:
        print("\nAnalysis completed with warnings.")

if __name__ == "__main__":
    main()