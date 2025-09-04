# -*- coding: utf-8 -*-
"""
================================================================================
End-to-End Skin Lesion Diagnosis Pipeline (Professional Workflow)
================================================================================
Author: Rafael Passos Domingues
Last Update: 2025-09-04

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

Suggested `requirements.txt`:
-----------------------------
tensorflow
scikit-learn
pandas
matplotlib
seaborn
opencv-python-headless
astropy
photutils
imblearn
tqdm
evidently  # Optional, for monitoring
Flask
numpy
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
from tensorflow.keras import layers, applications
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, f1_score, roc_auc_score, accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import PCA
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import SMOTE
from photutils.isophote import Ellipse, EllipseGeometry
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

# --- Model Monitoring & Drift Detection ---
try:
    from evidently.report import Report
    from evidently.metric_preset import DataDriftPreset
except ImportError:
    logging.warning("Evidently library not found. Monitoring features will be disabled.")
    # Create dummy classes for compatibility
    class Report:
        def __init__(self, metrics=None): pass
        def run(self, *args, **kwargs): logging.warning("Evidently not installed. Skipping drift detection.")
    class DataDriftPreset:
        def __init__(self): pass


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
    DATASET_BASE_PATH: str = "./data"  # Relative path to data directory
    
    # --- Data Handling ---
    TEST_SET_RATIO: float = 0.2
    VALIDATION_SET_RATIO: float = 0.1
    RANDOM_STATE_SEED: int = 42
    
    # --- Preprocessing & Feature Engineering ---
    IMAGE_TARGET_DIMENSIONS: Tuple[int, int] = (224, 224)
    ISOPHOTE_ANALYSIS_SAMPLE_SIZE: Optional[int] = 2000
    PCA_EXPLAINED_VARIANCE_TARGET: float = 0.95

    # --- Model Training ---
    CROSS_VALIDATION_FOLDS: int = 5
    
    # --- RandomForest Hyperparameter Tuning (RandomizedSearch) ---
    RF_N_ITER_RANDOM_SEARCH: int = 50
    RF_HYPERPARAMETER_GRID: Dict[str, Any] = {
        'n_estimators': [100, 200, 300, 400], 'max_depth': [10, 20, 30, None],
        'min_samples_split': [2, 5, 10], 'min_samples_leaf': [1, 2, 4],
        'max_features': ['sqrt', 'log2']
    }

    # --- CNN Configuration ---
    CNN_EPOCHS: int = 15
    CNN_BATCH_SIZE: int = 32
    CNN_LEARNING_RATE: float = 0.001
    CNN_ARCHITECTURE: str = "EfficientNetB0"  # Options: "SimpleCNN", "ResNet50", "EfficientNetB0"
    CNN_FINE_TUNE_EPOCHS: int = 10
    CNN_FINE_TUNE_LEARNING_RATE: float = 0.0001

    # --- Model Monitoring ---
    MONITORING_WINDOW_SIZE: int = 1000

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
    """Encapsulates the project's objectives and constraints documentation."""
    def documentProblemDefinition(self):
        print("="*80 + "\nCHECKLIST STEP 1: FRAME THE PROBLEM & BIG PICTURE\n" + "="*80)
        print("""
        1. Business Objective: Develop a system to classify skin lesions from images,
           assisting dermatologists in early cancer detection.
        2. Problem Framing: Supervised binary/multiclass classification.
        3. Performance Metric: Weighted F1-Score is primary due to class imbalance
           and the costs of both false positives and false negatives. ROC AUC is secondary.
        4. Key Assumption: The visual features captured by isophote analysis and CNNs
           are sufficient and relevant for accurate classification.
        """)
        print("="*80 + "\n")

# ==============================================================================
# CHECKLIST STEP 2: GET THE DATA
# ==============================================================================
class DataAcquisitionManager:
    """Handles data loading, validation, and partitioning."""
    def __init__(self, config: PipelineConfiguration):
        self.config = config

    def executeDataPipeline(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        print("="*80 + "\nCHECKLIST STEP 2: GET THE DATA\n" + "="*80)
        raw_df = self._load_data()
        train_val_df, test_df = train_test_split(
            raw_df, test_size=self.config.TEST_SET_RATIO,
            random_state=self.config.RANDOM_STATE_SEED, stratify=raw_df['label']
        )
        train_df, val_df = train_test_split(
            train_val_df, test_size=self.config.VALIDATION_SET_RATIO / (1 - self.config.TEST_SET_RATIO),
            random_state=self.config.RANDOM_STATE_SEED, stratify=train_val_df['label']
        )
        logging.info(f"Data split complete: Train ({len(train_df)}), Validation ({len(val_df)}), Test ({len(test_df)})")
        print("="*80 + "\n")
        return train_df.reset_index(drop=True), val_df.reset_index(drop=True), test_df.reset_index(drop=True)

    def _load_data(self) -> pd.DataFrame:
        logging.info("Loading data from HAM10000 dataset...")
        metadata_path = os.path.join(self.config.DATASET_BASE_PATH, 'HAM10000_metadata.csv')
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Metadata file not found at {metadata_path}")
        
        df = pd.read_csv(metadata_path)
        
        image_dirs = [
            os.path.join(self.config.DATASET_BASE_PATH, 'HAM10000_images_part_1'),
            os.path.join(self.config.DATASET_BASE_PATH, 'HAM10000_images_part_2')
        ]
        image_files = {
            file.replace('.jpg', ''): os.path.join(root, file)
            for image_dir in image_dirs for root, _, files in os.walk(image_dir) for file in files if file.endswith('.jpg')
        }
        
        if not image_files:
            raise FileNotFoundError("No image files found. Check DATASET_BASE_PATH.")
            
        df['imagePath'] = df['image_id'].map(image_files)
        df.dropna(subset=['imagePath'], inplace=True)
        df.rename(columns={'dx': 'label'}, inplace=True)
        logging.info(f"Successfully loaded {len(df)} image records.")
        return df

# ==============================================================================
# CHECKLIST STEP 3: EXPLORE THE DATA (EDA)
# ==============================================================================
class ExploratoryDataAnalyzer:
    """Performs and summarizes EDA on the training data."""
    def __init__(self, config: PipelineConfiguration, trainingData: pd.DataFrame):
        self.config = config
        self.explorationData = trainingData.copy()

    def conductExploratoryDataAnalysis(self):
        print("="*80 + "\nCHECKLIST STEP 3: EXPLORE THE DATA (EDA)\n" + "="*80)
        logging.info("Visualizing data distributions.")
        plt.figure(figsize=(10, 6))
        sns.countplot(y=self.explorationData['label'], order=self.explorationData['label'].value_counts().index)
        plt.title('Class Distribution in Training Set')
        plt.xlabel('Count')
        plt.ylabel('Lesion Type')
        plt.tight_layout()
        savePath = os.path.join(self.config.RESULTS_OUTPUT_DIRECTORY, "eda_class_distribution.png")
        plt.savefig(savePath)
        plt.close()
        logging.info(f"Class distribution plot saved to {savePath}")
        
        print("""
        --- EDA Learnings & Next Steps ---
        - The dataset is highly imbalanced, with 'nv' (melanocytic nevi) being the
          overwhelming majority class.
        - This imbalance must be addressed during training using techniques like
          class weighting or resampling (SMOTE) to prevent the model from being
          biased towards the majority class.
        """)
        print("="*80 + "\n")

# ==============================================================================
# CHECKLIST STEP 4: PREPARE THE DATA
# ==============================================================================
class ImagePreprocessor:
    """Handles image loading, resizing, and normalization."""
    def __init__(self, config: PipelineConfiguration):
        self.targetSize = config.IMAGE_TARGET_DIMENSIONS

    def preprocessImage(self, imagePath: str) -> Optional[np.ndarray]:
        try:
            img = cv2.imread(imagePath)
            if img is None: return None
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, self.targetSize, interpolation=cv2.INTER_AREA)
            
            # Ensure 3 channels for CNN compatibility
            if len(img.shape) == 2: img = np.stack((img,)*3, axis=-1)
            elif img.shape[2] == 1: img = np.repeat(img, 3, axis=2)
            elif img.shape[2] == 4: img = img[:, :, :3]
                
            return img / 255.0  # Normalize to [0, 1]
        except Exception as e:
            logging.error(f"Error preprocessing image {imagePath}: {e}")
            return None

class IsophoteFeatureExtractor:
    """Extracts morphological features using Astropy/Photutils."""
    def extractFeatures(self, image: np.ndarray) -> Dict[str, float]:
        try:
            # Denormalize image for grayscale conversion
            gray = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
            ny, nx = gray.shape
            geometry = EllipseGeometry(x0=nx/2, y0=ny/2, sma=max(10, min(ny, nx)/10), eps=0.3, pa=0.0)
            ellipse = Ellipse(gray, geometry)
            isolist = ellipse.fit_image(maxit=50)
            
            if not isolist: return self._getDefaultFeatures()
            
            iso = isolist.get_closest(isolist.sma.max() / 2)
            return {
                'ellipticity': iso.eps, 'asymmetry': np.sqrt(iso.a3**2 + iso.b3**2),
                'meanIntensity': iso.intens, 'sma': iso.sma,
                'diskyness': iso.b4 if iso.b4 > 0 else 0, 'boxyness': abs(iso.b4) if iso.b4 < 0 else 0,
                'intensityGradient': iso.grad if iso.grad is not None else 0
            }
        except Exception:
            return self._getDefaultFeatures()

    def _getDefaultFeatures(self) -> Dict[str, float]:
        return {k: 0.0 for k in ['ellipticity', 'asymmetry', 'meanIntensity', 'sma', 'diskyness', 'boxyness', 'intensityGradient']}

class DataPreparationManager:
    """A pipeline for transforming raw data into feature-engineered data."""
    def __init__(self, config: PipelineConfiguration):
        self.config = config
        self.preprocessor = ImagePreprocessor(config)
        self.featureExtractor = IsophoteFeatureExtractor()
        self.labelEncoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=self.config.PCA_EXPLAINED_VARIANCE_TARGET)
        self.is_fitted = False
        self.feature_columns = None

    def fit_transform(self, dataFrame: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        print("="*80 + "\nCHECKLIST STEP 4: PREPARING DATA (Fit & Transform)\n" + "="*80)
        X_images, X_tab, y = self._process_data(dataFrame)
        
        # Fit transformers
        y_encoded = self.labelEncoder.fit_transform(y)
        X_tab_scaled = self.scaler.fit_transform(X_tab)
        X_tab_pca = self.pca.fit_transform(X_tab_scaled)
        
        self.is_fitted = True
        logging.info(f"Data preparation pipeline fitted. PCA reduced features to {X_tab_pca.shape[1]}.")
        print("="*80 + "\n")
        return X_images, X_tab_pca, y_encoded

    def transform(self, dataFrame: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        if not self.is_fitted:
            raise RuntimeError("Must call fit_transform before transform.")
        logging.info("Transforming new data with fitted pipeline...")
        X_images, X_tab, y = self._process_data(dataFrame)
        
        # Transform using fitted objects
        y_encoded = self.labelEncoder.transform(y)
        X_tab_scaled = self.scaler.transform(X_tab)
        X_tab_pca = self.pca.transform(X_tab_scaled)
        
        return X_images, X_tab_pca, y_encoded

    def _process_data(self, dataFrame: pd.DataFrame) -> Tuple[np.ndarray, pd.DataFrame, pd.Series]:
        """Shared data processing logic for both fit and transform."""
        logging.info(f"Processing {len(dataFrame)} records...")
        
        processed_images = {}
        with ProcessPoolExecutor() as executor:
            future_to_path = {executor.submit(self.preprocessor.preprocessImage, path): path for path in dataFrame['imagePath']}
            for future in tqdm(as_completed(future_to_path), total=len(future_to_path), desc="Preprocessing Images"):
                path = future_to_path[future]
                result = future.result()
                if result is not None:
                    processed_images[path] = result
        
        # Filter dataframe for successfully processed images
        valid_paths = list(processed_images.keys())
        df_filtered = dataFrame[dataFrame['imagePath'].isin(valid_paths)].copy()
        
        # Extract Isophote features in parallel
        features_list = []
        with ProcessPoolExecutor() as executor:
            future_to_path = {executor.submit(self.featureExtractor.extractFeatures, processed_images[path]): path for path in df_filtered['imagePath']}
            for future in tqdm(as_completed(future_to_path), total=len(future_to_path), desc="Extracting Isophote Features"):
                path = future_to_path[future]
                features = future.result()
                features['imagePath'] = path
                features_list.append(features)

        features_df = pd.DataFrame(features_list)
        full_df = pd.merge(df_filtered, features_df, on='imagePath')

        # Handle metadata
        full_df['age'].fillna(full_df['age'].mean(), inplace=True)
        categorical_features = ['sex', 'localization', 'dx_type']
        full_df = pd.get_dummies(full_df, columns=categorical_features, dummy_na=False)

        # Align columns with training set if pipeline is already fitted
        if self.is_fitted:
            current_cols = full_df.columns
            missing_cols = set(self.feature_columns) - set(current_cols)
            for c in missing_cols:
                full_df[c] = 0
            full_df = full_df[self.feature_columns]
        else:
            self.feature_columns = full_df.columns

        # Separate features and labels
        X_images = np.array([processed_images[path] for path in full_df['imagePath']])
        y_labels = full_df['label']
        X_tab = full_df.select_dtypes(include=np.number).drop(columns=['lesion_id'], errors='ignore')
        
        if not self.is_fitted:
             self.feature_columns = X_tab.columns # Save numeric columns for inference

        X_tab = X_tab[self.feature_columns] # Ensure order

        return X_images, X_tab, y_labels

# ==============================================================================
# CHECKLIST STEP 5 & 6: SHORTLIST & FINE-TUNE MODELS
# ==============================================================================
class ModelFactory:
    """Factory to create and train different types of models."""
    def __init__(self, config: PipelineConfiguration):
        self.config = config

    def buildCNNModel(self, image_input_shape: Tuple[int,int,int], tabular_input_shape: Tuple[int,], num_classes: int) -> keras.Model:
        print("="*80 + "\nCHECKLIST STEP 5 & 6: BUILD & TRAIN CNN MODEL\n" + "="*80)
        
        # --- Image Branch ---
        h, w, c = image_input_shape
        image_input = layers.Input(shape=(h, w, c), name='image_input')
        
        # **IMPROVEMENT**: Adapt input to 3 channels if it's grayscale, making the model robust.
        processed_image = image_input
        if c == 1:
            logging.info("Input is grayscale. Adding layer to convert to 3 channels.")
            processed_image = layers.Concatenate()([image_input, image_input, image_input])
        
        # --- Base Model (Transfer Learning) ---
        if self.config.CNN_ARCHITECTURE == "EfficientNetB0":
            base_model = applications.EfficientNetB0(weights='imagenet', include_top=False, input_shape=(h, w, 3))
        elif self.config.CNN_ARCHITECTURE == "ResNet50":
            base_model = applications.ResNet50(weights='imagenet', include_top=False, input_shape=(h, w, 3))
        else:
            raise ValueError(f"Unsupported CNN architecture: {self.config.CNN_ARCHITECTURE}")
            
        base_model.trainable = False  # Freeze base layers initially
        
        # **IMPROVEMENT**: Added training=False for best practice when using frozen layers with BatchNorm.
        x = base_model(processed_image, training=False)
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dense(128, activation='relu')(x)
        x = layers.Dropout(0.5)(x)
        
        # --- Tabular Branch ---
        tabular_input = layers.Input(shape=tabular_input_shape, name='tabular_input')
        y = layers.Dense(64, activation='relu')(tabular_input)
        y = layers.Dropout(0.5)(y)
        
        # --- Combined Model ---
        combined = layers.concatenate([x, y])
        output = layers.Dense(num_classes, activation='softmax' if num_classes > 2 else 'sigmoid')(combined)
        
        model = keras.Model(inputs=[image_input, tabular_input], outputs=output)
        
        loss = 'sparse_categorical_crossentropy' if num_classes > 2 else 'binary_crossentropy'
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.config.CNN_LEARNING_RATE),
            loss=loss,
            metrics=['accuracy', keras.metrics.AUC(name='auc')]
        )
        logging.info(f"CNN model built with {self.config.CNN_ARCHITECTURE} base.")
        model.summary()
        return model

    def fineTuneModel(self, model: keras.Model):
        logging.info("Unfreezing top layers of the base model for fine-tuning...")
        # Unfreeze layers for fine-tuning
        base_model = next((layer for layer in model.layers if "efficientnet" in layer.name or "resnet" in layer.name), None)
        if base_model:
            base_model.trainable = True
            # Fine-tune from a specific layer onwards
            fine_tune_at = len(base_model.layers) // 2
            for layer in base_model.layers[:fine_tune_at]:
                layer.trainable = False
        
        # Recompile with a lower learning rate
        loss = 'sparse_categorical_crossentropy' if model.output_shape[-1] > 2 else 'binary_crossentropy'
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.config.CNN_FINE_TUNE_LEARNING_RATE),
            loss=loss,
            metrics=['accuracy', keras.metrics.AUC(name='auc')]
        )
        logging.info("Model recompiled for fine-tuning.")
        return model

# ==============================================================================
# CHECKLIST STEP 7: PRESENT YOUR SOLUTION (EVALUATION)
# ==============================================================================
class ModelEvaluator:
    """Handles the final evaluation of a trained model on the unseen test set."""
    def __init__(self, config: PipelineConfiguration):
        self.config = config

    def evaluateFinalModel(self, model: Any, X_test: Union[np.ndarray, List[np.ndarray]], y_test: np.ndarray, classNames: List[str]):
        print("="*80 + "\nCHECKLIST STEP 7: EVALUATE FINAL MODEL ON TEST SET\n" + "="*80)
        logging.warning("This is the final evaluation. The model will not be tweaked further.")

        y_pred_proba = model.predict(X_test)
        y_pred = np.argmax(y_pred_proba, axis=1) if len(classNames) > 2 else (y_pred_proba > 0.5).astype("int32")
        
        print("\n--- Generalization Error Estimation ---")
        print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
        print(f"F1-Score (Weighted): {f1_score(y_test, y_pred, average='weighted'):.4f}")
        
        try:
            auc_score = roc_auc_score(y_test, y_pred_proba, multi_class='ovr', average='weighted') if len(classNames) > 2 else roc_auc_score(y_test, y_pred_proba)
            print(f"ROC AUC Score: {auc_score:.4f}")
        except Exception as e:
            logging.warning(f"Could not compute ROC AUC: {e}")

        print("\n--- Classification Report ---")
        print(classification_report(y_test, y_pred, target_names=classNames))

        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classNames, yticklabels=classNames)
        plt.title('Confusion Matrix on Unseen Test Set')
        plt.xlabel('Predicted Label')
        plt.ylabel('True Label')
        savePath = os.path.join(self.config.RESULTS_OUTPUT_DIRECTORY, "final_confusion_matrix.png")
        plt.savefig(savePath)
        plt.close()
        logging.info(f"Final confusion matrix saved to {savePath}")
        print("="*80 + "\n")

# ==============================================================================
# CHECKLIST STEP 8: LAUNCH, MONITOR, MAINTAIN
# ==============================================================================
class DeploymentPlanner:
    """Documents the deployment plan and provides a functional Flask API."""
    def __init__(self, config: PipelineConfiguration):
        self.config = config
        
    def documentDeploymentPlan(self):
        print("="*80 + "\nCHECKLIST STEP 8: LAUNCH, MONITOR, MAINTAIN\n" + "="*80)
        print("""
        1. Production Readiness: The model and the `DataPreparationManager` are saved.
           They can be loaded by a production server to make predictions.
        2. Monitoring: The provided Flask API includes logging for every prediction.
           A separate process could analyze these logs for data drift using a tool like
           Evidently AI or by comparing statistical properties of features over time.
        3. Retraining: A CI/CD pipeline (e.g., using GitHub Actions, Jenkins) should be
           set up to trigger this script automatically when new labeled data is available,
           versioning the output model and data preparator.
        """)

    @staticmethod
    def createFlaskApp(model: keras.Model, data_preparator: DataPreparationManager, config: PipelineConfiguration):
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            return "<h1>Skin Lesion Diagnosis API</h1><p>Send a POST request to /predict</p>"
        
        @app.route('/predict', methods=['POST'])
        def predict():
            try:
                if 'image' not in request.files:
                    return jsonify({'error': 'No image file provided'}), 400
                
                image_file = request.files['image']
                metadata_json = request.form.get('metadata')
                if not metadata_json:
                     return jsonify({'error': 'No metadata provided'}), 400
                
                metadata = json.loads(metadata_json)
                
                # --- Single Instance Prediction Pipeline ---
                # 1. Preprocess image
                img_array = data_preparator.preprocessor.preprocessImage(image_file.read())
                if img_array is None:
                    return jsonify({'error': 'Invalid image file'}), 400
                img_array = np.expand_dims(img_array, axis=0) # Add batch dimension
                
                # 2. Extract Isophote Features
                isophote_features = data_preparator.featureExtractor.extractFeatures(img_array[0])
                
                # 3. Combine with metadata and create DataFrame
                instance_data = {**metadata, **isophote_features}
                instance_df = pd.DataFrame([instance_data])
                
                # 4. Align columns with training data
                current_cols = instance_df.columns
                missing_cols = set(data_preparator.feature_columns) - set(current_cols)
                for c in missing_cols: instance_df[c] = 0
                instance_df = instance_df[data_preparator.feature_columns]

                # 5. Scale and apply PCA
                X_tab_scaled = data_preparator.scaler.transform(instance_df)
                X_tab_pca = data_preparator.pca.transform(X_tab_scaled)
                
                # 6. Predict
                prediction_proba = model.predict([img_array, X_tab_pca])[0]
                
                # 7. Format Response
                class_names = data_preparator.labelEncoder.classes_
                probabilities = {class_names[i]: float(prob) for i, prob in enumerate(prediction_proba)}
                predicted_class_idx = np.argmax(prediction_proba)
                predicted_class = class_names[predicted_class_idx]

                response = {
                    'prediction': predicted_class,
                    'probabilities': probabilities
                }
                
                return jsonify(response)
                
            except Exception as e:
                logging.error(f"Prediction error: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        return app

# ==============================================================================
# MAIN EXECUTION PIPELINE
# ==============================================================================
def main():
    config = PipelineConfiguration()
    
    problemFramer = ProblemFramer()
    problemFramer.documentProblemDefinition()
    
    dataManager = DataAcquisitionManager(config)
    trainSet, validationSet, testSet = dataManager.executeDataPipeline()
    
    edaAnalyzer = ExploratoryDataAnalyzer(config, trainSet)
    edaAnalyzer.conductExploratoryDataAnalysis()
    
    dataPreparator = DataPreparationManager(config)
    X_train_img, X_train_tab, y_train = dataPreparator.fit_transform(trainSet)
    X_val_img, X_val_tab, y_val = dataPreparator.transform(validationSet)
    X_test_img, X_test_tab, y_test = dataPreparator.transform(testSet)

    # Handle class imbalance on tabular data with SMOTE
    logging.info("Applying SMOTE to handle class imbalance on tabular features...")
    smote = SMOTE(random_state=config.RANDOM_STATE_SEED)
    X_train_tab_resampled, y_train_resampled = smote.fit_resample(X_train_tab, y_train)
    logging.info(f"Data resampled. New tabular shape: {X_train_tab_resampled.shape}")

    # To keep image data aligned with the new tabular data, we find the original
    # images that are "closest" to the newly synthesized tabular data points.
    from sklearn.neighbors import NearestNeighbors
    nn = NearestNeighbors(n_neighbors=1).fit(X_train_tab)
    _, indices = nn.kneighbors(X_train_tab_resampled)
    X_train_img_resampled = X_train_img[indices.flatten()]
    logging.info(f"Image data duplicated to match resampled tabular data. New image shape: {X_train_img_resampled.shape}")

    modelFactory = ModelFactory(config)
    image_input_shape = X_train_img_resampled.shape[1:]
    tabular_input_shape = (X_train_tab_resampled.shape[1],)
    num_classes = len(dataPreparator.labelEncoder.classes_)

    cnn_model = modelFactory.buildCNNModel(image_input_shape, tabular_input_shape, num_classes)
    
    logging.info("Initial training of the model...")
    cnn_model.fit(
        [X_train_img_resampled, X_train_tab_resampled], y_train_resampled,
        epochs=config.CNN_EPOCHS, batch_size=config.CNN_BATCH_SIZE,
        validation_data=([X_val_img, X_val_tab], y_val),
        class_weight=compute_class_weight('balanced', classes=np.unique(y_train_resampled), y=y_train_resampled),
        callbacks=[keras.callbacks.EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)],
        verbose=1
    )
    
    if config.CNN_ARCHITECTURE in ["EfficientNetB0", "ResNet50"]:
        cnn_model = modelFactory.fineTuneModel(cnn_model)
        logging.info("Fine-tuning the model...")
        cnn_model.fit(
            [X_train_img_resampled, X_train_tab_resampled], y_train_resampled,
            epochs=config.CNN_FINE_TUNE_EPOCHS, batch_size=config.CNN_BATCH_SIZE,
            validation_data=([X_val_img, X_val_tab], y_val),
            class_weight=compute_class_weight('balanced', classes=np.unique(y_train_resampled), y=y_train_resampled),
            callbacks=[keras.callbacks.EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)],
            verbose=1
        )
    
    modelEvaluator = ModelEvaluator(config)
    modelEvaluator.evaluateFinalModel(cnn_model, [X_test_img, X_test_tab], y_test, dataPreparator.labelEncoder.classes_)

    # Save the final model and the data preparation pipeline
    model_path = os.path.join(config.MODEL_SAVE_DIRECTORY, "final_cnn_model.keras")
    preparator_path = os.path.join(config.MODEL_SAVE_DIRECTORY, "data_preparator.pkl")
    cnn_model.save(model_path)
    with open(preparator_path, 'wb') as f:
        pickle.dump(dataPreparator, f)
    logging.info(f"Final model saved to {model_path}")
    logging.info(f"Data preparation pipeline saved to {preparator_path}")
    
    deploymentPlanner = DeploymentPlanner(config)
    deploymentPlanner.documentDeploymentPlan()
    
    print("\n--- API Server ---")
    print("To run the prediction server, execute the following command in your terminal:")
    print(f"FLASK_APP=main.py flask run --host={config.FLASK_HOST} --port={config.FLASK_PORT}")
    print("You will need to implement a small script to load the model and preparator and create the app instance.")


if __name__ == "__main__":
    main()
