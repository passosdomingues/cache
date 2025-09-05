# -*- coding: utf-8 -*-
"""
================================================================================
ENHANCED ULTRA-ATOMIC SKIN LESION DIAGNOSIS PIPELINE
================================================================================
Author: Rafael Passos Domingues
Last Update: 2025-09-05

Enhancements:
- Two-stage cascading pipeline with recursive exclusion
- Focal loss with class balancing
- Advanced data augmentation
- Isophote maps as additional input channels
- Polar transformation for radial analysis
- Hard negative mining
- Clinical validation metrics
"""

# Add these imports at the top of your file
import albumentations as A
from albumentations.pytorch import ToTensorV2
from sklearn.metrics import precision_recall_curve, auc
from sklearn.calibration import calibration_curve
from skimage.transform import warp_polar
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from torch.optim.lr_scheduler import CosineAnnealingLR
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

# Add these classes and functions to your existing code

class FocalLoss(nn.Module):
    """Focal Loss for handling class imbalance"""
    def __init__(self, alpha=None, gamma=2.0, reduction='mean'):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, inputs, targets):
        ce_loss = nn.CrossEntropyLoss(reduction='none')(inputs, targets)
        pt = torch.exp(-ce_loss)
        focal_loss = (1 - pt) ** self.gamma * ce_loss
        
        if self.alpha is not None:
            alpha_weight = self.alpha[targets]
            focal_loss = alpha_weight * focal_loss
            
        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        return focal_loss

class SkinLesionDataset(Dataset):
    """Enhanced dataset with advanced transformations"""
    def __init__(self, df, config, is_training=True, is_melanoma_binary=False):
        self.df = df.reset_index(drop=True)
        self.config = config
        self.is_training = is_training
        self.is_melanoma_binary = is_melanoma_binary
        
        # Define augmentations
        if is_training:
            self.transform = A.Compose([
                A.HorizontalFlip(p=0.5),
                A.VerticalFlip(p=0.5),
                A.Rotate(limit=30, p=0.5),
                A.RandomBrightnessContrast(p=0.3),
                A.GaussNoise(p=0.2),
                A.CoarseDropout(max_holes=8, max_height=20, max_width=20, p=0.3),
                A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
                ToTensorV2()
            ])
        else:
            self.transform = A.Compose([
                A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
                ToTensorV2()
            ])
            
    def __len__(self):
        return len(self.df)
    
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        image_path = row['imagePath']
        
        # Load and preprocess image
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Apply transformations
        augmented = self.transform(image=image)
        image_tensor = augmented['image']
        
        # Generate isophote map
        isophote_map = self.generate_isophote_map(image)
        isophote_map = torch.from_numpy(isophote_map).float().unsqueeze(0)
        
        # Generate polar transformed image
        polar_image = self.generate_polar_image(image)
        polar_image = torch.from_numpy(polar_image).float()
        
        # Prepare label
        if self.is_melanoma_binary:
            label = 1 if row['label'] == 'mel' else 0
        else:
            label = self.config.label_encoder.transform([row['label']])[0]
            
        return {
            'image': image_tensor,
            'isophote_map': isophote_map,
            'polar_image': polar_image,
            'label': torch.tensor(label, dtype=torch.long),
            'metadata': torch.tensor(row[['age']].fillna(0).values.astype(np.float32))
        }
    
    def generate_isophote_map(self, image):
        """Generate isophote map from image"""
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        magnitude = np.sqrt(sobelx**2 + sobely**2)
        return (magnitude / magnitude.max() * 255).astype(np.uint8)
    
    def generate_polar_image(self, image, center=None):
        """Generate polar transformed image"""
        if center is None:
            center = (image.shape[1] // 2, image.shape[0] // 2)
        
        max_radius = min(center[0], center[1], image.shape[1]-center[0], image.shape[0]-center[1])
        polar = warp_polar(image, center=center, radius=max_radius, output_shape=(224, 224))
        return polar

class HybridLesionModel(nn.Module):
    """Enhanced hybrid model with multiple input branches"""
    def __init__(self, num_classes, use_metadata=True):
        super(HybridLesionModel, self).__init__()
        self.use_metadata = use_metadata
        
        # Image branch (EfficientNet)
        self.image_backbone = models.efficientnet_b0(pretrained=True)
        self.image_backbone.classifier = nn.Identity()
        
        # Isophote branch
        self.isophote_conv = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten()
        )
        
        # Polar branch
        self.polar_conv = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten()
        )
        
        # Metadata branch
        self.metadata_fc = nn.Sequential(
            nn.Linear(1, 16),
            nn.ReLU(),
            nn.Dropout(0.3)
        )
        
        # Combined classifier
        combined_features = 1280 + 64 + 64  # Image + Isophote + Polar
        if use_metadata:
            combined_features += 16
            
        self.classifier = nn.Sequential(
            nn.Linear(combined_features, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )
        
    def forward(self, x):
        image, isophote, polar, metadata = x
        
        # Image features
        image_features = self.image_backbone(image)
        
        # Isophote features
        isophote_features = self.isophote_conv(isophote)
        
        # Polar features
        polar_features = self.polar_conv(polar)
        
        # Metadata features
        if self.use_metadata:
            metadata_features = self.metadata_fc(metadata)
            combined = torch.cat([image_features, isophote_features, polar_features, metadata_features], dim=1)
        else:
            combined = torch.cat([image_features, isophote_features, polar_features], dim=1)
            
        return self.classifier(combined)

def train_first_stage(config, train_df, val_df):
    """First stage: Train multiclass model on all data"""
    logger.log_step("FIRST STAGE: TRAINING MULTICLASS MODEL")
    
    # Create datasets
    train_dataset = SkinLesionDataset(train_df, config, is_training=True)
    val_dataset = SkinLesionDataset(val_df, config, is_training=False)
    
    # Calculate class weights for focal loss
    class_counts = train_df['label'].value_counts().to_dict()
    total_samples = sum(class_counts.values())
    class_weights = {config.label_encoder.transform([k])[0]: total_samples/(len(class_counts)*v) 
                     for k, v in class_counts.items()}
    class_weights_tensor = torch.tensor([class_weights[i] for i in range(len(class_weights))])
    
    # Create weighted sampler
    labels = train_df['label'].map(lambda x: config.label_encoder.transform([x])[0]).values
    class_weights_all = [class_weights[label] for label in labels]
    sampler = WeightedRandomSampler(class_weights_all, len(class_weights_all))
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=config.BATCH_SIZE, 
                             sampler=sampler, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=config.BATCH_SIZE, 
                           shuffle=False, num_workers=4)
    
    # Initialize model
    model = HybridLesionModel(num_classes=len(config.label_encoder.classes_))
    model = model.to(config.DEVICE)
    
    # Loss and optimizer
    criterion = FocalLoss(alpha=class_weights_tensor.to(config.DEVICE), gamma=2.0)
    optimizer = torch.optim.Adam(model.parameters(), lr=config.LEARNING_RATE)
    scheduler = CosineAnnealingLR(optimizer, T_max=config.FIRST_STAGE_EPOCHS)
    
    # Training loop
    best_val_loss = float('inf')
    for epoch in range(config.FIRST_STAGE_EPOCHS):
        model.train()
        train_loss = 0
        
        for batch in tqdm(train_loader, desc=f"Epoch {epoch+1}/{config.FIRST_STAGE_EPOCHS}"):
            images = batch['image'].to(config.DEVICE)
            isophotes = batch['isophote_map'].to(config.DEVICE)
            polars = batch['polar_image'].to(config.DEVICE)
            metadata = batch['metadata'].to(config.DEVICE)
            labels = batch['label'].to(config.DEVICE)
            
            optimizer.zero_grad()
            outputs = model((images, isophotes, polars, metadata))
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        scheduler.step()
        
        # Validation
        model.eval()
        val_loss = 0
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            for batch in val_loader:
                images = batch['image'].to(config.DEVICE)
                isophotes = batch['isophote_map'].to(config.DEVICE)
                polars = batch['polar_image'].to(config.DEVICE)
                metadata = batch['metadata'].to(config.DEVICE)
                labels = batch['label'].to(config.DEVICE)
                
                outputs = model((images, isophotes, polars, metadata))
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                
                _, preds = torch.max(outputs, 1)
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        # Calculate metrics
        val_loss /= len(val_loader)
        melanoma_idx = config.label_encoder.transform(['mel'])[0]
        melanoma_mask = np.array(all_labels) == melanoma_idx
        melanoma_recall = recall_score(np.array(all_labels)[melanoma_mask], 
                                      np.array(all_preds)[melanoma_mask]) if any(melanoma_mask) else 0
        
        logger.log_atomic(f"Epoch {epoch+1}: Train Loss: {train_loss/len(train_loader):.4f}, "
                         f"Val Loss: {val_loss:.4f}, Melanoma Recall: {melanoma_recall:.4f}")
        
        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), os.path.join(config.MODEL_SAVE_DIRECTORY, "first_stage_best.pth"))
    
    return model

def identify_confident_nevi(config, model, df, confidence_threshold=0.9):
    """Identify confident nevi predictions for recursive exclusion"""
    logger.log_step("IDENTIFYING CONFIDENT NEVI PREDICTIONS")
    
    dataset = SkinLesionDataset(df, config, is_training=False)
    loader = DataLoader(dataset, batch_size=config.BATCH_SIZE, shuffle=False, num_workers=4)
    
    model.eval()
    confident_nevi_indices = []
    all_probs = []
    
    with torch.no_grad():
        for i, batch in enumerate(tqdm(loader, desc="Identifying confident nevi")):
            images = batch['image'].to(config.DEVICE)
            isophotes = batch['isophote_map'].to(config.DEVICE)
            polars = batch['polar_image'].to(config.DEVICE)
            metadata = batch['metadata'].to(config.DEVICE)
            
            outputs = model((images, isophotes, polars, metadata))
            probs = torch.softmax(outputs, dim=1)
            all_probs.append(probs.cpu().numpy())
            
            # Get nevi class index
            nevi_idx = config.label_encoder.transform(['nv'])[0]
            
            # Find confident nevi predictions
            batch_confident = (probs.argmax(dim=1) == nevi_idx) & (probs[:, nevi_idx] > confidence_threshold)
            batch_indices = np.where(batch_confident.cpu().numpy())[0] + i * config.BATCH_SIZE
            confident_nevi_indices.extend(batch_indices)
    
    # Find hard nevi (misclassified by first model)
    all_probs = np.vstack(all_probs)
    nevi_mask = df['label'] == 'nv'
    nevi_probs = all_probs[nevi_mask]
    nevi_preds = np.argmax(nevi_probs, axis=1)
    nevi_correct = nevi_preds == config.label_encoder.transform(['nv'])[0]
    hard_nevi_indices = df[nevi_mask].index[~nevi_correct].tolist()
    
    logger.log_atomic(f"Found {len(confident_nevi_indices)} confident nevi and {len(hard_nevi_indices)} hard nevi")
    
    return confident_nevi_indices, hard_nevi_indices

def train_second_stage(config, train_df, val_df, hard_negatives_indices):
    """Second stage: Train binary melanoma vs rest classifier"""
    logger.log_step("SECOND STAGE: TRAINING BINARY MELANOMA CLASSIFIER")
    
    # Prepare data for binary classification
    binary_train_df = train_df.copy()
    binary_train_df['binary_label'] = binary_train_df['label'].apply(lambda x: 1 if x == 'mel' else 0)
    
    # Add hard negatives
    if hard_negatives_indices:
        hard_negatives_df = train_df.loc[hard_negatives_indices].copy()
        hard_negatives_df['binary_label'] = 0
        binary_train_df = pd.concat([binary_train_df, hard_negatives_df])
    
    # Oversample melanoma cases
    melanoma_df = binary_train_df[binary_train_df['binary_label'] == 1]
    non_melanoma_df = binary_train_df[binary_train_df['binary_label'] == 0]
    
    # Balance classes with oversampling
    oversampled_melanoma = melanoma_df.sample(
        n=len(non_melanoma_df), 
        replace=True, 
        random_state=config.RANDOM_STATE_SEED
    )
    balanced_train_df = pd.concat([non_melanoma_df, oversampled_melanoma])
    
    # Create datasets
    train_dataset = SkinLesionDataset(
        balanced_train_df, config, is_training=True, is_melanoma_binary=True
    )
    val_dataset = SkinLesionDataset(
        val_df, config, is_training=False, is_melanoma_binary=True
    )
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=config.BATCH_SIZE, 
                             shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=config.BATCH_SIZE, 
                           shuffle=False, num_workers=4)
    
    # Initialize model
    model = HybridLesionModel(num_classes=2)  # Binary classification
    model = model.to(config.DEVICE)
    
    # Loss and optimizer
    criterion = FocalLoss(gamma=2.0)  # No class weights as we balanced the dataset
    optimizer = torch.optim.Adam(model.parameters(), lr=config.LEARNING_RATE/10)  # Lower LR for fine-tuning
    scheduler = CosineAnnealingLR(optimizer, T_max=config.SECOND_STAGE_EPOCHS)
    
    # Training loop
    best_melanoma_recall = 0
    for epoch in range(config.SECOND_STAGE_EPOCHS):
        model.train()
        train_loss = 0
        
        for batch in tqdm(train_loader, desc=f"Epoch {epoch+1}/{config.SECOND_STAGE_EPOCHS}"):
            images = batch['image'].to(config.DEVICE)
            isophotes = batch['isophote_map'].to(config.DEVICE)
            polars = batch['polar_image'].to(config.DEVICE)
            metadata = batch['metadata'].to(config.DEVICE)
            labels = batch['label'].to(config.DEVICE)
            
            optimizer.zero_grad()
            outputs = model((images, isophotes, polars, metadata))
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        scheduler.step()
        
        # Validation
        model.eval()
        val_loss = 0
        all_preds = []
        all_labels = []
        all_probs = []
        
        with torch.no_grad():
            for batch in val_loader:
                images = batch['image'].to(config.DEVICE)
                isophotes = batch['isophote_map'].to(config.DEVICE)
                polars = batch['polar_image'].to(config.DEVICE)
                metadata = batch['metadata'].to(config.DEVICE)
                labels = batch['label'].to(config.DEVICE)
                
                outputs = model((images, isophotes, polars, metadata))
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                
                probs = torch.softmax(outputs, dim=1)
                _, preds = torch.max(outputs, 1)
                
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
                all_probs.extend(probs[:, 1].cpu().numpy())  # Probability of melanoma
        
        # Calculate melanoma-specific metrics
        val_loss /= len(val_loader)
        all_labels = np.array(all_labels)
        all_preds = np.array(all_preds)
        all_probs = np.array(all_probs)
        
        melanoma_mask = all_labels == 1
        melanoma_recall = recall_score(all_labels[melanoma_mask], all_preds[melanoma_mask]) if any(melanoma_mask) else 0
        
        # Calculate sensitivity at 95% specificity
        if any(all_labels == 0):  # If there are non-melanoma cases
            fpr, tpr, thresholds = roc_curve(all_labels, all_probs)
            specificity = 1 - fpr
            sensitivity_at_95 = tpr[specificity >= 0.95][0] if any(specificity >= 0.95) else 0
        else:
            sensitivity_at_95 = 0
        
        logger.log_atomic(f"Epoch {epoch+1}: Val Loss: {val_loss:.4f}, "
                         f"Melanoma Recall: {melanoma_recall:.4f}, "
                         f"Sensitivity @ 95% Specificity: {sensitivity_at_95:.4f}")
        
        # Save best model based on melanoma recall
        if melanoma_recall > best_melanoma_recall:
            best_melanoma_recall = melanoma_recall
            torch.save(model.state_dict(), os.path.join(config.MODEL_SAVE_DIRECTORY, "second_stage_best.pth"))
    
    return model

def evaluate_cascade(config, test_df, first_stage_model, second_stage_model):
    """Evaluate the complete cascading pipeline"""
    logger.log_step("EVALUATING CASCADE PIPELINE")
    
    test_dataset = SkinLesionDataset(test_df, config, is_training=False)
    test_loader = DataLoader(test_dataset, batch_size=config.BATCH_SIZE, shuffle=False, num_workers=4)
    
    # Get first stage predictions
    first_stage_model.eval()
    second_stage_model.eval()
    
    all_first_preds = []
    all_second_preds = []
    all_final_preds = []
    all_labels = []
    all_probs = []
    
    with torch.no_grad():
        for batch in tqdm(test_loader, desc="Evaluating cascade"):
            images = batch['image'].to(config.DEVICE)
            isophotes = batch['isophote_map'].to(config.DEVICE)
            polars = batch['polar_image'].to(config.DEVICE)
            metadata = batch['metadata'].to(config.DEVICE)
            labels = batch['label'].to(config.DEVICE)
            
            # First stage predictions
            first_outputs = first_stage_model((images, isophotes, polars, metadata))
            first_probs = torch.softmax(first_outputs, dim=1)
            first_preds = torch.argmax(first_outputs, dim=1)
            
            # Get nevi class index
            nevi_idx = config.label_encoder.transform(['nv'])[0]
            
            # Second stage predictions for potential melanomas
            second_input_mask = first_preds != nevi_idx  # Everything not classified as nevi
            second_outputs = second_stage_model((images[second_input_mask], 
                                               isophotes[second_input_mask], 
                                               polars[second_input_mask], 
                                               metadata[second_input_mask]))
            
            # Combine predictions
            final_preds = first_preds.clone()
            if len(second_outputs) > 0:
                second_preds = torch.argmax(second_outputs, dim=1)
                # Convert binary predictions back to original labels
                mel_idx = config.label_encoder.transform(['mel'])[0]
                second_preds_original = torch.where(second_preds == 1, 
                                                   mel_idx, 
                                                   first_preds[second_input_mask])
                final_preds[second_input_mask] = second_preds_original
            
            # Store results
            all_first_preds.extend(first_preds.cpu().numpy())
            all_second_preds.extend(second_preds.cpu().numpy() if len(second_outputs) > 0 else [])
            all_final_preds.extend(final_preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    # Calculate metrics
    melanoma_idx = config.label_encoder.transform(['mel'])[0]
    melanoma_mask = np.array(all_labels) == melanoma_idx
    
    # First stage metrics
    first_stage_recall = recall_score(np.array(all_labels)[melanoma_mask], 
                                     np.array(all_first_preds)[melanoma_mask]) if any(melanoma_mask) else 0
    
    # Final cascade metrics
    cascade_recall = recall_score(np.array(all_labels)[melanoma_mask], 
                                 np.array(all_final_preds)[melanoma_mask]) if any(melanoma_mask) else 0
    
    # Precision-Recall AUC
    precision, recall, _ = precision_recall_curve(all_labels == melanoma_idx, 
                                                 np.array(all_final_preds) == melanoma_idx)
    pr_auc = auc(recall, precision)
    
    logger.log_atomic(f"First Stage Melanoma Recall: {first_stage_recall:.4f}")
    logger.log_atomic(f"Cascade Melanoma Recall: {cascade_recall:.4f}")
    logger.log_atomic(f"PR-AUC: {pr_auc:.4f}")
    
    # Generate comprehensive classification report
    logger.log_atomic("\nCOMPREHENSIVE CLASSIFICATION REPORT:")
    report = classification_report(all_labels, all_final_preds, 
                                  target_names=config.label_encoder.classes_)
    logger.log_atomic(report)
    
    return {
        'first_stage_recall': first_stage_recall,
        'cascade_recall': cascade_recall,
        'pr_auc': pr_auc
    }

# Update your configuration with new parameters
@dataclass
class EnhancedPipelineConfiguration(PipelineConfiguration):
    """Enhanced configuration with new parameters"""
    # Training parameters
    BATCH_SIZE: int = 16
    LEARNING_RATE: float = 1e-4
    FIRST_STAGE_EPOCHS: int = 50
    SECOND_STAGE_EPOCHS: int = 30
    CONFIDENCE_THRESHOLD: float = 0.9
    DEVICE: str = "cuda" if torch.cuda.is_available() else "cpu"

# Update your main function to use the enhanced pipeline
def enhanced_main():
    """Enhanced main function with two-stage pipeline"""
    try:
        # Initialize enhanced configuration
        config = EnhancedPipelineConfiguration()
        
        # Setup environment
        setup_environment(config)
        
        # Step 1: Frame the problem
        frame_problem()
        
        # Step 2: Get the data
        data = load_metadata(config)
        
        # Step 3: Explore the data
        explore_data(config, data)
        
        # Step 4: Prepare the data
        prepared_data = prepare_data(config, data)
        
        # Initialize label encoder
        label_encoder = LabelEncoder()
        prepared_data['label_encoded'] = label_encoder.fit_transform(prepared_data['label'])
        config.label_encoder = label_encoder
        
        # Split data
        train_val_df, test_df = train_test_split(
            prepared_data, test_size=config.TEST_SET_RATIO,
            random_state=config.RANDOM_STATE_SEED, stratify=prepared_data['label']
        )
        
        train_df, val_df = train_test_split(
            train_val_df, test_size=config.VALIDATION_SET_RATIO / (1 - config.TEST_SET_RATIO),
            random_state=config.RANDOM_STATE_SEED, stratify=train_val_df['label']
        )
        
        # Step 5: First stage - Train multiclass model
        first_stage_model = train_first_stage(config, train_df, val_df)
        
        # Step 6: Identify confident nevi and hard negatives
        confident_nevi_indices, hard_negatives_indices = identify_confident_nevi(
            config, first_stage_model, train_df, config.CONFIDENCE_THRESHOLD
        )
        
        # Step 7: Second stage - Train binary melanoma classifier
        # Remove some confident nevi but keep hard negatives
        filtered_train_df = train_df.drop(confident_nevi_indices[:len(confident_nevi_indices)//2])
        second_stage_model = train_second_stage(config, filtered_train_df, val_df, hard_negatives_indices)
        
        # Step 8: Evaluate the complete cascade
        metrics = evaluate_cascade(config, test_df, first_stage_model, second_stage_model)
        
        # Step 9: Present results
        logger.log_step("PRESENTING ENHANCED RESULTS")
        logger.log_atomic(f"Final Cascade Performance:")
        logger.log_atomic(f"Melanoma Recall: {metrics['cascade_recall']:.4f}")
        logger.log_atomic(f"PR-AUC: {metrics['pr_auc']:.4f}")
        
        # Save models
        torch.save(first_stage_model.state_dict(), 
                  os.path.join(config.MODEL_SAVE_DIRECTORY, "first_stage_final.pth"))
        torch.save(second_stage_model.state_dict(), 
                  os.path.join(config.MODEL_SAVE_DIRECTORY, "second_stage_final.pth"))
        
        logger.log_atomic("Enhanced pipeline completed successfully")
        
    except Exception as e:
        logger.log_atomic(f"Enhanced pipeline failed with error: {e}")
        raise

if __name__ == "__main__":
    enhanced_main()
