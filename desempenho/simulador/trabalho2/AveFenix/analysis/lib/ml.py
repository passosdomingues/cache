#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MLAnalyzer Module
=================
Applies Unsupervised Learning to detect states and anomalies.
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)

class MLAnalyzer:
    """
    @brief Wraps Scikit-Learn models for queueing system analysis.
    """

    def __init__(self, df: pd.DataFrame):
        """
        @param df Input DataFrame containing simulation data.
        """
        self.df = df.copy()
        self.scaler = StandardScaler()
        self.features = ['q0_len', 'q1_len', 'q2_len', 'system_occupancy', 'server_busy']

    def performClustering(self, nClusters: int = 3) -> pd.DataFrame:
        """
        @brief Applies K-Means to identify system congestion states.
        @param nClusters Number of states to identify (e.g., Low, Med, High).
        @return DataFrame with a new 'clusterState' column.
        """
        # Replace NaNs with 0 for stability
        X = self.df[self.features].fillna(0)
        X_scaled = self.scaler.fit_transform(X)

        kmeans = KMeans(n_clusters=nClusters, random_state=42, n_init=10)
        self.df['clusterState'] = kmeans.fit_predict(X_scaled)
        
        return self.df

    def performPCA(self) -> pd.DataFrame:
        """
        @brief Reduces dimensionality to 2D for visualization purposes.
        @return DataFrame with 'pca1' and 'pca2' columns.
        """
        X = self.df[self.features].fillna(0)
        X_scaled = self.scaler.fit_transform(X)

        pca = PCA(n_components=2)
        components = pca.fit_transform(X_scaled)
        
        self.df['pca1'] = components[:, 0]
        self.df['pca2'] = components[:, 1]
        
        logger.info(f"PCA Explained Variance Ratio: {pca.explained_variance_ratio_}")
        return self.df