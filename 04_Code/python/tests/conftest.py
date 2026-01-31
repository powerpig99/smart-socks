#!/usr/bin/env python3
"""
Smart Socks - Pytest Configuration
ELEC-E7840 Smart Wearables (Aalto University)

Shared fixtures and configuration for all tests.
"""

import pytest
import numpy as np
import pandas as pd
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import SENSORS, HARDWARE


@pytest.fixture
def sample_sensor_data():
    """Generate sample sensor data for testing."""
    np.random.seed(42)
    n_samples = 100
    
    data = {
        'time_ms': np.arange(n_samples) * HARDWARE['sample_interval_ms'],
    }
    
    # Generate realistic sensor values with some patterns
    for sensor in SENSORS['names']:
        # Base value with noise
        base = np.random.randint(500, 1500)
        noise = np.random.normal(0, 50, n_samples)
        
        # Add some periodic component (simulating walking)
        t = np.linspace(0, 4*np.pi, n_samples)
        signal = np.sin(t) * 200
        
        data[sensor] = np.clip(base + noise + signal, 0, HARDWARE['adc_max_value']).astype(int)
    
    return pd.DataFrame(data)


@pytest.fixture
def invalid_sensor_data():
    """Generate invalid sensor data with issues for testing validation."""
    np.random.seed(42)
    n_samples = 100
    
    data = {
        'time_ms': np.arange(n_samples) * HARDWARE['sample_interval_ms'],
    }
    
    for i, sensor in enumerate(SENSORS['names']):
        if i == 0:
            # Stuck sensor (constant value)
            data[sensor] = np.full(n_samples, 500)
        elif i == 1:
            # Saturated sensor
            data[sensor] = np.full(n_samples, 4090)
        elif i == 2:
            # Disconnected (near zero)
            data[sensor] = np.full(n_samples, 5)
        else:
            # Normal
            data[sensor] = np.random.randint(500, 1500, n_samples)
    
    return pd.DataFrame(data)


@pytest.fixture
def missing_timestamp_data():
    """Generate data with timestamp issues."""
    np.random.seed(42)
    n_samples = 100
    
    data = {
        'time_ms': np.sort(np.random.choice(np.arange(2000), n_samples, replace=False)),
    }
    
    for sensor in SENSORS['names']:
        data[sensor] = np.random.randint(500, 1500, n_samples)
    
    return pd.DataFrame(data)


@pytest.fixture
def temp_output_dir(tmp_path):
    """Provide a temporary output directory."""
    return tmp_path / "output"


@pytest.fixture(scope="session")
def test_data_dir():
    """Provide path to test data directory."""
    path = os.path.join(os.path.dirname(__file__), 'fixtures')
    os.makedirs(path, exist_ok=True)
    return path


@pytest.fixture
def sample_features_df():
    """Generate a DataFrame mimicking features_all.csv output."""
    from sklearn.datasets import make_classification

    np.random.seed(42)
    n_samples = 200
    n_features = 20

    # Create feature names that resemble real pipeline output
    feature_names = []
    for sensor in SENSORS['names'][:3]:
        for stat in ['mean', 'std', 'min']:
            feature_names.append(f'{sensor}_{stat}')
    # Add cross-sensor features to reach n_features
    cross_features = [
        'total_pressure', 'fore_hind_ratio', 'left_right_balance',
        'left_right_correlation', 'spectral_energy_L_P_Heel',
    ]
    feature_names.extend(cross_features[:n_features - len(feature_names)])
    # Pad if needed
    while len(feature_names) < n_features:
        feature_names.append(f'extra_feature_{len(feature_names)}')

    X, y_int = make_classification(
        n_samples=n_samples, n_features=n_features, n_informative=10,
        n_classes=3, random_state=42
    )

    activities = ['walking_forward', 'stairs_up', 'standing_upright']
    y = np.array([activities[i] for i in y_int])

    subjects = np.array([f'S0{(i % 2) + 1}' for i in range(n_samples)])

    df = pd.DataFrame(X, columns=feature_names)
    df['label'] = y
    df['subject'] = subjects
    return df


@pytest.fixture
def trained_rf_model(sample_features_df):
    """Train a small RandomForest on sample_features_df."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler

    df = sample_features_df
    feature_names = [c for c in df.columns if c not in ('label', 'subject')]
    X = df[feature_names].values
    y = df['label'].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = RandomForestClassifier(
        n_estimators=10, max_depth=5, random_state=42
    )
    model.fit(X_scaled, y)

    return model, scaler, feature_names


@pytest.fixture
def sample_buffer_data():
    """List of dicts mimicking collector.py buffer format with smooth transitions."""
    np.random.seed(42)
    n_samples = 250  # 5 seconds at 50Hz
    buffer = []
    # Generate smooth signals (base + small noise) to avoid temporal jumps
    base_values = {}
    for sensor in SENSORS['names']:
        t = np.linspace(0, 4 * np.pi, n_samples)
        base_values[sensor] = (1200 + np.sin(t) * 200 +
                               np.random.normal(0, 20, n_samples)).astype(int)
        base_values[sensor] = np.clip(base_values[sensor], 0, 4095)
    for i in range(n_samples):
        sample = {'time_ms': i * HARDWARE['sample_interval_ms']}
        for sensor in SENSORS['names']:
            sample[sensor] = int(base_values[sensor][i])
        buffer.append(sample)
    return buffer


@pytest.fixture
def sample_buffer_with_issues():
    """Buffer with stuck sensor and temporal jump problems."""
    np.random.seed(42)
    n_samples = 250
    buffer = []
    for i in range(n_samples):
        sample = {'time_ms': i * HARDWARE['sample_interval_ms']}
        for j, sensor in enumerate(SENSORS['names']):
            if j == 0:
                # Stuck sensor
                sample[sensor] = 1000
            elif j == 1 and i == 50:
                # Temporal jump
                sample[sensor] = 4000
            else:
                sample[sensor] = int(np.random.randint(500, 2000))
        # Fill sensor 1 for non-jump samples
        if SENSORS['names'][1] not in sample or sample.get(SENSORS['names'][1]) is None:
            sample[SENSORS['names'][1]] = int(np.random.randint(500, 2000))
        buffer.append(sample)
    # Ensure sensor 1 has a jump: set surrounding values to normal range
    buffer[49][SENSORS['names'][1]] = 800
    buffer[50][SENSORS['names'][1]] = 4000
    buffer[51][SENSORS['names'][1]] = 850
    return buffer
