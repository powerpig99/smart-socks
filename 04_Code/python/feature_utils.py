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

from config import SENSOR_NAMES, SAMPLING


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
    
    Args:
        data: numpy array of shape (n_samples, n_sensors) or list of dicts
        sensor_names: List of sensor names (default from config)
    
    Returns:
        Dictionary of cross-sensor features
    """
    # Convert list of dicts to array if needed
    if isinstance(data, list):
        data = np.array([[s[sensor] for sensor in sensor_names] for s in data])
    
    features = {}
    n_sensors = len(sensor_names)
    n_left = n_sensors // 2  # Assume first half are left foot
    
    # Calculate total pressure per foot
    left_total = np.sum(data[:, 0:n_left], axis=1)
    right_total = np.sum(data[:, n_left:n_sensors], axis=1)
    
    features['left_total_mean'] = np.mean(left_total)
    features['left_total_std'] = np.std(left_total)
    features['right_total_mean'] = np.mean(right_total)
    features['right_total_std'] = np.std(right_total)
    features['left_right_ratio'] = np.mean(left_total) / (np.mean(right_total) + 1e-6)
    
    # Forefoot vs hindfoot pressure ratio (assuming: heel, arch = hind, metaM, metaL, toe = fore)
    left_forefoot = np.sum(data[:, 2:n_left], axis=1)  # MetaM, MetaL, Toe
    left_hindfoot = np.sum(data[:, 0:2], axis=1)  # Heel, Arch
    right_forefoot = np.sum(data[:, n_left+2:n_sensors], axis=1)
    right_hindfoot = np.sum(data[:, n_left:n_left+2], axis=1)
    
    features['left_fore_hind_ratio'] = np.mean(left_forefoot) / (np.mean(left_hindfoot) + 1e-6)
    features['right_fore_hind_ratio'] = np.mean(right_forefoot) / (np.mean(right_hindfoot) + 1e-6)
    
    # Medial vs lateral pressure (for metatarsals: index 2 and 3)
    if n_left >= 4:
        left_medial = data[:, 2]  # MetaM
        left_lateral = data[:, 3]  # MetaL
        features['left_medial_lateral_ratio'] = np.mean(left_medial) / (np.mean(left_lateral) + 1e-6)
    else:
        features['left_medial_lateral_ratio'] = 0
    
    if n_sensors >= n_left + 4:
        right_medial = data[:, n_left + 2]  # MetaM
        right_lateral = data[:, n_left + 3]  # MetaL
        features['right_medial_lateral_ratio'] = np.mean(right_medial) / (np.mean(right_lateral) + 1e-6)
    else:
        features['right_medial_lateral_ratio'] = 0
    
    # Balance between feet (correlation)
    if len(left_total) > 1 and np.std(left_total) > 0 and np.std(right_total) > 0:
        features['left_right_correlation'] = np.corrcoef(left_total, right_total)[0, 1]
    else:
        features['left_right_correlation'] = 0
    
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
