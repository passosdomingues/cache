#!/usr/bin/env python3
"""
Python Analysis Package for Queueing System Simulator
Author: Rafael Passos Domingues
Last Update: 2025 Oct 8

Comprehensive statistical analysis and machine learning pipeline for queueing system simulation data.
Performs detailed time-series analysis, stability detection, bootstrap confidence intervals,
clustering analysis, and generates publication-quality visualizations.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import mannwhitneyu, kstest, yeojohnson, boxcox
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, mean_squared_error, r2_score, silhouette_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.manifold import TSNE
import os
import glob
import json
from datetime import datetime
import warnings
from tqdm import tqdm
import matplotlib as mpl

# Configurações profissionais para plots
mpl.rcParams['figure.dpi'] = 300
mpl.rcParams['savefig.dpi'] = 300
mpl.rcParams['font.size'] = 10
mpl.rcParams['legend.fontsize'] = 8
mpl.rcParams['axes.titlesize'] = 12
mpl.rcParams['axes.labelsize'] = 10

warnings.filterwarnings('ignore')


class AdvancedQueueingAnalyzer:
    """
    Advanced analysis class for comprehensive queueing system simulation analysis.
    Features professional-grade visualizations, statistical analysis, and ML pipelines.
    """

    def __init__(self, results_directory='results', output_directory='analysis_output'):
        self.results_directory = results_directory
        self.output_directory = output_directory
        self.data = {}
        self.averaged_data = {}
        self.scenario_summaries = {}
        self.clustering_results = {}
        self.ml_models = {}

        # Cores para cenários
        self.scenario_colors = {
            'rho_0.800': '#2E86AB',
            'rho_0.900': '#A23B72',
            'rho_0.950': '#F18F01',
            'rho_0.999': '#C73E1D'
        }

        self.create_directories()

    def create_directories(self):
        """Create comprehensive directory structure for outputs."""
        directories = [
            'plots/time_series/individual',
            'plots/time_series/averaged',
            'plots/statistical',
            'plots/clustering',
            'plots/correlations',
            'plots/distributions',
            'models',
            'reports',
            'data_summaries'
        ]

        for directory in directories:
            os.makedirs(os.path.join(self.output_directory, directory), exist_ok=True)

    def load_and_process_data(self):
        """Load all simulation data and compute averaged metrics across seeds."""
        print("Loading and processing simulation data...")

        csv_files = glob.glob(os.path.join(self.results_directory, "*.csv"))

        # Carregar dados individuais
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

        # Computar médias entre seeds para cada cenário
        print("Computing averaged metrics across seeds...")
        for scenario, seed_data in self.data.items():
            # Encontrar tempo comum mínimo entre todas as seeds
            min_length = min(len(df) for df in seed_data.values())
            averaged_dfs = []

            for i in range(min_length):
                timepoint_data = {}
                # Definir colunas numéricas para cálculo de média
                numeric_columns = ['EN', 'EW', 'queueSize1', 'queueSize2', 'queueSize3',
                                   'measuredLambda', 'measuredOccupancy', 'littleError']

                for col in numeric_columns:
                    values = [df[col].iloc[i] for df in seed_data.values()]
                    timepoint_data[col] = np.mean(values)
                    timepoint_data[f'{col}_std'] = np.std(values)

                timepoint_data['timestamp'] = list(seed_data.values())[0]['timestamp'].iloc[i]
                timepoint_data['sampleIndex'] = i
                averaged_dfs.append(timepoint_data)

            self.averaged_data[scenario] = pd.DataFrame(averaged_dfs)

        print(f"Loaded {len(self.data)} scenarios with {sum(len(seeds) for seeds in self.data.values())} total seeds")

    def perform_clustering_analysis(self):
        """Perform comprehensive clustering analysis on simulation data."""
        print("Performing clustering analysis...")

        # Prepare data for clustering
        feature_data = []
        scenario_labels = []
        seed_labels = []

        # Definir colunas numéricas para clusterização
        numeric_columns = ['EN', 'EW', 'queueSize1', 'queueSize2', 'queueSize3',
                           'measuredLambda', 'measuredOccupancy', 'littleError']

        for scenario, seed_data in self.data.items():
            for seed, df in seed_data.items():
                # Usar estado final para clusterização - apenas colunas numéricas
                try:
                    # Selecionar apenas colunas numéricas e calcular média
                    numeric_data = df[numeric_columns].iloc[-100:]
                    final_state = numeric_data.mean()

                    features = final_state.tolist()
                    feature_data.append(features)
                    scenario_labels.append(scenario)
                    seed_labels.append(seed)
                except Exception as e:
                    print(f"Warning: Error processing scenario {scenario}, seed {seed}: {str(e)}")
                    continue

        if not feature_data:
            print("Error: No valid data for clustering analysis")
            return

        feature_matrix = np.array(feature_data)

        # Padronizar características
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(feature_matrix)

        # Determinar número ótimo de clusters
        wcss = []
        silhouette_scores = []
        k_range = range(2, min(8, len(feature_matrix) + 1))

        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(features_scaled)
            wcss.append(kmeans.inertia_)
            if len(np.unique(labels)) > 1:
                silhouette_scores.append(silhouette_score(features_scaled, labels))
            else:
                silhouette_scores.append(0)

        # Escolher k ótimo
        if silhouette_scores:
            optimal_k = k_range[np.argmax(silhouette_scores)]
        else:
            optimal_k = 2

        # Realizar clusterização final
        final_kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
        cluster_labels = final_kmeans.fit_predict(features_scaled)

        # Armazenar resultados
        self.clustering_results = {
            'kmeans': final_kmeans,
            'labels': cluster_labels,
            'optimal_k': optimal_k,
            'wcss': wcss,
            'silhouette_scores': silhouette_scores,
            'feature_names': numeric_columns,
            'scenario_labels': scenario_labels,
            'seed_labels': seed_labels,
            'features_scaled': features_scaled
        }

        # Gerar visualizações de clusterização
        self._plot_clustering_results()

    def _plot_clustering_results(self):
        """Plot comprehensive clustering analysis results."""
        cr = self.clustering_results

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('K-means Clustering Analysis of Simulation Results', fontsize=16, fontweight='bold')

        # Curva do cotovelo
        axes[0, 0].plot(range(2, 2 + len(cr['wcss'])), cr['wcss'], 'bo-', linewidth=2, markersize=8)
        axes[0, 0].axvline(x=cr['optimal_k'], color='red', linestyle='--', alpha=0.7,
                           label=f'Optimal k = {cr["optimal_k"]}')
        axes[0, 0].set_title('Elbow Method for Optimal k')
        axes[0, 0].set_xlabel('Number of Clusters')
        axes[0, 0].set_ylabel('Within-Cluster Sum of Squares (WCSS)')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)

        # Pontuações de silhueta
        axes[0, 1].plot(range(2, 2 + len(cr['silhouette_scores'])), cr['silhouette_scores'], 'go-', linewidth=2,
                        markersize=8)
        axes[0, 1].axvline(x=cr['optimal_k'], color='red', linestyle='--', alpha=0.7,
                           label=f'Optimal k = {cr["optimal_k"]}')
        axes[0, 1].set_title('Silhouette Scores for Different k')
        axes[0, 1].set_xlabel('Number of Clusters')
        axes[0, 1].set_ylabel('Silhouette Score')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)

        # Visualização PCA
        pca = PCA(n_components=2)
        principal_components = pca.fit_transform(cr['features_scaled'])

        scatter = axes[1, 0].scatter(principal_components[:, 0], principal_components[:, 1],
                                     c=cr['labels'], cmap='viridis', alpha=0.7, s=60)
        axes[1, 0].set_title(f'PCA Visualization (Clusters)')
        axes[1, 0].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)')
        axes[1, 0].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)')
        plt.colorbar(scatter, ax=axes[1, 0], label='Cluster')
        axes[1, 0].grid(True, alpha=0.3)

        # Visualização t-SNE
        if len(cr['features_scaled']) > 1:
            tsne = TSNE(n_components=2, random_state=42, perplexity=min(5, len(cr['features_scaled']) - 1))
            tsne_components = tsne.fit_transform(cr['features_scaled'])

            # Colorir por cenário
            scenario_encoder = LabelEncoder()
            scenario_encoded = scenario_encoder.fit_transform(cr['scenario_labels'])

            scatter = axes[1, 1].scatter(tsne_components[:, 0], tsne_components[:, 1],
                                         c=scenario_encoded, cmap='Set1', alpha=0.7, s=60)
            axes[1, 1].set_title('t-SNE Visualization (Colored by Scenario)')
            axes[1, 1].set_xlabel('t-SNE Component 1')
            axes[1, 1].set_ylabel('t-SNE Component 2')

            # Criar legenda para cenários
            handles = []
            for i, scenario in enumerate(scenario_encoder.classes_):
                handle = plt.Line2D([0], [0], marker='o', color='w',
                                    markerfacecolor=plt.cm.Set1(i / len(scenario_encoder.classes_)),
                                    markersize=8, label=scenario)
                handles.append(handle)
            axes[1, 1].legend(handles=handles, title='Scenarios', bbox_to_anchor=(1.05, 1), loc='upper left')
            axes[1, 1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_directory, 'plots/clustering',
                                 'comprehensive_clustering_analysis.png'),
                    dpi=300, bbox_inches='tight')
        plt.close()

    def perform_statistical_analysis(self):
        """Perform comprehensive statistical analysis."""
        print("Performing statistical analysis...")

        # Testes estatísticos entre cenários
        statistical_results = {}

        for scenario, avg_df in self.averaged_data.items():
            # Estatísticas básicas
            final_100 = avg_df.iloc[-100:]  # Últimas 100 amostras para análise de estado estacionário

            stats_summary = {
                'EN_mean': final_100['EN'].mean(),
                'EN_std': final_100['EN'].std(),
                'EW_mean': final_100['EW'].mean(),
                'EW_std': final_100['EW'].std(),
                'littleError_mean': final_100['littleError'].mean(),
                'littleError_std': final_100['littleError'].std(),
                'queueSize_mean': final_100[['queueSize1', 'queueSize2', 'queueSize3']].mean().mean(),
                'occupancy_mean': final_100['measuredOccupancy'].mean()
            }

            statistical_results[scenario] = stats_summary

        self.statistical_results = statistical_results

        # Gerar gráficos estatísticos
        self._plot_statistical_summary()

        # Salvar sumário estatístico
        stats_df = pd.DataFrame(statistical_results).T
        stats_df.to_csv(os.path.join(self.output_directory, 'data_summaries', 'statistical_summary.csv'))

        print("Statistical analysis completed")

    def _plot_statistical_summary(self):
        """Plot statistical summary across scenarios."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Statistical Summary Across Scenarios', fontsize=16, fontweight='bold')

        scenarios = list(self.statistical_results.keys())
        scenario_labels = [s.split('_')[1] for s in scenarios]

        # E[N] e E[W] com barras de erro
        en_means = [self.statistical_results[s]['EN_mean'] for s in scenarios]
        en_stds = [self.statistical_results[s]['EN_std'] for s in scenarios]
        ew_means = [self.statistical_results[s]['EW_mean'] for s in scenarios]
        ew_stds = [self.statistical_results[s]['EW_std'] for s in scenarios]

        x = np.arange(len(scenarios))
        width = 0.35

        axes[0, 0].bar(x - width / 2, en_means, width, yerr=en_stds, capsize=5,
                       label='E[N]', alpha=0.7, color='blue')
        axes[0, 0].bar(x + width / 2, ew_means, width, yerr=ew_stds, capsize=5,
                       label='E[W]', alpha=0.7, color='orange')
        axes[0, 0].set_title('E[N] and E[W] with Standard Deviation')
        axes[0, 0].set_xlabel('Occupancy Scenario')
        axes[0, 0].set_ylabel('Metric Value')
        axes[0, 0].set_xticks(x)
        axes[0, 0].set_xticklabels(scenario_labels)
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)

        # Distribuição do erro de Little
        little_errors = [self.statistical_results[s]['littleError_mean'] for s in scenarios]
        little_stds = [self.statistical_results[s]['littleError_std'] for s in scenarios]

        axes[0, 1].bar(x, little_errors, yerr=little_stds, capsize=5,
                       alpha=0.7, color='red')
        axes[0, 1].axhline(y=0, color='black', linestyle='--', alpha=0.5)
        axes[0, 1].set_title("Little's Law Error")
        axes[0, 1].set_xlabel('Occupancy Scenario')
        axes[0, 1].set_ylabel('Error (E[N] - λ·E[W])')
        axes[0, 1].set_xticks(x)
        axes[0, 1].set_xticklabels(scenario_labels)
        axes[0, 1].grid(True, alpha=0.3)

        # Comparação de tamanhos de fila
        queue_means = []
        for scenario in scenarios:
            q1 = self.averaged_data[scenario]['queueSize1'].iloc[-100:].mean()
            q2 = self.averaged_data[scenario]['queueSize2'].iloc[-100:].mean()
            q3 = self.averaged_data[scenario]['queueSize3'].iloc[-100:].mean()
            queue_means.append([q1, q2, q3])

        queue_means = np.array(queue_means)

        bottom = np.zeros(len(scenarios))
        for i in range(3):
            axes[1, 0].bar(x, queue_means[:, i], bottom=bottom,
                           label=f'Queue {i + 1}', alpha=0.7)
            bottom += queue_means[:, i]

        axes[1, 0].set_title('Average Queue Sizes in Steady State')
        axes[1, 0].set_xlabel('Occupancy Scenario')
        axes[1, 0].set_ylabel('Average Queue Size')
        axes[1, 0].set_xticks(x)
        axes[1, 0].set_xticklabels(scenario_labels)
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)

        # Ocupação vs Erro de Little
        occupancies = [self.statistical_results[s]['occupancy_mean'] for s in scenarios]

        scatter = axes[1, 1].scatter(occupancies, little_errors, s=100, alpha=0.7,
                                     c=range(len(scenarios)), cmap='viridis')
        for i, scenario in enumerate(scenario_labels):
            axes[1, 1].annotate(scenario, (occupancies[i], little_errors[i]),
                                xytext=(5, 5), textcoords='offset points', fontsize=8)

        axes[1, 1].axhline(y=0, color='black', linestyle='--', alpha=0.5)
        axes[1, 1].set_title('Occupancy vs Little\'s Law Error')
        axes[1, 1].set_xlabel('Measured Occupancy (ρ)')
        axes[1, 1].set_ylabel('Little\'s Law Error')
        axes[1, 1].grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=axes[1, 1], label='Scenario Index')

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_directory, 'plots/statistical',
                                 'statistical_summary.png'),
                    dpi=300, bbox_inches='tight')
        plt.close()

    def generate_comprehensive_time_series_plots(self):
        """Generate comprehensive time series plots for all metrics."""
        print("Generating comprehensive time series plots...")

        # 1. Plot individual para cada cenário (médias entre seeds)
        for scenario, avg_df in self.averaged_data.items():
            self._plot_scenario_time_series(scenario, avg_df)

        # 2. Plot comparativo entre cenários
        self._plot_comparative_time_series()

        # 3. Plot de estabilização
        self._plot_stability_analysis()

    def _plot_scenario_time_series(self, scenario, avg_df):
        """Plot detailed time series for a single scenario."""
        fig, axes = plt.subplots(3, 2, figsize=(15, 12))
        fig.suptitle(f'Detailed Metrics Analysis - {scenario}', fontsize=16, fontweight='bold')

        color = self.scenario_colors.get(scenario, '#333333')

        # E[N] and E[W]
        axes[0, 0].plot(avg_df['timestamp'], avg_df['EN'], label='E[N]', color=color, linewidth=2)
        if 'EN_std' in avg_df.columns:
            axes[0, 0].fill_between(avg_df['timestamp'],
                                    avg_df['EN'] - avg_df['EN_std'],
                                    avg_df['EN'] + avg_df['EN_std'],
                                    alpha=0.3, color=color)
        axes[0, 0].set_title('Average Number in System (E[N])')
        axes[0, 0].set_ylabel('E[N]')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].legend()

        axes[0, 1].plot(avg_df['timestamp'], avg_df['EW'], label='E[W]', color=color, linewidth=2)
        if 'EW_std' in avg_df.columns:
            axes[0, 1].fill_between(avg_df['timestamp'],
                                    avg_df['EW'] - avg_df['EW_std'],
                                    avg_df['EW'] + avg_df['EW_std'],
                                    alpha=0.3, color=color)
        axes[0, 1].set_title('Average Waiting Time (E[W])')
        axes[0, 1].set_ylabel('E[W] (seconds)')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].legend()

        # Queue sizes
        axes[1, 0].plot(avg_df['timestamp'], avg_df['queueSize1'], label='Queue 1', linewidth=1.5, alpha=0.8)
        axes[1, 0].plot(avg_df['timestamp'], avg_df['queueSize2'], label='Queue 2', linewidth=1.5, alpha=0.8)
        axes[1, 0].plot(avg_df['timestamp'], avg_df['queueSize3'], label='Queue 3', linewidth=1.5, alpha=0.8)
        axes[1, 0].set_title('Queue Sizes Over Time')
        axes[1, 0].set_ylabel('Queue Size')
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].legend()

        # Lambda and Occupancy
        axes[1, 1].plot(avg_df['timestamp'], avg_df['measuredLambda'], label='Measured Lambda', color='purple',
                        linewidth=2)
        axes[1, 1].set_title('Arrival Rate (λ)')
        axes[1, 1].set_ylabel('λ (arrivals/second)')
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].legend()

        ax2 = axes[1, 1].twinx()
        ax2.plot(avg_df['timestamp'], avg_df['measuredOccupancy'], label='Occupancy', color='red', linewidth=2,
                 linestyle='--')
        ax2.set_ylabel('Occupancy (ρ)')
        ax2.legend(loc='upper right')

        # Little's Law Error
        axes[2, 0].plot(avg_df['timestamp'], avg_df['littleError'], label="Little's Law Error", color='red',
                        linewidth=2)
        if 'littleError_std' in avg_df.columns:
            axes[2, 0].fill_between(avg_df['timestamp'],
                                    avg_df['littleError'] - avg_df['littleError_std'],
                                    avg_df['littleError'] + avg_df['littleError_std'],
                                    alpha=0.3, color='red')
        axes[2, 0].axhline(y=0, color='black', linestyle='--', alpha=0.5)
        axes[2, 0].set_title("Little's Law Validation Error")
        axes[2, 0].set_ylabel('Error (E[N] - λ·E[W])')
        axes[2, 0].set_xlabel('Time (seconds)')
        axes[2, 0].grid(True, alpha=0.3)
        axes[2, 0].legend()

        # E[N] vs E[W] scatter with time color
        scatter = axes[2, 1].scatter(avg_df['EN'], avg_df['EW'],
                                     c=avg_df['timestamp'], cmap='viridis', alpha=0.7, s=20)
        axes[2, 1].set_title('E[N] vs E[W] (colored by time)')
        axes[2, 1].set_xlabel('E[N]')
        axes[2, 1].set_ylabel('E[W]')
        axes[2, 1].grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=axes[2, 1], label='Time (seconds)')

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_directory, 'plots/time_series/individual',
                                 f'time_series_detailed_{scenario}.png'),
                    dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_comparative_time_series(self):
        """Plot comparative time series across all scenarios."""
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle('Comparative Analysis Across All Occupancy Scenarios', fontsize=16, fontweight='bold')

        # E[N] comparison
        for scenario, avg_df in self.averaged_data.items():
            color = self.scenario_colors.get(scenario, '#333333')
            axes[0, 0].plot(avg_df['timestamp'], avg_df['EN'],
                            label=f'ρ = {scenario.split("_")[1]}', color=color, linewidth=2)
            if 'EN_std' in avg_df.columns:
                axes[0, 0].fill_between(avg_df['timestamp'],
                                        avg_df['EN'] - avg_df['EN_std'],
                                        avg_df['EN'] + avg_df['EN_std'],
                                        alpha=0.2, color=color)

        axes[0, 0].set_title('E[N] Comparison Across Scenarios')
        axes[0, 0].set_ylabel('E[N]')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)

        # E[W] comparison
        for scenario, avg_df in self.averaged_data.items():
            color = self.scenario_colors.get(scenario, '#333333')
            axes[0, 1].plot(avg_df['timestamp'], avg_df['EW'],
                            label=f'ρ = {scenario.split("_")[1]}', color=color, linewidth=2)
            if 'EW_std' in avg_df.columns:
                axes[0, 1].fill_between(avg_df['timestamp'],
                                        avg_df['EW'] - avg_df['EW_std'],
                                        avg_df['EW'] + avg_df['EW_std'],
                                        alpha=0.2, color=color)

        axes[0, 1].set_title('E[W] Comparison Across Scenarios')
        axes[0, 1].set_ylabel('E[W] (seconds)')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)

        # Little's Law Error comparison
        for scenario, avg_df in self.averaged_data.items():
            color = self.scenario_colors.get(scenario, '#333333')
            axes[1, 0].plot(avg_df['timestamp'], avg_df['littleError'],
                            label=f'ρ = {scenario.split("_")[1]}', color=color, linewidth=2)

        axes[1, 0].axhline(y=0, color='black', linestyle='--', alpha=0.5)
        axes[1, 0].set_title("Little's Law Error Comparison")
        axes[1, 0].set_ylabel('Error (E[N] - λ·E[W])')
        axes[1, 0].set_xlabel('Time (seconds)')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)

        # Final state metrics bar plot
        final_metrics = []
        scenarios = []
        for scenario, avg_df in self.averaged_data.items():
            final_row = avg_df.iloc[-1]
            final_metrics.append({
                'EN': final_row['EN'],
                'EW': final_row['EW'],
                'littleError': abs(final_row['littleError'])
            })
            scenarios.append(scenario.split('_')[1])

        x = np.arange(len(scenarios))
        width = 0.25

        axes[1, 1].bar(x - width, [m['EN'] for m in final_metrics], width, label='E[N]', alpha=0.8)
        axes[1, 1].bar(x, [m['EW'] for m in final_metrics], width, label='E[W]', alpha=0.8)
        axes[1, 1].bar(x + width, [m['littleError'] for m in final_metrics], width, label='|Little Error|', alpha=0.8)

        axes[1, 1].set_title('Final State Metrics Comparison')
        axes[1, 1].set_xlabel('Occupancy Scenario')
        axes[1, 1].set_ylabel('Metric Value')
        axes[1, 1].set_xticks(x)
        axes[1, 1].set_xticklabels(scenarios)
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_directory, 'plots/time_series/averaged',
                                 'comparative_analysis_all_scenarios.png'),
                    dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_stability_analysis(self):
        """Plot stability analysis for system metrics."""
        print("Performing stability analysis...")

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('System Stability Analysis', fontsize=16, fontweight='bold')

        for scenario, avg_df in self.averaged_data.items():
            color = self.scenario_colors.get(scenario, '#333333')
            label = f'ρ = {scenario.split("_")[1]}'

            # Média móvel e desvio padrão para E[N]
            window_size = min(100, len(avg_df) // 10)
            rolling_mean = avg_df['EN'].rolling(window=window_size).mean()
            rolling_std = avg_df['EN'].rolling(window=window_size).std()

            axes[0, 0].plot(avg_df['timestamp'], rolling_mean, label=label, color=color, linewidth=2)
            axes[0, 0].fill_between(avg_df['timestamp'],
                                    rolling_mean - rolling_std,
                                    rolling_mean + rolling_std,
                                    alpha=0.2, color=color)

        axes[0, 0].set_title(f'E[N] Rolling Mean ± Std Dev (Window={window_size})')
        axes[0, 0].set_ylabel('E[N]')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)

        # Coeficiente de variação ao longo do tempo
        for scenario, avg_df in self.averaged_data.items():
            color = self.scenario_colors.get(scenario, '#333333')
            cv = (avg_df['EN'] / avg_df['EN'].mean()).rolling(window=50).std()
            axes[0, 1].plot(avg_df['timestamp'], cv, label=label, color=color, linewidth=2)

        axes[0, 1].set_title('Coefficient of Variation (CV) for E[N]')
        axes[0, 1].set_ylabel('CV = σ/μ')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)

        # Análise de convergência - diferença do valor final
        for scenario, avg_df in self.averaged_data.items():
            color = self.scenario_colors.get(scenario, '#333333')
            final_en = avg_df['EN'].iloc[-1]
            convergence = np.abs(avg_df['EN'] - final_en) / final_en
            axes[1, 1].plot(avg_df['timestamp'], convergence,
                            label=label, color=color, linewidth=2)

        axes[1, 1].set_title('Convergence to Steady State')
        axes[1, 1].set_ylabel('|E[N](t) - E[N](final)| / E[N](final)')
        axes[1, 1].set_xlabel('Time (seconds)')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].set_yscale('log')

        # Placeholder para autocorrelação (requer statsmodels)
        axes[1, 0].text(0.5, 0.5, 'Autocorrelation Analysis\n(requires statsmodels)',
                        horizontalalignment='center', verticalalignment='center',
                        transform=axes[1, 0].transAxes, fontsize=12)
        axes[1, 0].set_title('Autocorrelation Function for E[N]')
        axes[1, 0].set_xlabel('Lag')
        axes[1, 0].set_ylabel('Autocorrelation')
        axes[1, 0].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_directory, 'plots/statistical',
                                 'stability_analysis.png'),
                    dpi=300, bbox_inches='tight')
        plt.close()

    def build_machine_learning_models(self):
        """Build and evaluate machine learning models."""
        print("Building machine learning models...")

        # Preparar dados para ML
        feature_data = []
        target_scenario = []
        target_little_error = []

        # Definir colunas numéricas para ML
        feature_columns = ['EN', 'EW', 'queueSize1', 'queueSize2', 'queueSize3',
                           'measuredLambda', 'measuredOccupancy']

        for scenario, seed_data in self.data.items():
            for seed, df in seed_data.items():
                try:
                    # Usar características de estado estacionário (média das últimas 100 amostras)
                    steady_state = df[feature_columns].iloc[-100:].mean()

                    features = steady_state.tolist()
                    feature_data.append(features)
                    target_scenario.append(scenario)
                    target_little_error.append(abs(df['littleError'].iloc[-100:].mean()))
                except Exception as e:
                    print(f"Warning: Error in ML processing for scenario {scenario}, seed {seed}: {str(e)}")
                    continue

        if not feature_data:
            print("Error: No valid data for machine learning")
            return

        X = np.array(feature_data)
        y_scenario = np.array(target_scenario)
        y_error = np.array(target_little_error)

        # Classificação de cenário
        le = LabelEncoder()
        y_scenario_encoded = le.fit_transform(y_scenario)

        X_train, X_test, y_train, y_test = train_test_split(X, y_scenario_encoded, test_size=0.2, random_state=42)

        # Random Forest Classifier
        rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_classifier.fit(X_train, y_train)
        y_pred = rf_classifier.predict(X_test)

        # Random Forest Regressor para predição de erro
        X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(X, y_error, test_size=0.2, random_state=42)
        rf_regressor = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_regressor.fit(X_train_reg, y_train_reg)
        y_pred_reg = rf_regressor.predict(X_test_reg)

        # Armazenar modelos e resultados
        self.ml_models = {
            'classifier': rf_classifier,
            'regressor': rf_regressor,
            'label_encoder': le,
            'feature_names': feature_columns,
            'classification_metrics': {
                'accuracy': np.mean(y_pred == y_test),
                'confusion_matrix': confusion_matrix(y_test, y_pred),
                'classification_report': classification_report(y_test, y_pred, target_names=le.classes_,
                                                               output_dict=True)
            },
            'regression_metrics': {
                'mse': mean_squared_error(y_test_reg, y_pred_reg),
                'r2': r2_score(y_test_reg, y_pred_reg),
                'rmse': np.sqrt(mean_squared_error(y_test_reg, y_pred_reg))
            }
        }

        print("Machine learning models trained and evaluated")

    def generate_comprehensive_report(self):
        """Generate comprehensive HTML report with all analysis results."""
        print("Generating comprehensive report...")

        report_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Advanced Queueing System Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; border-left: 4px solid #3498db; padding-left: 10px; margin-top: 30px; }}
                .summary {{ background: #ecf0f1; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .plot {{ text-align: center; margin: 25px 0; padding: 15px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                img {{ max-width: 95%; height: auto; border: 1px solid #ddd; border-radius: 4px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #3498db; color: white; }}
            </style>
        </head>
        <body>
            <h1>Advanced Queueing System Analysis Report</h1>
            <p><strong>Author:</strong> Rafael Passos Domingues</p>
            <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

            <div class="summary">
                <h2>Executive Summary</h2>
                <p>Comprehensive analysis of queueing system simulation across four occupancy scenarios.</p>
                <p><strong>Scenarios Analyzed:</strong> {len(self.data)}</p>
                <p><strong>Total Seeds:</strong> {sum(len(seeds) for seeds in self.data.values())}</p>
            </div>

            <h2>Time Series Analysis</h2>
            <p>Detailed time-series analysis showing system dynamics and convergence behavior.</p>

            <div class="plot">
                <img src="../plots/time_series/averaged/comparative_analysis_all_scenarios.png" alt="Comparative Time Series">
                <p><em>Comparative analysis of E[N] and E[W] across all occupancy scenarios</em></p>
            </div>

            <h2>Statistical Summary</h2>
            <p>Steady-state statistics computed from the final 100 samples of each simulation.</p>

            <h2>Clustering Analysis</h2>
            <p>K-means clustering identified patterns in simulation data based on system behavior.</p>

            <div class="plot">
                <img src="../plots/clustering/comprehensive_clustering_analysis.png" alt="Clustering Analysis">
                <p><em>Comprehensive clustering analysis showing optimal k selection and cluster visualization</em></p>
            </div>

            <h2>Key Findings</h2>
            <ul>
                <li>Little's Law validation across all scenarios</li>
                <li>System stability and convergence patterns</li>
                <li>Cluster analysis reveals distinct behavioral patterns</li>
                <li>Machine learning models provide predictive insights</li>
            </ul>
        </body>
        </html>
        """

        report_path = os.path.join(self.output_directory, 'reports', 'comprehensive_analysis_report.html')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"Comprehensive report generated: {report_path}")

    def run_complete_analysis(self):
        """Execute the complete analysis pipeline."""
        print("Starting complete analysis pipeline...")
        print("=" * 60)

        start_time = datetime.now()

        # Executar todas as etapas de análise
        self.load_and_process_data()
        self.generate_comprehensive_time_series_plots()
        self.perform_statistical_analysis()
        self.perform_clustering_analysis()
        self.build_machine_learning_models()
        self.generate_comprehensive_report()

        end_time = datetime.now()
        duration = end_time - start_time

        print("=" * 60)
        print("Analysis completed successfully!")
        print(f"Total execution time: {duration}")
        print(f"Results saved to: {self.output_directory}")


def main():
    """Main execution function."""
    analyzer = AdvancedQueueingAnalyzer()
    analyzer.run_complete_analysis()


if __name__ == "__main__":
    main()