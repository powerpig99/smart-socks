#!/usr/bin/env python3
"""
Smart Socks - Feature Extraction Utilities
ELEC-E7840 Smart Wearables (Aalto University)

Shared feature extraction functions used by both training pipeline
and real-time classifiers to ensure consistency.
"""

import numpy as np
from scipy import stats
from scipy.fft import fft

from config import SENSORS, HARDWARE

# Backwards compatibility
SENSOR_NAMES = SENSORS['names']
SAMPLING = {'rate_hz': HARDWARE['sample_rate_hz']}

# Sensor groupings for 6-sensor design (4 pressure + 2 stretch)
PRESSURE_SENSORS = SENSORS['pressure_sensors']
STRETCH_SENSORS = SENSORS['stretch_sensors']
HEEL_ZONES = SENSORS['heel_zones']
BALL_ZONES = SENSORS['ball_zones']
LEFT_PRESSURE = SENSORS['left_pressure']
RIGHT_PRESSURE = SENSORS['right_pressure']


def extract_statistical_features(data, sensor_names=SENSOR_NAMES):
    """
    Extract statistical features from a window of sensor data.
    
    Args:
        data: numpy array of shape (n_samples, n_sensors) or list of dicts
        sensor_names: List of sensor names (default from config)
    
    Returns:
        Dictionary of feature names and values
    """
    # Convert list of dicts to array if needed
    if isinstance(data, list):
        data = np.array([[s[sensor] for sensor in sensor_names] for s in data])
    
    features = {}
    n_samples = len(data)
    
    for i, sensor in enumerate(sensor_names):
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
        
        # Zero crossing rate (fixed formula)
        if n_samples > 1:
            zcr = np.sum(np.abs(np.diff(np.sign(sensor_data - np.mean(sensor_data)))) / 2)
            features[f'{sensor}_zcr'] = zcr / (n_samples - 1)
        else:
            features[f'{sensor}_zcr'] = 0
        
        # Root mean square
        features[f'{sensor}_rms'] = np.sqrt(np.mean(sensor_data**2))
        
        # Energy (sum of squares)
        features[f'{sensor}_energy'] = np.sum(sensor_data**2)
        
        # Slope (linear trend)
        if n_samples > 1:
            slope, _, _, _, _ = stats.linregress(np.arange(n_samples), sensor_data)
            features[f'{sensor}_slope'] = slope
        else:
            features[f'{sensor}_slope'] = 0
    
    return features


def extract_cross_sensor_features(data, sensor_names=SENSOR_NAMES):
    """
    Extract features that combine multiple sensors.
    
    Designed for 6-sensor layout: 2 pressure + 1 stretch per leg
    - Pressure: L_P_Heel, L_P_Ball, R_P_Heel, R_P_Ball
    - Stretch: L_S_Knee, R_S_Knee
    
    Args:
        data: numpy array of shape (n_samples, n_sensors) or list of dicts
        sensor_names: List of sensor names (default from config)
    
    Returns:
        Dictionary of cross-sensor features
    """
    # Convert list of dicts to array if needed
    if isinstance(data, list):
        data = np.array([[s[sensor] for sensor in sensor_names] for s in data])
    
    # Build index mapping for sensor names
    sensor_idx = {name: i for i, name in enumerate(sensor_names)}
    
    features = {}
    
    # Helper to get column by sensor name
    def get_col(name):
        return data[:, sensor_idx[name]] if name in sensor_idx else np.zeros(data.shape[0])
    
    # ===== PRESSURE FEATURES =====
    # Calculate total pressure per leg (heel + ball)
    left_pressure_sum = sum(get_col(s) for s in LEFT_PRESSURE)
    right_pressure_sum = sum(get_col(s) for s in RIGHT_PRESSURE)
    
    features['left_pressure_mean'] = np.mean(left_pressure_sum)
    features['left_pressure_std'] = np.std(left_pressure_sum)
    features['right_pressure_mean'] = np.mean(right_pressure_sum)
    features['right_pressure_std'] = np.std(right_pressure_sum)
    features['left_right_pressure_ratio'] = np.mean(left_pressure_sum) / (np.mean(right_pressure_sum) + 1e-6)
    
    # Heel vs Ball pressure ratio (hindfoot vs forefoot)
    left_heel = get_col('L_P_Heel')
    left_ball = get_col('L_P_Ball')
    right_heel = get_col('R_P_Heel')
    right_ball = get_col('R_P_Ball')
    
    features['left_heel_ball_ratio'] = np.mean(left_heel) / (np.mean(left_ball) + 1e-6)
    features['right_heel_ball_ratio'] = np.mean(right_heel) / (np.mean(right_ball) + 1e-6)
    
    # ===== STRETCH FEATURES =====
    left_knee = get_col('L_S_Knee')
    right_knee = get_col('R_S_Knee')
    
    features['left_knee_mean'] = np.mean(left_knee)
    features['left_knee_std'] = np.std(left_knee)
    features['right_knee_mean'] = np.mean(right_knee)
    features['right_knee_std'] = np.std(right_knee)
    features['left_right_knee_ratio'] = np.mean(left_knee) / (np.mean(right_knee) + 1e-6)
    
    # ===== COMBINED FEATURES =====
    # Total activity per leg (pressure + stretch)
    left_total = left_pressure_sum + left_knee
    right_total = right_pressure_sum + right_knee
    
    features['left_total_mean'] = np.mean(left_total)
    features['right_total_mean'] = np.mean(right_total)
    features['left_right_total_ratio'] = np.mean(left_total) / (np.mean(right_total) + 1e-6)
    
    # Balance between legs (correlation of total activity)
    if len(left_total) > 1 and np.std(left_total) > 0 and np.std(right_total) > 0:
        features['left_right_correlation'] = np.corrcoef(left_total, right_total)[0, 1]
    else:
        features['left_right_correlation'] = 0
    
    # Pressure vs Stretch correlation (within each leg)
    if np.std(left_pressure_sum) > 0 and np.std(left_knee) > 0:
        features['left_pressure_stretch_corr'] = np.corrcoef(left_pressure_sum, left_knee)[0, 1]
    else:
        features['left_pressure_stretch_corr'] = 0
        
    if np.std(right_pressure_sum) > 0 and np.std(right_knee) > 0:
        features['right_pressure_stretch_corr'] = np.corrcoef(right_pressure_sum, right_knee)[0, 1]
    else:
        features['right_pressure_stretch_corr'] = 0
    
    return features


def extract_frequency_features(data, sample_rate=SAMPLING['rate_hz'], sensor_names=SENSOR_NAMES):
    """
    Extract frequency domain features using FFT.
    
    Args:
        data: numpy array of shape (n_samples, n_sensors) or list of dicts
        sample_rate: Sampling rate in Hz (default from config)
        sensor_names: List of sensor names (default from config)
    
    Returns:
        Dictionary of frequency features
    """
    # Convert list of dicts to array if needed
    if isinstance(data, list):
        data = np.array([[s[sensor] for sensor in sensor_names] for s in data])
    
    features = {}
    n_samples = len(data)
    
    for i, sensor in enumerate(sensor_names):
        sensor_data = data[:, i]
        
        # Compute FFT
        fft_vals = np.abs(fft(sensor_data))
        freqs = np.fft.fftfreq(n_samples, d=1/sample_rate)
        
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
    features = {}
    features.update(extract_statistical_features(data, sensor_names))
    features.update(extract_cross_sensor_features(data, sensor_names))
    features.update(extract_frequency_features(data, sample_rate, sensor_names))
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
