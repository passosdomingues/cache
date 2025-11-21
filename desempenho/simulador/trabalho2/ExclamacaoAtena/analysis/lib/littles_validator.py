"""
@file littles_validator.py
@brief Specialized validator for Little's Law metrics in M/M/k queue context
@author Project Chronos
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class LittlesLawValidator:
    """
    @brief Validates Little's Law compliance: E[N] = lambda * E[W]
    
    This class extracts and validates queueing metrics from simulation logs,
    comparing measured values against theoretical M/M/k predictions.
    """
    
    def __init__(self, errorThreshold: float = 0.05):
        """
        @brief Constructor for LittlesLawValidator
        @param errorThreshold Maximum acceptable relative error for Little's Law validation
        """
        self.errorThreshold = errorThreshold
        logger.info(f"Initialized LittlesLawValidator with error threshold: {errorThreshold}")
    
    def extractMetrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        @brief Extract Little's Law metrics from simulation logs
        @param df Simulation DataFrame with columns: time, systemOccupancy, arrivalRate, littleError
        @return DataFrame with aggregated metrics per policy/rho combination
        
        Calculates:
        - lambda: Effective arrival rate (mean over steady state)
        - E[N]: Time-averaged system occupancy
        - E[W]: Average waiting time (derived from Little's Law)
        - relativeError: |E[N] - lambda*E[W]| / E[N]
        """
        logger.info("Extracting Little's Law metrics from simulation data...")
        
        # Group by scenario and load factor
        grouped = df.groupby(['scenarioPolicy', 'rho'], observed=True)
        
        results = []
        for (policy, rho), group in grouped:
            # Calculate arrival rate (lambda)
            lambdaEstimate = group['arrivalRate'].mean()
            
            # Calculate E[N] (time-averaged occupancy)
            expectedN = group['systemOccupancy'].mean()
            
            # Calculate E[W] from Little's Law: E[W] = E[N] / lambda
            expectedW = expectedN / lambdaEstimate if lambdaEstimate > 0 else 0.0
            
            # Get mean Little's Law error from tracker
            littleErrorMean = group['littleError'].mean()
            littleErrorStd = group['littleError'].std()
            
            # Calculate relative error
            relativeError = abs(littleErrorMean / expectedN) if expectedN > 0 else 0.0
            
            # Check compliance
            isCompliant = relativeError <= self.errorThreshold
            
            results.append({
                'scenarioPolicy': policy,
                'rho': rho,
                'lambda': lambdaEstimate,
                'expectedN': expectedN,
                'expectedW': expectedW,
                'littleErrorMean': littleErrorMean,
                'littleErrorStd': littleErrorStd,
                'relativeError': relativeError,
                'isCompliant': isCompliant,
                'sampleCount': len(group)
            })
        
        resultDf = pd.DataFrame(results)
        
        # Log violations
        violations = resultDf[~resultDf['isCompliant']]
        if len(violations) > 0:
            logger.warning(f"Found {len(violations)} Little's Law violations:")
            for _, row in violations.iterrows():
                logger.warning(f"  {row['scenarioPolicy']} @ rho={row['rho']}: error={row['relativeError']:.4f}")
        else:
            logger.info("All scenarios comply with Little's Law!")
        
        return resultDf
    
    def compareTheoretical(self, df: pd.DataFrame, numServers: int = 1, 
                          serviceRate: float = 1.0) -> pd.DataFrame:
        """
        @brief Compare measured metrics against M/M/k theoretical values
        @param df DataFrame with measured metrics (from extractMetrics)
        @param numServers Number of servers (k) in M/M/k system
        @param serviceRate Service rate (mu) per server
        @return DataFrame with theoretical vs measured comparison
        
        Calculates theoretical E[N] using Erlang-C formula for M/M/k queues.
        """
        logger.info(f"Comparing against M/M/{numServers} theoretical model (mu={serviceRate})...")
        
        results = []
        for _, row in df.iterrows():
            lambdaVal = row['lambda']
            rho = row['rho']
            
            # Traffic intensity
            a = lambdaVal / serviceRate
            
            # Utilization per server
            utilization = a / numServers if numServers > 0 else 0.0
            
            # Theoretical E[N] for M/M/k (simplified for k=1: E[N] = rho/(1-rho))
            if numServers == 1:
                theoreticalN = utilization / (1 - utilization) if utilization < 1.0 else float('inf')
            else:
                # For k>1, use Erlang-C approximation
                theoreticalN = self._erlangCOccupancy(lambdaVal, serviceRate, numServers)
            
            # Deviation from theory
            measuredN = row['expectedN']
            deviation = abs(measuredN - theoreticalN) / theoreticalN if theoreticalN > 0 else 0.0
            
            results.append({
                'scenarioPolicy': row['scenarioPolicy'],
                'rho': rho,
                'measuredN': measuredN,
                'theoreticalN': theoreticalN,
                'deviation': deviation,
                'lambda': lambdaVal,
                'utilization': utilization
            })
        
        return pd.DataFrame(results)
    
    def _erlangCOccupancy(self, arrivalRate: float, serviceRate: float, 
                          numServers: int) -> float:
        """
        @brief Calculate expected occupancy for M/M/k queue using Erlang-C
        @param arrivalRate Lambda (arrival rate)
        @param serviceRate Mu (service rate per server)
        @param numServers Number of servers (k)
        @return Expected number in system E[N]
        
        Uses iterative calculation for Erlang-C probability.
        """
        a = arrivalRate / serviceRate  # Traffic intensity
        rho = a / numServers  # Per-server utilization
        
        if rho >= 1.0:
            return float('inf')  # System unstable
        
        # Calculate Erlang-C probability (probability of queuing)
        erlangB = self._erlangB(a, numServers)
        erlangC = erlangB / (1 - rho * (1 - erlangB))
        
        # Expected queue length
        expectedQueue = erlangC * rho / (1 - rho)
        
        # Expected number in system
        expectedN = a + expectedQueue
        
        return expectedN
    
    def _erlangB(self, trafficIntensity: float, numServers: int) -> float:
        """
        @brief Calculate Erlang-B blocking probability
        @param trafficIntensity Traffic intensity (a = lambda/mu)
        @param numServers Number of servers
        @return Blocking probability
        """
        if numServers == 0:
            return 1.0
        
        # Iterative calculation to avoid overflow
        erlangB = 1.0
        for k in range(1, numServers + 1):
            erlangB = (trafficIntensity * erlangB) / (k + trafficIntensity * erlangB)
        
        return erlangB
    
    def generateValidationReport(self, metricsDf: pd.DataFrame, 
                                 theoreticalDf: pd.DataFrame) -> str:
        """
        @brief Generate markdown validation report
        @param metricsDf DataFrame from extractMetrics
        @param theoreticalDf DataFrame from compareTheoretical
        @return Markdown-formatted report string
        """
        report = "# Little's Law Validation Report\n\n"
        report += "## Summary\n\n"
        
        totalScenarios = len(metricsDf)
        compliantScenarios = metricsDf['isCompliant'].sum()
        complianceRate = (compliantScenarios / totalScenarios * 100) if totalScenarios > 0 else 0
        
        report += f"- Total scenarios analyzed: {totalScenarios}\n"
        report += f"- Compliant scenarios: {compliantScenarios}\n"
        report += f"- Compliance rate: {complianceRate:.1f}%\n"
        report += f"- Error threshold: {self.errorThreshold}\n\n"
        
        report += "## Violations\n\n"
        violations = metricsDf[~metricsDf['isCompliant']]
        if len(violations) > 0:
            report += "| Policy | Rho | Relative Error | E[N] | Lambda | E[W] |\n"
            report += "|--------|-----|----------------|------|--------|------|\n"
            for _, row in violations.iterrows():
                report += f"| {row['scenarioPolicy']} | {row['rho']} | {row['relativeError']:.4f} | "
                report += f"{row['expectedN']:.2f} | {row['lambda']:.4f} | {row['expectedW']:.4f} |\n"
        else:
            report += "No violations detected.\n"
        
        report += "\n## Theoretical Comparison\n\n"
        report += "Top 5 deviations from M/M/k theory:\n\n"
        topDeviations = theoreticalDf.nlargest(5, 'deviation')
        report += "| Policy | Rho | Measured E[N] | Theoretical E[N] | Deviation |\n"
        report += "|--------|-----|---------------|------------------|------------|\n"
        for _, row in topDeviations.iterrows():
            report += f"| {row['scenarioPolicy']} | {row['rho']} | {row['measuredN']:.2f} | "
            report += f"{row['theoreticalN']:.2f} | {row['deviation']:.4f} |\n"
        
        return report
