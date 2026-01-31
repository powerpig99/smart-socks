#!/usr/bin/env python3
"""
Smart Socks - Unknown Class Detection / Rejection
ELEC-E7840 Smart Wearables (Aalto University)

Implements two strategies for handling non-target activities:
1. Confidence Threshold: Reject low-confidence predictions
2. Novelty Detection: One-class SVM or Isolation Forest

Usage:
    # Train with rejection capability
    python unknown_class.py --train --features ../../03_Data/features/features_all.csv --output ./models/

    # Test rejection
    python unknown_class.py --test --model ./models/rejecting_classifier.joblib --test-data ../../03_Data/features/test_unknown.csv

    # Compare methods
    python unknown_class.py --compare --features ../../03_Data/features/features_all.csv --output ./comparison/
"""

import argparse
import json
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from config import ACTIVITIES, MODEL


class ConfidenceThresholdClassifier:
    """
    Wrapper that adds rejection capability based on prediction confidence.

    Simple but effective: if max probability < threshold, classify as 'unknown'.
    """

    def __init__(self, base_model, threshold: float = 0.6):
        self.base_model = base_model
        self.threshold = threshold
        self.classes_ = list(base_model.classes_) + ['unknown']
        self.scaler = None

    def predict(self, X):
        """Predict with rejection for low-confidence samples."""
        X_input = X
        if self.scaler is not None:
            X_input = self.scaler.transform(X)

        probs = self.base_model.predict_proba(X_input)
        max_probs = np.max(probs, axis=1)
        predictions = self.base_model.predict(X_input)

        rejected = max_probs < self.threshold
        result = predictions.copy()
        result = np.where(rejected, 'unknown', result)

        return result

    def predict_proba(self, X):
        """Return probability including unknown class."""
        X_input = X
        if self.scaler is not None:
            X_input = self.scaler.transform(X)

        base_probs = self.base_model.predict_proba(X_input)
        max_probs = np.max(base_probs, axis=1)

        unknown_prob = np.maximum(0, self.threshold - max_probs)
        adjusted_probs = base_probs * ((1 - unknown_prob) / np.sum(base_probs, axis=1))[:, np.newaxis]

        return np.column_stack([adjusted_probs, unknown_prob])

    def set_scaler(self, scaler):
        """Set scaler for preprocessing."""
        self.scaler = scaler

    def save(self, filepath: Path):
        """Save the rejecting classifier."""
        joblib.dump({
            'base_model': self.base_model,
            'threshold': self.threshold,
            'scaler': self.scaler,
            'classes': self.classes_
        }, filepath)

    @classmethod
    def load(cls, filepath: Path):
        """Load a saved rejecting classifier."""
        data = joblib.load(filepath)
        classifier = cls(data['base_model'], data['threshold'])
        classifier.set_scaler(data['scaler'])
        return classifier


class NoveltyDetector:
    """
    Two-stage classifier: Novelty detection -> Classification.

    First checks if sample is "known" (target activity) or "novel" (unknown).
    Then classifies known samples into specific activities.
    """

    def __init__(self,
                 classifier: RandomForestClassifier,
                 novelty_detector,
                 scaler: StandardScaler):
        self.classifier = classifier
        self.novelty_detector = novelty_detector
        self.scaler = scaler
        self.classes_ = list(classifier.classes_) + ['unknown']

    def fit_novelty_detector(self, X_target: np.ndarray):
        """Fit novelty detector on target activities only."""
        X_scaled = self.scaler.transform(X_target)
        self.novelty_detector.fit(X_scaled)
        print(f"Fitted novelty detector on {len(X_target)} target samples")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict with novelty rejection."""
        X_scaled = self.scaler.transform(X)

        is_known = self.novelty_detector.predict(X_scaled) == 1

        predictions = np.full(len(X), 'unknown', dtype=object)
        if np.any(is_known):
            known_predictions = self.classifier.predict(X_scaled[is_known])
            predictions[is_known] = known_predictions

        return predictions

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray,
                 unknown_label: str = 'unknown') -> Dict:
        """Evaluate rejection performance."""
        predictions = self.predict(X_test)

        is_unknown_actual = y_test == unknown_label
        is_unknown_pred = predictions == 'unknown'

        true_positives = np.sum(is_unknown_actual & is_unknown_pred)
        false_positives = np.sum(~is_unknown_actual & is_unknown_pred)
        false_negatives = np.sum(is_unknown_actual & ~is_unknown_pred)

        rejection_recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        rejection_precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0

        accepted_mask = ~is_unknown_pred
        if np.sum(accepted_mask) > 0:
            classification_acc = np.mean(predictions[accepted_mask] == y_test[accepted_mask])
        else:
            classification_acc = 0

        return {
            'rejection_recall': rejection_recall,
            'rejection_precision': rejection_precision,
            'classification_accuracy': classification_acc,
            'unknown_rejected': int(np.sum(is_unknown_pred)),
            'total_unknown': int(np.sum(is_unknown_actual))
        }

    def save(self, filepath: Path):
        """Save the novelty detector."""
        joblib.dump({
            'classifier': self.classifier,
            'novelty_detector': self.novelty_detector,
            'scaler': self.scaler,
            'classes': self.classes_
        }, filepath)

    @classmethod
    def load(cls, filepath: Path):
        """Load a saved novelty detector."""
        data = joblib.load(filepath)
        detector = cls(data['classifier'], data['novelty_detector'], data['scaler'])
        return detector


def train_with_rejection(features_path: Path,
                         output_dir: Path,
                         method: str = 'confidence',
                         confidence_threshold: float = 0.6,
                         contamination: float = 0.1):
    """
    Train a classifier with unknown class rejection capability.

    Args:
        features_path: Path to features CSV
        output_dir: Directory to save models
        method: 'confidence' or 'novelty'
        confidence_threshold: Threshold for confidence method
        contamination: Expected proportion of outliers for novelty method
    """
    print(f"Loading features from {features_path}...")
    df = pd.read_csv(features_path)

    X = df.drop(['label', 'subject'], axis=1, errors='ignore').values
    y = df['label'].values

    target_activities = [a for a in ACTIVITIES['all'] if a != 'unknown']
    is_target = np.isin(y, target_activities)

    X_target = X[is_target]
    y_target = y[is_target]

    scaler = StandardScaler()
    X_target_scaled = scaler.fit_transform(X_target)

    rf_params = MODEL['random_forest']

    print("Training base classifier on target activities...")
    base_classifier = RandomForestClassifier(**rf_params)
    base_classifier.fit(X_target_scaled, y_target)

    output_dir.mkdir(parents=True, exist_ok=True)

    if method == 'confidence':
        print(f"Creating confidence-based rejector (threshold={confidence_threshold})...")
        rejector = ConfidenceThresholdClassifier(base_classifier, confidence_threshold)
        rejector.set_scaler(scaler)

        rejector.save(output_dir / 'rejecting_classifier.joblib')

        config = {
            'method': 'confidence_threshold',
            'threshold': confidence_threshold,
            'classes': list(rejector.classes_),
            'target_activities': target_activities
        }

    elif method == 'novelty':
        print(f"Training novelty detector (contamination={contamination})...")

        novelty_detector = IsolationForest(
            contamination=contamination,
            random_state=rf_params.get('random_state', 42),
            n_jobs=rf_params.get('n_jobs', -1)
        )

        full_detector = NoveltyDetector(base_classifier, novelty_detector, scaler)
        full_detector.fit_novelty_detector(X_target)

        full_detector.save(output_dir / 'novelty_detector.joblib')

        config = {
            'method': 'novelty_detection',
            'contamination': contamination,
            'classes': list(full_detector.classes_),
            'target_activities': target_activities
        }

    else:
        raise ValueError(f"Unknown method: {method}")

    with open(output_dir / 'rejection_config.json', 'w') as f:
        json.dump(config, f, indent=2)

    print(f"\nModel saved to {output_dir}/")
    print(f"   Method: {method}")
    print(f"   Classes: {config['classes']}")


def evaluate_rejection(model_path: Path, test_data_path: Path, method: str):
    """Evaluate rejection performance on test data including unknown activities."""
    print(f"Loading model from {model_path}...")

    if method == 'confidence':
        model = ConfidenceThresholdClassifier.load(model_path)
    else:
        model = NoveltyDetector.load(model_path)

    print(f"Loading test data from {test_data_path}...")
    df = pd.read_csv(test_data_path)

    X_test = df.drop(['label', 'subject'], axis=1, errors='ignore').values
    y_test = df['label'].values

    print(f"\nTest set: {len(X_test)} samples")
    print(f"Activities: {np.unique(y_test)}")

    predictions = model.predict(X_test)

    print("\n" + "=" * 60)
    print("CLASSIFICATION REPORT WITH REJECTION")
    print("=" * 60)
    print(classification_report(y_test, predictions))

    cm = confusion_matrix(y_test, predictions, labels=model.classes_)

    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=model.classes_,
                yticklabels=model.classes_,
                ax=ax)
    ax.set_xlabel('Predicted')
    ax.set_ylabel('True')
    ax.set_title('Confusion Matrix with Unknown Class Rejection')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()

    output_path = Path(model_path).parent / 'rejection_confusion_matrix.png'
    plt.savefig(output_path, dpi=150)
    print(f"\nSaved confusion matrix to {output_path}")

    unknown_actual = y_test == 'unknown'
    unknown_pred = predictions == 'unknown'

    if np.any(unknown_actual):
        recall = np.sum(unknown_actual & unknown_pred) / np.sum(unknown_actual)
        print(f"\nUnknown Class Detection:")
        print(f"  Recall: {recall:.2%} ({np.sum(unknown_actual & unknown_pred)}/{np.sum(unknown_actual)})")
        print(f"  False Positive Rate: {np.sum(~unknown_actual & unknown_pred) / np.sum(~unknown_actual):.2%}")


def compare_methods(features_path: Path, output_dir: Path):
    """Compare confidence threshold vs novelty detection methods."""
    print("Comparing rejection methods...\n")

    df = pd.read_csv(features_path)
    X = df.drop(['label', 'subject'], axis=1, errors='ignore').values
    y = df['label'].values

    # Simulate unknown by holding out one activity
    unknown_activity = 'stairs_up'
    y_simulated = y.copy()
    y_simulated[y == unknown_activity] = 'unknown'

    # Use proper train/test split
    X_train, X_test, y_train_sim, y_test_sim = train_test_split(
        X, y_simulated, test_size=0.3, random_state=42, stratify=y_simulated
    )

    # Save train split as temp features for training
    # Build a DataFrame for training (exclude 'unknown' rows)
    feature_cols = [c for c in df.columns if c not in ('label', 'subject')]

    results = []

    for method_name, params in [
        ('confidence_0.5', {'method': 'confidence', 'confidence_threshold': 0.5}),
        ('confidence_0.6', {'method': 'confidence', 'confidence_threshold': 0.6}),
        ('confidence_0.7', {'method': 'confidence', 'confidence_threshold': 0.7}),
        ('novelty_0.05', {'method': 'novelty', 'contamination': 0.05}),
        ('novelty_0.10', {'method': 'novelty', 'contamination': 0.10}),
    ]:
        method_dir = output_dir / method_name
        method_dir.mkdir(parents=True, exist_ok=True)

        # Train on training split (target activities only)
        is_target_train = y_train_sim != 'unknown'
        X_train_target = X_train[is_target_train]
        y_train_target = y_train_sim[is_target_train]

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train_target)

        rf_params = MODEL['random_forest']
        base_clf = RandomForestClassifier(**rf_params)
        base_clf.fit(X_train_scaled, y_train_target)

        if params['method'] == 'confidence':
            model = ConfidenceThresholdClassifier(base_clf, params['confidence_threshold'])
            model.set_scaler(scaler)
        else:
            novelty_det = IsolationForest(
                contamination=params['contamination'],
                random_state=42, n_jobs=-1
            )
            model = NoveltyDetector(base_clf, novelty_det, scaler)
            model.fit_novelty_detector(X_train_target)

        # Evaluate on test split
        predictions = model.predict(X_test)

        unknown_actual = y_test_sim == 'unknown'
        unknown_pred = predictions == 'unknown'

        recall = np.sum(unknown_actual & unknown_pred) / np.sum(unknown_actual) if np.sum(unknown_actual) > 0 else 0
        precision = np.sum(unknown_actual & unknown_pred) / np.sum(unknown_pred) if np.sum(unknown_pred) > 0 else 0

        accepted = ~unknown_pred
        acc_on_accepted = np.mean(predictions[accepted] == y_test_sim[accepted]) if np.sum(accepted) > 0 else 0

        results.append({
            'method': method_name,
            'unknown_recall': recall,
            'unknown_precision': precision,
            'accuracy_on_accepted': acc_on_accepted,
            'rejection_rate': np.mean(unknown_pred)
        })

    print("\n" + "=" * 80)
    print("METHOD COMPARISON")
    print("=" * 80)
    print(f"{'Method':<20} {'Unknown Recall':>15} {'Unknown Prec':>15} {'Acc (Accepted)':>15} {'Reject Rate':>15}")
    print("-" * 80)
    for r in results:
        print(f"{r['method']:<20} {r['unknown_recall']:>15.2%} {r['unknown_precision']:>15.2%} "
              f"{r['accuracy_on_accepted']:>15.2%} {r['rejection_rate']:>15.2%}")

    results_df = pd.DataFrame(results)
    output_dir.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(output_dir / 'method_comparison.csv', index=False)
    print(f"\nSaved comparison to {output_dir / 'method_comparison.csv'}")


def main():
    parser = argparse.ArgumentParser(
        description='Unknown class detection for Smart Socks'
    )
    parser.add_argument('--train', action='store_true',
                       help='Train a rejecting classifier')
    parser.add_argument('--test', action='store_true',
                       help='Test/evaluate a rejecting classifier')
    parser.add_argument('--compare', action='store_true',
                       help='Compare different rejection methods')
    parser.add_argument('--features',
                       help='Path to features CSV file (required for --train and --compare)')
    parser.add_argument('--model',
                       help='Path to saved model (for testing)')
    parser.add_argument('--test-data',
                       help='Path to test data including unknown activities')
    parser.add_argument('--output', '-o', default='./rejection_models',
                       help='Output directory')
    parser.add_argument('--method', default='confidence',
                       choices=['confidence', 'novelty'],
                       help='Rejection method')
    parser.add_argument('--threshold', type=float, default=0.6,
                       help='Confidence threshold for rejection')
    parser.add_argument('--contamination', type=float, default=0.1,
                       help='Expected proportion of outliers (for novelty method)')

    args = parser.parse_args()

    if args.train:
        if not args.features:
            print("Error: --train requires --features")
            return 1
        train_with_rejection(
            Path(args.features),
            Path(args.output),
            method=args.method,
            confidence_threshold=args.threshold,
            contamination=args.contamination
        )
    elif args.test:
        if not args.model or not args.test_data:
            print("Error: --test requires --model and --test-data")
            return 1
        evaluate_rejection(Path(args.model), Path(args.test_data), args.method)
    elif args.compare:
        if not args.features:
            print("Error: --compare requires --features")
            return 1
        compare_methods(Path(args.features), Path(args.output))
    else:
        print("Error: Specify --train, --test, or --compare")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
