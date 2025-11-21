# lib/loader.py
import pandas as pd
import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogParser:
    """
    @brief Enhanced CSV loader for 23-column simulation logs.
    """
    
    # Defined column mapping based on user specification
    COLUMNS = [
        'time', 'sample_idx', 'total_occupancy', 'arrival_rate_est',
        'q0_len', 'q1_len', 'q2_len', 'server_busy',
        'q0_EN', 'q0_EW', 'q0_lambda',
        'q1_EN', 'q1_EW', 'q1_lambda',
        'q2_EN', 'q2_EW', 'q2_lambda',
        'system_EN', 'system_EW', 'system_lambda',
        'little_error', 'system_state_id', 'active_policy'
    ]

    def __init__(self, dataDir: Path):
        self.dataDir = Path(dataDir)

    def extractMetadata(self, filename: str) -> dict:
        """
        @brief Extracts Policy, Rho, and Seed from standard filename format.
        Format expected: POLICY_NAME_rho0.900_seed123.csv
        """
        pattern = r'([A-Z_]+)_rho([0-9.]+)_seed(\d+)'
        match = re.search(pattern, filename)
        
        if match:
            return {
                'policy': match.group(1),
                'rho': float(match.group(2)),
                'seed': int(match.group(3))
            }
        return {'policy': 'UNKNOWN', 'rho': 0.0, 'seed': 0}

    def loadAllScenarios(self) -> pd.DataFrame:
        all_data = []
        files = list(self.dataDir.glob("*.csv"))
        
        logger.info(f"Found {len(files)} log files in {self.dataDir}")

        for f in files:
            try:
                # Load CSV with specific header mapping
                df = pd.read_csv(f, header=None, names=self.COLUMNS, skiprows=1)
                
                # Enrich with metadata
                meta = self.extractMetadata(f.name)
                df['policy'] = meta['policy']
                df['rho'] = meta['rho']
                df['seed'] = meta['seed']
                
                all_data.append(df)
            except Exception as e:
                logger.error(f"Failed to load {f.name}: {e}")

        if not all_data:
            return pd.DataFrame()
            
        return pd.concat(all_data, ignore_index=True)