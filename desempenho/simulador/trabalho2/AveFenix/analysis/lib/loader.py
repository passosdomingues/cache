#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LogParser Module
================
Responsible for loading and preprocessing simulation logs.
"""

import pandas as pd
import re
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class LogParser:
    """
    @brief Handles the ingestion and parsing of raw CSV simulation logs.
    """

    def __init__(self, dataDir: Path):
        """
        @brief Constructor for LogParser.
        @param dataDir Path object pointing to the raw data directory.
        """
        self.dataDir = dataDir
        # Regex to extract metadata from filename: POLICY_rho0.800_seed42.csv
        self.filePattern = re.compile(r"([A-Z_]+)_rho(\d+\.\d+)_seed(\d+)\.csv")

    def loadAllScenarios(self) -> pd.DataFrame:
        """
        @brief Iterates through directory, parses filenames, and consolidates data.
        @return A single pandas DataFrame containing all simulation runs.
        @raises FileNotFoundError If no CSVs are found.
        """
        files = list(self.dataDir.glob("*.csv"))
        if not files:
            raise FileNotFoundError(f"No CSV files found in {self.dataDir}")

        dataFrames = []
        logger.info(f"Found {len(files)} log files. Starting ingestion...")

        for filePath in files:
            match = self.filePattern.match(filePath.name)
            if not match:
                logger.warning(f"Skipping non-compliant file: {filePath.name}")
                continue

            policy, rho, seed = match.groups()
            
            try:
                df = pd.read_csv(filePath)
                
                # Inject metadata
                df['policy'] = policy
                df['rho'] = float(rho)
                df['seed'] = int(seed)
                
                # Optimization: Category types for repeated strings
                df['policy'] = df['policy'].astype('category')
                
                dataFrames.append(df)
            except Exception as e:
                logger.error(f"Failed to process {filePath.name}: {e}")

        if not dataFrames:
            raise RuntimeError("Ingestion failed: No valid data loaded.")

        masterDf = pd.concat(dataFrames, ignore_index=True)
        logger.info(f"Ingestion complete. Loaded {len(masterDf)} rows.")
        return masterDf