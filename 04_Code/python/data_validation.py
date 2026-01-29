#!/usr/bin/env python3
"""
Smart Socks - Data Validation
ELEC-E7840 Smart Wearables (Aalto University)

Validates sensor data quality and provides detailed quality reports.

Usage:
    from data_validation import validate_sensor_data, DataQualityReport
    report = validate_sensor_data(df)
    print(report.summary())
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import logging

from config import SENSORS, HARDWARE, DATA_QUALITY


logger = logging.getLogger(__name__)


@dataclass
class DataQualityReport:
    """Data class for storing data quality check results."""
    filename: str = ""
    total_samples: int = 0
    duration_ms: float = 0.0
    expected_samples: int = 0
    dropout_count: int = 0
    dropout_rate: float = 0.0
    
    # Sensor-specific issues
    stuck_sensors: List[str] = field(default_factory=list)
    saturated_sensors: List[str] = field(default_factory=list)
    disconnected_sensors: List[str] = field(default_factory=list)
    
    # Data integrity
    missing_columns: List[str] = field(default_factory=list)
    timestamp_issues: List[str] = field(default_factory=list)
    outlier_count: int = 0
    
    # Overall assessment
    is_valid: bool = True
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def summary(self) -> str:
        """Generate human-readable summary."""
        lines = [
            f"Data Quality Report: {self.filename}",
            "=" * 50,
            f"Samples: {self.total_samples} (expected: {self.expected_samples})",
            f"Duration: {self.duration_ms/1000:.1f} seconds",
            f"Dropout Rate: {self.dropout_rate:.2%}",
            f"Valid: {'Yes' if self.is_valid else 'No'}",
        ]
        
        if self.stuck_sensors:
            lines.append(f"⚠️  Stuck Sensors: {', '.join(self.stuck_sensors)}")
        if self.saturated_sensors:
            lines.append(f"⚠️  Saturated Sensors: {', '.join(self.saturated_sensors)}")
        if self.disconnected_sensors:
            lines.append(f"❌ Disconnected: {', '.join(self.disconnected_sensors)}")
        
        if self.issues:
            lines.append("\nIssues:")
            for issue in self.issues:
                lines.append(f"  ❌ {issue}")
        
        if self.warnings:
            lines.append("\nWarnings:")
            for warning in self.warnings:
                lines.append(f"  ⚠️  {warning}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'filename': self.filename,
            'total_samples': self.total_samples,
            'duration_ms': self.duration_ms,
            'dropout_rate': self.dropout_rate,
            'is_valid': self.is_valid,
            'stuck_sensors': self.stuck_sensors,
            'saturated_sensors': self.saturated_sensors,
            'disconnected_sensors': self.disconnected_sensors,
            'issues_count': len(self.issues),
            'warnings_count': len(self.warnings),
        }


def check_adc_range(df: pd.DataFrame) -> Tuple[List[str], List[str]]:
    """
    Check if sensor values are within valid ADC range.
    
    Returns:
        Tuple of (saturated_sensors, disconnected_sensors)
    """
    saturated = []
    disconnected = []
    
    for sensor in SENSORS['names']:
        if sensor not in df.columns:
            continue
        
        values = df[sensor]
        max_val = values.max()
        min_val = values.min()
        
        # Check for saturation
        if max_val > DATA_QUALITY['adc_saturation_threshold']:
            if (values > DATA_QUALITY['adc_saturation_threshold']).sum() > len(values) * 0.1:
                saturated.append(sensor)
        
        # Check for disconnection/noise
        if max_val < DATA_QUALITY['adc_noise_threshold']:
            disconnected.append(sensor)
    
    return saturated, disconnected


def check_stuck_sensors(df: pd.DataFrame) -> List[str]:
    """Identify sensors with near-constant values."""
    stuck = []
    
    for sensor in SENSORS['names']:
        if sensor not in df.columns:
            continue
        
        unique_count = df[sensor].nunique()
        if unique_count < DATA_QUALITY['stuck_sensor_threshold']:
            stuck.append(f"{sensor} ({unique_count} unique values)")
        elif df[sensor].std() < DATA_QUALITY['min_sensor_variance']:
            stuck.append(f"{sensor} (low variance: {df[sensor].std():.2f})")
    
    return stuck


def check_timestamps(df: pd.DataFrame) -> Tuple[bool, List[str], int]:
    """
    Check timestamp integrity.
    
    Returns:
        Tuple of (is_valid, issues, dropout_count)
    """
    issues = []
    dropout_count = 0
    
    if 'time_ms' not in df.columns:
        return False, ["Missing timestamp column 'time_ms'"], 0
    
    timestamps = df['time_ms']
    
    # Check monotonicity
    if not timestamps.is_monotonic_increasing:
        issues.append("Timestamps not monotonically increasing")
    
    # Check for duplicate timestamps
    if timestamps.duplicated().any():
        dup_count = timestamps.duplicated().sum()
        issues.append(f"Found {dup_count} duplicate timestamps")
    
    # Check for gaps (dropouts)
    time_diffs = timestamps.diff().dropna()
    expected_interval = HARDWARE['sample_interval_ms']
    max_gap = DATA_QUALITY['max_acceptable_gap_ms']
    
    gaps = time_diffs[time_diffs > max_gap]
    dropout_count = len(gaps)
    
    if dropout_count > 0:
        max_gap_val = gaps.max()
        issues.append(f"Found {dropout_count} gaps > {max_gap}ms (max: {max_gap_val:.0f}ms)")
    
    return len(issues) == 0, issues, dropout_count


def check_required_columns(df: pd.DataFrame) -> List[str]:
    """Check if all required columns are present."""
    missing = []
    
    # Always require timestamp
    if 'time_ms' not in df.columns:
        missing.append('time_ms')
    
    # Check sensor columns
    for sensor in SENSORS['names']:
        if sensor not in df.columns:
            missing.append(sensor)
    
    return missing


def calculate_dropout_rate(df: pd.DataFrame) -> float:
    """Calculate the percentage of missing samples."""
    if 'time_ms' not in df.columns or len(df) < 2:
        return 0.0
    
    duration = df['time_ms'].iloc[-1] - df['time_ms'].iloc[0]
    expected_samples = int(duration / HARDWARE['sample_interval_ms']) + 1
    actual_samples = len(df)
    
    if expected_samples <= 0:
        return 0.0
    
    return (expected_samples - actual_samples) / expected_samples


def validate_sensor_data(df: pd.DataFrame, filename: str = "") -> DataQualityReport:
    """
    Comprehensive data validation.
    
    Args:
        df: DataFrame with sensor data
        filename: Optional filename for reporting
    
    Returns:
        DataQualityReport with validation results
    """
    report = DataQualityReport(filename=filename)
    report.total_samples = len(df)
    
    logger.info(f"Validating {filename}: {len(df)} samples")
    
    # Check required columns
    report.missing_columns = check_required_columns(df)
    if report.missing_columns:
        report.issues.append(f"Missing columns: {', '.join(report.missing_columns)}")
        report.is_valid = False
        logger.error(f"Missing columns: {report.missing_columns}")
        return report
    
    # Calculate duration
    if 'time_ms' in df.columns and len(df) > 0:
        report.duration_ms = df['time_ms'].iloc[-1] - df['time_ms'].iloc[0]
        report.expected_samples = int(report.duration_ms / HARDWARE['sample_interval_ms']) + 1
    
    # Check timestamps
    timestamp_valid, timestamp_issues, dropout_count = check_timestamps(df)
    report.timestamp_issues = timestamp_issues
    report.dropout_count = dropout_count
    report.dropout_rate = calculate_dropout_rate(df)
    report.issues.extend(timestamp_issues)
    
    # Check ADC range
    saturated, disconnected = check_adc_range(df)
    report.saturated_sensors = saturated
    report.disconnected_sensors = disconnected
    
    if saturated:
        report.warnings.append(f"Saturated sensors: {', '.join(saturated)}")
    if disconnected:
        report.issues.append(f"Possibly disconnected sensors: {', '.join(disconnected)}")
    
    # Check for stuck sensors
    report.stuck_sensors = check_stuck_sensors(df)
    if report.stuck_sensors:
        report.issues.append(f"Stuck sensors: {', '.join(report.stuck_sensors)}")
    
    # Validate dropout rate
    if report.dropout_rate > DATA_QUALITY['max_dropout_rate']:
        report.issues.append(
            f"High dropout rate: {report.dropout_rate:.2%} "
            f"(max allowed: {DATA_QUALITY['max_dropout_rate']:.2%})"
        )
        report.is_valid = False
    
    # Final validity check
    if report.issues and not report.is_valid:
        logger.warning(f"Data validation failed for {filename}")
    elif report.warnings:
        logger.info(f"Data validation passed with warnings for {filename}")
    else:
        logger.info(f"Data validation passed for {filename}")
    
    return report


def batch_validate_files(filepaths: List[str]) -> pd.DataFrame:
    """
    Validate multiple files and return summary DataFrame.
    
    Args:
        filepaths: List of CSV file paths
    
    Returns:
        DataFrame with validation results for all files
    """
    results = []
    
    for filepath in filepaths:
        try:
            df = pd.read_csv(filepath)
            report = validate_sensor_data(df, filename=filepath)
            results.append(report.to_dict())
        except Exception as e:
            logger.error(f"Failed to validate {filepath}: {e}")
            results.append({
                'filename': filepath,
                'is_valid': False,
                'issues_count': 1,
                'error': str(e),
            })
    
    return pd.DataFrame(results)


def get_quality_summary(df_reports: pd.DataFrame) -> Dict:
    """Generate summary statistics from batch validation reports."""
    total = len(df_reports)
    valid = df_reports['is_valid'].sum()
    
    return {
        'total_files': total,
        'valid_files': int(valid),
        'invalid_files': int(total - valid),
        'validity_rate': valid / total if total > 0 else 0,
        'avg_dropout_rate': df_reports['dropout_rate'].mean(),
        'files_with_stuck_sensors': df_reports['stuck_sensors'].apply(lambda x: len(x) > 0 if isinstance(x, list) else False).sum(),
        'files_with_saturated_sensors': df_reports['saturated_sensors'].apply(lambda x: len(x) > 0 if isinstance(x, list) else False).sum(),
    }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def quick_check(df: pd.DataFrame) -> bool:
    """
    Quick validation check suitable for pipeline use.
    
    Returns True if data is valid, False otherwise.
    """
    report = validate_sensor_data(df)
    return report.is_valid


def validate_and_report(df: pd.DataFrame, filename: str = "") -> Tuple[bool, str]:
    """
    Validate data and return result with message.
    
    Returns:
        Tuple of (is_valid, message)
    """
    report = validate_sensor_data(df, filename)
    return report.is_valid, report.summary()


if __name__ == '__main__':
    # Example usage
    import glob
    import os
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Find sample data files
    data_dir = '../../03_Data/raw/'
    if os.path.exists(data_dir):
        files = glob.glob(os.path.join(data_dir, '**/*.csv'), recursive=True)[:5]
        
        if files:
            print(f"Validating {len(files)} files...\n")
            reports_df = batch_validate_files(files)
            print(reports_df.to_string())
            
            print("\n" + "=" * 50)
            print("SUMMARY")
            print("=" * 50)
            summary = get_quality_summary(reports_df)
            for key, value in summary.items():
                print(f"  {key}: {value}")
        else:
            print(f"No CSV files found in {data_dir}")
    else:
        print(f"Data directory not found: {data_dir}")
        print("This is expected if you haven't collected data yet.")
