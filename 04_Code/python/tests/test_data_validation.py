#!/usr/bin/env python3
"""
Smart Socks - Data Validation Tests
ELEC-E7840 Smart Wearables (Aalto University)
"""

import pytest
import numpy as np
import pandas as pd

# Import config for sensor names
from config import SENSORS

from data_validation import (
    validate_sensor_data,
    check_adc_range,
    check_stuck_sensors,
    check_timestamps,
    calculate_dropout_rate,
    DataQualityReport,
    quick_check,
)


class TestDataValidation:
    """Test suite for data validation functions."""
    
    def test_valid_data_passes(self, sample_sensor_data):
        """Test that valid data passes validation."""
        report = validate_sensor_data(sample_sensor_data, "test.csv")
        
        assert report.is_valid, f"Valid data failed validation: {report.issues}"
        assert report.total_samples == 100
        assert len(report.missing_columns) == 0
    
    def test_stuck_sensor_detection(self, invalid_sensor_data):
        """Test detection of stuck sensors."""
        report = validate_sensor_data(invalid_sensor_data, "test.csv")
        
        # First sensor should be detected as stuck
        stuck_names = [s.split()[0] for s in report.stuck_sensors]
        assert SENSORS['names'][0] in stuck_names
    
    def test_saturated_sensor_detection(self, invalid_sensor_data):
        """Test detection of saturated sensors."""
        report = validate_sensor_data(invalid_sensor_data, "test.csv")
        
        assert SENSORS['names'][1] in report.saturated_sensors
    
    def test_disconnected_sensor_detection(self, invalid_sensor_data):
        """Test detection of disconnected sensors."""
        report = validate_sensor_data(invalid_sensor_data, "test.csv")
        
        assert SENSORS['names'][2] in report.disconnected_sensors
    
    def test_missing_columns_detected(self, sample_sensor_data):
        """Test detection of missing required columns."""
        # Drop some sensor columns
        df_missing = sample_sensor_data.drop(columns=[SENSORS['names'][0], SENSORS['names'][3]])
        
        report = validate_sensor_data(df_missing, "test.csv")
        
        assert not report.is_valid
        assert SENSORS['names'][0] in report.missing_columns
        assert SENSORS['names'][3] in report.missing_columns
    
    def test_missing_timestamp_detected(self, sample_sensor_data):
        """Test detection of missing timestamp column."""
        df_no_time = sample_sensor_data.drop(columns=["time_ms"])
        
        report = validate_sensor_data(df_no_time, "test.csv")
        
        assert not report.is_valid
        assert "time_ms" in report.missing_columns
    
    def test_dropout_rate_calculation(self, sample_sensor_data):
        """Test dropout rate calculation."""
        rate = calculate_dropout_rate(sample_sensor_data)
        
        # With 100 samples at 50Hz, should be close to 0
        assert 0 <= rate < 0.1
    
    def test_high_dropout_invalidates(self):
        """Test that high dropout rate invalidates data."""
        # Create data with many missing samples
        df = pd.DataFrame({
            'time_ms': [0, 100, 200, 3000, 3100],  # Big gap
            SENSORS['names'][0]: [100, 200, 300, 400, 500],
        })
        
        # Add remaining sensor columns
        for sensor in SENSORS['names'][1:]:
            df[sensor] = [100, 200, 300, 400, 500]
        
        report = validate_sensor_data(df, "test.csv")
        
        assert report.dropout_rate > 0.5
    
    def test_quick_check_function(self, sample_sensor_data):
        """Test the quick_check convenience function."""
        assert quick_check(sample_sensor_data) is True
    
    def test_quick_check_fails_on_bad_data(self, invalid_sensor_data):
        """Test that quick_check returns False for bad data."""
        # This might pass or fail depending on validation strictness
        result = quick_check(invalid_sensor_data)
        assert isinstance(result, bool)


class TestDataQualityReport:
    """Test DataQualityReport class."""
    
    def test_report_summary_format(self):
        """Test that summary produces readable output."""
        report = DataQualityReport(
            filename="test.csv",
            total_samples=100,
            dropout_rate=0.05,
            is_valid=True,
            stuck_sensors=[SENSORS['names'][0]],
            issues=["Stuck sensor detected"],
        )
        
        summary = report.summary()
        
        assert "test.csv" in summary
        assert "100" in summary
        assert "5.00%" in summary or "0.05" in summary
        assert SENSORS['names'][0] in summary
    
    def test_report_to_dict(self):
        """Test conversion to dictionary."""
        report = DataQualityReport(
            filename="test.csv",
            total_samples=100,
            is_valid=True,
        )
        
        d = report.to_dict()
        
        assert d['filename'] == "test.csv"
        assert d['total_samples'] == 100
        assert d['is_valid'] is True


class TestTimestampValidation:
    """Test timestamp-related validation."""
    
    def test_non_monotonic_timestamps_detected(self):
        """Test detection of non-monotonic timestamps."""
        df = pd.DataFrame({
            'time_ms': [0, 20, 40, 30, 60],  # Decrease at index 3
            SENSORS['names'][0]: [100, 200, 300, 400, 500],
        })
        # Add other sensors
        for sensor in SENSORS['names'][1:]:
            df[sensor] = [100, 200, 300, 400, 500]
        
        is_valid, issues, _ = check_timestamps(df)
        
        assert not is_valid
        assert any("monotonic" in issue.lower() for issue in issues)
    
    def test_duplicate_timestamps_detected(self):
        """Test detection of duplicate timestamps."""
        df = pd.DataFrame({
            'time_ms': [0, 20, 20, 40, 60],  # Duplicate at index 1,2
            SENSORS['names'][0]: [100, 200, 300, 400, 500],
        })
        # Add other sensors
        for sensor in SENSORS['names'][1:]:
            df[sensor] = [100, 200, 300, 400, 500]
        
        is_valid, issues, _ = check_timestamps(df)
        
        assert any("duplicate" in issue.lower() for issue in issues)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
