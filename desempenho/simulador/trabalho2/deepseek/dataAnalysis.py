#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Advanced Queueing Simulation Performance Analysis Toolkit
Author: Rafael Passos Domingues
Date: September 25, 2025

Final robust version with indexing corrections, refined stabilization logic,
analytical modeling, and fail-safe plot generation.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import silhouette_score, r2_score, mean_squared_error
import warnings
from typing import Dict, List, Tuple, Any, Optional
from glob import glob

warnings.filterwarnings('ignore')

# --- Configuration Classes ---

class AnalysisConfig:
    """Centralizes all configurable parameters for the analysis."""
    def __init__(self):
        # Data Configuration
        self.data_dir = "results"
        self.file_pattern_prefix = "dados_ocupacao"
        self.scenarios = ['0.800', '0.900', '0.950', '0.999']
        
        # Column Names (essential for adaptation)
        self.col_en = 'EN'
        self.col_ew = 'EW'
        self.col_lambda = 'measuredLambda'
        self.col_occupancy = 'measuredOccupancy'
        self.cols_queues = ['queueSize1', 'queueSize2', 'queueSize3']
        self.col_timestamp = 'timestamp'
        self.col_sample_index = 'sampleIndex'
        
        # Stabilization Detection Configuration (Relative Mean Method)
        self.stab_metric = self.col_en
        self.stab_window_size = 100  # Reduced window size for better detection
        self.stab_patience = 5       # Number of consecutive windows to confirm stability
        self.stab_tolerance = 0.02   # Increased tolerance to 2% for better detection

        # Machine Learning Configuration
        self.ml_test_size = 0.20
        self.ml_random_state = 42
        self.ml_feature_cols = [self.col_en, self.col_ew, self.col_lambda, 
                                self.col_occupancy] + self.cols_queues

class VisualizationConfig:
    """Settings for all generated plots."""
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.style = 'seaborn-v0_8-whitegrid'
        self.palette = "viridis"
        self.dpi = 300
        self.figsize = (14, 8)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.apply_settings()

    def apply_settings(self):
        plt.style.use(self.style)
        sns.set_palette(self.palette)
        plt.rcParams.update({
            'figure.dpi': self.dpi, 'savefig.dpi': self.dpi, 'font.size': 12,
            'axes.titlesize': 16, 'axes.labelsize': 12, 'legend.fontsize': 10
        })

# --- Core Components ---

class DataLoader:
    """Responsible for loading and validating simulation data."""
    def __init__(self, config: AnalysisConfig):
        self.config = config

    def load_and_validate_all(self) -> Dict[str, pd.DataFrame]:
        all_data = {}
        for scenario in self.config.scenarios:
            files = glob(str(Path(self.config.data_dir) / f"{self.config.file_pattern_prefix}_{scenario}_seed_*.csv"))
            if not files:
                single_file = Path(self.config.data_dir) / f"{self.config.file_pattern_prefix}_{scenario}.csv"
                files = [single_file] if single_file.exists() else []

            if not files:
                print(f"Warning: No data files found for scenario rho = {scenario}")
                continue

            # Load and combine files
            df_list = []
            for f in files:
                try:
                    df_temp = pd.read_csv(f)
                    df_list.append(df_temp)
                    print(f"  Loaded {len(df_temp)} records from {Path(f).name}")
                except Exception as e:
                    print(f"  Error loading {f}: {e}")
                    continue

            if not df_list:
                print(f"  No valid data for scenario {scenario}")
                continue

            df = pd.concat(df_list, ignore_index=True)
            if self._validate_data(df, scenario):
                all_data[scenario] = self._add_metadata(df, scenario)
                print(f"Data for scenario rho = {scenario} loaded and validated successfully ({len(df)} records).")
        return all_data
    
    def _validate_data(self, df: pd.DataFrame, scenario: str) -> bool:
        print(f"\n--- Validating data for scenario rho = {scenario} ---")
        
        # Check required columns - CORREÇÃO: usar self.config
        required_cols = [self.config.col_timestamp, self.config.col_sample_index, 
                        self.config.col_en, self.config.col_ew] + self.config.cols_queues
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"ERROR: Required columns not found: {missing_cols}")
            print(f"Available columns: {list(df.columns)}")
            return False
        
        # Check for NaN values
        nan_report = df[required_cols].isnull().sum()
        if nan_report.sum() > 0:
            print("NaN values found:")
            for col, count in nan_report.items():
                if count > 0:
                    print(f"  {col}: {count} NaN values ({(count/len(df))*100:.2f}%)")
        else:
            print("No missing (NaN) values found in key columns.")
        
        # Basic statistics
        print(f"Data range: samples {df[self.config.col_sample_index].min()} to {df[self.config.col_sample_index].max()}")
        print(f"Time range: {df[self.config.col_timestamp].min():.2f} to {df[self.config.col_timestamp].max():.2f} seconds")
        
        return True

    def _add_metadata(self, df: pd.DataFrame, scenario: str) -> pd.DataFrame:
        df['scenario'] = f"rho = {scenario}"
        df['rho_value'] = float(scenario)
        df['rho_category'] = f"rho_{scenario.replace('.', '_')}"  # For classification
        df['total_queue_size'] = df[self.config.cols_queues].sum(axis=1)  # CORREÇÃO: usar self.config
        return df

class StabilizationDetector:
    """Detects the stabilization point (end of the transient phase)."""
    def __init__(self, config: AnalysisConfig):
        self.config = config

    def detect(self, df: pd.DataFrame) -> int:
        metric = df[self.config.stab_metric].values
        win_size = self.config.stab_window_size
        
        print(f"  Data length: {len(metric)}, Window size: {win_size}")
        
        # If dataset is too small, use 25% as fallback
        if len(metric) < 2 * win_size: 
            fallback_point = int(len(metric) * 0.25)
            print(f"  Dataset too small for stabilization detection. Using fallback: {fallback_point}")
            return fallback_point

        # Calculate rolling means with overlapping windows
        means = []
        for i in range(0, len(metric) - win_size + 1, win_size // 4):  # 75% overlap
            window_mean = np.mean(metric[i:i + win_size])
            means.append((i, window_mean))
        
        if len(means) < 2:
            fallback_point = int(len(metric) * 0.25)
            print(f"  Not enough windows for analysis. Using fallback: {fallback_point}")
            return fallback_point
        
        patience_counter = 0
        stabilization_point = 0
        
        for i in range(1, len(means)):
            idx1, mean1 = means[i-1]
            idx2, mean2 = means[i]
            
            if mean1 > 1e-9:  # Avoid division by zero
                rel_diff = abs(mean2 - mean1) / mean1
                
                if rel_diff < self.config.stab_tolerance:
                    patience_counter += 1
                    if patience_counter >= self.config.stab_patience:
                        stabilization_point = max(0, idx1)
                        print(f"  Stabilization detected at sample {stabilization_point} "
                              f"(mean difference < {self.config.stab_tolerance*100:.1f}% for {patience_counter} windows)")
                        return stabilization_point
                else:
                    patience_counter = 0
                    stabilization_point = idx2  # Move stabilization point forward
        
        # If no clear stabilization, find point where variance reduces significantly
        rolling_std = pd.Series(metric).rolling(window=win_size).std().dropna()
        if len(rolling_std) > 10:
            # Find point where standard deviation stabilizes
            relative_std = rolling_std / rolling_std.mean()
            stable_points = np.where(relative_std < 1.5)[0]  # Where std is less than 150% of mean std
            if len(stable_points) > 0:
                stabilization_point = stable_points[0]
                print(f"  Stabilization detected at sample {stabilization_point} (variance reduction)")
                return stabilization_point
        
        fallback_point = int(len(metric) * 0.10)  # More aggressive fallback
        print(f"  Warning: Stabilization not clearly detected. Using fallback: {fallback_point}")
        return fallback_point

class MachineLearningPipeline:
    """Encapsulates the Machine Learning workflow."""
    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)

    def run_all(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[PCA], pd.Series]:
        """Run the complete ML pipeline on the provided data."""
        if data.empty:
            print("Warning: No data provided for ML pipeline.")
            return data, None, pd.Series(dtype=float)
            
        # Prepare features
        features = data[self.config.ml_feature_cols].dropna()
        if features.empty:
            print("Warning: No data for ML pipeline after dropping NaNs.")
            return data, None, pd.Series(dtype=float)

        print(f"\nML Pipeline: Processing {len(features)} samples with {len(features.columns)} features")
        
        # Run unsupervised learning
        clustered_data, pca = self.run_pca_kmeans(data, features)
        
        # Run supervised learning - using regression instead of classification
        feature_importance = self.run_random_forest_regression(clustered_data)
        
        return clustered_data, pca, feature_importance

    def run_pca_kmeans(self, original_data: pd.DataFrame, features: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[PCA]]:
        """Perform PCA and KMeans clustering."""
        print("\n--- Unsupervised Learning: PCA and KMeans ---")
        
        try:
            # Scale features
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            # Perform PCA
            pca = PCA(n_components=2)
            features_pca = pca.fit_transform(features_scaled)
            variance_explained = np.sum(pca.explained_variance_ratio_)
            print(f"PCA: Variance explained by 2 components: {variance_explained:.2%}")
            
            # Determine optimal number of clusters (limit to reasonable range)
            k_range = range(2, min(8, len(features_scaled) // 10))  # More conservative range
            scores = []
            
            for k in k_range:
                try:
                    kmeans = KMeans(n_clusters=k, random_state=self.config.ml_random_state, n_init=10)
                    labels = kmeans.fit_predict(features_scaled)
                    if len(np.unique(labels)) > 1:
                        score = silhouette_score(features_scaled, labels)
                        scores.append(score)
                    else:
                        scores.append(-1)
                except Exception as e:
                    print(f"  Warning: Could not compute silhouette for k={k}: {e}")
                    scores.append(-1)
            
            if scores and max(scores) > 0.1:  # Require reasonable silhouette score
                optimal_k = k_range[np.argmax(scores)]
                print(f"KMeans: Optimal number of clusters (k) found: {optimal_k} (silhouette: {max(scores):.3f})")
                
                # Apply KMeans with optimal k
                kmeans = KMeans(n_clusters=optimal_k, random_state=self.config.ml_random_state, n_init=10)
                clusters = kmeans.fit_predict(features_scaled)
                
                # Add results to data
                data_with_clusters = original_data.copy()
                valid_indices = features.index
                data_with_clusters.loc[valid_indices, 'cluster'] = clusters
                data_with_clusters.loc[valid_indices, 'PC1'] = features_pca[:, 0]
                data_with_clusters.loc[valid_indices, 'PC2'] = features_pca[:, 1]
                
                return data_with_clusters, pca
            else:
                print("Warning: Could not determine optimal clusters. Silhouette scores too low.")
                return original_data, pca
                
        except Exception as e:
            print(f"Error in PCA/KMeans: {e}")
            return original_data, None

    def run_random_forest_regression(self, data: pd.DataFrame) -> pd.Series:
        """Train Random Forest REGRESSOR (not classifier) for continuous rho values."""
        print("\n--- Supervised Learning: RandomForest Regression ---")
        
        try:
            # Prepare data - using rho_value as continuous target for regression
            df = data.copy().dropna(subset=self.config.ml_feature_cols + ['rho_value'])
            if df.empty or df['rho_value'].nunique() < 2:
                print("Warning: Insufficient data for regression.")
                return pd.Series(dtype=float)
            
            print(f"Regression data: {len(df)} samples, rho range: {df['rho_value'].min():.3f} to {df['rho_value'].max():.3f}")
            
            X, y = df[self.config.ml_feature_cols], df['rho_value']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=self.config.ml_test_size, 
                random_state=self.config.ml_random_state
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train regression model
            model = RandomForestRegressor(n_estimators=100, random_state=self.config.ml_random_state)
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test_scaled)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            print("Regression Results:")
            print(f"  Mean Squared Error: {mse:.6f}")
            print(f"  R² Score: {r2:.4f}")
            print(f"  Mean Absolute Error: {np.mean(np.abs(y_test - y_pred)):.4f}")
            
            # Save model and scaler
            joblib.dump(model, self.models_dir / "rf_regressor.joblib")
            joblib.dump(scaler, self.models_dir / "rf_scaler.joblib")
            print(f"RandomForest regressor and scaler saved to '{self.models_dir}'")
            
            # Return feature importance
            importance = pd.Series(model.feature_importances_, index=self.config.ml_feature_cols)
            importance = importance.sort_values(ascending=False)
            
            print("\nFeature Importance:")
            for feat, imp in importance.items():
                print(f"  {feat}: {imp:.4f}")
            
            return importance
            
        except Exception as e:
            print(f"Error in Random Forest regression: {e}")
            return pd.Series(dtype=float)

class AnalyticalModeler:
    """Fits analytical models to simulation results."""
    def fit_polynomial(self, x: np.ndarray, y: np.ndarray, max_degree: int = 3) -> Dict[str, Any]:
        """Fit polynomial model to the data."""
        print("\n--- Fitting Analytical (Polynomial) Model ---")
        
        if len(x) < max_degree + 1:
            max_degree = max(1, len(x) - 1)
            print(f"Reducing max degree to {max_degree} due to limited data points")
        
        best_model = {'r2': -np.inf, 'degree': 0, 'model': None, 'equation': ''}
        
        for degree in range(1, max_degree + 1):
            try:
                poly_features = PolynomialFeatures(degree=degree)
                x_poly = poly_features.fit_transform(x.reshape(-1, 1))
                model = LinearRegression().fit(x_poly, y)
                r2 = r2_score(y, model.predict(x_poly))
                
                if r2 > best_model['r2']:
                    best_model.update({
                        'r2': r2, 
                        'degree': degree, 
                        'model': model, 
                        'poly_features': poly_features
                    })
            except Exception as e:
                print(f"Warning: Failed to fit degree {degree} polynomial: {e}")
                continue
        
        if best_model['model']:
            coefs = best_model['model'].coef_.flatten()
            intercept = best_model['model'].intercept_
            
            # Build equation string
            eq_parts = [f"{intercept:.4f}"]
            for i in range(1, len(coefs)):
                if abs(coefs[i]) > 1e-10:  # Only include significant terms
                    eq_parts.append(f"{coefs[i]:+.4f}*ρ^{i}")
            
            best_model['equation'] = "y = " + " ".join(eq_parts)
            print(f"Best model found (degree {best_model['degree']}):")
            print(f"  Equation: {best_model['equation']}")
            print(f"  R²: {best_model['r2']:.6f}")
        else:
            print("Warning: No valid polynomial model could be fitted")
            
        return best_model

# --- Main Orchestration Class ---

class SimulationAnalysisPipeline:
    """Orchestrates the entire analysis pipeline."""
    def __init__(self):
        self.config = AnalysisConfig()
        self.vis_config = VisualizationConfig(Path(self.config.data_dir) / "plots")
        self.data_loader = DataLoader(self.config)
        self.stab_detector = StabilizationDetector(self.config)
        self.ml_pipeline = MachineLearningPipeline(self.config)
        self.modeler = AnalyticalModeler()

    def run(self):
        """Execute the complete analysis pipeline."""
        print("="*80 + "\nSTARTING ADVANCED QUEUEING SIMULATION ANALYSIS\n" + "="*80)
        
        # Load and validate data
        raw_data = self.data_loader.load_and_validate_all()
        if not raw_data: 
            raise ValueError("No data was loaded. Check file paths and patterns.")
        
        # Detect steady-state phase
        print("\n--- Detecting Steady-State Phase ---")
        stable_data_per_scenario = {}
        for scenario, df in raw_data.items():
            print(f"\nAnalyzing scenario {scenario}:")
            stab_point = self.stab_detector.detect(df)
            stable_data_per_scenario[scenario] = df.iloc[stab_point:].copy()
            print(f"  Using {len(stable_data_per_scenario[scenario])} samples from index {stab_point}")
        
        # Combine stable data
        stable_data_combined = pd.concat(stable_data_per_scenario.values(), ignore_index=True)
        
        # Generate summary statistics
        summary_df = self._generate_summary_report(stable_data_per_scenario)
        
        # Fit analytical models
        analytical_models = {}
        for metric in [self.config.col_en, self.config.col_ew]:
            if len(summary_df) >= 2:  # Need at least 2 points for modeling
                analytical_models[metric] = self.modeler.fit_polynomial(
                    summary_df['rho'].values, 
                    summary_df[metric].values
                )
            else:
                print(f"Warning: Insufficient data for {metric} modeling")
                analytical_models[metric] = {'r2': 0, 'degree': 0, 'model': None, 'equation': 'N/A'}
        
        # Run machine learning pipeline
        ml_results = self.ml_pipeline.run_all(stable_data_combined)
        
        # Generate visualizations
        self._generate_visualizations(raw_data, stable_data_per_scenario, summary_df, analytical_models, ml_results)

        print("\n" + "="*80 + "\nANALYSIS COMPLETED SUCCESSFULLY!\n" + "="*80)

    def _generate_summary_report(self, stable_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Generate comprehensive statistics report."""
        print("\n" + "-"*60 + "\nSTATISTICS REPORT (STEADY-STATE PHASE)\n" + "-"*60)
        
        summary_rows = []
        for scenario, df in stable_data.items():
            print(f"\nScenario rho = {scenario} ({len(df)} samples):")
            row = {'rho': float(scenario)}
            
            for metric in [self.config.col_en, self.config.col_ew, 'total_queue_size']:
                if metric in df.columns:
                    values = df[metric]
                    mean, std = values.mean(), values.std()
                    median, q1, q3 = values.median(), values.quantile(0.25), values.quantile(0.75)
                    row[metric] = mean
                    
                    print(f"  - {metric}:")
                    print(f"    Mean={mean:.2f}, StdDev={std:.2f}")
                    print(f"    Median={median:.2f}, IQR={q3-q1:.2f}")
                    print(f"    Min={values.min():.2f}, Max={values.max():.2f}")
            
            summary_rows.append(row)
        
        print("-" * 60)
        return pd.DataFrame(summary_rows)

    def _generate_visualizations(self, raw_data: Dict[str, pd.DataFrame], 
                               stable_data: Dict[str, pd.DataFrame], 
                               summary_df: pd.DataFrame,
                               analytical_models: Dict[str, Dict[str, Any]],
                               ml_results: Tuple[pd.DataFrame, Optional[PCA], pd.Series]):
        """Generate all visualization plots."""
        print("\n--- Generating Visualizations ---")
        
        clustered_data, pca, feature_importance = ml_results
        
        # 1. Stabilization Detection Plot
        self._plot_stabilization(raw_data, stable_data)
        
        # 2. Analytical Models Plot
        self._plot_analytical_models(summary_df, analytical_models)
        
        # 3. Clustering Results Plot
        self._plot_clustering_results(clustered_data, pca)
        
        # 4. Feature Importance Plot
        self._plot_feature_importance(feature_importance)
        
        # 5. Time Series Comparison Plot
        self._plot_time_series_comparison(stable_data)
        
        # 6. Distribution Comparison Plot
        self._plot_distribution_comparison(stable_data)

    def _plot_stabilization(self, raw_data: Dict[str, pd.DataFrame], 
                          stable_data: Dict[str, pd.DataFrame]):
        """Plot stabilization detection results."""
        try:
            n_scenarios = len(raw_data)
            n_cols = min(2, n_scenarios)
            n_rows = (n_scenarios + n_cols - 1) // n_cols
            
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 6*n_rows))
            if n_scenarios == 1:
                axes = np.array([axes])
            axes = axes.flat
            
            for idx, (scenario, df) in enumerate(raw_data.items()):
                ax = axes[idx]
                stable_df = stable_data[scenario]
                
                # Use sampleIndex for x-axis if available, otherwise use index
                if self.config.col_sample_index in df.columns:
                    x_vals = df[self.config.col_sample_index]
                    x_label = 'Sample Index'
                else:
                    x_vals = df.index
                    x_label = 'Row Index'
                
                # Plot full timeline
                ax.plot(x_vals, df[self.config.col_en], alpha=0.7, label='Full data', linewidth=1)
                
                # Mark stabilization point
                if len(stable_df) > 0:
                    if self.config.col_sample_index in stable_df.columns:
                        stab_point = stable_df[self.config.col_sample_index].iloc[0]
                    else:
                        stab_point = stable_df.index[0]
                    
                    ax.axvline(x=stab_point, color='red', linestyle='--', 
                              linewidth=2, label=f'Stabilization point')
                    
                    # Highlight stable region
                    ax.axvspan(stab_point, x_vals.max(), alpha=0.2, color='green', label='Steady-state region')
                
                ax.set_title(f'Scenario ρ = {scenario}', fontsize=14)
                ax.set_xlabel(x_label)
                ax.set_ylabel('Number in System (EN)')
                ax.legend()
                ax.grid(True, alpha=0.3)
            
            # Hide empty subplots
            for idx in range(len(raw_data), len(axes)):
                axes[idx].set_visible(False)
            
            fig.suptitle('Steady-State Phase Detection', fontsize=16, fontweight='bold')
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            plt.savefig(self.vis_config.output_dir / "stabilization_detection.png", 
                       dpi=self.vis_config.dpi, bbox_inches='tight')
            plt.close()
            print("✓ Plot 'stabilization_detection.png' saved.")
            
        except Exception as e:
            print(f"✗ Failed to generate stabilization plot: {e}")

    def _plot_analytical_models(self, summary_df: pd.DataFrame, 
                              analytical_models: Dict[str, Dict[str, Any]]):
        """Plot analytical model fitting results."""
        try:
            if len(summary_df) < 2:
                print("Skipping analytical models plot: insufficient data")
                return
                
            fig, axes = plt.subplots(1, 2, figsize=(16, 6))
            metrics = [self.config.col_en, self.config.col_ew]
            metric_names = ['Number in System (EN)', 'Number in Queue (EW)']
            
            for i, (metric, name) in enumerate(zip(metrics, metric_names)):
                ax = axes[i]
                model_info = analytical_models[metric]
                
                # Plot actual data points
                ax.scatter(summary_df['rho'], summary_df[metric], 
                          s=100, alpha=0.7, label='Simulation Data', zorder=5)
                
                # Plot fitted model if available
                if model_info['model']:
                    rho_smooth = np.linspace(summary_df['rho'].min() * 0.95, 
                                           summary_df['rho'].max() * 1.05, 200)
                    x_poly = model_info['poly_features'].transform(rho_smooth.reshape(-1, 1))
                    y_pred = model_info['model'].predict(x_poly)
                    
                    ax.plot(rho_smooth, y_pred, 'r-', linewidth=2, 
                           label=f"Polynomial (degree {model_info['degree']})\nR² = {model_info['r2']:.4f}")
                
                ax.set_xlabel('Traffic Intensity (ρ)')
                ax.set_ylabel(name)
                ax.set_title(f'{name} vs. Traffic Intensity')
                ax.legend()
                ax.grid(True, alpha=0.3)
            
            fig.suptitle('Analytical Performance Modeling', fontsize=16, fontweight='bold')
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            plt.savefig(self.vis_config.output_dir / "analytical_models.png", 
                       dpi=self.vis_config.dpi, bbox_inches='tight')
            plt.close()
            print("✓ Plot 'analytical_models.png' saved.")
            
        except Exception as e:
            print(f"✗ Failed to generate analytical models plot: {e}")

    def _plot_clustering_results(self, clustered_data: pd.DataFrame, pca: Optional[PCA]):
        """Plot PCA and clustering results."""
        try:
            if pca is None or 'cluster' not in clustered_data.columns:
                print("Skipping clustering plot: no PCA/clustering results available")
                return
                
            plt.figure(figsize=(12, 8))
            
            # Filter out rows without cluster assignments
            plot_data = clustered_data.dropna(subset=['cluster', 'PC1', 'PC2'])
            
            if len(plot_data) > 0:
                scatter = plt.scatter(plot_data['PC1'], plot_data['PC2'], 
                                    c=plot_data['cluster'], cmap='viridis', 
                                    alpha=0.6, s=30)
                plt.colorbar(scatter, label='Cluster')
                
                # Add scenario information
                unique_scenarios = plot_data['scenario'].unique()
                for scenario in unique_scenarios:
                    scenario_data = plot_data[plot_data['scenario'] == scenario]
                    plt.scatter([], [], alpha=0.6, s=30, label=scenario)
                
                plt.xlabel(f'Principal Component 1 ({pca.explained_variance_ratio_[0]:.2%} variance)')
                plt.ylabel(f'Principal Component 2 ({pca.explained_variance_ratio_[1]:.2%} variance)')
                plt.title('KMeans Clustering on PCA-Reduced Features')
                plt.legend()
                plt.grid(True, alpha=0.3)
                
                plt.tight_layout()
                plt.savefig(self.vis_config.output_dir / "clustering_results.png", 
                           dpi=self.vis_config.dpi, bbox_inches='tight')
                plt.close()
                print("✓ Plot 'clustering_results.png' saved.")
            else:
                print("No data available for clustering plot")
                
        except Exception as e:
            print(f"✗ Failed to generate clustering plot: {e}")

    def _plot_feature_importance(self, feature_importance: pd.Series):
        """Plot feature importance from Random Forest."""
        try:
            if feature_importance.empty:
                print("Skipping feature importance plot: no importance data")
                return
                
            plt.figure(figsize=(10, 6))
            feature_importance.sort_values().plot(kind='barh', color='skyblue')
            plt.title('Random Forest Feature Importance (Regression)')
            plt.xlabel('Importance Score')
            plt.grid(True, alpha=0.3, axis='x')
            plt.tight_layout()
            plt.savefig(self.vis_config.output_dir / "feature_importance.png", 
                       dpi=self.vis_config.dpi, bbox_inches='tight')
            plt.close()
            print("✓ Plot 'feature_importance.png' saved.")
            
        except Exception as e:
            print(f"✗ Failed to generate feature importance plot: {e}")

    def _plot_time_series_comparison(self, stable_data: Dict[str, pd.DataFrame]):
        """Plot time series comparison across scenarios."""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(16, 10))
            axes = axes.flat
            
            metrics = [self.config.col_en, self.config.col_ew, 'total_queue_size', self.config.col_occupancy]
            metric_names = ['Number in System (EN)', 'Number in Queue (EW)', 'Total Queue Size', 'Occupancy']
            
            for i, (metric, name) in enumerate(zip(metrics, metric_names)):
                ax = axes[i]
                
                for scenario, df in stable_data.items():
                    if metric in df.columns and len(df) > 0:
                        # Use sample index for x-axis
                        if self.config.col_sample_index in df.columns:
                            x_vals = df[self.config.col_sample_index].iloc[:500]  # First 500 points for clarity
                            y_vals = df[metric].iloc[:500]
                        else:
                            x_vals = df.index[:500]
                            y_vals = df[metric].iloc[:500]
                            
                        ax.plot(x_vals, y_vals, alpha=0.7, label=f'ρ = {scenario}', linewidth=1)
                
                ax.set_xlabel('Sample Index')
                ax.set_ylabel(name)
                ax.set_title(f'{name} Time Series')
                if i == 0:  # Only show legend on first subplot
                    ax.legend()
                ax.grid(True, alpha=0.3)
            
            fig.suptitle('Time Series Comparison Across Scenarios (First 500 Samples)', 
                        fontsize=16, fontweight='bold')
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            plt.savefig(self.vis_config.output_dir / "time_series_comparison.png", 
                       dpi=self.vis_config.dpi, bbox_inches='tight')
            plt.close()
            print("✓ Plot 'time_series_comparison.png' saved.")
            
        except Exception as e:
            print(f"✗ Failed to generate time series comparison plot: {e}")

    def _plot_distribution_comparison(self, stable_data: Dict[str, pd.DataFrame]):
        """Plot distribution comparison across scenarios."""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(16, 10))
            axes = axes.flat
            
            metrics = [self.config.col_en, self.config.col_ew, 'total_queue_size', self.config.col_occupancy]
            metric_names = ['Number in System (EN)', 'Number in Queue (EW)', 'Total Queue Size', 'Occupancy']
            
            for i, (metric, name) in enumerate(zip(metrics, metric_names)):
                ax = axes[i]
                
                plot_data = []
                labels = []
                for scenario, df in stable_data.items():
                    if metric in df.columns and len(df) > 0:
                        plot_data.append(df[metric].values)
                        labels.append(f'ρ = {scenario}')
                
                if plot_data:
                    # Use KDE plot for better visualization
                    for j, data in enumerate(plot_data):
                        sns.kdeplot(data, ax=ax, label=labels[j], alpha=0.7)
                    
                    ax.set_xlabel(name)
                    ax.set_ylabel('Density')
                    ax.set_title(f'{name} Distribution')
                    if i == 0:  # Only show legend on first subplot
                        ax.legend()
                    ax.grid(True, alpha=0.3)
            
            fig.suptitle('Distribution Comparison Across Scenarios', fontsize=16, fontweight='bold')
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            plt.savefig(self.vis_config.output_dir / "distribution_comparison.png", 
                       dpi=self.vis_config.dpi, bbox_inches='tight')
            plt.close()
            print("✓ Plot 'distribution_comparison.png' saved.")
            
        except Exception as e:
            print(f"✗ Failed to generate distribution comparison plot: {e}")

def main():
    """Main function to run the analysis."""
    try:
        pipeline = SimulationAnalysisPipeline()
        pipeline.run()
    except Exception as e:
        print(f"\n❌ UNRECOVERABLE ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    return 0

if __name__ == "__main__":
    exit(main())
