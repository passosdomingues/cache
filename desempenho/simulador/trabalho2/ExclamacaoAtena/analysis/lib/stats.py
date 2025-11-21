# lib/stats.py
import pandas as pd
import numpy as np
from scipy import stats
import logging

logger = logging.getLogger(__name__)

class StatsEngine:
    """
    @brief Statistical backend for queueing analysis.
    """

    def calculateMetrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        @brief Generates aggregated metrics per Policy x Rho.
        """
        # Define aggregations
        aggs = {
            'total_occupancy': ['mean', 'std', 'max', lambda x: x.quantile(0.99)],
            'system_EN': 'mean',
            'system_EW': 'mean',
            'little_error': ['mean', 'max'],
            'server_busy': 'mean'
        }
        
        grouped = df.groupby(['policy', 'rho'], observed=True)
        metrics = grouped.agg(aggs).reset_index()
        
        # Flatten columns
        metrics.columns = [
            'policy', 'rho', 
            'occupancy_mean', 'occupancy_std', 'occupancy_max', 'occupancy_p99',
            'EN_mean', 'EW_mean', 
            'little_error_mean', 'little_error_max', 
            'utilization'
        ]
        
        return metrics

    def checkConvergence(self, df: pd.DataFrame, window_size=1000) -> pd.DataFrame:
        """
        @brief Analyzes stability of the mean occupancy over time.
        """
        results = []
        for (policy, rho), group in df.groupby(['policy', 'rho']):
            # Rolling mean variance
            rolling_mean = group['total_occupancy'].rolling(window=window_size).mean()
            stability = rolling_mean.std() / (rolling_mean.mean() + 1e-9)
            
            results.append({
                'policy': policy, 
                'rho': rho, 
                'stability_index': stability,
                'converged': stability < 0.05
            })
            
        return pd.DataFrame(results)

    def getCorrelationMatrix(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        @brief Correlates key queueing metrics.
        """
        cols = ['total_occupancy', 'arrival_rate_est', 'system_EN', 'system_EW', 'little_error']
        return df[cols].corr()