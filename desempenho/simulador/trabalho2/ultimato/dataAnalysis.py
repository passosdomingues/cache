#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
Comprehensive Queueing System Analysis Toolkit (v6.0)
================================================================================
Author: Rafael Passos Domingues
Date: October 24, 2025

Description:
Advanced multi-faceted analysis of queueing system simulation data featuring:
- Temporal dynamics and spectral analysis
- Statistical distributions and moment analysis
- Advanced machine learning insights
- Cross-scenario comparative analysis
- Robust error handling and validation
- Publication-ready visualizations (300 DPI)

Features:
✓ 20+ different visualization types
✓ Comprehensive statistical testing
✓ Advanced signal processing
✓ Multi-dimensional clustering
✓ Anomaly detection and analysis
✓ Feature importance analysis
✓ Comparative performance metrics
✓ Automated report generation
"""

# --- Standard Library Imports ---
import sys
import re
import warnings
import traceback
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import logging

# --- Third-Party Imports ---
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from glob import glob
from scipy import fft, stats
from scipy.signal import spectrogram, welch, periodogram
from scipy.stats import shapiro, anderson, kstest, normaltest
import scipy.cluster.hierarchy as sch

# --- Scikit-learn Imports ---
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.decomposition import PCA, FastICA
from sklearn.mixture import GaussianMixture
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.cluster import DBSCAN, AgglomerativeClustering, KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.manifold import TSNE
from sklearn.feature_selection import mutual_info_regression

# --- Statistical Testing ---
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.stats.diagnostic import lilliefors
import statsmodels.api as sm

# --- Global Configuration ---
warnings.filterwarnings('ignore')
plt.rcParams['figure.max_open_warning'] = 150

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION CLASSES
# =============================================================================

class AnalysisConfiguration:
    def __init__(self):
        # Data I/O Configuration
        self.data_directory = Path("results")
        self.output_directory = Path("results/comprehensive_analysis")
        self.backup_directory = Path("results/backup_analysis")
        
        # File patterns
        self.file_pattern = "queue_data_*_occupancy_*.csv"
        self.file_name_regex = re.compile(r"queue_data_(.*?)_occupancy_(.*?).csv")

        # Experiment dimensions
        self.policies = ["RoundRobin", "WaitingTimePriority", "UtilityBased"]
        self.rhos = ['0.800', '0.900', '0.950', '0.999']
        self.queue_names = ['queue1', 'queue2', 'queue3']

        # Column mappings
        self.col_timestamp = "timestamp"
        self.col_agg_en = "averageNumberInSystem"
        self.col_agg_ew = "averageWaitingTime"
        self.col_queues = ['queueSize1', 'queueSize2', 'queueSize3']
        self.col_occupancy = "measuredOccupancy"
        self.col_arrival_rate = "measuredArrivalRate"

        # Analysis parameters
        self.steady_state_detection = {
            'window': 100,
            'threshold': 0.02,
            'patience': 5,
            'fallback_ratio': 0.15
        }
        
        self.spectral_analysis = {
            'nperseg': 256,
            'noverlap': 128,
            'nfft': 1024
        }
        
        self.clustering = {
            'n_clusters_range': range(2, 6),
            'random_state': 42
        }


class VisualizationConfiguration:
    def __init__(self):
        self.dpi = 300
        self.style = "whitegrid"
        self.context = "paper"
        self.palette = {
            "RoundRobin": "#0072B2",
            "WaitingTimePriority": "#E69F00", 
            "UtilityBased": "#009E73",
            "queue1": "#FF6B6B",
            "queue2": "#4ECDC4", 
            "queue3": "#45B7D1",
            "anomaly": "#DC267F",
            "normal": "#648FFF"
        }
        self.cmap = "viridis"
        self.figsize_standard = (12, 8)
        self.figsize_large = (16, 12)
        self.figsize_small = (8, 6)
        
        sns.set_theme(context=self.context, style=self.style)
        
        # Matplotlib style configuration
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['legend.fontsize'] = 10


# =============================================================================
# ERROR HANDLING AND VALIDATION
# =============================================================================

class AnalysisError(Exception):
    """Custom exception for analysis errors"""
    pass


class DataValidation:
    """Data validation and sanity checks"""
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> bool:
        """Validate DataFrame structure and content"""
        if df.empty:
            raise AnalysisError("DataFrame is empty")
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise AnalysisError(f"Missing required columns: {missing_columns}")
        
        # Check for infinite values
        if np.any(np.isinf(df.select_dtypes(include=[np.number]))):
            logger.warning("DataFrame contains infinite values")
            
        # Check for excessive null values
        null_counts = df.isnull().sum()
        if null_counts.any():
            logger.warning(f"DataFrame contains null values: {null_counts[null_counts > 0].to_dict()}")
            
        return True
    
    @staticmethod
    def validate_numerical_range(df: pd.DataFrame, columns: List[str], min_val: float = 0, max_val: float = 1e6) -> bool:
        """Validate numerical ranges for specified columns"""
        for col in columns:
            if col in df.columns:
                if df[col].min() < min_val or df[col].max() > max_val:
                    logger.warning(f"Column {col} has values outside expected range [{min_val}, {max_val}]")
        return True


# =============================================================================
# MAIN ANALYSIS PIPELINE CLASS
# =============================================================================

class ComprehensiveQueueAnalysis:
    """
    Comprehensive analysis pipeline for queueing system simulation data
    """
    
    def __init__(self):
        logger.info("Initializing Comprehensive Queue Analysis Pipeline (v6.0)")
        
        self.config = AnalysisConfiguration()
        self.vis_config = VisualizationConfiguration()
        self.validator = DataValidation()
        
        # Data storage
        self.master_data: pd.DataFrame = pd.DataFrame()
        self.analysis_results: Dict[str, Any] = {}
        self.statistical_tests: Dict[str, Any] = {}
        
        # Create output directories
        self.config.output_directory.mkdir(exist_ok=True)
        self.config.backup_directory.mkdir(exist_ok=True)
        
        # Analysis state
        self.analysis_completed = False
        
    def run_comprehensive_analysis(self) -> bool:
        """
        Execute the complete analysis pipeline with robust error handling
        """
        try:
            logger.info("Starting comprehensive analysis pipeline")
            start_time = datetime.now()
            
            # Phase 1: Data Loading and Validation
            if not self._load_and_validate_data():
                raise AnalysisError("Data loading and validation failed")
            
            # Phase 2: Statistical Analysis
            self._perform_statistical_analysis()
            
            # Phase 3: Temporal Analysis
            self._perform_temporal_analysis()
            
            # Phase 4: Spectral Analysis
            self._perform_spectral_analysis()
            
            # Phase 5: Machine Learning Analysis
            self._perform_ml_analysis()
            
            # Phase 6: Comparative Analysis
            self._perform_comparative_analysis()
            
            # Phase 7: Generate Comprehensive Report
            self._generate_analysis_report()
            
            # Phase 8: Create All Visualizations
            self._create_all_visualizations()
            
            self.analysis_completed = True
            end_time = datetime.now()
            duration = end_time - start_time
            
            logger.info(f"Analysis completed successfully in {duration}")
            return True
            
        except Exception as e:
            logger.error(f"Analysis pipeline failed: {str(e)}")
            logger.error(traceback.format_exc())
            self._create_error_report(e)
            return False
    
    def _load_and_validate_data(self) -> bool:
        """Load and validate all simulation data"""
        try:
            logger.info("Loading simulation data...")
            
            file_paths = glob(str(self.config.data_directory / self.config.file_pattern))
            if not file_paths:
                raise AnalysisError(f"No files found matching pattern: {self.config.file_pattern}")
            
            logger.info(f"Found {len(file_paths)} data files")
            
            all_dataframes = []
            loaded_scenarios = 0
            
            for file_path in file_paths:
                try:
                    match = self.config.file_name_regex.search(Path(file_path).name)
                    if not match:
                        logger.warning(f"Skipping non-matching file: {file_path}")
                        continue
                    
                    policy, rho_str = match.group(1), match.group(2)
                    if policy not in self.config.policies or rho_str not in self.config.rhos:
                        logger.warning(f"Skipping unrecognized policy/rho: {policy}/{rho_str}")
                        continue
                    
                    # Load and validate individual file
                    df = self._load_single_file(file_path, policy, rho_str)
                    all_dataframes.append(df)
                    loaded_scenarios += 1
                    logger.info(f"Successfully loaded {policy} (ρ={rho_str})")
                    
                except Exception as e:
                    logger.error(f"Failed to load {file_path}: {str(e)}")
                    continue
            
            if not all_dataframes:
                raise AnalysisError("No valid data files could be loaded")
            
            # Combine all data
            self.master_data = pd.concat(all_dataframes, ignore_index=True)
            logger.info(f"Master dataset created: {len(self.master_data)} rows, {loaded_scenarios} scenarios")
            
            # Perform comprehensive validation
            required_columns = [self.config.col_timestamp, self.config.col_agg_en, 
                              self.config.col_agg_ew] + self.config.col_queues
            self.validator.validate_dataframe(self.master_data, required_columns)
            
            # Add derived metrics
            self._enrich_dataset()
            
            return True
            
        except Exception as e:
            logger.error(f"Data loading failed: {str(e)}")
            raise
    
    def _load_single_file(self, file_path: str, policy: str, rho: str) -> pd.DataFrame:
        """Load and validate a single data file"""
        try:
            df = pd.read_csv(file_path)
            
            # Basic validation
            if df.empty:
                raise AnalysisError(f"Empty file: {file_path}")
            
            # Add metadata
            df['policy'] = policy
            df['rho'] = rho
            df['scenario_id'] = f"{policy}_rho{rho}"
            df['file_source'] = Path(file_path).name
            
            return df
            
        except Exception as e:
            raise AnalysisError(f"Failed to load {file_path}: {str(e)}")
    
    def _enrich_dataset(self) -> None:
        """Add comprehensive derived metrics to the dataset"""
        logger.info("Enriching dataset with derived metrics...")
        
        # Queue-based metrics
        queue_data = self.master_data[self.config.col_queues]
        
        # Basic statistics
        self.master_data['queue_imbalance'] = queue_data.std(axis=1)
        self.master_data['queue_spread'] = queue_data.max(axis=1) - queue_data.min(axis=1)
        self.master_data['total_queues'] = queue_data.sum(axis=1)
        self.master_data['queue_mean'] = queue_data.mean(axis=1)
        self.master_data['queue_cv'] = queue_data.std(axis=1) / (queue_data.mean(axis=1) + 1e-8)  # Coefficient of variation
        
        # Advanced metrics
        self.master_data['max_queue_ratio'] = queue_data.max(axis=1) / (queue_data.mean(axis=1) + 1e-8)
        self.master_data['min_queue_ratio'] = queue_data.min(axis=1) / (queue_data.mean(axis=1) + 1e-8)
        self.master_data['dominant_queue'] = queue_data.idxmax(axis=1)
        
        # Little's Law validation metrics
        self.master_data['littles_ratio'] = (
            self.master_data[self.config.col_agg_en] / 
            (self.master_data[self.config.col_arrival_rate] * self.master_data[self.config.col_agg_ew] + 1e-8)
        )
        
        # Temporal features (if timestamp is available)
        if self.config.col_timestamp in self.master_data.columns:
            self.master_data['time_from_start'] = (
                self.master_data[self.config.col_timestamp] - 
                self.master_data.groupby('scenario_id')[self.config.col_timestamp].transform('min')
            )
    
    def _perform_statistical_analysis(self) -> None:
        """Perform comprehensive statistical analysis"""
        logger.info("Performing statistical analysis...")
        
        try:
            self.statistical_tests = {}
            
            # 1. Normality tests for key metrics
            normality_results = {}
            test_metrics = [self.config.col_agg_ew, 'queue_imbalance', 'total_queues']
            
            for scenario in self.master_data['scenario_id'].unique():
                scenario_data = self.master_data[self.master_data['scenario_id'] == scenario]
                normality_results[scenario] = {}
                
                for metric in test_metrics:
                    if metric in scenario_data.columns:
                        data = scenario_data[metric].dropna()
                        if len(data) > 3:  # Minimum sample size for tests
                            normality_results[scenario][metric] = {
                                'shapiro': shapiro(data),
                                'anderson': anderson(data),
                                'normaltest': normaltest(data)
                            }
            
            self.statistical_tests['normality'] = normality_results
            
            # 2. Stationarity tests for time series
            stationarity_results = {}
            for scenario in self.master_data['scenario_id'].unique()[:3]:  # Limit to first 3 for performance
                scenario_data = self.master_data[self.master_data['scenario_id'] == scenario]
                if len(scenario_data) > 100:  # Sufficient data for stationarity tests
                    for metric in test_metrics:
                        if metric in scenario_data.columns:
                            data = scenario_data[metric].dropna().values
                            if len(data) > 100:
                                try:
                                    adf_result = adfuller(data)
                                    kpss_result = kpss(data)
                                    stationarity_results[f"{scenario}_{metric}"] = {
                                        'adf': adf_result,
                                        'kpss': kpss_result
                                    }
                                except Exception as e:
                                    logger.warning(f"Stationarity test failed for {scenario}_{metric}: {e}")
            
            self.statistical_tests['stationarity'] = stationarity_results
            
            # 3. Correlation analysis
            correlation_matrices = {}
            for policy in self.config.policies:
                policy_data = self.master_data[self.master_data['policy'] == policy]
                if not policy_data.empty:
                    numeric_cols = policy_data.select_dtypes(include=[np.number]).columns
                    correlation_matrices[policy] = policy_data[numeric_cols].corr()
            
            self.statistical_tests['correlation'] = correlation_matrices
            
            logger.info("Statistical analysis completed successfully")
            
        except Exception as e:
            logger.error(f"Statistical analysis failed: {str(e)}")
            raise
    
    def _perform_temporal_analysis(self) -> None:
        """Perform comprehensive temporal analysis"""
        logger.info("Performing temporal analysis...")
        
        try:
            self.analysis_results['temporal'] = {}
            
            # Calculate rolling statistics
            window_sizes = [50, 100, 200]
            for window in window_sizes:
                for scenario in self.master_data['scenario_id'].unique():
                    scenario_data = self.master_data[self.master_data['scenario_id'] == scenario].copy()
                    if len(scenario_data) > window:
                        for metric in [self.config.col_agg_ew, 'queue_imbalance']:
                            if metric in scenario_data.columns:
                                scenario_data[f'{metric}_rolling_mean_{window}'] = (
                                    scenario_data[metric].rolling(window=window).mean()
                                )
                                scenario_data[f'{metric}_rolling_std_{window}'] = (
                                    scenario_data[metric].rolling(window=window).std()
                                )
            
            self.analysis_results['temporal']['rolling_stats'] = {
                'window_sizes': window_sizes,
                'metrics_analyzed': [self.config.col_agg_ew, 'queue_imbalance']
            }
            
            logger.info("Temporal analysis completed successfully")
            
        except Exception as e:
            logger.error(f"Temporal analysis failed: {str(e)}")
            raise
    
    def _perform_spectral_analysis(self) -> None:
        """Perform spectral analysis using FFT and related techniques"""
        logger.info("Performing spectral analysis...")
        
        try:
            self.analysis_results['spectral'] = {}
            
            spectral_results = {}
            high_load_data = self.master_data[self.master_data['rho'] == '0.999']
            
            for policy in self.config.policies:
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if policy_data.empty:
                    continue
                
                spectral_results[policy] = {}
                
                for queue_col in self.config.col_queues:
                    if queue_col in policy_data.columns:
                        data = policy_data[queue_col].values
                        
                        # Remove any NaN values
                        data = data[~np.isnan(data)]
                        
                        if len(data) > self.config.spectral_analysis['nperseg']:
                            # FFT Analysis
                            fft_vals = np.abs(fft.fft(data))
                            freqs = fft.fftfreq(len(data))
                            
                            # Power Spectral Density
                            f, Pxx = welch(data, nperseg=self.config.spectral_analysis['nperseg'])
                            
                            spectral_results[policy][queue_col] = {
                                'fft_magnitude': fft_vals,
                                'frequencies': freqs,
                                'psd_frequencies': f,
                                'psd': Pxx,
                                'dominant_frequency': f[np.argmax(Pxx)],
                                'total_power': np.sum(Pxx)
                            }
            
            self.analysis_results['spectral'] = spectral_results
            logger.info("Spectral analysis completed successfully")
            
        except Exception as e:
            logger.error(f"Spectral analysis failed: {str(e)}")
            raise
    
    def _perform_ml_analysis(self) -> None:
        """Perform comprehensive machine learning analysis"""
        logger.info("Performing machine learning analysis...")
        
        try:
            self.analysis_results['ml'] = {}
            
            # Prepare data for ML analysis
            high_load_data = self.master_data[self.master_data['rho'] == '0.999']
            
            if high_load_data.empty:
                logger.warning("No high-load data available for ML analysis")
                return
            
            # Feature set for ML
            ml_features = (
                self.config.col_queues + 
                ['queue_imbalance', 'queue_spread', 'total_queues', 'queue_mean', 'queue_cv']
            )
            
            ml_data = high_load_data[ml_features + ['policy']].dropna()
            
            if ml_data.empty:
                logger.warning("No valid data for ML analysis after preprocessing")
                return
            
            X = ml_data[ml_features]
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            self.analysis_results['ml']['scaler'] = scaler
            self.analysis_results['ml']['feature_names'] = ml_features
            
            # 1. Dimensionality Reduction
            self._perform_dimensionality_reduction(X_scaled, ml_data)
            
            # 2. Clustering Analysis
            self._perform_clustering_analysis(X_scaled, ml_data)
            
            # 3. Anomaly Detection
            self._perform_anomaly_detection(X_scaled, ml_data)
            
            # 4. Feature Importance Analysis
            self._perform_feature_importance_analysis(high_load_data)
            
            logger.info("Machine learning analysis completed successfully")
            
        except Exception as e:
            logger.error(f"Machine learning analysis failed: {str(e)}")
            raise
    
    def _perform_dimensionality_reduction(self, X_scaled: np.ndarray, metadata: pd.DataFrame) -> None:
        """Perform various dimensionality reduction techniques"""
        
        # PCA
        pca = PCA(n_components=2, random_state=42)
        X_pca = pca.fit_transform(X_scaled)
        self.analysis_results['ml']['pca'] = {
            'components': X_pca,
            'explained_variance': pca.explained_variance_ratio_,
            'model': pca
        }
        
        # t-SNE
        tsne = TSNE(n_components=2, random_state=42, perplexity=30)
        X_tsne = tsne.fit_transform(X_scaled)
        self.analysis_results['ml']['tsne'] = {
            'components': X_tsne,
            'model': tsne
        }
        
        # ICA
        ica = FastICA(n_components=2, random_state=42, max_iter=1000)
        X_ica = ica.fit_transform(X_scaled)
        self.analysis_results['ml']['ica'] = {
            'components': X_ica,
            'model': ica
        }
    
    def _perform_clustering_analysis(self, X_scaled: np.ndarray, metadata: pd.DataFrame) -> None:
        """Perform comprehensive clustering analysis"""
        
        clustering_results = {}
        
        # GMM Clustering
        best_gmm_score = -1
        best_gmm = None
        
        for n_components in self.config.clustering['n_clusters_range']:
            gmm = GaussianMixture(
                n_components=n_components, 
                random_state=self.config.clustering['random_state'],
                n_init=10
            )
            clusters = gmm.fit_predict(X_scaled)
            
            if len(np.unique(clusters)) > 1:
                silhouette_avg = silhouette_score(X_scaled, clusters)
                if silhouette_avg > best_gmm_score:
                    best_gmm_score = silhouette_avg
                    best_gmm = gmm
        
        if best_gmm is not None:
            gmm_clusters = best_gmm.predict(X_scaled)
            clustering_results['gmm'] = {
                'clusters': gmm_clusters,
                'silhouette_score': best_gmm_score,
                'n_components': best_gmm.n_components,
                'model': best_gmm
            }
        
        # DBSCAN Clustering
        dbscan = DBSCAN(eps=0.5, min_samples=10)
        dbscan_clusters = dbscan.fit_predict(X_scaled)
        if len(np.unique(dbscan_clusters)) > 1:
            clustering_results['dbscan'] = {
                'clusters': dbscan_clusters,
                'n_clusters': len(np.unique(dbscan_clusters[dbscan_clusters != -1])),
                'n_noise': np.sum(dbscan_clusters == -1)
            }
        
        self.analysis_results['ml']['clustering'] = clustering_results
    
    def _perform_anomaly_detection(self, X_scaled: np.ndarray, metadata: pd.DataFrame) -> None:
        """Perform comprehensive anomaly detection"""
        
        anomaly_results = {}
        
        # Isolation Forest
        iso_forest = IsolationForest(
            contamination=0.1, 
            random_state=42,
            n_estimators=100
        )
        iso_predictions = iso_forest.fit_predict(X_scaled)
        anomaly_results['isolation_forest'] = {
            'predictions': iso_predictions,
            'anomaly_indices': np.where(iso_predictions == -1)[0],
            'model': iso_forest
        }
        
        # Statistical anomaly detection (Z-score based)
        z_scores = np.abs(stats.zscore(X_scaled, axis=0))
        statistical_anomalies = np.any(z_scores > 3, axis=1)
        anomaly_results['statistical'] = {
            'z_scores': z_scores,
            'anomaly_indices': np.where(statistical_anomalies)[0],
            'threshold': 3
        }
        
        self.analysis_results['ml']['anomaly_detection'] = anomaly_results
    
    def _perform_feature_importance_analysis(self, data: pd.DataFrame) -> None:
        """Analyze feature importance using multiple methods"""
        
        feature_importance = {}
        
        # Mutual Information
        X = data[self.config.col_queues + ['queue_imbalance', 'queue_spread', 'total_queues']]
        y = data[self.config.col_agg_ew]
        
        valid_indices = ~(X.isnull().any(axis=1) | y.isnull())
        X_valid = X[valid_indices]
        y_valid = y[valid_indices]
        
        if len(X_valid) > 0 and len(y_valid) > 0:
            mi_scores = mutual_info_regression(X_valid, y_valid, random_state=42)
            feature_importance['mutual_information'] = dict(zip(X.columns, mi_scores))
        
        # Random Forest Feature Importance
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(X_valid, y_valid)
        feature_importance['random_forest'] = dict(zip(X.columns, rf.feature_importances_))
        
        self.analysis_results['ml']['feature_importance'] = feature_importance
    
    def _perform_comparative_analysis(self) -> None:
        """Perform cross-policy and cross-scenario comparative analysis"""
        logger.info("Performing comparative analysis...")
        
        try:
            self.analysis_results['comparative'] = {}
            
            # Performance metrics by policy and rho
            performance_metrics = {}
            
            for policy in self.config.policies:
                policy_data = self.master_data[self.master_data['policy'] == policy]
                performance_metrics[policy] = {}
                
                for rho in self.config.rhos:
                    rho_data = policy_data[policy_data['rho'] == rho]
                    if not rho_data.empty:
                        performance_metrics[policy][rho] = {
                            'mean_waiting_time': rho_data[self.config.col_agg_ew].mean(),
                            'std_waiting_time': rho_data[self.config.col_agg_ew].std(),
                            'mean_queue_imbalance': rho_data['queue_imbalance'].mean(),
                            'std_queue_imbalance': rho_data['queue_imbalance'].std(),
                            'throughput': rho_data[self.config.col_arrival_rate].mean() * (1 - float(rho)),
                            'sample_size': len(rho_data)
                        }
            
            self.analysis_results['comparative']['performance_metrics'] = performance_metrics
            
            # Statistical significance testing
            significance_tests = {}
            
            # Compare policies at high load
            high_load_data = self.master_data[self.master_data['rho'] == '0.999']
            for metric in [self.config.col_agg_ew, 'queue_imbalance']:
                if metric in high_load_data.columns:
                    groups = [high_load_data[high_load_data['policy'] == policy][metric].dropna() 
                             for policy in self.config.policies if len(high_load_data[high_load_data['policy'] == policy]) > 0]
                    
                    if len(groups) >= 2:
                        # ANOVA test
                        f_stat, p_value = stats.f_oneway(*groups)
                        significance_tests[f'anova_{metric}'] = {
                            'f_statistic': f_stat,
                            'p_value': p_value,
                            'significant': p_value < 0.05
                        }
            
            self.analysis_results['comparative']['significance_tests'] = significance_tests
            
            logger.info("Comparative analysis completed successfully")
            
        except Exception as e:
            logger.error(f"Comparative analysis failed: {str(e)}")
            raise
    
    def _generate_analysis_report(self) -> None:
        """Generate comprehensive analysis report"""
        logger.info("Generating analysis report...")
        
        try:
            report_content = []
            report_content.append("COMPREHENSIVE QUEUEING SYSTEM ANALYSIS REPORT")
            report_content.append("=" * 60)
            report_content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_content.append(f"Total scenarios analyzed: {len(self.master_data['scenario_id'].unique())}")
            report_content.append(f"Total data points: {len(self.master_data)}")
            report_content.append("")
            
            # Summary statistics
            report_content.append("SUMMARY STATISTICS")
            report_content.append("-" * 40)
            
            for policy in self.config.policies:
                policy_data = self.master_data[self.master_data['policy'] == policy]
                if not policy_data.empty:
                    report_content.append(f"\nPolicy: {policy}")
                    report_content.append(f"  Scenarios: {policy_data['scenario_id'].nunique()}")
                    report_content.append(f"  Average E[W]: {policy_data[self.config.col_agg_ew].mean():.3f}")
                    report_content.append(f"  Average queue imbalance: {policy_data['queue_imbalance'].mean():.3f}")
            
            # Save report
            report_path = self.config.output_directory / "analysis_report.txt"
            with open(report_path, 'w') as f:
                f.write('\n'.join(report_content))
            
            logger.info(f"Analysis report saved to: {report_path}")
            
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            raise
    
    def _create_all_visualizations(self) -> None:
        """Create all comprehensive visualizations"""
        logger.info("Creating comprehensive visualizations...")
        
        try:
            # 1. Temporal Analysis Plots
            self._create_temporal_visualizations()
            
            # 2. Spectral Analysis Plots
            self._create_spectral_visualizations()
            
            # 3. Statistical Analysis Plots
            self._create_statistical_visualizations()
            
            # 4. Machine Learning Plots
            self._create_ml_visualizations()
            
            # 5. Comparative Analysis Plots
            self._create_comparative_visualizations()
            
            # 6. Advanced Analysis Plots
            self._create_advanced_visualizations()
            
            logger.info("All visualizations created successfully")
            
        except Exception as e:
            logger.error(f"Visualization creation failed: {str(e)}")
            raise
    
    def _create_temporal_visualizations(self) -> None:
        """Create temporal analysis visualizations"""
        
        # 1. Time Series of Queue Sizes
        self._plot_queue_timeseries()
        
        # 2. Rolling Statistics
        self._plot_rolling_statistics()
        
        # 3. Temporal Heatmaps
        self._plot_temporal_heatmaps()
        
        # 4. Phase Space Diagrams
        self._plot_phase_diagrams()
        
        # 5. Transient vs Steady State Analysis
        self._plot_transient_analysis()
    
    def _create_spectral_visualizations(self) -> None:
        """Create spectral analysis visualizations"""
        
        # 6. FFT Analysis
        self._plot_fft_analysis()
        
        # 7. Power Spectral Density
        self._plot_power_spectral_density()
        
        # 8. Spectrograms
        self._plot_spectrograms()
        
        # 9. Frequency Domain Comparison
        self._plot_frequency_comparison()
    
    def _create_statistical_visualizations(self) -> None:
        """Create statistical analysis visualizations"""
        
        # 10. Distribution Analysis
        self._plot_distribution_analysis()
        
        # 11. Correlation Matrices
        self._plot_correlation_matrices()
        
        # 12. Box Plots
        self._plot_box_whisker()
        
        # 13. Q-Q Plots
        self._plot_qq_plots()
        
        # 14. Violin Plots
        self._plot_violin_plots()
    
    def _create_ml_visualizations(self) -> None:
        """Create machine learning visualizations"""
        
        # 15. Dimensionality Reduction
        self._plot_dimensionality_reduction()
        
        # 16. Clustering Results
        self._plot_clustering_results()
        
        # 17. Anomaly Detection
        self._plot_anomaly_detection()
        
        # 18. Feature Importance
        self._plot_feature_importance()
    
    def _create_comparative_visualizations(self) -> None:
        """Create comparative analysis visualizations"""
        
        # 19. Performance Comparison
        self._plot_performance_comparison()
        
        # 20. Radar Charts
        self._plot_radar_charts()
        
        # 21. Parallel Coordinates
        self._plot_parallel_coordinates()
    
    def _create_advanced_visualizations(self) -> None:
        """Create advanced specialized visualizations"""
        
        # 22. 3D Trajectory Plots
        self._plot_3d_trajectories()
        
        # 23. Network Graphs
        self._plot_network_graphs()
        
        # 24. Interactive-style Static Plots
        self._plot_interactive_style()
        
        # 25. Summary Dashboard
        self._plot_summary_dashboard()

    # =========================================================================
    # VISUALIZATION METHODS (25+ different plot types)
    # =========================================================================

    def _plot_queue_timeseries(self) -> None:
        """Plot detailed time series of queue sizes"""
        try:
            high_load_data = self.master_data[self.master_data['rho'] == '0.999']
            
            for policy in self.config.policies:
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if policy_data.empty:
                    continue
                
                fig, axes = plt.subplots(2, 2, figsize=self.vis_config.figsize_large)
                axes = axes.flatten()
                
                # Plot individual queues
                for i, queue_col in enumerate(self.config.col_queues):
                    if i < len(axes) - 1:
                        axes[i].plot(policy_data[self.config.col_timestamp], 
                                   policy_data[queue_col],
                                   color=self.vis_config.palette[f'queue{i+1}'],
                                   linewidth=1, alpha=0.8)
                        axes[i].set_title(f'{policy} - {queue_col}')
                        axes[i].set_xlabel('Time')
                        axes[i].set_ylabel('Queue Size')
                        axes[i].grid(True, alpha=0.3)
                
                # Plot all queues together
                for i, queue_col in enumerate(self.config.col_queues):
                    axes[-1].plot(policy_data[self.config.col_timestamp], 
                                policy_data[queue_col],
                                color=self.vis_config.palette[f'queue{i+1}'],
                                linewidth=1, alpha=0.7, label=f'Queue {i+1}')
                
                axes[-1].set_title(f'{policy} - All Queues')
                axes[-1].set_xlabel('Time')
                axes[-1].set_ylabel('Queue Size')
                axes[-1].legend()
                axes[-1].grid(True, alpha=0.3)
                
                plt.tight_layout()
                self._save_plot(fig, f"1_timeseries_{policy}.png")
                
        except Exception as e:
            logger.error(f"Queue timeseries plot failed: {str(e)}")

    def _plot_rolling_statistics(self) -> None:
        """Plot rolling mean and standard deviation"""
        try:
            high_load_data = self.master_data[self.master_data['rho'] == '0.999']
            
            fig, axes = plt.subplots(2, 2, figsize=self.vis_config.figsize_large)
            
            for i, policy in enumerate(self.config.policies):
                if i >= 4:  # Limit to 4 subplots
                    break
                    
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if policy_data.empty:
                    continue
                
                row, col = i // 2, i % 2
                ax = axes[row, col]
                
                # Calculate rolling statistics
                window = 100
                if len(policy_data) > window:
                    rolling_mean = policy_data[self.config.col_agg_ew].rolling(window=window).mean()
                    rolling_std = policy_data[self.config.col_agg_ew].rolling(window=window).std()
                    
                    ax.plot(policy_data[self.config.col_timestamp], rolling_mean, 
                           label='Rolling Mean', color='blue', linewidth=2)
                    ax.fill_between(policy_data[self.config.col_timestamp],
                                  rolling_mean - rolling_std,
                                  rolling_mean + rolling_std,
                                  alpha=0.3, color='blue', label='±1 STD')
                
                ax.set_title(f'{policy} - Rolling Statistics (Window={window})')
                ax.set_xlabel('Time')
                ax.set_ylabel('E[W]')
                ax.legend()
                ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            self._save_plot(fig, "2_rolling_statistics.png")
            
        except Exception as e:
            logger.error(f"Rolling statistics plot failed: {str(e)}")

    def _plot_temporal_heatmaps(self) -> None:
        """Create heatmaps of temporal evolution"""
        try:
            high_load_data = self.master_data[self.master_data['rho'] == '0.999']
            
            fig, axes = plt.subplots(1, 3, figsize=(18, 6))
            
            for i, policy in enumerate(self.config.policies):
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if policy_data.empty:
                    continue
                
                # Create matrix of queue sizes over time
                queue_matrix = policy_data[self.config.col_queues].values.T
                
                im = axes[i].imshow(queue_matrix, aspect='auto', cmap='viridis',
                                  extent=[0, 1, 0, 3])
                axes[i].set_title(f'{policy} - Queue Evolution')
                axes[i].set_xlabel('Normalized Time')
                axes[i].set_ylabel('Queue')
                axes[i].set_yticks([0.5, 1.5, 2.5])
                axes[i].set_yticklabels(['Q1', 'Q2', 'Q3'])
                
                plt.colorbar(im, ax=axes[i], label='Queue Size')
            
            plt.tight_layout()
            self._save_plot(fig, "3_temporal_heatmaps.png")
            
        except Exception as e:
            logger.error(f"Temporal heatmaps plot failed: {str(e)}")

    def _plot_phase_diagrams(self) -> None:
        """Create phase space diagrams"""
        try:
            high_load_data = self.master_data[self.master_data['rho'] == '0.999']
            
            fig, axes = plt.subplots(2, 3, figsize=(18, 12))
            
            phase_pairs = [
                ('queueSize1', 'queueSize2', 'Q1 vs Q2'),
                ('queueSize1', 'queueSize3', 'Q1 vs Q3'), 
                ('queueSize2', 'queueSize3', 'Q2 vs Q3'),
                ('queue_imbalance', 'total_queues', 'Imbalance vs Total'),
                (self.config.col_agg_en, self.config.col_agg_ew, 'E[N] vs E[W]'),
                ('queue_spread', 'queue_imbalance', 'Spread vs Imbalance')
            ]
            
            for i, (x_col, y_col, title) in enumerate(phase_pairs):
                row, col = i // 3, i % 3
                ax = axes[row, col]
                
                for policy in self.config.policies:
                    policy_data = high_load_data[high_load_data['policy'] == policy]
                    if not policy_data.empty:
                        # Sample for clarity
                        sample_data = policy_data.iloc[::10]
                        ax.scatter(sample_data[x_col], sample_data[y_col],
                                 alpha=0.6, s=10, label=policy,
                                 color=self.vis_config.palette[policy])
                
                ax.set_title(title, fontweight='bold')
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                ax.legend()
                ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            self._save_plot(fig, "4_phase_diagrams.png")
            
        except Exception as e:
            logger.error(f"Phase diagrams plot failed: {str(e)}")

    def _plot_transient_analysis(self) -> None:
        """Analyze transient vs steady-state behavior"""
        try:
            fig, axes = plt.subplots(3, 2, figsize=(15, 12))
            
            for policy_idx, policy in enumerate(self.config.policies):
                policy_data = self.master_data[self.master_data['policy'] == policy]
                if policy_data.empty:
                    continue
                    
                for rho_idx, rho in enumerate(['0.800', '0.999']):
                    rho_data = policy_data[policy_data['rho'] == rho]
                    if rho_data.empty:
                        continue
                        
                    # Split into transient and steady-state
                    transient_cut = int(0.3 * len(rho_data))
                    transient_data = rho_data.iloc[:transient_cut]
                    steady_data = rho_data.iloc[transient_cut:]
                    
                    ax = axes[policy_idx, rho_idx]
                    
                    # Plot both phases
                    if not transient_data.empty:
                        ax.plot(transient_data[self.config.col_timestamp],
                               transient_data[self.config.col_agg_ew],
                               color='red', alpha=0.7, linewidth=2,
                               label='Transient')
                    
                    if not steady_data.empty:
                        ax.plot(steady_data[self.config.col_timestamp],
                               steady_data[self.config.col_agg_ew],
                               color='blue', alpha=0.7, linewidth=2,
                               label='Steady-State')
                    
                    ax.set_title(f'{policy} - ρ={rho}', fontweight='bold')
                    ax.set_ylabel('E[W]')
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    
                    if policy_idx == 2:
                        ax.set_xlabel('Time')
            
            plt.tight_layout()
            self._save_plot(fig, "5_transient_analysis.png")
            
        except Exception as e:
            logger.error(f"Transient analysis plot failed: {str(e)}")

    def _plot_fft_analysis(self) -> None:
        """Plot FFT analysis results"""
        try:
            if 'spectral' not in self.analysis_results:
                return
                
            spectral_data = self.analysis_results['spectral']
            
            fig, axes = plt.subplots(3, 1, figsize=(12, 15))
            
            for i, policy in enumerate(self.config.policies):
                if policy not in spectral_data:
                    continue
                    
                ax = axes[i]
                
                for queue_name in self.config.col_queues:
                    if queue_name in spectral_data[policy]:
                        queue_data = spectral_data[policy][queue_name]
                        freqs = queue_data['frequencies']
                        fft_mag = queue_data['fft_magnitude']
                        
                        # Plot only positive frequencies
                        positive_idx = freqs > 0
                        ax.semilogy(freqs[positive_idx], fft_mag[positive_idx],
                                  label=queue_name, alpha=0.7, linewidth=2)
                
                ax.set_title(f'{policy} - FFT Analysis')
                ax.set_xlabel('Frequency')
                ax.set_ylabel('Magnitude (log)')
                ax.legend()
                ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            self._save_plot(fig, "6_fft_analysis.png")
            
        except Exception as e:
            logger.error(f"FFT analysis plot failed: {str(e)}")

    def _plot_power_spectral_density(self) -> None:
        """Plot power spectral density"""
        try:
            if 'spectral' not in self.analysis_results:
                return
                
            spectral_data = self.analysis_results['spectral']
            
            fig, axes = plt.subplots(3, 1, figsize=(12, 15))
            
            for i, policy in enumerate(self.config.policies):
                if policy not in spectral_data:
                    continue
                    
                ax = axes[i]
                
                for queue_name in self.config.col_queues:
                    if queue_name in spectral_data[policy]:
                        queue_data = spectral_data[policy][queue_name]
                        f = queue_data['psd_frequencies']
                        Pxx = queue_data['psd']
                        
                        ax.semilogy(f, Pxx, label=queue_name, alpha=0.7, linewidth=2)
                
                ax.set_title(f'{policy} - Power Spectral Density')
                ax.set_xlabel('Frequency [Hz]')
                ax.set_ylabel('Power/Frequency [dB/Hz]')
                ax.legend()
                ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            self._save_plot(fig, "7_power_spectral_density.png")
            
        except Exception as e:
            logger.error(f"PSD plot failed: {str(e)}")

    def _plot_spectrograms(self) -> None:
        """Create spectrograms for queue time series"""
        try:
            high_load_data = self.master_data[self.master_data['rho'] == '0.999']
            
            fig, axes = plt.subplots(3, 3, figsize=(18, 12))
            
            for policy_idx, policy in enumerate(self.config.policies):
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if policy_data.empty:
                    continue
                    
                for queue_idx, queue_col in enumerate(self.config.col_queues):
                    ax = axes[policy_idx, queue_idx]
                    queue_data = policy_data[queue_col].values
                    
                    # Calculate spectrogram
                    f, t, Sxx = spectrogram(queue_data, fs=1.0, 
                                          nperseg=min(256, len(queue_data)//4))
                    
                    im = ax.pcolormesh(t, f, 10 * np.log10(Sxx), 
                                     shading='gouraud', cmap='viridis')
                    ax.set_title(f'{policy} - {queue_col}')
                    ax.set_ylabel('Frequency [Hz]')
                    ax.set_xlabel('Time [s]')
                    
                    plt.colorbar(im, ax=ax, label='Power [dB]')
            
            plt.tight_layout()
            self._save_plot(fig, "8_spectrograms.png")
            
        except Exception as e:
            logger.error(f"Spectrograms plot failed: {str(e)}")

    def _plot_frequency_comparison(self) -> None:
        """Compare frequency domain characteristics"""
        try:
            if 'spectral' not in self.analysis_results:
                return
                
            spectral_data = self.analysis_results['spectral']
            
            fig, axes = plt.subplots(1, 2, figsize=(15, 6))
            
            # Plot dominant frequencies
            dominant_freqs = {}
            for policy in self.config.policies:
                if policy in spectral_data:
                    freqs = []
                    for queue in self.config.col_queues:
                        if queue in spectral_data[policy]:
                            freqs.append(spectral_data[policy][queue]['dominant_frequency'])
                    if freqs:
                        dominant_freqs[policy] = freqs
            
            # Box plot of dominant frequencies
            if dominant_freqs:
                axes[0].boxplot(dominant_freqs.values(), labels=dominant_freqs.keys())
                axes[0].set_title('Distribution of Dominant Frequencies')
                axes[0].set_ylabel('Dominant Frequency [Hz]')
                axes[0].grid(True, alpha=0.3)
            
            # Total power comparison
            total_power = {}
            for policy in self.config.policies:
                if policy in spectral_data:
                    power = []
                    for queue in self.config.col_queues:
                        if queue in spectral_data[policy]:
                            power.append(spectral_data[policy][queue]['total_power'])
                    if power:
                        total_power[policy] = power
            
            if total_power:
                axes[1].boxplot(total_power.values(), labels=total_power.keys())
                axes[1].set_title('Distribution of Total Power')
                axes[1].set_ylabel('Total Power')
                axes[1].grid(True, alpha=0.3)
            
            plt.tight_layout()
            self._save_plot(fig, "9_frequency_comparison.png")
            
        except Exception as e:
            logger.error(f"Frequency comparison plot failed: {str(e)}")

    def _plot_distribution_analysis(self) -> None:
        """Analyze distributions of key metrics"""
        try:
            high_load_data = self.master_data[self.master_data['rho'] == '0.999']
            
            metrics = [self.config.col_agg_ew, 'queue_imbalance', 'total_queues']
            
            fig, axes = plt.subplots(3, 3, figsize=(15, 12))
            
            for i, metric in enumerate(metrics):
                for j, policy in enumerate(self.config.policies):
                    policy_data = high_load_data[high_load_data['policy'] == policy]
                    if policy_data.empty:
                        continue
                        
                    ax = axes[i, j]
                    data = policy_data[metric].dropna()
                    
                    # Histogram with KDE
                    sns.histplot(data, ax=ax, kde=True, 
                               color=self.vis_config.palette[policy], alpha=0.7)
                    
                    ax.set_title(f'{policy} - {metric}')
                    ax.set_xlabel(metric)
                    ax.set_ylabel('Frequency')
                    ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            self._save_plot(fig, "10_distribution_analysis.png")
            
        except Exception as e:
            logger.error(f"Distribution analysis plot failed: {str(e)}")

    def _plot_correlation_matrices(self) -> None:
        """Plot correlation matrices for each policy"""
        try:
            high_load_data = self.master_data[self.master_data['rho'] == '0.999']
            
            fig, axes = plt.subplots(1, 3, figsize=(18, 6))
            
            for i, policy in enumerate(self.config.policies):
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if policy_data.empty:
                    continue
                
                # Select numeric columns for correlation
                numeric_cols = policy_data.select_dtypes(include=[np.number]).columns
                corr_matrix = policy_data[numeric_cols].corr()
                
                # Plot heatmap
                sns.heatmap(corr_matrix, ax=axes[i], cmap='coolwarm', center=0,
                          annot=True, fmt='.2f', square=True)
                axes[i].set_title(f'{policy} - Correlation Matrix')
            
            plt.tight_layout()
            self._save_plot(fig, "11_correlation_matrices.png")
            
        except Exception as e:
            logger.error(f"Correlation matrices plot failed: {str(e)}")

    def _plot_box_whisker(self) -> None:
        """Create box and whisker plots"""
        try:
            high_load_data = self.master_data[self.master_data['rho'] == '0.999']
            
            metrics = [self.config.col_agg_ew, 'queue_imbalance', 'total_queues']
            
            fig, axes = plt.subplots(1, 3, figsize=(15, 6))
            
            for i, metric in enumerate(metrics):
                data_to_plot = []
                labels = []
                
                for policy in self.config.policies:
                    policy_data = high_load_data[high_load_data['policy'] == policy]
                    if not policy_data.empty and metric in policy_data.columns:
                        data_to_plot.append(policy_data[metric].dropna().values)
                        labels.append(policy)
                
                if data_to_plot:
                    axes[i].boxplot(data_to_plot, labels=labels)
                    axes[i].set_title(f'Box Plot - {metric}')
                    axes[i].set_ylabel(metric)
                    axes[i].grid(True, alpha=0.3)
                    axes[i].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            self._save_plot(fig, "12_box_whisker.png")
            
        except Exception as e:
            logger.error(f"Box whisker plot failed: {str(e)}")

    def _plot_qq_plots(self) -> None:
        """Create Q-Q plots for normality assessment"""
        try:
            high_load_data = self.master_data[self.master_data['rho'] == '0.999']
            
            metrics = [self.config.col_agg_ew, 'queue_imbalance']
            
            fig, axes = plt.subplots(2, 3, figsize=(15, 10))
            
            for i, metric in enumerate(metrics):
                for j, policy in enumerate(self.config.policies):
                    policy_data = high_load_data[high_load_data['policy'] == policy]
                    if policy_data.empty:
                        continue
                        
                    ax = axes[i, j]
                    data = policy_data[metric].dropna()
                    
                    if len(data) > 0:
                        stats.probplot(data, dist="norm", plot=ax)
                        ax.set_title(f'{policy} - {metric} Q-Q Plot')
                        ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            self._save_plot(fig, "13_qq_plots.png")
            
        except Exception as e:
            logger.error(f"Q-Q plots failed: {str(e)}")

    def _plot_violin_plots(self) -> None:
        """Create violin plots for distribution visualization"""
        try:
            high_load_data = self.master_data[self.master_data['rho'] == '0.999']
            
            # Prepare data for violin plots
            plot_data = []
            for policy in self.config.policies:
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if not policy_data.empty:
                    for queue_col in self.config.col_queues:
                        if queue_col in policy_data.columns:
                            for value in policy_data[queue_col].dropna():
                                plot_data.append({
                                    'policy': policy,
                                    'queue': queue_col,
                                    'value': value
                                })
            
            if plot_data:
                df_plot = pd.DataFrame(plot_data)
                
                fig, ax = plt.subplots(figsize=(12, 8))
                sns.violinplot(data=df_plot, x='policy', y='value', hue='queue',
                             ax=ax, palette='pastel', split=True)
                
                ax.set_title('Queue Size Distributions by Policy')
                ax.set_xlabel('Policy')
                ax.set_ylabel('Queue Size')
                ax.legend(title='Queue')
                
                plt.tight_layout()
                self._save_plot(fig, "14_violin_plots.png")
            
        except Exception as e:
            logger.error(f"Violin plots failed: {str(e)}")

    def _plot_dimensionality_reduction(self) -> None:
        """Plot various dimensionality reduction techniques"""
        try:
            if 'ml' not in self.analysis_results or 'pca' not in self.analysis_results['ml']:
                return
                
            ml_results = self.analysis_results['ml']
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            
            # PCA
            if 'pca' in ml_results:
                pca_data = ml_results['pca']['components']
                explained_var = ml_results['pca']['explained_variance']
                
                scatter = axes[0, 0].scatter(pca_data[:, 0], pca_data[:, 1], 
                                           alpha=0.6, s=20, cmap='viridis')
                axes[0, 0].set_title(f'PCA (Variance: {explained_var.sum():.2%})')
                axes[0, 0].set_xlabel(f'PC1 ({explained_var[0]:.2%})')
                axes[0, 0].set_ylabel(f'PC2 ({explained_var[1]:.2%})')
                axes[0, 0].grid(True, alpha=0.3)
            
            # t-SNE
            if 'tsne' in ml_results:
                tsne_data = ml_results['tsne']['components']
                axes[0, 1].scatter(tsne_data[:, 0], tsne_data[:, 1], 
                                 alpha=0.6, s=20, cmap='viridis')
                axes[0, 1].set_title('t-SNE Visualization')
                axes[0, 1].set_xlabel('t-SNE 1')
                axes[0, 1].set_ylabel('t-SNE 2')
                axes[0, 1].grid(True, alpha=0.3)
            
            # ICA
            if 'ica' in ml_results:
                ica_data = ml_results['ica']['components']
                axes[1, 0].scatter(ica_data[:, 0], ica_data[:, 1], 
                                 alpha=0.6, s=20, cmap='viridis')
                axes[1, 0].set_title('Independent Component Analysis')
                axes[1, 0].set_xlabel('ICA 1')
                axes[1, 0].set_ylabel('ICA 2')
                axes[1, 0].grid(True, alpha=0.3)
            
            # Variance explained by PCA components
            if 'pca' in ml_results:
                explained_var = ml_results['pca']['explained_variance']
                cumulative_var = np.cumsum(explained_var)
                
                axes[1, 1].plot(range(1, len(explained_var) + 1), cumulative_var, 'bo-')
                axes[1, 1].set_title('PCA Cumulative Variance')
                axes[1, 1].set_xlabel('Number of Components')
                axes[1, 1].set_ylabel('Cumulative Variance')
                axes[1, 1].grid(True, alpha=0.3)
                axes[1, 1].set_ylim(0, 1)
            
            plt.tight_layout()
            self._save_plot(fig, "15_dimensionality_reduction.png")
            
        except Exception as e:
            logger.error(f"Dimensionality reduction plot failed: {str(e)}")

    def _plot_clustering_results(self) -> None:
        """Plot clustering analysis results"""
        try:
            if 'ml' not in self.analysis_results or 'clustering' not in self.analysis_results['ml']:
                return
                
            clustering_results = self.analysis_results['ml']['clustering']
            pca_data = self.analysis_results['ml']['pca']['components']
            
            n_clusters = len(clustering_results)
            if n_clusters == 0:
                return
                
            fig, axes = plt.subplots(1, n_clusters, figsize=(5 * n_clusters, 5))
            
            if n_clusters == 1:
                axes = [axes]
            
            for idx, (method, result) in enumerate(clustering_results.items()):
                if idx >= len(axes):
                    break
                    
                clusters = result['clusters']
                ax = axes[idx]
                
                scatter = ax.scatter(pca_data[:, 0], pca_data[:, 1], 
                                   c=clusters, cmap='Set1', alpha=0.6, s=20)
                ax.set_title(f'{method.upper()} Clustering')
                ax.set_xlabel('PC1')
                ax.set_ylabel('PC2')
                ax.grid(True, alpha=0.3)
                
                # Add colorbar
                plt.colorbar(scatter, ax=ax, label='Cluster')
            
            plt.tight_layout()
            self._save_plot(fig, "16_clustering_results.png")
            
        except Exception as e:
            logger.error(f"Clustering results plot failed: {str(e)}")

    def _plot_anomaly_detection(self) -> None:
        """Plot anomaly detection results"""
        try:
            if 'ml' not in self.analysis_results or 'anomaly_detection' not in self.analysis_results['ml']:
                return
                
            anomaly_results = self.analysis_results['ml']['anomaly_detection']
            pca_data = self.analysis_results['ml']['pca']['components']
            
            n_methods = len(anomaly_results)
            if n_methods == 0:
                return
                
            fig, axes = plt.subplots(1, n_methods, figsize=(5 * n_methods, 5))
            
            if n_methods == 1:
                axes = [axes]
            
            for idx, (method, result) in enumerate(anomaly_results.items()):
                if idx >= len(axes):
                    break
                    
                ax = axes[idx]
                anomaly_indices = result['anomaly_indices']
                normal_indices = np.setdiff1d(np.arange(len(pca_data)), anomaly_indices)
                
                # Plot normal points
                ax.scatter(pca_data[normal_indices, 0], pca_data[normal_indices, 1],
                         color='blue', alpha=0.6, s=20, label='Normal')
                
                # Plot anomalies
                if len(anomaly_indices) > 0:
                    ax.scatter(pca_data[anomaly_indices, 0], pca_data[anomaly_indices, 1],
                             color='red', alpha=0.8, s=50, marker='x', label='Anomaly')
                
                ax.set_title(f'{method.replace("_", " ").title()}')
                ax.set_xlabel('PC1')
                ax.set_ylabel('PC2')
                ax.legend()
                ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            self._save_plot(fig, "17_anomaly_detection.png")
            
        except Exception as e:
            logger.error(f"Anomaly detection plot failed: {str(e)}")

    def _plot_feature_importance(self) -> None:
        """Plot feature importance analysis"""
        try:
            if 'ml' not in self.analysis_results or 'feature_importance' not in self.analysis_results['ml']:
                return
                
            feature_importance = self.analysis_results['ml']['feature_importance']
            
            n_methods = len(feature_importance)
            if n_methods == 0:
                return
                
            fig, axes = plt.subplots(1, n_methods, figsize=(5 * n_methods, 6))
            
            if n_methods == 1:
                axes = [axes]
            
            for idx, (method, importance_dict) in enumerate(feature_importance.items()):
                if idx >= len(axes):
                    break
                    
                ax = axes[idx]
                
                # Sort features by importance
                sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
                features, importance = zip(*sorted_features)
                
                y_pos = np.arange(len(features))
                ax.barh(y_pos, importance, align='center', alpha=0.7)
                ax.set_yticks(y_pos)
                ax.set_yticklabels(features)
                ax.set_xlabel('Importance')
                ax.set_title(f'{method.replace("_", " ").title()}')
                ax.grid(True, alpha=0.3, axis='x')
            
            plt.tight_layout()
            self._save_plot(fig, "18_feature_importance.png")
            
        except Exception as e:
            logger.error(f"Feature importance plot failed: {str(e)}")

    def _plot_performance_comparison(self) -> None:
        """Create comprehensive performance comparison plots"""
        try:
            if 'comparative' not in self.analysis_results:
                return
                
            performance_metrics = self.analysis_results['comparative']['performance_metrics']
            
            # Create comparison plots for different metrics
            metrics_to_compare = ['mean_waiting_time', 'mean_queue_imbalance', 'throughput']
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            axes = axes.flatten()
            
            for i, metric in enumerate(metrics_to_compare):
                if i >= len(axes):
                    break
                    
                ax = axes[i]
                
                # Prepare data for plotting
                x_pos = np.arange(len(self.config.rhos))
                width = 0.25
                
                for j, policy in enumerate(self.config.policies):
                    if policy in performance_metrics:
                        metric_values = [performance_metrics[policy][rho][metric] 
                                       for rho in self.config.rhos 
                                       if rho in performance_metrics[policy]]
                        
                        if len(metric_values) == len(self.config.rhos):
                            ax.bar(x_pos + j * width, metric_values, width,
                                 label=policy, color=self.vis_config.palette[policy],
                                 alpha=0.8)
                
                ax.set_xlabel('System Occupancy (ρ)')
                ax.set_ylabel(metric.replace('_', ' ').title())
                ax.set_title(f'{metric.replace("_", " ").title()} Comparison')
                ax.set_xticks(x_pos + width)
                ax.set_xticklabels(self.config.rhos)
                ax.legend()
                ax.grid(True, alpha=0.3)
            
            # Add significance test results if available
            if 'significance_tests' in self.analysis_results['comparative']:
                significance_tests = self.analysis_results['comparative']['significance_tests']
                ax = axes[3]
                
                test_results = []
                test_names = []
                for test_name, test_result in significance_tests.items():
                    test_results.append(test_result['p_value'])
                    test_names.append(test_name.replace('_', ' ').title())
                
                if test_results:
                    ax.bar(range(len(test_results)), test_results, 
                          color=['red' if p < 0.05 else 'blue' for p in test_results])
                    ax.axhline(y=0.05, color='red', linestyle='--', label='Significance Threshold (0.05)')
                    ax.set_xticks(range(len(test_results)))
                    ax.set_xticklabels(test_names, rotation=45)
                    ax.set_ylabel('P-value')
                    ax.set_title('Statistical Significance Tests')
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    ax.set_yscale('log')
            
            plt.tight_layout()
            self._save_plot(fig, "19_performance_comparison.png")
            
        except Exception as e:
            logger.error(f"Performance comparison plot failed: {str(e)}")

    def _plot_radar_charts(self) -> None:
        """Create radar charts for multi-dimensional comparison"""
        try:
            if 'comparative' not in self.analysis_results:
                return
                
            performance_metrics = self.analysis_results['comparative']['performance_metrics']
            
            # Select metrics for radar chart
            radar_metrics = ['mean_waiting_time', 'mean_queue_imbalance', 'throughput']
            
            fig, axes = plt.subplots(2, 2, figsize=(12, 12), subplot_kw=dict(projection='polar'))
            axes = axes.flatten()
            
            for rho_idx, rho in enumerate(self.config.rhos):
                if rho_idx >= len(axes):
                    break
                    
                ax = axes[rho_idx]
                
                # Prepare data for this rho
                angles = np.linspace(0, 2 * np.pi, len(radar_metrics), endpoint=False).tolist()
                angles += angles[:1]  # Complete the circle
                
                for policy in self.config.policies:
                    if policy in performance_metrics and rho in performance_metrics[policy]:
                        values = [performance_metrics[policy][rho][metric] for metric in radar_metrics]
                        
                        # Normalize values for radar chart
                        max_vals = [max(performance_metrics[p][rho][metric] for p in self.config.policies 
                                      if p in performance_metrics and rho in performance_metrics[p])
                                  for metric in radar_metrics]
                        
                        normalized_values = [v / m if m > 0 else 0 for v, m in zip(values, max_vals)]
                        normalized_values += normalized_values[:1]  # Complete the circle
                        
                        ax.plot(angles, normalized_values, 'o-', linewidth=2, 
                              label=policy, color=self.vis_config.palette[policy])
                        ax.fill(angles, normalized_values, alpha=0.1, 
                              color=self.vis_config.palette[policy])
                
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels([m.replace('_', '\n') for m in radar_metrics])
                ax.set_title(f'Radar Chart - ρ={rho}', size=14, y=1.1)
                ax.grid(True)
                ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
            
            plt.tight_layout()
            self._save_plot(fig, "20_radar_charts.png")
            
        except Exception as e:
            logger.error(f"Radar charts plot failed: {str(e)}")

    def _plot_parallel_coordinates(self) -> None:
        """Create parallel coordinates plot"""
        try:
            # Prepare data for parallel coordinates
            plot_data = []
            
            for policy in self.config.policies:
                policy_data = self.master_data[self.master_data['policy'] == policy]
                if not policy_data.empty:
                    # Aggregate by scenario
                    for scenario in policy_data['scenario_id'].unique():
                        scenario_data = policy_data[policy_data['scenario_id'] == scenario]
                        if not scenario_data.empty:
                            plot_data.append({
                                'policy': policy,
                                'rho': scenario_data['rho'].iloc[0],
                                'mean_waiting_time': scenario_data[self.config.col_agg_ew].mean(),
                                'mean_imbalance': scenario_data['queue_imbalance'].mean(),
                                'total_throughput': scenario_data[self.config.col_arrival_rate].mean() * 
                                                  (1 - float(scenario_data['rho'].iloc[0])),
                                'queue_variability': scenario_data['queue_cv'].mean()
                            })
            
            if plot_data:
                df_plot = pd.DataFrame(plot_data)
                
                # Normalize data for parallel coordinates
                features = ['mean_waiting_time', 'mean_imbalance', 'total_throughput', 'queue_variability']
                df_normalized = df_plot.copy()
                
                for feature in features:
                    if feature in df_normalized.columns:
                        min_val = df_normalized[feature].min()
                        max_val = df_normalized[feature].max()
                        if max_val > min_val:
                            df_normalized[feature] = (df_normalized[feature] - min_val) / (max_val - min_val)
                
                fig, ax = plt.subplots(figsize=(12, 8))
                
                # Plot each policy with different colors
                for policy in self.config.policies:
                    policy_data = df_normalized[df_normalized['policy'] == policy]
                    if not policy_data.empty:
                        for i, row in policy_data.iterrows():
                            values = [row[feature] for feature in features]
                            ax.plot(range(len(features)), values, 
                                  color=self.vis_config.palette[policy], alpha=0.3, linewidth=1)
                
                ax.set_xticks(range(len(features)))
                ax.set_xticklabels([f.replace('_', '\n') for f in features])
                ax.set_ylabel('Normalized Value')
                ax.set_title('Parallel Coordinates Plot')
                ax.grid(True, alpha=0.3)
                
                # Create legend
                from matplotlib.lines import Line2D
                legend_elements = [Line2D([0], [0], color=self.vis_config.palette[policy], 
                                        lw=2, label=policy) for policy in self.config.policies]
                ax.legend(handles=legend_elements)
                
                plt.tight_layout()
                self._save_plot(fig, "21_parallel_coordinates.png")
            
        except Exception as e:
            logger.error(f"Parallel coordinates plot failed: {str(e)}")

    def _plot_3d_trajectories(self) -> None:
        """Create 3D trajectory plots"""
        try:
            high_load_data = self.master_data[self.master_data['rho'] == '0.999']
            
            fig = plt.figure(figsize=(15, 10))
            
            for i, policy in enumerate(self.config.policies):
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if policy_data.empty:
                    continue
                
                # Create 3D subplot
                ax = fig.add_subplot(2, 2, i+1, projection='3d')
                
                # Sample data for clarity
                sample_data = policy_data.iloc[::10]
                
                # Plot trajectory in 3D space of queues
                ax.plot(sample_data['queueSize1'], sample_data['queueSize2'], sample_data['queueSize3'],
                       color=self.vis_config.palette[policy], alpha=0.7, linewidth=1.5)
                
                # Mark start and end points
                if len(sample_data) > 0:
                    ax.scatter([sample_data['queueSize1'].iloc[0]], 
                             [sample_data['queueSize2'].iloc[0]],
                             [sample_data['queueSize3'].iloc[0]],
                             color='green', s=100, marker='o', label='Start')
                    ax.scatter([sample_data['queueSize1'].iloc[-1]], 
                             [sample_data['queueSize2'].iloc[-1]],
                             [sample_data['queueSize3'].iloc[-1]],
                             color='red', s=100, marker='s', label='End')
                
                ax.set_xlabel('Queue 1')
                ax.set_ylabel('Queue 2')
                ax.set_zlabel('Queue 3')
                ax.set_title(f'{policy} - 3D Trajectory')
                ax.legend()
            
            plt.tight_layout()
            self._save_plot(fig, "22_3d_trajectories.png")
            
        except Exception as e:
            logger.error(f"3D trajectories plot failed: {str(e)}")

    def _plot_network_graphs(self) -> None:
        """Create network-style visualization of queue relationships"""
        try:
            high_load_data = self.master_data[self.master_data['rho'] == '0.999']
            
            fig, axes = plt.subplots(1, 3, figsize=(18, 6))
            
            for i, policy in enumerate(self.config.policies):
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if policy_data.empty:
                    continue
                
                ax = axes[i]
                
                # Calculate correlations between queues
                corr_matrix = policy_data[self.config.col_queues].corr()
                
                # Create a simple network visualization
                n_queues = len(self.config.col_queues)
                positions = {
                    'queueSize1': (0, 1),
                    'queueSize2': (-0.866, -0.5),
                    'queueSize3': (0.866, -0.5)
                }
                
                # Plot nodes
                for queue, pos in positions.items():
                    ax.scatter(pos[0], pos[1], s=500, 
                             color=self.vis_config.palette[queue.replace('Size', '')],
                             alpha=0.7, label=queue)
                    ax.annotate(queue, xy=pos, xytext=(pos[0], pos[1] + 0.1),
                              ha='center', va='center', fontweight='bold')
                
                # Plot edges with thickness based on correlation
                queues = list(positions.keys())
                for i, q1 in enumerate(queues):
                    for j, q2 in enumerate(queues):
                        if i < j:  # Avoid duplicate edges
                            corr = corr_matrix.loc[q1, q2]
                            if abs(corr) > 0.1:  # Only plot significant correlations
                                pos1 = positions[q1]
                                pos2 = positions[q2]
                                
                                # Line properties based on correlation
                                linewidth = abs(corr) * 5
                                color = 'green' if corr > 0 else 'red'
                                alpha = abs(corr)
                                
                                ax.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]],
                                      color=color, linewidth=linewidth, alpha=alpha)
                                
                                # Add correlation value label
                                mid_x = (pos1[0] + pos2[0]) / 2
                                mid_y = (pos1[1] + pos2[1]) / 2
                                ax.annotate(f'{corr:.2f}', xy=(mid_x, mid_y),
                                          xytext=(mid_x, mid_y + 0.05),
                                          ha='center', va='center',
                                          fontsize=8, fontweight='bold')
                
                ax.set_xlim(-1.2, 1.2)
                ax.set_ylim(-0.8, 1.2)
                ax.set_aspect('equal')
                ax.set_title(f'{policy} - Queue Relationships')
                ax.axis('off')
            
            plt.tight_layout()
            self._save_plot(fig, "23_network_graphs.png")
            
        except Exception as e:
            logger.error(f"Network graphs plot failed: {str(e)}")

    def _plot_interactive_style(self) -> None:
        """Create interactive-style static plots with multiple layers of information"""
        try:
            high_load_data = self.master_data[self.master_data['rho'] == '0.999']
            
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # Plot 1: Time series with confidence intervals
            for policy in self.config.policies:
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if not policy_data.empty:
                    # Calculate rolling statistics
                    window = 50
                    if len(policy_data) > window:
                        rolling_mean = policy_data[self.config.col_agg_ew].rolling(window=window).mean()
                        rolling_std = policy_data[self.config.col_agg_ew].rolling(window=window).std()
                        
                        ax1.plot(policy_data[self.config.col_timestamp], rolling_mean,
                               label=policy, color=self.vis_config.palette[policy], linewidth=2)
                        ax1.fill_between(policy_data[self.config.col_timestamp],
                                       rolling_mean - rolling_std,
                                       rolling_mean + rolling_std,
                                       alpha=0.2, color=self.vis_config.palette[policy])
            
            ax1.set_title('Average Waiting Time with Confidence Intervals')
            ax1.set_xlabel('Time')
            ax1.set_ylabel('E[W]')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Plot 2: Scatter plot with marginal distributions
            for policy in self.config.policies:
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if not policy_data.empty:
                    sample_data = policy_data.iloc[::10]  # Sample for clarity
                    ax2.scatter(sample_data[self.config.col_agg_en], 
                              sample_data[self.config.col_agg_ew],
                              alpha=0.6, s=30, label=policy,
                              color=self.vis_config.palette[policy])
            
            ax2.set_title('E[N] vs E[W] Relationship')
            ax2.set_xlabel('E[N]')
            ax2.set_ylabel('E[W]')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # Plot 3: Stacked area chart of queue contributions
            time_normalized = np.linspace(0, 1, 100)
            for policy in self.config.policies:
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if not policy_data.empty:
                    # Resample to fixed number of points for area plot
                    from scipy.interpolate import interp1d
                    
                    original_time = np.linspace(0, 1, len(policy_data))
                    queue_data = []
                    
                    for queue_col in self.config.col_queues:
                        if queue_col in policy_data.columns:
                            f = interp1d(original_time, policy_data[queue_col].values, 
                                       kind='linear', fill_value='extrapolate')
                            queue_data.append(f(time_normalized))
                    
                    if queue_data:
                        queue_data = np.array(queue_data)
                        ax3.stackplot(time_normalized, queue_data,
                                    labels=[f'Queue {i+1}' for i in range(len(self.config.col_queues))],
                                    alpha=0.7)
            
            ax3.set_title('Queue Size Contributions Over Time')
            ax3.set_xlabel('Normalized Time')
            ax3.set_ylabel('Queue Size')
            ax3.legend(loc='upper left')
            ax3.grid(True, alpha=0.3)
            
            # Plot 4: Heatmap of policy performance across metrics
            performance_data = []
            metrics = ['mean_waiting_time', 'mean_imbalance', 'throughput', 'queue_variability']
            
            if 'comparative' in self.analysis_results:
                performance_metrics = self.analysis_results['comparative']['performance_metrics']
                
                for policy in self.config.policies:
                    if policy in performance_metrics and '0.999' in performance_metrics[policy]:
                        row_data = [performance_metrics[policy]['0.999'][metric] for metric in metrics]
                        performance_data.append(row_data)
                
                if performance_data:
                    im = ax4.imshow(performance_data, cmap='RdYlGn_r', aspect='auto')
                    ax4.set_xticks(range(len(metrics)))
                    ax4.set_xticklabels([m.replace('_', '\n') for m in metrics], rotation=45)
                    ax4.set_yticks(range(len(self.config.policies)))
                    ax4.set_yticklabels(self.config.policies)
                    ax4.set_title('Policy Performance Heatmap (ρ=0.999)')
                    
                    # Add value annotations
                    for i in range(len(self.config.policies)):
                        for j in range(len(metrics)):
                            text = ax4.text(j, i, f'{performance_data[i][j]:.2f}',
                                          ha="center", va="center", color="black", fontweight='bold')
                    
                    plt.colorbar(im, ax=ax4, label='Performance')
            
            plt.tight_layout()
            self._save_plot(fig, "24_interactive_style.png")
            
        except Exception as e:
            logger.error(f"Interactive-style plot failed: {str(e)}")

    def _plot_summary_dashboard(self) -> None:
        """Create a comprehensive summary dashboard"""
        try:
            fig = plt.figure(figsize=(20, 16))
            
            # Create a grid specification
            gs = fig.add_gridspec(4, 4)
            
            # Plot 1: Performance comparison (top left)
            ax1 = fig.add_subplot(gs[0, 0])
            high_load_data = self.master_data[self.master_data['rho'] == '0.999']
            
            performance_data = []
            for policy in self.config.policies:
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if not policy_data.empty:
                    performance_data.append(policy_data[self.config.col_agg_ew].mean())
            
            if performance_data:
                bars = ax1.bar(self.config.policies, performance_data, 
                             color=[self.vis_config.palette[p] for p in self.config.policies],
                             alpha=0.8)
                ax1.set_title('Average Waiting Time (ρ=0.999)')
                ax1.set_ylabel('E[W]')
                ax1.grid(True, alpha=0.3, axis='y')
                
                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    ax1.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.2f}', ha='center', va='bottom', fontweight='bold')
            
            # Plot 2: Queue imbalance comparison (top right)
            ax2 = fig.add_subplot(gs[0, 1])
            imbalance_data = []
            for policy in self.config.policies:
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if not policy_data.empty:
                    imbalance_data.append(policy_data['queue_imbalance'].mean())
            
            if imbalance_data:
                bars = ax2.bar(self.config.policies, imbalance_data,
                             color=[self.vis_config.palette[p] for p in self.config.policies],
                             alpha=0.8)
                ax2.set_title('Queue Imbalance (ρ=0.999)')
                ax2.set_ylabel('Imbalance (Std Dev)')
                ax2.grid(True, alpha=0.3, axis='y')
                
                for bar in bars:
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.2f}', ha='center', va='bottom', fontweight='bold')
            
            # Plot 3: Temporal evolution (middle left)
            ax3 = fig.add_subplot(gs[1, :2])
            for policy in self.config.policies:
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if not policy_data.empty:
                    sample_data = policy_data.iloc[::20]
                    ax3.plot(sample_data[self.config.col_timestamp],
                           sample_data[self.config.col_agg_ew],
                           label=policy, color=self.vis_config.palette[policy],
                           linewidth=2, alpha=0.8)
            
            ax3.set_title('Temporal Evolution of Waiting Times')
            ax3.set_xlabel('Time')
            ax3.set_ylabel('E[W]')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            # Plot 4: Distribution comparison (middle right)
            ax4 = fig.add_subplot(gs[1, 2:])
            distribution_data = []
            for policy in self.config.policies:
                policy_data = high_load_data[high_load_data['policy'] == policy]
                if not policy_data.empty:
                    distribution_data.append(policy_data[self.config.col_agg_ew].values)
            
            if distribution_data:
                ax4.boxplot(distribution_data, labels=self.config.policies,
                          patch_artist=True,
                          boxprops=dict(facecolor='lightblue', alpha=0.7),
                          medianprops=dict(color='red', linewidth=2))
                ax4.set_title('Distribution of Waiting Times')
                ax4.set_ylabel('E[W]')
                ax4.grid(True, alpha=0.3)
            
            # Plot 5: Feature importance (bottom left)
            ax5 = fig.add_subplot(gs[2, :2])
            if 'ml' in self.analysis_results and 'feature_importance' in self.analysis_results['ml']:
                feature_importance = self.analysis_results['ml']['feature_importance']
                if 'random_forest' in feature_importance:
                    importance_dict = feature_importance['random_forest']
                    sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
                    
                    features, importance = zip(*sorted_features[:8])  # Top 8 features
                    y_pos = np.arange(len(features))
                    
                    ax5.barh(y_pos, importance, align='center', alpha=0.7, color='lightgreen')
                    ax5.set_yticks(y_pos)
                    ax5.set_yticklabels(features)
                    ax5.set_xlabel('Importance')
                    ax5.set_title('Top Feature Importance (Random Forest)')
                    ax5.grid(True, alpha=0.3, axis='x')
            
            # Plot 6: Anomaly rates (bottom right)
            ax6 = fig.add_subplot(gs[2, 2:])
            if 'ml' in self.analysis_results and 'anomaly_detection' in self.analysis_results['ml']:
                anomaly_results = self.analysis_results['ml']['anomaly_detection']
                if 'isolation_forest' in anomaly_results:
                    anomaly_predictions = anomaly_results['isolation_forest']['predictions']
                    
                    anomaly_rates = {}
                    for policy in self.config.policies:
                        policy_mask = high_load_data['policy'] == policy
                        if policy_mask.any():
                            policy_anomalies = anomaly_predictions[policy_mask] == -1
                            anomaly_rate = np.mean(policy_anomalies) * 100
                            anomaly_rates[policy] = anomaly_rate
                    
                    if anomaly_rates:
                        bars = ax6.bar(anomaly_rates.keys(), anomaly_rates.values(),
                                     color=[self.vis_config.palette[p] for p in anomaly_rates.keys()],
                                     alpha=0.8)
                        ax6.set_title('Anomaly Detection Rates')
                        ax6.set_ylabel('Anomaly Rate (%)')
                        ax6.grid(True, alpha=0.3, axis='y')
                        
                        for bar in bars:
                            height = bar.get_height()
                            ax6.text(bar.get_x() + bar.get_width()/2., height,
                                   f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            # Plot 7: Summary statistics (bottom full width)
            ax7 = fig.add_subplot(gs[3, :])
            ax7.axis('off')
            
            # Create summary text
            summary_text = []
            summary_text.append("SUMMARY STATISTICS")
            summary_text.append("=" * 50)
            
            total_scenarios = len(self.master_data['scenario_id'].unique())
            summary_text.append(f"Total Scenarios Analyzed: {total_scenarios}")
            summary_text.append(f"Total Data Points: {len(self.master_data):,}")
            summary_text.append("")
            
            # Add policy-specific summaries
            for policy in self.config.policies:
                policy_data = self.master_data[self.master_data['policy'] == policy]
                if not policy_data.empty:
                    avg_wait = policy_data[self.config.col_agg_ew].mean()
                    avg_imbalance = policy_data['queue_imbalance'].mean()
                    summary_text.append(f"{policy}:")
                    summary_text.append(f"  Average E[W]: {avg_wait:.3f}")
                    summary_text.append(f"  Average Imbalance: {avg_imbalance:.3f}")
                    summary_text.append("")
            
            # Add analysis completion info
            if self.analysis_completed:
                summary_text.append("ANALYSIS STATUS: COMPLETED SUCCESSFULLY")
            else:
                summary_text.append("ANALYSIS STATUS: INCOMPLETE")
            
            ax7.text(0.05, 0.95, '\n'.join(summary_text), transform=ax7.transAxes,
                   fontfamily='monospace', fontsize=10, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
            
            plt.suptitle('Comprehensive Queueing System Analysis Dashboard', 
                        fontsize=16, fontweight='bold', y=0.98)
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            self._save_plot(fig, "25_summary_dashboard.png")
            
        except Exception as e:
            logger.error(f"Summary dashboard plot failed: {str(e)}")

    def _save_plot(self, fig: plt.Figure, filename: str) -> None:
        """Save plot with comprehensive error handling"""
        try:
            path = self.config.output_directory / filename
            fig.savefig(path, dpi=self.vis_config.dpi, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            plt.close(fig)
            logger.info(f"Saved: {filename}")
            
            # Create backup
            backup_path = self.config.backup_directory / filename
            fig.savefig(backup_path, dpi=self.vis_config.dpi, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
            
        except Exception as e:
            logger.error(f"Failed to save plot {filename}: {str(e)}")
    
    def _create_error_report(self, error: Exception) -> None:
        """Create error report when analysis fails"""
        try:
            error_report = [
                "ANALYSIS ERROR REPORT",
                "=" * 50,
                f"Error Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Error Type: {type(error).__name__}",
                f"Error Message: {str(error)}",
                "",
                "TRACEBACK:",
                traceback.format_exc(),
                "",
                "ANALYSIS STATE:",
                f"Master Data Loaded: {not self.master_data.empty}",
                f"Data Shape: {self.master_data.shape if not self.master_data.empty else 'N/A'}",
                f"Scenarios Loaded: {self.master_data['scenario_id'].nunique() if not self.master_data.empty else 0}"
            ]
            
            error_path = self.config.output_directory / "error_report.txt"
            with open(error_path, 'w') as f:
                f.write('\n'.join(error_report))
            
            logger.error(f"Error report saved to: {error_path}")
            
        except Exception as e:
            logger.error(f"Failed to create error report: {str(e)}")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    """
    Main execution block with comprehensive error handling
    """
    try:
        logger.info("Starting Comprehensive Queue Analysis")
        
        # Initialize and run analysis
        analyzer = ComprehensiveQueueAnalysis()
        success = analyzer.run_comprehensive_analysis()
        
        if success:
            logger.info("Analysis completed successfully!")
            print(f"\n{'='*60}")
            print("COMPREHENSIVE ANALYSIS COMPLETED SUCCESSFULLY!")
            print(f"Results saved to: {analyzer.config.output_directory}")
            print(f"{'='*60}")
        else:
            logger.error("Analysis failed!")
            print(f"\n{'='*60}")
            print("ANALYSIS FAILED! Check error report in output directory.")
            print(f"{'='*60}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        print("\nAnalysis interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        logger.critical(f"Unexpected error in main execution: {str(e)}")
        logger.critical(traceback.format_exc())
        print(f"\nCritical error: {str(e)}")
        sys.exit(1)