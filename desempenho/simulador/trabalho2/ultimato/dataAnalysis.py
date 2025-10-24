#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
Spectral Queue Dynamics Analysis Toolkit (v5.0)
================================================================================
Author: Rafael Passos Domingues
Date: October 24, 2025

Description:
Análise espectral e temporal avançada de sistemas de filas, focando em:
- Dinâmica temporal das filas individuais
- Comportamento espectral (FFT) das séries temporais
- Métricas de Little em alta resolução temporal
- Histórias atômicas de cada política
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
from glob import glob
from scipy import fft
from scipy.signal import spectrogram

# --- Scikit-learn Imports ---
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture
from sklearn.ensemble import IsolationForest
from sklearn.metrics import silhouette_score

# --- Global Configuration ---
warnings.filterwarnings('ignore')
plt.rcParams['figure.max_open_warning'] = 100


# =============================================================================
# CONFIGURATION CLASSES
# =============================================================================

class AnalysisConfiguration:
    def __init__(self):
        self.dataDirectory = Path("results")
        self.outputDirectory = Path("results/spectral_analysis")

        self.filePattern = "queue_data_*_occupancy_*.csv"
        self.fileNameRegex = re.compile(r"queue_data_(.*?)_occupancy_(.*?).csv")

        self.policies = ["RoundRobin", "WaitingTimePriority", "UtilityBased"]
        self.rhos = ['0.800', '0.900', '0.950', '0.999']

        self.colTimestamp = "timestamp"
        self.colAggEN = "averageNumberInSystem"
        self.colAggEW = "averageWaitingTime"
        self.colQueues = ['queueSize1', 'queueSize2', 'queueSize3']
        self.colOccupancy = "measuredOccupancy"
        self.colArrivalRate = "measuredArrivalRate"


class VisualizationConfiguration:
    def __init__(self):
        self.dpi = 300
        self.palette = {
            "RoundRobin": "#0072B2",
            "WaitingTimePriority": "#E69F00",
            "UtilityBased": "#009E73",
            "queue1": "#FF6B6B",
            "queue2": "#4ECDC4",
            "queue3": "#45B7D1"
        }
        self.context = "paper"
        self.style = "darkgrid"
        sns.set_theme(context=self.context, style=self.style)


# =============================================================================
# MAIN ANALYSIS PIPELINE CLASS
# =============================================================================

class SpectralQueueAnalysis:
    def __init__(self):
        print("=================================================================")
        print("  Spectral Queue Dynamics Analysis (v5.0) Initializing")
        print("  (Focus: Temporal Dynamics, Spectral Analysis, Atomic Stories)")
        print("=================================================================")

        self.config = AnalysisConfiguration()
        self.visConfig = VisualizationConfiguration()

        self.masterDataFrame: pd.DataFrame = pd.DataFrame()
        self.spectralData: Dict = {}

        self.config.outputDirectory.mkdir(exist_ok=True)

    def runFullPipeline(self):
        try:
            print("\n--- [PHASE 1/5] Data Loading ---")
            self._loadAllData()

            print("\n--- [PHASE 2/5] Temporal Dynamics Analysis ---")
            self._analyzeTemporalDynamics()

            print("\n--- [PHASE 3/5] Spectral Analysis ---")
            self._performSpectralAnalysis()

            print("\n--- [PHASE 4/5] Atomic Stories Visualization ---")
            self._createAtomicStories()

            print("\n--- [PHASE 5/5] Advanced ML Insights ---")
            self._createAdvancedMLInsights()

            print("\n=================================================================")
            print("  Spectral Analysis Completed Successfully!")
            print(f"  All plots saved to: {self.config.outputDirectory}")
            print("=================================================================")

        except Exception as e:
            print(f"\n[FATAL ERROR] Pipeline failed: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def _loadAllData(self):
        """Carrega todos os dados mantendo a estrutura temporal completa"""
        filePaths = glob(str(self.config.dataDirectory / self.config.filePattern))
        if not filePaths:
            raise FileNotFoundError(f"No files found in '{self.config.dataDirectory}'")

        print(f"  Found {len(filePaths)} files. Processing...")
        allDataFrames = []

        for filePath in filePaths:
            match = self.config.fileNameRegex.search(Path(filePath).name)
            if not match:
                continue

            policy, rhoStr = match.group(1), match.group(2)
            if policy not in self.config.policies or rhoStr not in self.config.rhos:
                continue

            try:
                df = pd.read_csv(filePath)
                df['policy'] = policy
                df['rho'] = rhoStr
                df['scenario'] = f"{policy}_rho{rhoStr}"

                # Calcular métricas de variabilidade
                queue_data = df[self.config.colQueues]
                df['queue_imbalance'] = queue_data.std(axis=1)
                df['queue_spread'] = queue_data.max(axis=1) - queue_data.min(axis=1)
                df['total_queues'] = queue_data.sum(axis=1)

                allDataFrames.append(df)
                print(f"    Loaded {policy} ρ={rhoStr} ({len(df)} samples)")

            except Exception as e:
                print(f"  [Error] Failed to load {filePath}: {e}")

        if not allDataFrames:
            raise ValueError("No valid data was loaded.")

        self.masterDataFrame = pd.concat(allDataFrames, ignore_index=True)
        print(f"  Master DataFrame: {len(self.masterDataFrame)} total samples")

    def _analyzeTemporalDynamics(self):
        """Análise detalhada da dinâmica temporal"""
        print("  Creating temporal dynamics visualizations...")

        # Plot 1: Série temporal das filas individuais em alta carga
        self._plotQueueTimeSeriesHighLoad()

        # Plot 2: Comparação side-by-side das políticas
        self._plotPolicyComparisonTimeSeries()

        # Plot 3: Little's Law em tempo real
        self._plotRealtimeLittlesLaw()

        # Plot 4: Heatmaps de evolução temporal
        self._plotTemporalHeatmaps()

    def _performSpectralAnalysis(self):
        """Análise espectral das séries temporais"""
        print("  Performing spectral analysis...")

        # Plot 5: Análise espectral (FFT)
        self._plotSpectralAnalysis()

        # Plot 6: Espectrogramas
        self._plotSpectrograms()

        # Plot 7: Análise de componentes principais temporais
        self._plotTemporalPCA()

    def _createAtomicStories(self):
        """Cria visualizações que contam 'histórias atômicas'"""
        print("  Creating atomic stories...")

        # Plot 8: Histórias individuais das filas
        self._plotQueueIndividualStories()

        # Plot 9: Diagramas de fase
        self._plotPhaseDiagrams()

        # Plot 10: Comportamento transiente vs steady-state
        self._plotTransientBehavior()

    def _createAdvancedMLInsights(self):
        """Insights avançados de ML mantendo os que você gostou"""
        print("  Creating advanced ML insights...")

        # Plot 11: GMM Clustering (que você gostou)
        self._plotGMMClustering()

        # Plot 12: Anomaly Detection (que você gostou)
        self._plotAnomalyDetection()

        # Plot 13: Análise de trajetórias
        self._plotTrajectoryAnalysis()

    # =========================================================================
    # PLOTTING FUNCTIONS - TEMPORAL DYNAMICS
    # =========================================================================

    def _plotQueueTimeSeriesHighLoad(self):
        """Série temporal detalhada das 3 filas em alta carga"""
        try:
            high_load_data = self.masterDataFrame[self.masterDataFrame['rho'] == '0.999']

            fig, axes = plt.subplots(3, 1, figsize=(16, 12), sharex=True)
            queue_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']

            for policy_idx, policy in enumerate(self.config.policies):
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if policy_data.empty:
                    continue

                # Amostrar para visualização mais limpa
                sample_data = policy_data.iloc[::10]  # Cada 10º ponto

                ax = axes[policy_idx]
                for i, queue_col in enumerate(self.config.colQueues):
                    ax.plot(sample_data[self.config.colTimestamp],
                            sample_data[queue_col],
                            color=queue_colors[i],
                            alpha=0.8,
                            linewidth=1.5,
                            label=f'Fila {i + 1}')

                ax.set_title(f'Política: {policy} - Dinâmica Temporal das Filas (ρ=0.999)',
                             fontsize=14, fontweight='bold', pad=20)
                ax.set_ylabel('Tamanho da Fila', fontsize=12)
                ax.legend(loc='upper right')
                ax.grid(True, alpha=0.3)

                # Adicionar estatísticas no gráfico
                avg_queues = [sample_data[col].mean() for col in self.config.colQueues]
                ax.text(0.02, 0.98, f'Médias: Q1={avg_queues[0]:.1f}, Q2={avg_queues[1]:.1f}, Q3={avg_queues[2]:.1f}',
                        transform=ax.transAxes, verticalalignment='top',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

            axes[-1].set_xlabel('Tempo de Simulação (s)', fontsize=12)
            plt.tight_layout()
            self._savePlot(fig, "1_Queue_Time_Series_High_Load.png")

        except Exception as e:
            print(f"  [Error] Queue time series plot failed: {e}")

    def _plotPolicyComparisonTimeSeries(self):
        """Comparação side-by-side das políticas para um rho específico"""
        try:
            fig, axes = plt.subplots(2, 3, figsize=(20, 12))
            rho_to_plot = '0.999'
            plot_data = self.masterDataFrame[self.masterDataFrame['rho'] == rho_to_plot]

            metrics = [
                ('queueSize1', 'Fila 1'),
                ('queueSize2', 'Fila 2'),
                ('queueSize3', 'Fila 3'),
                ('queue_imbalance', 'Desequilíbrio'),
                ('total_queues', 'Total nas Filas'),
                ('averageWaitingTime', 'E[W]')
            ]

            for i, (metric, title) in enumerate(metrics):
                row, col = i // 3, i % 3
                ax = axes[row, col]

                for policy in self.config.policies:
                    policy_data = plot_data[plot_data['policy'] == policy]
                    if not policy_data.empty:
                        sample_data = policy_data.iloc[::20]  # Amostragem
                        ax.plot(sample_data[self.config.colTimestamp],
                                sample_data[metric],
                                label=policy,
                                color=self.visConfig.palette[policy],
                                alpha=0.7,
                                linewidth=1.2)

                ax.set_title(title, fontweight='bold')
                ax.set_xlabel('Tempo')
                ax.set_ylabel(title)
                ax.legend()
                ax.grid(True, alpha=0.3)

            plt.suptitle(f'Comparação de Políticas - ρ={rho_to_plot}', fontsize=16, fontweight='bold')
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            self._savePlot(fig, "2_Policy_Comparison_TimeSeries.png")

        except Exception as e:
            print(f"  [Error] Policy comparison plot failed: {e}")

    def _plotRealtimeLittlesLaw(self):
        """Visualização da Lei de Little em tempo real"""
        try:
            high_load_data = self.masterDataFrame[self.masterDataFrame['rho'] == '0.999']

            fig, axes = plt.subplots(3, 2, figsize=(18, 12))

            for policy_idx, policy in enumerate(self.config.policies):
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if policy_data.empty:
                    continue

                sample_data = policy_data.iloc[::10]

                # E[N] vs tempo
                ax1 = axes[policy_idx, 0]
                ax1.plot(sample_data[self.config.colTimestamp],
                         sample_data[self.config.colAggEN],
                         color='purple', alpha=0.8, linewidth=2)
                ax1.set_title(f'{policy} - Número Médio no Sistema (E[N])')
                ax1.set_ylabel('E[N]')
                ax1.grid(True, alpha=0.3)

                # E[W] vs tempo
                ax2 = axes[policy_idx, 1]
                ax2.plot(sample_data[self.config.colTimestamp],
                         sample_data[self.config.colAggEW],
                         color='orange', alpha=0.8, linewidth=2)
                ax2.set_title(f'{policy} - Tempo Médio de Espera (E[W])')
                ax2.set_ylabel('E[W] (s)')
                ax2.grid(True, alpha=0.3)

                # Calcular e mostrar Little's Law
                avg_N = sample_data[self.config.colAggEN].mean()
                avg_W = sample_data[self.config.colAggEW].mean()
                lambda_ = sample_data[self.config.colArrivalRate].mean()
                little_check = avg_N / (lambda_ * avg_W) if lambda_ * avg_W > 0 else 0

                ax1.text(0.02, 0.98, f'Little\'s Law: E[N]/(λ·E[W]) = {little_check:.3f}',
                         transform=ax1.transAxes, verticalalignment='top',
                         bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

            plt.suptitle('Lei de Little em Tempo Real - ρ=0.999', fontsize=16, fontweight='bold')
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            self._savePlot(fig, "3_Realtime_Littles_Law.png")

        except Exception as e:
            print(f"  [Error] Little's Law plot failed: {e}")

    def _plotTemporalHeatmaps(self):
        """Heatmaps da evolução temporal"""
        try:
            high_load_data = self.masterDataFrame[self.masterDataFrame['rho'] == '0.999']

            fig, axes = plt.subplots(1, 3, figsize=(20, 8))

            for i, policy in enumerate(self.config.policies):
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if policy_data.empty:
                    continue

                # Preparar dados para heatmap
                queue_matrix = policy_data[self.config.colQueues].values.T
                timestamp_normalized = np.linspace(0, 1, len(policy_data))

                im = axes[i].imshow(queue_matrix, aspect='auto', cmap='viridis',
                                    extent=[0, 1, 0, 3], interpolation='nearest')
                axes[i].set_title(f'{policy} - Evolução das Filas', fontweight='bold')
                axes[i].set_xlabel('Tempo Normalizado')
                axes[i].set_ylabel('Fila')
                axes[i].set_yticks([0.5, 1.5, 2.5])
                axes[i].set_yticklabels(['Fila 1', 'Fila 2', 'Fila 3'])

                plt.colorbar(im, ax=axes[i], label='Tamanho da Fila')

            plt.suptitle('Heatmaps de Evolução Temporal das Filas - ρ=0.999',
                         fontsize=16, fontweight='bold')
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            self._savePlot(fig, "4_Temporal_Heatmaps.png")

        except Exception as e:
            print(f"  [Error] Temporal heatmaps plot failed: {e}")

    # =========================================================================
    # PLOTTING FUNCTIONS - SPECTRAL ANALYSIS
    # =========================================================================

    def _plotSpectralAnalysis(self):
        """Análise espectral via FFT das séries temporais"""
        try:
            high_load_data = self.masterDataFrame[self.masterDataFrame['rho'] == '0.999']

            fig, axes = plt.subplots(3, 1, figsize=(15, 12))

            for policy_idx, policy in enumerate(self.config.policies):
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if policy_data.empty:
                    continue

                ax = axes[policy_idx]

                for queue_idx, queue_col in enumerate(self.config.colQueues):
                    queue_data = policy_data[queue_col].values

                    # Remover tendência linear
                    detrended = queue_data - np.mean(queue_data)

                    # FFT
                    fft_vals = np.abs(fft.fft(detrended))
                    freqs = fft.fftfreq(len(detrended))

                    # Plotar apenas frequências positivas
                    positive_freq_idx = freqs > 0
                    ax.semilogy(freqs[positive_freq_idx], fft_vals[positive_freq_idx],
                                label=f'Fila {queue_idx + 1}', alpha=0.7, linewidth=2)

                ax.set_title(f'{policy} - Análise Espectral (FFT)', fontweight='bold')
                ax.set_xlabel('Frequência')
                ax.set_ylabel('Magnitude (log)')
                ax.legend()
                ax.grid(True, alpha=0.3)

            plt.suptitle('Análise Espectral das Séries Temporais das Filas',
                         fontsize=16, fontweight='bold')
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            self._savePlot(fig, "5_Spectral_Analysis_FFT.png")

        except Exception as e:
            print(f"  [Error] Spectral analysis plot failed: {e}")

    def _plotSpectrograms(self):
        """Espectrogramas das séries temporais"""
        try:
            high_load_data = self.masterDataFrame[self.masterDataFrame['rho'] == '0.999']

            fig, axes = plt.subplots(3, 3, figsize=(18, 12))

            for policy_idx, policy in enumerate(self.config.policies):
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if policy_data.empty:
                    continue

                for queue_idx, queue_col in enumerate(self.config.colQueues):
                    ax = axes[policy_idx, queue_idx]
                    queue_data = policy_data[queue_col].values

                    # Calcular espectrograma
                    f, t, Sxx = spectrogram(queue_data, fs=1.0, nperseg=min(256, len(queue_data) // 4))

                    im = ax.pcolormesh(t, f, 10 * np.log10(Sxx), shading='gouraud', cmap='viridis')
                    ax.set_title(f'{policy} - Fila {queue_idx + 1}')
                    ax.set_ylabel('Frequência [Hz]')
                    ax.set_xlabel('Tempo [s]')

                    plt.colorbar(im, ax=ax, label='Potência (dB)')

            plt.suptitle('Espectrogramas das Séries Temporais das Filas',
                         fontsize=16, fontweight='bold')
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            self._savePlot(fig, "6_Spectrograms.png")

        except Exception as e:
            print(f"  [Error] Spectrograms plot failed: {e}")

    def _plotTemporalPCA(self):
        """PCA das séries temporais"""
        try:
            high_load_data = self.masterDataFrame[self.masterDataFrame['rho'] == '0.999']

            fig, axes = plt.subplots(1, 3, figsize=(18, 6))

            for i, policy in enumerate(self.config.policies):
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if policy_data.empty:
                    continue

                # Preparar dados para PCA
                features = policy_data[self.config.colQueues + ['queue_imbalance', 'total_queues']]
                scaler = StandardScaler()
                features_scaled = scaler.fit_transform(features)

                # PCA
                pca = PCA(n_components=2)
                principal_components = pca.fit_transform(features_scaled)

                # Colorir por tempo
                time_normalized = np.linspace(0, 1, len(principal_components))

                scatter = axes[i].scatter(principal_components[:, 0], principal_components[:, 1],
                                          c=time_normalized, cmap='viridis', alpha=0.6, s=10)
                axes[i].set_title(f'{policy} - PCA Temporal\nVariance: {pca.explained_variance_ratio_.sum():.2%}')
                axes[i].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%})')
                axes[i].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%})')

                plt.colorbar(scatter, ax=axes[i], label='Tempo Normalizado')

            plt.suptitle('Análise de Componentes Principais das Trajetórias Temporais',
                         fontsize=16, fontweight='bold')
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            self._savePlot(fig, "7_Temporal_PCA.png")

        except Exception as e:
            print(f"  [Error] Temporal PCA plot failed: {e}")

    # =========================================================================
    # PLOTTING FUNCTIONS - ATOMIC STORIES
    # =========================================================================

    def _plotQueueIndividualStories(self):
        """Histórias individuais detalhadas de cada fila"""
        try:
            high_load_data = self.masterDataFrame[self.masterDataFrame['rho'] == '0.999']

            # Focar em uma janela temporal específica para mais detalhes
            for policy in self.config.policies:
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if policy_data.empty:
                    continue

                # Pegar uma janela do meio da simulação
                window_size = min(1000, len(policy_data))
                start_idx = len(policy_data) // 3
                window_data = policy_data.iloc[start_idx:start_idx + window_size]

                fig, axes = plt.subplots(2, 2, figsize=(15, 10))

                # Plot 1: Três filas juntas
                for i, queue_col in enumerate(self.config.colQueues):
                    axes[0, 0].plot(window_data[self.config.colTimestamp],
                                    window_data[queue_col],
                                    label=f'Fila {i + 1}',
                                    color=self.visConfig.palette[f'queue{i + 1}'],
                                    linewidth=2)

                axes[0, 0].set_title(f'{policy} - Comportamento das 3 Filas')
                axes[0, 0].set_ylabel('Tamanho da Fila')
                axes[0, 0].legend()
                axes[0, 0].grid(True, alpha=0.3)

                # Plot 2: Desequilíbrio
                axes[0, 1].plot(window_data[self.config.colTimestamp],
                                window_data['queue_imbalance'],
                                color='red', linewidth=2)
                axes[0, 1].set_title(f'{policy} - Desequilíbrio entre Filas')
                axes[0, 1].set_ylabel('Desequilíbrio (std)')
                axes[0, 1].grid(True, alpha=0.3)

                # Plot 3: Spread
                axes[1, 0].plot(window_data[self.config.colTimestamp],
                                window_data['queue_spread'],
                                color='purple', linewidth=2)
                axes[1, 0].set_title(f'{policy} - Spread (max-min)')
                axes[1, 0].set_ylabel('Spread')
                axes[1, 0].grid(True, alpha=0.3)

                # Plot 4: Histograma dos tamanhos
                for i, queue_col in enumerate(self.config.colQueues):
                    axes[1, 1].hist(window_data[queue_col],
                                    alpha=0.6,
                                    label=f'Fila {i + 1}',
                                    color=self.visConfig.palette[f'queue{i + 1}'],
                                    bins=30)

                axes[1, 1].set_title(f'{policy} - Distribuição dos Tamanhos')
                axes[1, 1].set_xlabel('Tamanho da Fila')
                axes[1, 1].set_ylabel('Frequência')
                axes[1, 1].legend()

                plt.suptitle(f'História Atômica: {policy} - ρ=0.999',
                             fontsize=16, fontweight='bold')
                plt.tight_layout(rect=[0, 0, 1, 0.96])
                self._savePlot(fig, f"8_Atomic_Story_{policy}.png")
                plt.close(fig)  # Fechar figura para liberar memória

        except Exception as e:
            print(f"  [Error] Atomic stories plot failed: {e}")

    def _plotPhaseDiagrams(self):
        """Diagramas de fase mostrando relações entre variáveis"""
        try:
            high_load_data = self.masterDataFrame[self.masterDataFrame['rho'] == '0.999']

            fig, axes = plt.subplots(2, 3, figsize=(18, 12))

            phase_pairs = [
                ('queueSize1', 'queueSize2', 'Fila 1 vs Fila 2'),
                ('queueSize1', 'queueSize3', 'Fila 1 vs Fila 3'),
                ('queueSize2', 'queueSize3', 'Fila 2 vs Fila 3'),
                ('queue_imbalance', 'total_queues', 'Desequilíbrio vs Total'),
                ('averageNumberInSystem', 'averageWaitingTime', 'E[N] vs E[W]'),
                ('queue_spread', 'queue_imbalance', 'Spread vs Desequilíbrio')
            ]

            for i, (x_col, y_col, title) in enumerate(phase_pairs):
                row, col = i // 3, i % 3
                ax = axes[row, col]

                for policy in self.config.policies:
                    policy_data = high_load_data[high_load_data['policy'] == policy]
                    if not policy_data.empty:
                        sample_data = policy_data.iloc[::5]  # Amostrar para clareza
                        ax.scatter(sample_data[x_col], sample_data[y_col],
                                   alpha=0.6, s=10, label=policy,
                                   color=self.visConfig.palette[policy])

                ax.set_title(title, fontweight='bold')
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                ax.legend()
                ax.grid(True, alpha=0.3)

            plt.suptitle('Diagramas de Fase - Relações entre Variáveis',
                         fontsize=16, fontweight='bold')
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            self._savePlot(fig, "9_Phase_Diagrams.png")

        except Exception as e:
            print(f"  [Error] Phase diagrams plot failed: {e}")

    def _plotTransientBehavior(self):
        """Análise do comportamento transiente vs steady-state"""
        try:
            fig, axes = plt.subplots(3, 2, figsize=(16, 12))

            for policy_idx, policy in enumerate(self.config.policies):
                policy_data = self.masterDataFrame[self.masterDataFrame['policy'] == policy]
                if policy_data.empty:
                    continue

                for rho_idx, rho in enumerate(['0.800', '0.999']):  # Baixa vs alta carga
                    rho_data = policy_data[policy_data['rho'] == rho]
                    if rho_data.empty:
                        continue

                    # Dividir em transiente (primeiros 30%) e steady-state (últimos 70%)
                    transient_cut = int(0.3 * len(rho_data))
                    transient_data = rho_data.iloc[:transient_cut]
                    steady_data = rho_data.iloc[transient_cut:]

                    ax = axes[policy_idx, rho_idx]

                    # Plot transiente
                    if not transient_data.empty:
                        ax.plot(transient_data[self.config.colTimestamp],
                                transient_data[self.config.colAggEN],
                                color='red', alpha=0.7, linewidth=2,
                                label='Transiente')

                    # Plot steady-state
                    if not steady_data.empty:
                        ax.plot(steady_data[self.config.colTimestamp],
                                steady_data[self.config.colAggEN],
                                color='blue', alpha=0.7, linewidth=2,
                                label='Steady-State')

                    ax.set_title(f'{policy} - ρ={rho}', fontweight='bold')
                    ax.set_ylabel('E[N]')
                    ax.legend()
                    ax.grid(True, alpha=0.3)

                    if policy_idx == 2:  # Última linha
                        ax.set_xlabel('Tempo')

            plt.suptitle('Comportamento Transiente vs Steady-State',
                         fontsize=16, fontweight='bold')
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            self._savePlot(fig, "10_Transient_vs_SteadyState.png")

        except Exception as e:
            print(f"  [Error] Transient behavior plot failed: {e}")

    # =========================================================================
    # PLOTTING FUNCTIONS - ADVANCED ML (OS QUE VOCÊ GOSTOU)
    # =========================================================================

    def _plotGMMClustering(self):
        """GMM Clustering melhorado"""
        try:
            high_load_data = self.masterDataFrame[self.masterDataFrame['rho'] == '0.999']

            # Preparar features para clustering
            features = []
            labels = []
            for policy in self.config.policies:
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if not policy_data.empty:
                    policy_features = policy_data[self.config.colQueues + ['queue_imbalance']].values
                    features.append(policy_features)
                    labels.extend([policy] * len(policy_features))

            if not features:
                return

            X = np.vstack(features)
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # GMM
            gmm = GaussianMixture(n_components=4, random_state=42, n_init=10)
            clusters = gmm.fit_predict(X_scaled)

            # PCA para visualização
            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(X_scaled)

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

            # Plot por cluster
            scatter1 = ax1.scatter(X_pca[:, 0], X_pca[:, 1], c=clusters,
                                   cmap='viridis', alpha=0.6, s=20)
            ax1.set_title('Clusters GMM (4 componentes)')
            ax1.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%})')
            ax1.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%})')
            plt.colorbar(scatter1, ax=ax1, label='Cluster')

            # Plot por política
            policy_to_num = {policy: i for i, policy in enumerate(self.config.policies)}
            policy_nums = [policy_to_num[label] for label in labels]

            scatter2 = ax2.scatter(X_pca[:, 0], X_pca[:, 1], c=policy_nums,
                                   cmap='Set1', alpha=0.6, s=20)
            ax2.set_title('Coloração por Política')
            ax2.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%})')
            ax2.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%})')

            # Criar legend customizado para políticas
            from matplotlib.lines import Line2D
            legend_elements = [Line2D([0], [0], marker='o', color='w',
                                      markerfacecolor=plt.cm.Set1(i),
                                      markersize=10, label=policy)
                               for i, policy in enumerate(self.config.policies)]
            ax2.legend(handles=legend_elements)

            plt.suptitle('Análise de Clusters GMM - Estados do Sistema',
                         fontsize=16, fontweight='bold')
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            self._savePlot(fig, "11_GMM_Clustering_Enhanced.png")

        except Exception as e:
            print(f"  [Error] GMM clustering plot failed: {e}")

    def _plotAnomalyDetection(self):
        """Anomaly Detection melhorado"""
        try:
            high_load_data = self.masterDataFrame[self.masterDataFrame['rho'] == '0.999']

            features = []
            policy_labels = []
            time_labels = []

            for policy in self.config.policies:
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if not policy_data.empty:
                    policy_features = policy_data[self.config.colQueues + [
                        'queue_imbalance', 'queue_spread', 'total_queues'
                    ]].values
                    features.append(policy_features)
                    policy_labels.extend([policy] * len(policy_features))
                    time_labels.extend(policy_data[self.config.colTimestamp].values)

            if not features:
                return

            X = np.vstack(features)
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # Isolation Forest
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            anomalies = iso_forest.fit_predict(X_scaled)

            # PCA para visualização
            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(X_scaled)

            fig, axes = plt.subplots(2, 2, figsize=(16, 12))

            # Plot 1: Anomalias por política
            for i, policy in enumerate(self.config.policies):
                mask = np.array(policy_labels) == policy
                if not np.any(mask):
                    continue

                policy_anomalies = anomalies[mask] == -1
                policy_normal = anomalies[mask] == 1

                # Normais
                axes[0, 0].scatter(X_pca[mask, 0][policy_normal], X_pca[mask, 1][policy_normal],
                                   alpha=0.3, s=20, label=f'{policy} (Normal)',
                                   color=self.visConfig.palette[policy])
                # Anomalias
                axes[0, 0].scatter(X_pca[mask, 0][policy_anomalies], X_pca[mask, 1][policy_anomalies],
                                   alpha=0.8, s=50, marker='x', label=f'{policy} (Anomalia)',
                                   color=self.visConfig.palette[policy], linewidth=2)

            axes[0, 0].set_title('Detecção de Anomalias por Política')
            axes[0, 0].set_xlabel('PC1')
            axes[0, 0].set_ylabel('PC2')
            axes[0, 0].legend()

            # Plot 2: Taxa de anomalias por política
            anomaly_rates = {}
            for policy in self.config.policies:
                mask = np.array(policy_labels) == policy
                if np.any(mask):
                    rate = (anomalies[mask] == -1).mean() * 100
                    anomaly_rates[policy] = rate

            axes[0, 1].bar(anomaly_rates.keys(), anomaly_rates.values(),
                           color=[self.visConfig.palette[p] for p in anomaly_rates.keys()])
            axes[0, 1].set_title('Taxa de Anomalias por Política')
            axes[0, 1].set_ylabel('Anomalias (%)')

            # Plot 3: Anomalias ao longo do tempo
            time_labels = np.array(time_labels)
            for policy in self.config.policies:
                mask = np.array(policy_labels) == policy
                if not np.any(mask):
                    continue

                policy_times = time_labels[mask]
                policy_anomalies = anomalies[mask] == -1

                axes[1, 0].scatter(policy_times[policy_anomalies],
                                   [list(self.config.policies).index(policy)] * np.sum(policy_anomalies),
                                   alpha=0.6, s=30, marker='x',
                                   color=self.visConfig.palette[policy])

            axes[1, 0].set_title('Anomalias ao Longo do Tempo')
            axes[1, 0].set_xlabel('Tempo de Simulação')
            axes[1, 0].set_ylabel('Política')
            axes[1, 0].set_yticks(range(len(self.config.policies)))
            axes[1, 0].set_yticklabels(self.config.policies)

            # Plot 4: Características das anomalias
            anomaly_features = X[anomalies == -1]
            if len(anomaly_features) > 0:
                feature_means = anomaly_features.mean(axis=0)
                feature_names = self.config.colQueues + ['Desequilíbrio', 'Spread', 'Total']

                axes[1, 1].barh(feature_names, feature_means)
                axes[1, 1].set_title('Características Médias das Anomalias')
                axes[1, 1].set_xlabel('Valor Médio')

            plt.suptitle('Análise Avançada de Detecção de Anomalias',
                         fontsize=16, fontweight='bold')
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            self._savePlot(fig, "12_Anomaly_Detection_Enhanced.png")

        except Exception as e:
            print(f"  [Error] Anomaly detection plot failed: {e}")

    def _plotTrajectoryAnalysis(self):
        """Análise de trajetórias no espaço de estados"""
        try:
            high_load_data = self.masterDataFrame[self.masterDataFrame['rho'] == '0.999']

            fig = plt.figure(figsize=(15, 10))
            ax = fig.add_subplot(111, projection='3d')

            for policy in self.config.policies:
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if policy_data.empty:
                    continue

                # Amostrar trajetória
                sample_data = policy_data.iloc[::10]

                # Trajetória no espaço 3D das filas
                ax.plot(sample_data['queueSize1'],
                        sample_data['queueSize2'],
                        sample_data['queueSize3'],
                        label=policy, alpha=0.7, linewidth=1.5,
                        color=self.visConfig.palette[policy])

                # Pontos inicial e final
                ax.scatter([sample_data['queueSize1'].iloc[0]],
                           [sample_data['queueSize2'].iloc[0]],
                           [sample_data['queueSize3'].iloc[0]],
                           color=self.visConfig.palette[policy], s=100, marker='o')
                ax.scatter([sample_data['queueSize1'].iloc[-1]],
                           [sample_data['queueSize2'].iloc[-1]],
                           [sample_data['queueSize3'].iloc[-1]],
                           color=self.visConfig.palette[policy], s=100, marker='s')

            ax.set_xlabel('Fila 1')
            ax.set_ylabel('Fila 2')
            ax.set_zlabel('Fila 3')
            ax.set_title('Trajetórias no Espaço de Estados das Filas', fontweight='bold')
            ax.legend()

            plt.tight_layout()
            self._savePlot(fig, "13_Trajectory_Analysis_3D.png")

        except Exception as e:
            print(f"  [Error] Trajectory analysis plot failed: {e}")

    def _savePlot(self, fig: plt.Figure, filename: str):
        """Salva plot com alta qualidade"""
        path = self.config.outputDirectory / filename
        fig.savefig(path, dpi=self.visConfig.dpi, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close(fig)
        print(f"    Saved: {filename}")


# =============================================================================
# SCRIPT EXECUTION
# =============================================================================

if __name__ == "__main__":
    pipeline = SpectralQueueAnalysis()
    pipeline.runFullPipeline()