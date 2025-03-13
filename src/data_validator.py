import pandas as pd
import json
from typing import Dict, Any

class DataValidator:
    def __init__(self):
        self.supported_formats = ['csv', 'json', 'parquet']
        
    def validate_dataset(self, file_path: str, metadata: Dict[str, Any]) -> bool:
        file_format = metadata.get('format', '').lower()
        if file_format not in self.supported_formats:
            return False
            
        try:
            if file_format == 'csv':
                df = pd.read_csv(file_path)
            elif file_format == 'json':
                df = pd.read_json(file_path)
            elif file_format == 'parquet':
                df = pd.read_parquet(file_path)
                
            # Basic validation checks
            if df.empty:
                return False
                
            # Check for required columns
            required_columns = metadata.get('required_columns', [])
            if not all(col in df.columns for col in required_columns):
                return False
                
            # Check data types
            column_types = metadata.get('column_types', {})
            for col, dtype in column_types.items():
                if col in df.columns and str(df[col].dtype) != dtype:
                    return False
                    
            return True
            
        except Exception:
            return False 