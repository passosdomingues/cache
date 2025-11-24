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
import warnings

# Machine Learning Imports
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
import scipy.stats as stats
import statsmodels.api as sm

warnings.filterwarnings('ignore')


# =================================================================================
# CONFIGURATION & CONSTANTS - Enhanced Configuration
# =================================================================================
class AnalysisConfig:
    """
    @brief Central configuration for the comprehensive MM1 Analysis Pipeline
    """
    # Path configurations
    rawDataPath: str = "../results/raw"
    outputPath: str = "../analysis"
    plotsPath: str = "../analysis/plots"
    summariesPath: str = "../analysis/summaries"
    captionsPath: str = "../analysis/captions"
    mlResultsPath: str = "../analysis/ml_results"

    # Graphics settings
    dpi: int = 300
    figSizeLarge: Tuple[int, int] = (16, 10)
    figSizeMedium: Tuple[int, int] = (12, 8)
    figSizeSmall: Tuple[int, int] = (10, 6)

    # Analysis parameters
    totalSamples: int = 8640
    randomState: int = 42
    testSizeRatio: float = 0.2
    crossValidationFolds: int = 5

    # Plot sampling for performance
    scatterSampleSize: int = 10000
    timeSeriesSampleStep: int = 10

    # Special focus policies
    protagonistPolicies: List[str] = ["MAX_AVG_WAIT", "ROUND_ROBIN", "SALLES_UTILITY"]

    # All load scenarios
    loadScenarios: List[float] = [0.800, 0.900, 0.950, 0.999]

    @classmethod
    def getProtagonistPolicies(cls):
        """
        @brief Get the list of protagonist policies
        @return List of protagonist policy names
        """
        return cls.protagonistPolicies

    @classmethod
    def getLoadScenarios(cls):
        """
        @brief Get the list of load scenarios
        @return List of load scenario values
        """
        return cls.loadScenarios

    @classmethod
    def setupDirectories(cls):
        """
        @brief Creates all necessary output directories with validation
        """
        directories = [
            cls.outputPath, cls.plotsPath, cls.summariesPath,
            cls.captionsPath, cls.mlResultsPath
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
    @return Configured logger instance
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
        """
        @brief Initialize the data ingestion engine
        """
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
        cleanName = filename.replace('.csv', '')

        seedMatch = re.search(r'_seed(\d+)', cleanName)
        seed = int(seedMatch.group(1)) if seedMatch else 42

        rhoMatch = re.search(r'rho(0\.\d+)', cleanName)
        if not rhoMatch:
            raise ValueError(f"Could not extract rho from filename: {filename}")
        rho = float(rhoMatch.group(1))

        policyMatch = re.match(r'(.*)_rho', cleanName)
        if not policyMatch:
            raise ValueError(f"Could not extract policy from filename: {filename}")
        policy = policyMatch.group(1)

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
        requiredColumns = [
            'time', 'sample_idx', 'total_occupancy', 'arrival_rate_est',
            'q0_len', 'q1_len', 'q2_len', 'server_busy', 'system_EN',
            'system_EW', 'little_error'
        ]

        missingColumns = [col for col in requiredColumns if col not in dataframe.columns]
        if missingColumns:
            logger.error(f"Missing required columns in {filename}: {missingColumns}")
            return False

        if len(dataframe) != AnalysisConfig.totalSamples:
            logger.warning(
                f"Sample count mismatch in {filename}: {len(dataframe)} vs {AnalysisConfig.totalSamples}")

        return True

    def loadAndValidateAllData(self) -> pd.DataFrame:
        """
        @brief Loads ALL 44 CSV files with comprehensive validation
        @return Combined and validated DataFrame
        """
        dataPath = Path(AnalysisConfig.rawDataPath)
        if not dataPath.exists():
            raise FileNotFoundError(f"Raw data path does not exist: {AnalysisConfig.rawDataPath}")

        csvFiles = list(dataPath.glob("*.csv"))
        logger.info(f"Found {len(csvFiles)} CSV files for analysis")

        if len(csvFiles) != 44:
            logger.warning(f"Expected 44 files, found {len(csvFiles)}. Continuing with available files.")

        dataFrames = []
        validationResults = {}
        loadedCount = 0

        for filePath in csvFiles:
            filename = filePath.name
            logger.info(f"Processing file: {filename}")

            try:
                df = pd.read_csv(filePath)
                metadata = self.parseFilenameWithEnhancedRegex(filename)
                isValid = self.validateDataStructure(df, filename)

                validationResults[filename] = {
                    'valid': isValid,
                    'row_count': len(df),
                    'metadata': metadata
                }

                if not isValid:
                    logger.error(f"Validation failed for {filename}, skipping")
                    continue

                df['policy_name'] = metadata['policy']
                df['load_factor'] = metadata['rho']
                df['seed_value'] = metadata['seed']
                df['scenario_id'] = f"{metadata['policy']}_rho{metadata['rho']}"

                self.loadedPolicies.add(metadata['policy'])
                self.loadedScenarios.add(metadata['rho'])
                self.fileMetadata[filename] = metadata
                dataFrames.append(df)
                loadedCount += 1

                logger.info(f"Successfully loaded {filename} with {len(df)} rows")

            except Exception as e:
                logger.error(f"Failed to process {filename}: {str(e)}")
                validationResults[filename] = {'valid': False, 'error': str(e)}
                continue

        if not dataFrames:
            raise ValueError("No valid data files could be loaded")

        self.globalDataFrame = pd.concat(dataFrames, ignore_index=True)
        logger.info(f"Combined dataset created with {len(self.globalDataFrame)} total rows from {loadedCount} files")
        logger.info(f"Loaded policies: {sorted(self.loadedPolicies)}")
        logger.info(f"Loaded scenarios: {sorted(self.loadedScenarios)}")

        self._generateValidationReport(validationResults)
        return self.globalDataFrame

    def performEnhancedDataCleaning(self) -> pd.DataFrame:
        """
        @brief Performs comprehensive data cleaning and feature engineering for ALL data
        @return Cleaned and enhanced DataFrame
        """
        initialRowCount = len(self.globalDataFrame)
        logger.info("Starting enhanced data cleaning for all scenarios")

        self.globalDataFrame = self.globalDataFrame.drop_duplicates()

        numericColumns = self.globalDataFrame.select_dtypes(include=[np.number]).columns
        for col in numericColumns:
            if self.globalDataFrame[col].isnull().sum() > 0:
                self.globalDataFrame[col] = self.globalDataFrame[col].fillna(method='ffill')
                self.globalDataFrame[col] = self.globalDataFrame[col].fillna(self.globalDataFrame[col].median())

        logger.info("Performing advanced feature engineering for all policies and scenarios")

        # Create system_lambda if it doesn't exist
        if 'system_lambda' not in self.globalDataFrame.columns:
            self.globalDataFrame['system_lambda'] = self.globalDataFrame['arrival_rate_est']

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

        self.globalDataFrame['throughput_efficiency'] = (
                self.globalDataFrame['system_lambda'] /
                (self.globalDataFrame['arrival_rate_est'] + 1e-6)
        )

        self.globalDataFrame['load_category'] = pd.cut(
            self.globalDataFrame['load_factor'],
            bins=[0.7, 0.85, 0.95, 1.0],
            labels=['Low (0.8)', 'Medium (0.9)', 'High (0.95-0.999)']
        )

        protagonistPolicies = AnalysisConfig.getProtagonistPolicies()
        self.globalDataFrame['policy_type'] = self.globalDataFrame['policy_name'].apply(
            lambda x: 'PROTAGONIST' if x in protagonistPolicies else 'SUPPORTING'
        )

        finalRowCount = len(self.globalDataFrame)
        self.cleaningReport = {
            'initial_rows': initialRowCount,
            'final_rows': finalRowCount,
            'rows_removed': initialRowCount - finalRowCount,
            'cleaning_percentage': ((initialRowCount - finalRowCount) / initialRowCount * 100),
            'total_policies': len(self.loadedPolicies),
            'total_scenarios': len(self.loadedScenarios)
        }

        logger.info(f"Enhanced data cleaning completed: {self.cleaningReport}")
        return self.globalDataFrame

    def _generateValidationReport(self, validationResults: Dict):
        """
        @brief Generates comprehensive validation report
        @param validationResults: Dictionary with validation results
        """
        validFiles = [f for f, result in validationResults.items() if result.get('valid', False)]
        invalidFiles = [f for f, result in validationResults.items() if not result.get('valid', False)]

        report = {
            'total_files_processed': len(validationResults),
            'valid_files': len(validFiles),
            'invalid_files': len(invalidFiles),
            'validation_rate': len(validFiles) / len(validationResults) * 100,
            'invalid_files_details': invalidFiles
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
        """
        @brief Initialize the visualization engine
        @param dataFrame: The complete dataset for visualization
        """
        self.df = dataFrame
        self.plotCounter = 1
        self.captionRegistry = {}

        plt.style.use('seaborn-v0_8-whitegrid')
        sns.set_palette("husl")
        plt.rcParams['figure.dpi'] = AnalysisConfig.dpi
        plt.rcParams['savefig.dpi'] = AnalysisConfig.dpi
        plt.rcParams['figure.figsize'] = AnalysisConfig.figSizeMedium

        self.protagonistColors = {
            'MAX_AVG_WAIT': '#FF6B6B',
            'ROUND_ROBIN': '#4ECDC4',
            'SALLES_UTILITY': '#45B7D1'
        }

        self.loadColors = {
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
        plotFilename = f"plot_{self.plotCounter:02d}_{plotName}.png"
        plotPath = Path(AnalysisConfig.plotsPath) / plotFilename
        figure.savefig(plotPath, dpi=AnalysisConfig.dpi, bbox_inches='tight',
                       facecolor='white', edgecolor='none')
        plt.close(figure)

        captionFilename = f"plot_{self.plotCounter:02d}_{plotName}_caption.txt"
        captionPath = Path(AnalysisConfig.captionsPath) / captionFilename

        protagonistPolicies = AnalysisConfig.getProtagonistPolicies()

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

SPECIAL FOCUS: Policies {', '.join(protagonistPolicies)} are highlighted for comparative analysis.
"""

        with open(captionPath, 'w', encoding='utf-8') as f:
            f.write(captionContent)

        self.captionRegistry[self.plotCounter] = {
            'plot_name': plotName,
            'caption_title': captionTitle,
            'filename': plotFilename
        }

        logger.info(f"Generated plot {self.plotCounter:02d}: {plotName}")
        self.plotCounter += 1

    def plot01TemporalEvolutionAllScenarios(self):
        """
        @brief Plot 1: Temporal evolution across ALL 4 load scenarios with protagonist highlight
        """
        logger.info("Creating temporal evolution analysis for all 4 load scenarios")

        fig, axes = plt.subplots(4, 3, figsize=(24, 16))

        loadScenarios = AnalysisConfig.getLoadScenarios()
        protagonistPolicies = AnalysisConfig.getProtagonistPolicies()

        for loadIdx, loadFactor in enumerate(loadScenarios):
            scenarioData = self.df[self.df['load_factor'] == loadFactor]
            sampledData = scenarioData.iloc[::AnalysisConfig.timeSeriesSampleStep]
            policiesPresent = sampledData['policy_name'].unique()

            for policy in policiesPresent:
                policyData = sampledData[sampledData['policy_name'] == policy]
                if not policyData.empty:
                    color = self.protagonistColors.get(policy, 'gray')
                    linewidth = 2.0 if policy in protagonistPolicies else 1.0
                    alpha = 0.9 if policy in protagonistPolicies else 0.5
                    linestyle = '-' if policy in protagonistPolicies else '--'

                    axes[loadIdx, 0].plot(policyData['time'], policyData['system_EN'],
                                          label=policy, linewidth=linewidth, alpha=alpha,
                                          linestyle=linestyle, color=color)

            axes[loadIdx, 0].set_title(f'System EN Evolution @ ρ={loadFactor}', fontsize=12, fontweight='bold')
            axes[loadIdx, 0].set_ylabel('Expected Number')
            axes[loadIdx, 0].grid(True, alpha=0.3)
            if loadIdx == 0:
                axes[loadIdx, 0].legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)

            for policy in policiesPresent:
                policyData = sampledData[sampledData['policy_name'] == policy]
                if not policyData.empty:
                    color = self.protagonistColors.get(policy, 'gray')
                    linewidth = 2.0 if policy in protagonistPolicies else 1.0
                    alpha = 0.9 if policy in protagonistPolicies else 0.5
                    linestyle = '-' if policy in protagonistPolicies else '--'

                    axes[loadIdx, 1].plot(policyData['time'], policyData['system_EW'],
                                          label=policy, linewidth=linewidth, alpha=alpha,
                                          linestyle=linestyle, color=color)

            axes[loadIdx, 1].set_title(f'System EW Evolution @ ρ={loadFactor}', fontsize=12, fontweight='bold')
            axes[loadIdx, 1].set_ylabel('Expected Wait')
            axes[loadIdx, 1].grid(True, alpha=0.3)

            for policy in policiesPresent:
                policyData = sampledData[sampledData['policy_name'] == policy]
                if not policyData.empty:
                    color = self.protagonistColors.get(policy, 'gray')
                    linewidth = 2.0 if policy in protagonistPolicies else 1.0
                    alpha = 0.9 if policy in protagonistPolicies else 0.5
                    linestyle = '-' if policy in protagonistPolicies else '--'

                    axes[loadIdx, 2].plot(policyData['time'], policyData['little_error'].abs(),
                                          label=policy, linewidth=linewidth, alpha=alpha,
                                          linestyle=linestyle, color=color)

            axes[loadIdx, 2].set_title(f'Little\'s Error Evolution @ ρ={loadFactor}', fontsize=12, fontweight='bold')
            axes[loadIdx, 2].set_ylabel('|Little Error|')
            axes[loadIdx, 2].set_xlabel('Time (s)')
            axes[loadIdx, 2].grid(True, alpha=0.3)
            axes[loadIdx, 2].set_yscale('log')

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

    def plot02QueueDistributionViolinAllLoads(self):
        """
        @brief Plot 02: Violin plots of queue length distributions across all loads and policies
        """
        logger.info("Creating violin plots: queue distribution across all loads")

        loadScenarios = AnalysisConfig.getLoadScenarios()
        fig, axes = plt.subplots(len(loadScenarios), 1, figsize=(14, 4 * len(loadScenarios)))
        if len(loadScenarios) == 1:
            axes = [axes]

        for i, load in enumerate(loadScenarios):
            ax = axes[i]
            data = self.df[self.df['load_factor'] == load]
            if data.empty:
                ax.text(0.5, 0.5, f'No data for ρ={load}', ha='center', va='center')
                continue

            queues = ['q0_len', 'q1_len', 'q2_len']
            longDf = pd.melt(data, id_vars=['policy_name'], value_vars=queues,
                             var_name='queue', value_name='length')
            longDf = longDf.sample(n=min(len(longDf), 20000), random_state=42)

            sns.violinplot(x='queue', y='length', hue='policy_name', data=longDf,
                           split=False, inner='quartile', ax=ax, palette=self.protagonistColors,
                           linewidth=0.8)
            ax.set_title(f'Queue Length Distribution @ ρ={load}', fontweight='bold')
            ax.set_ylabel('Queue length')
            ax.grid(True, alpha=0.25)
            if i == 0:
                ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=7)
            else:
                ax.get_legend().remove()

        plt.tight_layout()

        caption = """
HYPOTHESIS: Queue length distributions vary by policy and load; protagonist policies present
             distinctive distribution shapes under stress.

EXPECTED INSIGHTS:
  - Distribution width increases with load
  - Some policies concentrate mass at low-length (stable) whereas others spread to heavy tails
  - Protagonist policies may show tighter distributions under moderate loads

METHODOLOGY: Create violin plots of q0_len, q1_len, q2_len for each load scenario. Policies are shown as hue to compare distributional shapes.

IMPACT: Visual identification of fairness, stability and heavy-tail risk across policies and loads.
"""
        self.savePlotWithScientificCaption(fig, "queue_distribution_violin_all_loads",
                                           "Queue Distribution Violin Plots Across Loads", caption)

    def plot03ProtagonistPolicyDeepDive(self):
        """
        @brief Plot 3: Deep dive analysis focusing on the 3 protagonist policies
        """
        logger.info("Creating protagonist policy deep dive analysis")

        protagonistPolicies = AnalysisConfig.getProtagonistPolicies()
        protagonistData = self.df[self.df['policy_name'].isin(protagonistPolicies)]

        fig, axes = plt.subplots(3, 4, figsize=(20, 15))

        metrics = ['system_EW', 'system_EN', 'little_error', 'queue_imbalance']
        metricNames = ['System Expected Wait', 'System Expected Number',
                       'Little\'s Law Error', 'Queue Imbalance']

        for policyIdx, policy in enumerate(protagonistPolicies):
            policyData = protagonistData[protagonistData['policy_name'] == policy]

            for metricIdx, (metric, metricName) in enumerate(zip(metrics, metricNames)):
                boxplotData = []
                loadLabels = []

                loadScenarios = AnalysisConfig.getLoadScenarios()
                for load in loadScenarios:
                    loadMetricData = policyData[policyData['load_factor'] == load][metric]
                    if len(loadMetricData) > 0:
                        boxplotData.append(loadMetricData)
                        loadLabels.append(f'ρ={load}')

                if boxplotData:
                    box = axes[policyIdx, metricIdx].boxplot(boxplotData, labels=loadLabels,
                                                             patch_artist=True)

                    for patch, loadVal in zip(box['boxes'], loadScenarios):
                        patch.set_facecolor(self.loadColors[loadVal])
                        patch.set_alpha(0.7)

                    axes[policyIdx, metricIdx].set_title(f'{policy}\n{metricName}', fontweight='bold')
                    axes[policyIdx, metricIdx].set_ylabel(metricName)
                    axes[policyIdx, metricIdx].grid(True, alpha=0.3, axis='y')

                    if metric == 'little_error':
                        axes[policyIdx, metricIdx].set_yscale('log')

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

    def plot04LoadScenarioComparativeAnalysis(self):
        """
        @brief Plot 04: Comparative metrics across load scenarios (bar + errorbars)
        """
        logger.info("Creating load scenario comparative analysis (bar + errorbars)")

        loadScenarios = AnalysisConfig.getLoadScenarios()
        protagonistPolicies = AnalysisConfig.getProtagonistPolicies()

        metrics = ['system_EW', 'system_EN', 'throughput_efficiency']
        metricNames = ['Expected Wait (EW)', 'Expected Number (EN)', 'Throughput Efficiency']

        agg = self.df.groupby(['policy_name', 'load_factor']).agg({
            'system_EW': ['mean', 'std'],
            'system_EN': ['mean', 'std'],
            'throughput_efficiency': ['mean', 'std']
        })
        agg.columns = ['_'.join(col).strip() for col in agg.columns.values]
        agg = agg.reset_index()

        fig, axes = plt.subplots(1, len(metrics), figsize=(18, 6))

        for idx, metric in enumerate(metrics):
            ax = axes[idx]
            pivotMean = agg.pivot(index='policy_name', columns='load_factor', values=f'{metric}_mean').fillna(0)
            pivotStd = agg.pivot(index='policy_name', columns='load_factor', values=f'{metric}_std').fillna(0)

            x = np.arange(len(pivotMean.index))
            width = 0.18
            offsets = np.linspace(-width * (len(loadScenarios) - 1) / 2, width * (len(loadScenarios) - 1) / 2,
                                  len(loadScenarios))

            for j, load in enumerate(loadScenarios):
                vals = pivotMean[load] if load in pivotMean.columns else np.zeros(len(pivotMean))
                errs = pivotStd[load] if load in pivotStd.columns else np.zeros(len(pivotMean))
                ax.bar(x + offsets[j], vals, width=width, label=f'ρ={load}', alpha=0.9)
                ax.errorbar(x + offsets[j], vals, yerr=errs, fmt='none', ecolor='black', alpha=0.6, capsize=3)

            ax.set_xticks(x)
            ax.set_xticklabels(pivotMean.index, rotation=90)
            ax.set_title(metricNames[idx], fontweight='bold')
            ax.grid(True, axis='y', alpha=0.25)
            if idx == len(metrics) - 1:
                ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=8)

        plt.tight_layout()

        caption = """
HYPOTHESIS: Aggregate performance metrics (EW, EN, throughput) change predictably with load;
             some policies scale better than others.

EXPECTED INSIGHTS:
  - Mean and variability indicate robustness and sensitivity to load
  - Protagonist policies expected to show favorable trade-offs

METHODOLOGY: Compute mean ± std for key metrics for each policy × load and display as grouped bar charts with error bars.

IMPACT: Enables policy selection based on aggregate metrics and variability across operational loads.
"""
        self.savePlotWithScientificCaption(fig, "load_scenario_comparative_analysis",
                                           "Load Scenario Comparative Analysis (Aggregate Metrics)", caption)

    def plot05CorrelationAnalysisMatrix(self):
        """
        @brief Plot 05: Correlation matrix for core numerical features (heatmap)
        """
        logger.info("Creating correlation analysis matrix")

        features = ['system_EW', 'system_EN', 'little_error', 'queue_imbalance',
                    'throughput_efficiency', 'total_occupancy', 'arrival_rate_est']
        features = [f for f in features if f in self.df.columns]

        sampleDf = self.df[features].sample(n=min(20000, len(self.df)), random_state=42)
        corr = sampleDf.corr()

        fig, ax = plt.subplots(1, 1, figsize=(10, 8))
        sns.heatmap(corr, annot=True, fmt='.2f', square=True, cmap='vlag', ax=ax, cbar_kws={'shrink': 0.8})
        ax.set_title('Correlation Matrix - Core Features', fontweight='bold')
        plt.tight_layout()

        caption = """
HYPOTHESIS: Core numerical features exhibit structured correlations revealing performance trade-offs.

EXPECTED INSIGHTS:
  - Strong positive correlation between EN and occupancy
  - Negative correlation between throughput efficiency and EW for good policies
  - Little's error should correlate with mismatch in arrival/service estimators

METHODOLOGY: Pearson correlation computed on sampled data for numerical features and displayed as annotated heatmap.

IMPACT: Identifies collinearities and candidate features for dimensionality reduction or modeling.
"""
        self.savePlotWithScientificCaption(fig, "correlation_analysis_matrix",
                                           "Correlation Analysis Matrix (Core Numeric Features)", caption)

    def plot06PerformanceRadarAllPolicies(self):
        """
        @brief Plot 06: Radar plots comparing normalized metrics across policies
        """
        logger.info("Creating performance radar charts for all policies")

        metrics = ['system_EW', 'system_EN', 'throughput_efficiency', 'little_error']
        metrics = [m for m in metrics if m in self.df.columns]
        policyList = sorted(self.df['policy_name'].unique())

        agg = self.df.groupby('policy_name')[metrics].mean()
        norm = (agg - agg.min()) / (agg.max() - agg.min() + 1e-9)

        numMetrics = len(metrics)
        angles = np.linspace(0, 2 * np.pi, numMetrics, endpoint=False).tolist()
        angles += angles[:1]

        fig = plt.figure(figsize=(14, max(6, len(policyList) // 3)))
        rows = max(1, int(np.ceil(len(policyList) / 4)))
        cols = min(4, len(policyList))
        for idx, policy in enumerate(policyList):
            ax = plt.subplot(rows, cols, idx + 1, polar=True)
            values = norm.loc[policy].tolist()
            values += values[:1]
            ax.plot(angles, values, linewidth=1.5, linestyle='solid',
                    color=self.protagonistColors.get(policy, 'gray'))
            ax.fill(angles, values, alpha=0.25, color=self.protagonistColors.get(policy, 'gray'))
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(metrics, fontsize=8)
            ax.set_yticks([0.25, 0.5, 0.75, 1.0])
            ax.set_title(policy, fontsize=9)
            ax.grid(True, alpha=0.3)

        plt.tight_layout()

        caption = """
HYPOTHESIS: Multi-metric radar visualization highlights trade-offs and balanced performers across policies.

EXPECTED INSIGHTS:
  - Policies with balanced shapes are more robust
  - Outliers show specialization (optimize a metric at cost of others)
  - Protagonist policies expected to show favorable balanced profiles

METHODOLOGY: Mean metric values per policy are normalized and displayed in radar plots for visual multi-criteria comparison.

IMPACT: Rapid identification of balanced vs specialized policies for decision making.
"""
        self.savePlotWithScientificCaption(fig, "performance_radar_all_policies",
                                           "Performance Radar for All Policies", caption)

    def plot07StatisticalDistributionAnalysis(self):
        """
        @brief Plot 07: Statistical distribution analysis (QQ plots + histograms) for key metrics
        """
        logger.info("Creating statistical distribution analysis")

        metrics = ['system_EW', 'system_EN', 'little_error']
        metrics = [m for m in metrics if m in self.df.columns]

        fig, axes = plt.subplots(len(metrics), 2, figsize=(14, 5 * len(metrics)))
        if len(metrics) == 1:
            axes = [axes]

        for i, metric in enumerate(metrics):
            axHist = axes[i][0]
            axQq = axes[i][1]

            data = self.df[metric].dropna()
            data = data.sample(n=min(20000, len(data)), random_state=42)

            sns.histplot(data, kde=True, stat='density', ax=axHist)
            axHist.set_title(f'Histogram & KDE: {metric}', fontweight='bold')
            axHist.grid(True, alpha=0.25)

            sm.qqplot(data, line='s', ax=axQq)
            axQq.set_title(f'QQ-Plot (Normal) - {metric}', fontweight='bold')
            axQq.grid(True, alpha=0.25)

        plt.tight_layout()

        caption = """
HYPOTHESIS: Distributional properties (skew, heavy tails) differ across metrics and reveal modeling needs.

EXPECTED INSIGHTS:
  - EW and EN may show heavy-tail behavior at high loads
  - Little's error distribution indicates systematic bias or noise

METHODOLOGY: Histogram + KDE and QQ-plot against normal distribution for each selected metric, sampled for performance.

IMPACT: Guides transformation choices (log, robust scaling) for modeling and hypothesis testing.
"""
        self.savePlotWithScientificCaption(fig, "statistical_distribution_analysis",
                                           "Statistical Distribution Analysis (Histogram & QQ)", caption)

    def plot08LittlesLawValidationComprehensive(self):
        """
        @brief Plot 08: Littles' Law validation — scatter comparing EN vs lambda * EW per scenario/policy
        """
        logger.info("Creating comprehensive Little's Law validation plots")

        loadScenarios = AnalysisConfig.getLoadScenarios()
        fig, axes = plt.subplots(len(loadScenarios), 1, figsize=(12, 4 * len(loadScenarios)))
        if len(loadScenarios) == 1:
            axes = [axes]

        for i, load in enumerate(loadScenarios):
            ax = axes[i]
            subset = self.df[self.df['load_factor'] == load]
            if subset.empty:
                ax.text(0.5, 0.5, f'No data for ρ={load}', ha='center', va='center')
                continue

            if 'system_EN' in subset.columns and 'system_EW' in subset.columns and 'system_lambda' in subset.columns:
                sel = subset.sample(n=min(5000, len(subset)), random_state=42)
                lhs = sel['system_EN']
                rhs = sel['system_lambda'] * sel['system_EW']
                sns.scatterplot(x=rhs, y=lhs, hue=sel['policy_name'], alpha=0.6, ax=ax,
                                palette=self.protagonistColors, s=20)
                lims = [min(lhs.min(), rhs.min()), max(lhs.max(), rhs.max())]
                ax.plot(lims, lims, linestyle='--', color='black', linewidth=1)
                ax.set_xlim(lims)
                ax.set_ylim(lims)
                ax.set_title(f"Little's Law: EN vs λ·EW @ ρ={load}", fontweight='bold')
                ax.set_xlabel('λ · EW')
                ax.set_ylabel('EN')
                if i == 0:
                    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=7)
                else:
                    ax.get_legend().remove()
            else:
                ax.text(0.5, 0.5, 'Missing required columns: system_lambda / system_EW / system_EN',
                        ha='center', va='center')

        plt.tight_layout()

        caption = """
HYPOTHESIS: Little's Law (EN ≈ λ·EW) holds within sampling variability; deviations highlight estimator bias or dynamics.

EXPECTED INSIGHTS:
  - Degree of scatter quantifies Little's Law violations per policy and load
  - Systematic bias appears as consistent offset from identity line
  - High-load scenarios may show larger deviations

METHODOLOGY: Scatter EN vs λ·EW with identity line, colored by policy, for each load scenario.

IMPACT: Validates modeling assumptions and exposes estimator/systematic errors requiring correction.
"""
        self.savePlotWithScientificCaption(fig, "littles_law_validation_comprehensive",
                                           "Comprehensive Little's Law Validation", caption)

    def plot09BehavioralClusteringAnalysis(self):
        """
        @brief Plot 09: Clustering + t-SNE/PCA visualization of policy behavior
        """
        logger.info("Creating behavioral clustering analysis (KMeans + t-SNE)")

        featureColumns = [
            'system_EW', 'system_EN', 'little_error', 'queue_imbalance',
            'throughput_efficiency', 'total_occupancy', 'arrival_rate_est'
        ]
        featureColumns = [f for f in featureColumns if f in self.df.columns]
        if not featureColumns:
            logger.error("No feature columns available for clustering")
            return

        sampleDf = self.df.sample(n=min(10000, len(self.df)), random_state=42)
        X = sampleDf[featureColumns].fillna(sampleDf[featureColumns].mean())

        scaler = StandardScaler()
        Xs = scaler.fit_transform(X)

        nClusters = 6
        km = KMeans(n_clusters=nClusters, random_state=42)
        clusterLabels = km.fit_predict(Xs)

        tsne = TSNE(n_components=2, random_state=42, perplexity=40, n_iter=1000)
        Xtsne = tsne.fit_transform(Xs)

        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        scatter = ax.scatter(Xtsne[:, 0], Xtsne[:, 1], c=clusterLabels, cmap='tab10', s=10, alpha=0.8)
        ax.set_title('Behavioral Clustering (t-SNE + KMeans)', fontweight='bold')
        ax.grid(True, alpha=0.25)
        plt.legend(*scatter.legend_elements(num=None), title="Cluster", bbox_to_anchor=(1.02, 1), loc='upper left')

        plt.tight_layout()

        caption = """
HYPOTHESIS: Policy behaviors cluster in feature space; clusters correspond to strategy families and load responses.

EXPECTED INSIGHTS:
  - Identify clusters representing similar operational regimes
  - Map clusters back to policies to find commonalities or anomalous policies

METHODOLOGY: KMeans clustering on standardized features combined with t-SNE projection for visualization.

IMPACT: Supports taxonomy of policies and targeted improvements for outlier behaviors.
"""
        self.savePlotWithScientificCaption(fig, "behavioral_clustering_analysis",
                                           "Behavioral Clustering Analysis (KMeans + t-SNE)", caption)

    def plot10ComparativePerformanceDashboard(self):
        """
        @brief Plot 10: Compact dashboard combining small multiples for key metrics per protagonist policy
        """
        logger.info("Creating comparative performance dashboard")

        protagonistPolicies = AnalysisConfig.getProtagonistPolicies()
        metrics = ['system_EW', 'system_EN', 'throughput_efficiency', 'little_error']
        metrics = [m for m in metrics if m in self.df.columns]

        nPolicies = len(protagonistPolicies)
        fig, axes = plt.subplots(nPolicies, len(metrics), figsize=(4 * len(metrics), 3 * nPolicies))
        if nPolicies == 1:
            axes = [axes]

        for i, policy in enumerate(protagonistPolicies):
            pdata = self.df[self.df['policy_name'] == policy]
            if pdata.empty:
                for j in range(len(metrics)):
                    axes[i][j].text(0.5, 0.5, f'No data for {policy}', ha='center', va='center')
                continue

            for j, metric in enumerate(metrics):
                ax = axes[i][j]
                medianData = pdata.groupby('time')[metric].median().reset_index().iloc[
                    ::AnalysisConfig.timeSeriesSampleStep]
                sns.lineplot(data=medianData, x='time', y=metric, ax=ax, linewidth=1.2)
                ax.set_title(f'{policy} — {metric}', fontsize=9)
                ax.grid(True, alpha=0.25)
                if metric == 'little_error':
                    ax.set_yscale('log')

        plt.tight_layout()

        caption = """
HYPOTHESIS: Compact dashboards for protagonist policies allow rapid comparative assessment of temporal median behavior.

EXPECTED INSIGHTS:
  - Differences in medians and temporal trends are quickly visible
  - Little's error temporal patterns identify episodic estimator failure

METHODOLOGY: Small multiples of median time series per protagonist policy across key metrics.

IMPACT: Quickly communicates operational differences for decision makers and engineers.
"""
        self.savePlotWithScientificCaption(fig, "comparative_performance_dashboard",
                                           "Comparative Performance Dashboard (Protagonist Policies)", caption)

    def generateAllVisualizations(self):
        """
        @brief Executes ALL visualization methods in sequence
        """
        logger.info("Starting comprehensive visualization generation for ALL data")

        visualizationMethods = [
            self.plot01TemporalEvolutionAllScenarios,
            self.plot02QueueDistributionViolinAllLoads,
            self.plot03ProtagonistPolicyDeepDive,
            self.plot04LoadScenarioComparativeAnalysis,
            self.plot05CorrelationAnalysisMatrix,
            self.plot06PerformanceRadarAllPolicies,
            self.plot07StatisticalDistributionAnalysis,
            self.plot08LittlesLawValidationComprehensive,
            self.plot09BehavioralClusteringAnalysis,
            self.plot10ComparativePerformanceDashboard
        ]

        for method in visualizationMethods:
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
        catalogPath = Path(AnalysisConfig.captionsPath) / "visualization_catalog.txt"

        protagonistPolicies = AnalysisConfig.getProtagonistPolicies()

        catalogContent = "COMPREHENSIVE VISUALIZATION CATALOG\n"
        catalogContent += "=" * 60 + "\n\n"
        catalogContent += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        catalogContent += f"Total Plots: {self.plotCounter - 1}\n"
        catalogContent += f"Total Policies: {self.df['policy_name'].nunique()}\n"
        catalogContent += f"Load Scenarios: {sorted(self.df['load_factor'].unique())}\n"
        catalogContent += f"Protagonist Policies: {', '.join(protagonistPolicies)}\n\n"

        for plotId, plotInfo in self.captionRegistry.items():
            catalogContent += f"PLOT {plotId:02d}: {plotInfo['caption_title']}\n"
            catalogContent += f"  Filename: {plotInfo['filename']}\n"
            catalogContent += f"  Analysis: {plotInfo['plot_name']}\n"
            catalogContent += "-" * 50 + "\n"

        with open(catalogPath, 'w', encoding='utf-8') as f:
            f.write(catalogContent)


# =================================================================================
# ENHANCED STATISTICAL & MACHINE LEARNING ENGINE
# =================================================================================
class EnhancedStatisticalLearningEngine:
    """
    @brief Enhanced statistical analysis and machine learning for ALL data
    """

    def __init__(self, dataFrame: pd.DataFrame):
        """
        @brief Initialize the statistical learning engine
        @param dataFrame: The complete dataset for analysis
        """
        self.df = dataFrame
        self.mlResults = {}
        self.statisticalTests = {}

    def performComprehensiveStatisticalAnalysis(self):
        """
        @brief Performs advanced statistical analysis including hypothesis testing for ALL data
        @return Descriptive statistics DataFrame
        """
        logger.info("Performing comprehensive statistical analysis for all policies and scenarios")

        descriptiveStats = self.df.groupby(['policy_name', 'load_factor']).agg({
            'system_EW': ['mean', 'std', 'min', 'max'],
            'system_EN': ['mean', 'std', 'min', 'max'],
            'total_occupancy': ['mean', 'max'],
            'throughput_efficiency': ['mean']
        })

        from scipy.stats import f_oneway
        policies = self.df['policy_name'].unique()
        anovaGroups = [self.df[self.df['policy_name'] == policy]['system_EW'] for policy in policies]
        anovaResult = f_oneway(*anovaGroups)

        self.statisticalTests['anova_policy_performance'] = {
            'f_statistic': anovaResult.statistic,
            'p_value': anovaResult.pvalue,
            'significance': anovaResult.pvalue < 0.05
        }

        protagonistPolicies = AnalysisConfig.getProtagonistPolicies()
        protagonistStats = self.df[self.df['policy_name'].isin(protagonistPolicies)]
        protagonistSummary = protagonistStats.groupby('policy_name').agg({
            'system_EW': ['mean', 'std'],
            'system_EN': ['mean', 'std'],
            'little_error': lambda x: np.abs(x).mean()
        }).round(4)

        reportPath = Path(AnalysisConfig.summariesPath) / "comprehensive_statistical_analysis.txt"

        with open(reportPath, 'w', encoding='utf-8') as f:
            f.write("COMPREHENSIVE STATISTICAL ANALYSIS REPORT\n")
            f.write("=" * 60 + "\n\n")

            f.write("DATASET OVERVIEW:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total samples: {len(self.df):,}\n")
            f.write(f"Policies analyzed: {len(policies)}\n")
            f.write(f"Load scenarios: {sorted(self.df['load_factor'].unique())}\n")
            f.write(f"Protagonist policies: {', '.join(protagonistPolicies)}\n\n")

            f.write("STATISTICAL TESTS:\n")
            f.write("-" * 30 + "\n")
            f.write("ANOVA - Policy Performance Differences:\n")
            f.write(f"  F-statistic: {anovaResult.statistic:.4f}\n")
            f.write(f"  P-value: {anovaResult.pvalue:.6f}\n")
            f.write(f"  Significant Difference: {anovaResult.pvalue < 0.05}\n\n")

            f.write("PROTAGONIST POLICIES SUMMARY:\n")
            f.write("-" * 30 + "\n")
            f.write(protagonistSummary.to_string())
            f.write("\n\n")

            f.write("COMPLETE DESCRIPTIVE STATISTICS:\n")
            f.write("-" * 30 + "\n")
            f.write(descriptiveStats.to_string())

        logger.info("Comprehensive statistical analysis completed")
        return descriptiveStats

    def performAdvancedDimensionalityReduction(self):
        """
        @brief Performs PCA and clustering analysis for ALL data
        @return Dimensionality reduction results dictionary
        """
        logger.info("Performing advanced dimensionality reduction for all data")

        featureColumns = [
            'system_EW', 'system_EN', 'little_error', 'queue_imbalance',
            'throughput_efficiency', 'total_occupancy', 'arrival_rate_est'
        ]
        featureColumns = [col for col in featureColumns if col in self.df.columns]

        sampleDf = self.df.sample(n=min(10000, len(self.df)), random_state=42)
        X = sampleDf[featureColumns]
        y = sampleDf['policy_name']

        X = X.fillna(X.mean())

        scaler = StandardScaler()
        XScaled = scaler.fit_transform(X)

        pca = PCA(n_components=2)
        XPca = pca.fit_transform(XScaled)

        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        viz = EnhancedScientificVisualizationEngine(self.df)
        protagonistPolicies = AnalysisConfig.getProtagonistPolicies()

        for policy in sorted(y.unique()):
            mask = y == policy
            color = viz.protagonistColors.get(policy, 'gray')
            alphaVal = 0.8 if policy in protagonistPolicies else 0.4
            size = 50 if policy in protagonistPolicies else 20

            axes[0].scatter(XPca[mask, 0], XPca[mask, 1],
                            label=policy, alpha=alphaVal, s=size, color=color)

        axes[0].set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%})')
        axes[0].set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%})')
        axes[0].set_title('PCA: Policy Behavioral Space\n(All Data)', fontweight='bold')
        axes[0].legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        axes[0].grid(True, alpha=0.3)

        loadFactors = sampleDf['load_factor']
        scatter = axes[1].scatter(XPca[:, 0], XPca[:, 1], c=loadFactors,
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

        self.mlResults['dimensionality_reduction'] = {
            'pca': pca,
            'explained_variance': pca.explained_variance_ratio_
        }

        return self.mlResults['dimensionality_reduction']

    def trainEnhancedRegressionModels(self):
        """
        @brief Trains enhanced regression models to predict system performance metrics
        @return Dictionary with regression results
        """
        logger.info("Training enhanced regression models for system performance prediction")

        featureColumns = [
            'total_occupancy', 'arrival_rate_est', 'q0_len', 'q1_len', 'q2_len',
            'server_busy', 'queue_imbalance', 'system_utilization', 'load_factor'
        ]
        featureColumns = [col for col in featureColumns if col in self.df.columns]

        targetColumn = 'system_EW'
        if targetColumn not in self.df.columns:
            logger.error(f"Target column {targetColumn} not found in dataset")
            return {}

        sampleDf = self.df.sample(n=min(20000, len(self.df)), random_state=42)
        X = sampleDf[featureColumns]
        y = sampleDf[targetColumn]

        X = X.fillna(X.mean())
        y = y.fillna(y.mean())

        XTrain, XTest, yTrain, yTest = train_test_split(
            X, y, test_size=AnalysisConfig.testSizeRatio, random_state=AnalysisConfig.randomState
        )

        scaler = StandardScaler()
        XTrainScaled = scaler.fit_transform(XTrain)
        XTestScaled = scaler.transform(XTest)

        models = {
            'LinearRegression': LinearRegression(),
            'Ridge': Ridge(alpha=1.0),
            'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
            'GradientBoosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
        }

        results = {}
        for name, model in models.items():
            model.fit(XTrainScaled, yTrain)
            yPred = model.predict(XTestScaled)
            mse = mean_squared_error(yTest, yPred)
            r2 = r2_score(yTest, yPred)

            results[name] = {
                'model': model,
                'mse': mse,
                'r2': r2,
                'feature_importance': getattr(model, 'feature_importances_', None)
            }

            logger.info(f"{name} - MSE: {mse:.4f}, R2: {r2:.4f}")

        bestModelName = max(results.keys(), key=lambda x: results[x]['r2'])
        bestR2 = results[bestModelName]['r2']

        self.mlResults['regression'] = {
            'results': results,
            'best_model': bestModelName,
            'best_r2': bestR2,
            'feature_columns': featureColumns
        }

        resultsPath = Path(AnalysisConfig.mlResultsPath) / "regression_analysis.txt"
        with open(resultsPath, 'w', encoding='utf-8') as f:
            f.write("ENHANCED REGRESSION ANALYSIS RESULTS\n")
            f.write("=" * 50 + "\n\n")
            for name, result in results.items():
                f.write(f"{name}:\n")
                f.write(f"  MSE: {result['mse']:.4f}\n")
                f.write(f"  R2: {result['r2']:.4f}\n\n")
            f.write(f"Best Model: {bestModelName} (R2: {bestR2:.4f})\n")

        logger.info(f"Regression analysis completed. Best model: {bestModelName} with R2: {bestR2:.4f}")
        return self.mlResults['regression']


# =================================================================================
# COMPREHENSIVE PIPELINE ORCHESTRATOR - ENHANCED
# =================================================================================
class EnhancedMM1Pipeline:
    """
    @brief Main orchestrator for the complete enhanced analysis pipeline
    """

    def __init__(self):
        """
        @brief Initialize the analysis pipeline
        """
        self.dataEngine = EnhancedDataIngestionEngine()
        self.visualizationEngine = None
        self.mlEngine = None
        self.analysisSummary = {}

    def executeCompleteAnalysis(self):
        """
        @brief Executes the complete enhanced analysis pipeline
        """
        logger.info("Starting Enhanced MM1 Analysis Pipeline")
        startTime = datetime.now()

        try:
            AnalysisConfig.setupDirectories()
            logger.info("Phase 1: Environment setup completed")

            logger.info("Phase 2: Loading and processing ALL 44 data files...")
            rawData = self.dataEngine.loadAndValidateAllData()
            cleanedData = self.dataEngine.performEnhancedDataCleaning()
            logger.info("Phase 2: Data ingestion and processing completed")

            logger.info("Phase 3: Performing comprehensive statistical analysis...")
            self.mlEngine = EnhancedStatisticalLearningEngine(cleanedData)
            statisticalResults = self.mlEngine.performComprehensiveStatisticalAnalysis()
            logger.info("Phase 3: Statistical analysis completed")

            logger.info("Phase 4: Generating comprehensive visualizations...")
            self.visualizationEngine = EnhancedScientificVisualizationEngine(cleanedData)
            self.visualizationEngine.generateAllVisualizations()
            logger.info("Phase 4: Comprehensive visualization completed")

            logger.info("Phase 5: Performing advanced machine learning analysis...")
            dimensionalityResults = self.mlEngine.performAdvancedDimensionalityReduction()
            regressionResults = self.mlEngine.trainEnhancedRegressionModels()
            logger.info("Phase 5: Machine learning analysis completed")

            logger.info("Phase 6: Generating final reports and summaries...")
            self._generateEnhancedComprehensiveSummary()
            logger.info("Phase 6: Final reporting completed")

            executionTime = datetime.now() - startTime
            self.analysisSummary['execution_time'] = executionTime
            self.analysisSummary['completion_status'] = 'SUCCESS'

            logger.info(f"Enhanced analysis pipeline completed successfully in {executionTime}")

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

        executiveSummaryPath = Path(AnalysisConfig.summariesPath) / "enhanced_executive_summary.txt"

        protagonistPolicies = AnalysisConfig.getProtagonistPolicies()

        with open(executiveSummaryPath, 'w', encoding='utf-8') as f:
            f.write("ENHANCED COMPREHENSIVE QUEUEING SYSTEM ANALYSIS - EXECUTIVE SUMMARY\n")
            f.write("=" * 80 + "\n\n")

            f.write("ANALYSIS OVERVIEW:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Data Files Processed: {len(self.dataEngine.fileMetadata)}/44\n")
            f.write(f"Total Data Points: {len(self.dataEngine.globalDataFrame):,}\n")
            f.write(f"Policies Analyzed: {self.dataEngine.globalDataFrame['policy_name'].nunique()}\n")
            f.write(f"Load Scenarios: {sorted(self.dataEngine.globalDataFrame['load_factor'].unique())}\n")
            f.write(f"Protagonist Policies: {', '.join(protagonistPolicies)}\n\n")

            f.write("KEY FINDINGS:\n")
            f.write("-" * 30 + "\n")

            avgPerformance = self.dataEngine.globalDataFrame.groupby('policy_name')['system_EW'].mean()
            bestPolicy = avgPerformance.idxmin()
            bestPerformance = avgPerformance.min()

            f.write(f"• Best Overall Performance: {bestPolicy} (EW: {bestPerformance:.2f})\n")

            protagonistData = self.dataEngine.globalDataFrame[
                self.dataEngine.globalDataFrame['policy_name'].isin(protagonistPolicies)
            ]

            f.write("• Protagonist Policy Rankings:\n")
            for policy in protagonistPolicies:
                if policy in avgPerformance.index:
                    policyRank = (avgPerformance.index == policy).argmax() + 1
                    policyPerf = avgPerformance[policy]
                    f.write(f"  - {policy}: Rank {policyRank}, EW: {policyPerf:.2f}\n")

            if hasattr(self.mlEngine, 'mlResults') and 'regression' in self.mlEngine.mlResults:
                bestR2 = self.mlEngine.mlResults['regression']['best_r2']
                f.write(f"• System EW Predictability: R² = {bestR2:.3f}\n")

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
