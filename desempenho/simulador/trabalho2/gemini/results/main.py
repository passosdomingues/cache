# -*- coding: utf-8 -*-
"""
Single-file Python analysis pipeline for the M/M/1 Multi-Queue Simulator.

Project: M/M/1 Multi-Queue Simulator Analysis
Author: Rafael Passos Domingues
Last Update: 2025 Sep 25 14h36

Purpose:
This script provides a complete, self-contained pipeline for analyzing the
output data from the C-based queueing system simulator. It automates the process
of data ingestion, stabilization detection, statistical analysis, machine
learning modeling, and generation of a comprehensive HTML report. All required
functions and the HTML template are included in this single file for portability
and ease of use.

Expected output:
- A directory 'analysis_results/' containing generated plots and the final report.
- A directory 'saved_models/' containing persisted machine learning models.
- A final HTML report named 'final_report.html' in 'analysis_results/'.
"""

# --- 1. IMPORTS ---
import os
import re
import base64
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import defaultdict
from jinja2 import Environment, BaseLoader
from scipy.stats import ks_2samp, shapiro, yeojohnson
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, silhouette_score
from sklearn.utils import resample

# --- 2. HTML REPORT TEMPLATE ---

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Simulation Analysis Report</title>
    <style>
        body { font-family: sans-serif; line-height: 1.6; margin: 20px; background-color: #f4f4f4; color: #333; }
        h1, h2, h3 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px; }
        .container { max-width: 1200px; margin: auto; background: white; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .scenario { border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
        .plot { max-width: 100%; height: auto; border: 1px solid #ccc; margin-top: 10px; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #3498db; color: white; }
        pre { background: #eee; padding: 10px; border-radius: 5px; white-space: pre-wrap; word-wrap: break-word; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Queueing System Simulation Analysis Report</h1>
        <p><strong>Author:</strong> Rafael Passos Domingues</p>
        <p><strong>Last Update:</strong> 2025 Sep 25 14h36</p>
        
        <h2>Executive Summary</h2>
        <p>This report details the analysis of a multi-queue, single-server simulation. Data from multiple seeds and scenarios (combinations of scheduling policies and server occupancies) were analyzed. The analysis includes stabilization detection, statistical summaries, and machine learning models to classify system behavior.</p>

        {% for scenario in scenarios %}
        <div class="scenario">
            <h2>Scenario: {{ scenario.scenario_name }}</h2>
            <h3>Configuration</h3>
            <ul>
                <li><strong>Policy:</strong> {{ scenario.params.policy }}</li>
                <li><strong>Rho (Occupancy):</strong> {{ scenario.params.rho }}</li>
                <li><strong>Number of Seeds:</strong> {{ scenario.num_seeds }}</li>
                <li><strong>Stabilization Point (Sample Index):</strong> {{ scenario.stabilization_index }}</li>
            </ul>

            <h3>Steady-State Statistics (95% CI)</h3>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Mean</th>
                    <th>CI Lower Bound</th>
                    <th>CI Upper Bound</th>
                </tr>
                {% for metric, values in scenario.stats.items() %}
                <tr>
                    <td>{{ metric }}</td>
                    <td>{{ "%.4f"|format(values.mean) }}</td>
                    <td>{{ "%.4f"|format(values.ci_low) }}</td>
                    <td>{{ "%.4f"|format(values.ci_high) }}</td>
                </tr>
                {% endfor %}
            </table>
            <p><strong>E[W] Normality Check:</strong> Normal before transform: {{ scenario.normality.ew_normal_before }}. Normal after Yeo-Johnson transform: {{ scenario.normality.ew_normal_after }}.</p>

            <h3>Visualizations</h3>
            <h4>E[N] and E[W] Time Series</h4>
            <img src="data:image/png;base64,{{ scenario.embedded_plots.timeseries_en_ew }}" alt="Time Series Plot" class="plot">
            
            <h4>Queue Sizes Over Time</h4>
            <img src="data:image/png;base64,{{ scenario.embedded_plots.queuesizes_time }}" alt="Queue Sizes Plot" class="plot">

            <h4>Steady-State Metrics Distribution</h4>
            <img src="data:image/png;base64,{{ scenario.embedded_plots.boxplots_steady }}" alt="Boxplots" class="plot">

            <h4>E[N] vs E[W] Relationship</h4>
            <img src="data:image/png;base64,{{ scenario.embedded_plots.en_vs_ew }}" alt="E[N] vs E[W] Plot" class="plot">
        </div>
        {% endfor %}

        {% if ml_results %}
        <div class="scenario">
            <h2>Machine Learning Pipeline Results</h2>
            
            <h3>Unsupervised Clustering (PCA + K-Means)</h3>
            <p>Data was scaled, reduced to 2 dimensions using PCA, and clustered with K-Means to find natural groupings in system behavior across all scenarios.</p>
            <img src="data:image/png;base64,{{ embedded_ml_plots.pca_plot }}" alt="PCA Plot" class="plot">

            <h3>Supervised Classification (Random Forest)</h3>
            <p>A Random Forest classifier was trained to predict the scenario (Policy + Rho) based on steady-state metrics. The model performance is detailed below.</p>
            <h4>Classification Report</h4>
            <pre>{{ ml_results.classification_report | tojson(indent=4) }}</pre>

            <h4>Confusion Matrix</h4>
            <img src="data:image/png;base64,{{ embedded_ml_plots.cm_plot }}" alt="Confusion Matrix" class="plot">
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

# --- 3. DATA LOADER FUNCTIONS ---

def find_simulation_files(results_path: Path):
    """
    Finds all simulation CSV files and groups them by scenario. This function
    scans a directory for CSV files matching a specific naming pattern, extracts
    the simulation parameters (policy, rho, seed) from the filename, and groups
    the file paths by their common policy and rho values.

    @param results_path: The path to the directory containing CSV files.
    @return: A dictionary where keys are dictionaries of parameters
             (e.g., {'policy': 1, 'rho': 0.8}) and values are lists of
             corresponding file paths.
    """
    file_pattern = re.compile(r"sim_policy(\d+)_rho([\d.]+)_seed(\d+)\.csv")
    grouped_files = defaultdict(list)

    if not results_path.exists():
        return {}

    for file_path in results_path.glob("*.csv"):
        match = file_pattern.match(file_path.name)
        if match:
            policy = int(match.group(1))
            rho = float(match.group(2))
            seed = int(match.group(3))
            params = {'policy': policy, 'rho': rho}
            # Use a frozenset of items to make the dict key hashable
            grouped_files[frozenset(params.items())].append(file_path)

    # Convert frozenset keys back to standard dicts for easier use
    return {dict(k): v for k, v in grouped_files.items()}

def load_and_aggregate_data(file_list: list) -> pd.DataFrame:
    """
    Loads multiple CSV files for a single scenario and aggregates them into a
    single pandas DataFrame. Each file corresponds to a different simulation
    seed. A 'seed' column is added to the DataFrame to track the origin of each
    row.

    @param file_list: A list of Path objects for the CSV files to be loaded.
    @return: A single pandas DataFrame containing the combined data from all
             input files. Returns an empty DataFrame if no files can be read.
    """
    df_list = []
    seed_pattern = re.compile(r"seed(\d+)\.csv")

    for file_path in file_list:
        try:
            match = seed_pattern.search(file_path.name)
            if match:
                seed = int(match.group(1))
                df = pd.read_csv(file_path)
                df['seed'] = seed
                df_list.append(df)
        except Exception as e:
            print(f"Warning: Could not read or parse {file_path}. Error: {e}")

    if not df_list:
        return pd.DataFrame()

    return pd.concat(df_list, ignore_index=True)


# --- 4. STATISTICAL UTILITY FUNCTIONS ---

def detect_stabilization_point(series: pd.Series, window_size: int = 100, alpha: float = 1e-6) -> int:
    """
    Detects the stabilization point (end of warm-up period) in a time series.
    It uses a sliding window approach, comparing the distributions of two
    consecutive windows with the Kolmogorov-Smirnov (KS) two-sample test.
    The system is considered stable when the p-value of the test exceeds a given
    significance level (alpha), indicating the distributions are statistically similar.
    The default alpha corresponds to a ~5-sigma confidence level.

    @param series: The pandas Series of time-series data (e.g., E[N] or E[W]).
    @param window_size: The number of data points in each sliding window.
    @param alpha: The significance level for the KS-test. A higher p-value
                  suggests the distributions are similar.
    @return: The sample index at which the series is considered stable. Returns 0
             if not enough data exists or if no stabilization is detected.
    """
    if len(series) < 2 * window_size:
        return 0  # Not enough data to determine

    i = 0
    while i + 2 * window_size <= len(series):
        window1 = series.iloc[i : i + window_size]
        window2 = series.iloc[i + window_size : i + 2 * window_size]

        if window1.isnull().all() or window2.isnull().all():
             i += window_size // 2
             continue
        
        stat, p_value = ks_2samp(window1.dropna(), window2.dropna())

        if p_value > alpha:
            # The distributions are statistically similar, system may be stable
            return i + window_size

        i += window_size // 2  # Slide window by a half-step

    return 0  # Return 0 if no stabilization point is found

def analyze_normality_and_transform(data: pd.Series, alpha: float = 0.05):
    """
    Checks data for normality using the Shapiro-Wilk test. If the data is not
    normally distributed (p-value <= alpha), it applies a Yeo-Johnson power
    transformation to attempt to normalize it. It then re-tests for normality.

    @param data: A pandas Series of numerical data.
    @param alpha: The significance level for the Shapiro-Wilk test.
    @return: A tuple containing:
             - transformed_data (pandas Series): The transformed data (or original if already normal).
             - is_normal_before (bool): True if data was normal before transformation.
             - is_normal_after (bool): True if data is normal after transformation.
    """
    # Test before transform
    data_clean = data.dropna()
    if len(data_clean) < 3: # Shapiro-Wilk needs at least 3 samples
        return data, False, False

    stat_before, p_before = shapiro(data_clean)
    is_normal_before = p_before > alpha

    if is_normal_before:
        return data, True, True

    # Apply Yeo-Johnson transform
    transformed_data, _ = yeojohnson(data)
    transformed_series = pd.Series(transformed_data, index=data.index)

    # Test after transform
    transformed_clean = transformed_series.dropna()
    if len(transformed_clean) < 3:
        return transformed_series, is_normal_before, False
        
    stat_after, p_after = shapiro(transformed_clean)
    is_normal_after = p_after > alpha

    return transformed_series, is_normal_before, is_normal_after

def get_bootstrap_ci(data: pd.Series, n_iterations: int = 1000, alpha: float = 0.05):
    """
    Calculates a non-parametric confidence interval for the mean of the data
    using the bootstrap resampling method. It repeatedly samples with replacement
    from the original data, calculates the mean for each sample, and determines
    the confidence interval from the distribution of these means.

    @param data: A pandas Series of numerical data.
    @param n_iterations: The number of bootstrap samples to generate.
    @param alpha: The significance level (e.g., 0.05 for a 95% CI).
    @return: A tuple containing the lower and upper bounds of the confidence interval.
    """
    means = np.zeros(n_iterations)
    data_np = data.dropna().to_numpy()

    if len(data_np) == 0:
        return np.nan, np.nan

    for i in range(n_iterations):
        bootstrap_sample = resample(data_np, replace=True)
        if len(bootstrap_sample) > 0:
            means[i] = np.mean(bootstrap_sample)
        else:
            means[i] = np.nan
            
    means = means[~np.isnan(means)]
    if len(means) == 0:
        return np.nan, np.nan

    lower_bound = np.percentile(means, 100 * (alpha / 2))
    upper_bound = np.percentile(means, 100 * (1 - alpha / 2))

    return lower_bound, upper_bound


# --- 5. PLOTTING FUNCTIONS ---

def generate_all_plots(df_full, df_steady, scenario_name: str, plots_dir: Path) -> dict:
    """
    Generates and saves a standard set of plots for a given simulation scenario.
    This includes time series plots of key metrics, boxplots of steady-state
    distributions, a scatter plot to validate Little's Law, and a time series
    of queue sizes. All plots are saved as PNG files.

    @param df_full: DataFrame with all data, including the warm-up period.
    @param df_steady: DataFrame with only steady-state data.
    @param scenario_name: A string identifier for the scenario (e.g., "Policy1_Rho0.8").
    @param plots_dir: The pathlib.Path object for the directory to save plots in.
    @return: A dictionary mapping descriptive plot names to their saved file paths.
    """
    sns.set_theme(style="whitegrid", palette="viridis")
    paths = {}

    # 1. Time Series of E[N] and E[W]
    path = plots_dir / f"{scenario_name}_timeseries_EN_EW.png"
    plt.figure(figsize=(12, 8))
    plt.subplot(2, 1, 1)
    sns.lineplot(data=df_full, x='timestamp', y='EN', hue='seed', legend=False, alpha=0.5)
    plt.title(f'E[N] over Time for {scenario_name}')
    plt.xlabel('Time (s)')
    plt.ylabel('E[N]')
    
    plt.subplot(2, 1, 2)
    sns.lineplot(data=df_full, x='timestamp', y='EW', hue='seed', legend=False, alpha=0.5)
    plt.title(f'E[W] over Time for {scenario_name}')
    plt.xlabel('Time (s)')
    plt.ylabel('E[W]')

    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()
    paths['timeseries_en_ew'] = path

    # 2. Boxplots of steady-state metrics
    path = plots_dir / f"{scenario_name}_boxplots_steady.png"
    plt.figure(figsize=(12, 6))
    metrics_to_plot = ['EN', 'EW', 'measuredOccupancy', 'littleError']
    df_steady[metrics_to_plot].plot(kind='box', title=f'Steady-State Metrics for {scenario_name}')
    plt.ylabel('Value')
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()
    paths['boxplots_steady'] = path

    # 3. E[N] vs E[W] scatter plot with regression
    path = plots_dir / f"{scenario_name}_EN_vs_EW.png"
    plt.figure(figsize=(8, 8))
    sns.regplot(data=df_steady, x='EW', y='EN', scatter_kws={'alpha':0.2}, line_kws={'color':'red'})
    plt.title(f'E[N] vs E[W] (Little\'s Law Validation) for {scenario_name}')
    plt.xlabel('E[W] (Average Time in System)')
    plt.ylabel('E[N] (Average Number in System)')
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()
    paths['en_vs_ew'] = path

    # 4. Queue sizes over time
    path = plots_dir / f"{scenario_name}_queuesizes_time.png"
    plt.figure(figsize=(12, 6))
    q_cols = ['queueSize1', 'queueSize2', 'queueSize3']
    df_melted = df_full.melt(id_vars=['timestamp', 'seed'], value_vars=q_cols, var_name='queue', value_name='size')
    sns.lineplot(data=df_melted, x='timestamp', y='size', hue='queue', errorbar=None)
    plt.title(f'Average Queue Sizes Over Time for {scenario_name}')
    plt.xlabel('Time (s)')
    plt.ylabel('Number of Customers')
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()
    paths['queuesizes_time'] = path

    return paths


# --- 6. MACHINE LEARNING PIPELINE ---

def run_full_ml_pipeline(df: pd.DataFrame, plots_dir: Path, models_dir: Path) -> dict:
    """
    Runs a complete machine learning pipeline on the combined steady-state data.
    The pipeline includes:
    1. Unsupervised Learning: PCA for dimensionality reduction and k-Means for
       clustering to discover inherent patterns in the data. The optimal number
       of clusters 'k' is determined using the silhouette score.
    2. Supervised Learning: A Random Forest Classifier is trained to predict the
       simulation scenario (a combination of policy and rho) from the performance
       metrics. The model's performance is evaluated and reported.
    All models (scaler, PCA, k-Means, RF) are saved to disk.

    @param df: The combined steady-state DataFrame from all scenarios.
    @param plots_dir: The directory to save ML-related plots.
    @param models_dir: The directory to save trained models.
    @return: A dictionary containing paths to generated plots and models, along
             with the classification report from the supervised model.
    """
    results = {}
    features = ['EN', 'EW', 'measuredOccupancy', 'queueSize1', 'queueSize2', 'queueSize3']
    X = df[features]
    if X.empty:
        return {"error": "No data for ML pipeline."}

    # --- Scaling ---
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    joblib.dump(scaler, models_dir / "scaler.joblib")
    results['scaler_path'] = models_dir / "scaler.joblib"

    # --- Unsupervised: PCA + k-Means ---
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    joblib.dump(pca, models_dir / "pca_model.joblib")

    # Find optimal k using silhouette score
    best_k, best_score = -1, -1
    k_range = range(2, min(6, len(df['rho'].unique()) * len(df['policy'].unique()) + 1))
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
        labels = kmeans.fit_predict(X_scaled)
        score = silhouette_score(X_scaled, labels)
        if score > best_score:
            best_k, best_score = k, score
    
    if best_k == -1: best_k = 2

    kmeans = KMeans(n_clusters=best_k, random_state=42, n_init='auto')
    df['cluster'] = kmeans.fit_predict(X_scaled)
    joblib.dump(kmeans, models_dir / "kmeans_model.joblib")
    results['kmeans_model_path'] = models_dir / "kmeans_model.joblib"

    # Plot clusters
    pca_plot_path = plots_dir / "ml_pca_kmeans_clusters.png"
    plt.figure(figsize=(10, 8))
    sns.scatterplot(x=X_pca[:, 0], y=X_pca[:, 1], hue=df['cluster'], palette='bright', s=50, alpha=0.7)
    plt.title(f'K-Means Clusters (k={best_k}) on PCA-reduced Data')
    plt.xlabel('Principal Component 1')
    plt.ylabel('Principal Component 2')
    plt.legend(title='Cluster')
    plt.savefig(pca_plot_path, dpi=300)
    plt.close()
    results['pca_plot_path'] = pca_plot_path

    # --- Supervised: Random Forest Classifier ---
    y = df['policy'].astype(str) + '_rho' + df['rho'].astype(str)
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)

    rf = RandomForestClassifier(n_estimators=100, random_state=42, oob_score=True)
    rf.fit(X_train, y_train)
    joblib.dump(rf, models_dir / "random_forest_model.joblib")
    results['rf_model_path'] = models_dir / "random_forest_model.joblib"

    y_pred = rf.predict(X_test)

    # Classification Report
    report = classification_report(y_test, y_pred, output_dict=True)
    results['classification_report'] = report
    print("Random Forest Classification Report:\n", classification_report(y_test, y_pred))

    # Confusion Matrix Plot
    cm_plot_path = plots_dir / "ml_rf_confusion_matrix.png"
    cm = confusion_matrix(y_test, y_pred, labels=rf.classes_)
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=rf.classes_, yticklabels=rf.classes_)
    plt.title('Random Forest Confusion Matrix')
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(cm_plot_path, dpi=300)
    plt.close()
    results['cm_plot_path'] = cm_plot_path

    return results


# --- 7. REPORT GENERATION ---

def image_to_base64(image_path: Path):
    """
    Converts an image file to a base64 encoded string. This allows the image
    to be embedded directly into an HTML file, making the report a single,
    self-contained file.

    @param image_path: The path to the image file.
    @return: A base64 encoded string representation of the image, or an
             empty string if the file cannot be read.
    """
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except IOError:
        return ""

def create_html_report(report_data: list, ml_results: dict, output_path: Path):
    """
    Generates a single, self-contained HTML report from the analysis results
    using the Jinja2 templating engine. All plots are embedded as base64 strings.

    @param report_data: A list of dictionaries, where each dictionary contains
                        the analysis results for a single simulation scenario.
    @param ml_results: A dictionary containing the results from the machine
                       learning pipeline.
    @param output_path: The file path for the final HTML report.
    """
    env = Environment(loader=BaseLoader())
    template = env.from_string(HTML_TEMPLATE)

    # Embed scenario-specific plots as base64 strings
    for item in report_data:
        item['embedded_plots'] = {
            name: image_to_base64(path) for name, path in item.get('plots', {}).items()
        }

    # Embed ML plots as base64 strings
    embedded_ml_plots = {}
    if ml_results and 'error' not in ml_results:
        if ml_results.get('pca_plot_path'):
            embedded_ml_plots['pca_plot'] = image_to_base64(ml_results['pca_plot_path'])
        if ml_results.get('cm_plot_path'):
            embedded_ml_plots['cm_plot'] = image_to_base64(ml_results['cm_plot_path'])

    html_content = template.render(
        scenarios=report_data,
        ml_results=ml_results,
        embedded_ml_plots=embedded_ml_plots
    )

    with open(output_path, "w", encoding='utf-8') as f:
        f.write(html_content)


# --- 8. MAIN ORCHESTRATION FUNCTION ---

def main():
    """
    Main function to orchestrate the entire analysis pipeline. It discovers
    simulation files, processes each scenario by loading data, detecting the
    steady-state, performing statistical analysis, and generating plots.
    Finally, it runs a combined machine learning pipeline on all steady-state
    data and compiles the results into a single HTML report.
    """
    print("Starting Python Analysis Pipeline...")

    # --- Configuration ---
    base_results_path = Path("../C_Simulator/results")
    output_dir = Path("analysis_results")
    plots_dir = output_dir / "plots"
    models_dir = Path("saved_models")

    # Create output directories
    output_dir.mkdir(exist_ok=True)
    plots_dir.mkdir(exist_ok=True)
    models_dir.mkdir(exist_ok=True)

    # --- Data Loading ---
    simulation_files = find_simulation_files(base_results_path)
    if not simulation_files:
        print(f"Error: No simulation CSV files found in '{base_results_path}'. Exiting.")
        return

    report_data = []
    all_steady_state_data = []

    # --- Process Each Scenario ---
    for params, file_list in simulation_files.items():
        # Sort by rho then policy to ensure consistent processing order
        sorted_params = dict(sorted(params.items(), key=lambda item: (item[1] if item[0] == 'rho' else item[0])))
        scenario_name = f"Policy{sorted_params['policy']}_Rho{sorted_params['rho']}"
        print(f"\nProcessing scenario: {scenario_name} ({len(file_list)} seeds)")

        # Load and aggregate data from all seeds for this scenario
        df_agg = load_and_aggregate_data(file_list)
        if df_agg.empty:
            print(f"  Warning: No data loaded for {scenario_name}. Skipping.")
            continue

        # Detect stabilization point
        stabilization_index = detect_stabilization_point(df_agg['EN'], window_size=100, alpha=1e-6)
        print(f"  Stabilization detected at sample index: {stabilization_index}")
        df_steady = df_agg[df_agg['sampleIndex'] >= stabilization_index].copy()

        if df_steady.empty:
            print("  Warning: No steady-state data found after stabilization cut-off. Skipping.")
            continue

        # Store for combined ML analysis
        df_steady['policy'] = sorted_params['policy']
        df_steady['rho'] = sorted_params['rho']
        all_steady_state_data.append(df_steady)

        # --- Statistical Analysis ---
        metrics_to_analyze = ['EN', 'EW', 'measuredOccupancy']
        stats_summary = {}
        for metric in metrics_to_analyze:
            ci_low, ci_high = get_bootstrap_ci(df_steady[metric])
            mean_val = df_steady[metric].mean()
            stats_summary[metric] = {'mean': mean_val, 'ci_low': ci_low, 'ci_high': ci_high}
            print(f"  - {metric}: Mean = {mean_val:.4f}, 95% CI = [{ci_low:.4f}, {ci_high:.4f}]")

        # Normality analysis for EW
        transformed_ew, is_normal_before, is_normal_after = analyze_normality_and_transform(df_steady['EW'])
        df_steady['EW_transformed'] = transformed_ew

        # --- Plotting ---
        plot_paths = generate_all_plots(df_agg, df_steady, scenario_name, plots_dir)
        print(f"  Plots generated for {scenario_name}.")

        report_data.append({
            'scenario_name': scenario_name,
            'params': sorted_params,
            'num_seeds': len(file_list),
            'stabilization_index': stabilization_index,
            'stats': stats_summary,
            'normality': {'ew_normal_before': is_normal_before, 'ew_normal_after': is_normal_after},
            'plots': plot_paths
        })

    # --- Combined ML Pipeline ---
    if all_steady_state_data:
        print("\nRunning Combined Machine Learning Pipeline...")
        combined_df = pd.concat(all_steady_state_data, ignore_index=True)
        ml_results = run_full_ml_pipeline(combined_df, plots_dir, models_dir)
        print("  ML Pipeline complete.")
    else:
        ml_results = None
        print("\nSkipping ML Pipeline: No steady-state data available.")

    # --- Report Generation ---
    print("\nGenerating Final HTML Report...")
    # Sort report data for consistent report structure
    report_data.sort(key=lambda x: (x['params']['policy'], x['params']['rho']))
    create_html_report(report_data, ml_results, output_dir / "final_report.html")
    print(f"Analysis complete! Report saved to '{output_dir / 'final_report.html'}'")


# --- 9. SCRIPT EXECUTION ---
if __name__ == "__main__":
    main()
