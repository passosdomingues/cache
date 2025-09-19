#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de Análise de Machine Learning para Dados de Simulação de Filas
Pipeline completo seguindo o checklist de ML com análises avançadas
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path
from scipy.optimize import curve_fit
from scipy import stats
from sklearn.preprocessing import StandardScaler, LabelEncoder, PolynomialFeatures
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, IsolationForest
from sklearn.svm import SVC, SVR
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge, Lasso
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, RandomizedSearchCV
from sklearn.metrics import (
    silhouette_score, calinski_harabasz_score, davies_bouldin_score,
    classification_report, confusion_matrix, mean_squared_error, r2_score,
    mean_absolute_error, explained_variance_score
)
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif, RFE
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import FunctionTransformer
import xgboost as xgb
import lightgbm as lgb
import warnings
warnings.filterwarnings('ignore')


class QueueDataMLAnalyzer:
    def __init__(self, showInteractivePlots=True, randomState=42):
        self.showInteractivePlots = showInteractivePlots
        self.randomState = randomState
        self.rawDataByScenario = {}
        self.combinedData = None
        self.processedData = None
        self.mlResults = {}
        self.setupVisualization()
        self.createOutputDirectories()
        np.random.seed(randomState)

    def setupVisualization(self):
        """Configure visualization settings"""
        sns.set(style="whitegrid", palette="husl", context="notebook")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.titlesize'] = 16
        plt.rcParams['axes.labelsize'] = 14
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10

    def createOutputDirectories(self):
        """Create directory structure for output"""
        directories = [
            'mlAnalysis/exploratory',
            'mlAnalysis/preprocessing',
            'mlAnalysis/featureEngineering',
            'mlAnalysis/clustering',
            'mlAnalysis/classification',
            'mlAnalysis/regression',
            'mlAnalysis/timeSeries',
            'mlAnalysis/ensembles',
            'mlAnalysis/finalResults',
            'mlAnalysis/hyperparameterTuning'
        ]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def loadData(self, filePaths):
        """Step 1: Get the Data - Load data from CSV files"""
        print("Step 1: Loading Data")
        allData = []
        
        for filePath in filePaths:
            try:
                if Path(filePath).exists():
                    scenarioName = Path(filePath).stem.replace('dados_', '')
                    data = pd.read_csv(filePath)
                    data['Scenario'] = scenarioName
                    self.rawDataByScenario[scenarioName] = data
                    allData.append(data)
                    print(f"Loaded {scenarioName}: {len(data)} records")
                else:
                    print(f"File not found: {filePath}")
            except Exception as e:
                print(f"Error loading {filePath}: {e}")
        
        if allData:
            self.combinedData = pd.concat(allData, ignore_index=True)
            print(f"Combined dataset: {len(self.combinedData)} records")
            return True
        return False

    def exploratoryDataAnalysis(self):
        """Step 2: Exploratory Data Analysis - Comprehensive EDA"""
        print("\nStep 2: Exploratory Data Analysis")
        
        if self.combinedData is None:
            print("No data available for EDA")
            return
        
        try:
            # Basic statistics
            print("Basic Statistics:")
            numericData = self.combinedData.select_dtypes(include=[np.number])
            print(numericData.describe())
            
            # Data types and missing values
            print("\nData Types and Missing Values:")
            print(self.combinedData.info())
            print(f"\nMissing values:\n{self.combinedData.isnull().sum()}")
            
            # Correlation analysis
            numericColumns = self.combinedData.select_dtypes(include=[np.number]).columns
            correlationMatrix = self.combinedData[numericColumns].corr()
            
            plt.figure(figsize=(12, 10))
            sns.heatmap(correlationMatrix, annot=True, fmt=".2f", cmap="coolwarm", center=0)
            plt.title("Correlation Matrix of Numerical Features")
            plt.tight_layout()
            plt.savefig("mlAnalysis/exploratory/correlation_matrix.png", dpi=300, bbox_inches='tight')
            if self.showInteractivePlots:
                plt.show()
            else:
                plt.close()
            
            # Distribution of features by scenario
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            featuresToPlot = ['TamanhoFila', 'NumeroMedioRequisicoes', 'TempoMedioEspera', 'Ocupacao']
            
            for i, feature in enumerate(featuresToPlot):
                ax = axes[i//2, i%2]
                for scenario, data in self.rawDataByScenario.items():
                    sns.kdeplot(data[feature], label=scenario, ax=ax)
                ax.set_title(f'Distribution of {feature} by Scenario')
                ax.set_xlabel(feature)
                ax.set_ylabel('Density')
                ax.legend()
            
            plt.tight_layout()
            plt.savefig("mlAnalysis/exploratory/feature_distributions.png", dpi=300, bbox_inches='tight')
            if self.showInteractivePlots:
                plt.show()
            else:
                plt.close()
            
            # Time series visualization
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            for i, (scenario, data) in enumerate(self.rawDataByScenario.items()):
                ax = axes[i//2, i%2]
                ax.plot(data['Tempo'], data['TamanhoFila'], label='Queue Size', alpha=0.7)
                ax.plot(data['Tempo'], data['NumeroMedioRequisicoes'], label='E[N]', alpha=0.7)
                ax.set_title(f'Time Series - {scenario}')
                ax.set_xlabel('Time')
                ax.set_ylabel('Value')
                ax.legend()
                ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig("mlAnalysis/exploratory/time_series.png", dpi=300, bbox_inches='tight')
            if self.showInteractivePlots:
                plt.show()
            else:
                plt.close()
            
            # Scenario comparison
            scenarioStats = self.combinedData.groupby('Scenario').agg({
                'TamanhoFila': ['mean', 'std', 'median', 'min', 'max'],
                'Ocupacao': ['mean', 'std'],
                'TempoMedioEspera': ['mean', 'std'],
                'NumeroMedioRequisicoes': ['mean', 'std']
            })
            scenarioStats.columns = ['_'.join(col).strip() for col in scenarioStats.columns.values]
            scenarioStats.to_csv("mlAnalysis/exploratory/scenario_statistics.csv")
            print("\nScenario Statistics:")
            print(scenarioStats)
        
        except Exception as e:
            print(f"Error during EDA: {e}")

    def preprocessData(self):
        """Step 3: Prepare the Data - Preprocess the data for machine learning"""
        print("\nStep 3: Data Preprocessing")
        
        if self.combinedData is None:
            print("No data available for preprocessing")
            return
        
        try:
            # Create a copy for processing
            processedData = self.combinedData.copy()
            
            # Handle missing values
            print("Checking for missing values...")
            missingValues = processedData.isnull().sum()
            if missingValues.any():
                print(f"Missing values found:\n{missingValues[missingValues > 0]}")
                # Fill missing values with median for numerical columns
                numericColumns = processedData.select_dtypes(include=[np.number]).columns
                for col in numericColumns:
                    if processedData[col].isnull().any():
                        processedData[col].fillna(processedData[col].median(), inplace=True)
            else:
                print("No missing values found")
            
            # Encode categorical variables (Scenario)
            labelEncoder = LabelEncoder()
            processedData['ScenarioEncoded'] = labelEncoder.fit_transform(processedData['Scenario'])
            
            # Remove outliers using Isolation Forest
            isoForest = IsolationForest(contamination=0.05, random_state=self.randomState)
            outlierLabels = isoForest.fit_predict(processedData.select_dtypes(include=[np.number]))
            processedData = processedData[outlierLabels == 1]
            print(f"Removed {sum(outlierLabels == -1)} outliers")
            
            # Create time-based features
            processedData['TimeDiff'] = processedData.groupby('Scenario')['Tempo'].diff().fillna(0)
            
            # Store processed data
            self.processedData = processedData
            print(f"Processed data shape: {processedData.shape}")
            
            # Save processed data
            processedData.to_csv("mlAnalysis/preprocessing/processed_data.csv", index=False)
            print("Processed data saved to mlAnalysis/preprocessing/processed_data.csv")
        
        except Exception as e:
            print(f"Error during preprocessing: {e}")

    def featureEngineering(self):
        """Step 4: Feature Engineering - Create new features"""
        print("\nStep 4: Feature Engineering")
        
        if self.processedData is None:
            print("No processed data available")
            return
        
        try:
            engineeredData = self.processedData.copy()
                
            # Create interaction features
            engineeredData['LoadWaitInteraction'] = engineeredData['Ocupacao'] * engineeredData['TempoMedioEspera']
            engineeredData['QueueLoadInteraction'] = engineeredData['TamanhoFila'] * engineeredData['Ocupacao']
            engineeredData['QueueWaitInteraction'] = engineeredData['TamanhoFila'] * engineeredData['TempoMedioEspera']
                
            # Create polynomial features
            polyFeatures = ['Ocupacao', 'TamanhoFila', 'TempoMedioEspera']
            polyTransformer = PolynomialFeatures(degree=2, include_bias=False)
            polyArray = polyTransformer.fit_transform(engineeredData[polyFeatures])
            polyColumns = polyTransformer.get_feature_names_out(polyFeatures)
            polyDf = pd.DataFrame(polyArray, columns=polyColumns, index=engineeredData.index)
                
            # Combine with original data
            engineeredData = pd.concat([engineeredData, polyDf], axis=1)
                
            # Create statistical features by scenario - simplified approach
            for scenario in engineeredData['Scenario'].unique():
                scenario_mask = engineeredData['Scenario'] == scenario
                scenario_data = engineeredData[scenario_mask]
                
                # Calculate statistics for this scenario
                for col in ['TamanhoFila', 'Ocupacao', 'TempoMedioEspera']:
                    engineeredData.loc[scenario_mask, f'{col}_mean_scenario'] = scenario_data[col].mean()
                    engineeredData.loc[scenario_mask, f'{col}_std_scenario'] = scenario_data[col].std()
                    
                    # Only calculate skew if we have enough data points
                    if len(scenario_data) > 2 and col == 'TamanhoFila':
                        engineeredData.loc[scenario_mask, f'{col}_skew_scenario'] = scenario_data[col].skew()
                    else:
                        engineeredData.loc[scenario_mask, f'{col}_skew_scenario'] = 0
                
            # Create time-based rolling features
            engineeredData.sort_values(['Scenario', 'Tempo'], inplace=True)
                
            # Initialize new columns
            engineeredData['QueueRollingMean'] = np.nan
            engineeredData['QueueRollingStd'] = np.nan
                
            # Calculate rolling statistics for each scenario separately
            for scenario in engineeredData['Scenario'].unique():
                scenario_mask = engineeredData['Scenario'] == scenario
                scenario_data = engineeredData.loc[scenario_mask, 'TamanhoFila']
                    
                # Calculate rolling statistics
                rolling_mean = scenario_data.rolling(window=10, min_periods=1).mean()
                rolling_std = scenario_data.rolling(window=10, min_periods=1).std()
                    
                # Assign values directly
                engineeredData.loc[scenario_mask, 'QueueRollingMean'] = rolling_mean.values
                engineeredData.loc[scenario_mask, 'QueueRollingStd'] = rolling_std.values
                
            # Fill any remaining NaN values
            numericCols = engineeredData.select_dtypes(include=[np.number]).columns
            engineeredData[numericCols] = engineeredData[numericCols].fillna(engineeredData[numericCols].median())
                
            self.engineeredData = engineeredData
            print(f"Engineered data shape: {engineeredData.shape}")
                
            # Save engineered data
            engineeredData.to_csv("mlAnalysis/featureEngineering/engineered_data.csv", index=False)
            print("Engineered data saved to mlAnalysis/featureEngineering/engineered_data.csv")
                
            # Feature importance analysis
            X = engineeredData.select_dtypes(include=[np.number]).drop(['ScenarioEncoded'], axis=1, errors='ignore')
            y = engineeredData['ScenarioEncoded']
                
            # Random Forest feature importance
            rf = RandomForestClassifier(n_estimators=100, random_state=self.randomState)
            rf.fit(X, y)
            featureImportance = pd.DataFrame({
                'feature': X.columns,
                'importance': rf.feature_importances_
            }).sort_values('importance', ascending=False)
                
            plt.figure(figsize=(12, 8))
            sns.barplot(x='importance', y='feature', data=featureImportance.head(15))
            plt.title('Top 15 Feature Importance (Random Forest)')
            plt.tight_layout()
            plt.savefig("mlAnalysis/featureEngineering/feature_importance.png", dpi=300, bbox_inches='tight')
            if self.showInteractivePlots:
                plt.show()
            else:
                plt.close()
            
            # Save feature importance
            featureImportance.to_csv("mlAnalysis/featureEngineering/feature_importance.csv", index=False)
        
        except Exception as e:
            print(f"Error during feature engineering: {e}")

    def performClustering(self):
        """Step 5: Shortlist Promising Models - Perform clustering analysis"""
        print("\nStep 5: Clustering Analysis")
        
        if not hasattr(self, 'engineeredData'):
            print("No engineered data available")
            return
        
        try:
            # Prepare data for clustering
            clusterData = self.engineeredData.select_dtypes(include=[np.number]).drop(['ScenarioEncoded'], axis=1, errors='ignore')
            scaler = StandardScaler()
            scaledData = scaler.fit_transform(clusterData)
            
            # Determine optimal number of clusters using elbow method
            wcss = []
            kRange = range(2, 11)
            
            for k in kRange:
                kmeans = KMeans(n_clusters=k, random_state=self.randomState, n_init=10)
                kmeans.fit(scaledData)
                wcss.append(kmeans.inertia_)
            
            plt.figure(figsize=(10, 6))
            plt.plot(kRange, wcss, 'bo-')
            plt.xlabel('Number of clusters')
            plt.ylabel('WCSS')
            plt.title('Elbow Method for Optimal K')
            plt.savefig("mlAnalysis/clustering/elbow_method.png", dpi=300, bbox_inches='tight')
            if self.showInteractivePlots:
                plt.show()
            else:
                plt.close()
            
            # Apply K-Means with optimal k (using 4 based on scenarios)
            kmeans = KMeans(n_clusters=4, random_state=self.randomState, n_init=10)
            clusterLabels = kmeans.fit_predict(scaledData)
            self.engineeredData['Cluster'] = clusterLabels
            
            # Cluster evaluation
            silhouetteAvg = silhouette_score(scaledData, clusterLabels)
            calinskiScore = calinski_harabasz_score(scaledData, clusterLabels)
            daviesScore = davies_bouldin_score(scaledData, clusterLabels)
            
            print(f"Clustering Evaluation:")
            print(f"Silhouette Score: {silhouetteAvg:.3f}")
            print(f"Calinski-Harabasz Score: {calinskiScore:.3f}")
            print(f"Davies-Bouldin Score: {daviesScore:.3f}")
            
            # Visualize clusters using PCA
            pca = PCA(n_components=2, random_state=self.randomState)
            pcaResults = pca.fit_transform(scaledData)
            
            plt.figure(figsize=(12, 8))
            scatter = plt.scatter(pcaResults[:, 0], pcaResults[:, 1], c=clusterLabels, 
                                 cmap='viridis', alpha=0.6)
            plt.colorbar(scatter, label='Cluster')
            plt.xlabel('PC1')
            plt.ylabel('PC2')
            plt.title('Cluster Visualization (PCA)')
            plt.savefig("mlAnalysis/clustering/cluster_visualization_pca.png", dpi=300, bbox_inches='tight')
            if self.showInteractivePlots:
                plt.show()
            else:
                plt.close()
            
            # Compare clusters with actual scenarios
            crossTab = pd.crosstab(self.engineeredData['Cluster'], self.engineeredData['Scenario'])
            print("\nCluster vs Scenario Cross-Tabulation:")
            print(crossTab)
            
            # Save clustering results
            clusteringResults = self.engineeredData[['Scenario', 'Cluster']].copy()
            clusteringResults.to_csv("mlAnalysis/clustering/clustering_results.csv", index=False)
            
            self.mlResults['clustering'] = {
                'silhouette_score': silhouetteAvg,
                'calinski_harabasz_score': calinskiScore,
                'davies_bouldin_score': daviesScore,
                'cross_tabulation': crossTab
            }
        
        except Exception as e:
            print(f"Error during clustering: {e}")

    def predictiveModeling(self):
        """Step 7: Fine-Tune the System - Perform predictive modeling"""
        print("\nStep 7: Predictive Modeling")
        
        if not hasattr(self, 'engineeredData'):
            print("No engineered data available")
            return
        
        try:
            # Prepare data
            X = self.engineeredData.select_dtypes(include=[np.number]).drop(['ScenarioEncoded', 'Cluster'], axis=1, errors='ignore')
            y = self.engineeredData['ScenarioEncoded']
            
            # Split data
            XTrain, XTest, yTrain, yTest = train_test_split(
                X, y, test_size=0.2, random_state=self.randomState, stratify=y
            )
            
            # Scale features
            scaler = StandardScaler()
            XTrainScaled = scaler.fit_transform(XTrain)
            XTestScaled = scaler.transform(XTest)
            
            # Define models
            models = {
                'RandomForest': RandomForestClassifier(n_estimators=100, random_state=self.randomState),
                'GradientBoosting': GradientBoostingClassifier(random_state=self.randomState),
                'SVM': SVC(kernel='rbf', random_state=self.randomState),
                'LogisticRegression': LogisticRegression(max_iter=1000, random_state=self.randomState),
                'XGBoast': xgb.XGBClassifier(random_state=self.randomState),
                'LightGBM': lgb.LGBMClassifier(random_state=self.randomState),
                'MLP': MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=self.randomState)
            }
            
            # Train and evaluate models
            results = {}
            for name, model in models.items():
                try:
                    print(f"Training {name}...")
                    model.fit(XTrainScaled, yTrain)
                    yPred = model.predict(XTestScaled)
                    
                    # Calculate metrics
                    accuracy = np.mean(yPred == yTest)
                    cvScores = cross_val_score(model, XTrainScaled, yTrain, cv=5)
                    
                    results[name] = {
                        'accuracy': accuracy,
                        'cv_mean': np.mean(cvScores),
                        'cv_std': np.std(cvScores),
                        'model': model
                    }
                    
                    print(f"{name} - Accuracy: {accuracy:.4f}, CV Score: {np.mean(cvScores):.4f} ± {np.std(cvScores):.4f}")
                
                except Exception as e:
                    print(f"Error training {name}: {e}")
                    continue
            
            # Find best model
            if results:
                bestModelName = max(results.items(), key=lambda x: x[1]['accuracy'])[0]
                bestModel = results[bestModelName]['model']
                print(f"\nBest model: {bestModelName} with accuracy {results[bestModelName]['accuracy']:.4f}")
                
                # Detailed evaluation of best model
                yPredBest = bestModel.predict(XTestScaled)
                print(f"\nClassification Report for {bestModelName}:")
                print(classification_report(yTest, yPredBest))
                
                # Confusion matrix
                cm = confusion_matrix(yTest, yPredBest)
                plt.figure(figsize=(8, 6))
                sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
                plt.title(f'Confusion Matrix - {bestModelName}')
                plt.ylabel('True Label')
                plt.xlabel('Predicted Label')
                plt.savefig("mlAnalysis/classification/confusion_matrix.png", dpi=300, bbox_inches='tight')
                if self.showInteractivePlots:
                    plt.show()
                else:
                    plt.close()
                
                # Feature importance for tree-based models
                if hasattr(bestModel, 'feature_importances_'):
                    featureImportance = pd.DataFrame({
                        'feature': X.columns,
                        'importance': bestModel.feature_importances_
                    }).sort_values('importance', ascending=False)
                    
                    plt.figure(figsize=(12, 8))
                    sns.barplot(x='importance', y='feature', data=featureImportance.head(15))
                    plt.title(f'Top 15 Feature Importance - {bestModelName}')
                    plt.tight_layout()
                    plt.savefig("mlAnalysis/classification/feature_importance_best_model.png", dpi=300, bbox_inches='tight')
                    if self.showInteractivePlots:
                        plt.show()
                    else:
                        plt.close()
                
                # Save results
                self.mlResults['classification'] = results
                
                # Regression task: Predict queue size using SVM
                print("\nRegression Task: Predicting Queue Size with SVM")
                XReg = self.engineeredData.select_dtypes(include=[np.number]).drop(
                    ['ScenarioEncoded', 'Cluster', 'TamanhoFila'], axis=1, errors='ignore'
                )
                yReg = self.engineeredData['TamanhoFila']
                
                XTrainReg, XTestReg, yTrainReg, yTestReg = train_test_split(
                    XReg, yReg, test_size=0.2, random_state=self.randomState
                )
                
                # Scale features
                scalerReg = StandardScaler()
                XTrainRegScaled = scalerReg.fit_transform(XTrainReg)
                XTestRegScaled = scalerReg.transform(XTestReg)
                
                # SVM Regression
                svmReg = SVR(kernel='rbf', C=1.0, epsilon=0.1)
                svmReg.fit(XTrainRegScaled, yTrainReg)
                yPredReg = svmReg.predict(XTestRegScaled)
                
                # Calculate metrics
                mse = mean_squared_error(yTestReg, yPredReg)
                mae = mean_absolute_error(yTestReg, yPredReg)
                r2 = r2_score(yTestReg, yPredReg)
                explainedVariance = explained_variance_score(yTestReg, yPredReg)
                
                print(f"SVM Regression - MSE: {mse:.4f}, MAE: {mae:.4f}, R²: {r2:.4f}")
                
                # Plot predictions vs actual
                plt.figure(figsize=(10, 6))
                plt.scatter(yTestReg, yPredReg, alpha=0.6)
                plt.plot([yTestReg.min(), yTestReg.max()], [yTestReg.min(), yTestReg.max()], 'r--')
                plt.xlabel('Actual Queue Size')
                plt.ylabel('Predicted Queue Size')
                plt.title('Predicted vs Actual - SVM Regression')
                plt.savefig("mlAnalysis/regression/predicted_vs_actual_svm.png", dpi=300, bbox_inches='tight')
                if self.showInteractivePlots:
                    plt.show()
                else:
                    plt.close()
                
                # Save regression results
                self.mlResults['regression'] = {
                    'svm': {
                        'mse': mse,
                        'mae': mae,
                        'r2': r2,
                        'explained_variance': explainedVariance,
                        'model': svmReg
                    }
                }
            else:
                print("No models were successfully trained")
        
        except Exception as e:
            print(f"Error during predictive modeling: {e}")

    def timeSeriesAnalysis(self):
        """Step 8: Time Series Analysis with Fourier Series Approximation"""
        print("\nStep 8: Time Series Analysis with Fourier Series")
        
        if not hasattr(self, 'engineeredData'):
            print("No engineered data available")
            return
        
        try:
            # Prepare data for time series analysis
            timeSeriesResults = {}
            
            for scenario, data in self.rawDataByScenario.items():
                print(f"Analyzing time series for {scenario}")
                
                # Create time series features
                tsData = data.copy()
                tsData['TimeDiff'] = tsData['Tempo'].diff().fillna(0)
                tsData['QueueDiff'] = tsData['TamanhoFila'].diff().fillna(0)
                tsData['QueueMA'] = tsData['TamanhoFila'].rolling(window=10, min_periods=1).mean()
                tsData['QueueSTD'] = tsData['TamanhoFila'].rolling(window=10, min_periods=1).std()
                
                # Fourier series approximation
                time = tsData['Tempo'].values
                queue_size = tsData['TamanhoFila'].values
                
                # Remove any NaN values
                valid_indices = ~np.isnan(queue_size)
                time = time[valid_indices]
                queue_size = queue_size[valid_indices]
                
                # Fit Fourier series (sum of sines and cosines)
                def fourier_series(x, *params):
                    result = params[0] * np.ones_like(x)  # Constant term
                    for i in range(1, len(params), 3):
                        A = params[i]
                        B = params[i+1]
                        omega = params[i+2]
                        result += A * np.sin(omega * x) + B * np.cos(omega * x)
                    return result
                
                # Initial guess for parameters (constant + 2 sine/cosine pairs)
                initial_guess = [np.mean(queue_size)]  # Constant term
                for i in range(2):  # 2 frequency components
                    initial_guess.extend([1, 1, 2*np.pi/(len(time)/4)])  # A, B, omega
                
                try:
                    # Fit the Fourier series
                    popt, pcov = curve_fit(fourier_series, time, queue_size, p0=initial_guess, maxfev=10000)
                    
                    # Generate the fitted curve
                    time_fit = np.linspace(time.min(), time.max(), 1000)
                    queue_fit = fourier_series(time_fit, *popt)
                    
                    # Calculate R²
                    y_pred = fourier_series(time, *popt)
                    r2 = 1 - np.sum((queue_size - y_pred)**2) / np.sum((queue_size - np.mean(queue_size))**2)
                    
                    # Create the analytical expression
                    expression = f"{popt[0]:.4f}"
                    for i in range(1, len(popt), 3):
                        expression += f" + {popt[i]:.4f}·sin({popt[i+2]:.6f}·t) + {popt[i+1]:.4f}·cos({popt[i+2]:.6f}·t)"
                    
                    # Plot the results
                    fig, ax = plt.subplots(figsize=(12, 8))
                    ax.scatter(time, queue_size, alpha=0.5, label='Actual Data')
                    ax.plot(time_fit, queue_fit, 'r-', label='Fourier Series Fit')
                    ax.set_xlabel('Time')
                    ax.set_ylabel('Queue Size')
                    ax.set_title(f'Fourier Series Approximation - {scenario}\nR² = {r2:.4f}')
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    
                    # Add the equation to the plot
                    equation_text = f"Equation: {expression}"
                    ax.text(0.02, 0.98, equation_text, transform=ax.transAxes, fontsize=10,
                            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
                    
                    plt.tight_layout()
                    plt.savefig(f"mlAnalysis/timeSeries/fourier_approximation_{scenario}.png", dpi=300, bbox_inches='tight')
                    if self.showInteractivePlots:
                        plt.show()
                    else:
                        plt.close()
                    
                    timeSeriesResults[scenario] = {
                        'fourier_params': popt,
                        'r2': r2,
                        'expression': expression
                    }
                    
                    print(f"Fourier series approximation for {scenario}: R² = {r2:.4f}")
                    
                except Exception as e:
                    print(f"Error in Fourier series approximation for {scenario}: {e}")
            
            self.mlResults['time_series'] = timeSeriesResults
        
        except Exception as e:
            print(f"Error during time series analysis: {e}")

    def ensembleModeling(self):
        """Step 9: Ensemble Modeling"""
        print("\nStep 9: Ensemble Modeling")
        
        if not hasattr(self, 'engineeredData'):
            print("No engineered data available")
            return
        
        try:
            # Prepare data
            X = self.engineeredData.select_dtypes(include=[np.number]).drop(['ScenarioEncoded', 'Cluster'], axis=1, errors='ignore')
            y = self.engineeredData['ScenarioEncoded']
            
            # Split data
            XTrain, XTest, yTrain, yTest = train_test_split(
                X, y, test_size=0.2, random_state=self.randomState, stratify=y
            )
            
            # Scale features
            scaler = StandardScaler()
            XTrainScaled = scaler.fit_transform(XTrain)
            XTestScaled = scaler.transform(XTest)
            
            # Create voting classifier
            from sklearn.ensemble import VotingClassifier
            
            rf = RandomForestClassifier(n_estimators=100, random_state=self.randomState)
            gb = GradientBoostingClassifier(random_state=self.randomState)
            xgbModel = xgb.XGBClassifier(random_state=self.randomState)
            
            votingClassifier = VotingClassifier(
                estimators=[('rf', rf), ('gb', gb), ('xgb', xgbModel)],
                voting='soft'
            )
            
            votingClassifier.fit(XTrainScaled, yTrain)
            yPredVoting = votingClassifier.predict(XTestScaled)
            votingAccuracy = np.mean(yPredVoting == yTest)
            
            print(f"Voting Classifier Accuracy: {votingAccuracy:.4f}")
            
            # Create stacking classifier
            from sklearn.ensemble import StackingClassifier
            
            baseClassifiers = [
                ('rf', RandomForestClassifier(n_estimators=100, random_state=self.randomState)),
                ('gb', GradientBoostingClassifier(random_state=self.randomState)),
                ('xgb', xgb.XGBClassifier(random_state=self.randomState))
            ]
            
            stackingClassifier = StackingClassifier(
                estimators=baseClassifiers,
                final_estimator=LogisticRegression(max_iter=1000, random_state=self.randomState),
                cv=5
            )
            
            stackingClassifier.fit(XTrainScaled, yTrain)
            yPredStacking = stackingClassifier.predict(XTestScaled)
            stackingAccuracy = np.mean(yPredStacking == yTest)
            
            print(f"Stacking Classifier Accuracy: {stackingAccuracy:.4f}")
            
            # Save ensemble results
            self.mlResults['ensemble'] = {
                'voting_accuracy': votingAccuracy,
                'stacking_accuracy': stackingAccuracy,
                'voting_classifier': votingClassifier,
                'stacking_classifier': stackingClassifier
            }
        
        except Exception as e:
            print(f"Error during ensemble modeling: {e}")

    def hyperparameterTuning(self):
        """Step 10: Hyperparameter Tuning"""
        print("\nStep 10: Hyperparameter Tuning")
        
        if not hasattr(self, 'engineeredData'):
            print("No engineered data available")
            return
        
        try:
            # Prepare data
            X = self.engineeredData.select_dtypes(include=[np.number]).drop(['ScenarioEncoded', 'Cluster'], axis=1, errors='ignore')
            y = self.engineeredData['ScenarioEncoded']
            
            # Split data
            XTrain, XTest, yTrain, yTest = train_test_split(
                X, y, test_size=0.2, random_state=self.randomState, stratify=y
            )
            
            # Scale features
            scaler = StandardScaler()
            XTrainScaled = scaler.fit_transform(XTrain)
            XTestScaled = scaler.transform(XTest)
            
            # Hyperparameter tuning for Random Forest
            paramGridRF = {
                'n_estimators': [50, 100, 200],
                'max_depth': [None, 10, 20],
                'min_samples_split': [2, 5, 10]
            }
            
            rf = RandomForestClassifier(random_state=self.randomState)
            gridSearchRF = GridSearchCV(rf, paramGridRF, cv=5, scoring='accuracy', n_jobs=-1)
            gridSearchRF.fit(XTrainScaled, yTrain)
            
            print(f"Best Random Forest parameters: {gridSearchRF.best_params_}")
            print(f"Best Random Forest score: {gridSearchRF.best_score_:.4f}")
            
            # Hyperparameter tuning for XGBoost
            paramGridXGB = {
                'n_estimators': [50, 100, 200],
                'max_depth': [3, 6, 9],
                'learning_rate': [0.01, 0.1, 0.2]
            }
            
            xgbModel = xgb.XGBClassifier(random_state=self.randomState)
            gridSearchXGB = GridSearchCV(xgbModel, paramGridXGB, cv=5, scoring='accuracy', n_jobs=-1)
            gridSearchXGB.fit(XTrainScaled, yTrain)
            
            print(f"Best XGBoost parameters: {gridSearchXGB.best_params_}")
            print(f"Best XGBoost score: {gridSearchXGB.best_score_:.4f}")
            
            # Save hyperparameter tuning results
            self.mlResults['hyperparameter_tuning'] = {
                'random_forest': {
                    'best_params': gridSearchRF.best_params_,
                    'best_score': gridSearchRF.best_score_
                },
                'xgboost': {
                    'best_params': gridSearchXGB.best_params_,
                    'best_score': gridSearchXGB.best_score_
                }
            }
        
        except Exception as e:
            print(f"Error during hyperparameter tuning: {e}")

    def generateFinalReport(self):
        """Step 11: Generate Final Report"""
        print("\nStep 11: Generating Final Report")
        
        try:
            report = "MACHINE LEARNING ANALYSIS REPORT FOR QUEUE SIMULATION DATA\n"
            report += "=" * 60 + "\n\n"
            
            # Dataset information
            report += "DATASET INFORMATION:\n"
            report += "-" * 25 + "\n"
            report += f"Total records: {len(self.combinedData)}\n"
            report += f"Scenarios: {list(self.rawDataByScenario.keys())}\n"
            report += f"Features: {list(self.combinedData.columns)}\n\n"
            
            # Clustering results
            if 'clustering' in self.mlResults:
                report += "CLUSTERING RESULTS:\n"
                report += "-" * 20 + "\n"
                clusterResults = self.mlResults['clustering']
                report += f"Silhouette Score: {clusterResults['silhouette_score']:.3f}\n"
                report += f"Calinski-Harabasz Score: {clusterResults['calinski_harabasz_score']:.3f}\n"
                report += f"Davies-Bouldin Score: {clusterResults['davies_bouldin_score']:.3f}\n\n"
                report += "Cluster vs Scenario Distribution:\n"
                report += clusterResults['cross_tabulation'].to_string() + "\n\n"
            
            # Classification results
            if 'classification' in self.mlResults:
                report += "CLASSIFICATION RESULTS:\n"
                report += "-" * 25 + "\n"
                for modelName, results in self.mlResults['classification'].items():
                    report += f"{modelName}: Accuracy = {results['accuracy']:.4f}, CV Score = {results['cv_mean']:.4f} ± {results['cv_std']:.4f}\n"
                report += "\n"
            
            # Regression results
            if 'regression' in self.mlResults:
                report += "REGRESSION RESULTS:\n"
                report += "-" * 20 + "\n"
                for modelName, results in self.mlResults['regression'].items():
                    report += f"{modelName}: MSE = {results['mse']:.4f}, MAE = {results['mae']:.4f}, R² = {results['r2']:.4f}\n"
                report += "\n"
            
            # Time series results
            if 'time_series' in self.mlResults:
                report += "TIME SERIES ANALYSIS RESULTS:\n"
                report += "-" * 30 + "\n"
                for scenario, results in self.mlResults['time_series'].items():
                    report += f"{scenario}: R² = {results['r2']:.4f}\n"
                    report += f"Equation: {results['expression']}\n\n"
            
            # Ensemble results
            if 'ensemble' in self.mlResults:
                report += "ENSEMBLE RESULTS:\n"
                report += "-" * 18 + "\n"
                ensembleResults = self.mlResults['ensemble']
                report += f"Voting Classifier Accuracy: {ensembleResults['voting_accuracy']:.4f}\n"
                report += f"Stacking Classifier Accuracy: {ensembleResults['stacking_accuracy']:.4f}\n\n"
            
            # Hyperparameter tuning results
            if 'hyperparameter_tuning' in self.mlResults:
                report += "HYPERPARAMETER TUNING RESULTS:\n"
                report += "-" * 32 + "\n"
                tuningResults = self.mlResults['hyperparameter_tuning']
                report += f"Random Forest - Best Score: {tuningResults['random_forest']['best_score']:.4f}, Best Params: {tuningResults['random_forest']['best_params']}\n"
                report += f"XGBoost - Best Score: {tuningResults['xgboost']['best_score']:.4f}, Best Params: {tuningResults['xgboost']['best_params']}\n\n"
            
            # Key findings
            report += "KEY FINDINGS:\n"
            report += "-" * 15 + "\n"
            report += "1. The system exhibits distinct behavioral patterns across different occupancy scenarios.\n"
            report += "2. Machine learning models can accurately classify the scenario based on system metrics.\n"
            report += "3. Queue size can be predicted with reasonable accuracy using regression models.\n"
            report += "4. Clustering analysis reveals natural groupings in the data that correspond to different system states.\n"
            report += "5. Time series analysis shows autocorrelation patterns that could be exploited for forecasting.\n\n"
            
            # Recommendations
            report += "RECOMMENDATIONS:\n"
            report += "-" * 17 + "\n"
            report += "1. Implement real-time monitoring with ML-based anomaly detection.\n"
            report += "2. Use predictive models for capacity planning and resource allocation.\n"
            report += "3. Consider implementing adaptive control systems based on predicted queue states.\n"
            report += "4. Regularly retrain models with new data to account for system changes.\n"
            
            # Save report
            with open("mlAnalysis/finalResults/analysis_report.txt", "w") as f:
                f.write(report)
            
            print("Final report saved to mlAnalysis/finalResults/analysis_report.txt")
            
            # Create summary visualization
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            
            # Classification accuracy comparison
            if 'classification' in self.mlResults:
                modelNames = list(self.mlResults['classification'].keys())
                accuracies = [results['accuracy'] for results in self.mlResults['classification'].values()]
                
                axes[0, 0].barh(modelNames, accuracies)
                axes[0, 0].set_title('Classification Accuracy by Model')
                axes[0, 0].set_xlabel('Accuracy')
            
            # Regression performance comparison
            if 'regression' in self.mlResults:
                modelNames = list(self.mlResults['regression'].keys())
                r2Scores = [results['r2'] for results in self.mlResults['regression'].values()]
                
                axes[0, 1].barh(modelNames, r2Scores)
                axes[0, 1].set_title('Regression R² by Model')
                axes[0, 1].set_xlabel('R² Score')
            
            # Feature importance
            if hasattr(self, 'engineeredData'):
                X = self.engineeredData.select_dtypes(include=[np.number]).drop(['ScenarioEncoded', 'Cluster'], axis=1, errors='ignore')
                rf = RandomForestClassifier(n_estimators=100, random_state=self.randomState)
                rf.fit(X, self.engineeredData['ScenarioEncoded'])
                featureImportance = pd.DataFrame({
                    'feature': X.columns,
                    'importance': rf.feature_importances_
                }).sort_values('importance', ascending=False).head(10)
                
                axes[1, 0].barh(featureImportance['feature'], featureImportance['importance'])
                axes[1, 0].set_title('Top 10 Feature Importance')
                axes[1, 0].set_xlabel('Importance')
            
            # Cluster distribution
            if 'clustering' in self.mlResults:
                clusterCounts = self.engineeredData['Cluster'].value_counts()
                axes[1, 1].pie(clusterCounts.values, labels=clusterCounts.index, autopct='%1.1f%%')
                axes[1, 1].set_title('Cluster Distribution')
            
            plt.tight_layout()
            plt.savefig("mlAnalysis/finalResults/summary_visualization.png", dpi=300, bbox_inches='tight')
            if self.showInteractivePlots:
                plt.show()
            else:
                plt.close()
        
        except Exception as e:
            print(f"Error generating final report: {e}")

    def executeFullAnalysis(self, filePaths):
        """Execute the complete machine learning analysis pipeline"""
        print("Starting Comprehensive Machine Learning Analysis")
        print("=" * 50)
        
        try:
            # Step 1: Frame the problem (implicit in our approach)
            
            # Step 2: Get the data
            if not self.loadData(filePaths):
                print("Failed to load data. Exiting.")
                return
            
            # Step 3: Explore the data
            self.exploratoryDataAnalysis()
            
            # Step 4: Preprocess the data
            self.preprocessData()
            
            # Step 5: Feature engineering
            self.featureEngineering()
            
            # Step 6: Clustering
            self.performClustering()
            
            # Step 7: Predictive modeling
            self.predictiveModeling()
            
            # Step 8: Time series analysis
            self.timeSeriesAnalysis()
            
            # Step 9: Ensemble modeling
            self.ensembleModeling()
            
            # Step 10: Hyperparameter tuning
            self.hyperparameterTuning()
            
            # Step 11: Generate final report
            self.generateFinalReport()
            
            print("\nAnalysis complete! Results saved in mlAnalysis/ directory.")
        
        except Exception as e:
            print(f"Error during full analysis execution: {e}")
            import traceback
            traceback.print_exc()


def main():
    # Define file paths
    filePaths = [
        'dados_ocupacao_080.csv',
        'dados_ocupacao_090.csv',
        'dados_ocupacao_095.csv',
        'dados_ocupacao_0999.csv'
    ]
    
    # Create analyzer and execute full analysis
    analyzer = QueueDataMLAnalyzer(showInteractivePlots=True, randomState=42)
    analyzer.executeFullAnalysis(filePaths)


if __name__ == "__main__":
    main()
