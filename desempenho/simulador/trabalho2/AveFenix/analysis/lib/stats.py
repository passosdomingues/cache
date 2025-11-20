#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
StatsEngine Module
==================
Core statistical calculations and Little's Law validation.
"""

import pandas as pd
import numpy as np
from scipy import stats
import logging

logger = logging.getLogger(__name__)

class StatsEngine:
    """
    @brief Performs statistical analysis on queueing data.
    """

    def __init__(self):
        pass

    def calculateMetrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        @brief Aggregates performance metrics by Policy and Load (Rho).
        @param df The raw simulation DataFrame.
        @return A summarized DataFrame with Mean, Std, P95, P99, and CI.
        """
        logger.info("Calculating statistical metrics (Mean, P99, CI)...")

        def p95(x): return x.quantile(0.95)
        def p99(x): return x.quantile(0.99)
        def confidenceInterval(x):
            if len(x) < 2: return 0
            return stats.sem(x) * 1.96 # 95% Confidence Interval

        # Ensure we include all necessary columns
        metrics = df.groupby(['policy', 'rho']).agg({
            'system_occupancy': ['mean', 'std', p95, p99, confidenceInterval],
            'avg_wait_error': 'mean',
            'little_error': 'mean',
            'server_busy': 'mean',
            'q0_len': 'mean',
            'q1_len': 'mean',
            'q2_len': 'mean'
        })

        # Flatten MultiIndex columns
        metrics.columns = [
            'occupancyMean', 'occupancyStd', 'occupancyP95', 'occupancyP99', 'occupancyCI',
            'avgWaitError', 'littleError', 'utilization',
            'q0Mean', 'q1Mean', 'q2Mean'
        ]
        
        return metrics.reset_index()

    def verifyLittlesLaw(self, metricsDf: pd.DataFrame, threshold: float = 1.0) -> pd.DataFrame:
        """
        @brief Checks for violations of Little's Law (L = lambda * W).
        @param metricsDf The summarized metrics DataFrame.
        @param threshold The maximum acceptable error value.
        @return DataFrame containing only the violating scenarios.
        """
        violations = metricsDf[metricsDf['littleError'] > threshold]
        if not violations.empty:
            logger.warning(f"Found {len(violations)} scenarios violating Little's Law stability check.")
        return violations