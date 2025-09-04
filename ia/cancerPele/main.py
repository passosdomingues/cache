# -*- coding: utf-8 -*-
"""
================================================================================
End-to-End Skin Lesion Diagnosis Pipeline (Professional & Optimized Workflow)
================================================================================
Author: Rafael Passos Domingues
Last Update: 2025-09-04

Description:
This script implements a comprehensive, robust, and memory-efficient Machine
Learning pipeline for classifying skin lesions. It is specifically optimized
to handle large datasets (>10,000 images) without crashing by leveraging
batch processing and data generators.

The original script's primary issue was loading the entire image dataset into
RAM, leading to memory exhaustion. This revised version solves this by:
1.  **Pre-computing Features:** Performing the computationally expensive isophote
    feature extraction once, in parallel, and saving the results.
2.  **Using a Keras Data Generator:** A custom `HybridDataGenerator` class
    (inheriting from `keras.utils.Sequence`) reads and processes only one
    batch of data from disk at a time, keeping memory usage low and constant.
3.  **Efficient Class Imbalance Handling:** Eliminating the memory-intensive
    SMOTE + image duplication strategy in favor of the `class_weight`
    parameter in `model.fit`, which is highly memory-efficient.

The architecture remains modular and object-oriented, following a professional
data science workflow from data acquisition to deployment considerations.

Key Features:
- Memory-efficient design using data generators for out-of-core training.
- Concurrent, batched feature extraction to handle large-scale datasets.
- Advanced Object-Oriented design with clear separation of concerns.
- Hybrid modeling: A CNN fed by both image data and pre-computed
  tabular features (metadata + isophote analysis).
- Robust evaluation with detailed metrics and confusion matrices.
- Production-ready REST API stub with Flask.
- Comprehensive logging, serialization, and detailed in-code documentation.

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
tqdm
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
from math import ceil

# --- Machine Learning & Image Processing Libraries ---
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, applications, utils
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, f1_score, roc_auc_score, accuracy_score
from sklearn.decomposition import PCA
from sklearn.utils.class_weight import compute_class_weight
from photutils.isophote import Ellipse, EllipseGeometry
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

# --- Web Framework ---
from flask import Flask, request, jsonify

# ==============================================================================
# 0. GLOBAL CONFIGURATION AND SETUP
# ==============================================================================
class PipelineConfiguration:
    """
    Centralized configuration hub for the entire ML pipeline.
    Encapsulates all hyperparameters, paths, and settings for easy management.
    """
    # --- Data & File Paths ---
    DATASET_BASE_PATH: str = "./data"
    FEATURE_ENGINEERED_DATA_PATH: str = "./data/features_engineered.csv" # Path for pre-computed features
    RESULTS_OUTPUT_DIRECTORY: str = "pipeline_results"
    MODEL_SAVE_DIRECTORY: str = "saved_models"

    # --- Data Handling & Splitting ---
    TEST_SET_RATIO: float = 0.2
    VALIDATION_SET_RATIO: float = 0.1
    RANDOM_STATE_SEED: int = 42

    # --- Preprocessing & Feature Engineering ---
    IMAGE_TARGET_DIMENSIONS: Tuple[int, int] = (224, 224)
    PCA_EXPLAINED_VARIANCE_TARGET: float = 0.95
    FEATURE_EXTRACTION_BATCH_SIZE: int = 500 # How many images to process in a parallel batch

    # --- CNN Model Training ---
    CNN_EPOCHS: int = 15
    CNN_BATCH_SIZE: int = 32
    CNN_LEARNING_RATE: float = 0.001
    CNN_ARCHITECTURE: str = "ResNet50"  # Changed to ResNet50 to avoid EfficientNet issue

    # --- CNN Fine-Tuning ---
    ENABLE_FINE_TUNING: bool = True
    CNN_FINE_TUNE_EPOCHS: int = 10
    CNN_FINE_TUNE_LEARNING_RATE: float = 0.0001

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


# ==============================================================================
# CHECKLIST STEP 1: FRAME THE PROBLEM & BIG PICTURE
# ==============================================================================
class ProblemFramer:
    """
    Encapsulates the project's objectives and constraints documentation.
    This step clarifies the business goal and technical approach.
    """
    def document_problem_definition(self) -> None:
        """Prints a summary of the problem definition to the console."""
        print("="*80 + "\nCHECKLIST STEP 1: FRAME THE PROBLEM & BIG PICTURE\n" + "="*80)
        print("""
        1. Business Objective: Develop a system to classify skin lesions from images,
           assisting dermatologists in early cancer detection. The primary goal is to
           increase accuracy and efficiency in diagnosis.
        2. Problem Framing: Supervised multi-class classification. The model will predict
           one of several lesion types from an input image and associated metadata.
        3. Performance Metric: Weighted F1-Score is the primary metric. This is crucial
           due to the severe class imbalance in the dataset. It provides a balance
           between precision and recall, accounting for the cost of both false
           positives and false negatives across different classes. ROC AUC is a
           valuable secondary metric.
        4. Key Assumption: The visual features captured by the CNN from images, combined
           with tabular features (patient metadata and morphological isophote data),
           provide a sufficiently rich signal for an accurate classification.
        """)
        print("="*80 + "\n")


# ==============================================================================
# CHECKLIST STEP 2: GET THE DATA
# ==============================================================================
class DataAcquisitionManager:
    """
    Handles the initial loading of metadata and validates the existence of
    the required data files and directories.
    """
    def __init__(self, config: PipelineConfiguration):
        """
        Initializes the manager with the pipeline configuration.

        Args:
            config (PipelineConfiguration): The global configuration object.
        """
        self.config = config

    def load_metadata(self) -> pd.DataFrame:
        """
        Loads the HAM10000 metadata, maps it to the image file paths, and
        returns a consolidated DataFrame.

        Returns:
            pd.DataFrame: A DataFrame containing the lesion metadata and the
                          full path to each corresponding image file.

        Raises:
            FileNotFoundError: If the metadata CSV or image directories are not found.
        """
        print("="*80 + "\nCHECKLIST STEP 2: GET THE DATA\n" + "="*80)
        logging.info("Loading data from HAM10000 dataset...")

        metadata_path = os.path.join(self.config.DATASET_BASE_PATH, 'HAM10000_metadata.csv')
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Metadata file not found at {metadata_path}")

        df = pd.read_csv(metadata_path)

        # Create a dictionary mapping image_id to its full file path for quick lookup
        image_dirs = [
            os.path.join(self.config.DATASET_BASE_PATH, 'HAM10000_images_part_1'),
            os.path.join(self.config.DATASET_BASE_PATH, 'HAM10000_images_part_2')
        ]
        image_files = {
            file.replace('.jpg', ''): os.path.join(root, file)
            for image_dir in image_dirs for root, _, files in os.walk(image_dir) for file in files if file.endswith('.jpg')
        }

        if not image_files:
            raise FileNotFoundError(f"No image files found. Check DATASET_BASE_PATH: {self.config.DATASET_BASE_PATH}")

        # Map the file paths to the dataframe and clean up
        df['imagePath'] = df['image_id'].map(image_files)
        df.dropna(subset=['imagePath'], inplace=True)
        df.rename(columns={'dx': 'label'}, inplace=True)
        logging.info(f"Successfully loaded metadata for {len(df)} image records.")
        print("="*80 + "\n")
        return df


# ==============================================================================
# CHECKLIST STEP 3: EXPLORE THE DATA (EDA)
# ==============================================================================
class ExploratoryDataAnalyzer:
    """
    Performs and summarizes Exploratory Data Analysis (EDA) on the dataset.
    This helps in understanding data characteristics and planning modeling strategies.
    """
    def __init__(self, config: PipelineConfiguration):
        """
        Initializes the analyzer with the pipeline configuration.

        Args:
            config (PipelineConfiguration): The global configuration object.
        """
        self.config = config

    def conduct_eda(self, data: pd.DataFrame) -> None:
        """
        Conducts EDA on the provided data, focusing on class distribution.

        Args:
            data (pd.DataFrame): The DataFrame to analyze.
        """
        print("="*80 + "\nCHECKLIST STEP 3: EXPLORE THE DATA (EDA)\n" + "="*80)
        logging.info("Visualizing data distributions.")

        plt.figure(figsize=(12, 7))
        sns.countplot(y=data['label'], order=data['label'].value_counts().index)
        plt.title('Class Distribution in the Full Dataset')
        plt.xlabel('Count')
        plt.ylabel('Lesion Type')
        plt.tight_layout()
        save_path = os.path.join(self.config.RESULTS_OUTPUT_DIRECTORY, "eda_class_distribution.png")
        plt.savefig(save_path)
        plt.close()
        logging.info(f"Class distribution plot saved to {save_path}")

        print("""
        --- EDA Learnings & Next Steps ---
        - The dataset is highly imbalanced. 'nv' (melanocytic nevi) is the
          overwhelming majority class.
        - This imbalance is a critical issue. If not addressed, the model will be
          heavily biased towards predicting the majority class, leading to poor
          performance on rare but clinically important lesion types.
        - Strategy: We will address this using the `class_weight` argument during
          model training. This technique adjusts the loss function to penalize
          misclassifications of minority classes more heavily, without creating
          synthetic data or duplicating images in memory.
        """)
        print("="*80 + "\n")

# ==============================================================================
# CHECKLIST STEP 4: PREPARE THE DATA (FEATURE EXTRACTION & TRANSFORMATION)
# ==============================================================================
class ImagePreprocessor:
    """Handles image loading, resizing, and normalization."""
    def __init__(self, target_size: Tuple[int, int]):
        """
        Args:
            target_size (Tuple[int, int]): The desired (height, width) for the images.
        """
        self.target_size = target_size

    def preprocess_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Reads an image file, decodes it, resizes, and normalizes it.

        Args:
            image_path (str): The full path to the image file.

        Returns:
            Optional[np.ndarray]: The preprocessed image as a NumPy array in the
                                  range [0, 1], or None if an error occurs.
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                logging.warning(f"Could not read image: {image_path}")
                return None
            
            # Ensure image has 3 channels
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            else:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
            img = cv2.resize(img, self.target_size, interpolation=cv2.INTER_AREA)
            return img / 255.0  # Normalize to [0, 1]
        except Exception as e:
            logging.error(f"Error preprocessing image {image_path}: {e}")
            return None

class IsophoteFeatureExtractor:
    """
    Extracts morphological features from an image using isophote analysis
    from the Astropy/Photutils library. Isophotes are contours of constant
    brightness, and their shape characteristics (like ellipticity, asymmetry)
    can provide useful, quantifiable features for lesion analysis.
    """
    def extract_features(self, image: np.ndarray) -> Dict[str, float]:
        """
        Calculates isophotal features for a single image.

        Args:
            image (np.ndarray): A preprocessed image (normalized to [0, 1]).

        Returns:
            Dict[str, float]: A dictionary of extracted morphological features.
        """
        try:
            # Convert image to grayscale for isophote analysis
            gray_img = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
            ny, nx = gray_img.shape
            # Define an initial ellipse geometry at the center of the image
            geometry = EllipseGeometry(x0=nx/2, y0=ny/2, sma=max(10, min(ny, nx)/10), eps=0.3, pa=0.0)
            ellipse = Ellipse(gray_img, geometry)
            # Fit multiple isophotes to the image
            isolist = ellipse.fit_image(maxit=50)

            if not isolist or len(isolist) == 0:
                return self._get_default_features()

            # Analyze the isophote at half the maximum semi-major axis
            iso = isolist.get_closest(isolist.sma.max() / 2)
            if iso is None:
                return self._get_default_features()
                
            return {
                'ellipticity': iso.eps,
                'asymmetry': np.sqrt(iso.a3**2 + iso.b3**2) if iso.a3 is not None and iso.b3 is not None else 0.0,
                'mean_intensity': iso.intens,
                'sma': iso.sma,
                'diskyness': iso.b4 if iso.b4 is not None and iso.b4 > 0 else 0.0,
                'boxyness': abs(iso.b4) if iso.b4 is not None and iso.b4 < 0 else 0.0,
                'intensity_gradient': iso.grad if iso.grad is not None else 0.0
            }
        except Exception:
            # If isophote fitting fails, return default zero values
            return self._get_default_features()

    def _get_default_features(self) -> Dict[str, float]:
        """Returns a dictionary of zero-valued features for failed extractions."""
        return {k: 0.0 for k in ['ellipticity', 'asymmetry', 'mean_intensity', 'sma', 'diskyness', 'boxyness', 'intensity_gradient']}


class DataPreparationManager:
    """
    Orchestrates the entire data preparation pipeline, including:
    1.  One-time, concurrent extraction of isophote features.
    2.  Fitting of data transformers (Encoder, Scaler, PCA) on the training set.
    """
    def __init__(self, config: PipelineConfiguration):
        self.config = config
        self.preprocessor = ImagePreprocessor(config.IMAGE_TARGET_DIMENSIONS)
        self.feature_extractor = IsophoteFeatureExtractor()
        # Initialize transformers; they will be fitted later.
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=config.PCA_EXPLAINED_VARIANCE_TARGET)
        self.tabular_feature_columns = None # Will store the final column order

    def _process_single_image(self, image_path: str) -> Optional[Dict[str, Any]]:
        """Helper function to process one image and extract its features."""
        image_array = self.preprocessor.preprocess_image(image_path)
        if image_array is not None:
            return self.feature_extractor.extract_features(image_array)
        return None

    def extract_and_save_features(self, df: pd.DataFrame, output_path: str) -> pd.DataFrame:
        """
        Performs concurrent feature extraction on all images and saves the
        combined feature set to a CSV file.

        Args:
            df (pd.DataFrame): The initial dataframe with metadata and image paths.
            output_path (str): The path to save the resulting CSV file.

        Returns:
            pd.DataFrame: The dataframe enriched with isophote features.
        """
        print("="*80 + "\nCHECKLIST STEP 4: PREPARE THE DATA (Feature Extraction)\n" + "="*80)
        logging.info(f"Starting concurrent isophote feature extraction for {len(df)} images.")
        
        results = []
        with ProcessPoolExecutor() as executor:
            # Submit all image processing tasks to the pool
            future_to_path = {executor.submit(self._process_single_image, row.imagePath): row.image_id for _, row in df.iterrows()}
            
            # Collect results as they complete with a progress bar
            for future in tqdm(as_completed(future_to_path), total=len(df), desc="Extracting Isophote Features"):
                image_id = future_to_path[future]
                isophote_features = future.result()
                if isophote_features:
                    isophote_features['image_id'] = image_id
                    results.append(isophote_features)

        features_df = pd.DataFrame(results)
        logging.info(f"Successfully extracted features for {len(features_df)} images.")
        
        # Merge extracted features back with original metadata
        full_df = pd.merge(df, features_df, on='image_id')
        
        # Handle missing values and create dummy variables for categorical features
        full_df['age'].fillna(full_df['age'].median(), inplace=True)
        categorical_features = ['sex', 'localization', 'dx_type']
        full_df = pd.get_dummies(full_df, columns=categorical_features, dummy_na=False)

        full_df.to_csv(output_path, index=False)
        logging.info(f"Engineered features saved to {output_path}")
        print("="*80 + "\n")
        return full_df

    def fit_transformers(self, train_df: pd.DataFrame) -> None:
        """
        Fits the LabelEncoder, StandardScaler, and PCA on the training data.
        This ensures that transformations are learned only from the training set
        to prevent data leakage.

        Args:
            train_df (pd.DataFrame): The training portion of the feature-engineered data.
        """
        logging.info("Fitting data transformers (LabelEncoder, StandardScaler, PCA) on the training set.")
        
        # Fit LabelEncoder on the target variable
        y_train = self.label_encoder.fit_transform(train_df['label'])
        
        # Identify and store the columns for tabular data
        # Exclude identifiers, labels, and paths
        cols_to_exclude = ['image_id', 'lesion_id', 'imagePath', 'label']
        self.tabular_feature_columns = [
            col for col in train_df.columns if train_df[col].dtype in ['int64', 'float64', 'uint8'] and col not in cols_to_exclude
        ]
        
        X_train_tab = train_df[self.tabular_feature_columns].copy()
        
        # Fit StandardScaler and PCA
        X_train_scaled = self.scaler.fit_transform(X_train_tab)
        self.pca.fit(X_train_scaled)
        
        logging.info(f"Transformers fitted. PCA will reduce features to {self.pca.n_components_} components.")


# ==============================================================================
# DATA GENERATOR FOR MEMORY-EFFICIENT TRAINING
# ==============================================================================
class HybridDataGenerator(utils.Sequence):
    """
    A Keras Sequence generator that loads and processes data in batches from disk.
    This is essential for handling large datasets that do not fit into memory.
    """
    def __init__(self, df: pd.DataFrame, data_preparator: DataPreparationManager,
                 batch_size: int, is_training: bool = True):
        """
        Initializes the data generator.

        Args:
            df (pd.DataFrame): The dataframe partition (train, val, or test) to generate batches from.
            data_preparator (DataPreparationManager): The fitted data preparation manager,
                                                     containing the transformers.
            batch_size (int): The number of samples per batch.
            is_training (bool): If True, the generator will shuffle data at the end of each epoch.
        """
        self.df = df
        self.preparator = data_preparator
        self.batch_size = batch_size
        self.is_training = is_training
        self.image_preprocessor = ImagePreprocessor(data_preparator.config.IMAGE_TARGET_DIMENSIONS)
        self.tabular_cols = self.preparator.tabular_feature_columns
        self.n_classes = len(self.preparator.label_encoder.classes_)
        self.indexes = np.arange(len(self.df))  # Use integer indices for shuffling
        self.on_epoch_end()

    def __len__(self) -> int:
        """Returns the number of batches per epoch."""
        return ceil(len(self.df) / self.batch_size)

    def __getitem__(self, index: int) -> Tuple[List[np.ndarray], np.ndarray]:
        """
        Generates one batch of data.

        Args:
            index (int): The index of the batch.

        Returns:
            Tuple[List[np.ndarray], np.ndarray]: A tuple containing the batch of
            inputs ([images, tabular_data]) and the batch of labels.
        """
        # Determine the rows for the current batch
        start_index = index * self.batch_size
        end_index = (index + 1) * self.batch_size
        batch_indexes = self.indexes[start_index:end_index]
        batch_df = self.df.iloc[batch_indexes]  # Use iloc for integer indexing
        
        # --- Prepare Image Data ---
        # Load, preprocess, and stack images for the batch
        batch_images = np.stack([
            self.image_preprocessor.preprocess_image(fp)
            for fp in batch_df['imagePath']
            if self.image_preprocessor.preprocess_image(fp) is not None
        ])

        # --- Prepare Tabular Data ---
        # Ensure correct column order, then scale and apply PCA
        X_tab = batch_df[self.tabular_cols]
        X_tab_scaled = self.preparator.scaler.transform(X_tab)
        X_tab_pca = self.preparator.pca.transform(X_tab_scaled)
        
        # --- Prepare Labels ---
        # Transform labels to integer representation
        y = self.preparator.label_encoder.transform(batch_df['label'])

        return [batch_images, X_tab_pca], y

    def on_epoch_end(self) -> None:
        """
        Shuffles the data indices at the end of each epoch if in training mode.
        This helps the model generalize better.
        """
        if self.is_training:
            np.random.shuffle(self.indexes)


# ==============================================================================
# CHECKLIST STEP 5 & 6: SHORTLIST, BUILD & TRAIN MODELS
# ==============================================================================
class ModelFactory:
    """
    Factory to construct and compile the hybrid deep learning model.
    This architecture combines a Convolutional Neural Network (CNN) for image
    feature extraction with a Multi-Layer Perceptron (MLP) for tabular data.
    """
    def __init__(self, config: PipelineConfiguration):
        """
        Args:
            config (PipelineConfiguration): The global configuration object.
        """
        self.config = config

    def build_hybrid_cnn_model(self, image_input_shape: Tuple[int, int, int],
                             tabular_input_shape: Tuple[int,],
                             num_classes: int) -> keras.Model:
        """
        Constructs the hybrid model.

        Args:
            image_input_shape (Tuple): The shape of the input images (H, W, C).
            tabular_input_shape (Tuple): The shape of the input tabular data (num_features,).
            num_classes (int): The number of output classes for classification.

        Returns:
            keras.Model: The compiled, untrained Keras model.
        """
        print("="*80 + "\nCHECKLIST STEP 5 & 6: BUILD & TRAIN HYBRID CNN MODEL\n" + "="*80)
        
        # --- Image Branch (CNN) ---
        image_input = layers.Input(shape=image_input_shape, name='image_input')
        
        # Select the base CNN model for transfer learning
        if self.config.CNN_ARCHITECTURE == "EfficientNetB0":
            base_model = applications.EfficientNetB0(weights='imagenet', include_top=False, input_shape=image_input_shape)
        elif self.config.CNN_ARCHITECTURE == "ResNet50":
            base_model = applications.ResNet50(weights='imagenet', include_top=False, input_shape=image_input_shape)
        else:
            raise ValueError(f"Unsupported CNN architecture: {self.config.CNN_ARCHITECTURE}")
        
        base_model.trainable = False  # Freeze the base layers initially

        # Image feature processing layers
        x = base_model(image_input, training=False)
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dense(128, activation='relu')(x)
        x = layers.Dropout(0.5)(x)
        
        # --- Tabular Branch (MLP) ---
        tabular_input = layers.Input(shape=tabular_input_shape, name='tabular_input')
        y = layers.Dense(64, activation='relu')(tabular_input)
        y = layers.Dropout(0.3)(y)
        
        # --- Combined Model ---
        # Concatenate features from both branches
        combined = layers.concatenate([x, y])
        # Final output layer
        output = layers.Dense(num_classes, activation='softmax')(combined)
        
        model = keras.Model(inputs=[image_input, tabular_input], outputs=output)
        
        # Compile the model with optimizer, loss, and metrics
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.config.CNN_LEARNING_RATE),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy', keras.metrics.AUC(name='auc')]
        )
        logging.info(f"Hybrid CNN model built with {self.config.CNN_ARCHITECTURE} base.")
        model.summary()
        return model

    def fine_tune_model(self, model: keras.Model) -> keras.Model:
        """
        Unfreezes the top layers of the base CNN and recompiles the model with
        a lower learning rate for fine-tuning.

        Args:
            model (keras.Model): The model to be fine-tuned.

        Returns:
            keras.Model: The recompiled model, ready for fine-tuning.
        """
        logging.info("Unfreezing top layers of the base model for fine-tuning...")
        base_model = next((layer for layer in model.layers if "efficientnet" in layer.name or "resnet" in layer.name), None)
        if base_model:
            base_model.trainable = True
            # Fine-tune from the last third of the layers onwards
            fine_tune_at = len(base_model.layers) * 2 // 3
            for layer in base_model.layers[:fine_tune_at]:
                layer.trainable = False
        
        # Recompile with a lower learning rate for stable fine-tuning
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.config.CNN_FINE_TUNE_LEARNING_RATE),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy', keras.metrics.AUC(name='auc')]
        )
        logging.info(f"Model recompiled for fine-tuning with learning rate {self.config.CNN_FINE_TUNE_LEARNING_RATE}.")
        return model


# ==============================================================================
# CHECKLIST STEP 7: PRESENT YOUR SOLUTION (EVALUATION)
# ==============================================================================
class ModelEvaluator:
    """Handles the final evaluation of a trained model on the unseen test set."""
    def __init__(self, config: PipelineConfiguration):
        self.config = config

    def evaluate_final_model(self, model: keras.Model, test_generator: HybridDataGenerator, class_names: List[str]):
        """
        Evaluates the model on the test data generator, printing and plotting results.

        Args:
            model (keras.Model): The trained final model.
            test_generator (HybridDataGenerator): The data generator for the test set.
            class_names (List[str]): A list of class names for reporting.
        """
        print("="*80 + "\nCHECKLIST STEP 7: EVALUATE FINAL MODEL ON TEST SET\n" + "="*80)
        logging.warning("This is the final evaluation on unseen data. The model will not be tweaked further based on these results.")

        # Get predictions and true labels from the generator
        y_pred_proba = model.predict(test_generator, verbose=1)
        y_pred = np.argmax(y_pred_proba, axis=1)
        y_true = self.preparator.label_encoder.transform(test_generator.df['label'])

        print("\n--- Generalization Error Estimation ---")
        print(f"Accuracy: {accuracy_score(y_true, y_pred):.4f}")
        print(f"F1-Score (Weighted): {f1_score(y_true, y_pred, average='weighted'):.4f}")
        
        try:
            auc_score = roc_auc_score(y_true, y_pred_proba, multi_class='ovr', average='weighted')
            print(f"ROC AUC Score (Weighted OVR): {auc_score:.4f}")
        except Exception as e:
            logging.warning(f"Could not compute ROC AUC score: {e}")

        print("\n--- Classification Report ---")
        print(classification_report(y_true, y_pred, target_names=class_names))

        # Plot and save the confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        plt.figure(figsize=(12, 10))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
        plt.title('Confusion Matrix on Unseen Test Set')
        plt.xlabel('Predicted Label')
        plt.ylabel('True Label')
        save_path = os.path.join(self.config.RESULTS_OUTPUT_DIRECTORY, "final_confusion_matrix.png")
        plt.savefig(save_path)
        plt.close()
        logging.info(f"Final confusion matrix saved to {save_path}")
        print("="*80 + "\n")


# ==============================================================================
# CHECKLIST STEP 8: LAUNCH, MONITOR, MAINTAIN
# ==============================================================================
class DeploymentPlanner:
    """
    Documents the deployment plan and provides a functional Flask API for serving
    the model.
    """
    def __init__(self, config: PipelineConfiguration):
        self.config = config
        
    def document_deployment_plan(self):
        print("="*80 + "\nCHECKLIST STEP 8: LAUNCH, MONITOR, MAINTAIN\n" + "="*80)
        print("""
        1. Production Artifacts: The trained Keras model (`final_cnn_model.keras`) and
           the `DataPreparationManager` object (`data_preparator.pkl`) are the key
           artifacts. The preparator is crucial as it contains the fitted transformers
           (scaler, PCA, encoder) needed to process new data exactly as the training
           data was processed, preventing training-serving skew.
        2. Deployment API: A sample Flask API is provided. To deploy, this application
           can be containerized (e.g., using Docker) and hosted on a cloud service
           (like AWS, GCP, Azure) or an on-premise server using a production-grade
           WSGI server like Gunicorn or uWSGI.
        3. Monitoring Strategy:
           - Input Data Drift: Log incoming prediction requests (features and metadata).
             Periodically, compare the statistical distribution (mean, std, etc.) of
             new data against the training data distribution. Tools like Evidently AI
             or custom statistical tests can automate this.
           - Model Performance: If feedback (ground truth labels) becomes available,
             track performance metrics (F1, Accuracy) over time to detect model decay.
        4. Retraining Pipeline: A CI/CD pipeline (e.g., using GitHub Actions, Jenkins)
           should be established. This pipeline would trigger a full retraining run
           (executing this script) when significant data drift is detected or when a
           sufficient amount of new labeled data is collected.
        """)

    @staticmethod
    def create_flask_app(model: keras.Model, data_preparator: DataPreparationManager) -> Flask:
        """
        Creates and configures a Flask application to serve the model.
        
        Args:
            model (keras.Model): The trained Keras model.
            data_preparator (DataPreparationManager): The fitted data preparation manager.

        Returns:
            Flask: The configured Flask application instance.
        """
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            return "<h1>Skin Lesion Diagnosis API</h1><p>Send a POST request to /predict</p>"
        
        @app.route('/predict', methods=['POST'])
        def predict():
            try:
                if 'image' not in request.files:
                    return jsonify({'error': 'No image file provided'}), 400
                
                image_file = request.files['image'].read()
                metadata_json = request.form.get('metadata')
                if not metadata_json:
                     return jsonify({'error': 'No metadata provided'}), 400
                
                metadata = json.loads(metadata_json)
                
                # --- Single Instance Prediction Pipeline ---
                # 1. Preprocess image from bytes
                img_np = np.frombuffer(image_file, np.uint8)
                img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
                if img is None:
                    return jsonify({'error': 'Invalid image file format'}), 400
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img_resized = cv2.resize(img_rgb, data_preparator.config.IMAGE_TARGET_DIMENSIONS, interpolation=cv2.INTER_AREA)
                img_normalized = img_resized / 255.0
                
                # 2. Extract Isophote Features
                isophote_features = data_preparator.feature_extractor.extract_features(img_normalized)
                
                # 3. Combine with metadata into a DataFrame
                instance_data = {**metadata, **isophote_features}
                instance_df = pd.DataFrame([instance_data])
                
                # 4. Create dummy variables and align columns with training data
                instance_df = pd.get_dummies(instance_df)
                missing_cols = set(data_preparator.tabular_feature_columns) - set(instance_df.columns)
                for c in missing_cols:
                    instance_df[c] = 0
                instance_df = instance_df[data_preparator.tabular_feature_columns]

                # 5. Scale and apply PCA using the FITTED transformers
                X_tab_scaled = data_preparator.scaler.transform(instance_df)
                X_tab_pca = data_preparator.pca.transform(X_tab_scaled)
                
                # 6. Predict
                img_batch = np.expand_dims(img_normalized, axis=0) # Add batch dimension
                prediction_proba = model.predict([img_batch, X_tab_pca])[0]
                
                # 7. Format Response
                class_names = data_preparator.label_encoder.classes_
                probabilities = {class_names[i]: float(prob) for i, prob in enumerate(prediction_proba)}
                predicted_class_idx = np.argmax(prediction_proba)
                predicted_class = class_names[predicted_class_idx]

                response = {
                    'prediction': predicted_class,
                    'probabilities': probabilities
                }
                return jsonify(response)
                
            except Exception as e:
                logging.error(f"Prediction error: {e}", exc_info=True)
                return jsonify({'error': 'Internal server error during prediction'}), 500
        
        return app


# ==============================================================================
# MAIN EXECUTION PIPELINE
# ==============================================================================
def main():
    """The main function to execute the entire ML pipeline."""
    config = PipelineConfiguration()
    
    # --- Step 1: Frame the Problem ---
    problem_framer = ProblemFramer()
    problem_framer.document_problem_definition()
    
    # --- Step 2: Get Data ---
    data_manager = DataAcquisitionManager(config)
    raw_metadata_df = data_manager.load_metadata()
    
    # --- Step 3: EDA ---
    eda_analyzer = ExploratoryDataAnalyzer(config)
    eda_analyzer.conduct_eda(raw_metadata_df)
    
    # --- Step 4: Data Preparation ---
    data_preparator = DataPreparationManager(config)
    
    # This is the heavy, one-time feature extraction step.
    # If the feature file already exists, we can skip it.
    if os.path.exists(config.FEATURE_ENGINEERED_DATA_PATH):
        logging.info(f"Found existing feature file at {config.FEATURE_ENGINEERED_DATA_PATH}. Loading it.")
        features_df = pd.read_csv(config.FEATURE_ENGINEERED_DATA_PATH)
    else:
        features_df = data_preparator.extract_and_save_features(raw_metadata_df, config.FEATURE_ENGINEERED_DATA_PATH)

    # Split the data into training, validation, and test sets
    train_val_df, test_df = train_test_split(
        features_df, test_size=config.TEST_SET_RATIO,
        random_state=config.RANDOM_STATE_SEED, stratify=features_df['label']
    )
    train_df, val_df = train_test_split(
        train_val_df, test_size=config.VALIDATION_SET_RATIO / (1 - config.TEST_SET_RATIO),
        random_state=config.RANDOM_STATE_SEED, stratify=train_val_df['label']
    )
    logging.info(f"Data split complete: Train ({len(train_df)}), Validation ({len(val_df)}), Test ({len(test_df)})")

    # Fit the transformers ONLY on the training data
    data_preparator.fit_transformers(train_df)

    # --- Create Data Generators ---
    train_generator = HybridDataGenerator(train_df.reset_index(drop=True), data_preparator, config.CNN_BATCH_SIZE)
    val_generator = HybridDataGenerator(val_df.reset_index(drop=True), data_preparator, config.CNN_BATCH_SIZE, is_training=False)
    test_generator = HybridDataGenerator(test_df.reset_index(drop=True), data_preparator, config.CNN_BATCH_SIZE, is_training=False)

    # --- Step 5 & 6: Build and Train Model ---
    model_factory = ModelFactory(config)
    
    # Define model input shapes from configuration and fitted PCA
    image_shape = (*config.IMAGE_TARGET_DIMENSIONS, 3)
    tabular_shape = (data_preparator.pca.n_components_,)
    num_classes = len(data_preparator.label_encoder.classes_)

    cnn_model = model_factory.build_hybrid_cnn_model(image_shape, tabular_shape, num_classes)
    
    # Calculate class weights to handle imbalance
    class_weights = compute_class_weight(
        'balanced',
        classes=np.unique(data_preparator.label_encoder.transform(train_df['label'])),
        y=data_preparator.label_encoder.transform(train_df['label'])
    )
    class_weights_dict = dict(enumerate(class_weights))
    
    callbacks = [
        keras.callbacks.EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
    ]
    
    logging.info("Starting initial model training...")
    cnn_model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=config.CNN_EPOCHS,
        class_weight=class_weights_dict,
        callbacks=callbacks,
        verbose=1
    )
    
    if config.ENABLE_FINE_TUNING:
        cnn_model = model_factory.fine_tune_model(cnn_model)
        logging.info("Starting model fine-tuning...")
        cnn_model.fit(
            train_generator,
            validation_data=val_generator,
            epochs=config.CNN_FINE_TUNE_EPOCHS,
            class_weight=class_weights_dict,
            callbacks=callbacks,
            verbose=1
        )
    
    # --- Step 7: Evaluate Model ---
    model_evaluator = ModelEvaluator(config)
    model_evaluator.evaluate_final_model(cnn_model, test_generator, data_preparator.label_encoder.classes_)

    # --- Save Final Artifacts ---
    model_path = os.path.join(config.MODEL_SAVE_DIRECTORY, "final_cnn_model.keras")
    preparator_path = os.path.join(config.MODEL_SAVE_DIRECTORY, "data_preparator.pkl")
    cnn_model.save(model_path)
    with open(preparator_path, 'wb') as f:
        pickle.dump(data_preparator, f)
    logging.info(f"Final model saved to {model_path}")
    logging.info(f"Data preparation pipeline saved to {preparator_path}")
    
    # --- Step 8: Document Deployment ---
    deployment_planner = DeploymentPlanner(config)
    deployment_planner.document_deployment_plan()
    
    print("\n--- API Server Instructions ---")
    print("To run the prediction server, you need a separate script (e.g., `app.py`) that loads the artifacts and runs the Flask app.")
    print("Example `app.py`:")
    print("-----------------------------------")
    print("import pickle")
    print("from tensorflow import keras")
    print("from main import DeploymentPlanner, DataPreparationManager")
    print("")
    print("model = keras.models.load_model('saved_models/final_cnn_model.keras')")
    print("with open('saved_models/data_preparator.pkl', 'rb') as f:")
    print("    preparator = pickle.load(f)")
    print("")
    print("app = DeploymentPlanner.create_flask_app(model, preparator)")
    print("")
    print("if __name__ == '__main__':")
    print("    app.run(host='0.0.0.0', port=5000)")
    print("-----------------------------------")
    print("\nThen run from your terminal: python app.py")


if __name__ == "__main__":
    main()
