# lib/policy_learner.py
import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class PolicyLearner:
    """
    @brief Reconstructs optimal policy matrix from simulation logs (Inverse RL/Oracle approach).
    """
    
    def __init__(self):
        # Maps internal C++ enums to integers for the CSV matrix
        self.policyMap = {
            "LONGEST_QUEUE": 0, "SHORTEST_QUEUE": 1, "ROUND_ROBIN": 2,
            "STRICT_PRIORITY": 3, "MAX_AVG_WAIT": 4, "SALLES_UTILITY": 5,
            "C_MU_RULE": 6, "WEIGHTED_ROUND_ROBIN": 7, "WHITTLE_INDEX": 8,
            "MARKOV_SWITCHING": 9, "NONE": -1, "OLDEST_PACKET": 10, "AGING": 11
        }

    def trainOptimalMatrix(self, df: pd.DataFrame, outputPath: Path):
        """
        @brief Finds the policy that minimized occupancy for each visited state across all runs.
        @param df Raw simulation DataFrame.
        @param outputPath Path to save the CSV matrix.
        """
        logger.info("Training optimal policy matrix (State-Space Search)...")

        # 1. Group by State and Policy -> Get Mean Occupancy (Cost function)
        stateCosts = df.groupby(['systemStateId', 'scenarioPolicy'], observed=True)['systemOccupancy'].mean().reset_index()
        
        # 2. Find the policy with Minimum Cost for each unique State
        bestStrategies = stateCosts.loc[stateCosts.groupby('systemStateId')['systemOccupancy'].idxmin()]
        
        # 3. Map Policy Names to IDs
        bestStrategies['policyId'] = bestStrategies['scenarioPolicy'].map(self.policyMap).fillna(-1).astype(int)
        
        # 4. Export
        matrix = bestStrategies[['systemStateId', 'policyId']].sort_values('systemStateId')
        matrix.to_csv(outputPath, index=False)
        
        logger.info(f"Optimal Policy Matrix saved to {outputPath}. Covered {len(matrix)} states.")
        return matrix
    
    def analyzePolicyPerformance(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        @brief Rank policies by multiple performance criteria
        @param df Raw simulation DataFrame
        @return DataFrame with policy rankings across different metrics
        
        Ranking criteria:
        - Mean occupancy (lower is better)
        - P99 occupancy (lower is better)
        - Stability: standard deviation (lower is better)
        - Fairness: variance across queues (lower is better)
        """
        logger.info("Analyzing policy performance across multiple criteria...")
        
        # Group by policy and rho
        grouped = df.groupby(['scenarioPolicy', 'rho'], observed=True)
        
        performanceMetrics = []
        for (policy, rho), group in grouped:
            # Calculate metrics
            occupancyMean = group['systemOccupancy'].mean()
            occupancyStd = group['systemOccupancy'].std()
            occupancyP99 = group['systemOccupancy'].quantile(0.99)
            
            # Queue fairness (lower variance = more fair)
            queueLengths = group[['q0Len', 'q1Len', 'q2Len']]
            fairnessScore = queueLengths.var(axis=1).mean()
            
            # Little's Law compliance
            littleErrorMean = group['littleError'].mean()
            
            performanceMetrics.append({
                'scenarioPolicy': policy,
                'rho': rho,
                'occupancyMean': occupancyMean,
                'occupancyStd': occupancyStd,
                'occupancyP99': occupancyP99,
                'fairnessScore': fairnessScore,
                'littleErrorMean': littleErrorMean,
                'sampleCount': len(group)
            })
        
        resultDf = pd.DataFrame(performanceMetrics)
        
        # Add rankings (rank within each rho group)
        for rho in resultDf['rho'].unique():
            mask = resultDf['rho'] == rho
            rhoGroup = resultDf[mask]
            
            # Lower is better for all metrics
            resultDf.loc[mask, 'rankMean'] = rhoGroup['occupancyMean'].rank()
            resultDf.loc[mask, 'rankStability'] = rhoGroup['occupancyStd'].rank()
            resultDf.loc[mask, 'rankP99'] = rhoGroup['occupancyP99'].rank()
            resultDf.loc[mask, 'rankFairness'] = rhoGroup['fairnessScore'].rank()
            
            # Composite score (average rank)
            resultDf.loc[mask, 'compositeRank'] = resultDf.loc[mask, ['rankMean', 'rankStability', 'rankP99', 'rankFairness']].mean(axis=1)
        
        # Sort by composite rank
        resultDf = resultDf.sort_values(['rho', 'compositeRank'])
        
        logger.info(f"Performance analysis complete for {len(resultDf)} policy-rho combinations")
        return resultDf