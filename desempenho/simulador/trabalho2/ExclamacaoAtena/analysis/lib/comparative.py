#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ComparativeAnalyzer Module
==========================
Analyzes trade-offs between policies.
"""

import pandas as pd

class ComparativeAnalyzer:
    """
    @brief Logic for ranking and comparing policies.
    """
    
    @staticmethod
    def getBestHighLoadPolicy(metricsDf: pd.DataFrame) -> pd.Series:
        """
        @brief Identifies the winner for Rho=0.999 based on Occupancy.
        @param metricsDf The dataframe containing calculated metrics.
        @return Series containing the best policy row, or None if data missing.
        """
        highLoad = metricsDf[metricsDf['rho'] == 0.999]
        if highLoad.empty:
            return None
        # We want the Minimum occupancy
        return highLoad.sort_values('occupancyMean').iloc[0]

    @staticmethod
    def calculateFairnessIndex(df: pd.DataFrame) -> pd.DataFrame:
        """
        @brief Calculates fairness based on variance between queue lengths.
        @details A lower variance between q0, q1, q2 indicates better fairness.
        """
        df['fairnessVar'] = df[['q0_len', 'q1_len', 'q2_len']].var(axis=1)
        return df.groupby('policy')['fairnessVar'].mean().reset_index().sort_values('fairnessVar')