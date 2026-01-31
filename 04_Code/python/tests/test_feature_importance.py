#!/usr/bin/env python3
"""Tests for feature_importance.py - Feature Importance Analysis."""

import pytest
import numpy as np
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from feature_importance import (
    analyze_feature_importance,
    group_features_by_sensor,
    generate_edge_config,
)


class TestAnalyzeFeatureImportance:
    def test_returns_expected_keys(self, trained_rf_model):
        """Results should contain all expected top-level keys."""
        model, scaler, feature_names = trained_rf_model
        results = analyze_feature_importance(model, feature_names)

        assert 'total_features' in results
        assert 'top_features' in results
        assert 'thresholds' in results
        assert 'feature_groups' in results

    def test_thresholds_monotonically_increasing(self, trained_rf_model):
        """90% < 95% < 99% in number of features required."""
        model, scaler, feature_names = trained_rf_model
        results = analyze_feature_importance(model, feature_names)

        n_90 = results['thresholds']['90_percent']['n_features']
        n_95 = results['thresholds']['95_percent']['n_features']
        n_99 = results['thresholds']['99_percent']['n_features']

        assert n_90 <= n_95 <= n_99


class TestGroupFeaturesBySensor:
    def test_groups_sensor_features_correctly(self):
        """L_P_Heel_mean should be grouped under sensor L_P_Heel."""
        features = ['L_P_Heel_mean', 'L_P_Heel_std', 'R_P_Ball_min']
        groups = group_features_by_sensor(features)

        assert 'L_P_Heel' in groups['by_sensor']
        assert 'L_P_Heel_mean' in groups['by_sensor']['L_P_Heel']
        assert 'R_P_Ball' in groups['by_sensor']

    def test_groups_cross_sensor_features(self):
        """Cross-sensor features like left_right_balance should go to cross_sensor."""
        features = [
            'L_P_Heel_mean', 'left_right_balance', 'total_pressure',
            'fore_hind_ratio'
        ]
        groups = group_features_by_sensor(features)

        assert 'cross_sensor' in groups['by_sensor']
        assert 'left_right_balance' in groups['by_sensor']['cross_sensor']
        assert 'total_pressure' in groups['by_sensor']['cross_sensor']


class TestGenerateEdgeConfig:
    def test_creates_valid_json(self, trained_rf_model, tmp_path):
        """Edge config should be valid JSON with expected structure."""
        model, scaler, feature_names = trained_rf_model
        results = analyze_feature_importance(model, feature_names)

        output_path = tmp_path / 'edge_config.json'
        config = generate_edge_config(results, output_path)

        assert output_path.exists()

        with open(output_path) as f:
            loaded = json.load(f)

        assert 'metadata' in loaded
        assert 'features' in loaded
        assert 'sensors_required' in loaded
        assert 'computational_savings' in loaded
        assert loaded['metadata']['original_features'] == len(feature_names)
        assert isinstance(loaded['features']['all'], list)
        assert len(loaded['features']['all']) > 0
