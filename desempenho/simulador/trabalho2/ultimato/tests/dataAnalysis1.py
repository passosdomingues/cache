#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Advanced Queueing Simulation Performance Analysis Toolkit
Author: Rafael Passos Domingues
Last Update: October 23, 2025

Comprehensive analysis of multi-queue scheduling policies with:
- Round Robin, Waiting Time Priority, and Utility-Based scheduling
- Comparative performance analysis across traffic intensities
- Statistical validation and visualization
- Machine learning insights for policy optimization
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


# =============================================================================
# CONFIGURATION CLASSES
# =============================================================================

class AnalysisConfiguration:
    """Centralizes all configurable parameters for the analysis pipeline."""

    def __init__(self):
        # Data Configuration
        self.dataDirectory = "results"
        self.filePattern = "queue_data_*_occupancy_*.csv"
        self.occupancyScenarios = ['0.800', '0.900', '0.950', '0.999']
        self.schedulingPolicies = ['RoundRobin', 'WaitingTimePriority', 'UtilityBased']

        # Column Name Mapping (CORRIGIDO - baseado nos cabeçalhos reais dos CSV)
        self.columnAverageNumberInSystem = 'averageNumberInSystem'
        self.columnAverageWaitingTime = 'averageWaitingTime'
        self.columnArrivalRate = 'measuredArrivalRate'
        self.columnOccupancy = 'measuredOccupancy'
        self.columnQueueSizes = ['queueSize1', 'queueSize2', 'queueSize3']
        self.columnTimestamp = 'timestamp'
        self.columnSampleIndex = 'sampleIndex'
        self.columnLittlesLawError = 'littlesLawError'

        # Steady-State Detection Configuration
        self.stabilizationMetric = self.columnAverageNumberInSystem
        self.stabilizationWindowSize = 100
        self.stabilizationPatience = 5
        self.stabilizationTolerance = 0.02

        # Machine Learning Configuration
        self.machineLearningTestSize = 0.20
        self.machineLearningRandomState = 42
        self.machineLearningFeatures = [
                                           self.columnAverageNumberInSystem,
                                           self.columnAverageWaitingTime,
                                           self.columnArrivalRate,
                                           self.columnOccupancy
                                       ] + self.columnQueueSizes


class VisualizationConfiguration:
    """Manages all visualization settings and output formatting."""

    def __init__(self, outputDirectory: Path):
        self.outputDirectory = outputDirectory
        self.plotStyle = 'seaborn-v0_8-whitegrid'
        self.colorPalette = "viridis"
        self.figureDPI = 300
        self.defaultFigureSize = (14, 8)
        self.outputDirectory.mkdir(parents=True, exist_ok=True)
        self._applyVisualizationSettings()

    def _applyVisualizationSettings(self):
        """Applies consistent styling to all matplotlib plots."""
        plt.style.use(self.plotStyle)
        sns.set_palette(self.colorPalette)
        plt.rcParams.update({
            'figure.dpi': self.figureDPI,
            'savefig.dpi': self.figureDPI,
            'font.size': 12,
            'axes.titlesize': 16,
            'axes.labelsize': 12,
            'legend.fontsize': 10,
            'figure.titlesize': 18
        })


# =============================================================================
# CORE ANALYSIS COMPONENTS
# =============================================================================

class SimulationDataLoader:
    """Handles loading, validation, and preprocessing of simulation data."""

    def __init__(self, config: AnalysisConfiguration):
        self.config = config

    def loadAllSimulationData(self) -> Dict[str, pd.DataFrame]:
        """
        Loads all simulation data files and organizes them by policy and scenario.

        Returns:
            Dictionary mapping (policy, scenario) tuples to DataFrames
        """
        print("Loading simulation data from CSV files...")

        allData = {}
        dataFiles = glob(str(Path(self.config.dataDirectory) / self.config.filePattern))

        if not dataFiles:
            raise FileNotFoundError(f"No simulation data files found in {self.config.dataDirectory}/")

        for filePath in dataFiles:
            try:
                # Extract policy and scenario from filename
                fileName = Path(filePath).stem
                parts = fileName.split('_')

                # Expected format: queue_data_{Policy}_occupancy_{Scenario}
                if len(parts) >= 5 and parts[2] in self.config.schedulingPolicies:
                    policy = parts[2]
                    scenario = parts[4]  # occupancy value

                    # Load and validate the data
                    df = pd.read_csv(filePath)

                    if self._validateDataFrame(df, policy, scenario):
                        df = self._augmentDataFrameWithMetadata(df, policy, scenario)
                        key = f"{policy}_{scenario}"
                        allData[key] = df
                        print(f"  ✓ Loaded {len(df)} records: {policy} (ρ={scenario})")
                    else:
                        print(f"  ✗ Validation failed: {fileName}")

            except Exception as error:
                print(f"  ✗ Error loading {filePath}: {error}")

        print(f"Successfully loaded {len(allData)} simulation datasets")
        return allData

    def _validateDataFrame(self, dataFrame: pd.DataFrame, policy: str, scenario: str) -> bool:
        """Validates the structure and integrity of a loaded DataFrame."""
        requiredColumns = [
                              self.config.columnTimestamp,
                              self.config.columnSampleIndex,
                              self.config.columnAverageNumberInSystem,
                              self.config.columnAverageWaitingTime
                          ] + self.config.columnQueueSizes

        missingColumns = [col for col in requiredColumns if col not in dataFrame.columns]

        if missingColumns:
            print(f"ERROR: Missing required columns in {policy}_{scenario}: {missingColumns}")
            print(f"Available columns: {list(dataFrame.columns)}")
            return False

        # Check for excessive missing values
        missingValues = dataFrame[requiredColumns].isnull().sum()
        totalMissing = missingValues.sum()

        if totalMissing > 0:
            missingPercentage = (totalMissing / (len(dataFrame) * len(requiredColumns))) * 100
            print(f"WARNING: {totalMissing} missing values ({missingPercentage:.2f}%) in {policy}_{scenario}")

        return True

    def _augmentDataFrameWithMetadata(self, dataFrame: pd.DataFrame, policy: str, scenario: str) -> pd.DataFrame:
        """Adds metadata columns to the DataFrame for analysis."""
        dataFrame['schedulingPolicy'] = policy
        dataFrame['occupancyScenario'] = f"ρ = {scenario}"
        dataFrame['occupancyValue'] = float(scenario)
        dataFrame['totalQueueSize'] = dataFrame[self.config.columnQueueSizes].sum(axis=1)
        dataFrame['policyScenario'] = f"{policy} (ρ={scenario})"

        return dataFrame


class SteadyStateDetector:
    """Identifies the steady-state phase of simulation data."""

    def __init__(self, config: AnalysisConfiguration):
        self.config = config

    def detectSteadyStateStart(self, dataFrame: pd.DataFrame) -> int:
        """
        Detects the start of the steady-state phase using relative mean stabilization.

        Args:
            dataFrame: Input data with time series metrics

        Returns:
            Index indicating the start of steady-state phase
        """
        metricData = dataFrame[self.config.stabilizationMetric].values
        windowSize = self.config.stabilizationWindowSize

        print(f"  Analyzing stabilization for {len(metricData)} samples (window: {windowSize})")

        # Fallback for insufficient data
        if len(metricData) < 2 * windowSize:
            fallbackIndex = int(len(metricData) * 0.25)
            print(f"  Insufficient data, using fallback index: {fallbackIndex}")
            return fallbackIndex

        # Calculate rolling means with overlapping windows
        windowMeans = []
        stepSize = max(1, windowSize // 4)  # 75% overlap for smooth detection

        for startIndex in range(0, len(metricData) - windowSize + 1, stepSize):
            windowMean = np.mean(metricData[startIndex:startIndex + windowSize])
            windowMeans.append((startIndex, windowMean))

        if len(windowMeans) < 2:
            fallbackIndex = int(len(metricData) * 0.25)
            print(f"  Not enough windows, using fallback index: {fallbackIndex}")
            return fallbackIndex

        # Detect stabilization point
        stabilizationIndex = 0
        consecutiveStableWindows = 0

        for i in range(1, len(windowMeans)):
            previousIndex, previousMean = windowMeans[i - 1]
            currentIndex, currentMean = windowMeans[i]

            if previousMean > 1e-9:  # Avoid division by zero
                relativeDifference = abs(currentMean - previousMean) / previousMean

                if relativeDifference < self.config.stabilizationTolerance:
                    consecutiveStableWindows += 1
                    if consecutiveStableWindows >= self.config.stabilizationPatience:
                        stabilizationIndex = max(0, previousIndex)
                        print(f"  Stabilization detected at sample {stabilizationIndex} "
                              f"(relative change < {self.config.stabilizationTolerance * 100:.1f}% "
                              f"for {consecutiveStableWindows} consecutive windows)")
                        return stabilizationIndex
                else:
                    consecutiveStableWindows = 0
                    stabilizationIndex = currentIndex

        # Fallback: use variance reduction method
        rollingStd = pd.Series(metricData).rolling(window=windowSize).std().dropna()
        if len(rollingStd) > 10:
            relativeStd = rollingStd / rollingStd.mean()
            lowVarianceIndices = np.where(relativeStd < 1.5)[0]
            if len(lowVarianceIndices) > 0:
                stabilizationIndex = lowVarianceIndices[0]
                print(f"  Stabilization detected at sample {stabilizationIndex} (variance reduction)")
                return stabilizationIndex

        fallbackIndex = int(len(metricData) * 0.10)
        print(f"  WARNING: Clear stabilization not detected, using fallback: {fallbackIndex}")
        return fallbackIndex


class PerformanceAnalyzer:
    """Performs comparative analysis of scheduling policies."""

    def __init__(self, config: AnalysisConfiguration):
        self.config = config

    def generateComparativeSummary(self, steadyStateData: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Generates a comprehensive summary of performance metrics across all scenarios.

        Args:
            steadyStateData: Dictionary of steady-state DataFrames

        Returns:
            DataFrame with aggregated performance statistics
        """
        print("\nGenerating comparative performance summary...")

        summaryRows = []

        for scenarioKey, dataFrame in steadyStateData.items():
            policy = dataFrame['schedulingPolicy'].iloc[0]
            occupancy = dataFrame['occupancyValue'].iloc[0]

            print(f"  Processing {policy} (ρ={occupancy:.3f}): {len(dataFrame)} samples")

            summaryRow = {
                'schedulingPolicy': policy,
                'occupancy': occupancy,
                'sampleCount': len(dataFrame)
            }

            # Calculate key performance metrics
            metricsToCalculate = [
                (self.config.columnAverageNumberInSystem, 'numberInSystem'),
                (self.config.columnAverageWaitingTime, 'waitingTime'),
                ('totalQueueSize', 'totalQueueSize')
            ]

            for column, metricName in metricsToCalculate:
                if column in dataFrame.columns:
                    values = dataFrame[column]
                    summaryRow[f'{metricName}_mean'] = values.mean()
                    summaryRow[f'{metricName}_std'] = values.std()
                    summaryRow[f'{metricName}_median'] = values.median()
                    summaryRow[f'{metricName}_q1'] = values.quantile(0.25)
                    summaryRow[f'{metricName}_q3'] = values.quantile(0.75)

            summaryRows.append(summaryRow)

        summaryDataFrame = pd.DataFrame(summaryRows)

        # Print summary statistics
        self._printSummaryStatistics(summaryDataFrame)

        return summaryDataFrame

    def _printSummaryStatistics(self, summaryDataFrame: pd.DataFrame):
        """Prints formatted summary statistics to console."""
        print("\n" + "=" * 80)
        print("PERFORMANCE SUMMARY STATISTICS")
        print("=" * 80)

        for policy in summaryDataFrame['schedulingPolicy'].unique():
            policyData = summaryDataFrame[summaryDataFrame['schedulingPolicy'] == policy]
            print(f"\n{policy} Scheduling:")
            print("-" * 40)

            for _, row in policyData.iterrows():
                print(f"  ρ = {row['occupancy']:.3f}:")
                print(f"    E[N] = {row['numberInSystem_mean']:.2f} ± {row['numberInSystem_std']:.2f}")
                print(f"    E[W] = {row['waitingTime_mean']:.2f} ± {row['waitingTime_std']:.2f}")
                print(f"    Samples: {row['sampleCount']}")


class AnalyticalModeler:
    """Fits analytical models to simulation results for theoretical validation."""

    def fitPolynomialModel(self, xValues: np.ndarray, yValues: np.ndarray,
                           maxDegree: int = 3) -> Dict[str, Any]:
        """
        Fits polynomial models to find the best analytical approximation.

        Args:
            xValues: Independent variable (typically occupancy)
            yValues: Dependent variable (performance metric)
            maxDegree: Maximum polynomial degree to test

        Returns:
            Dictionary with model parameters and quality metrics
        """
        print(f"\nFitting polynomial model (max degree: {maxDegree})...")

        if len(xValues) < maxDegree + 1:
            maxDegree = max(1, len(xValues) - 1)
            print(f"  Reduced max degree to {maxDegree} due to limited data points")

        bestModel = {
            'rSquared': -np.inf,
            'polynomialDegree': 0,
            'regressionModel': None,
            'polynomialFeatures': None,
            'equation': 'No valid model'
        }

        for degree in range(1, maxDegree + 1):
            try:
                polynomialTransformer = PolynomialFeatures(degree=degree)
                xPolynomial = polynomialTransformer.fit_transform(xValues.reshape(-1, 1))

                model = LinearRegression().fit(xPolynomial, yValues)
                predictions = model.predict(xPolynomial)
                rSquared = r2_score(yValues, predictions)

                if rSquared > bestModel['rSquared']:
                    bestModel.update({
                        'rSquared': rSquared,
                        'polynomialDegree': degree,
                        'regressionModel': model,
                        'polynomialFeatures': polynomialTransformer
                    })
            except Exception as error:
                print(f"  Warning: Failed to fit degree {degree} polynomial: {error}")
                continue

        if bestModel['regressionModel'] is not None:
            coefficients = bestModel['regressionModel'].coef_.flatten()
            intercept = bestModel['regressionModel'].intercept_

            # Build human-readable equation
            equationTerms = [f"{intercept:.4f}"]
            for power in range(1, len(coefficients)):
                if abs(coefficients[power]) > 1e-10:
                    equationTerms.append(f"{coefficients[power]:+.4f}·ρ^{power}")

            bestModel['equation'] = "y = " + " + ".join(equationTerms)

            print(f"  Best model: degree {bestModel['polynomialDegree']}")
            print(f"  Equation: {bestModel['equation']}")
            print(f"  R² = {bestModel['rSquared']:.6f}")
        else:
            print("  Warning: No valid polynomial model could be fitted")

        return bestModel


class MachineLearningPipeline:
    """Applies machine learning techniques for deeper insights."""

    def __init__(self, config: AnalysisConfiguration):
        self.config = config
        self.modelDirectory = Path("machine_learning_models")
        self.modelDirectory.mkdir(exist_ok=True)

    def executeCompletePipeline(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[PCA], pd.Series]:
        """
        Executes the complete ML pipeline including clustering and regression.

        Args:
            data: Combined steady-state data from all scenarios

        Returns:
            Tuple of (clustered data, PCA model, feature importance)
        """
        if data.empty:
            print("Warning: No data available for machine learning pipeline")
            return data, None, pd.Series(dtype=float)

        print("\nExecuting Machine Learning Pipeline...")
        print("=" * 50)

        # Prepare features
        features = data[self.config.machineLearningFeatures].dropna()
        if features.empty:
            print("Warning: No features available after cleaning")
            return data, None, pd.Series(dtype=float)

        print(f"Processing {len(features)} samples with {len(features.columns)} features")

        # Execute unsupervised learning
        clusteredData, pcaModel = self._performUnsupervisedLearning(data, features)

        # Execute supervised learning
        featureImportance = self._performSupervisedLearning(clusteredData)

        return clusteredData, pcaModel, featureImportance

    def _performUnsupervisedLearning(self, originalData: pd.DataFrame,
                                     features: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[PCA]]:
        """Performs PCA and K-means clustering for pattern discovery."""
        print("\n--- Unsupervised Learning: PCA and Clustering ---")

        try:
            # Standardize features
            scaler = StandardScaler()
            scaledFeatures = scaler.fit_transform(features)

            # Apply PCA for dimensionality reduction
            pca = PCA(n_components=2)
            principalComponents = pca.fit_transform(scaledFeatures)
            explainedVariance = np.sum(pca.explained_variance_ratio_)
            print(f"PCA: {explainedVariance:.2%} variance explained by 2 components")

            # Determine optimal number of clusters
            clusterRange = range(2, min(8, len(scaledFeatures) // 10))
            silhouetteScores = []

            for clusterCount in clusterRange:
                try:
                    kmeans = KMeans(n_clusters=clusterCount,
                                    random_state=self.config.machineLearningRandomState,
                                    n_init=10)
                    clusterLabels = kmeans.fit_predict(scaledFeatures)

                    if len(np.unique(clusterLabels)) > 1:
                        score = silhouette_score(scaledFeatures, clusterLabels)
                        silhouetteScores.append(score)
                    else:
                        silhouetteScores.append(-1)
                except Exception as error:
                    print(f"  Warning: Clustering failed for k={clusterCount}: {error}")
                    silhouetteScores.append(-1)

            if silhouetteScores and max(silhouetteScores) > 0.1:
                optimalClusters = clusterRange[np.argmax(silhouetteScores)]
                bestScore = max(silhouetteScores)
                print(f"K-means: Optimal clusters = {optimalClusters} (silhouette: {bestScore:.3f})")

                # Apply clustering with optimal k
                kmeans = KMeans(n_clusters=optimalClusters,
                                random_state=self.config.machineLearningRandomState,
                                n_init=10)
                clusterAssignments = kmeans.fit_predict(scaledFeatures)

                # Add results to data
                resultData = originalData.copy()
                validIndices = features.index
                resultData.loc[validIndices, 'cluster'] = clusterAssignments
                resultData.loc[validIndices, 'principalComponent1'] = principalComponents[:, 0]
                resultData.loc[validIndices, 'principalComponent2'] = principalComponents[:, 1]

                return resultData, pca
            else:
                print("Warning: No meaningful clusters found (low silhouette scores)")
                return originalData, pca

        except Exception as error:
            print(f"Error in unsupervised learning: {error}")
            return originalData, None

    def _performSupervisedLearning(self, data: pd.DataFrame) -> pd.Series:
        """Trains Random Forest regressor to predict performance from features."""
        print("\n--- Supervised Learning: Random Forest Regression ---")

        try:
            # Prepare data for regression
            regressionData = data.copy().dropna(
                subset=self.config.machineLearningFeatures + ['occupancyValue']
            )

            if regressionData.empty or regressionData['occupancyValue'].nunique() < 2:
                print("Warning: Insufficient data for regression analysis")
                return pd.Series(dtype=float)

            print(f"Regression dataset: {len(regressionData)} samples, "
                  f"occupancy range: {regressionData['occupancyValue'].min():.3f} to "
                  f"{regressionData['occupancyValue'].max():.3f}")

            features = regressionData[self.config.machineLearningFeatures]
            target = regressionData['occupancyValue']

            # Split data into training and testing sets
            featuresTrain, featuresTest, targetTrain, targetTest = train_test_split(
                features, target,
                test_size=self.config.machineLearningTestSize,
                random_state=self.config.machineLearningRandomState
            )

            # Standardize features
            scaler = StandardScaler()
            featuresTrainScaled = scaler.fit_transform(featuresTrain)
            featuresTestScaled = scaler.transform(featuresTest)

            # Train Random Forest regressor
            model = RandomForestRegressor(
                n_estimators=100,
                random_state=self.config.machineLearningRandomState
            )
            model.fit(featuresTrainScaled, targetTrain)

            # Evaluate model performance
            predictions = model.predict(featuresTestScaled)
            mse = mean_squared_error(targetTest, predictions)
            r2 = r2_score(targetTest, predictions)
            mae = np.mean(np.abs(targetTest - predictions))

            print("Regression Performance:")
            print(f"  Mean Squared Error: {mse:.6f}")
            print(f"  R² Score: {r2:.4f}")
            print(f"  Mean Absolute Error: {mae:.4f}")

            # Save trained models
            joblib.dump(model, self.modelDirectory / "random_forest_regressor.joblib")
            joblib.dump(scaler, self.modelDirectory / "feature_scaler.joblib")
            print(f"Models saved to '{self.modelDirectory}'")

            # Analyze feature importance
            importance = pd.Series(
                model.feature_importances_,
                index=self.config.machineLearningFeatures
            )
            importance = importance.sort_values(ascending=False)

            print("\nFeature Importance Ranking:")
            for feature, score in importance.items():
                print(f"  {feature}: {score:.4f}")

            return importance

        except Exception as error:
            print(f"Error in supervised learning: {error}")
            return pd.Series(dtype=float)


# =============================================================================
# VISUALIZATION ENGINE
# =============================================================================

class ComparativeVisualizer:
    """Generates comprehensive comparative visualizations."""

    def __init__(self, config: AnalysisConfiguration, visConfig: VisualizationConfiguration):
        self.config = config
        self.visConfig = visConfig

    def generateAllComparativePlots(self, rawData: Dict[str, pd.DataFrame],
                                    steadyStateData: Dict[str, pd.DataFrame],
                                    summaryData: pd.DataFrame,
                                    analyticalModels: Dict[str, Dict[str, Any]],
                                    mlResults: Tuple[pd.DataFrame, Optional[PCA], pd.Series]):
        """Generates the complete set of comparative analysis plots."""
        print("\nGenerating Comparative Visualizations...")

        clusteredData, pcaModel, featureImportance = mlResults

        # 1. Policy Comparison Plot (Key Result)
        self._plotPolicyComparison(summaryData)

        # 2. Steady-State Detection Visualization
        self._plotSteadyStateDetection(rawData, steadyStateData)

        # 3. Analytical Model Fitting
        self._plotAnalyticalModels(summaryData, analyticalModels)

        # 4. Time Series Behavior Comparison
        self._plotTimeSeriesComparison(steadyStateData)

        # 5. Distribution Analysis
        self._plotPerformanceDistributions(steadyStateData)

        # 6. Machine Learning Insights
        self._plotMachineLearningResults(clusteredData, pcaModel, featureImportance)

        print("✓ All visualizations completed successfully")

    def _plotPolicyComparison(self, summaryData: pd.DataFrame):
        """Creates the main policy comparison plot (the 'money plot')."""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            axes = axes.flat

            metrics = [
                ('numberInSystem_mean', 'Average Number in System (E[N])'),
                ('waitingTime_mean', 'Average Waiting Time (E[W])'),
                ('numberInSystem_std', 'StdDev of Number in System'),
                ('waitingTime_std', 'StdDev of Waiting Time')
            ]

            for idx, (metric, title) in enumerate(metrics):
                ax = axes[idx]

                for policy in self.config.schedulingPolicies:
                    policyData = summaryData[summaryData['schedulingPolicy'] == policy]

                    if not policyData.empty:
                        x = policyData['occupancy']
                        y = policyData[metric]

                        # Plot with error bars for mean metrics
                        if 'mean' in metric:
                            yError = policyData[metric.replace('_mean', '_std')]
                            ax.errorbar(x, y, yerr=yError, fmt='-o', capsize=5,
                                        label=policy, linewidth=2, markersize=6)
                        else:
                            ax.plot(x, y, 'o-', label=policy, linewidth=2, markersize=6)

                ax.set_xlabel('Traffic Intensity (ρ)')
                ax.set_ylabel(title)
                ax.set_title(f'{title} vs. Traffic Intensity')
                ax.legend()
                ax.grid(True, alpha=0.3)

                # Set appropriate y-axis scaling
                if 'Waiting' in title:
                    ax.set_yscale('log')  # Waiting times often need log scale

            plt.suptitle('Scheduling Policy Performance Comparison',
                         fontsize=18, fontweight='bold')
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            plt.savefig(self.visConfig.outputDirectory / "policy_comparison.png",
                        dpi=self.visConfig.figureDPI, bbox_inches='tight')
            plt.close()
            print("✓ Generated 'policy_comparison.png'")

        except Exception as error:
            print(f"✗ Failed to generate policy comparison: {error}")

    def _plotSteadyStateDetection(self, rawData: Dict[str, pd.DataFrame],
                                  steadyStateData: Dict[str, pd.DataFrame]):
        """Visualizes steady-state detection for each scenario."""
        try:
            scenarios = list(rawData.keys())[:4]  # Plot first 4 scenarios for clarity
            nScenarios = len(scenarios)

            nCols = min(2, nScenarios)
            nRows = (nScenarios + nCols - 1) // nCols

            fig, axes = plt.subplots(nRows, nCols, figsize=(16, 6 * nRows))
            if nScenarios == 1:
                axes = np.array([axes])
            axes = axes.flat

            for idx, scenarioKey in enumerate(scenarios):
                ax = axes[idx]
                rawDf = rawData[scenarioKey]
                steadyDf = steadyStateData[scenarioKey]

                policy = rawDf['schedulingPolicy'].iloc[0]
                occupancy = rawDf['occupancyValue'].iloc[0]

                # Use sample index for x-axis
                xValues = rawDf[self.config.columnSampleIndex]
                yValues = rawDf[self.config.stabilizationMetric]

                # Plot full data series
                ax.plot(xValues, yValues, alpha=0.7, linewidth=1,
                        label='Transient Phase', color='blue')

                # Mark steady-state region
                if len(steadyDf) > 0:
                    steadyStart = steadyDf[self.config.columnSampleIndex].iloc[0]
                    ax.axvline(x=steadyStart, color='red', linestyle='--',
                               linewidth=2, label='Steady-State Start')
                    ax.axvspan(steadyStart, xValues.max(), alpha=0.2,
                               color='green', label='Steady-State Region')

                ax.set_title(f'{policy} Policy (ρ = {occupancy})', fontsize=14)
                ax.set_xlabel('Sample Index')
                ax.set_ylabel('Number in System (E[N])')
                ax.legend()
                ax.grid(True, alpha=0.3)

            # Hide empty subplots
            for idx in range(len(scenarios), len(axes)):
                axes[idx].set_visible(False)

            plt.suptitle('Steady-State Phase Detection Across Policies',
                         fontsize=16, fontweight='bold')
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            plt.savefig(self.visConfig.outputDirectory / "steady_state_detection.png",
                        dpi=self.visConfig.figureDPI, bbox_inches='tight')
            plt.close()
            print("✓ Generated 'steady_state_detection.png'")

        except Exception as error:
            print(f"✗ Failed to generate steady-state plot: {error}")

    def _plotAnalyticalModels(self, summaryData: pd.DataFrame,
                              analyticalModels: Dict[str, Dict[str, Any]]):
        """Plots analytical model fits against simulation data."""
        try:
            if len(summaryData) < 2:
                print("Skipping analytical models plot: insufficient data")
                return

            fig, axes = plt.subplots(1, 2, figsize=(16, 6))

            metrics = [
                (self.config.columnAverageNumberInSystem, 'Average Number in System (E[N])'),
                (self.config.columnAverageWaitingTime, 'Average Waiting Time (E[W])')
            ]

            for idx, (metric, title) in enumerate(metrics):
                ax = axes[idx]
                modelInfo = analyticalModels[metric]

                # Plot simulation data points
                for policy in self.config.schedulingPolicies:
                    policyData = summaryData[summaryData['schedulingPolicy'] == policy]
                    if not policyData.empty:
                        ax.scatter(policyData['occupancy'], policyData[f'{metric.split("_")[-1]}_mean'],
                                   s=80, alpha=0.7, label=policy)

                # Plot fitted model if available
                if modelInfo['regressionModel']:
                    occupancyRange = np.linspace(
                        summaryData['occupancy'].min() * 0.95,
                        summaryData['occupancy'].max() * 1.05,
                        200
                    )
                    xPoly = modelInfo['polynomialFeatures'].transform(occupancyRange.reshape(-1, 1))
                    yPred = modelInfo['regressionModel'].predict(xPoly)

                    ax.plot(occupancyRange, yPred, 'k-', linewidth=3,
                            label=f"Polynomial Fit (R² = {modelInfo['rSquared']:.4f})")

                ax.set_xlabel('Traffic Intensity (ρ)')
                ax.set_ylabel(title)
                ax.set_title(f'Analytical Model: {title}')
                ax.legend()
                ax.grid(True, alpha=0.3)

                if 'Waiting' in title:
                    ax.set_yscale('log')

            plt.suptitle('Analytical Performance Modeling vs. Simulation Data',
                         fontsize=16, fontweight='bold')
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            plt.savefig(self.visConfig.outputDirectory / "analytical_models.png",
                        dpi=self.visConfig.figureDPI, bbox_inches='tight')
            plt.close()
            print("✓ Generated 'analytical_models.png'")

        except Exception as error:
            print(f"✗ Failed to generate analytical models plot: {error}")

    def _plotTimeSeriesComparison(self, steadyStateData: Dict[str, pd.DataFrame]):
        """Compares time series behavior across policies for high-load scenario."""
        try:
            # Focus on high occupancy scenario for clear differences
            highOccupancyData = {}
            for key, df in steadyStateData.items():
                if df['occupancyValue'].iloc[0] >= 0.95:  # High load scenario
                    highOccupancyData[key] = df

            if not highOccupancyData:
                print("No high-occupancy data for time series comparison")
                return

            fig, axes = plt.subplots(2, 2, figsize=(16, 10))
            axes = axes.flat

            metrics = [
                (self.config.columnAverageNumberInSystem, 'Number in System (E[N])'),
                (self.config.columnAverageWaitingTime, 'Waiting Time (E[W])'),
                ('totalQueueSize', 'Total Queue Size'),
                (self.config.columnOccupancy, 'Server Occupancy')
            ]

            for idx, (metric, title) in enumerate(metrics):
                ax = axes[idx]

                for scenarioKey, df in highOccupancyData.items():
                    policy = df['schedulingPolicy'].iloc[0]
                    occupancy = df['occupancyValue'].iloc[0]

                    # Plot first 500 samples for clarity
                    plotData = df.head(500)
                    if self.config.columnSampleIndex in plotData.columns:
                        x = plotData[self.config.columnSampleIndex]
                    else:
                        x = plotData.index

                    y = plotData[metric]
                    ax.plot(x, y, alpha=0.7, linewidth=1.5,
                            label=f'{policy} (ρ={occupancy})')

                ax.set_xlabel('Sample Index')
                ax.set_ylabel(title)
                ax.set_title(f'{title} Time Series')
                if idx == 0:  # Legend only on first plot
                    ax.legend()
                ax.grid(True, alpha=0.3)

            plt.suptitle('Time Series Behavior Under High Load (First 500 Samples)',
                         fontsize=16, fontweight='bold')
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            plt.savefig(self.visConfig.outputDirectory / "time_series_comparison.png",
                        dpi=self.visConfig.figureDPI, bbox_inches='tight')
            plt.close()
            print("✓ Generated 'time_series_comparison.png'")

        except Exception as error:
            print(f"✗ Failed to generate time series comparison: {error}")

    def _plotPerformanceDistributions(self, steadyStateData: Dict[str, pd.DataFrame]):
        """Compares performance metric distributions across policies."""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(16, 10))
            axes = axes.flat

            metrics = [
                (self.config.columnAverageNumberInSystem, 'Number in System (E[N])'),
                (self.config.columnAverageWaitingTime, 'Waiting Time (E[W])'),
                ('totalQueueSize', 'Total Queue Size'),
                (self.config.columnOccupancy, 'Server Occupancy')
            ]

            for idx, (metric, title) in enumerate(metrics):
                ax = axes[idx]

                plotData = []
                labels = []

                for scenarioKey, df in steadyStateData.items():
                    if metric in df.columns:
                        policy = df['schedulingPolicy'].iloc[0]
                        occupancy = df['occupancyValue'].iloc[0]

                        plotData.append(df[metric].values)
                        labels.append(f'{policy} (ρ={occupancy})')

                if plotData:
                    # Use KDE for smooth distribution visualization
                    for data, label in zip(plotData, labels):
                        sns.kdeplot(data, ax=ax, label=label, alpha=0.7)

                    ax.set_xlabel(title)
                    ax.set_ylabel('Density')
                    ax.set_title(f'Distribution of {title}')
                    if idx == 0:  # Legend only on first plot
                        ax.legend()
                    ax.grid(True, alpha=0.3)

            plt.suptitle('Performance Metric Distributions Across Policies',
                         fontsize=16, fontweight='bold')
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            plt.savefig(self.visConfig.outputDirectory / "performance_distributions.png",
                        dpi=self.visConfig.figureDPI, bbox_inches='tight')
            plt.close()
            print("✓ Generated 'performance_distributions.png'")

        except Exception as error:
            print(f"✗ Failed to generate distribution plot: {error}")

    def _plotMachineLearningResults(self, clusteredData: pd.DataFrame,
                                    pcaModel: Optional[PCA],
                                    featureImportance: pd.Series):
        """Visualizes machine learning insights including clustering and feature importance."""
        try:
            fig, axes = plt.subplots(1, 2, figsize=(16, 6))

            # Plot 1: PCA Clustering Results
            if pcaModel is not None and 'cluster' in clusteredData.columns:
                ax1 = axes[0]
                plotData = clusteredData.dropna(subset=['cluster', 'principalComponent1', 'principalComponent2'])

                if len(plotData) > 0:
                    scatter = ax1.scatter(plotData['principalComponent1'],
                                          plotData['principalComponent2'],
                                          c=plotData['cluster'], cmap='viridis',
                                          alpha=0.6, s=30)
                    plt.colorbar(scatter, ax=ax1, label='Cluster')

                    # Add policy information
                    for policy in plotData['schedulingPolicy'].unique():
                        policyData = plotData[plotData['schedulingPolicy'] == policy]
                        ax1.scatter([], [], alpha=0.6, s=30, label=policy)

                    ax1.set_xlabel(f'Principal Component 1 ({pcaModel.explained_variance_ratio_[0]:.2%} variance)')
                    ax1.set_ylabel(f'Principal Component 2 ({pcaModel.explained_variance_ratio_[1]:.2%} variance)')
                    ax1.set_title('K-means Clustering on Performance Features')
                    ax1.legend()
                    ax1.grid(True, alpha=0.3)

            # Plot 2: Feature Importance
            if not featureImportance.empty:
                ax2 = axes[1]
                featureImportance.sort_values().plot(kind='barh', ax=ax2, color='lightcoral')
                ax2.set_title('Random Forest Feature Importance')
                ax2.set_xlabel('Importance Score')
                ax2.grid(True, alpha=0.3, axis='x')

            plt.suptitle('Machine Learning Insights from Simulation Data',
                         fontsize=16, fontweight='bold')
            plt.tight_layout(rect=[0, 0, 1, 0.96])
            plt.savefig(self.visConfig.outputDirectory / "machine_learning_insights.png",
                        dpi=self.visConfig.figureDPI, bbox_inches='tight')
            plt.close()
            print("✓ Generated 'machine_learning_insights.png'")

        except Exception as error:
            print(f"✗ Failed to generate ML results plot: {error}")


# =============================================================================
# MAIN ANALYSIS PIPELINE
# =============================================================================

class SimulationAnalysisPipeline:
    """Orchestrates the complete analysis workflow from data loading to visualization."""

    def __init__(self):
        self.config = AnalysisConfiguration()
        self.visConfig = VisualizationConfiguration(Path(self.config.dataDirectory) / "analysis_plots")
        self.dataLoader = SimulationDataLoader(self.config)
        self.steadyStateDetector = SteadyStateDetector(self.config)
        self.performanceAnalyzer = PerformanceAnalyzer(self.config)
        self.analyticalModeler = AnalyticalModeler()
        self.machineLearningPipeline = MachineLearningPipeline(self.config)
        self.visualizer = ComparativeVisualizer(self.config, self.visConfig)

    def executeCompleteAnalysis(self):
        """Executes the end-to-end analysis pipeline."""
        print("=" * 80)
        print("ADVANCED QUEUEING SIMULATION ANALYSIS PIPELINE")
        print("=" * 80)

        try:
            # Phase 1: Data Loading and Validation
            print("\nPHASE 1: Data Loading and Validation")
            print("-" * 40)
            allRawData = self.dataLoader.loadAllSimulationData()
            if not allRawData:
                raise ValueError("No valid simulation data could be loaded")

            # Phase 2: Steady-State Detection
            print("\nPHASE 2: Steady-State Detection")
            print("-" * 40)
            steadyStateData = self._detectSteadyStateForAllScenarios(allRawData)

            # Phase 3: Performance Analysis
            print("\nPHASE 3: Performance Analysis")
            print("-" * 40)
            summaryStatistics = self.performanceAnalyzer.generateComparativeSummary(steadyStateData)

            # Phase 4: Analytical Modeling
            print("\nPHASE 4: Analytical Modeling")
            print("-" * 40)
            analyticalModels = self._fitAnalyticalModels(summaryStatistics)

            # Phase 5: Machine Learning Insights
            print("\nPHASE 5: Machine Learning Analysis")
            print("-" * 40)
            combinedSteadyStateData = pd.concat(steadyStateData.values(), ignore_index=True)
            mlResults = self.machineLearningPipeline.executeCompletePipeline(combinedSteadyStateData)

            # Phase 6: Comprehensive Visualization
            print("\nPHASE 6: Visualization and Reporting")
            print("-" * 40)
            self.visualizer.generateAllComparativePlots(
                allRawData, steadyStateData, summaryStatistics,
                analyticalModels, mlResults
            )

            print("\n" + "=" * 80)
            print("ANALYSIS COMPLETED SUCCESSFULLY!")
            print("=" * 80)
            print(f"Results saved to: {self.visConfig.outputDirectory}")

        except Exception as error:
            print(f"\n❌ PIPELINE ERROR: {error}")
            import traceback
            traceback.print_exc()
            raise

    def _detectSteadyStateForAllScenarios(self, rawData: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Applies steady-state detection to all loaded datasets."""
        steadyStateData = {}

        for scenarioKey, dataFrame in rawData.items():
            print(f"Analyzing {scenarioKey}:")
            steadyStateStart = self.steadyStateDetector.detectSteadyStateStart(dataFrame)
            steadyStateData[scenarioKey] = dataFrame.iloc[steadyStateStart:].copy()
            print(f"  Using {len(steadyStateData[scenarioKey])} steady-state samples\n")

        return steadyStateData

    def _fitAnalyticalModels(self, summaryData: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Fits analytical models to key performance metrics."""
        analyticalModels = {}

        # Mapeamento correto das métricas para os nomes das colunas no summary
        metric_mapping = {
            self.config.columnAverageNumberInSystem: 'numberInSystem_mean',
            self.config.columnAverageWaitingTime: 'waitingTime_mean'
        }

        if len(summaryData) >= 2:
            for metric, summary_column in metric_mapping.items():
                # Verifica se a coluna existe no summaryData
                if summary_column in summaryData.columns:
                    # Use mean values for each occupancy level
                    occupancyData = summaryData.groupby('occupancy')[summary_column].mean()

                    if len(occupancyData) >= 2:
                        print(f"Fitting model for {metric} -> {summary_column}")
                        analyticalModels[metric] = self.analyticalModeler.fitPolynomialModel(
                            occupancyData.index.values,
                            occupancyData.values
                        )
                    else:
                        analyticalModels[metric] = {'equation': 'Insufficient data points', 'rSquared': 0}
                else:
                    print(f"Warning: Column {summary_column} not found in summary data")
                    print(f"Available columns: {summaryData.columns.tolist()}")
                    analyticalModels[metric] = {'equation': 'Column not found', 'rSquared': 0}
        else:
            print("Insufficient data for analytical modeling")

        return analyticalModels


def main():
    """Main execution function for the analysis pipeline."""
    try:
        pipeline = SimulationAnalysisPipeline()
        pipeline.executeCompleteAnalysis()
        return 0
    except Exception as error:
        print(f"\nFATAL ERROR: Analysis pipeline failed - {error}")
        return 1


if __name__ == "__main__":
    exit(main())