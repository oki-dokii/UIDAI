#!/usr/bin/env python3
"""
UIDAI Data Quality Validator
Detects suspicious values, calculates confidence intervals, and generates quality reports.
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')


class DataQualityValidator:
    """Validates UIDAI data quality and generates annotations."""
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize validator with dataframe.
        
        Args:
            df: UIDAI data (state or district level)
        """
        self.df = df.copy()
        self.quality_flags = pd.DataFrame(index=df.index)
        self.quality_report = {}
    
    def detect_suspicious_values(self, columns: List[str], 
                                 threshold_multiplier: float = 1e9) -> pd.DataFrame:
        """
        Detect suspiciously round numbers that likely indicate placeholders.
        
        Args:
            columns: List of column names to check
            threshold_multiplier: Values that are exact multiples of this are flagged
            
        Returns:
            DataFrame with boolean flags for suspicious values
        """
        flags = pd.DataFrame(index=self.df.index)
        
        for col in columns:
            if col not in self.df.columns:
                continue
                
            # Check if values are exact multiples of threshold (e.g., exactly 10 billion)
            values = self.df[col].fillna(0)
            
            # Flag 1: Exact multiples of large round numbers
            is_round = (values % threshold_multiplier == 0) & (values > 0)
            
            # Flag 2: Values that are suspiciously large outliers
            if len(values) > 3:
                mean_val = values.mean()
                std_val = values.std()
                if std_val > 0:
                    z_scores = np.abs((values - mean_val) / std_val)
                    is_outlier = z_scores > 5
                else:
                    is_outlier = pd.Series([False] * len(values), index=values.index)
            else:
                is_outlier = pd.Series([False] * len(values), index=values.index)
            
            # Flag 3: Exactly zero when neighbors are non-zero
            is_suspicious_zero = (values == 0) & (values.shift(1).fillna(0) > 0)
            
            # Combine flags
            flags[f'{col}_suspicious'] = is_round | is_outlier | is_suspicious_zero
            
            # Store counts
            self.quality_report[col] = {
                'total_records': len(values),
                'round_numbers': is_round.sum(),
                'outliers': is_outlier.sum(),
                'suspicious_zeros': is_suspicious_zero.sum(),
                'flagged_total': flags[f'{col}_suspicious'].sum(),
                'flagged_percentage': (flags[f'{col}_suspicious'].sum() / len(values) * 100)
            }
        
        self.quality_flags = pd.concat([self.quality_flags, flags], axis=1)
        return flags
    
    def calculate_confidence_intervals(self, metric_col: str, 
                                       group_col: Optional[str] = None,
                                       confidence: float = 0.95,
                                       n_bootstrap: int = 1000) -> pd.DataFrame:
        """
        Calculate bootstrap confidence intervals for a metric.
        
        Args:
            metric_col: Column name for metric
            group_col: Optional grouping column (e.g., 'state')
            confidence: Confidence level (default 0.95 for 95% CI)
            n_bootstrap: Number of bootstrap samples
            
        Returns:
            DataFrame with lower and upper CI bounds
        """
        results = []
        
        if group_col:
            groups = self.df[group_col].unique()
        else:
            groups = ['all']
            
        for group in groups:
            if group_col:
                data = self.df[self.df[group_col] == group][metric_col].dropna()
            else:
                data = self.df[metric_col].dropna()
            
            if len(data) < 2:
                results.append({
                    group_col or 'group': group,
                    f'{metric_col}_mean': np.nan,
                    f'{metric_col}_ci_lower': np.nan,
                    f'{metric_col}_ci_upper': np.nan,
                    f'{metric_col}_ci_width': np.nan,
                    'sample_size': len(data)
                })
                continue
            
            # Bootstrap resampling
            bootstrap_means = []
            for _ in range(n_bootstrap):
                sample = np.random.choice(data, size=len(data), replace=True)
                bootstrap_means.append(np.mean(sample))
            
            # Calculate CI
            alpha = 1 - confidence
            ci_lower = np.percentile(bootstrap_means, alpha/2 * 100)
            ci_upper = np.percentile(bootstrap_means, (1 - alpha/2) * 100)
            
            results.append({
                group_col or 'group': group,
                f'{metric_col}_mean': data.mean(),
                f'{metric_col}_ci_lower': ci_lower,
                f'{metric_col}_ci_upper': ci_upper,
                f'{metric_col}_ci_width': ci_upper - ci_lower,
                'sample_size': len(data)
            })
        
        return pd.DataFrame(results)
    
    def identify_small_sample_concern(self, group_col: str, 
                                      min_sample_size: int = 30) -> pd.Series:
        """
        Identify groups with small sample sizes that may have unreliable estimates.
        
        Args:
            group_col: Column to group by
            min_sample_size: Minimum acceptable sample size
            
        Returns:
            Series of boolean flags
        """
        group_sizes = self.df.groupby(group_col).size()
        small_sample_groups = group_sizes[group_sizes < min_sample_size].index
        
        is_small_sample = self.df[group_col].isin(small_sample_groups)
        
        self.quality_report['small_sample_concern'] = {
            'groups_flagged': list(small_sample_groups),
            'count': len(small_sample_groups),
            'threshold': min_sample_size
        }
        
        return is_small_sample
    
    def generate_quality_score(self) -> pd.Series:
        """
        Generate overall quality score (0-100) for each record.
        
        Returns:
            Series of quality scores
        """
        scores = pd.Series(100.0, index=self.df.index)
        
        # Deduct points for each quality issue
        for col in self.quality_flags.columns:
            if '_suspicious' in col:
                scores -= self.quality_flags[col] * 30  # -30 points for suspicious values
        
        # Ensure scores are in [0, 100]
        scores = scores.clip(0, 100)
        
        return scores
    
    def generate_report(self, output_path: Optional[str] = None) -> Dict:
        """
        Generate comprehensive data quality report.
        
        Args:
            output_path: Optional path to save report as CSV
            
        Returns:
            Dictionary with quality statistics
        """
        report = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'total_records': len(self.df),
            'checks_performed': list(self.quality_report.keys()),
            'details': self.quality_report
        }
        
        # Add overall quality scores
        quality_scores = self.generate_quality_score()
        report['mean_quality_score'] = quality_scores.mean()
        report['median_quality_score'] = quality_scores.median()
        report['records_below_80'] = (quality_scores < 80).sum()
        
        if output_path:
            # Save detailed report
            report_df = pd.DataFrame([report])
            report_df.to_csv(output_path, index=False)
            print(f"✅ Quality report saved: {output_path}")
        
        return report
    
    def annotate_dataframe(self) -> pd.DataFrame:
        """
        Return dataframe with quality annotations added.
        
        Returns:
            DataFrame with added quality flag columns
        """
        annotated = self.df.copy()
        annotated = pd.concat([annotated, self.quality_flags], axis=1)
        annotated['quality_score'] = self.generate_quality_score()
        return annotated


def validate_state_data(state_data: pd.DataFrame, 
                       intensity_threshold: float = 1e9) -> Tuple[pd.DataFrame, Dict]:
    """
    Convenience function to validate state-level data.
    
    Args:
        state_data: State-level aggregated data
        intensity_threshold: Threshold for detecting suspicious round numbers
        
    Returns:
        Tuple of (annotated dataframe, quality report dict)
    """
    validator = DataQualityValidator(state_data)
    
    # Check intensity and update metrics
    intensity_cols = ['total_intensity', 'demo_intensity', 'bio_intensity', 'total_updates']
    validator.detect_suspicious_values(intensity_cols, threshold_multiplier=intensity_threshold)
    
    # Calculate CIs for key metrics
    gap_ci = validator.calculate_confidence_intervals('child_attention_gap', group_col='state')
    intensity_ci = validator.calculate_confidence_intervals('total_intensity', group_col='state')
    
    # Generate report
    report = validator.generate_report()
    report['gap_confidence_intervals'] = gap_ci.to_dict('records')
    report['intensity_confidence_intervals'] = intensity_ci.to_dict('records')
    
    # Return annotated data
    annotated_df = validator.annotate_dataframe()
    
    return annotated_df, report


if __name__ == "__main__":
    import os
    import sys
    
    # Test with actual UIDAI data
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_FILE = os.path.join(BASE_DIR, "outputs", "integrated_analysis", "integrated_data.csv")
    
    if os.path.exists(DATA_FILE):
        print("Testing Data Quality Validator...")
        df = pd.read_csv(DATA_FILE)
        
        # Aggregate to state level
        state_agg = df.groupby('state').agg({
            'total_enrol': 'sum',
            'total_updates': 'sum',
            'total_intensity': 'mean',
            'child_attention_gap': 'mean',
            'demo_intensity': 'mean',
            'bio_intensity': 'mean'
        }).reset_index()
        
        # Validate
        annotated, report = validate_state_data(state_agg)
        
        print("\n📊 QUALITY REPORT SUMMARY:")
        print(f"   Total Records: {report['total_records']}")
        print(f"   Mean Quality Score: {report['mean_quality_score']:.1f}/100")
        print(f"   Records Below 80: {report['records_below_80']}")
        
        print("\n🔍 SUSPICIOUS VALUE DETECTION:")
        for col, stats in report['details'].items():
            if isinstance(stats, dict) and 'flagged_total' in stats:
                print(f"   {col}:")
                print(f"      Flagged: {stats['flagged_total']} ({stats['flagged_percentage']:.1f}%)")
                print(f"      Round Numbers: {stats['round_numbers']}")
                print(f"      Outliers: {stats['outliers']}")
        
        # Save annotated data
        OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "geospatial_plots")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        annotated.to_csv(os.path.join(OUTPUT_DIR, "state_data_quality_annotated.csv"), index=False)
        print(f"\n✅ Annotated data saved to {OUTPUT_DIR}")
    else:
        print(f"❌ Data file not found: {DATA_FILE}")
