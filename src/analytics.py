import pandas as pd
import numpy as np
from typing import Dict, Any, List
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import completeness_score, homogeneity_score

class DatasetAnalytics:
    def __init__(self):
        self.supported_formats = ['csv', 'json', 'parquet']
    
    def analyze_dataset(self, file_path: str) -> Dict[str, Any]:
        """Generate comprehensive analytics for a dataset"""
        try:
            # Load dataset
            df = self._load_dataset(file_path)
            
            # Basic statistics
            basic_stats = self._get_basic_stats(df)
            
            # Data quality metrics
            quality_metrics = self._get_quality_metrics(df)
            
            # Column correlations
            correlations = self._get_correlations(df)
            
            # Data distribution analysis
            distributions = self._analyze_distributions(df)
            
            return {
                "basic_stats": basic_stats,
                "quality_metrics": quality_metrics,
                "correlations": correlations,
                "distributions": distributions
            }
        except Exception as e:
            raise ValueError(f"Error analyzing dataset: {str(e)}")
    
    def _load_dataset(self, file_path: str) -> pd.DataFrame:
        """Load dataset from file"""
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith('.json'):
            return pd.read_json(file_path)
        elif file_path.endswith('.parquet'):
            return pd.read_parquet(file_path)
        else:
            raise ValueError("Unsupported file format")
    
    def _get_basic_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic statistics of the dataset"""
        return {
            "row_count": len(df),
            "column_count": len(df.columns),
            "memory_usage": df.memory_usage(deep=True).sum(),
            "numeric_columns": df.select_dtypes(include=['int64', 'float64']).describe().to_dict(),
            "categorical_columns": {
                col: df[col].value_counts().to_dict()
                for col in df.select_dtypes(include=['object']).columns
            }
        }
    
    def _get_quality_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate data quality metrics"""
        metrics = {
            "completeness": {
                col: 1 - (df[col].isnull().sum() / len(df))
                for col in df.columns
            },
            "uniqueness": {
                col: len(df[col].unique()) / len(df)
                for col in df.columns
            },
            "consistency": self._check_consistency(df),
            "accuracy": self._check_accuracy(df)
        }
        return metrics
    
    def _check_consistency(self, df: pd.DataFrame) -> Dict[str, float]:
        """Check data consistency"""
        consistency = {}
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                # Check for outliers using IQR method
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                consistency[col] = 1 - len(
                    df[(df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))]
                ) / len(df)
        return consistency
    
    def _check_accuracy(self, df: pd.DataFrame) -> Dict[str, float]:
        """Check data accuracy"""
        accuracy = {}
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                # Check for values within reasonable range
                mean = df[col].mean()
                std = df[col].std()
                accuracy[col] = 1 - len(
                    df[abs(df[col] - mean) > 3 * std]
                ) / len(df)
        return accuracy
    
    def _get_correlations(self, df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Calculate correlations between numeric columns"""
        numeric_df = df.select_dtypes(include=['int64', 'float64'])
        if not numeric_df.empty:
            corr_matrix = numeric_df.corr()
            return corr_matrix.to_dict()
        return {}
    
    def _analyze_distributions(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Analyze data distributions for each column"""
        distributions = {}
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                distributions[col] = {
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "std": float(df[col].std()),
                    "skewness": float(df[col].skew()),
                    "kurtosis": float(df[col].kurtosis()),
                    "histogram": np.histogram(df[col].dropna(), bins=10)
                }
        return distributions 