#!/usr/bin/env python3
"""
Smart Socks - Automated Data Validation
ELEC-E7840 Smart Wearables (Aalto University)

Provides live validation during data collection and post-collection
quality reports. Wraps existing data_validation.py for streaming use.

Usage:
    from auto_validator import LiveValidator
    validator = LiveValidator()

    # During collection
    ok, issues = validator.validate_buffer(buffer, activity)

    # After collection
    report = validator.post_collection_report(filepath)
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple

from config import SENSORS, HARDWARE, DATA_QUALITY
from data_validation import validate_sensor_data, DataQualityReport


class LiveValidator:
    """Wraps existing data validation for streaming/live use during collection."""

    def __init__(self, validation_interval_s: float = None):
        if validation_interval_s is None:
            validation_interval_s = DATA_QUALITY.get('live_validation_interval_s', 5)
        self.validation_interval_s = validation_interval_s
        self._last_validation_time = -validation_interval_s

    def validate_buffer(self, buffer: List[Dict], activity: str) -> Tuple[bool, List[str]]:
        """
        Validate current data buffer during live collection.

        Args:
            buffer: List of sample dicts from collector (keys: time_ms + sensor names)
            activity: Current activity label

        Returns:
            Tuple of (is_ok, list_of_issues)
        """
        issues = []

        if len(buffer) < 2:
            return True, []

        df = pd.DataFrame(buffer)

        # Run existing validation
        report = validate_sensor_data(df, filename=f"live_{activity}")
        issues.extend(report.issues)

        # Additional: temporal jump check
        temporal_threshold = DATA_QUALITY.get('temporal_jump_threshold', 1000)
        for sensor in SENSORS['names']:
            if sensor not in df.columns:
                continue
            diffs = df[sensor].diff().abs().dropna()
            jump_count = (diffs > temporal_threshold).sum()
            if jump_count > 0:
                issues.append(
                    f"Temporal jumps in {sensor}: {jump_count} samples "
                    f"with ADC change > {temporal_threshold}"
                )

        # Duration check: need enough samples for meaningful validation
        min_samples = int(HARDWARE['sample_rate_hz'] * 0.5)  # at least 0.5s
        if len(buffer) < min_samples:
            issues.append(
                f"Buffer too short for reliable validation: "
                f"{len(buffer)} samples (need >= {min_samples})"
            )

        is_ok = len(issues) == 0
        return is_ok, issues

    def post_collection_report(self, filepath: Path) -> DataQualityReport:
        """
        Run full validation on a saved CSV file after collection.

        Args:
            filepath: Path to saved CSV file

        Returns:
            DataQualityReport with comprehensive results
        """
        filepath = Path(filepath)
        df = pd.read_csv(filepath)

        report = validate_sensor_data(df, filename=str(filepath.name))

        # Additional: minimum duration check
        min_duration_s = DATA_QUALITY.get('min_recording_duration_s', 10)
        actual_duration_s = report.duration_ms / 1000.0
        if actual_duration_s < min_duration_s:
            report.issues.append(
                f"Recording too short: {actual_duration_s:.1f}s "
                f"(minimum: {min_duration_s}s)"
            )
            report.is_valid = False

        # Additional: sample completeness check
        expected_samples = int(actual_duration_s * HARDWARE['sample_rate_hz'])
        if expected_samples > 0:
            completeness = report.total_samples / expected_samples
            if completeness < 0.8:
                report.warnings.append(
                    f"Low sample completeness: {completeness:.1%} "
                    f"({report.total_samples}/{expected_samples} samples)"
                )

        # Additional: temporal jump check on full file
        temporal_threshold = DATA_QUALITY.get('temporal_jump_threshold', 1000)
        for sensor in SENSORS['names']:
            if sensor not in df.columns:
                continue
            diffs = df[sensor].diff().abs().dropna()
            jump_count = (diffs > temporal_threshold).sum()
            if jump_count > 0:
                report.warnings.append(
                    f"Temporal jumps in {sensor}: {jump_count} samples "
                    f"with ADC change > {temporal_threshold}"
                )

        return report

    def should_validate(self, elapsed_seconds: float) -> bool:
        """
        Check if it's time for the next validation cycle.

        Args:
            elapsed_seconds: Time elapsed since recording started

        Returns:
            True if validation should run now
        """
        if elapsed_seconds >= self._last_validation_time + self.validation_interval_s:
            self._last_validation_time = elapsed_seconds
            return True
        return False
