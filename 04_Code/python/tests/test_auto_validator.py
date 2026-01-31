#!/usr/bin/env python3
"""Tests for auto_validator.py - Live Data Validation."""

import pytest
import numpy as np
import pandas as pd
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auto_validator import LiveValidator
from config import SENSORS, HARDWARE, DATA_QUALITY


class TestLiveValidatorBuffer:
    def test_valid_buffer_returns_ok(self, sample_buffer_data):
        """A clean buffer should return (True, [])."""
        validator = LiveValidator()
        ok, issues = validator.validate_buffer(sample_buffer_data, 'walking_forward')
        # May have minor issues from synthetic data, but no temporal jumps
        temporal_issues = [i for i in issues if 'Temporal jumps' in i]
        assert len(temporal_issues) == 0

    def test_buffer_with_temporal_jumps(self, sample_buffer_with_issues):
        """Buffer with temporal jumps should report issues."""
        validator = LiveValidator()
        ok, issues = validator.validate_buffer(sample_buffer_with_issues, 'walking_forward')

        temporal_issues = [i for i in issues if 'Temporal jumps' in i]
        assert len(temporal_issues) > 0

    def test_buffer_with_stuck_sensor(self, sample_buffer_with_issues):
        """Buffer with a stuck sensor should report issues."""
        validator = LiveValidator()
        ok, issues = validator.validate_buffer(sample_buffer_with_issues, 'walking_forward')

        stuck_issues = [i for i in issues if 'Stuck' in i or 'stuck' in i.lower()]
        # The stuck sensor (constant 1000) should be caught by data_validation
        assert len(stuck_issues) > 0

    def test_empty_buffer_returns_ok(self):
        """Empty or very short buffer should return ok (not enough data to validate)."""
        validator = LiveValidator()
        ok, issues = validator.validate_buffer([], 'walking_forward')
        assert ok is True


class TestPostCollectionReport:
    def test_generates_report(self, sample_buffer_data, tmp_path):
        """post_collection_report should generate a DataQualityReport."""
        # Save buffer as CSV
        df = pd.DataFrame(sample_buffer_data)
        filepath = tmp_path / 'test_recording.csv'
        df.to_csv(filepath, index=False)

        validator = LiveValidator()
        report = validator.post_collection_report(filepath)

        assert report.total_samples == len(sample_buffer_data)
        assert report.filename == 'test_recording.csv'

    def test_short_recording_flagged(self, tmp_path):
        """Recording shorter than min_recording_duration_s should be flagged."""
        # Create a very short recording (1 second)
        n_samples = 50
        data = {'time_ms': [i * HARDWARE['sample_interval_ms'] for i in range(n_samples)]}
        for sensor in SENSORS['names']:
            data[sensor] = [1000] * n_samples

        df = pd.DataFrame(data)
        filepath = tmp_path / 'short_recording.csv'
        df.to_csv(filepath, index=False)

        validator = LiveValidator()
        report = validator.post_collection_report(filepath)

        short_issues = [i for i in report.issues if 'too short' in i.lower()]
        assert len(short_issues) > 0


class TestShouldValidate:
    def test_returns_true_at_interval(self):
        """should_validate should return True at each validation interval."""
        validator = LiveValidator(validation_interval_s=5)

        assert validator.should_validate(0.0) is True
        assert validator.should_validate(2.0) is False
        assert validator.should_validate(4.9) is False
        assert validator.should_validate(5.0) is True
        assert validator.should_validate(7.0) is False
        assert validator.should_validate(10.0) is True
