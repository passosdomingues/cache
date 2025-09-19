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
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, IsolationForest, VotingClassifier, StackingClassifier
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
import traceback
from typing import List

warnings.filterwarnings('ignore')


class QueueDataMLAnalyzer:
    def __init__(self, showInteractivePlots: bool = True, randomState: int = 42):
        self.showInteractivePlots = showInteractivePlots
        self.randomState = randomState
        self.rawDataByScenario = {}
        self.combinedData = None
        self.processedData = None
        self.engineeredData = None
        self.featureImportance = None
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
            'mlAnalysis/exploratory', 'mlAnalysis/preprocessing', 'mlAnalysis/featureEngineering',
            'mlAnalysis/clustering', 'mlAnalysis/classification', 'mlAnalysis/regression',
            'mlAnalysis/timeSeries', 'mlAnalysis/ensembles', 'mlAnalysis/finalResults',
            'mlAnalysis/hyperparameterTuning'
        ]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def loadData(self, filePaths: List[str]) -> bool:
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
            print("Basic Statistics:")
            print(self.combinedData.select_dtypes(include=[np.number]).describe())
            
            print("\nData Types and Missing Values:")
            self.combinedData.info()
            print(f"\nMissing values:\n{self.combinedData.isnull().sum()}")
            
            numericColumns = self.combinedData.select_dtypes(include=[np.number]).columns
            correlationMatrix = self.combinedData[numericColumns].corr()
            
            plt.figure(figsize=(12, 10))
            sns.heatmap(correlationMatrix, annot=True, fmt=".2f", cmap="coolwarm", center=0)
            plt.title("Correlation Matrix of Numerical Features")
            plt.tight_layout()
            plt.savefig("mlAnalysis/exploratory/correlation_matrix.png", dpi=300, bbox_inches='tight')
            plt.show() if self.showInteractivePlots else plt.close()
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            featuresToPlot = ['TamanhoFila', 'NumeroMedioRequisicoes', 'TempoMedioEspera', 'Ocupacao']
            for i, feature in enumerate(featuresToPlot):
                ax = axes[i//2, i%2]
                for scenario, data in self.rawDataByScenario.items():
                    sns.kdeplot(data[feature], label=scenario, ax=ax, fill=True)
                ax.set_title(f'Distribution of {feature} by Scenario')
                ax.legend()
            
            plt.tight_layout()
            plt.savefig("mlAnalysis/exploratory/feature_distributions.png", dpi=300, bbox_inches='tight')
            plt.show() if self.showInteractivePlots else plt.close()
            
        except Exception as e:
            print(f"Error during EDA: {e}")

    def preprocessData(self):
        """Step 3: Prepare the Data - Preprocess the data for machine learning"""
        print("\nStep 3: Data Preprocessing")
        if self.combinedData is None:
            print("No data available for preprocessing")
            return
        
        try:
            processedData = self.combinedData.copy()
            
            if processedData.isnull().sum().any():
                numericColumns = processedData.select_dtypes(include=[np.number]).columns
                for col in numericColumns:
                    if processedData[col].isnull().any():
                        processedData[col].fillna(processedData[col].median(), inplace=True)
            
            labelEncoder = LabelEncoder()
            processedData['ScenarioEncoded'] = labelEncoder.fit_transform(processedData['Scenario'])
            
            isoForest = IsolationForest(contamination=0.05, random_state=self.randomState)
            outlierLabels = isoForest.fit_predict(processedData.select_dtypes(include=[np.number]))
            numOutliers = sum(outlierLabels == -1)
            processedData = processedData[outlierLabels == 1].reset_index(drop=True)
            print(f"Removed {numOutliers} outliers")
            
            self.processedData = processedData
            print(f"Processed data shape: {processedData.shape}")
            processedData.to_csv("mlAnalysis/preprocessing/processed_data.csv", index=False)
        
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
                
            engineeredData['LoadWaitInteraction'] = engineeredData['Ocupacao'] * engineeredData['TempoMedioEspera']
            engineeredData['QueueLoadInteraction'] = engineeredData['TamanhoFila'] * engineeredData['Ocupacao']
            
            polyFeatures = ['Ocupacao', 'TamanhoFila', 'TempoMedioEspera']
            polyTransformer = PolynomialFeatures(degree=2, include_bias=False)
            polyArray = polyTransformer.fit_transform(engineeredData[polyFeatures])
            polyColumns = polyTransformer.get_feature_names_out(polyFeatures)
            polyDf = pd.DataFrame(polyArray, columns=polyColumns, index=engineeredData.index)
            
            # [FIX] Drop original columns from polyDf to avoid duplicate column names.
            # This was the source of the original error, as duplicate columns cause
            # slicing (e.g., df['col']) to return a DataFrame instead of a Series.
            polyDf.drop(columns=polyFeatures, inplace=True, errors='ignore')
                
            engineeredData = pd.concat([engineeredData, polyDf], axis=1)
                
            statFeatures = ['TamanhoFila', 'Ocupacao', 'TempoMedioEspera']
            grouped = engineeredData.groupby('Scenario')
            for col in statFeatures:
                engineeredData[f'{col}_mean_scenario'] = grouped[col].transform('mean')
                engineeredData[f'{col}_std_scenario'] = grouped[col].transform('std')
                engineeredData[f'{col}_skew_scenario'] = grouped[col].transform(lambda x: x.skew() if len(x) > 2 else 0)
                
            engineeredData.sort_values(['Scenario', 'Tempo'], inplace=True)
            grouped = engineeredData.groupby('Scenario')['TamanhoFila']
            engineeredData['QueueRollingMean'] = grouped.transform(lambda x: x.rolling(window=10, min_periods=1).mean())
            engineeredData['QueueRollingStd'] = grouped.transform(lambda x: x.rolling(window=10, min_periods=1).std())
                
            engineeredData.fillna(engineeredData.median(numeric_only=True), inplace=True)
                
            self.engineeredData = engineeredData
            print(f"Engineered data shape: {engineeredData.shape}")
            engineeredData.to_csv("mlAnalysis/featureEngineering/engineered_data.csv", index=False)
                
            X = engineeredData.select_dtypes(include=[np.number]).drop(['ScenarioEncoded'], axis=1, errors='ignore')
            y = engineeredData['ScenarioEncoded']
                
            rf = RandomForestClassifier(n_estimators=100, random_state=self.randomState)
            rf.fit(X, y)
            self.featureImportance = pd.DataFrame({
                'feature': X.columns,
                'importance': rf.feature_importances_
            }).sort_values('importance', ascending=False)
                
            plt.figure(figsize=(12, 10))
            sns.barplot(x='importance', y='feature', data=self.featureImportance.head(20))
            plt.title('Top 20 Feature Importance (Random Forest)')
            plt.tight_layout()
            plt.savefig("mlAnalysis/featureEngineering/feature_importance.png", dpi=300, bbox_inches='tight')
            plt.show() if self.showInteractivePlots else plt.close()
            
        except Exception as e:
            print(f"Error during feature engineering: {e}")
            traceback.print_exc()

    def performClustering(self):
        """Step 5: Shortlist Promising Models - Perform clustering analysis"""
        print("\nStep 5: Clustering Analysis")
        if self.engineeredData is None:
            print("No engineered data available")
            return
        
        try:
            clusterData = self.engineeredData.select_dtypes(include=[np.number]).drop(['ScenarioEncoded'], axis=1, errors='ignore')
            scaler = StandardScaler()
            scaledData = scaler.fit_transform(clusterData)
            
            wcss = [KMeans(n_clusters=k, random_state=self.randomState, n_init=10).fit(scaledData).inertia_ for k in range(2, 11)]
            
            plt.figure(figsize=(10, 6))
            plt.plot(range(2, 11), wcss, 'bo-')
            plt.xlabel('Number of clusters (K)')
            plt.ylabel('WCSS (Inertia)')
            plt.title('Elbow Method for Optimal K')
            plt.savefig("mlAnalysis/clustering/elbow_method.png", dpi=300, bbox_inches='tight')
            plt.show() if self.showInteractivePlots else plt.close()
            
            # Assuming 4 clusters based on the number of scenarios
            optimal_k = 4
            kmeans = KMeans(n_clusters=optimal_k, random_state=self.randomState, n_init=10)
            self.engineeredData['Cluster'] = kmeans.fit_predict(scaledData)
            
            silhouetteAvg = silhouette_score(scaledData, self.engineeredData['Cluster'])
            print(f"Silhouette Score (K={optimal_k}): {silhouetteAvg:.3f}")
            
            pca = PCA(n_components=2, random_state=self.randomState)
            pcaResults = pca.fit_transform(scaledData)
            
            plt.figure(figsize=(12, 8))
            scatter = plt.scatter(pcaResults[:, 0], pcaResults[:, 1], c=self.engineeredData['Cluster'], cmap='viridis', alpha=0.7)
            plt.colorbar(scatter, label='Cluster')
            plt.xlabel('Principal Component 1')
            plt.ylabel('Principal Component 2')
            plt.title('Cluster Visualization (PCA)')
            plt.savefig("mlAnalysis/clustering/cluster_visualization_pca.png", dpi=300, bbox_inches='tight')
            plt.show() if self.showInteractivePlots else plt.close()
            
            crossTab = pd.crosstab(self.engineeredData['Cluster'], self.engineeredData['Scenario'])
            print("\nCluster vs Scenario Cross-Tabulation:")
            print(crossTab)
            
            self.mlResults['clustering'] = {'silhouette_score': silhouetteAvg, 'cross_tabulation': crossTab}
        
        except Exception as e:
            print(f"Error during clustering: {e}")

    def predictiveModeling(self):
        """Step 7: Fine-Tune the System - Perform predictive modeling"""
        print("\nStep 7: Predictive Modeling")
        if self.engineeredData is None:
            print("No engineered data available")
            return
        
        try:
            X = self.engineeredData.select_dtypes(include=[np.number]).drop(['ScenarioEncoded', 'Cluster'], axis=1, errors='ignore')
            y = self.engineeredData['ScenarioEncoded']
            
            XTrain, XTest, yTrain, yTest = train_test_split(X, y, test_size=0.2, random_state=self.randomState, stratify=y)
            
            pipeline = Pipeline([('scaler', StandardScaler()), ('classifier', RandomForestClassifier())])
            
            models = {
                'RandomForest': RandomForestClassifier(random_state=self.randomState),
                'GradientBoosting': GradientBoostingClassifier(random_state=self.randomState),
                'XGBoost': xgb.XGBClassifier(random_state=self.randomState, use_label_encoder=False, eval_metric='mlogloss'),
                'LightGBM': lgb.LGBMClassifier(random_state=self.randomState),
                'MLP': MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=self.randomState)
            }
            
            results = {}
            for name, model in models.items():
                print(f"Training {name}...")
                pipeline.set_params(classifier=model)
                pipeline.fit(XTrain, yTrain)
                yPred = pipeline.predict(XTest)
                accuracy = np.mean(yPred == yTest)
                results[name] = {'accuracy': accuracy, 'model': pipeline.named_steps['classifier']}
                print(f"{name} - Accuracy: {accuracy:.4f}")
            
            bestModelName = max(results, key=lambda name: results[name]['accuracy'])
            print(f"\nBest model: {bestModelName} with accuracy {results[bestModelName]['accuracy']:.4f}")
            
            pipeline.set_params(classifier=results[bestModelName]['model'])
            yPredBest = pipeline.predict(XTest)
            print(f"\nClassification Report for {bestModelName}:\n{classification_report(yTest, yPredBest)}")
            
            cm = confusion_matrix(yTest, yPredBest)
            plt.figure(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
            plt.title(f'Confusion Matrix - {bestModelName}')
            plt.savefig("mlAnalysis/classification/confusion_matrix.png", dpi=300, bbox_inches='tight')
            plt.show() if self.showInteractivePlots else plt.close()
            
            self.mlResults['classification'] = results
        
        except Exception as e:
            print(f"Error during predictive modeling: {e}")

    def timeSeriesAnalysis(self, n_fourier_terms: int = 3):
        """Step 8: Time Series Analysis with Fourier Series Approximation"""
        print(f"\nStep 8: Time Series Analysis with {n_fourier_terms} Fourier Terms")
        if not self.rawDataByScenario:
            print("No raw data available for Time Series analysis")
            return
        
        def fourier_series(x, *params):
            num_terms = (len(params) - 1) // 3
            result = params[0]  # a0 (constant term)
            for i in range(num_terms):
                offset = 1 + i * 3
                A, B, omega = params[offset], params[offset + 1], params[offset + 2]
                result += A * np.sin(omega * x) + B * np.cos(omega * x)
            return result
            
        timeSeriesResults = {}
        for scenario, data in self.rawDataByScenario.items():
            print(f"Analyzing time series for {scenario}...")
            time, queue_size = data['Tempo'].values, data['TamanhoFila'].values
            
            try:
                initial_guess = [np.mean(queue_size)]
                time_range = time.max() - time.min()
                for i in range(1, n_fourier_terms + 1):
                    initial_guess.extend([1, 1, 2 * np.pi * i / time_range if time_range > 0 else 1])
                
                popt, _ = curve_fit(fourier_series, time, queue_size, p0=initial_guess, maxfev=10000)
                
                y_pred = fourier_series(time, *popt)
                r2 = r2_score(queue_size, y_pred)
                
                expression = f"{popt[0]:.4f}"
                for i in range(n_fourier_terms):
                    offset = 1 + i * 3
                    expression += f" + ({popt[offset]:.4f})*sin({popt[offset+2]:.6f}*t) + ({popt[offset+1]:.4f})*cos({popt[offset+2]:.6f}*t)"

                plt.figure(figsize=(14, 8))
                plt.scatter(time, queue_size, alpha=0.3, label='Actual Data', s=10)
                plt.plot(time, y_pred, 'r-', label=f'Fourier Fit (R²={r2:.4f})', linewidth=2)
                plt.title(f'Fourier Series Approximation - {scenario}')
                plt.xlabel('Time'), plt.ylabel('Queue Size'), plt.legend()
                plt.figtext(0.5, 0.01, expression, ha="center", fontsize=9, bbox={"facecolor":"orange", "alpha":0.5, "pad":5})
                plt.tight_layout(rect=[0, 0.05, 1, 1])
                plt.savefig(f"mlAnalysis/timeSeries/fourier_approximation_{scenario}.png", dpi=300)
                plt.show() if self.showInteractivePlots else plt.close()
                
                timeSeriesResults[scenario] = {'r2': r2, 'expression': expression}
            except Exception as e:
                print(f"Could not fit Fourier series for {scenario}: {e}")
        
        self.mlResults['time_series'] = timeSeriesResults

    def generateFinalReport(self):
        """Step 11: Generate Final Report"""
        print("\nStep 11: Generating Final Report")
        try:
            report_path = "mlAnalysis/finalResults/analysis_report.txt"
            with open(report_path, "w") as f:
                f.write("MACHINE LEARNING ANALYSIS REPORT\n" + "="*60 + "\n\n")
                
                if 'clustering' in self.mlResults:
                    f.write("CLUSTERING RESULTS:\n" + "-"*20 + "\n")
                    f.write(f"Silhouette Score: {self.mlResults['clustering']['silhouette_score']:.3f}\n\n")
                    f.write("Cluster vs Scenario Distribution:\n")
                    f.write(self.mlResults['clustering']['cross_tabulation'].to_string() + "\n\n")
                
                if 'classification' in self.mlResults:
                    f.write("CLASSIFICATION RESULTS:\n" + "-"*25 + "\n")
                    for name, res in self.mlResults['classification'].items():
                        f.write(f"{name}: Accuracy = {res['accuracy']:.4f}\n")
                    f.write("\n")

                if 'time_series' in self.mlResults:
                    f.write("TIME SERIES ANALYSIS (R² values):\n" + "-"*30 + "\n")
                    for scenario, res in self.mlResults['time_series'].items():
                        f.write(f"{scenario}: R² = {res['r2']:.4f}\n")
                    f.write("\n")
            
            print(f"Final report saved to {report_path}")
            
            fig, axes = plt.subplots(2, 2, figsize=(16, 14))
            
            if 'classification' in self.mlResults:
                accuracies = {name: res['accuracy'] for name, res in self.mlResults['classification'].items()}
                sns.barplot(x=list(accuracies.keys()), y=list(accuracies.values()), ax=axes[0, 0], palette='viridis')
                axes[0, 0].set_title('Classification Accuracy by Model')
                axes[0, 0].set_ylabel('Accuracy')
                axes[0, 0].tick_params(axis='x', rotation=45)

            if self.featureImportance is not None:
                sns.barplot(x='importance', y='feature', data=self.featureImportance.head(10), ax=axes[1, 0], palette='rocket')
                axes[1, 0].set_title('Top 10 Feature Importance')

            if 'clustering' in self.mlResults and 'Cluster' in self.engineeredData.columns:
                cluster_counts = self.engineeredData['Cluster'].value_counts()
                axes[1, 1].pie(cluster_counts.values, labels=cluster_counts.index, autopct='%1.1f%%', startangle=90)
                axes[1, 1].set_title('Cluster Distribution')
                axes[1, 1].axis('equal')
            
            fig.delaxes(axes[0,1]) # Remove unused subplot
            plt.tight_layout()
            plt.savefig("mlAnalysis/finalResults/summary_visualization.png", dpi=300)
            plt.show() if self.showInteractivePlots else plt.close()
        except Exception as e:
            print(f"Error generating final report: {e}")

    def executeFullAnalysis(self, filePaths: List[str]):
        """Execute the complete machine learning analysis pipeline"""
        print("Starting Comprehensive Machine Learning Analysis\n" + "=" * 50)
        try:
            if not self.loadData(filePaths):
                print("Failed to load data. Exiting.")
                return
            
            self.exploratoryDataAnalysis()
            self.preprocessData()
            self.featureEngineering()
            self.performClustering()
            self.predictiveModeling()
            self.timeSeriesAnalysis()
            self.generateFinalReport()
            
            print("\nAnalysis complete! Results saved in mlAnalysis/ directory.")
        
        except Exception as e:
            print(f"An error occurred during the full analysis execution: {e}")
            traceback.print_exc()

def main():
    filePaths = [
        'dados_ocupacao_080.csv',
        'dados_ocupacao_090.csv',
        'dados_ocupacao_095.csv',
        'dados_ocupacao_0999.csv'
    ]
    
    # Set showInteractivePlots=False to run without GUI interruptions
    analyzer = QueueDataMLAnalyzer(showInteractivePlots=True, randomState=42)
    analyzer.executeFullAnalysis(filePaths)

if __name__ == "__main__":
    main()
