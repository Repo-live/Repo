from typing import Dict, Any, List
import pandas as pd
import numpy as np
from datetime import datetime

class QualityChecker:
    def __init__(self):
        self.quality_thresholds = {
            "completeness": 0.9,  # 90% data completeness
            "consistency": 0.95,  # 95% data consistency
            "accuracy": 0.95,     # 95% data accuracy
            "timeliness": 30,     # Data should be no older than 30 days
        }
    
    def evaluate_quality(self, file_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate the quality of a dataset"""
        try:
            df = self._load_dataset(file_path)
            
            quality_scores = {
                "completeness": self._check_completeness(df),
                "consistency": self._check_consistency(df),
                "accuracy": self._check_accuracy(df),
                "timeliness": self._check_timeliness(metadata),
                "format_validity": self._check_format_validity(df),
                "schema_compliance": self._check_schema_compliance(df, metadata)
            }
            
            # Calculate overall quality score
            weights = {
                "completeness": 0.3,
                "consistency": 0.2,
                "accuracy": 0.2,
                "timeliness": 0.1,
                "format_validity": 0.1,
                "schema_compliance": 0.1
            }
            
            overall_score = sum(
                score * weights[metric]
                for metric, score in quality_scores.items()
            )
            
            return {
                "overall_score": overall_score,
                "detailed_scores": quality_scores,
                "recommendations": self._generate_recommendations(quality_scores)
            }
            
        except Exception as e:
            raise ValueError(f"Error evaluating dataset quality: {str(e)}")
    
    def _check_completeness(self, df: pd.DataFrame) -> float:
        """Check data completeness"""
        return 1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1])
    
    def _check_consistency(self, df: pd.DataFrame) -> float:
        """Check data consistency"""
        consistency_scores = []
        
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                # Check for outliers
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = len(
                    df[(df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))]
                )
                consistency_scores.append(1 - outliers / len(df))
        
        return np.mean(consistency_scores) if consistency_scores else 1.0
    
    def _check_accuracy(self, df: pd.DataFrame) -> float:
        """Check data accuracy"""
        accuracy_scores = []
        
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                # Check for values within reasonable range
                mean = df[col].mean()
                std = df[col].std()
                outliers = len(df[abs(df[col] - mean) > 3 * std])
                accuracy_scores.append(1 - outliers / len(df))
        
        return np.mean(accuracy_scores) if accuracy_scores else 1.0
    
    def _check_timeliness(self, metadata: Dict[str, Any]) -> float:
        """Check data timeliness"""
        if 'last_updated' in metadata:
            last_updated = datetime.fromisoformat(metadata['last_updated'])
            days_old = (datetime.now() - last_updated).days
            return max(0, 1 - days_old / self.quality_thresholds['timeliness'])
        return 0.5  # Default score if no timestamp available
    
    def _check_format_validity(self, df: pd.DataFrame) -> float:
        """Check if data format is valid"""
        try:
            # Check for proper data types
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            categorical_cols = df.select_dtypes(include=['object']).columns
            
            format_scores = []
            
            # Check numeric columns
            for col in numeric_cols:
                invalid_count = pd.to_numeric(df[col], errors='coerce').isnull().sum()
                format_scores.append(1 - invalid_count / len(df))
            
            return np.mean(format_scores) if format_scores else 1.0
            
        except Exception:
            return 0.0
    
    def _check_schema_compliance(self, df: pd.DataFrame, metadata: Dict[str, Any]) -> float:
        """Check if data complies with expected schema"""
        if 'schema' not in metadata:
            return 0.5  # Default score if no schema provided
        
        expected_schema = metadata['schema']
        actual_schema = df.dtypes.to_dict()
        
        matching_columns = sum(
            1 for col in expected_schema
            if col in actual_schema and str(actual_schema[col]) == expected_schema[col]
        )
        
        return matching_columns / len(expected_schema)
    
    def _generate_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """Generate recommendations based on quality scores"""
        recommendations = []
        
        for metric, score in scores.items():
            if score < self.quality_thresholds.get(metric, 0.9):
                if metric == "completeness":
                    recommendations.append(
                        "Consider handling missing values or collecting more complete data"
                    )
                elif metric == "consistency":
                    recommendations.append(
                        "Review and handle outliers in the dataset"
                    )
                elif metric == "accuracy":
                    recommendations.append(
                        "Validate extreme values and consider data cleaning"
                    )
                elif metric == "timeliness":
                    recommendations.append(
                        "Update the dataset with more recent data"
                    )
                elif metric == "format_validity":
                    recommendations.append(
                        "Review data types and format specifications"
                    )
                elif metric == "schema_compliance":
                    recommendations.append(
                        "Ensure data follows the expected schema"
                    )
        
        return recommendations 