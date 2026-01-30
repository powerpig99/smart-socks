#!/usr/bin/env python3
"""
Smart Socks - Feature Extraction
ELEC-E7840 Smart Wearables (Aalto University)

Extracts time-domain and frequency-domain features from raw sensor data
for machine learning classification.

Usage:
    python feature_extraction.py --input ../03_Data/raw/ --output ../03_Data/features/
"""

import argparse
import os
import glob
import numpy as np
import pandas as pd
from scipy import stats
from scipy.fft import fft
from tqdm import tqdm

from config import SENSORS, HARDWARE, WINDOWING, ACTIVITIES

# Backwards compatibility
SENSOR_NAMES = SENSORS['names']
SAMPLING = {'rate_hz': HARDWARE['sample_rate_hz']}

# Window configuration (from config)
WINDOW_SIZE_MS = WINDOWING['window_size_ms']
WINDOW_STRIDE_MS = WINDOWING['stride_ms']
SAMPLE_RATE_HZ = SAMPLING['rate_hz']
SAMPLES_PER_WINDOW = WINDOWING['samples_per_window']


def extract_activity_from_filename(filename):
    """Extract activity name from filename by matching against known activities.
    
    Args:
        filename: Filename like 'S01_walking_forward_20260115_143022.csv'
    
    Returns:
        Activity name string, or 'unknown' if not found
    """
    # Remove extension and split
    name = filename.replace('.csv', '')
    
    # Try to match each known activity
    for activity in ACTIVITIES['all']:
        if activity in name:
            return activity
    
    # Fallback: try old parsing method for unknown activities
    parts = name.split('_')
    if len(parts) >= 3:
        # Assume format: SUBJECT_ACTIVITY_TIMESTAMP
        # Activity is everything between subject (first part) and timestamp (last 2 parts)
        return '_'.join(parts[1:-2])
    
    return 'unknown'


def extract_statistical_features(data):
    """
    Extract statistical features from a window of sensor data.
    
    Args:
        data: numpy array of shape (n_samples, n_sensors)
    
    Returns:
        Dictionary of feature names and values
    """
    features = {}
    
    for i, sensor in enumerate(SENSOR_NAMES):
        sensor_data = data[:, i]
        
        # Basic statistics
        features[f'{sensor}_mean'] = np.mean(sensor_data)
        features[f'{sensor}_std'] = np.std(sensor_data)
        features[f'{sensor}_min'] = np.min(sensor_data)
        features[f'{sensor}_max'] = np.max(sensor_data)
        features[f'{sensor}_range'] = np.max(sensor_data) - np.min(sensor_data)
        
        # Percentiles
        features[f'{sensor}_q25'] = np.percentile(sensor_data, 25)
        features[f'{sensor}_q50'] = np.percentile(sensor_data, 50)
        features[f'{sensor}_q75'] = np.percentile(sensor_data, 75)
        
        # Shape features
        features[f'{sensor}_skewness'] = stats.skew(sensor_data)
        features[f'{sensor}_kurtosis'] = stats.kurtosis(sensor_data)
        
        # Zero crossing rate
        zero_crossings = np.sum(np.diff(np.signbit(sensor_data - np.mean(sensor_data))))
        features[f'{sensor}_zcr'] = zero_crossings / len(sensor_data)
        
        # Root mean square
        features[f'{sensor}_rms'] = np.sqrt(np.mean(sensor_data**2))
        
        # Energy (sum of squares)
        features[f'{sensor}_energy'] = np.sum(sensor_data**2)
        
        # Slope (linear trend)
        if len(sensor_data) > 1:
            slope, _, _, _, _ = stats.linregress(np.arange(len(sensor_data)), sensor_data)
            features[f'{sensor}_slope'] = slope
        else:
            features[f'{sensor}_slope'] = 0
    
    return features


def extract_cross_sensor_features(data):
    """
    Extract features that combine multiple sensors.
    
    Args:
        data: numpy array of shape (n_samples, n_sensors)
    
    Returns:
        Dictionary of cross-sensor features
    """
    features = {}
    
    # Get sensor indices from config
    left_indices = [SENSOR_NAMES.index(s) for s in SENSORS['left_leg']]
    right_indices = [SENSOR_NAMES.index(s) for s in SENSORS['right_leg']]
    pressure_indices = [SENSOR_NAMES.index(s) for s in SENSORS['pressure_sensors']]
    stretch_indices = [SENSOR_NAMES.index(s) for s in SENSORS['stretch_sensors']]
    
    # Calculate total per leg (pressure + stretch)
    left_total = np.sum(data[:, left_indices], axis=1)
    right_total = np.sum(data[:, right_indices], axis=1)
    
    features['left_total_mean'] = np.mean(left_total)
    features['left_total_std'] = np.std(left_total)
    features['right_total_mean'] = np.mean(right_total)
    features['right_total_std'] = np.std(right_total)
    features['left_right_ratio'] = np.mean(left_total) / (np.mean(right_total) + 1e-6)
    
    # Pressure sensors only (for pressure-based ratios)
    left_pressure_data = data[:, [SENSOR_NAMES.index(s) for s in SENSORS['left_pressure']]]
    right_pressure_data = data[:, [SENSOR_NAMES.index(s) for s in SENSORS['right_pressure']]]
    
    # Heel vs Ball pressure ratio
    left_heel = left_pressure_data[:, 0]  # L_P_Heel
    left_ball = left_pressure_data[:, 1]  # L_P_Ball
    right_heel = right_pressure_data[:, 0]  # R_P_Heel
    right_ball = right_pressure_data[:, 1]  # R_P_Ball
    
    # Heel vs Ball pressure ratio
    features['left_heel_ball_ratio'] = np.mean(left_heel) / (np.mean(left_ball) + 1e-6)
    features['right_heel_ball_ratio'] = np.mean(right_heel) / (np.mean(right_ball) + 1e-6)
    
    # Knee stretch sensors
    left_knee_idx = SENSOR_NAMES.index('L_S_Knee')
    right_knee_idx = SENSOR_NAMES.index('R_S_Knee')
    left_knee = data[:, left_knee_idx]
    right_knee = data[:, right_knee_idx]
    
    features['left_knee_mean'] = np.mean(left_knee)
    features['left_knee_std'] = np.std(left_knee)
    features['right_knee_mean'] = np.mean(right_knee)
    features['right_knee_std'] = np.std(right_knee)
    features['left_right_knee_ratio'] = np.mean(left_knee) / (np.mean(right_knee) + 1e-6)
    
    # Balance between feet (correlation)
    if len(left_total) > 1 and np.std(left_total) > 0 and np.std(right_total) > 0:
        features['left_right_correlation'] = np.corrcoef(left_total, right_total)[0, 1]
    else:
        features['left_right_correlation'] = 0
    
    return features


def extract_frequency_features(data, sample_rate=None):
    """
    Extract frequency domain features using FFT.
    
    Args:
        data: numpy array of shape (n_samples, n_sensors)
    
    Returns:
        Dictionary of frequency features
    """
    features = {}
    
    for i, sensor in enumerate(SENSOR_NAMES):
        sensor_data = data[:, i]
        
        # Compute FFT
        fft_vals = np.abs(fft(sensor_data))
        freqs = np.fft.fftfreq(len(sensor_data), d=1/SAMPLE_RATE_HZ)
        
        # Keep only positive frequencies
        positive_freqs = freqs[:len(freqs)//2]
        positive_fft = fft_vals[:len(fft_vals)//2]
        
        # Spectral features
        features[f'{sensor}_spectral_energy'] = np.sum(positive_fft**2)
        features[f'{sensor}_spectral_entropy'] = stats.entropy(positive_fft + 1e-10)
        
        # Dominant frequency
        if len(positive_fft) > 0:
            features[f'{sensor}_dominant_freq'] = positive_freqs[np.argmax(positive_fft)]
        else:
            features[f'{sensor}_dominant_freq'] = 0
        
        # Spectral centroid
        if np.sum(positive_fft) > 0:
            features[f'{sensor}_spectral_centroid'] = np.sum(positive_freqs * positive_fft) / np.sum(positive_fft)
        else:
            features[f'{sensor}_spectral_centroid'] = 0
    
    return features


def extract_features_from_window(data):
    """
    Extract all features from a single window of data.
    
    Args:
        data: numpy array of shape (n_samples, n_sensors)
    
    Returns:
        Dictionary of all features
    """
    features = {}
    features.update(extract_statistical_features(data))
    features.update(extract_cross_sensor_features(data))
    features.update(extract_frequency_features(data))
    return features


def segment_data(df, window_size_ms=WINDOW_SIZE_MS, stride_ms=WINDOW_STRIDE_MS):
    """
    Segment continuous data into overlapping windows.
    
    Args:
        df: DataFrame with sensor data
        window_size_ms: Window size in milliseconds
        stride_ms: Stride between windows in milliseconds
    
    Returns:
        List of DataFrames, each representing a window
    """
    windows = []
    start_time = df['time_ms'].iloc[0]
    end_time = df['time_ms'].iloc[-1]
    
    current_start = start_time
    while current_start + window_size_ms <= end_time:
        window_df = df[
            (df['time_ms'] >= current_start) & 
            (df['time_ms'] < current_start + window_size_ms)
        ]
        if len(window_df) >= SAMPLES_PER_WINDOW * 0.8:  # At least 80% of expected samples
            windows.append(window_df)
        current_start += stride_ms
    
    return windows


def process_file(filepath, label=None):
    """
    Process a single CSV file and extract features from all windows.
    
    Args:
        filepath: Path to CSV file
        label: Activity label (if None, extracted from filename)
    
    Returns:
        DataFrame with features for each window
    """
    # Extract label from filename if not provided
    if label is None:
        filename = os.path.basename(filepath)
        label = extract_activity_from_filename(filename)
    
    # Load data
    df = pd.read_csv(filepath)
    
    # Ensure all sensor columns exist
    missing_cols = [col for col in SENSOR_NAMES if col not in df.columns]
    if missing_cols:
        print(f"Warning: Missing columns in {filepath}: {missing_cols}")
        return None
    
    # Segment into windows
    windows = segment_data(df)
    
    if not windows:
        print(f"Warning: No valid windows extracted from {filepath}")
        return None
    
    # Extract features from each window
    feature_list = []
    for window_df in windows:
        data = window_df[SENSOR_NAMES].values
        features = extract_features_from_window(data)
        features['label'] = label
        features['subject'] = os.path.basename(filepath).split('_')[0]
        feature_list.append(features)
    
    return pd.DataFrame(feature_list)


def extract_all_features(data, sample_rate=SAMPLING['rate_hz'], sensor_names=SENSOR_NAMES):
    """
    Extract all features from a window of data.
    
    Args:
        data: numpy array of shape (n_samples, n_sensors) or list of dicts
        sample_rate: Sampling rate in Hz (default from config)
        sensor_names: List of sensor names (default from config)
    
    Returns:
        Dictionary of all features
    """
    # Convert list of dicts to array if needed
    if isinstance(data, list):
        data = np.array([[s[sensor] for sensor in sensor_names] for s in data])
    
    features = {}
    features.update(extract_statistical_features(data))
    features.update(extract_cross_sensor_features(data))
    features.update(extract_frequency_features(data, sample_rate))
    return features


def features_to_array(features_dict, feature_order=None):
    """
    Convert feature dictionary to numpy array.
    
    Args:
        features_dict: Dictionary of features
        feature_order: Optional list to enforce specific feature order
    
    Returns:
        numpy array of shape (1, n_features)
    """
    if feature_order is None:
        feature_order = sorted(features_dict.keys())
    
    return np.array([[features_dict[f] for f in feature_order]])


def get_feature_names(sensor_names=SENSOR_NAMES):
    """
    Get the list of feature names in consistent order.
    
    Args:
        sensor_names: List of sensor names
    
    Returns:
        List of feature names
    """
    # Create dummy data to get feature names
    dummy_data = np.zeros((50, len(sensor_names)))
    features = extract_all_features(dummy_data, sensor_names=sensor_names)
    return sorted(features.keys())


def main():
    parser = argparse.ArgumentParser(
        description='Smart Socks Feature Extraction'
    )
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Directory containing raw CSV files'
    )
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output directory for feature CSV files'
    )
    parser.add_argument(
        '--window-size',
        type=int,
        default=WINDOW_SIZE_MS,
        help=f'Window size in milliseconds (default: {WINDOW_SIZE_MS})'
    )
    parser.add_argument(
        '--stride',
        type=int,
        default=WINDOW_STRIDE_MS,
        help=f'Stride between windows in milliseconds (default: {WINDOW_STRIDE_MS})'
    )

    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    # Find all CSV files
    csv_files = glob.glob(os.path.join(args.input, '**/*.csv'), recursive=True)
    
    if not csv_files:
        print(f"No CSV files found in {args.input}")
        return 1

    print(f"Found {len(csv_files)} CSV files")
    print(f"Window size: {args.window_size}ms, Stride: {args.stride}ms")
    print()

    # Process each file
    all_features = []
    for filepath in tqdm(csv_files, desc="Processing files"):
        try:
            features_df = process_file(filepath)
            if features_df is not None:
                all_features.append(features_df)
        except Exception as e:
            print(f"Error processing {filepath}: {e}")

    if not all_features:
        print("No features extracted!")
        return 1

    # Combine all features
    combined_df = pd.concat(all_features, ignore_index=True)
    
    # Save features
    output_path = os.path.join(args.output, 'features_all.csv')
    combined_df.to_csv(output_path, index=False)
    
    print(f"\nExtracted {len(combined_df)} feature vectors")
    print(f"Features per vector: {len(combined_df.columns) - 2}")  # Exclude label and subject
    print(f"Activities: {combined_df['label'].unique()}")
    print(f"Subjects: {combined_df['subject'].unique()}")
    print(f"\nSaved to: {output_path}")

    return 0


if __name__ == '__main__':
    exit(main())
