#!/usr/bin/env python3
"""
COMPREHENSIVE QUEUEING SYSTEM ANALYSIS PIPELINE - ENHANCED VERSION
Project MM1: Complete Analysis of 11 Scheduling Policies × 4 Load Scenarios
Author: Senior Data Scientist
Description: Enhanced analysis processing ALL 44 files, ALL policies, ALL load scenarios
             with special focus on MAX_AVG_WAIT, ROUND_ROBIN, and SALLES_UTILITY policies.
"""

import os
import glob
import re
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import warnings

# Machine Learning Imports
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVC
from sklearn.metrics import mean_squared_error, r2_score, classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
import scipy.stats as stats
from scipy import signal

warnings.filterwarnings('ignore')


# =================================================================================
# CONFIGURATION & CONSTANTS - Enhanced Configuration
# =================================================================================
@dataclass
class AnalysisConfiguration:
    """
    @brief Central configuration for the comprehensive MM1 Analysis Pipeline
    """
    # Path configurations
    RAW_DATA_PATH: str = "../results/raw"
    OUTPUT_PATH: str = "../analysis"
    PLOTS_PATH: str = "plots"
    SUMMARIES_PATH: str = "summaries"
    CAPTIONS_PATH: str = "captions"
    ML_RESULTS_PATH: str = "ml_results"

    # Graphics settings
    DPI: int = 300
    FIG_SIZE_LARGE: Tuple[int, int] = (16, 10)
    FIG_SIZE_MEDIUM: Tuple[int, int] = (12, 8)
    FIG_SIZE_SMALL: Tuple[int, int] = (10, 6)

    # Analysis parameters
    TOTAL_SAMPLES: int = 8641
    RANDOM_STATE: int = 42
    TEST_SIZE_RATIO: float = 0.2
    CROSS_VALIDATION_FOLDS: int = 5

    # Plot sampling for performance
    SCATTER_SAMPLE_SIZE: int = 10000
    TIME_SERIES_SAMPLE_STEP: int = 10

    # Special focus policies
    PROTAGONIST_POLICIES = ["MAX_AVG_WAIT", "ROUND_ROBIN", "SALLES_UTILITY"]

    # All load scenarios
    LOAD_SCENARIOS: List[float] = field(default_factory=lambda: [0.800, 0.900, 0.950, 0.999])

    @classmethod
    def setupDirectories(cls):
        """
        @brief Creates all necessary output directories with validation
        """
        directories = [
            cls.OUTPUT_PATH, cls.PLOTS_PATH, cls.SUMMARIES_PATH,
            cls.CAPTIONS_PATH, cls.ML_RESULTS_PATH
        ]

        for directory in directories:
            path = Path(directory)
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directory ensured: {directory}")


# =================================================================================
# ENHANCED LOGGING SETUP
# =================================================================================
def setupLogging():
    """
    @brief Configures comprehensive logging for the analysis pipeline
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
        handlers=[
            logging.FileHandler("comprehensive_MM1_analysis.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


logger = setupLogging()


# =================================================================================
# ENHANCED DATA INGESTION ENGINE - PROCESSES ALL 44 FILES
# =================================================================================
class EnhancedDataIngestionEngine:
    """
    @brief Enhanced data ingestion that processes ALL 44 files with ALL policies and ALL load scenarios
    """

    def __init__(self):
        self.globalDataFrame = pd.DataFrame()
        self.fileMetadata = {}
        self.cleaningReport = {}
        self.loadedPolicies = set()
        self.loadedScenarios = set()
        self.validationReport = {}

    def parseFilenameWithEnhancedRegex(self, filename: str) -> Dict[str, Any]:
        """
        @brief Enhanced filename parsing that handles ALL policy names correctly
        @param filename: Name of the CSV file
        @return Dictionary with parsed metadata
        """
        # Remove extension
        clean_name = filename.replace('.csv', '')

        # Extract seed (always 42 except one case)
        seed_match = re.search(r'_seed(\d+)', clean_name)
        seed = int(seed_match.group(1)) if seed_match else 42

        # Extract rho
        rho_match = re.search(r'rho(0\.\d+)', clean_name)
        if not rho_match:
            raise ValueError(f"Could not extract rho from filename: {filename}")
        rho = float(rho_match.group(1))

        # Extract policy name (everything before _rho)
        policy_match = re.match(r'(.*)_rho', clean_name)
        if not policy_match:
            raise ValueError(f"Could not extract policy from filename: {filename}")
        policy = policy_match.group(1)

        return {
            'policy': policy,
            'rho': rho,
            'seed': seed,
            'filename': filename
        }

    def validateDataStructure(self, dataframe: pd.DataFrame, filename: str) -> bool:
        """
        @brief Comprehensive validation of data structure and integrity
        @param dataframe: DataFrame to validate
        @param filename: Source filename for logging
        @return Boolean indicating validation success
        """
        required_columns = [
            'time', 'sample_idx', 'total_occupancy', 'arrival_rate_est',
            'q0_len', 'q1_len', 'q2_len', 'server_busy', 'system_EN',
            'system_EW', 'little_error'
        ]

        # Check required columns
        missing_columns = [col for col in required_columns if col not in dataframe.columns]
        if missing_columns:
            logger.error(f"Missing required columns in {filename}: {missing_columns}")
            return False

        # Check sample count
        if len(dataframe) != AnalysisConfiguration.TOTAL_SAMPLES:
            logger.warning(
                f"Sample count mismatch in {filename}: {len(dataframe)} vs {AnalysisConfiguration.TOTAL_SAMPLES}")

        return True

    def loadAndValidateAllData(self) -> pd.DataFrame:
        """
        @brief Loads ALL 44 CSV files with comprehensive validation
        @return Combined and validated DataFrame
        """
        data_path = Path(AnalysisConfiguration.RAW_DATA_PATH)
        if not data_path.exists():
            raise FileNotFoundError(f"Raw data path does not exist: {AnalysisConfiguration.RAW_DATA_PATH}")

        csv_files = list(data_path.glob("*.csv"))
        logger.info(f"Found {len(csv_files)} CSV files for analysis")

        if len(csv_files) != 44:
            logger.warning(f"Expected 44 files, found {len(csv_files)}. Continuing with available files.")

        data_frames = []
        validation_results = {}
        loaded_count = 0

        for file_path in csv_files:
            filename = file_path.name
            logger.info(f"Processing file: {filename}")

            try:
                # Read CSV with error handling
                df = pd.read_csv(file_path)

                # Extract metadata
                metadata = self.parseFilenameWithEnhancedRegex(filename)

                # Validate structure
                is_valid = self.validateDataStructure(df, filename)
                validation_results[filename] = {
                    'valid': is_valid,
                    'row_count': len(df),
                    'metadata': metadata
                }

                if not is_valid:
                    logger.error(f"Validation failed for {filename}, skipping")
                    continue

                # Enrich data with metadata
                df['policy_name'] = metadata['policy']
                df['load_factor'] = metadata['rho']
                df['seed_value'] = metadata['seed']
                df['scenario_id'] = f"{metadata['policy']}_rho{metadata['rho']}"

                # Track loaded policies and scenarios
                self.loadedPolicies.add(metadata['policy'])
                self.loadedScenarios.add(metadata['rho'])

                # Store metadata
                self.fileMetadata[filename] = metadata
                data_frames.append(df)
                loaded_count += 1

                logger.info(f"Successfully loaded {filename} with {len(df)} rows")

            except Exception as e:
                logger.error(f"Failed to process {filename}: {str(e)}")
                validation_results[filename] = {'valid': False, 'error': str(e)}
                continue

        # Combine all data
        if not data_frames:
            raise ValueError("No valid data files could be loaded")

        self.globalDataFrame = pd.concat(data_frames, ignore_index=True)
        logger.info(f"Combined dataset created with {len(self.globalDataFrame)} total rows from {loaded_count} files")
        logger.info(f"Loaded policies: {sorted(self.loadedPolicies)}")
        logger.info(f"Loaded scenarios: {sorted(self.loadedScenarios)}")

        # Generate validation report
        self._generateValidationReport(validation_results)

        return self.globalDataFrame

    def performEnhancedDataCleaning(self) -> pd.DataFrame:
        """
        @brief Performs comprehensive data cleaning and feature engineering for ALL data
        @return Cleaned and enhanced DataFrame
        """
        initial_row_count = len(self.globalDataFrame)

        logger.info("Starting enhanced data cleaning for all scenarios")

        # Remove duplicates
        self.globalDataFrame = self.globalDataFrame.drop_duplicates()

        # Handle missing values with advanced strategy
        numeric_columns = self.globalDataFrame.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if self.globalDataFrame[col].isnull().sum() > 0:
                # Use forward fill for time series data, then median for remaining
                self.globalDataFrame[col] = self.globalDataFrame[col].fillna(method='ffill')
                self.globalDataFrame[col] = self.globalDataFrame[col].fillna(self.globalDataFrame[col].median())

        # Enhanced Feature Engineering
        logger.info("Performing advanced feature engineering for all policies and scenarios")

        # Queue system features
        self.globalDataFrame['total_queue_length'] = (
                self.globalDataFrame['q0_len'] +
                self.globalDataFrame['q1_len'] +
                self.globalDataFrame['q2_len']
        )

        self.globalDataFrame['queue_imbalance'] = (
            self.globalDataFrame[['q0_len', 'q1_len', 'q2_len']].std(axis=1)
        )

        self.globalDataFrame['system_utilization'] = (
                self.globalDataFrame['total_occupancy'] /
                (self.globalDataFrame['total_occupancy'].max() + 1e-6)
        )

        # Rate-based features
        self.globalDataFrame['throughput_efficiency'] = (
                self.globalDataFrame['system_lambda'] /
                (self.globalDataFrame['arrival_rate_est'] + 1e-6)
        )

        # Load category with proper binning for all 4 scenarios
        self.globalDataFrame['load_category'] = pd.cut(
            self.globalDataFrame['load_factor'],
            bins=[0.7, 0.85, 0.95, 1.0],
            labels=['Low (0.8)', 'Medium (0.9)', 'High (0.95-0.999)']
        )

        # Policy categorization
        self.globalDataFrame['policy_type'] = self.globalDataFrame['policy_name'].apply(
            lambda x: 'PROTAGONIST' if x in AnalysisConfiguration.PROTAGONIST_POLICIES else 'SUPPORTING'
        )

        final_row_count = len(self.globalDataFrame)
        self.cleaningReport = {
            'initial_rows': initial_row_count,
            'final_rows': final_row_count,
            'rows_removed': initial_row_count - final_row_count,
            'cleaning_percentage': ((initial_row_count - final_row_count) / initial_row_count * 100),
            'total_policies': len(self.loadedPolicies),
            'total_scenarios': len(self.loadedScenarios)
        }

        logger.info(f"Enhanced data cleaning completed: {self.cleaningReport}")
        return self.globalDataFrame

    def _generateValidationReport(self, validation_results: Dict):
        """
        @brief Generates comprehensive validation report
        @param validation_results: Dictionary with validation results
        """
        valid_files = [f for f, result in validation_results.items() if result.get('valid', False)]
        invalid_files = [f for f, result in validation_results.items() if not result.get('valid', False)]

        report = {
            'total_files_processed': len(validation_results),
            'valid_files': len(valid_files),
            'invalid_files': len(invalid_files),
            'validation_rate': len(valid_files) / len(validation_results) * 100,
            'invalid_files_details': invalid_files
        }

        self.validationReport = report
        logger.info(f"Validation completed: {report['valid_files']}/{report['total_files_processed']} files valid")


# =================================================================================
# COMPREHENSIVE SCIENTIFIC VISUALIZATION ENGINE - ENHANCED
# =================================================================================
class EnhancedScientificVisualizationEngine:
    """
    @brief Enhanced visualization engine with special focus on protagonist policies
    """

    def __init__(self, dataFrame: pd.DataFrame):
        self.df = dataFrame
        self.plotCounter = 1
        self.captionRegistry = {}

        # Set professional plotting style
        plt.style.use('seaborn-v0_8-whitegrid')
        sns.set_palette("husl")
        plt.rcParams['figure.dpi'] = AnalysisConfiguration.DPI
        plt.rcParams['savefig.dpi'] = AnalysisConfiguration.DPI
        plt.rcParams['figure.figsize'] = AnalysisConfiguration.FIG_SIZE_MEDIUM

        # Color scheme for protagonist policies
        self.protagonist_colors = {
            'MAX_AVG_WAIT': '#FF6B6B',  # Red
            'ROUND_ROBIN': '#4ECDC4',  # Teal
            'SALLES_UTILITY': '#45B7D1'  # Blue
        }

        # Color scheme for load scenarios
        self.load_colors = {
            0.800: '#2E86AB',
            0.900: '#A23B72',
            0.950: '#F18F01',
            0.999: '#C73E1D'
        }

    def savePlotWithScientificCaption(self, figure: plt.Figure, plotName: str,
                                      captionTitle: str, scientificCaption: str):
        """
        @brief Saves plot and corresponding scientific caption with detailed documentation
        @param figure: Matplotlib figure object
        @param plotName: Descriptive name for the plot
        @param captionTitle: Formal title of the analysis
        @param scientificCaption: Comprehensive scientific justification
        """
        # Save high-resolution plot
        plotFilename = f"plot_{self.plotCounter:02d}_{plotName}.png"
        plotPath = Path(AnalysisConfiguration.PLOTS_PATH) / plotFilename
        figure.savefig(plotPath, dpi=AnalysisConfiguration.DPI, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
        plt.close(figure)

        # Save detailed scientific caption
        captionFilename = f"plot_{self.plotCounter:02d}_{plotName}_caption.txt"
        captionPath = Path(AnalysisConfiguration.CAPTIONS_PATH) / captionFilename

        captionContent = f"""
SCIENTIFIC ANALYSIS: {captionTitle.upper()}
================================================================================
PLOT ID: {self.plotCounter:02d}
FILENAME: {plotFilename}
GENERATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
DATA: {len(self.df):,} samples from {self.df['policy_name'].nunique()} policies × {self.df['load_factor'].nunique()} load scenarios

HYPOTHESIS:
{scientificCaption.split('HYPOTHESIS:')[1].split('EXPECTED INSIGHTS:')[0].strip()}

EXPECTED INSIGHTS:
{scientificCaption.split('EXPECTED INSIGHTS:')[1].split('METHODOLOGY:')[0].strip()}

METHODOLOGY:
{scientificCaption.split('METHODOLOGY:')[1].split('IMPACT:')[0].strip()}

IMPACT:
{scientificCaption.split('IMPACT:')[1].strip()}

SPECIAL FOCUS: Policies {', '.join(AnalysisConfiguration.PROTAGONIST_POLICIES)} are highlighted for comparative analysis.
"""

        with open(captionPath, 'w', encoding='utf-8') as f:
            f.write(captionContent)

        # Register plot in catalog
        self.captionRegistry[self.plotCounter] = {
            'plot_name': plotName,
            'caption_title': captionTitle,
            'filename': plotFilename
        }

        logger.info(f"Generated plot {self.plotCounter:02d}: {plotName}")
        self.plotCounter += 1

    def plot01_TemporalEvolutionAllScenarios(self):
        """
        @brief Plot 1: Temporal evolution across ALL 4 load scenarios with protagonist highlight
        """
        logger.info("Creating temporal evolution analysis for all 4 load scenarios")

        fig, axes = plt.subplots(4, 3, figsize=(24, 16))

        for load_idx, load_factor in enumerate(AnalysisConfiguration.LOAD_SCENARIOS):
            scenario_data = self.df[self.df['load_factor'] == load_factor]

            # Sample for performance
            sampled_data = scenario_data.iloc[::AnalysisConfiguration.TIME_SERIES_SAMPLE_STEP]

            # Get all policies for this scenario
            policies_present = sampled_data['policy_name'].unique()

            # Plot System EN
            for policy in policies_present:
                policy_data = sampled_data[sampled_data['policy_name'] == policy]
                if not policy_data.empty:
                    color = self.protagonist_colors.get(policy, 'gray')
                    linewidth = 2.0 if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 1.0
                    alpha = 0.9 if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 0.5
                    linestyle = '-' if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else '--'

                    axes[load_idx, 0].plot(policy_data['time'], policy_data['system_EN'],
                                           label=policy, linewidth=linewidth, alpha=alpha,
                                           linestyle=linestyle, color=color)

            axes[load_idx, 0].set_title(f'System EN Evolution @ ρ={load_factor}', fontsize=12, fontweight='bold')
            axes[load_idx, 0].set_ylabel('Expected Number')
            axes[load_idx, 0].grid(True, alpha=0.3)
            if load_idx == 0:
                axes[load_idx, 0].legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)

            # Plot System EW
            for policy in policies_present:
                policy_data = sampled_data[sampled_data['policy_name'] == policy]
                if not policy_data.empty:
                    color = self.protagonist_colors.get(policy, 'gray')
                    linewidth = 2.0 if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 1.0
                    alpha = 0.9 if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 0.5
                    linestyle = '-' if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else '--'

                    axes[load_idx, 1].plot(policy_data['time'], policy_data['system_EW'],
                                           label=policy, linewidth=linewidth, alpha=alpha,
                                           linestyle=linestyle, color=color)

            axes[load_idx, 1].set_title(f'System EW Evolution @ ρ={load_factor}', fontsize=12, fontweight='bold')
            axes[load_idx, 1].set_ylabel('Expected Wait')
            axes[load_idx, 1].grid(True, alpha=0.3)

            # Plot Little's Error
            for policy in policies_present:
                policy_data = sampled_data[sampled_data['policy_name'] == policy]
                if not policy_data.empty:
                    color = self.protagonist_colors.get(policy, 'gray')
                    linewidth = 2.0 if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 1.0
                    alpha = 0.9 if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 0.5
                    linestyle = '-' if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else '--'

                    axes[load_idx, 2].plot(policy_data['time'], policy_data['little_error'].abs(),
                                           label=policy, linewidth=linewidth, alpha=alpha,
                                           linestyle=linestyle, color=color)

            axes[load_idx, 2].set_title(f'Little\'s Error Evolution @ ρ={load_factor}', fontsize=12, fontweight='bold')
            axes[load_idx, 2].set_ylabel('|Little Error|')
            axes[load_idx, 2].set_xlabel('Time (s)')
            axes[load_idx, 2].grid(True, alpha=0.3)
            axes[load_idx, 2].set_yscale('log')

        plt.tight_layout()

        caption = """
HYPOTHESIS: Different scheduling policies exhibit distinct temporal convergence patterns
             across all four load scenarios (ρ=0.800, 0.900, 0.950, 0.999), with protagonist
             policies showing superior stability and performance characteristics.

EXPECTED INSIGHTS:
  - Protagonist policies maintain stability across load spectrum
  - System behavior becomes increasingly divergent at higher loads
  - Little's Law validation quality varies by policy and load
  - Critical load (ρ=0.999) reveals fundamental policy limitations

METHODOLOGY: Comprehensive time series analysis across all 4 load scenarios (rows) and
              3 key metrics (columns: EN, EW, Little Error) with protagonist policies
              highlighted for clear comparative analysis.

IMPACT: Provides complete understanding of policy temporal behavior across operational
         spectrum, enabling robust policy selection for varying load conditions.
"""
        self.savePlotWithScientificCaption(fig, "temporal_evolution_all_scenarios",
                                           "Comprehensive Temporal Analysis Across All Load Scenarios", caption)

    def plot02_QueueDistributionViolinAllLoads(self):
        """
        @brief Plot 2: Queue length distributions across ALL policies and ALL loads
        """
        logger.info("Creating comprehensive queue distribution analysis")

        fig, axes = plt.subplots(4, 3, figsize=(24, 16))

        for load_idx, load_factor in enumerate(AnalysisConfiguration.LOAD_SCENARIOS):
            load_data = self.df[self.df['load_factor'] == load_factor]

            # Sample for performance
            sampled_data = load_data.sample(n=min(2000, len(load_data)), random_state=42)

            for queue_idx in range(3):
                queue_data = []
                labels = []

                # Prepare data for violin plot
                for policy in sorted(sampled_data['policy_name'].unique()):
                    policy_queue_data = sampled_data[sampled_data['policy_name'] == policy][f'q{queue_idx}_len']
                    if len(policy_queue_data) > 0:
                        queue_data.append(policy_queue_data)
                        labels.append(policy)

                # Create violin plot
                violin_parts = axes[load_idx, queue_idx].violinplot(queue_data, showmeans=True, showmedians=True)

                # Color protagonist policies
                for i, label in enumerate(labels):
                    if label in AnalysisConfiguration.PROTAGONIST_POLICIES:
                        color = self.protagonist_colors[label]
                        violin_parts['bodies'][i].set_facecolor(color)
                        violin_parts['bodies'][i].set_alpha(0.7)

                axes[load_idx, queue_idx].set_title(f'Queue {queue_idx} @ ρ={load_factor}', fontweight='bold')
                axes[load_idx, queue_idx].set_ylabel('Queue Length')
                axes[load_idx, queue_idx].set_xticks(range(1, len(labels) + 1))
                axes[load_idx, queue_idx].set_xticklabels(labels, rotation=45, ha='right')
                axes[load_idx, queue_idx].grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        caption = """
HYPOTHESIS: Queue length distributions reveal fundamental policy characteristics
             and load-balancing strategies across all load scenarios, with protagonist
             policies demonstrating superior distribution properties.

EXPECTED INSIGHTS:
  - Protagonist policies show more balanced queue distributions
  - Distribution shapes reveal policy fairness characteristics
  - High load scenarios amplify policy differences
  - Tail behavior indicates congestion management capability

METHODOLOGY: Comprehensive violin plot analysis showing queue length distributions
              for all 3 queues (columns) across all 4 load scenarios (rows) for
              all 11 scheduling policies, with protagonist policies highlighted.

IMPACT: Identifies policies with desirable queue distribution properties for
         applications requiring fairness, load balancing, and predictable performance.
"""
        self.savePlotWithScientificCaption(fig, "queue_distributions_all_loads",
                                           "Queue Distribution Analysis Across All Load Scenarios", caption)

    def plot03_ProtagonistPolicyDeepDive(self):
        """
        @brief Plot 3: Deep dive analysis focusing on the 3 protagonist policies
        """
        logger.info("Creating protagonist policy deep dive analysis")

        protagonist_data = self.df[self.df['policy_name'].isin(AnalysisConfiguration.PROTAGONIST_POLICIES)]

        fig, axes = plt.subplots(3, 4, figsize=(20, 15))

        # Metrics to analyze
        metrics = ['system_EW', 'system_EN', 'little_error', 'queue_imbalance']
        metric_names = ['System Expected Wait', 'System Expected Number',
                        'Little\'s Law Error', 'Queue Imbalance']

        for policy_idx, policy in enumerate(AnalysisConfiguration.PROTAGONIST_POLICIES):
            policy_data = protagonist_data[protagonist_data['policy_name'] == policy]

            for metric_idx, (metric, metric_name) in enumerate(zip(metrics, metric_names)):
                # Create boxplot for each load scenario
                boxplot_data = []
                load_labels = []

                for load in AnalysisConfiguration.LOAD_SCENARIOS:
                    load_metric_data = policy_data[policy_data['load_factor'] == load][metric]
                    if len(load_metric_data) > 0:
                        boxplot_data.append(load_metric_data)
                        load_labels.append(f'ρ={load}')

                if boxplot_data:
                    box = axes[policy_idx, metric_idx].boxplot(boxplot_data, labels=load_labels,
                                                               patch_artist=True)

                    # Color boxes by load
                    for patch, load in zip(box['boxes'], AnalysisConfiguration.LOAD_SCENARIOS):
                        patch.set_facecolor(self.load_colors[load])
                        patch.set_alpha(0.7)

                    axes[policy_idx, metric_idx].set_title(f'{policy}\n{metric_name}', fontweight='bold')
                    axes[policy_idx, metric_idx].set_ylabel(metric_name)
                    axes[policy_idx, metric_idx].grid(True, alpha=0.3, axis='y')

                    if metric == 'little_error':
                        axes[policy_idx, metric_idx].set_yscale('log')

        plt.tight_layout()

        caption = """
HYPOTHESIS: The three protagonist policies (MAX_AVG_WAIT, ROUND_ROBIN, SALLES_UTILITY)
             exhibit distinct performance characteristics across different load scenarios,
             with each policy excelling in specific operational regimes.

EXPECTED INSIGHTS:
  - MAX_AVG_WAIT: Optimizes for wait time minimization across loads
  - ROUND_ROBIN: Provides consistent fairness but may sacrifice optimality
  - SALLES_UTILITY: Balances multiple objectives using utility optimization
  - Each policy shows different sensitivity to increasing load

METHODOLOGY: Comprehensive boxplot analysis of 4 key metrics (columns) for each of the
              3 protagonist policies (rows) across all 4 load scenarios, enabling
              detailed comparative performance assessment.

IMPACT: Enables informed selection among protagonist policies based on specific
         application requirements and expected load conditions.
"""
        self.savePlotWithScientificCaption(fig, "protagonist_policy_deep_dive",
                                           "Protagonist Policy Comparative Analysis", caption)

    def plot04_LoadScenarioComparativeAnalysis(self):
        """
        @brief Plot 4: Comparative analysis across all 4 load scenarios
        """
        logger.info("Creating load scenario comparative analysis")

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # Plot 4.1: Performance heatmap across loads and policies
        performance_matrix = self.df.groupby(['policy_name', 'load_factor'])['system_EW'].mean().unstack()

        im1 = axes[0, 0].imshow(performance_matrix.values, cmap='YlOrRd', aspect='auto')
        axes[0, 0].set_xticks(range(len(performance_matrix.columns)))
        axes[0, 0].set_yticks(range(len(performance_matrix.index)))
        axes[0, 0].set_xticklabels([f'ρ={col}' for col in performance_matrix.columns], rotation=45)
        axes[0, 0].set_yticklabels(performance_matrix.index)
        axes[0, 0].set_title('Average System EW\nAcross Policies and Loads', fontweight='bold')
        plt.colorbar(im1, ax=axes[0, 0], label='System Expected Wait')

        # Highlight protagonist policies
        for i, policy in enumerate(performance_matrix.index):
            if policy in AnalysisConfiguration.PROTAGONIST_POLICIES:
                axes[0, 0].get_yticklabels()[i].set_color(self.protagonist_colors[policy])
                axes[0, 0].get_yticklabels()[i].set_fontweight('bold')

        # Plot 4.2: Performance degradation from low to high load
        low_load_perf = performance_matrix[0.800]
        high_load_perf = performance_matrix[0.999]
        degradation_ratio = (high_load_perf - low_load_perf) / low_load_perf

        sorted_policies = degradation_ratio.sort_values(ascending=False).index
        sorted_degradation = degradation_ratio.loc[sorted_policies]

        colors = [self.protagonist_colors.get(policy, 'gray') for policy in sorted_policies]
        axes[0, 1].barh(range(len(sorted_policies)), sorted_degradation.values, color=colors, alpha=0.7)
        axes[0, 1].set_yticks(range(len(sorted_policies)))
        axes[0, 1].set_yticklabels(sorted_policies)
        axes[0, 1].set_xlabel('Performance Degradation Ratio\n(High Load vs Low Load)')
        axes[0, 1].set_title('Load Sensitivity Ranking', fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3, axis='x')

        # Plot 4.3: Stability across loads (Little's Law error)
        stability_matrix = self.df.groupby(['policy_name', 'load_factor'])['little_error'].abs().mean().unstack()

        x = np.arange(len(AnalysisConfiguration.LOAD_SCENARIOS))
        width = 0.8 / len(AnalysisConfiguration.PROTAGONIST_POLICIES)

        for i, policy in enumerate(AnalysisConfiguration.PROTAGONIST_POLICIES):
            if policy in stability_matrix.index:
                policy_stability = stability_matrix.loc[policy].values
                axes[1, 0].bar(x + i * width, policy_stability, width,
                               label=policy, color=self.protagonist_colors[policy], alpha=0.8)

        axes[1, 0].set_xticks(x + width)
        axes[1, 0].set_xticklabels([f'ρ={load}' for load in AnalysisConfiguration.LOAD_SCENARIOS])
        axes[1, 0].set_ylabel('Mean |Little Error|')
        axes[1, 0].set_title('Stability: Little\'s Law Error\n(Protagonist Policies)', fontweight='bold')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].set_yscale('log')

        # Plot 4.4: Queue utilization patterns
        queue_utilization = self.df.groupby(['policy_name', 'load_factor'])[['q0_len', 'q1_len', 'q2_len']].mean()

        # Focus on critical load
        critical_load_utilization = queue_utilization.xs(0.999, level='load_factor')

        x = np.arange(len(critical_load_utilization.index))
        width = 0.25

        for i, policy in enumerate(critical_load_utilization.index):
            color = self.protagonist_colors.get(policy, 'gray')
            alpha = 0.9 if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 0.5

            axes[1, 1].bar(x[i] - width, critical_load_utilization.loc[policy, 'q0_len'],
                           width, label='Q0' if i == 0 else "", color=color, alpha=alpha)
            axes[1, 1].bar(x[i], critical_load_utilization.loc[policy, 'q1_len'],
                           width, label='Q1' if i == 0 else "", color=color, alpha=alpha * 0.8)
            axes[1, 1].bar(x[i] + width, critical_load_utilization.loc[policy, 'q2_len'],
                           width, label='Q2' if i == 0 else "", color=color, alpha=alpha * 0.6)

        axes[1, 1].set_xticks(x)
        axes[1, 1].set_xticklabels(critical_load_utilization.index, rotation=45, ha='right')
        axes[1, 1].set_ylabel('Mean Queue Length')
        axes[1, 1].set_title('Queue Utilization @ Critical Load (ρ=0.999)', fontweight='bold')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        caption = """
HYPOTHESIS: Load sensitivity and performance degradation patterns vary significantly
             across policies, with protagonist policies demonstrating superior
             robustness and consistent behavior across the operational spectrum.

EXPECTED INSIGHTS:
  - Policies show dramatically different sensitivity to increasing load
  - Protagonist policies maintain better stability across load conditions
  - Queue utilization patterns reveal fundamental policy strategies
  - Critical load conditions separate robust from fragile policies

METHODOLOGY: Multi-faceted comparative analysis including performance heatmaps,
              load sensitivity ranking, stability assessment, and queue utilization
              patterns across all policies and load scenarios.

IMPACT: Critical for capacity planning and policy selection in environments with
         varying load conditions, ensuring robust performance across operational spectrum.
"""
        self.savePlotWithScientificCaption(fig, "load_scenario_comparative_analysis",
                                           "Comprehensive Load Scenario Analysis", caption)

    def plot05_CorrelationAnalysisMatrix(self):
        """
        @brief Plot 5: Comprehensive correlation analysis for all metrics
        """
        logger.info("Creating comprehensive correlation analysis")

        # Select key numerical features
        numerical_features = [
            'total_occupancy', 'arrival_rate_est', 'q0_len', 'q1_len', 'q2_len',
            'system_EN', 'system_EW', 'system_lambda', 'little_error',
            'queue_imbalance', 'system_utilization', 'throughput_efficiency'
        ]

        numerical_features = [col for col in numerical_features if col in self.df.columns]
        correlation_matrix = self.df[numerical_features].corr()

        fig, axes = plt.subplots(2, 2, figsize=(18, 14))

        # Plot 5.1: Full correlation matrix
        im0 = axes[0, 0].imshow(correlation_matrix, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
        axes[0, 0].set_xticks(range(len(numerical_features)))
        axes[0, 0].set_yticks(range(len(numerical_features)))
        axes[0, 0].set_xticklabels(numerical_features, rotation=45, ha='right', fontsize=8)
        axes[0, 0].set_yticklabels(numerical_features, fontsize=8)
        axes[0, 0].set_title('Complete Correlation Matrix', fontweight='bold')
        plt.colorbar(im0, ax=axes[0, 0])

        # Add correlation values
        for i in range(len(numerical_features)):
            for j in range(len(numerical_features)):
                axes[0, 0].text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}',
                                ha='center', va='center', fontsize=6)

        # Plot 5.2: System EW correlation with other metrics
        ew_correlations = correlation_matrix['system_EW'].drop('system_EW').sort_values(ascending=False)

        axes[0, 1].barh(range(len(ew_correlations)), ew_correlations.values, alpha=0.7, color='steelblue')
        axes[0, 1].set_yticks(range(len(ew_correlations)))
        axes[0, 1].set_yticklabels(ew_correlations.index)
        axes[0, 1].set_xlabel('Correlation with System EW')
        axes[0, 1].set_title('Feature Correlation with System Wait Time', fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3, axis='x')
        axes[0, 1].axvline(x=0, color='black', linewidth=0.5)

        # Plot 5.3: Correlation by load scenario
        correlation_by_load = []
        for load in AnalysisConfiguration.LOAD_SCENARIOS:
            load_data = self.df[self.df['load_factor'] == load]
            if len(load_data) > 0:
                load_corr = load_data[['system_EW', 'system_EN', 'arrival_rate_est']].corr().iloc[0, 1:].values
                correlation_by_load.append(load_corr)

        correlation_by_load = np.array(correlation_by_load)

        x = np.arange(len(AnalysisConfiguration.LOAD_SCENARIOS))
        width = 0.25

        axes[1, 0].bar(x - width, correlation_by_load[:, 0], width, label='EW vs EN', alpha=0.8)
        axes[1, 0].bar(x, correlation_by_load[:, 1], width, label='EW vs Arrival Rate', alpha=0.8)

        axes[1, 0].set_xticks(x)
        axes[1, 0].set_xticklabels([f'ρ={load}' for load in AnalysisConfiguration.LOAD_SCENARIOS])
        axes[1, 0].set_ylabel('Correlation Coefficient')
        axes[1, 0].set_title('Key Correlations by Load Scenario', fontweight='bold')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].axhline(y=0, color='black', linewidth=0.5)

        # Plot 5.4: Policy-specific correlations
        protagonist_correlations = []
        for policy in AnalysisConfiguration.PROTAGONIST_POLICIES:
            policy_data = self.df[self.df['policy_name'] == policy]
            if len(policy_data) > 0:
                policy_corr = policy_data[['system_EW', 'system_EN']].corr().iloc[0, 1]
                protagonist_correlations.append(policy_corr)

        axes[1, 1].bar(AnalysisConfiguration.PROTAGONIST_POLICIES, protagonist_correlations,
                       color=[self.protagonist_colors[p] for p in AnalysisConfiguration.PROTAGONIST_POLICIES],
                       alpha=0.7)
        axes[1, 1].set_ylabel('Correlation (EW vs EN)')
        axes[1, 1].set_title('EW-EN Correlation: Protagonist Policies', fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        caption = """
HYPOTHESIS: Correlation patterns between system metrics reveal fundamental queueing
             relationships and policy-specific behavioral characteristics, with
             protagonist policies showing distinct correlation signatures.

EXPECTED INSIGHTS:
  - Strong correlations indicate fundamental queueing relationships
  - Correlation strength varies by load scenario and policy
  - Protagonist policies may exhibit unique correlation patterns
  - Understanding correlations enables feature selection for predictive modeling

METHODOLOGY: Comprehensive correlation analysis including complete correlation matrix,
              feature importance for wait time prediction, load-dependent correlation
              patterns, and policy-specific correlation characteristics.

IMPACT: Reveals fundamental system relationships and supports feature engineering
         for machine learning models and system optimization.
"""
        self.savePlotWithScientificCaption(fig, "comprehensive_correlation_analysis",
                                           "Multi-dimensional Correlation Analysis", caption)

    def plot06_PerformanceRadarAllPolicies(self):
        """
        @brief Plot 6: Radar chart comparing ALL policies across multiple metrics
        """
        logger.info("Creating performance radar chart for all policies")

        # Calculate normalized performance metrics for each policy
        metrics = ['system_EW', 'system_EN', 'little_error', 'queue_imbalance', 'throughput_efficiency']
        policy_metrics = self.df.groupby('policy_name')[metrics].mean()

        # Normalize metrics (lower is better for most, except throughput efficiency)
        normalized_metrics = policy_metrics.copy()
        for metric in metrics:
            if metric == 'throughput_efficiency':
                # Higher is better
                normalized_metrics[metric] = (policy_metrics[metric] - policy_metrics[metric].min()) / \
                                             (policy_metrics[metric].max() - policy_metrics[metric].min())
            else:
                # Lower is better
                normalized_metrics[metric] = 1 - (policy_metrics[metric] - policy_metrics[metric].min()) / \
                                             (policy_metrics[metric].max() - policy_metrics[metric].min())

        # Create radar chart
        fig, axes = plt.subplots(2, 2, figsize=(16, 12), subplot_kw=dict(projection='polar'))
        axes = axes.flatten()

        # Plot all policies in groups for clarity
        all_policies = sorted(normalized_metrics.index)
        policy_groups = [all_policies[i:i + 4] for i in range(0, len(all_policies), 4)]

        for idx, policy_group in enumerate(policy_groups):
            if idx >= len(axes):
                break

            ax = axes[idx]
            angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
            angles += angles[:1]  # Complete the circle

            for policy in policy_group:
                values = normalized_metrics.loc[policy].values.tolist()
                values += values[:1]  # Complete the circle

                color = self.protagonist_colors.get(policy, 'gray')
                linewidth = 3 if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 1.5
                alpha = 0.9 if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 0.6

                ax.plot(angles, values, 'o-', linewidth=linewidth, label=policy,
                        alpha=alpha, color=color)
                ax.fill(angles, values, alpha=0.1, color=color)

            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(metrics)
            ax.set_ylim(0, 1)
            ax.set_title(f'Performance Comparison: Policies {idx + 1}', fontweight='bold')
            ax.legend(bbox_to_anchor=(1.1, 1.0), loc='upper left')
            ax.grid(True)

        plt.tight_layout()

        caption = """
HYPOTHESIS: Each scheduling policy exhibits a unique multi-dimensional performance
             profile, with tradeoffs between different metrics revealing fundamental
             design choices and optimization objectives.

EXPECTED INSIGHTS:
  - No single policy dominates all performance dimensions
  - Protagonist policies show balanced performance profiles
  - Clear tradeoffs exist between wait time, throughput, and stability
  - Radar visualization enables comprehensive policy comparison

METHODOLOGY: Radar chart visualization of normalized performance across 5 key metrics
              for all policies, grouped for clarity, with protagonist policies
              highlighted for easy identification and comparison.

IMPACT: Supports multi-criteria decision making by visualizing complex tradeoffs
         and enabling policy selection based on application-specific requirements.
"""
        self.savePlotWithScientificCaption(fig, "performance_radar_all_policies",
                                           "Comprehensive Policy Performance Radar Analysis", caption)

    def plot07_StatisticalDistributionAnalysis(self):
        """
        @brief Plot 7: Advanced statistical distribution analysis
        """
        logger.info("Creating statistical distribution analysis")

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # Focus on critical load for distribution analysis
        critical_data = self.df[self.df['load_factor'] == 0.999]

        # Plot 7.1: System EW distribution comparison
        ew_data = []
        labels = []
        for policy in sorted(critical_data['policy_name'].unique()):
            policy_ew = critical_data[critical_data['policy_name'] == policy]['system_EW']
            if len(policy_ew) > 0:
                ew_data.append(policy_ew)
                labels.append(policy)

        box = axes[0, 0].boxplot(ew_data, labels=labels, patch_artist=True)

        # Color protagonist policies
        for i, label in enumerate(labels):
            if label in AnalysisConfiguration.PROTAGONIST_POLICIES:
                box['boxes'][i].set_facecolor(self.protagonist_colors[label])
                box['boxes'][i].set_alpha(0.7)

        axes[0, 0].set_xticklabels(labels, rotation=45, ha='right')
        axes[0, 0].set_ylabel('System Expected Wait')
        axes[0, 0].set_title('System EW Distribution @ Critical Load (ρ=0.999)', fontweight='bold')
        axes[0, 0].grid(True, alpha=0.3, axis='y')

        # Plot 7.2: Q-Q plot for protagonist policies
        for policy in AnalysisConfiguration.PROTAGONIST_POLICIES:
            policy_data = critical_data[critical_data['policy_name'] == policy]['system_EW']
            if len(policy_data) > 0:
                stats.probplot(policy_data, dist="norm", plot=axes[0, 1])
        axes[0, 1].set_title('Q-Q Plot: System EW Normality\n(Protagonist Policies)', fontweight='bold')

        # Plot 7.3: Cumulative distribution functions
        for policy in AnalysisConfiguration.PROTAGONIST_POLICIES:
            policy_data = critical_data[critical_data['policy_name'] == policy]['system_EW']
            if len(policy_data) > 0:
                sorted_data = np.sort(policy_data)
                yvals = np.arange(len(sorted_data)) / float(len(sorted_data))
                axes[1, 0].plot(sorted_data, yvals, label=policy, linewidth=2,
                                color=self.protagonist_colors[policy])

        axes[1, 0].set_xlabel('System Expected Wait')
        axes[1, 0].set_ylabel('Cumulative Probability')
        axes[1, 0].set_title('CDF: System EW Distribution\n(Protagonist Policies)', fontweight='bold')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)

        # Plot 7.4: Statistical moments comparison
        moments_data = []
        for policy in AnalysisConfiguration.PROTAGONIST_POLICIES:
            policy_data = critical_data[critical_data['policy_name'] == policy]['system_EW']
            if len(policy_data) > 0:
                moments = {
                    'Policy': policy,
                    'Mean': policy_data.mean(),
                    'Std': policy_data.std(),
                    'Skewness': policy_data.skew(),
                    'Kurtosis': policy_data.kurtosis()
                }
                moments_data.append(moments)

        moments_df = pd.DataFrame(moments_data)
        x = np.arange(len(AnalysisConfiguration.PROTAGONIST_POLICIES))
        width = 0.2

        colors = [self.protagonist_colors[p] for p in AnalysisConfiguration.PROTAGONIST_POLICIES]

        axes[1, 1].bar(x - width * 1.5, moments_df['Mean'], width, label='Mean', alpha=0.8, color=colors)
        axes[1, 1].bar(x - width / 2, moments_df['Std'], width, label='Std Dev', alpha=0.8, color=colors)
        axes[1, 1].bar(x + width / 2, moments_df['Skewness'], width, label='Skewness', alpha=0.8, color=colors)
        axes[1, 1].bar(x + width * 1.5, moments_df['Kurtosis'], width, label='Kurtosis', alpha=0.8, color=colors)

        axes[1, 1].set_xlabel('Protagonist Policy')
        axes[1, 1].set_ylabel('Moment Value')
        axes[1, 1].set_title('Statistical Moments Comparison\n@ Critical Load', fontweight='bold')
        axes[1, 1].set_xticks(x)
        axes[1, 1].set_xticklabels(AnalysisConfiguration.PROTAGONIST_POLICIES)
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        caption = """
HYPOTHESIS: System performance metrics follow characteristic probability distributions
             that reveal fundamental policy behavior patterns, with statistical moments
             providing insights into stability, predictability, and risk characteristics.

EXPECTED INSIGHTS:
  - Distribution shapes reveal policy performance characteristics
  - Statistical moments quantify stability and predictability
  - Normality deviations indicate non-Gaussian system behavior
  - Heavy-tailed distributions suggest performance risk

METHODOLOGY: Comprehensive distribution analysis using boxplots for spread comparison,
              Q-Q plots for normality assessment, CDFs for performance guarantees,
              and statistical moments for behavioral characterization at critical load.

IMPACT: Provides deep understanding of performance risk profiles and statistical
         properties essential for service level agreement (SLA) planning and
         reliability engineering.
"""
        self.savePlotWithScientificCaption(fig, "statistical_distribution_analysis",
                                           "Advanced Statistical Distribution Analysis", caption)

    def plot08_LittlesLawValidationComprehensive(self):
        """
        @brief Plot 8: Comprehensive Little's Law validation across ALL scenarios
        """
        logger.info("Creating comprehensive Little's Law validation")

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # Plot 8.1: Little's Law error by policy and load
        error_matrix = self.df.groupby(['policy_name', 'load_factor'])['little_error'].abs().mean().unstack()

        im0 = axes[0, 0].imshow(error_matrix.values, cmap='viridis_r', aspect='auto')
        axes[0, 0].set_xticks(range(len(error_matrix.columns)))
        axes[0, 0].set_yticks(range(len(error_matrix.index)))
        axes[0, 0].set_xticklabels([f'ρ={col}' for col in error_matrix.columns], rotation=45)
        axes[0, 0].set_yticklabels(error_matrix.index)
        axes[0, 0].set_title("Little's Law Error Heatmap", fontweight='bold')
        axes[0, 0].set_xlabel('Load Factor')
        axes[0, 0].set_ylabel('Scheduling Policy')
        plt.colorbar(im0, ax=axes[0, 0], label='Mean |Little Error|')

        # Highlight protagonist policies
        for i, policy in enumerate(error_matrix.index):
            if policy in AnalysisConfiguration.PROTAGONIST_POLICIES:
                axes[0, 0].get_yticklabels()[i].set_color(self.protagonist_colors[policy])
                axes[0, 0].get_yticklabels()[i].set_fontweight('bold')

        # Plot 8.2: Little's Law validation scatter
        sample_data = self.df.sample(n=5000, random_state=42)
        theoretical_L = sample_data['system_lambda'] * sample_data['system_EW']
        actual_L = sample_data['system_EN']

        # Color by load factor
        scatter = axes[0, 1].scatter(theoretical_L, actual_L, c=sample_data['load_factor'],
                                     cmap='viridis', alpha=0.6, s=20)
        axes[0, 1].plot([theoretical_L.min(), theoretical_L.max()],
                        [theoretical_L.min(), theoretical_L.max()],
                        'r--', linewidth=2, label='Perfect Validation')
        axes[0, 1].set_xlabel('Theoretical L (λ × W)')
        axes[0, 1].set_ylabel('Actual L (EN)')
        axes[0, 1].set_title("Little's Law Validation: L = λW", fontweight='bold')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=axes[0, 1], label='Load Factor')

        # Plot 8.3: Error distribution by policy type
        protagonist_errors = self.df[self.df['policy_type'] == 'PROTAGONIST']['little_error'].abs()
        supporting_errors = self.df[self.df['policy_type'] == 'SUPPORTING']['little_error'].abs()

        box_data = [protagonist_errors, supporting_errors]
        box = axes[1, 0].boxplot(box_data, labels=['Protagonist', 'Supporting'], patch_artist=True)

        # Color boxes
        box['boxes'][0].set_facecolor('lightblue')
        box['boxes'][1].set_facecolor('lightgray')

        axes[1, 0].set_ylabel('Absolute Little Error')
        axes[1, 0].set_title("Little's Law Error by Policy Type", fontweight='bold')
        axes[1, 0].grid(True, alpha=0.3, axis='y')
        axes[1, 0].set_yscale('log')

        # Plot 8.4: Error trends across loads for protagonist policies
        for policy in AnalysisConfiguration.PROTAGONIST_POLICIES:
            policy_errors = []
            for load in AnalysisConfiguration.LOAD_SCENARIOS:
                load_error = self.df[
                    (self.df['policy_name'] == policy) &
                    (self.df['load_factor'] == load)
                    ]['little_error'].abs().mean()
                policy_errors.append(load_error)

            axes[1, 1].plot(AnalysisConfiguration.LOAD_SCENARIOS, policy_errors, 'o-',
                            label=policy, linewidth=2, markersize=8,
                            color=self.protagonist_colors[policy])

        axes[1, 1].set_xlabel('Load Factor (ρ)')
        axes[1, 1].set_ylabel('Mean |Little Error|')
        axes[1, 1].set_title("Little's Law Error Trends\n(Protagonist Policies)", fontweight='bold')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].set_yscale('log')

        plt.tight_layout()

        caption = """
HYPOTHESIS: Little's Law validation quality varies systematically across policies
             and load conditions, providing insights into simulation stability and
             policy-induced non-stationarities, with protagonist policies demonstrating
             superior theoretical consistency.

EXPECTED INSIGHTS:
  - Protagonist policies maintain better Little's Law validation
  - Error increases with load but patterns vary by policy
  - Policy type (protagonist vs supporting) correlates with validation quality
  - Systematic deviations may indicate implementation issues

METHODOLOGY: Comprehensive Little's Law validation using error heatmaps, direct
              law verification scatter plots, policy type comparison, and error
              trend analysis across the load spectrum.

IMPACT: Essential for simulation credibility assessment and identification of
         policies that maintain theoretical consistency under challenging conditions.
"""
        self.savePlotWithScientificCaption(fig, "littles_law_comprehensive_validation",
                                           "Little's Law Comprehensive Validation", caption)

    def plot09_BehavioralClusteringAnalysis(self):
        """
        @brief Plot 9: Behavioral clustering of ALL policies
        """
        logger.info("Creating behavioral clustering analysis")

        # Prepare features for clustering
        feature_columns = [
            'system_EW', 'system_EN', 'little_error', 'queue_imbalance',
            'throughput_efficiency', 'total_occupancy', 'arrival_rate_est'
        ]
        feature_columns = [col for col in feature_columns if col in self.df.columns]

        # Aggregate policy behavior (average across all scenarios)
        policy_features = self.df.groupby('policy_name')[feature_columns].mean()

        # Standardize features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(policy_features)

        # Perform PCA
        pca = PCA(n_components=2)
        principal_components = pca.fit_transform(scaled_features)

        # Perform clustering
        kmeans = KMeans(n_clusters=3, random_state=42)
        clusters = kmeans.fit_predict(scaled_features)

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # Plot 9.1: PCA visualization
        for i, policy in enumerate(policy_features.index):
            color = self.protagonist_colors.get(policy, 'gray')
            marker = 'o' if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 's'
            size = 100 if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 60
            alpha = 0.9 if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 0.6

            axes[0, 0].scatter(principal_components[i, 0], principal_components[i, 1],
                               c=[color], s=size, marker=marker, alpha=alpha, label=policy)

            # Add policy labels
            axes[0, 0].annotate(policy, (principal_components[i, 0], principal_components[i, 1]),
                                xytext=(5, 5), textcoords='offset points', fontsize=8,
                                fontweight='bold' if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 'normal')

        axes[0, 0].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} variance)')
        axes[0, 0].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} variance)')
        axes[0, 0].set_title('Policy Behavioral PCA', fontweight='bold')
        axes[0, 0].grid(True, alpha=0.3)

        # Plot 9.2: K-means clustering
        scatter = axes[0, 1].scatter(principal_components[:, 0], principal_components[:, 1],
                                     c=clusters, cmap='Set1', s=80, alpha=0.7)

        for i, policy in enumerate(policy_features.index):
            axes[0, 1].annotate(policy, (principal_components[i, 0], principal_components[i, 1]),
                                xytext=(5, 5), textcoords='offset points', fontsize=8,
                                fontweight='bold' if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 'normal')

        axes[0, 1].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} variance)')
        axes[0, 1].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} variance)')
        axes[0, 1].set_title('Policy Behavioral Clustering (K-means)', fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3)

        # Plot 9.3: Feature importance in PCA
        pca_loadings = pd.DataFrame(
            pca.components_.T,
            columns=['PC1', 'PC2'],
            index=feature_columns
        )

        # Plot top features for PC1
        top_features_pc1 = pca_loadings['PC1'].abs().nlargest(8)
        axes[1, 0].barh(range(len(top_features_pc1)), top_features_pc1.values, alpha=0.7, color='lightgreen')
        axes[1, 0].set_yticks(range(len(top_features_pc1)))
        axes[1, 0].set_yticklabels(top_features_pc1.index)
        axes[1, 0].set_xlabel('Absolute Loading')
        axes[1, 0].set_title('Top Feature Loadings on PC1', fontweight='bold')
        axes[1, 0].grid(True, alpha=0.3, axis='x')

        # Plot 9.4: Policy similarity matrix
        from sklearn.metrics.pairwise import cosine_similarity
        similarity_matrix = cosine_similarity(scaled_features)

        im = axes[1, 1].imshow(similarity_matrix, cmap='YlOrRd', aspect='auto', vmin=0, vmax=1)
        axes[1, 1].set_xticks(range(len(policy_features.index)))
        axes[1, 1].set_yticks(range(len(policy_features.index)))
        axes[1, 1].set_xticklabels(policy_features.index, rotation=45, ha='right', fontsize=8)
        axes[1, 1].set_yticklabels(policy_features.index, fontsize=8)
        axes[1, 1].set_title('Policy Behavioral Similarity Matrix', fontweight='bold')
        plt.colorbar(im, ax=axes[1, 1], label='Cosine Similarity')

        plt.tight_layout()

        caption = """
HYPOTHESIS: Scheduling policies form natural clusters in behavioral space based on
             their operational characteristics, with protagonist policies potentially
             defining distinct behavioral clusters or representing optimal points
             in the policy design space.

EXPECTED INSIGHTS:
  - Policies cluster by fundamental algorithmic characteristics
  - Protagonist policies may define cluster centroids or boundaries
  - Similarity matrix reveals policy families and relationships
  - Feature loadings identify key discriminative performance metrics

METHODOLOGY: Multi-method behavioral analysis combining PCA for dimensionality
              reduction, K-means clustering for group identification, feature
              importance analysis, and similarity matrix computation.

IMPACT: Enables policy taxonomy development, informed policy selection from
         similar families, and identification of unique vs redundant policies
         in the design space.
"""
        self.savePlotWithScientificCaption(fig, "behavioral_clustering_analysis",
                                           "Policy Behavioral Clustering Analysis", caption)

    def plot10_ComparativePerformanceDashboard(self):
        """
        @brief Plot 10: Comprehensive performance dashboard for ALL policies
        """
        logger.info("Creating comprehensive performance dashboard")

        # Calculate comprehensive performance metrics
        performance_metrics = self.df.groupby('policy_name').agg({
            'system_EW': ['mean', 'std', 'median', lambda x: x.quantile(0.95)],
            'system_EN': ['mean', 'std'],
            'little_error': lambda x: np.abs(x).mean(),
            'queue_imbalance': 'mean',
            'throughput_efficiency': 'mean'
        }).round(4)

        performance_metrics.columns = ['_'.join(col).strip() for col in performance_metrics.columns.values]
        performance_metrics.rename(columns={'system_EW_<lambda_0>': 'system_EW_p95'}, inplace=True)

        fig = plt.figure(figsize=(20, 16))

        # Create a comprehensive dashboard layout
        gs = fig.add_gridspec(3, 3)

        # Plot 10.1: Mean performance comparison
        ax1 = fig.add_subplot(gs[0, 0])
        sorted_policies = performance_metrics['system_EW_mean'].sort_values().index

        colors = [self.protagonist_colors.get(policy, 'lightgray') for policy in sorted_policies]
        alphas = [0.9 if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 0.6 for policy in sorted_policies]

        bars = ax1.barh(range(len(sorted_policies)), performance_metrics.loc[sorted_policies, 'system_EW_mean'],
                        color=colors, alpha=alphas)
        ax1.set_yticks(range(len(sorted_policies)))
        ax1.set_yticklabels(sorted_policies)
        ax1.set_xlabel('Mean System EW')
        ax1.set_title('Performance Ranking: Mean Wait Time\n(Lower is Better)', fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')

        # Plot 10.2: Performance stability
        ax2 = fig.add_subplot(gs[0, 1])
        cv = performance_metrics['system_EW_std'] / performance_metrics['system_EW_mean']
        cv_sorted = cv.sort_values()

        colors = [self.protagonist_colors.get(policy, 'lightgray') for policy in cv_sorted.index]
        alphas = [0.9 if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 0.6 for policy in cv_sorted.index]

        ax2.barh(range(len(cv_sorted)), cv_sorted.values, color=colors, alpha=alphas)
        ax2.set_yticks(range(len(cv_sorted)))
        ax2.set_yticklabels(cv_sorted.index)
        ax2.set_xlabel('Coefficient of Variation')
        ax2.set_title('Performance Stability Ranking\n(Lower is Better)', fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')

        # Plot 10.3: 95th percentile performance
        ax3 = fig.add_subplot(gs[0, 2])
        p95_sorted = performance_metrics['system_EW_p95'].sort_values()

        colors = [self.protagonist_colors.get(policy, 'lightgray') for policy in p95_sorted.index]
        alphas = [0.9 if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 0.6 for policy in p95_sorted.index]

        ax3.barh(range(len(p95_sorted)), p95_sorted.values, color=colors, alpha=alphas)
        ax3.set_yticks(range(len(p95_sorted)))
        ax3.set_yticklabels(p95_sorted.index)
        ax3.set_xlabel('95th Percentile System EW')
        ax3.set_title('Tail Performance Ranking\n(Lower is Better)', fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='x')

        # Plot 10.4: Throughput efficiency vs performance
        ax4 = fig.add_subplot(gs[1, 0])
        for policy in performance_metrics.index:
            color = self.protagonist_colors.get(policy, 'gray')
            size = 100 if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 60
            alpha = 0.9 if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 0.6
            marker = 'o' if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 's'

            ax4.scatter(performance_metrics.loc[policy, 'throughput_efficiency_mean'],
                        performance_metrics.loc[policy, 'system_EW_mean'],
                        s=size, alpha=alpha, color=color, marker=marker, label=policy)

            if policy in AnalysisConfiguration.PROTAGONIST_POLICIES:
                ax4.annotate(policy,
                             (performance_metrics.loc[policy, 'throughput_efficiency_mean'],
                              performance_metrics.loc[policy, 'system_EW_mean']),
                             xytext=(5, 5), textcoords='offset points', fontweight='bold')

        ax4.set_xlabel('Throughput Efficiency')
        ax4.set_ylabel('Mean System EW')
        ax4.set_title('Efficiency vs Performance Tradeoff', fontweight='bold')
        ax4.grid(True, alpha=0.3)

        # Plot 10.5: Stability vs performance
        ax5 = fig.add_subplot(gs[1, 1])
        for policy in performance_metrics.index:
            color = self.protagonist_colors.get(policy, 'gray')
            size = 100 if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 60
            alpha = 0.9 if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 0.6
            marker = 'o' if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 's'

            ax5.scatter(performance_metrics.loc[policy, 'system_EW_mean'],
                        performance_metrics.loc[policy, 'little_error_<lambda_0>'],
                        s=size, alpha=alpha, color=color, marker=marker, label=policy)

            if policy in AnalysisConfiguration.PROTAGONIST_POLICIES:
                ax5.annotate(policy,
                             (performance_metrics.loc[policy, 'system_EW_mean'],
                              performance_metrics.loc[policy, 'little_error_<lambda_0>']),
                             xytext=(5, 5), textcoords='offset points', fontweight='bold')

        ax5.set_xlabel('Mean System EW')
        ax5.set_ylabel('Mean |Little Error|')
        ax5.set_title('Performance vs Stability', fontweight='bold')
        ax5.grid(True, alpha=0.3)

        # Plot 10.6: Load balancing quality
        ax6 = fig.add_subplot(gs[1, 2])
        imbalance_sorted = performance_metrics['queue_imbalance_mean'].sort_values()

        colors = [self.protagonist_colors.get(policy, 'lightgray') for policy in imbalance_sorted.index]
        alphas = [0.9 if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 0.6 for policy in
                  imbalance_sorted.index]

        ax6.barh(range(len(imbalance_sorted)), imbalance_sorted.values, color=colors, alpha=alphas)
        ax6.set_yticks(range(len(imbalance_sorted)))
        ax6.set_yticklabels(imbalance_sorted.index)
        ax6.set_xlabel('Mean Queue Imbalance')
        ax6.set_title('Load Balancing Quality\n(Lower is Better)', fontweight='bold')
        ax6.grid(True, alpha=0.3, axis='x')

        # Plot 10.7: Comprehensive scoring summary
        ax7 = fig.add_subplot(gs[2, :])

        # Normalize metrics for radar-like visualization
        normalized_metrics = performance_metrics.copy()
        for metric in ['system_EW_mean', 'system_EW_std', 'system_EW_p95', 'little_error_<lambda_0>',
                       'queue_imbalance_mean']:
            normalized_metrics[metric] = 1 - (performance_metrics[metric] - performance_metrics[metric].min()) / \
                                         (performance_metrics[metric].max() - performance_metrics[metric].min())

        # For throughput efficiency, higher is better
        normalized_metrics['throughput_efficiency_mean'] = (
                                                                   performance_metrics['throughput_efficiency_mean'] -
                                                                   performance_metrics[
                                                                       'throughput_efficiency_mean'].min()
                                                           ) / (
                                                                   performance_metrics[
                                                                       'throughput_efficiency_mean'].max() -
                                                                   performance_metrics[
                                                                       'throughput_efficiency_mean'].min()
                                                           )

        # Focus on protagonist and a few supporting policies for clarity
        display_policies = list(AnalysisConfiguration.PROTAGONIST_POLICIES) + [
            p for p in performance_metrics.index
            if p not in AnalysisConfiguration.PROTAGONIST_POLICIES
        ][:3]  # Top 3 supporting policies

        radar_metrics = ['system_EW_mean', 'system_EW_std', 'system_EW_p95',
                         'little_error_<lambda_0>', 'queue_imbalance_mean', 'throughput_efficiency_mean']

        x = np.arange(len(radar_metrics))
        width = 0.15

        for i, policy in enumerate(display_policies):
            values = normalized_metrics.loc[policy, radar_metrics].values
            color = self.protagonist_colors.get(policy, 'lightgray')
            alpha = 0.9 if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 0.6

            ax7.bar(x + i * width, values, width, label=policy, alpha=alpha, color=color)

        ax7.set_xticks(x + width * len(display_policies) / 2)
        ax7.set_xticklabels(['Perf', 'Stability', 'Tail', 'Little', 'Balance', 'Efficiency'],
                            fontsize=10)
        ax7.set_ylabel('Normalized Score (Higher = Better)')
        ax7.set_title('Comprehensive Policy Performance Profile', fontweight='bold')
        ax7.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax7.grid(True, alpha=0.3)

        plt.tight_layout()

        caption = """
HYPOTHESIS: Comprehensive multi-metric evaluation reveals that protagonist policies
             generally achieve superior balanced performance across multiple dimensions,
             though specific supporting policies may excel in particular metrics.

EXPECTED INSIGHTS:
  - Protagonist policies show well-balanced performance profiles
  - No single policy dominates all evaluation dimensions
  - Clear tradeoffs exist between different performance metrics
  - Policy selection should consider application-specific requirements

METHODOLOGY: Comprehensive dashboard combining absolute performance rankings,
              stability assessments, tail behavior analysis, efficiency tradeoffs,
              stability relationships, load balancing quality, and multi-dimensional
              normalized scoring.

IMPACT: Provides complete decision support for policy selection based on multi-objective
         optimization considering specific performance requirements and operational constraints.
"""
        self.savePlotWithScientificCaption(fig, "comparative_performance_dashboard",
                                           "Comprehensive Policy Performance Dashboard", caption)

    def generateAllVisualizations(self):
        """
        @brief Executes ALL visualization methods in sequence
        """
        logger.info("Starting comprehensive visualization generation for ALL data")

        visualization_methods = [
            self.plot01_TemporalEvolutionAllScenarios,
            self.plot02_QueueDistributionViolinAllLoads,
            self.plot03_ProtagonistPolicyDeepDive,
            self.plot04_LoadScenarioComparativeAnalysis,
            self.plot05_CorrelationAnalysisMatrix,
            self.plot06_PerformanceRadarAllPolicies,
            self.plot07_StatisticalDistributionAnalysis,
            self.plot08_LittlesLawValidationComprehensive,
            self.plot09_BehavioralClusteringAnalysis,
            self.plot10_ComparativePerformanceDashboard
        ]

        for method in visualization_methods:
            try:
                logger.info(f"Generating {method.__name__}...")
                method()
                logger.info(f"Successfully generated {method.__name__}")
            except Exception as e:
                logger.error(f"Failed to generate {method.__name__}: {str(e)}")
                continue

        self._generateVisualizationCatalog()
        logger.info(f"Completed visualization generation. Created {self.plotCounter - 1} plots.")

    def _generateVisualizationCatalog(self):
        """
        @brief Generates a comprehensive catalog of all created visualizations
        """
        catalog_path = Path(AnalysisConfiguration.CAPTIONS_PATH) / "visualization_catalog.txt"

        catalog_content = "COMPREHENSIVE VISUALIZATION CATALOG\n"
        catalog_content += "=" * 60 + "\n\n"
        catalog_content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        catalog_content += f"Total Plots: {self.plotCounter - 1}\n"
        catalog_content += f"Total Policies: {self.df['policy_name'].nunique()}\n"
        catalog_content += f"Load Scenarios: {sorted(self.df['load_factor'].unique())}\n"
        catalog_content += f"Protagonist Policies: {', '.join(AnalysisConfiguration.PROTAGONIST_POLICIES)}\n\n"

        for plot_id, plot_info in self.captionRegistry.items():
            catalog_content += f"PLOT {plot_id:02d}: {plot_info['caption_title']}\n"
            catalog_content += f"  Filename: {plot_info['filename']}\n"
            catalog_content += f"  Analysis: {plot_info['plot_name']}\n"
            catalog_content += "-" * 50 + "\n"

        with open(catalog_path, 'w', encoding='utf-8') as f:
            f.write(catalog_content)


# =================================================================================
# ENHANCED STATISTICAL & MACHINE LEARNING ENGINE
# =================================================================================
class EnhancedStatisticalLearningEngine:
    """
    @brief Enhanced statistical analysis and machine learning for ALL data
    """

    def __init__(self, dataFrame: pd.DataFrame):
        self.df = dataFrame
        self.mlResults = {}
        self.statisticalTests = {}

    def performComprehensiveStatisticalAnalysis(self):
        """
        @brief Performs advanced statistical analysis including hypothesis testing for ALL data
        """
        logger.info("Performing comprehensive statistical analysis for all policies and scenarios")

        # 1. Descriptive statistics by policy and load
        descriptive_stats = self.df.groupby(['policy_name', 'load_factor']).agg({
            'system_EW': ['mean', 'std', 'min', 'max', 'skew', pd.Series.kurt],  # Use function object
            'system_EN': ['mean', 'std', 'min', 'max'],
            'total_occupancy': ['mean', 'max'],
            'throughput_efficiency': ['mean']
        })

        # 2. ANOVA test for policy performance differences
        from scipy.stats import f_oneway
        policies = self.df['policy_name'].unique()
        anova_groups = [self.df[self.df['policy_name'] == policy]['system_EW'] for policy in policies]
        anova_result = f_oneway(*anova_groups)

        self.statisticalTests['anova_policy_performance'] = {
            'f_statistic': anova_result.statistic,
            'p_value': anova_result.pvalue,
            'significance': anova_result.pvalue < 0.05
        }

        # 3. Special analysis for protagonist policies
        protagonist_stats = self.df[self.df['policy_name'].isin(AnalysisConfiguration.PROTAGONIST_POLICIES)]
        protagonist_summary = protagonist_stats.groupby('policy_name').agg({
            'system_EW': ['mean', 'std'],
            'system_EN': ['mean', 'std'],
            'little_error': lambda x: np.abs(x).mean()
        }).round(4)

        # Save comprehensive statistical report
        report_path = Path(AnalysisConfiguration.SUMMARIES_PATH) / "comprehensive_statistical_analysis.txt"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("COMPREHENSIVE STATISTICAL ANALYSIS REPORT\n")
            f.write("=" * 60 + "\n\n")

            f.write("DATASET OVERVIEW:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total samples: {len(self.df):,}\n")
            f.write(f"Policies analyzed: {len(policies)}\n")
            f.write(f"Load scenarios: {sorted(self.df['load_factor'].unique())}\n")
            f.write(f"Protagonist policies: {', '.join(AnalysisConfiguration.PROTAGONIST_POLICIES)}\n\n")

            f.write("STATISTICAL TESTS:\n")
            f.write("-" * 30 + "\n")
            f.write("ANOVA - Policy Performance Differences:\n")
            f.write(f"  F-statistic: {anova_result.statistic:.4f}\n")
            f.write(f"  P-value: {anova_result.pvalue:.6f}\n")
            f.write(f"  Significant Difference: {anova_result.pvalue < 0.05}\n\n")

            f.write("PROTAGONIST POLICIES SUMMARY:\n")
            f.write("-" * 30 + "\n")
            f.write(protagonist_summary.to_string())
            f.write("\n\n")

            f.write("COMPLETE DESCRIPTIVE STATISTICS:\n")
            f.write("-" * 30 + "\n")
            f.write(descriptive_stats.to_string())

        logger.info("Comprehensive statistical analysis completed")
        return descriptive_stats

    def performAdvancedDimensionalityReduction(self):
        """
        @brief Performs PCA and clustering analysis for ALL data
        """
        logger.info("Performing advanced dimensionality reduction for all data")

        # Prepare features
        feature_columns = [
            'system_EW', 'system_EN', 'little_error', 'queue_imbalance',
            'throughput_efficiency', 'total_occupancy', 'arrival_rate_est'
        ]
        feature_columns = [col for col in feature_columns if col in self.df.columns]

        # Sample data for performance
        sample_df = self.df.sample(n=min(10000, len(self.df)), random_state=42)
        X = sample_df[feature_columns]
        y = sample_df['policy_name']

        # Handle missing values
        X = X.fillna(X.mean())

        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # PCA
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)

        # Create visualization
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        # Color scheme for visualization engine
        viz = EnhancedScientificVisualizationEngine(self.df)

        # PCA colored by policy
        for policy in sorted(y.unique()):
            mask = y == policy
            color = viz.protagonist_colors.get(policy, 'gray')
            alpha = 0.8 if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 0.4
            size = 50 if policy in AnalysisConfiguration.PROTAGONIST_POLICIES else 20

            axes[0].scatter(X_pca[mask, 0], X_pca[mask, 1],
                            label=policy, alpha=alpha, s=size, color=color)

        axes[0].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%})')
        axes[0].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%})')
        axes[0].set_title('PCA: Policy Behavioral Space\n(All Data)', fontweight='bold')
        axes[0].legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        axes[0].grid(True, alpha=0.3)

        # PCA colored by load
        load_factors = sample_df['load_factor']
        scatter = axes[1].scatter(X_pca[:, 0], X_pca[:, 1], c=load_factors,
                                  cmap='viridis', alpha=0.6, s=30)
        axes[1].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%})')
        axes[1].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%})')
        axes[1].set_title('PCA: Load Factor Distribution\n(All Data)', fontweight='bold')
        axes[1].grid(True, alpha=0.3)
        plt.colorbar(scatter, ax=axes[1], label='Load Factor')

        plt.tight_layout()

        caption = """
HYPOTHESIS: The complete dataset containing all policies and load scenarios occupies
             a structured low-dimensional manifold, with clear separation between
             policies and systematic variation with load conditions.

EXPECTED INSIGHTS:
  - Policies form distinct clusters in the behavioral space
  - Load factor systematically influences system state
  - Protagonist policies may occupy characteristic regions
  - Dimensionality reduction reveals fundamental system structure

METHODOLOGY: Principal Component Analysis applied to the complete dataset containing
              all 11 policies across 4 load scenarios, visualizing both policy-based
              and load-based patterns in the reduced dimensional space.

IMPACT: Provides fundamental understanding of the complete policy design space
         and supports development of reduced-order models for system optimization.
"""
        viz.savePlotWithScientificCaption(fig, "advanced_dimensionality_reduction",
                                          "Comprehensive Dimensionality Reduction", caption)

        # Store results
        self.mlResults['dimensionality_reduction'] = {
            'pca': pca,
            'explained_variance': pca.explained_variance_ratio_
        }

        return self.mlResults['dimensionality_reduction']

    def trainEnhancedRegressionModels(self):
        """
        @brief Trains regression models to predict system performance
        """
        logger.info("Training enhanced regression models with all data")

        # Feature selection
        feature_columns = [
            'total_occupancy', 'arrival_rate_est', 'q0_len', 'q1_len', 'q2_len',
            'system_EN', 'system_lambda', 'queue_imbalance'
        ]
        feature_columns = [col for col in feature_columns if col in self.df.columns]

        target_column = 'system_EW'

        X = self.df[feature_columns]
        y = self.df[target_column]

        # Handle missing values
        X = X.fillna(X.mean())

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=AnalysisConfiguration.TEST_SIZE_RATIO,
            random_state=AnalysisConfiguration.RANDOM_STATE
        )

        # Train multiple models
        models = {
            'Linear Regression': LinearRegression(),
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        }

        results = {}

        for name, model in models.items():
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

            results[name] = {
                'mse': mse,
                'r2': r2,
                'model': model
            }

        # Create results visualization
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # Model comparison
        model_names = list(results.keys())
        r2_scores = [results[name]['r2'] for name in model_names]

        bars = axes[0].bar(model_names, r2_scores, alpha=0.7, color=['lightblue', 'lightgreen'])
        axes[0].set_ylabel('R² Score')
        axes[0].set_title('Regression Model Performance\n(System EW Prediction)', fontweight='bold')
        axes[0].grid(True, alpha=0.3, axis='y')

        for bar, score in zip(bars, r2_scores):
            axes[0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                         f'{score:.3f}', ha='center', va='bottom')

        # Feature importance from best model
        best_model_name = max(results, key=lambda x: results[x]['r2'])
        best_model = results[best_model_name]['model']

        if hasattr(best_model, 'feature_importances_'):
            feature_imp = pd.DataFrame({
                'feature': feature_columns,
                'importance': best_model.feature_importances_
            }).sort_values('importance', ascending=False)

            axes[1].barh(feature_imp['feature'], feature_imp['importance'], alpha=0.7, color='lightcoral')
            axes[1].set_xlabel('Feature Importance')
            axes[1].set_title(f'Feature Importance: {best_model_name}', fontweight='bold')
            axes[1].grid(True, alpha=0.3, axis='x')

        plt.tight_layout()

        # Save via visualization engine
        viz = EnhancedScientificVisualizationEngine(self.df)
        caption = f"""
HYPOTHESIS: System expected wait time can be accurately predicted from current
             system state metrics using machine learning regression, with the
             complete dataset providing robust training for predictive models.

EXPECTED INSIGHTS:
  - Ensemble methods achieve high prediction accuracy
  - Feature importance reveals key drivers of system performance
  - Comprehensive dataset enables robust model training
  - Predictive models can support real-time system optimization

METHODOLOGY: Comparative evaluation of regression algorithms using the complete
              dataset with rigorous train-test splitting and comprehensive performance
              metrics. Best model: {best_model_name} with R² = {results[best_model_name]['r2']:.3f}

IMPACT: Enables development of predictive models for system performance optimization
         and proactive management based on current system state.
"""
        viz.savePlotWithScientificCaption(fig, "enhanced_regression_analysis",
                                          "System Performance Prediction Modeling", caption)

        # Save results
        self.mlResults['regression'] = {
            'results': results,
            'best_model': best_model_name,
            'best_r2': results[best_model_name]['r2']
        }

        self._saveEnhancedMLResults()

        return self.mlResults['regression']

    def _saveEnhancedMLResults(self):
        """
        @brief Saves comprehensive machine learning results to file
        """
        ml_report_path = Path(AnalysisConfiguration.ML_RESULTS_PATH) / "enhanced_ml_analysis_report.txt"

        with open(ml_report_path, 'w', encoding='utf-8') as f:
            f.write("ENHANCED MACHINE LEARNING ANALYSIS REPORT\n")
            f.write("=" * 60 + "\n\n")

            f.write("DATASET CHARACTERISTICS:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total samples: {len(self.df):,}\n")
            f.write(f"Policies: {self.df['policy_name'].nunique()}\n")
            f.write(f"Load scenarios: {self.df['load_factor'].nunique()}\n")
            f.write(f"Protagonist policies: {', '.join(AnalysisConfiguration.PROTAGONIST_POLICIES)}\n\n")

            if 'regression' in self.mlResults:
                f.write("REGRESSION ANALYSIS RESULTS:\n")
                f.write("-" * 30 + "\n")
                reg_results = self.mlResults['regression']['results']
                for model_name, result in reg_results.items():
                    f.write(f"{model_name}:\n")
                    f.write(f"  R² Score: {result['r2']:.4f}\n")
                    f.write(f"  MSE: {result['mse']:.4f}\n")
                f.write(f"\nBest Model: {self.mlResults['regression']['best_model']}\n")
                f.write(f"Best R²: {self.mlResults['regression']['best_r2']:.4f}\n\n")

            if 'dimensionality_reduction' in self.mlResults:
                f.write("DIMENSIONALITY REDUCTION RESULTS:\n")
                f.write("-" * 30 + "\n")
                dr_results = self.mlResults['dimensionality_reduction']
                f.write(
                    f"PCA Explained Variance: {dr_results['explained_variance'][0]:.3f} (PC1) + {dr_results['explained_variance'][1]:.3f} (PC2)\n")
                f.write(f"Total Variance Explained: {dr_results['explained_variance'][:2].sum():.3f}\n")

        logger.info("Enhanced machine learning results saved")


# =================================================================================
# COMPREHENSIVE PIPELINE ORCHESTRATOR - ENHANCED
# =================================================================================
class EnhancedMM1Pipeline:
    """
    @brief Main orchestrator for the complete enhanced analysis pipeline
    """

    def __init__(self):
        self.dataEngine = EnhancedDataIngestionEngine()
        self.visualizationEngine = None
        self.mlEngine = None
        self.analysisSummary = {}

    def executeCompleteAnalysis(self):
        """
        @brief Executes the complete enhanced analysis pipeline
        """
        logger.info("Starting Enhanced MM1 Analysis Pipeline")
        start_time = datetime.now()

        try:
            # Phase 1: Setup and Configuration
            AnalysisConfiguration.setupDirectories()
            logger.info("Phase 1: Environment setup completed")

            # Phase 2: Data Ingestion and Processing - ALL 44 FILES
            logger.info("Phase 2: Loading and processing ALL 44 data files...")
            raw_data = self.dataEngine.loadAndValidateAllData()
            cleaned_data = self.dataEngine.performEnhancedDataCleaning()
            logger.info("Phase 2: Data ingestion and processing completed")

            # Phase 3: Statistical Analysis
            logger.info("Phase 3: Performing comprehensive statistical analysis...")
            self.mlEngine = EnhancedStatisticalLearningEngine(cleaned_data)
            statistical_results = self.mlEngine.performComprehensiveStatisticalAnalysis()
            logger.info("Phase 3: Statistical analysis completed")

            # Phase 4: Comprehensive Visualization - ALL POLICIES, ALL SCENARIOS
            logger.info("Phase 4: Generating comprehensive visualizations...")
            self.visualizationEngine = EnhancedScientificVisualizationEngine(cleaned_data)
            self.visualizationEngine.generateAllVisualizations()
            logger.info("Phase 4: Comprehensive visualization completed")

            # Phase 5: Advanced Machine Learning
            logger.info("Phase 5: Performing advanced machine learning analysis...")
            dimensionality_results = self.mlEngine.performAdvancedDimensionalityReduction()
            regression_results = self.mlEngine.trainEnhancedRegressionModels()
            logger.info("Phase 5: Machine learning analysis completed")

            # Phase 6: Final Reporting and Summary
            logger.info("Phase 6: Generating final reports and summaries...")
            self._generateEnhancedComprehensiveSummary()
            logger.info("Phase 6: Final reporting completed")

            # Calculate execution time
            execution_time = datetime.now() - start_time
            self.analysisSummary['execution_time'] = execution_time
            self.analysisSummary['completion_status'] = 'SUCCESS'

            logger.info(f"Enhanced analysis pipeline completed successfully in {execution_time}")

        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            self.analysisSummary['completion_status'] = 'FAILED'
            self.analysisSummary['error'] = str(e)
            raise

    def _generateEnhancedComprehensiveSummary(self):
        """
        @brief Generates comprehensive summary reports for all analysis phases
        """
        logger.info("Generating enhanced comprehensive analysis summary")

        # Executive Summary
        executive_summary_path = Path(AnalysisConfiguration.SUMMARIES_PATH) / "enhanced_executive_summary.txt"

        with open(executive_summary_path, 'w', encoding='utf-8') as f:
            f.write("ENHANCED COMPREHENSIVE QUEUEING SYSTEM ANALYSIS - EXECUTIVE SUMMARY\n")
            f.write("=" * 80 + "\n\n")

            f.write("ANALYSIS OVERVIEW:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Data Files Processed: {len(self.dataEngine.fileMetadata)}/44\n")
            f.write(f"Total Data Points: {len(self.dataEngine.globalDataFrame):,}\n")
            f.write(f"Policies Analyzed: {self.dataEngine.globalDataFrame['policy_name'].nunique()}\n")
            f.write(f"Load Scenarios: {sorted(self.dataEngine.globalDataFrame['load_factor'].unique())}\n")
            f.write(f"Protagonist Policies: {', '.join(AnalysisConfiguration.PROTAGONIST_POLICIES)}\n\n")

            f.write("KEY FINDINGS:\n")
            f.write("-" * 30 + "\n")

            # Performance insights
            avg_performance = self.dataEngine.globalDataFrame.groupby('policy_name')['system_EW'].mean()
            best_policy = avg_performance.idxmin()
            best_performance = avg_performance.min()

            f.write(f"• Best Overall Performance: {best_policy} (EW: {best_performance:.2f})\n")

            # Protagonist policy analysis
            protagonist_data = self.dataEngine.globalDataFrame[
                self.dataEngine.globalDataFrame['policy_name'].isin(AnalysisConfiguration.PROTAGONIST_POLICIES)
            ]

            f.write("• Protagonist Policy Rankings:\n")
            for policy in AnalysisConfiguration.PROTAGONIST_POLICIES:
                if policy in avg_performance.index:
                    policy_rank = (avg_performance.index == policy).argmax() + 1
                    policy_perf = avg_performance[policy]
                    f.write(f"  - {policy}: Rank {policy_rank}, EW: {policy_perf:.2f}\n")

            if hasattr(self.mlEngine, 'mlResults') and 'regression' in self.mlEngine.mlResults:
                best_r2 = self.mlEngine.mlResults['regression']['best_r2']
                f.write(f"• System EW Predictability: R² = {best_r2:.3f}\n")

            f.write(f"• Data Quality: {self.dataEngine.cleaningReport['cleaning_percentage']:.2f}% data retained\n\n")

            f.write("RECOMMENDATIONS:\n")
            f.write("-" * 30 + "\n")
            f.write("1. Review protagonist policy performance for specific use cases\n")
            f.write("2. Consider load sensitivity when selecting policies\n")
            f.write("3. Use comprehensive visualizations for policy comparison\n")
            f.write("4. Leverage statistical insights for capacity planning\n")
            f.write("5. Consider tradeoffs between performance, stability, and fairness\n\n")

            f.write("GENERATED ARTIFACTS:\n")
            f.write("-" * 30 + "\n")
            f.write(f"• Visualizations: {self.visualizationEngine.plotCounter - 1} high-resolution plots\n")
            f.write("• Statistical Reports: Comprehensive analysis and tests\n")
            f.write("• ML Results: Regression performance and feature importance\n")
            f.write("• Scientific Captions: Detailed analysis justifications\n")
            f.write("• Executive Summary: High-level findings and recommendations\n")

        logger.info("Enhanced comprehensive summary generation completed")


# =================================================================================
# MAIN EXECUTION
# =================================================================================
def main():
    """
    @brief Main execution function for the enhanced analysis pipeline
    """
    try:
        pipeline = EnhancedMM1Pipeline()
        pipeline.executeCompleteAnalysis()
        logger.info("Enhanced MM1 Analysis Pipeline completed successfully!")
        logger.info(
            f"Processed {pipeline.dataEngine.globalDataFrame['policy_name'].nunique()} policies across {pipeline.dataEngine.globalDataFrame['load_factor'].nunique()} load scenarios")
        logger.info(f"Generated {pipeline.visualizationEngine.plotCounter - 1} comprehensive visualizations")

    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
