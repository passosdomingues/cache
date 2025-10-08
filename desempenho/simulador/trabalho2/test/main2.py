#!/usr/bin/env python3
"""
Scientific Queueing System Analyzer - Focused Analysis Package
Author: Rafael Passos Domingues
Last Update: 2025-10-08

Scientific analysis focused on meaningful scatter plots, stability analysis,
and proper statistical validation of queueing system behavior.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.optimize import curve_fit
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import os
import glob
import warnings
from datetime import datetime
from tqdm import tqdm

warnings.filterwarnings('ignore')


class ScientificQueueingAnalyzer:
    """
    Scientific analysis class focusing on scatter plots, stability analysis,
    and proper statistical validation of queueing system behavior.
    """

    def __init__(self, results_directory='results', output_directory='scientific_analysis'):
        self.results_directory = results_directory
        self.output_directory = output_directory
        self.data = {}
        self.averaged_data = {}
        self.scenario_stats = {}

        # Scientific color scheme
        self.colors = {
            'rho_0.800': '#1f77b4',
            'rho_0.900': '#ff7f0e',
            'rho_0.950': '#2ca02c',
            'rho_0.999': '#d62728',
            'EN': '#1f77b4',
            'EW': '#ff7f0e',
            'queue1': '#1f77b4',
            'queue2': '#ff7f0e',
            'queue3': '#2ca02c'
        }

        self.create_directories()

    def create_directories(self):
        """Create scientific directory structure."""
        directories = [
            'plots/stability',
            'plots/queues',
            'plots/little_law',
            'plots/clustering',
            'plots/correlation',
            'statistics',
            'models'
        ]

        for directory in directories:
            os.makedirs(os.path.join(self.output_directory, directory), exist_ok=True)

    def load_and_process_data(self):
        """Load data with proper scientific validation."""
        print("Loading and validating simulation data...")

        csv_files = glob.glob(os.path.join(self.results_directory, "*.csv"))

        # Load individual files
        for file_path in tqdm(csv_files, desc="Loading files"):
            filename = os.path.basename(file_path)
            if 'dados_ocupacao' in filename:
                parts = filename.replace('dados_ocupacao_', '').replace('.csv', '').split('_')
                rho_value = float(parts[0])
                seed_value = int(parts[2])

                scenario_key = f"rho_{rho_value:.3f}"
                if scenario_key not in self.data:
                    self.data[scenario_key] = {}

                df = pd.read_csv(file_path)
                df['scenario'] = scenario_key
                df['seed'] = seed_value
                df['rho'] = rho_value

                self.data[scenario_key][seed_value] = df

        # Compute proper averaged data
        print("Computing scientifically validated averages...")
        for scenario, seed_data in self.data.items():
            all_dfs = list(seed_data.values())
            min_length = min(len(df) for df in all_dfs)

            averaged_records = []
            for i in range(min_length):
                record = {
                    'timestamp': all_dfs[0]['timestamp'].iloc[i],
                    'sampleIndex': i
                }

                # Compute robust statistics for each metric
                for col in ['EN', 'EW', 'queueSize1', 'queueSize2', 'queueSize3',
                            'measuredLambda', 'measuredOccupancy', 'littleError']:
                    values = [df[col].iloc[i] for df in all_dfs]
                    record[col] = np.mean(values)
                    record[f'{col}_std'] = np.std(values)
                    record[f'{col}_se'] = stats.sem(values)  # Standard error
                    record[f'{col}_cv'] = np.std(values) / np.mean(values) if np.mean(values) != 0 else 0

                averaged_records.append(record)

            self.averaged_data[scenario] = pd.DataFrame(averaged_records)

            # Compute comprehensive scenario statistics
            self._compute_scenario_statistics(scenario)

        print(f"Loaded {len(self.data)} scenarios with {sum(len(seeds) for seeds in self.data.values())} total seeds")

    def _compute_scenario_statistics(self, scenario):
        """Compute comprehensive scientific statistics."""
        avg_df = self.averaged_data[scenario]
        final_100 = avg_df.iloc[-100:]  # Steady state analysis

        stats_summary = {
            # Central tendency with confidence intervals
            'EN_mean': final_100['EN'].mean(),
            'EN_median': final_100['EN'].median(),
            'EW_mean': final_100['EW'].mean(),
            'EW_median': final_100['EW'].median(),

            # Variability metrics
            'EN_std': final_100['EN'].std(),
            'EW_std': final_100['EW'].std(),
            'EN_cv': final_100['EN'].std() / final_100['EN'].mean(),
            'EW_cv': final_100['EW'].std() / final_100['EW'].mean(),

            # Queue statistics
            'queue1_mean': final_100['queueSize1'].mean(),
            'queue2_mean': final_100['queueSize2'].mean(),
            'queue3_mean': final_100['queueSize3'].mean(),

            # System metrics
            'lambda_mean': final_100['measuredLambda'].mean(),
            'occupancy_mean': final_100['measuredOccupancy'].mean(),
            'little_error_mean': final_100['littleError'].mean(),
            'little_error_std': final_100['littleError'].std(),

            # Data quality indicators
            'num_samples': len(avg_df),
            'steady_state_samples': len(final_100),
            'data_quality_score': self._compute_data_quality(avg_df)
        }

        self.scenario_stats[scenario] = stats_summary

    def _compute_data_quality(self, df):
        """Compute data quality score based on stability and consistency."""
        # Check convergence
        final_100 = df.iloc[-100:]
        initial_100 = df.iloc[:100]

        # Convergence metric (should be small)
        en_convergence = abs(final_100['EN'].mean() - initial_100['EN'].mean()) / initial_100['EN'].mean()
        ew_convergence = abs(final_100['EW'].mean() - initial_100['EW'].mean()) / initial_100['EW'].mean()

        # Stability metric (coefficient of variation in steady state)
        en_stability = final_100['EN'].std() / final_100['EN'].mean()
        ew_stability = final_100['EW'].std() / final_100['EW'].mean()

        # Little's Law adherence
        little_error = abs(final_100['littleError'].mean())

        # Composite quality score (lower is better)
        quality_score = (en_convergence + ew_convergence + en_stability + ew_stability + little_error) / 5

        return quality_score

    def generate_stability_analysis(self):
        """Generate comprehensive stability analysis plots."""
        print("Generating stability analysis plots...")

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Comprehensive Stability Analysis', fontsize=16, fontweight='bold')

        # 1. Little's Law Error Comparison
        for scenario, avg_df in self.averaged_data.items():
            color = self.colors.get(scenario, '#333333')
            axes[0, 0].plot(avg_df['timestamp'], avg_df['littleError'],
                            label=f'ρ = {scenario.split("_")[1]}', color=color, linewidth=2)

        axes[0, 0].axhline(y=0, color='black', linestyle='--', alpha=0.5)
        axes[0, 0].set_title("Little's Law Error Comparison")
        axes[0, 0].set_ylabel('Error (E[N] - λ·E[W])')
        axes[0, 0].set_xlabel('Time (seconds)')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)

        # 2. Coefficient of Variation for E[N]
        for scenario, avg_df in self.averaged_data.items():
            color = self.colors.get(scenario, '#333333')
            # Use rolling window for CV calculation
            window_size = min(50, len(avg_df) // 10)
            cv = (avg_df['EN'].rolling(window=window_size).std() /
                  avg_df['EN'].rolling(window=window_size).mean())
            axes[0, 1].plot(avg_df['timestamp'], cv,
                            label=f'ρ = {scenario.split("_")[1]}', color=color, linewidth=2)

        axes[0, 1].set_title('Coefficient of Variation (CV) for E[N]')
        axes[0, 1].set_ylabel('CV = σ/μ')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)

        # 3. Convergence to Steady State
        for scenario, avg_df in self.averaged_data.items():
            color = self.colors.get(scenario, '#333333')
            final_en = avg_df['EN'].iloc[-1]
            convergence = np.abs(avg_df['EN'] - final_en) / final_en
            axes[1, 1].plot(avg_df['timestamp'], convergence,
                            label=f'ρ = {scenario.split("_")[1]}', color=color, linewidth=2)

        axes[1, 1].set_title('Convergence to Steady State')
        axes[1, 1].set_ylabel('|E[N](t) - E[N](final)| / E[N](final)')
        axes[1, 1].set_xlabel('Time (seconds)')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].set_yscale('log')

        # 4. Queue Size Dynamics
        for scenario, avg_df in self.averaged_data.items():
            color = self.colors.get(scenario, '#333333')
            total_queues = avg_df['queueSize1'] + avg_df['queueSize2'] + avg_df['queueSize3']
            axes[1, 0].plot(avg_df['timestamp'], total_queues,
                            label=f'ρ = {scenario.split("_")[1]}', color=color, linewidth=2)

        axes[1, 0].set_title('Total System Queue Size Dynamics')
        axes[1, 0].set_ylabel('Total Queue Size (Q1 + Q2 + Q3)')
        axes[1, 0].set_xlabel('Time (seconds)')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_directory, 'plots/stability',
                                 'comprehensive_stability_analysis.png'),
                    dpi=300, bbox_inches='tight')
        plt.close()

    def generate_queue_dynamics_plots(self):
        """Generate detailed queue dynamics plots."""
        print("Generating queue dynamics plots...")

        for scenario, avg_df in self.averaged_data.items():
            # Create individual plots for each scenario
            self._plot_individual_queue_dynamics(scenario, avg_df)

        # Create comparative plots
        self._plot_comparative_queue_dynamics()

    def _plot_individual_queue_dynamics(self, scenario, avg_df):
        """Plot individual queue dynamics for each scenario."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        # Queue sizes over time
        ax1.plot(avg_df['timestamp'], avg_df['queueSize1'],
                 color=self.colors['queue1'], label='Queue 1', linewidth=1.5, alpha=0.8)
        ax1.plot(avg_df['timestamp'], avg_df['queueSize2'],
                 color=self.colors['queue2'], label='Queue 2', linewidth=1.5, alpha=0.8)
        ax1.plot(avg_df['timestamp'], avg_df['queueSize3'],
                 color=self.colors['queue3'], label='Queue 3', linewidth=1.5, alpha=0.8)

        ax1.set_xlabel('Time (seconds)')
        ax1.set_ylabel('Queue Size')
        ax1.set_title(f'{scenario} - Individual Queue Sizes vs Time')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # EN and EW over time
        ax2.plot(avg_df['timestamp'], avg_df['EN'],
                 color=self.colors['EN'], label='E[N]', linewidth=2)
        ax2.plot(avg_df['timestamp'], avg_df['EW'],
                 color=self.colors['EW'], label='E[W]', linewidth=2)

        ax2.set_xlabel('Time (seconds)')
        ax2.set_ylabel('E[N] / E[W]')
        ax2.set_title(f'{scenario} - E[N] and E[W] vs Time')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_directory, 'plots/queues',
                                 f'{scenario}_queue_dynamics.png'),
                    dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_comparative_queue_dynamics(self):
        """Plot comparative queue dynamics across scenarios."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        metrics = [
            ('EN', 'E[N]'),
            ('EW', 'E[W]'),
            ('queueSize1', 'Queue 1'),
            ('queueSize2', 'Queue 2')
        ]

        for idx, (metric, title) in enumerate(metrics):
            ax = axes[idx // 2, idx % 2]
            for scenario, avg_df in self.averaged_data.items():
                color = self.colors.get(scenario, '#333333')
                ax.plot(avg_df['timestamp'], avg_df[metric],
                        label=f'ρ = {scenario.split("_")[1]}', color=color, linewidth=2)

            ax.set_xlabel('Time (seconds)')
            ax.set_ylabel(title)
            ax.set_title(f'{title} Comparison')
            ax.legend()
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_directory, 'plots/queues',
                                 'comparative_queue_dynamics.png'),
                    dpi=300, bbox_inches='tight')
        plt.close()

    def generate_little_law_analysis(self):
        """Generate comprehensive Little's Law validation plots."""
        print("Generating Little's Law analysis...")

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        # 1. EN vs EW scatter with theoretical line
        for scenario, avg_df in self.averaged_data.items():
            color = self.colors.get(scenario, '#333333')
            scatter = axes[0, 0].scatter(avg_df['EN'], avg_df['EW'],
                                         c=avg_df['timestamp'], cmap='viridis',
                                         alpha=0.6, s=20, label=f'ρ = {scenario.split("_")[1]}')

        # Add theoretical line (EN = lambda * EW)
        max_val = max([avg_df['EN'].max() for avg_df in self.averaged_data.values()])
        theoretical_lambda = 1.0  # Assuming mu = 1.0
        x_vals = np.linspace(0, max_val, 100)
        y_vals = x_vals / theoretical_lambda
        axes[0, 0].plot(x_vals, y_vals, 'r--', alpha=0.7, linewidth=2, label='EN = λ·EW')

        axes[0, 0].set_xlabel('E[N]')
        axes[0, 0].set_ylabel('E[W]')
        axes[0, 0].set_title('E[N] vs E[W] with Theoretical Relationship')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)

        # 2. Little's Law error distribution
        little_errors = []
        scenario_labels = []
        for scenario, avg_df in self.averaged_data.items():
            errors = avg_df['littleError'].values
            little_errors.extend(errors)
            scenario_labels.extend([scenario] * len(errors))

        error_df = pd.DataFrame({
            'LittleError': little_errors,
            'Scenario': scenario_labels
        })

        sns.boxplot(data=error_df, x='Scenario', y='LittleError', ax=axes[0, 1])
        axes[0, 1].axhline(y=0, color='red', linestyle='--', alpha=0.7)
        axes[0, 1].set_title("Little's Law Error Distribution")
        axes[0, 1].set_ylabel('Error (E[N] - λ·E[W])')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].grid(True, alpha=0.3)

        # 3. EN vs measuredLambda
        for scenario, avg_df in self.averaged_data.items():
            color = self.colors.get(scenario, '#333333')
            axes[1, 0].scatter(avg_df['measuredLambda'], avg_df['EN'],
                               color=color, alpha=0.6, s=20, label=f'ρ = {scenario.split("_")[1]}')

        axes[1, 0].set_xlabel('Measured Lambda (λ)')
        axes[1, 0].set_ylabel('E[N]')
        axes[1, 0].set_title('E[N] vs Measured Lambda')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)

        # 4. EW vs measuredOccupancy
        for scenario, avg_df in self.averaged_data.items():
            color = self.colors.get(scenario, '#333333')
            axes[1, 1].scatter(avg_df['measuredOccupancy'], avg_df['EW'],
                               color=color, alpha=0.6, s=20, label=f'ρ = {scenario.split("_")[1]}')

        axes[1, 1].set_xlabel('Measured Occupancy (ρ)')
        axes[1, 1].set_ylabel('E[W]')
        axes[1, 1].set_title('E[W] vs Measured Occupancy')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_directory, 'plots/little_law',
                                 'comprehensive_little_law_analysis.png'),
                    dpi=300, bbox_inches='tight')
        plt.close()

    def perform_clustering_analysis(self):
        """Perform K-means clustering on system features."""
        print("Performing clustering analysis...")

        # Prepare feature matrix
        features_list = []
        scenario_labels = []

        for scenario, avg_df in self.averaged_data.items():
            # Use steady-state characteristics
            steady_features = avg_df.iloc[-100:][[
                'EN', 'EW', 'queueSize1', 'queueSize2', 'queueSize3',
                'measuredLambda', 'measuredOccupancy', 'littleError'
            ]].mean().values

            features_list.append(steady_features)
            scenario_labels.append(scenario)

        feature_matrix = np.array(features_list)
        feature_names = ['EN', 'EW', 'queueSize1', 'queueSize2', 'queueSize3',
                         'measuredLambda', 'measuredOccupancy', 'littleError']

        # Standardize features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(feature_matrix)

        # Determine optimal number of clusters
        wcss = []
        k_range = range(1, min(6, len(feature_matrix) + 1))

        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(features_scaled)
            wcss.append(kmeans.inertia_)

        # Use elbow method to find optimal k
        optimal_k = 2  # Default
        if len(wcss) > 1:
            # Find the elbow point
            differences = [wcss[i - 1] - wcss[i] for i in range(1, len(wcss))]
            if differences:
                optimal_k = np.argmax(differences) + 2  # +2 because we start from k=2

        # Perform clustering with optimal k
        kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(features_scaled)

        # Store results
        self.clustering_results = {
            'kmeans': kmeans,
            'labels': cluster_labels,
            'optimal_k': optimal_k,
            'feature_names': feature_names,
            'scenario_labels': scenario_labels,
            'features_scaled': features_scaled
        }

        self._plot_clustering_results()

    def _plot_clustering_results(self):
        """Plot clustering analysis results."""
        cr = self.clustering_results

        # PCA for visualization
        pca = PCA(n_components=2)
        principal_components = pca.fit_transform(cr['features_scaled'])

        plt.figure(figsize=(10, 8))
        scatter = plt.scatter(principal_components[:, 0], principal_components[:, 1],
                              c=cr['labels'], cmap='Set1', s=100, alpha=0.7)

        # Add scenario labels
        for i, scenario in enumerate(cr['scenario_labels']):
            plt.annotate(scenario.split('_')[1],
                         (principal_components[i, 0], principal_components[i, 1]),
                         xytext=(5, 5), textcoords='offset points',
                         fontsize=8, fontweight='bold')

        plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)')
        plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)')
        plt.title(f'K-means Clustering (k={cr["optimal_k"]}) - Scenario Behavior Patterns')
        plt.colorbar(scatter, label='Cluster')
        plt.grid(True, alpha=0.3)

        plt.savefig(os.path.join(self.output_directory, 'plots/clustering',
                                 'scenario_clustering.png'),
                    dpi=300, bbox_inches='tight')
        plt.close()

    def generate_correlation_analysis(self):
        """Generate correlation matrices and relationship plots."""
        print("Generating correlation analysis...")

        # Combined correlation matrix
        all_data = []
        for scenario, avg_df in self.averaged_data.items():
            scenario_data = avg_df.iloc[-100:][[  # Steady state
                'EN', 'EW', 'queueSize1', 'queueSize2', 'queueSize3',
                'measuredLambda', 'measuredOccupancy', 'littleError'
            ]].copy()
            scenario_data['scenario'] = scenario
            all_data.append(scenario_data)

        combined_df = pd.concat(all_data, ignore_index=True)

        # Correlation matrix
        numeric_cols = combined_df.select_dtypes(include=[np.number]).columns
        corr_matrix = combined_df[numeric_cols].corr()

        plt.figure(figsize=(10, 8))
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm',
                    center=0, square=True, fmt='.2f', cbar_kws={"shrink": .8})
        plt.title('Correlation Matrix - All Scenarios (Steady State)')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_directory, 'plots/correlation',
                                 'correlation_matrix.png'),
                    dpi=300, bbox_inches='tight')
        plt.close()

        # Pairplot for key relationships
        key_features = ['EN', 'EW', 'measuredLambda', 'measuredOccupancy', 'littleError', 'scenario']
        pairplot_df = combined_df[key_features]

        plt.figure(figsize=(12, 10))
        sns.pairplot(pairplot_df, hue='scenario', diag_kind='hist',
                     palette=self.colors, plot_kws={'alpha': 0.6})
        plt.suptitle('Feature Relationships Across Scenarios', y=1.02)
        plt.savefig(os.path.join(self.output_directory, 'plots/correlation',
                                 'feature_pairplot.png'),
                    dpi=300, bbox_inches='tight')
        plt.close()

    def generate_summary_statistics(self):
        """Generate comprehensive summary statistics."""
        print("Generating summary statistics...")

        # Create summary table
        summary_data = []
        for scenario, stats in self.scenario_stats.items():
            summary_data.append({
                'Scenario': scenario,
                'ρ (theoretical)': float(scenario.split('_')[1]),
                'E[N] Mean': stats['EN_mean'],
                'E[N] Std': stats['EN_std'],
                'E[W] Mean': stats['EW_mean'],
                'E[W] Std': stats['EW_std'],
                'Little Error Mean': stats['little_error_mean'],
                'Little Error Std': stats['little_error_std'],
                'Queue 1 Mean': stats['queue1_mean'],
                'Queue 2 Mean': stats['queue2_mean'],
                'Queue 3 Mean': stats['queue3_mean'],
                'Lambda Mean': stats['lambda_mean'],
                'Occupancy Mean': stats['occupancy_mean'],
                'Data Quality Score': stats['data_quality_score']
            })

        summary_df = pd.DataFrame(summary_data)

        # Save to CSV
        summary_df.to_csv(os.path.join(self.output_directory, 'statistics',
                                       'summary_statistics.csv'), index=False)

        # Create visual summary
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        # E[N] by scenario
        scenarios = [s.split('_')[1] for s in summary_df['Scenario']]
        axes[0, 0].bar(scenarios, summary_df['E[N] Mean'],
                       color=[self.colors[f'rho_{s}'] for s in scenarios], alpha=0.7)
        axes[0, 0].set_title('E[N] by Occupancy Scenario')
        axes[0, 0].set_ylabel('E[N]')
        axes[0, 0].tick_params(axis='x', rotation=45)

        # E[W] by scenario
        axes[0, 1].bar(scenarios, summary_df['E[W] Mean'],
                       color=[self.colors[f'rho_{s}'] for s in scenarios], alpha=0.7)
        axes[0, 1].set_title('E[W] by Occupancy Scenario')
        axes[0, 1].set_ylabel('E[W]')
        axes[0, 1].tick_params(axis='x', rotation=45)

        # Little's Law error
        axes[1, 0].bar(scenarios, summary_df['Little Error Mean'],
                       color=[self.colors[f'rho_{s}'] for s in scenarios], alpha=0.7)
        axes[1, 0].axhline(y=0, color='red', linestyle='--', alpha=0.7)
        axes[1, 0].set_title("Little's Law Error by Scenario")
        axes[1, 0].set_ylabel('Error (E[N] - λ·E[W])')
        axes[1, 0].tick_params(axis='x', rotation=45)

        # Data quality scores
        axes[1, 1].bar(scenarios, summary_df['Data Quality Score'],
                       color=[self.colors[f'rho_{s}'] for s in scenarios], alpha=0.7)
        axes[1, 1].set_title('Data Quality Assessment')
        axes[1, 1].set_ylabel('Quality Score (lower is better)')
        axes[1, 1].tick_params(axis='x', rotation=45)

        for ax in axes.flat:
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_directory, 'statistics',
                                 'summary_visualization.png'),
                    dpi=300, bbox_inches='tight')
        plt.close()

        return summary_df

    def run_complete_analysis(self):
        """Execute complete scientific analysis pipeline."""
        print("Starting scientific analysis pipeline...")
        print("=" * 60)

        start_time = datetime.now()

        try:
            self.load_and_process_data()
            self.generate_stability_analysis()
            self.generate_queue_dynamics_plots()
            self.generate_little_law_analysis()
            self.perform_clustering_analysis()
            self.generate_correlation_analysis()
            summary_df = self.generate_summary_statistics()

            end_time = datetime.now()
            duration = end_time - start_time

            print("=" * 60)
            print("Scientific analysis completed successfully!")
            print(f"Total execution time: {duration}")
            print(f"Results saved to: {self.output_directory}")
            print("\nGenerated analysis:")
            print("✓ Stability analysis with CV and convergence")
            print("✓ Queue dynamics for individual scenarios")
            print("✓ Little's Law validation with scatter plots")
            print("✓ K-means clustering of scenario behavior")
            print("✓ Correlation matrices and pairplots")
            print("✓ Comprehensive summary statistics")
            print(f"✓ Data quality assessment completed")

            # Print key findings
            print("\nKey Scientific Findings:")
            for scenario, stats in self.scenario_stats.items():
                ρ = scenario.split('_')[1]
                print(f"ρ = {ρ}: E[N] = {stats['EN_mean']:.3f} ± {stats['EN_std']:.3f}, "
                      f"Little Error = {stats['little_error_mean']:.6f}")

        except Exception as e:
            print(f"Error during analysis: {str(e)}")
            import traceback
            traceback.print_exc()


def main():
    """Main execution function."""
    analyzer = ScientificQueueingAnalyzer()
    analyzer.run_complete_analysis()


if __name__ == "__main__":
    main()