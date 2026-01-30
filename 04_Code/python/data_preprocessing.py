#!/usr/bin/env python3
"""
Smart Socks - Data Preprocessing
ELEC-E7840 Smart Wearables (Aalto University)

Preprocesses raw sensor data: normalization, outlier removal,
interpolation for missing samples, and quality checks.

Usage:
    python data_preprocessing.py --input ../03_Data/raw/ --output ../03_Data/processed/
"""

import argparse
import os
import sys
import glob
import numpy as np
import pandas as pd
from scipy import interpolate, stats
from tqdm import tqdm
import matplotlib.pyplot as plt

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import SENSORS, DATA_QUALITY

# Sensor channel names from config
SENSOR_NAMES = SENSORS['names']

# Data quality thresholds from config
EXPECTED_INTERVAL_MS = 1000 // 50  # From HARDWARE['sample_rate_hz']
MAX_GAP_MS = DATA_QUALITY['max_acceptable_gap_ms']

# Note: EXPECTED_INTERVAL_MS and MAX_GAP_MS now imported from config above


def detect_outliers(data, method='iqr', threshold=3):
    """
    Detect outliers in sensor data.
    
    Args:
        data: numpy array
        method: 'iqr' or 'zscore'
        threshold: Threshold for outlier detection
    
    Returns:
        Boolean array indicating outliers
    """
    if method == 'iqr':
        Q1 = np.percentile(data, 25)
        Q3 = np.percentile(data, 75)
        IQR = Q3 - Q1
        lower = Q1 - threshold * IQR
        upper = Q3 + threshold * IQR
        return (data < lower) | (data > upper)
    
    elif method == 'zscore':
        zscores = np.abs(stats.zscore(data))
        return zscores > threshold
    
    return np.zeros(len(data), dtype=bool)


def interpolate_gaps(df, max_gap_ms=MAX_GAP_MS):
    """
    Interpolate missing samples in the data.
    
    Args:
        df: DataFrame with time_ms column
        max_gap_ms: Maximum gap to interpolate
    
    Returns:
        DataFrame with interpolated values
    """
    if len(df) < 2:
        return df
    
    # Calculate time differences
    time_diffs = df['time_ms'].diff().dropna()
    
    # Check for gaps
    gaps = time_diffs[time_diffs > max_gap_ms]
    
    if len(gaps) == 0:
        return df
    
    # Create regular time grid
    start_time = df['time_ms'].iloc[0]
    end_time = df['time_ms'].iloc[-1]
    regular_times = np.arange(start_time, end_time + EXPECTED_INTERVAL_MS, EXPECTED_INTERVAL_MS)
    
    # Interpolate each sensor
    interpolated_data = {'time_ms': regular_times}
    
    for sensor in SENSOR_NAMES:
        if sensor in df.columns:
            # Use linear interpolation
            f = interpolate.interp1d(
                df['time_ms'], 
                df[sensor], 
                kind='linear',
                bounds_error=False,
                fill_value='extrapolate'
            )
            interpolated_data[sensor] = f(regular_times)
    
    return pd.DataFrame(interpolated_data)


def remove_outliers(df, method='iqr', threshold=3):
    """
    Remove or correct outliers in sensor data.
    
    Args:
        df: DataFrame with sensor data
        method: Outlier detection method
        threshold: Detection threshold
    
    Returns:
        DataFrame with outliers corrected
    """
    df_clean = df.copy()
    outlier_count = 0
    
    for sensor in SENSOR_NAMES:
        if sensor in df_clean.columns:
            data = df_clean[sensor].values
            outlier_mask = detect_outliers(data, method, threshold)
            
            if np.any(outlier_mask):
                outlier_count += np.sum(outlier_mask)
                # Replace outliers with interpolated values
                valid_indices = np.where(~outlier_mask)[0]
                outlier_indices = np.where(outlier_mask)[0]
                
                if len(valid_indices) > 0:
                    df_clean.loc[outlier_mask, sensor] = np.interp(
                        outlier_indices,
                        valid_indices,
                        data[valid_indices]
                    )
    
    return df_clean, outlier_count


def normalize_data(df, method='minmax'):
    """
    Normalize sensor data.
    
    Args:
        df: DataFrame with sensor data
        method: 'minmax', 'standard', or 'robust'
    
    Returns:
        Normalized DataFrame and scaling parameters
    """
    df_norm = df.copy()
    scaling_params = {}
    
    for sensor in SENSOR_NAMES:
        if sensor in df_norm.columns:
            data = df_norm[sensor].values
            
            if method == 'minmax':
                min_val = np.min(data)
                max_val = np.max(data)
                if max_val > min_val:
                    df_norm[sensor] = (data - min_val) / (max_val - min_val)
                scaling_params[sensor] = {'min': min_val, 'max': max_val}
            
            elif method == 'standard':
                mean = np.mean(data)
                std = np.std(data)
                if std > 0:
                    df_norm[sensor] = (data - mean) / std
                scaling_params[sensor] = {'mean': mean, 'std': std}
            
            elif method == 'robust':
                median = np.median(data)
                mad = np.median(np.abs(data - median))
                if mad > 0:
                    df_norm[sensor] = (data - median) / mad
                scaling_params[sensor] = {'median': median, 'mad': mad}
    
    return df_norm, scaling_params


def check_data_quality(df):
    """
    Perform quality checks on the data.
    
    Args:
        df: DataFrame with sensor data
    
    Returns:
        Dictionary of quality metrics
    """
    quality = {
        'total_samples': len(df),
        'duration_ms': df['time_ms'].iloc[-1] - df['time_ms'].iloc[0] if len(df) > 0 else 0,
        'expected_samples': 0,
        'missing_samples': 0,
        'dropout_rate': 0.0,
        'valid': True,
        'issues': []
    }
    
    if len(df) < 2:
        quality['valid'] = False
        quality['issues'].append('Insufficient samples')
        return quality
    
    # Check for missing samples
    duration = quality['duration_ms']
    quality['expected_samples'] = int(duration / EXPECTED_INTERVAL_MS) + 1
    quality['missing_samples'] = quality['expected_samples'] - quality['total_samples']
    quality['dropout_rate'] = quality['missing_samples'] / quality['expected_samples'] if quality['expected_samples'] > 0 else 0
    
    # Check for gaps
    time_diffs = df['time_ms'].diff().dropna()
    large_gaps = time_diffs[time_diffs > MAX_GAP_MS]
    
    if len(large_gaps) > 0:
        quality['large_gaps'] = len(large_gaps)
        quality['max_gap_ms'] = large_gaps.max()
        if len(large_gaps) > 5:
            quality['issues'].append(f'Too many large gaps: {len(large_gaps)}')
    
    # Check for flat signals (sensor may be disconnected)
    for sensor in SENSOR_NAMES:
        if sensor in df.columns:
            unique_values = df[sensor].nunique()
            if unique_values == 1:
                quality['issues'].append(f'{sensor} has constant value (disconnected?)')
            elif unique_values < 10:
                quality['issues'].append(f'{sensor} has low variance ({unique_values} unique values)')
    
    # Validate dropout rate
    if quality['dropout_rate'] > 0.2:  # More than 20% missing
        quality['valid'] = False
        quality['issues'].append(f'High dropout rate: {quality["dropout_rate"]:.2%}')
    
    return quality


def plot_quality_check(df, quality, output_path=None):
    """
    Plot data quality visualization.
    
    Args:
        df: DataFrame with sensor data
        quality: Quality metrics dictionary
        output_path: Path to save plot
    """
    fig, axes = plt.subplots(5, 2, figsize=(15, 20))
    axes = axes.flatten()
    
    time_sec = df['time_ms'] / 1000
    
    for idx, sensor in enumerate(SENSOR_NAMES):
        ax = axes[idx]
        if sensor in df.columns:
            ax.plot(time_sec, df[sensor], label=sensor, linewidth=0.5)
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('ADC Value')
            ax.set_title(sensor)
            ax.grid(True, alpha=0.3)
    
    # Add quality info as text
    fig.text(0.5, 0.02, f"Dropout: {quality['dropout_rate']:.2%} | Issues: {', '.join(quality['issues']) if quality['issues'] else 'None'}", 
             ha='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout(rect=[0, 0.03, 1, 1])
    
    if output_path:
        plt.savefig(output_path, dpi=150)
        plt.close()
    else:
        plt.show()


def process_file(input_path, output_dir, plot_dir=None, normalize_method=None):
    """
    Process a single CSV file.
    
    Args:
        input_path: Path to input CSV
        output_dir: Directory for output CSV
        plot_dir: Directory for quality plots (optional)
        normalize_method: Normalization method (optional)
    
    Returns:
        Quality metrics dictionary
    """
    # Load data
    df = pd.read_csv(input_path)
    
    # Check quality
    quality = check_data_quality(df)
    quality['filename'] = os.path.basename(input_path)
    
    # Interpolate gaps
    df = interpolate_gaps(df)
    
    # Remove outliers
    df, outlier_count = remove_outliers(df)
    quality['outliers_removed'] = outlier_count
    
    # Normalize if requested
    if normalize_method:
        df, scaling_params = normalize_data(df, normalize_method)
        quality['scaling_params'] = scaling_params
    
    # Re-check quality after preprocessing
    quality_final = check_data_quality(df)
    quality['valid_after_preprocessing'] = quality_final['valid']
    
    # Save processed data
    output_path = os.path.join(output_dir, os.path.basename(input_path))
    df.to_csv(output_path, index=False)
    
    # Generate quality plot if requested
    if plot_dir:
        os.makedirs(plot_dir, exist_ok=True)
        plot_path = os.path.join(plot_dir, os.path.basename(input_path).replace('.csv', '.png'))
        plot_quality_check(df, quality, plot_path)
    
    return quality


def main():
    parser = argparse.ArgumentParser(
        description='Smart Socks Data Preprocessing'
    )
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Directory containing raw CSV files'
    )
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output directory for processed CSV files'
    )
    parser.add_argument(
        '--plots', '-p',
        help='Directory for quality check plots (optional)'
    )
    parser.add_argument(
        '--normalize',
        choices=['minmax', 'standard', 'robust'],
        help='Normalization method (optional)'
    )
    parser.add_argument(
        '--report',
        help='Path to save quality report CSV'
    )

    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    # Find all CSV files
    csv_files = glob.glob(os.path.join(args.input, '**/*.csv'), recursive=True)
    
    if not csv_files:
        print(f"No CSV files found in {args.input}")
        return 1

    print(f"Found {len(csv_files)} CSV files")
    print(f"Normalization: {args.normalize if args.normalize else 'None'}")
    print()

    # Process each file
    all_quality = []
    valid_count = 0
    invalid_count = 0
    
    for filepath in tqdm(csv_files, desc="Processing files"):
        try:
            quality = process_file(
                filepath, 
                args.output, 
                args.plots,
                args.normalize
            )
            all_quality.append(quality)
            
            if quality['valid']:
                valid_count += 1
            else:
                invalid_count += 1
                
        except Exception as e:
            print(f"\nError processing {filepath}: {e}")
            all_quality.append({
                'filename': os.path.basename(filepath),
                'valid': False,
                'issues': [f'Processing error: {str(e)}']
            })
            invalid_count += 1

    # Save quality report
    if args.report:
        report_df = pd.DataFrame(all_quality)
        report_df.to_csv(args.report, index=False)
        print(f"\nSaved quality report to {args.report}")
    
    # Print summary
    print("\n" + "="*60)
    print("Preprocessing Summary")
    print("="*60)
    print(f"Total files: {len(csv_files)}")
    print(f"Valid: {valid_count}")
    print(f"Invalid: {invalid_count}")
    
    if invalid_count > 0:
        print("\nInvalid files:")
        for q in all_quality:
            if not q['valid']:
                print(f"  - {q['filename']}: {', '.join(q.get('issues', []))}")

    return 0


if __name__ == '__main__':
    exit(main())
