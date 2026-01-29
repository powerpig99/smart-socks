#!/usr/bin/env python3
"""
Smart Socks - Configuration
ELEC-E7840 Smart Wearables (Aalto University)

Centralized configuration for all Python modules.
Modify values here to change behavior across the entire pipeline.
"""

import os
from dataclasses import dataclass
from typing import List, Dict, Any


# =============================================================================
# HARDWARE CONFIGURATION
# =============================================================================

HARDWARE = {
    # ESP32S3 XIAO ADC Configuration
    'adc_resolution_bits': 12,
    'adc_max_value': 4095,  # 2^12 - 1
    'adc_min_value': 0,
    
    # Sampling Configuration
    'sample_rate_hz': 50,
    'sample_interval_ms': 20,  # 1000 / 50
    
    # Serial Communication
    'serial_baudrate': 115200,
    'serial_timeout': 1,
    'serial_reset_delay': 2,  # seconds to wait after connection
    
    # BLE Configuration
    'ble_device_name': 'SmartSocks',
    'ble_service_uuid': '4fafc201-1fb5-459e-8fcc-c5c9c331914b',
    'ble_characteristic_uuid': 'beb5483e-36e1-4688-b7f5-ea07361b26a8',
    'ble_connection_timeout': 10,
}


# =============================================================================
# SENSOR CONFIGURATION
# Updated Jan 29, 2026: New design with pressure + stretch sensors
# =============================================================================

SENSORS = {
    # New design: 2 pressure sensors per sock + 1 stretch sensor per knee pad
    # Total: 6 sensors (4 pressure + 2 stretch)
    'count': 6,
    'names': [
        # Left leg
        "L_P_Heel",    # Left Pressure - Heel
        "L_P_Ball",    # Left Pressure - Ball of foot
        "L_S_Knee",    # Left Stretch - Knee pad
        # Right leg
        "R_P_Heel",    # Right Pressure - Heel
        "R_P_Ball",    # Right Pressure - Ball of foot
        "R_S_Knee",    # Right Stretch - Knee pad
    ],
    
    # Sensor zones per leg
    'left_leg': ["L_P_Heel", "L_P_Ball", "L_S_Knee"],
    'right_leg': ["R_P_Heel", "R_P_Ball", "R_S_Knee"],
    
    # Pressure sensors (for pressure-based features)
    'pressure_sensors': ["L_P_Heel", "L_P_Ball", "R_P_Heel", "R_P_Ball"],
    
    # Stretch sensors (for stretch-based features)
    'stretch_sensors': ["L_S_Knee", "R_S_Knee"],
    
    # Zone groupings for feature extraction
    'heel_zones': ["L_P_Heel", "R_P_Heel"],
    'ball_zones': ["L_P_Ball", "R_P_Ball"],
    'knee_zones': ["L_S_Knee", "R_S_Knee"],
    
    # Left vs Right comparisons
    'left_pressure': ["L_P_Heel", "L_P_Ball"],
    'right_pressure': ["R_P_Heel", "R_P_Ball"],
}


# =============================================================================
# WINDOWING CONFIGURATION
# =============================================================================

WINDOWING = {
    'window_size_ms': 1000,      # 1 second windows
    'stride_ms': 500,            # 50% overlap
    'min_samples_ratio': 0.8,    # Minimum 80% of expected samples
    
    # Derived values (don't modify directly)
    'samples_per_window': 50,  # 50 samples at 50Hz (1 second window)
}


# =============================================================================
# DATA QUALITY THRESHOLDS
# =============================================================================

DATA_QUALITY = {
    # Dropout detection
    'max_acceptable_gap_ms': 50,      # Maximum gap for interpolation
    'max_dropout_rate': 0.20,          # 20% maximum dropout
    
    # Sensor validation
    'stuck_sensor_threshold': 5,       # Unique values below this = stuck
    'min_sensor_variance': 10,         # Minimum std dev for active sensor
    
    # Outlier detection
    'outlier_method': 'iqr',           # 'iqr' or 'zscore'
    'outlier_threshold': 3.0,          # IQR multiplier or z-score threshold
    
    # ADC validation
    'adc_saturation_threshold': 4000,  # Near max value = saturated
    'adc_noise_threshold': 10,         # Near min value = disconnected/noisy
}


# =============================================================================
# FEATURE EXTRACTION CONFIGURATION
# =============================================================================

FEATURES = {
    # Statistical features to extract
    'statistical': {
        'mean': True,
        'std': True,
        'min': True,
        'max': True,
        'range': True,
        'q25': True,
        'q50': True,
        'q75': True,
        'skewness': True,
        'kurtosis': True,
        'zcr': True,        # Zero crossing rate
        'rms': True,        # Root mean square
        'energy': True,
        'slope': True,      # Linear trend
    },
    
    # Cross-sensor features
    'cross_sensor': {
        'total_pressure': True,
        'fore_hind_ratio': True,
        'medial_lateral_ratio': True,
        'left_right_ratio': True,
        'left_right_correlation': True,
    },
    
    # Frequency features
    'frequency': {
        'spectral_energy': True,
        'spectral_entropy': True,
        'dominant_freq': True,
        'spectral_centroid': True,
    },
}


# =============================================================================
# MODEL CONFIGURATION
# =============================================================================

MODEL = {
    # Random Forest parameters
    'random_forest': {
        'n_estimators': 100,
        'max_depth': 20,
        'min_samples_split': 5,
        'min_samples_leaf': 2,
        'random_state': 42,
        'n_jobs': -1,  # Use all CPU cores
    },
    
    # Hyperparameter tuning (optional)
    'tuning': {
        'enabled': False,
        'cv_folds': 5,
        'param_grid': {
            'n_estimators': [50, 100, 200],
            'max_depth': [10, 20, None],
            'min_samples_split': [2, 5, 10],
        },
    },
    
    # Training configuration
    'training': {
        'test_size': 0.3,              # 30% for testing
        'validation_size': 0.2,        # 20% of training for validation
        'cross_subject_validation': True,
        'stratified_split': True,
    },
    
    # Model saving
    'versioning': {
        'enabled': True,
        'keep_top_n': 5,              # Keep top 5 models by accuracy
        'include_timestamp': True,
    },
}


# =============================================================================
# ACTIVITY LABELS
# =============================================================================

ACTIVITIES = {
    'all': [
        'walking_forward', 'walking_backward',
        'stairs_up', 'stairs_down',
        'sitting_floor', 'sitting_crossed',
        'sit_to_stand', 'stand_to_sit',
        'standing_upright', 'standing_lean_left', 'standing_lean_right'
    ],
    
    'categories': {
        'walking': ['walking_forward', 'walking_backward'],
        'stairs': ['stairs_up', 'stairs_down'],
        'sitting': ['sitting_floor', 'sitting_crossed'],
        'transitions': ['sit_to_stand', 'stand_to_sit'],
        'standing': ['standing_upright', 'standing_lean_left', 'standing_lean_right'],
    },
    
    'requires_step_counting': [
        'walking_forward', 'walking_backward',
        'stairs_up', 'stairs_down'
    ],
}


# =============================================================================
# REAL-TIME CLASSIFICATION
# =============================================================================

REALTIME = {
    # Classification smoothing
    'smoothing_window': 5,        # Number of predictions to average
    'confidence_threshold': 0.6,  # Minimum confidence for prediction
    
    # Step counting
    'step_counting': {
        'enabled': True,
        'threshold': 2000,        # Pressure threshold for step detection
        'min_step_interval_ms': 300,  # Minimum time between steps
        'use_adaptive_threshold': False,
    },
    
    # Latency monitoring
    'max_acceptable_latency_ms': 100,
    'log_latency_stats': True,
}


# =============================================================================
# PATHS & DIRECTORIES
# =============================================================================

PATHS = {
    'data_raw': '../../03_Data/raw/',
    'data_processed': '../../03_Data/processed/',
    'data_features': '../../03_Data/features/',
    'data_calibration': '../../03_Data/calibration/',
    'analysis': '../../05_Analysis/',
    'models': '../../05_Analysis/models/',
    'reports': '../../06_Presentation/report/',
}


# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

LOGGING = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'file': 'smart_socks.log',
    'console': True,
    'file_output': True,
}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_feature_count() -> int:
    """Calculate total number of features based on configuration."""
    sensor_count = SENSORS['count']
    
    # Per-sensor features
    stat_count = sum(FEATURES['statistical'].values())
    freq_count = sum(FEATURES['frequency'].values())
    per_sensor = stat_count + freq_count
    
    # Cross-sensor features
    cross_count = sum(FEATURES['cross_sensor'].values())
    
    return (sensor_count * per_sensor) + cross_count


def validate_config() -> List[str]:
    """Validate configuration values and return list of issues."""
    issues = []
    
    # Check sample rate consistency
    expected_interval = 1000 / HARDWARE['sample_rate_hz']
    if abs(expected_interval - HARDWARE['sample_interval_ms']) > 0.1:
        issues.append(f"Sample interval ({HARDWARE['sample_interval_ms']}) "
                     f"doesn't match sample rate ({HARDWARE['sample_rate_hz']} Hz)")
    
    # Check window configuration
    if WINDOWING['stride_ms'] > WINDOWING['window_size_ms']:
        issues.append("Window stride cannot be larger than window size")
    
    # Check paths exist
    for name, path in PATHS.items():
        if not os.path.exists(path):
            issues.append(f"Path does not exist: {name} = {path}")
    
    return issues


def print_config():
    """Print current configuration for debugging."""
    print("=" * 60)
    print("SMART SOCKS CONFIGURATION")
    print("=" * 60)
    print(f"\nHardware:")
    print(f"  ADC Resolution: {HARDWARE['adc_resolution_bits']}-bit (0-{HARDWARE['adc_max_value']})")
    print(f"  Sample Rate: {HARDWARE['sample_rate_hz']} Hz")
    print(f"\nSensors: {SENSORS['count']} total")
    for sensor in SENSORS['names']:
        print(f"  - {sensor}")
    print(f"\nWindowing:")
    print(f"  Window Size: {WINDOWING['window_size_ms']} ms")
    print(f"  Stride: {WINDOWING['stride_ms']} ms")
    print(f"  Expected Features: ~{get_feature_count()}")
    print(f"\nActivities: {len(ACTIVITIES['all'])}")
    print("=" * 60)


# Run validation on import
if __name__ == '__main__':
    print_config()
    issues = validate_config()
    if issues:
        print("\n⚠️  Configuration Issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✅ Configuration valid")
