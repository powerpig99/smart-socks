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
