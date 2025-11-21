# lib/ml.py
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from scipy import stats
import logging

logger = logging.getLogger(__name__)

class MLAnalyzer:
    """
    @brief Applies machine learning techniques to simulation data.
    """

    def __init__(self, df: pd.DataFrame):
        """
        @brief Constructor.
        @param df Raw simulation DataFrame.
        """
        self.df = df.copy()

    def analyzeStateTransitions(self) -> pd.DataFrame:
        """
        @brief Calculates Markovian properties of the system state.
        @return DataFrame containing volatility and entropy metrics per policy.
        """
        logger.info("Calculating Markov Transition Matrices...")
        transitions = []
        
        for policy, group in self.df.groupby('scenarioPolicy', observed=True):
            # Shift to align current state with next state
            currentState = group['systemStateId']
            nextState = group['systemStateId'].shift(-1)
            
            # Average absolute jump size (Volatility)
            jumpSize = (nextState - currentState).abs().mean()
            
            # Entropy (Randomness of state distribution)
            stateEntropy = stats.entropy(group['systemStateId'].value_counts(normalize=True))
            
            transitions.append({
                'policy': policy,
                'avgStateJump': jumpSize,
                'stateEntropy': stateEntropy
            })
            
        return pd.DataFrame(transitions).sort_values('avgStateJump')

    def performClustering(self, nClusters=3) -> pd.DataFrame:
        """
        @brief Performs K-Means clustering to identify congestion levels.
        @param nClusters Number of clusters (e.g., Low, Medium, High congestion).
        @return DataFrame with a new 'cluster' column.
        """
        scaler = StandardScaler()
        # Select features relevant to congestion
        features = ['q0Len', 'q1Len', 'q2Len', 'systemOccupancy']
        
        # Handle missing values
        X = self.df[features].fillna(0)
        XScaled = scaler.fit_transform(X)
        
        kmeans = KMeans(n_clusters=nClusters, random_state=42, n_init=10)
        self.df['cluster'] = kmeans.fit_predict(XScaled)
        return self.df