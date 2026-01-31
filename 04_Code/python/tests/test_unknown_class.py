#!/usr/bin/env python3
"""Tests for unknown_class.py - Unknown Class Detection / Rejection."""

import pytest
import numpy as np
import pandas as pd
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unknown_class import (
    ConfidenceThresholdClassifier,
    NoveltyDetector,
    train_with_rejection,
)
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler


class TestConfidenceThresholdClassifier:
    def test_predict_returns_unknown_for_low_confidence(self, trained_rf_model):
        """Low-confidence inputs should be classified as 'unknown'."""
        model, scaler, feature_names = trained_rf_model

        # Use a very high threshold so everything is rejected
        rejector = ConfidenceThresholdClassifier(model, threshold=0.99)
        rejector.set_scaler(scaler)

        # Random noise should have low confidence
        X = np.random.RandomState(123).randn(10, len(feature_names)) * 100
        predictions = rejector.predict(X)

        assert 'unknown' in predictions

    def test_predict_accepts_high_confidence(self, trained_rf_model):
        """High-confidence inputs should NOT be classified as 'unknown'."""
        model, scaler, feature_names = trained_rf_model

        # Very low threshold - should accept everything
        rejector = ConfidenceThresholdClassifier(model, threshold=0.01)
        rejector.set_scaler(scaler)

        X = np.random.RandomState(42).randn(10, len(feature_names))
        predictions = rejector.predict(X)

        assert 'unknown' not in predictions

    def test_predict_proba_shape(self, trained_rf_model):
        """predict_proba should return n_classes + 1 columns (including unknown)."""
        model, scaler, feature_names = trained_rf_model
        rejector = ConfidenceThresholdClassifier(model, threshold=0.6)
        rejector.set_scaler(scaler)

        X = np.random.RandomState(42).randn(5, len(feature_names))
        proba = rejector.predict_proba(X)

        n_base_classes = len(model.classes_)
        assert proba.shape == (5, n_base_classes + 1)

    def test_save_load_roundtrip(self, trained_rf_model, tmp_path):
        """Save/load should preserve threshold and produce same predictions."""
        model, scaler, feature_names = trained_rf_model
        rejector = ConfidenceThresholdClassifier(model, threshold=0.55)
        rejector.set_scaler(scaler)

        filepath = tmp_path / 'test_rejector.joblib'
        rejector.save(filepath)

        loaded = ConfidenceThresholdClassifier.load(filepath)

        assert loaded.threshold == 0.55

        X = np.random.RandomState(42).randn(5, len(feature_names))
        np.testing.assert_array_equal(rejector.predict(X), loaded.predict(X))

    def test_predict_applies_scaler(self, trained_rf_model):
        """predict should apply scaler when one is set."""
        model, scaler, feature_names = trained_rf_model

        rejector_with = ConfidenceThresholdClassifier(model, threshold=0.5)
        rejector_with.set_scaler(scaler)

        rejector_without = ConfidenceThresholdClassifier(model, threshold=0.5)

        X = np.random.RandomState(42).randn(5, len(feature_names)) * 100
        X_scaled = scaler.transform(X)

        # With scaler set, passing raw X should give same results as
        # without scaler but passing pre-scaled X
        pred_with = rejector_with.predict(X)
        pred_without = rejector_without.predict(X_scaled)
        np.testing.assert_array_equal(pred_with, pred_without)


class TestNoveltyDetector:
    def test_predict_returns_unknown_for_outliers(self, trained_rf_model):
        """Out-of-distribution inputs should be classified as 'unknown'."""
        model, scaler, feature_names = trained_rf_model

        novelty_det = IsolationForest(contamination=0.1, random_state=42)
        detector = NoveltyDetector(model, novelty_det, scaler)

        # Fit on normal data
        X_normal = np.random.RandomState(42).randn(100, len(feature_names))
        detector.fit_novelty_detector(X_normal)

        # Extreme outlier data
        X_outlier = np.ones((5, len(feature_names))) * 1000
        predictions = detector.predict(X_outlier)

        assert 'unknown' in predictions

    def test_save_load_roundtrip(self, trained_rf_model, tmp_path):
        """Save/load should preserve the detector."""
        model, scaler, feature_names = trained_rf_model

        novelty_det = IsolationForest(contamination=0.1, random_state=42)
        detector = NoveltyDetector(model, novelty_det, scaler)

        X_normal = np.random.RandomState(42).randn(100, len(feature_names))
        detector.fit_novelty_detector(X_normal)

        filepath = tmp_path / 'test_novelty.joblib'
        detector.save(filepath)

        loaded = NoveltyDetector.load(filepath)

        X_test = np.random.RandomState(99).randn(10, len(feature_names))
        np.testing.assert_array_equal(detector.predict(X_test), loaded.predict(X_test))

    def test_evaluate_returns_expected_keys(self, trained_rf_model):
        """evaluate() should return dict with all expected metric keys."""
        model, scaler, feature_names = trained_rf_model

        novelty_det = IsolationForest(contamination=0.1, random_state=42)
        detector = NoveltyDetector(model, novelty_det, scaler)

        X_normal = np.random.RandomState(42).randn(100, len(feature_names))
        detector.fit_novelty_detector(X_normal)

        X_test = np.random.RandomState(99).randn(20, len(feature_names))
        y_test = np.array(['walking_forward'] * 15 + ['unknown'] * 5)

        result = detector.evaluate(X_test, y_test)

        expected_keys = {
            'rejection_recall', 'rejection_precision',
            'classification_accuracy', 'unknown_rejected', 'total_unknown'
        }
        assert set(result.keys()) == expected_keys
        assert result['total_unknown'] == 5


class TestTrainWithRejection:
    def test_creates_output_files_confidence(self, sample_features_df, tmp_path):
        """train_with_rejection with confidence method should create expected files."""
        features_path = tmp_path / 'features.csv'
        sample_features_df.to_csv(features_path, index=False)

        output_dir = tmp_path / 'output_confidence'
        train_with_rejection(features_path, output_dir, method='confidence')

        assert (output_dir / 'rejecting_classifier.joblib').exists()
        assert (output_dir / 'rejection_config.json').exists()

    def test_creates_output_files_novelty(self, sample_features_df, tmp_path):
        """train_with_rejection with novelty method should create expected files."""
        features_path = tmp_path / 'features.csv'
        sample_features_df.to_csv(features_path, index=False)

        output_dir = tmp_path / 'output_novelty'
        train_with_rejection(features_path, output_dir, method='novelty')

        assert (output_dir / 'novelty_detector.joblib').exists()
        assert (output_dir / 'rejection_config.json').exists()
