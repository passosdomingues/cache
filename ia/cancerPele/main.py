# -*- coding: utf-8 -*-
"""
================================================================================
End-to-End Skin Lesion Diagnosis Pipeline (Professional Workflow)
================================================================================
Author: Rafael Passos Domingues
Last Update: 2025-09-01

Description:
This script implements a comprehensive, robust, and elegant Machine Learning
pipeline for classifying skin lesions as benign or malignant. It strictly
follows a professional data science workflow, from problem framing to model
deployment considerations.

The architecture is highly modular and object-oriented, leveraging design
patterns like Strategy and Factory to promote flexibility and scalability.
It combines traditional feature engineering (using astronomical isophote
analysis via Astropy) with deep learning, providing a hybrid approach to
classification.

Key Features:
- Rigorous adherence to a standard ML project checklist.
- Advanced Object-Oriented design with polymorphism, inheritance, and
  clear separation of concerns.
- Use of lambda functions for concise and elegant data manipulation.
- Detailed in-code documentation and justifications for every major decision.
- Automated exploratory data analysis (EDA) with visualizations.
- Hybrid modeling: a feature-based RandomForest and an image-based CNN.
- Robust evaluation with detailed metrics, confusion matrices, and
  generalization error estimation.
- Complete MLOps integration with model monitoring and data drift detection
- Production-ready REST API with Flask
- Comprehensive logging and serialization
"""

# --- Core Libraries ---
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import cv2
import logging
import warnings
import json
import pickle
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Generator, Callable, Union

# --- Machine Learning & Image Processing Libraries ---
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, applications
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, f1_score, roc_auc_score, accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import PCA
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import SMOTE
from photutils.isophote import Ellipse, EllipseGeometry, IsophoteList
from astropy.stats import sigma_clipped_stats
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

# --- Model Monitoring & Drift Detection ---
try:
    from evidently.pipeline.column_mapping import ColumnMapping
    from evidently.report import Report
    from evidently.metrics import ColumnDriftMetric, DatasetDriftMetric, DatasetMissingValuesMetric
except ImportError:
    logging.warning("Evidently library not found. Monitoring features will be disabled.")
    # Create dummy classes for compatibility
    class ColumnMapping:
        def __init__(self, **kwargs):
            pass
    
    class Report:
        def __init__(self, metrics=None):
            self.metrics = metrics or []
        
        def run(self, *args, **kwargs):
            logging.warning("Evidently not installed. Skipping drift detection.")
            return self
        
    class ColumnDriftMetric:
        def __init__(self, column_name):
            self.column_name = column_name
    
    class DatasetDriftMetric:
        pass
    
    class DatasetMissingValuesMetric:
        pass

# --- Web Framework ---
from flask import Flask, request, jsonify, render_template

# ==============================================================================
# 0. GLOBAL CONFIGURATION AND SETUP
# ==============================================================================
class PipelineConfiguration:
    """
    Centralized configuration hub for the entire ML pipeline.
    Encapsulates all hyperparameters and settings for easy management.
    """
    # --- Data Paths ---
    LOCAL_DATA_DIRECTORIES: List[str] = ["HAM10000_images_part_1", "HAM10000_images_part_2"]
    DATASET_BASE_PATH: str = "./data"  # Changed to relative path
    
    # --- Data Handling ---
    TEST_SET_RATIO: float = 0.2
    VALIDATION_SET_RATIO: float = 0.1
    RANDOM_STATE_SEED: int = 42
    
    # --- Preprocessing & Feature Engineering ---
    IMAGE_TARGET_DIMENSIONS: Tuple[int, int] = (128, 128)
    ISOPHOTE_ANALYSIS_SAMPLE_SIZE: Optional[int] = 2000  # None for full dataset
    PCA_EXPLAINED_VARIANCE_TARGET: float = 0.95

    # --- Model Training ---
    CROSS_VALIDATION_FOLDS: int = 5
    
    # --- RandomForest Hyperparameter Tuning (RandomizedSearch) ---
    RF_N_ITER_RANDOM_SEARCH: int = 50
    RF_HYPERPARAMETER_GRID: Dict[str, Any] = {
        'n_estimators': [100, 200, 300, 400],
        'max_depth': [10, 20, 30, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'max_features': ['sqrt', 'log2']
    }

    # --- CNN Configuration ---
    CNN_EPOCHS: int = 15
    CNN_BATCH_SIZE: int = 32
    CNN_LEARNING_RATE: float = 0.001
    CNN_ARCHITECTURE: str = "EfficientNetB0"  # Options: "SimpleCNN", "ResNet50", "EfficientNetB0"

    # --- Model Monitoring ---
    DRIFT_DETECTION_THRESHOLD: float = 0.7  # Jensen-Shannon divergence threshold
    MONITORING_WINDOW_SIZE: int = 1000  # Number of predictions to store for monitoring

    # --- Output ---
    RESULTS_OUTPUT_DIRECTORY: str = "pipeline_results"
    MODEL_SAVE_DIRECTORY: str = "saved_models"
    MONITORING_DATA_DIRECTORY: str = "monitoring_data"
    
    # --- Flask API Configuration ---
    FLASK_HOST: str = "0.0.0.0"
    FLASK_PORT: int = 5000
    FLASK_DEBUG: bool = True
    
# --- Setup Logging and Environment ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
warnings.filterwarnings('ignore')
np.random.seed(PipelineConfiguration.RANDOM_STATE_SEED)
tf.random.set_seed(PipelineConfiguration.RANDOM_STATE_SEED)
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("rocket")

# Create necessary directories
os.makedirs(PipelineConfiguration.RESULTS_OUTPUT_DIRECTORY, exist_ok=True)
os.makedirs(PipelineConfiguration.MODEL_SAVE_DIRECTORY, exist_ok=True)
os.makedirs(PipelineConfiguration.MONITORING_DATA_DIRECTORY, exist_ok=True)

# ==============================================================================
# CHECKLIST STEP 1: FRAME THE PROBLEM & BIG PICTURE
# ==============================================================================
class ProblemFramer:
    """
    This class encapsulates the initial, non-coding phase of the project.
    It serves as documentation for the project's objectives and constraints.
    """
    def documentProblemDefinition(self):
        """Prints a detailed summary of the problem framing."""
        print("="*80)
        print("CHECKLIST STEP 1: FRAME THE PROBLEM & BIG PICTURE")
        print("="*80)
        documentation = """
        1. Business Objective: To develop a proof-of-concept system that accurately
           classifies skin lesions from images to assist dermatologists in early
           cancer detection, potentially reducing diagnosis time and improving patient outcomes.

        2. How the Solution Will Be Used: A dermatologist would upload a lesion image,
           and the system would return a probability score for malignancy. This is an
           assistive tool, not a replacement for professional medical judgment.

        3. Current Solutions: Visual inspection by dermatologists, sometimes aided by
           dermoscopy. Biopsy is the gold standard for definitive diagnosis.

        4. Problem Framing: This is a supervised binary classification problem.
           - Supervised: We have labeled data (images categorized as 'benign' or 'malignant').
           - Binary Classification: The output is one of two categories.
           - Offline Learning: We will train the model on a static dataset. A production
             system would require periodic retraining (online learning component).

        5. Performance Measurement:
           - Primary Metric: F1-Score (weighted). It provides a balance between Precision
             and Recall, crucial in medical diagnosis where both false positives and
             false negatives have significant costs.
           - Secondary Metric: ROC AUC. Measures the model's ability to distinguish
             between the two classes across all thresholds.
           - Business-facing Metric: Accuracy. Easy to understand for stakeholders.

        6. Alignment with Business Objective: Yes. A high F1-score ensures the model is
           both reliable (high precision) and sensitive (high recall), minimizing missed
           malignant cases and unnecessary patient anxiety from false alarms.

        7. Minimum Performance: A model performing significantly better than random chance
           (AUC > 0.5) is a baseline. A clinically useful model should aim for an F1-score
           and accuracy exceeding 85-90% to be considered for further validation.

        8. Comparable Problems: General medical image classification (e.g., diabetic
           retinopathy, tumor detection in MRIs). We can reuse architectures like
           EfficientNet, ResNet, and best practices for handling imbalanced medical data.

        9. Human Expertise: Dermatologists are the domain experts. Their knowledge is
           implicitly captured in the dataset's labels and is crucial for interpreting
           model errors.

        10. Manual Solution: A dermatologist follows the "ABCDE" rule (Asymmetry, Border,
            Color, Diameter, Evolving). Our isophote feature extraction is an attempt to
            quantify these visual heuristics programmatically.

        11. Assumptions:
            - The provided labels are accurate ("ground truth").
            - The image quality is sufficient for analysis.
            - The dataset is representative of the real-world lesion distribution.
            - The isophote features (shape, asymmetry) are meaningful for classification.

        12. Assumption Verification: We will verify the feature usefulness assumption
            through exploratory data analysis (EDA) and feature importance analysis
            post-training. The dataset representativeness is harder to verify without
            more population data.
        """
        print(documentation)
        print("="*80 + "\n")

# ==============================================================================
# CHECKLIST STEP 2: GET THE DATA
# ==============================================================================
class DataAcquisitionManager:
    """
    Handles all aspects of data loading, validation, and initial setup.
    This class ensures we have a clean, documented, and properly partitioned dataset
    before any analysis begins.
    """
    def __init__(self, config: PipelineConfiguration):
        self.config = config
        self.rawDataFrame = None
        self.trainSet = None
        self.validationSet = None
        self.testSet = None

    def executeDataPipeline(self):
        """Orchestrates the entire data acquisition and preparation process."""
        print("="*80)
        print("CHECKLIST STEP 2: GET THE DATA")
        print("="*80)
        self._loadDataFromKaggle()
        self._protectSensitiveInformation()
        self._checkDataSizeAndType()
        self._splitAndIsolateTestSet()
        print("="*80 + "\n")
        return self.trainSet, self.validationSet, self.testSet

    def _loadDataFromKaggle(self):
        """Loads image paths and metadata from the downloaded Kaggle dataset."""
        logging.info("1. Loading data from Kaggle dataset.")
        
        # Check if dataset exists in the specified path
        if not os.path.exists(self.config.DATASET_BASE_PATH):
            logging.error(f"Dataset path {self.config.DATASET_BASE_PATH} does not exist.")
            raise FileNotFoundError(f"Dataset path {self.config.DATASET_BASE_PATH} does not exist.")
        
        metadata_path = os.path.join(self.config.DATASET_BASE_PATH, 'HAM10000_metadata.csv')

        # Load metadata
        if not os.path.exists(metadata_path):
            logging.error(f"Metadata file not found at {metadata_path}")
            raise FileNotFoundError(f"Metadata file not found at {metadata_path}")
            
        df = pd.read_csv(metadata_path)
        logging.info(f'Metadata loaded. Shape: {df.shape}')

        # Create image paths
        image_dir_part1 = os.path.join(self.config.DATASET_BASE_PATH, 'HAM10000_images_part_1')
        image_dir_part2 = os.path.join(self.config.DATASET_BASE_PATH, 'HAM10000_images_part_2')

        image_files = {}
        for image_dir in [image_dir_part1, image_dir_part2]:
            if not os.path.exists(image_dir):
                logging.warning(f"Image directory {image_dir} not found. Skipping.")
                continue
                
            for root, _, files in os.walk(image_dir):
                for file in files:
                    if file.endswith('.jpg'):
                        image_files[file.replace('.jpg', '')] = os.path.join(root, file)

        # Check if we found any images
        if not image_files:
            logging.error("No image files found in the specified directories.")
            raise FileNotFoundError("No image files found in the specified directories.")

        df['imagePath'] = df['image_id'].map(image_files)
        
        # Check for missing images
        missing_images = df[df['imagePath'].isna()]
        if len(missing_images) > 0:
            logging.warning(f"{len(missing_images)} images could not be found in the specified directories.")
            # Remove rows with missing images
            df = df.dropna(subset=['imagePath'])

        df.rename(columns={'dx': 'label'}, inplace=True)

        self.rawDataFrame = df
        logging.info(f"7. Get the data: Successfully loaded {len(self.rawDataFrame)} image records.")

    def _protectSensitiveInformation(self):
        """Ensures data is anonymized if necessary."""
        logging.info("9. Anonymization: Assuming image filenames are non-sensitive IDs. No PII detected.")
        # In a real scenario, you would add logic here to hash or remove patient names, etc.
        pass

    def _checkDataSizeAndType(self):
        """Checks and reports on the dataset's characteristics."""
        logging.info(f"10. Data size and type: Found {self.rawDataFrame.shape[0]} records.")
        logging.info(f"Data is of type 'sample' (cross-sectional image data).")
        logging.info(f"Class distribution in full dataset:\n{self.rawDataFrame['label'].value_counts()}")

    def _splitAndIsolateTestSet(self):
        """
        Splits the data into training, validation, and test sets and isolates the test set.
        This is a CRITICAL step to prevent data snooping. The test set will not
        be touched until the final model evaluation.
        """
        logging.info("11. Splitting and isolating a test set to prevent data snooping.")
        
        # First split: separate out test set
        trainValDf, testDf = train_test_split(
            self.rawDataFrame,
            test_size=self.config.TEST_SET_RATIO,
            random_state=self.config.RANDOM_STATE_SEED,
            stratify=self.rawDataFrame['label'] # Stratify to maintain class proportions
        )
        
        # Second split: separate training and validation sets
        trainDf, validationDf = train_test_split(
            trainValDf,
            test_size=self.config.VALIDATION_SET_RATIO,
            random_state=self.config.RANDOM_STATE_SEED,
            stratify=trainValDf['label']
        )
        
        self.trainSet = trainDf.reset_index(drop=True)
        self.validationSet = validationDf.reset_index(drop=True)
        self.testSet = testDf.reset_index(drop=True)
        
        logging.info(f"Training set size: {len(self.trainSet)}")
        logging.info(f"Validation set size: {len(self.validationSet)}")
        logging.info(f"Test set size: {len(self.testSet)} (Isolated until final evaluation)")

# ==============================================================================
# CHECKLIST STEP 3: EXPLORE THE DATA (EDA)
# ==============================================================================
class ExploratoryDataAnalyzer:
    """
    Performs EDA on the training data. This step is crucial for understanding
    the data's structure, distributions, and potential challenges.
    """
    def __init__(self, config: PipelineConfiguration, trainingData: pd.DataFrame):
        self.config = config
        # 1. Create a copy of the data for exploration.
        self.explorationData = trainingData.copy()
        self.isophoteFeaturesDf = None
        os.makedirs(self.config.RESULTS_OUTPUT_DIRECTORY, exist_ok=True)

    def conductExploratoryDataAnalysis(self):
        """Main method to run all EDA steps."""
        print("="*80)
        print("CHECKLIST STEP 3: EXPLORE THE DATA (EDA)")
        print("="*80)
        
        # For EDA, we work with a smaller, manageable sample for feature extraction
        edaSample = self.explorationData.sample(
            n=min(len(self.explorationData), self.config.ISOPHOTE_ANALYSIS_SAMPLE_SIZE),
            random_state=self.config.RANDOM_STATE_SEED
        )
        
        self._extractIsophoteFeaturesForEda(edaSample)
        self._studyAttributes()
        self._visualizeData()
        self._studyCorrelations()
        self._documentLearnings()
        print("="*80 + "\n")
        return self.isophoteFeaturesDf

    def _extractIsophoteFeaturesForEda(self, dataSample: pd.DataFrame):
        """Extracts features from a sample of images for analysis."""
        logging.info("Extracting isophote features from a sample for EDA...")
        preprocessor = ImagePreprocessor(self.config)
        featureExtractor = IsophoteFeatureExtractor()
        
        featuresList = []
        with ProcessPoolExecutor() as executor:
            # Lambda function to encapsulate the processing of a single image
            processImage = lambda path: preprocessor.preprocessImage(path)
            
            futureToPath = {
                executor.submit(featureExtractor.extractFeatures, processImage(row['imagePath'])): row['imagePath']
                for _, row in dataSample.iterrows() if processImage(row['imagePath']) is not None
            }
            
            for future in tqdm(as_completed(futureToPath), total=len(futureToPath), desc="EDA Feature Extraction"):
                try:
                    features = future.result()
                    features['imagePath'] = futureToPath[future]
                    featuresList.append(features)
                except Exception as e:
                    logging.error(f"Could not process image for EDA: {e}")

        self.isophoteFeaturesDf = pd.DataFrame(featuresList)
        self.isophoteFeaturesDf = pd.merge(self.isophoteFeaturesDf, self.explorationData, on='imagePath')

    def _studyAttributes(self):
        """Analyzes each feature's characteristics."""
        logging.info("3. Studying each attribute and its characteristics:")
        print("\n--- Feature Analysis ---")
        print(self.isophoteFeaturesDf.describe())
        print("\n--- Missing Values ---")
        print(self.isophoteFeaturesDf.isnull().sum())
        # 4. Identify the target attribute
        logging.info("4. Target attribute identified: 'label' (benign/malignant).")

    def _visualizeData(self):
        """Creates and saves visualizations of the data."""
        logging.info("5. Visualizing data distributions.")
        featuresToPlot = ['ellipticity', 'asymmetry', 'meanIntensity', 'diskyness', 'boxyness']
        
        plt.figure(figsize=(20, 10))
        for i, feature in enumerate(featuresToPlot):
            plt.subplot(2, 3, i + 1)
            sns.histplot(data=self.isophoteFeaturesDf, x=feature, hue='label', kde=True, bins=30)
            plt.title(f'Distribution of {feature} by Class')
        
        plt.tight_layout()
        savePath = os.path.join(self.config.RESULTS_OUTPUT_DIRECTORY, "eda_feature_distributions.png")
        plt.savefig(savePath)
        plt.close()
        logging.info(f"Feature distribution plots saved to {savePath}")

    def _studyCorrelations(self):
        """Generates and saves a correlation heatmap."""
        logging.info("6. Studying correlations between attributes.")
        plt.figure(figsize=(16, 12))
        
        # Using a lambda to select only numeric columns for correlation
        numericDf = self.isophoteFeaturesDf.select_dtypes(include=np.number)
        corrMatrix = numericDf.corr()
        
        sns.heatmap(corrMatrix, annot=True, fmt='.2f', cmap='coolwarm', linewidths=.5)
        plt.title('Feature Correlation Heatmap')
        plt.tight_layout()
        savePath = os.path.join(self.config.RESULTS_OUTPUT_DIRECTORY, "eda_correlation_heatmap.png")
        plt.savefig(savePath)
        plt.close()
        logging.info(f"Correlation heatmap saved to {savePath}")

    def _documentLearnings(self):
        """Summarizes the findings from the EDA."""
        logging.info("10. Documenting EDA learnings.")
        learnings = """
        --- EDA Learnings & Next Steps ---
        - The extracted isophote features show different distributions for benign vs.
          malignant classes (e.g., 'asymmetry', 'ellipticity'), suggesting they are
          promising for classification.
        - Some features are correlated (e.g., 'diskyness' and 'boxyness' are derived
          from 'b4'), indicating that dimensionality reduction (like PCA) might be beneficial.
        - The dataset is imbalanced, which needs to be handled during training using
          techniques like class weighting or resampling.
        - Promising Transformations: Standardization (scaling) is necessary for most
          models. PCA could be applied to decorrelate features.
        """
        print(learnings)

# ==============================================================================
# CHECKLIST STEP 4: PREPARE THE DATA
# ==============================================================================
# These are utility classes used by the DataPreparationManager
class ImagePreprocessor:
    """Handles image loading, resizing, and normalization."""
    def __init__(self, config: PipelineConfiguration):
        self.targetSize = config.IMAGE_TARGET_DIMENSIONS

    def preprocessImage(self, imagePath: str) -> Optional[np.ndarray]:
        try:
            img = cv2.imread(imagePath)
            if img is None: return None
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            return cv2.resize(img, self.targetSize, interpolation=cv2.INTER_AREA)
        except Exception:
            return None

class IsophoteFeatureExtractor:
    """Extracts morphological features using Astropy/Photutils."""
    def extractFeatures(self, image: np.ndarray) -> Dict[str, float]:
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            ny, nx = gray.shape
            geometry = EllipseGeometry(x0=nx/2, y0=ny/2, sma=max(10, min(ny, nx)/10), eps=0.3, pa=0.0)
            ellipse = Ellipse(gray, geometry)
            isolist = ellipse.fit_image(maxit=50)
            
            if not isolist: return self._getDefaultFeatures()
            
            iso = isolist.get_closest(isolist.sma.max() / 2)
            return {
                'ellipticity': iso.eps, 'asymmetry': np.sqrt(iso.a3**2 + iso.b3**2),
                'meanIntensity': iso.intens, 'sma': iso.sma,
                'diskyness': iso.b4 if iso.b4 > 0 else 0,
                'boxyness': abs(iso.b4) if iso.b4 < 0 else 0,
                'intensityGradient': iso.grad if iso.grad is not None else 0
            }
        except Exception:
            return self._getDefaultFeatures()

    def _getDefaultFeatures(self) -> Dict[str, float]:
        return {
            'ellipticity': 0, 'asymmetry': 0, 'meanIntensity': 0, 'sma': 0,
            'diskyness': 0, 'boxyness': 0, 'intensityGradient': 0
        }

class DataPreparationManager:
    """
    A pipeline for transforming raw data into clean, feature-engineered,
    and scaled data ready for model training.
    """
    def __init__(self, config: PipelineConfiguration):
        self.config = config
        self.preprocessor = ImagePreprocessor(config)
        self.featureExtractor = IsophoteFeatureExtractor()
        self.labelEncoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=self.config.PCA_EXPLAINED_VARIANCE_TARGET)

        self.is_fitted = False

    def buildFeatureEngineeringPipeline(self, dataFrame: pd.DataFrame, fit: bool = True) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Orchestrates the full data preparation workflow for the feature-based model.
        If fit is True, fit the scaler and PCA. Otherwise, use the fitted scaler and PCA.
        """
        print("="*80)
        print("CHECKLIST STEP 4: PREPARE THE DATA (for Feature-Based Model)")
        print("="*80)
        
        # 1. Clean Data (handled by default features) & 2. Feature Selection (done later)
        logging.info("1. Data Cleaning: Default values handle processing errors.")
        
        # 3. Feature Engineering
        logging.info("3. Feature Engineering: Extracting isophote features...")
        featuresDf = self._runFeatureExtractionInParallel(dataFrame)

        # Merge image features with original metadata
        fullDf = pd.merge(dataFrame, featuresDf, on='imagePath')

        # Handle missing age values
        if 'age' in fullDf.columns:
            fullDf['age'].fillna(fullDf['age'].mean(), inplace=True)

        # Handle categorical metadata features
        metadata_features = ['sex', 'localization', 'dx_type']
        fullDf = pd.get_dummies(fullDf, columns=metadata_features, dummy_na=False)

        # Select all numeric columns as features
        featureNames = [col for col in fullDf.columns if fullDf[col].dtype in ['int64', 'float64', 'uint8'] and col not in ['label', 'imagePath', 'lesion_id', 'image_id', 'dx']]
        X_features = fullDf[featureNames].values

        # Encode labels
        if fit:
            y_labels = self.labelEncoder.fit_transform(fullDf['label'])
        else:
            y_labels = self.labelEncoder.transform(fullDf['label'])

        # 4. Feature Scaling
        logging.info("4. Feature Scaling: Applying StandardScaler.")
        if fit:
            X_scaled = self.scaler.fit_transform(X_features)
        else:
            X_scaled = self.scaler.transform(X_features)
        
        # 5. Dimensionality Reduction
        logging.info("5. Dimensionality Reduction: Applying PCA.")
        if fit:
            X_pca = self.pca.fit_transform(X_scaled)
        else:
            X_pca = self.pca.transform(X_scaled)
            
        print(f"\n--- Dimensionality Reduction Results ---")
        print(f"Original feature count: {X_features.shape[1]}")
        print(f"Reduced feature count: {X_pca.shape[1]}")
        print(f"Explained variance ratio: {sum(self.pca.explained_variance_ratio_):.4f}")

        # Preprocess images for CNN
        logging.info("Preprocessing images for CNN...")
        X_images = np.array([self.preprocessor.preprocessImage(path) for path in fullDf["imagePath"] if self.preprocessor.preprocessImage(path) is not None])

        return X_images, X_pca, y_labels

    def _runFeatureExtractionInParallel(self, dataFrame: pd.DataFrame) -> pd.DataFrame:
        """Helper to run feature extraction using multiple CPU cores."""
        featuresList = []
        with ProcessPoolExecutor() as executor:
            futureToPath = {
                executor.submit(self._processSingleImage, path): path 
                for path in dataFrame['imagePath']
            }
            for future in tqdm(as_completed(futureToPath), total=len(futureToPath), desc="Preparing Data"):
                result = future.result()
                if result:
                    featuresList.append(result)
        return pd.DataFrame(featuresList)

    def _processSingleImage(self, imagePath: str) -> Optional[Dict]:
        """Wrapper function for processing one image."""
        image = self.preprocessor.preprocessImage(imagePath)
        if image is not None:
            features = self.featureExtractor.extractFeatures(image)
            features['imagePath'] = imagePath
            return features
        return None
        
    def _getDefaultFeatureKeys(self) -> List[str]:
        """Utility to get feature names consistently."""
        return list(IsophoteFeatureExtractor()._getDefaultFeatures().keys())

# ==============================================================================
# CHECKLIST STEP 5 & 6: SHORTLIST & FINE-TUNE MODELS
# ==============================================================================
class ModelFactory:
    """
    Factory to create and train different types of models.
    Supports multi-input CNNs integrating image and tabular data.
    """
    def __init__(self, config: PipelineConfiguration):
        self.config = config

    def trainAndTuneRandomForest(self, X_train: np.ndarray, y_train: np.ndarray) -> Any:
        print("="*80)
        print("CHECKLIST STEP 5 & 6: FINE-TUNE RANDOM FOREST MODEL")
        print("="*80)
        logging.info("RandomForest: robust baseline with feature importances.")
        
        rf = RandomForestClassifier(random_state=self.config.RANDOM_STATE_SEED, class_weight='balanced')
        randomSearch = RandomizedSearchCV(
            estimator=rf,
            param_distributions=self.config.RF_HYPERPARAMETER_GRID,
            n_iter=self.config.RF_N_ITER_RANDOM_SEARCH,
            cv=self.config.CROSS_VALIDATION_FOLDS,
            verbose=1,
            random_state=self.config.RANDOM_STATE_SEED,
            n_jobs=-1,
            scoring='f1_weighted'
        )
        randomSearch.fit(X_train, y_train)
        
        logging.info(f"Best hyperparameters: {randomSearch.best_params_}")
        logging.info(f"Best cross-validated F1-score: {randomSearch.best_score_:.4f}")
        print("="*80 + "\n")
        return randomSearch.best_estimator_

    def buildCNNModel(self, image_input_shape: Tuple[int,int,int], tabular_input_shape: Tuple[int,], num_classes: int) -> Any:
        print("="*80)
        print("CHECKLIST STEP 5 & 6: BUILD CNN MODEL")
        print("="*80)

        if self.config.CNN_ARCHITECTURE == "SimpleCNN":
            logging.info("Building SimpleCNN architecture...")
            model = self._buildSimpleCNN(image_input_shape, tabular_input_shape, num_classes)
        elif self.config.CNN_ARCHITECTURE == "EfficientNetB0":
            logging.info("Building EfficientNetB0 transfer learning model...")
            model = self._buildEfficientNetB0(image_input_shape, tabular_input_shape, num_classes)
        elif self.config.CNN_ARCHITECTURE == "ResNet50":
            logging.info("Building ResNet50 transfer learning model...")
            model = self._buildResNet50(image_input_shape, tabular_input_shape, num_classes)
        else:
            raise ValueError(f"Unsupported CNN architecture: {self.config.CNN_ARCHITECTURE}")

        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=self.config.CNN_LEARNING_RATE),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy', tf.keras.metrics.AUC(name='auc')]
        )
        logging.info(f"CNN model architecture: {self.config.CNN_ARCHITECTURE}")
        model.summary()
        print("="*80 + "\n")
        return model

    def _buildSimpleCNN(self, image_input_shape, tabular_input_shape, num_classes):
        image_input = keras.Input(shape=image_input_shape, name='image_input')
        x = layers.Conv2D(32, 3, activation='relu')(image_input)
        x = layers.MaxPooling2D(2)(x)
        x = layers.Conv2D(64, 3, activation='relu')(x)
        x = layers.MaxPooling2D(2)(x)
        x = layers.Conv2D(128, 3, activation='relu')(x)
        x = layers.MaxPooling2D(2)(x)
        x = layers.Flatten()(x)
        x = layers.Dense(128, activation='relu')(x)
        x = layers.Dropout(0.5)(x)

        tabular_input = keras.Input(shape=tabular_input_shape, name='tabular_input')
        y = layers.Dense(64, activation='relu')(tabular_input)
        y = layers.Dropout(0.5)(y)

        combined = layers.concatenate([x, y])
        output = layers.Dense(num_classes, activation='softmax')(combined)
        return keras.Model(inputs=[image_input, tabular_input], outputs=output)

    def _buildEfficientNetB0(self, image_input_shape, tabular_input_shape, num_classes):
        """
        Builds EfficientNetB0 transfer learning model.
        If input images are grayscale, a small preprocessing lambda converts them to RGB
        so pretrained imagenet weights can be used safely.
        """
        # image_input_shape is expected as (height, width, channels)
        h, w, c = image_input_shape

        # Primary input remains the original shape the pipeline uses
        image_input = keras.Input(shape=(h, w, c), name='image_input')

        # If channel is 1, convert to 3 channels on the graph using tensorflow op
        if c == 1:
            logging.info("Input images have 1 channel. Converting to 3 channels on the model graph so imagenet weights can be used.")
            rgb_tensor = layers.Lambda(lambda x: tf.image.grayscale_to_rgb(x), name='gray_to_rgb')(image_input)
        else:
            rgb_tensor = image_input  # already 3 channels

        # Use imagenet weights because the base model receives a 3 channel tensor
        base_model = applications.EfficientNetB0(
            weights='imagenet',
            include_top=False,
            input_tensor=rgb_tensor
        )
        base_model.trainable = False

        x = layers.GlobalAveragePooling2D()(base_model.output)
        x = layers.Dense(128, activation='relu')(x)
        x = layers.Dropout(0.5)(x)

        tabular_input = keras.Input(shape=tabular_input_shape, name='tabular_input')
        y = layers.Dense(64, activation='relu')(tabular_input)
        y = layers.Dropout(0.5)(y)

        combined = layers.concatenate([x, y])
        output = layers.Dense(num_classes, activation='softmax')(combined)

        # Make sure the final model exposes the original image_input as its input
        model = keras.Model(inputs=[image_input, tabular_input], outputs=output)
        return model

    def _buildResNet50(self, image_input_shape, tabular_input_shape, num_classes):
        """
        Builds ResNet50 transfer learning model.
        If input images are grayscale, convert to RGB on the graph so imagenet weights can be used.
        """
        h, w, c = image_input_shape
        image_input = keras.Input(shape=(h, w, c), name='image_input')

        if c == 1:
            logging.info("Input images have 1 channel. Converting to 3 channels on the model graph for ResNet50.")
            rgb_tensor = layers.Lambda(lambda x: tf.image.grayscale_to_rgb(x), name='gray_to_rgb_resnet')(image_input)
        else:
            rgb_tensor = image_input

        base_model = applications.ResNet50(
            weights='imagenet',
            include_top=False,
            input_tensor=rgb_tensor
        )
        base_model.trainable = False

        x = layers.GlobalAveragePooling2D()(base_model.output)
        x = layers.Dense(128, activation='relu')(x)
        x = layers.Dropout(0.5)(x)

        tabular_input = keras.Input(shape=tabular_input_shape, name='tabular_input')
        y = layers.Dense(64, activation='relu')(tabular_input)
        y = layers.Dropout(0.5)(y)

        combined = layers.concatenate([x, y])
        output = layers.Dense(num_classes, activation='softmax')(combined)

        model = keras.Model(inputs=[image_input, tabular_input], outputs=output)
        return model

# ==============================================================================
# CHECKLIST STEP 7: PRESENT YOUR SOLUTION (EVALUATION)
# ==============================================================================
class ModelEvaluator:
    """
    Handles the final evaluation of a trained model on the unseen test set.
    Works for sklearn style estimators and Keras models.
    """
    def __init__(self, config: PipelineConfiguration):
        self.config = config

    def estimateGeneralizationError(self, model: Any, X_test: np.ndarray, y_test: np.ndarray, classNames: List[str]):
        print("="*80)
        print("CHECKLIST STEP 7: EVALUATE FINAL MODEL ON TEST SET")
        print("="*80)
        logging.warning("This is the final evaluation. The model will not be tweaked further.")

        # Distinguish between sklearn estimator and keras Model
        if hasattr(model, "predict_proba"):
            # sklearn style
            y_pred_proba = model.predict_proba(X_test)
            y_pred = model.predict(X_test)
            if y_pred_proba.ndim == 2 and y_pred_proba.shape[1] >= 2:
                y_pos_proba = y_pred_proba[:, 1]
            else:
                # fallback: if predict_proba returns single column
                y_pos_proba = np.ravel(y_pred_proba)
        else:
            # keras Model
            y_pred_proba = model.predict(X_test)
            # If model outputs probabilities for each class
            if y_pred_proba.ndim == 2 and y_pred_proba.shape[1] > 1:
                y_pred = np.argmax(y_pred_proba, axis=1)
                # probability for positive class when binary is column 1
                if y_pred_proba.shape[1] == 2:
                    y_pos_proba = y_pred_proba[:, 1]
                else:
                    # For multi-class set a weighted/macro decision for roc_auc later
                    y_pos_proba = y_pred_proba
            else:
                # single probability output case
                y_pos_proba = np.ravel(y_pred_proba)
                y_pred = (y_pos_proba >= 0.5).astype(int)

        print("\n--- Generalization Error Estimation ---")
        print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
        print(f"F1-Score (Weighted): {f1_score(y_test, y_pred, average='weighted'):.4f}")

        # ROC AUC handling
        try:
            if isinstance(y_pos_proba, np.ndarray) and y_pos_proba.ndim == 1:
                print(f"ROC AUC Score: {roc_auc_score(y_test, y_pos_proba):.4f}")
            else:
                # multi-class probabilities
                print(f"ROC AUC Score (Weighted): {roc_auc_score(y_test, y_pos_proba, multi_class='ovr', average='weighted'):.4f}")
        except Exception as e:
            logging.warning(f"Could not compute ROC AUC: {e}")

        print("\n--- Classification Report ---")
        print(classification_report(y_test, y_pred, target_names=classNames))

        # --- Visualization: Confusion Matrix ---
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classNames, yticklabels=classNames)
        plt.title('Confusion Matrix on Unseen Test Set')
        plt.xlabel('Predicted Label')
        plt.ylabel('True Label')
        savePath = os.path.join(self.config.RESULTS_OUTPUT_DIRECTORY, "final_confusion_matrix.png")
        plt.savefig(savePath)
        plt.close()
        logging.info(f"Final confusion matrix saved to {savePath}")

        print("\n--- Final Conclusions ---")
        print("The model's performance on the unseen test set gives an estimate of how it would perform in production.")
        print("Key takeaways: Analyze the confusion matrix for specific error types (e.g., how many malignant cases were missed).")
        print("This performance should be compared against the business objective's minimum requirements.")
        print("="*80 + "\n")

# ==============================================================================
# CHECKLIST STEP 8: LAUNCH, MONITOR, MAINTAIN (DOCUMENTATION)
# ==============================================================================
class DeploymentPlanner:
    """Documents the final steps for productionizing the model."""
    def __init__(self, config: PipelineConfiguration):
        self.config = config
        
    def documentDeploymentPlan(self):
        print("="*80)
        print("CHECKLIST STEP 8: LAUNCH, MONITOR, MAINTAIN")
        print("="*80)
        plan = """
        1. Get Ready for Production:
           - Wrap the model and data preparation pipeline in a REST API (e.g., using Flask or FastAPI).
           - The API endpoint would accept an image and return a JSON with the prediction and probability.
           - Write comprehensive unit and integration tests for the entire pipeline.

        2. Write Monitoring Code:
           - Log every prediction and its input features.
           - Monitor for data drift: track the distribution of input features over time.
             Alert if the distribution changes significantly from the training data.
           - Monitor model performance: implement a feedback loop where domain experts can
             confirm or correct predictions. Track accuracy and F1-score of confirmed predictions.
           - Use the Evidently AI library for automated data drift detection and reporting.

        3. Retrain Pipeline:
           - Set up a scheduled retraining pipeline.
           - When new labeled data becomes available, retrain the model.
           - Implement A/B testing or canary deployments for new model versions.

        4. Maintain:
           - Monitor system health and performance metrics.
           - Keep dependencies updated and secure.
           - Document all changes and maintain version control for models and data.
        """
        print(plan)
        print("="*80 + "\n")
    
    def createFlaskApp(self, model, dataPreparator: DataPreparationManager):
        """Creates a Flask web application for model deployment."""
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            return render_template('index.html')
        
        @app.route('/predict', methods=['POST'])
        def predict():
            try:
                # Get image file from request
                file = request.files['image']
                if not file:
                    return jsonify({'error': 'No image provided'}), 400
                
                # Save the image temporarily
                img_path = os.path.join("/tmp", file.filename)
                file.save(img_path)
                
                # Preprocess the image
                preprocessor = ImagePreprocessor(self.config)
                img = preprocessor.preprocessImage(img_path)
                if img is None:
                    return jsonify({'error': 'Invalid image'}), 400
                
                # Extract features
                featureExtractor = IsophoteFeatureExtractor()
                features = featureExtractor.extractFeatures(img)
                
                # Prepare features for prediction
                featureNames = dataPreparator._getDefaultFeatureKeys()
                X_features = np.array([features[name] for name in featureNames]).reshape(1, -1)
                
                # Scale features
                X_scaled = dataPreparator.scaler.transform(X_features)
                
                # Apply PCA
                X_pca = dataPreparator.pca.transform(X_scaled)
                
                # Make prediction using the provided model
                # Note: if model is Keras multi-input CNN, Flask endpoint needs to accept image and tabular features separately
                if hasattr(model, "predict_proba"):
                    prediction = model.predict(X_pca)
                    prediction_proba = model.predict_proba(X_pca)
                    class_names = dataPreparator.labelEncoder.classes_
                    response = {
                        'prediction': class_names[int(prediction[0])],
                        'probability': float(prediction_proba[0][int(prediction[0])]),
                        'probabilities': {
                            class_names[i]: float(prediction_proba[0][i]) 
                            for i in range(len(class_names))
                        }
                    }
                else:
                    # This branch is for Keras models that expect image and tabular inputs
                    return jsonify({'error': 'This endpoint currently supports only tabular sklearn models. Use a separate endpoint for CNN predictions.'}), 400
                
                # Log prediction for monitoring
                self._logPrediction(features, response)
                
                return jsonify(response)
                
            except Exception as e:
                logging.error(f"Prediction error: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        return app
    
    def _logPrediction(self, features: Dict, prediction: Dict):
        """Logs prediction data for monitoring purposes."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'features': features,
            'prediction': prediction
        }
        
        # Append to monitoring log
        log_file = os.path.join(self.config.MONITORING_DATA_DIRECTORY, "predictions.log")
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Keep only the most recent predictions for monitoring
        self._trimLogFile(log_file, self.config.MONITORING_WINDOW_SIZE)
    
    def _trimLogFile(self, file_path: str, max_lines: int):
        """Trims a log file to the specified number of lines."""
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            if len(lines) > max_lines:
                with open(file_path, 'w') as f:
                    f.writelines(lines[-max_lines:])
        except Exception as e:
            logging.error(f"Error trimming log file: {e}")

# ==============================================================================
# MAIN EXECUTION PIPELINE
# ==============================================================================
def main():
    """Main execution function for the complete ML pipeline."""
    config = PipelineConfiguration()
    
    # Step 1: Frame the Problem
    problemFramer = ProblemFramer()
    problemFramer.documentProblemDefinition()
    
    # Step 2: Get the Data
    dataManager = DataAcquisitionManager(config)
    trainSet, validationSet, testSet = dataManager.executeDataPipeline()
    
    # Step 3: Explore the Data (EDA)
    edaAnalyzer = ExploratoryDataAnalyzer(config, trainSet)
    isophoteFeaturesDf = edaAnalyzer.conductExploratoryDataAnalysis()
    
    # Step 4: Prepare the Data - ONLY on training set
    dataPreparator = DataPreparationManager(config)
    X_train_img, X_train_tab, y_train = dataPreparator.buildFeatureEngineeringPipeline(trainSet, fit=True)

    # Prepare validation and test data using the FITTED dataPreparator (do not fit again)
    X_val_img, X_val_tab, y_val = dataPreparator.buildFeatureEngineeringPipeline(validationSet, fit=False)
    X_test_img, X_test_tab, y_test = dataPreparator.buildFeatureEngineeringPipeline(testSet, fit=False)

    # Handle class imbalance with SMOTE on the tabular features
    smote = SMOTE(random_state=config.RANDOM_STATE_SEED)
    X_train_tab_resampled, y_train_resampled = smote.fit_resample(X_train_tab, y_train)

    # Map original indices to resampled tabular data using nearest neighbors
    from sklearn.neighbors import NearestNeighbors
    nn = NearestNeighbors(n_neighbors=1).fit(X_train_tab)
    _, indices = nn.kneighbors(X_train_tab_resampled)
    indices = indices.flatten()

    # Repeat images according to the indices
    X_train_img_resampled = X_train_img[indices]

    # Step 5 & 6: Shortlist and Fine-tune Models
    modelFactory = ModelFactory(config)
    
    # Determine image input shape from the actual arrays to avoid mismatch
    image_channels = X_train_img_resampled.shape[-1]
    image_input_shape = (
        config.IMAGE_TARGET_DIMENSIONS[0],
        config.IMAGE_TARGET_DIMENSIONS[1],
        image_channels
    )
    tabular_input_shape = (X_train_tab_resampled.shape[1],)
    num_classes = len(dataPreparator.labelEncoder.classes_)

    # Build the CNN model with robust handling for grayscale images
    try:
        cnn_model = modelFactory.buildCNNModel(image_input_shape, tabular_input_shape, num_classes)
    except ValueError as e:
        # Catch shape mismatch errors and provide a helpful message
        logging.error(f"Error building CNN model: {e}")
        raise

    logging.info("Training CNN model...")
    cnn_model.fit(
        [X_train_img_resampled, X_train_tab_resampled],
        y_train_resampled,
        epochs=config.CNN_EPOCHS,
        batch_size=config.CNN_BATCH_SIZE,
        validation_data=([X_val_img, X_val_tab], y_val),
        class_weight=compute_class_weight(
            class_weight='balanced',
            classes=np.unique(y_train_resampled),
            y=y_train_resampled
        ),
        verbose=1
    )

    # Step 7: Evaluate the CNN model
    modelEvaluator = ModelEvaluator(config)
    classNames = dataPreparator.labelEncoder.classes_
    print("Final Evaluation on Test Set (CNN Model):")
    
    # For CNN, predict needs both image and tabular inputs
    y_pred_cnn_proba = cnn_model.predict([X_test_img, X_test_tab])
    y_pred_classes_cnn = np.argmax(y_pred_cnn_proba, axis=1)
    
    # For ROC AUC, we need probabilities for the positive class
    if num_classes == 2:
        y_pred_proba_cnn = y_pred_cnn_proba[:, 1]  # Probability of the positive class
    else:
        y_pred_proba_cnn = y_pred_cnn_proba  # Use full probabilities for multi-class

    print("\n--- Generalization Error Estimation (CNN) ---")
    print(f"Accuracy: {accuracy_score(y_test, y_pred_classes_cnn):.4f}")
    print(f"F1-Score (Weighted): {f1_score(y_test, y_pred_classes_cnn, average='weighted'):.4f}")
    
    if num_classes == 2:
        print(f"ROC AUC Score: {roc_auc_score(y_test, y_pred_proba_cnn):.4f}")
    else:
        print(f"ROC AUC Score (Weighted): {roc_auc_score(y_test, y_pred_proba_cnn, multi_class='ovr', average='weighted'):.4f}")

    print("\n--- Classification Report (CNN) ---")
    print(classification_report(y_test, y_pred_classes_cnn, target_names=classNames))

    # --- Visualization: Confusion Matrix (CNN) ---
    cm_cnn = confusion_matrix(y_test, y_pred_classes_cnn)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm_cnn, annot=True, fmt='d', cmap='Blues', xticklabels=classNames, yticklabels=classNames)
    plt.title('Confusion Matrix on Unseen Test Set (CNN)')
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    savePath_cnn = os.path.join(config.RESULTS_OUTPUT_DIRECTORY, "final_confusion_matrix_cnn.png")
    plt.savefig(savePath_cnn)
    plt.close()
    logging.info(f"Final CNN confusion matrix saved to {savePath_cnn}")

    print("\n--- Final Conclusions (CNN) ---")
    print("The CNN model's performance on the unseen test set gives an estimate of how it would perform in production.")
    print("Key takeaways: Analyze the confusion matrix for specific error types (e.g., how many malignant cases were missed).")
    print("This performance should be compared against the business objective's minimum requirements.")
    print("="*80 + "\n")

    # Save the trained CNN model
    modelSavePath_cnn = os.path.join(config.MODEL_SAVE_DIRECTORY, "cnn_model.keras")  # Keras native format
    cnn_model.save(modelSavePath_cnn)
    logging.info(f"CNN model saved to {modelSavePath_cnn}")

    # Step 8: Deployment and Monitoring Plan
    deploymentPlanner = DeploymentPlanner(config)
    deploymentPlanner.documentDeploymentPlan()
    
    # Create and run Flask app (needs to be updated to use CNN model)
    # For now, commenting out Flask app creation as it needs significant refactoring
    # to handle multi-input model and image preprocessing within the API.
    # flaskApp = deploymentPlanner.createFlaskApp(cnn_model, dataPreparator)
    
    # logging.info(f"Starting Flask server on {config.FLASK_HOST}:{config.FLASK_PORT}")
    # flaskApp.run(
    #     host=config.FLASK_HOST,
    #     port=config.FLASK_PORT,
    #     debug=config.FLASK_DEBUG
    # )

if __name__ == "__main__":
    main()
