#!/usr/bin/env python3
"""
Smart Socks - Model Training
ELEC-E7840 Smart Wearables (Aalto University)

Trains a Random Forest classifier for activity recognition using
extracted features from sensor data.

Usage:
    python train_model.py --features ../03_Data/features/features_all.csv --output ../05_Analysis/
"""

import argparse
import os
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.model_selection import GridSearchCV
import joblib


# Activity labels
ACTIVITIES = [
    'walking_forward', 'walking_backward',
    'stairs_up', 'stairs_down',
    'sitting_floor', 'sitting_crossed',
    'sit_to_stand', 'stand_to_sit',
    'standing_upright', 'standing_lean_left', 'standing_lean_right'
]


def load_features(features_path):
    """
    Load feature data from CSV file.
    
    Args:
        features_path: Path to features CSV file
    
    Returns:
        X: Feature matrix
        y: Labels
        subjects: Subject IDs
        feature_names: List of feature names
    """
    df = pd.read_csv(features_path)
    
    # Separate features, labels, and subjects
    exclude_cols = ['label', 'subject']
    feature_names = [col for col in df.columns if col not in exclude_cols]
    
    X = df[feature_names].values
    y = df['label'].values
    subjects = df['subject'].values
    
    print(f"Loaded {len(df)} samples")
    print(f"Features: {len(feature_names)}")
    print(f"Activities: {np.unique(y)}")
    print(f"Subjects: {np.unique(subjects)}")
    
    return X, y, subjects, feature_names


def train_test_split_by_subject(X, y, subjects, test_subjects=None, test_size=0.3):
    """
    Split data ensuring no subject overlap between train and test sets.
    This is crucial for evaluating real-world generalization.
    
    Args:
        X: Feature matrix
        y: Labels
        subjects: Subject IDs for each sample
        test_subjects: Specific subjects to use for testing (optional)
        test_size: Proportion of subjects to use for testing
    
    Returns:
        X_train, X_test, y_train, y_test, train_subjects, test_subjects
    """
    unique_subjects = np.unique(subjects)
    
    if test_subjects is None:
        # Randomly select subjects for testing
        n_test = max(1, int(len(unique_subjects) * test_size))
        test_subjects = np.random.choice(unique_subjects, size=n_test, replace=False)
    
    test_subjects = set(test_subjects)
    train_subjects = set(unique_subjects) - test_subjects
    
    # Create masks
    train_mask = np.array([s in train_subjects for s in subjects])
    test_mask = np.array([s in test_subjects for s in subjects])
    
    X_train = X[train_mask]
    X_test = X[test_mask]
    y_train = y[train_mask]
    y_test = y[test_mask]
    
    print(f"\nTrain subjects: {sorted(train_subjects)} ({len(X_train)} samples)")
    print(f"Test subjects: {sorted(test_subjects)} ({len(X_test)} samples)")
    
    return X_train, X_test, y_train, y_test, train_subjects, test_subjects


def train_model(X_train, y_train, tune_hyperparams=False):
    """
    Train a Random Forest classifier.
    
    Args:
        X_train: Training features
        y_train: Training labels
        tune_hyperparams: Whether to perform hyperparameter tuning
    
    Returns:
        Trained model and scaler
    """
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    if tune_hyperparams:
        print("\nPerforming hyperparameter tuning...")
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [10, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        
        rf = RandomForestClassifier(random_state=42, n_jobs=-1)
        grid_search = GridSearchCV(
            rf, param_grid, cv=5, scoring='accuracy', n_jobs=-1, verbose=1
        )
        grid_search.fit(X_train_scaled, y_train)
        
        print(f"Best parameters: {grid_search.best_params_}")
        print(f"Best CV score: {grid_search.best_score_:.4f}")
        model = grid_search.best_estimator_
    else:
        # Use default parameters (usually work well)
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train_scaled, y_train)
    
    return model, scaler


def evaluate_model(model, scaler, X_test, y_test, output_dir=None):
    """
    Evaluate the trained model on test data.
    
    Args:
        model: Trained classifier
        scaler: Fitted scaler
        X_test: Test features
        y_test: Test labels
        output_dir: Directory to save evaluation results
    
    Returns:
        Dictionary of evaluation metrics
    """
    X_test_scaled = scaler.transform(X_test)
    y_pred = model.predict(X_test_scaled)
    
    # Overall accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n{'='*50}")
    print(f"Test Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"{'='*50}")
    
    # Per-class accuracy
    print("\nPer-class Accuracy:")
    print("-" * 50)
    class_report = classification_report(y_test, y_pred, digits=4)
    print(class_report)
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred, labels=sorted(np.unique(y_test)))
    
    if output_dir:
        # Save classification report
        report_path = os.path.join(output_dir, 'classification_report.txt')
        with open(report_path, 'w') as f:
            f.write(f"Test Accuracy: {accuracy:.4f}\n\n")
            f.write(class_report)
        print(f"\nSaved classification report to {report_path}")
        
        # Plot confusion matrix
        plt.figure(figsize=(12, 10))
        sns.heatmap(
            cm, 
            annot=True, 
            fmt='d', 
            cmap='Blues',
            xticklabels=sorted(np.unique(y_test)),
            yticklabels=sorted(np.unique(y_test))
        )
        plt.xlabel('Predicted')
        plt.ylabel('True')
        plt.title('Confusion Matrix')
        plt.tight_layout()
        cm_path = os.path.join(output_dir, 'confusion_matrix.png')
        plt.savefig(cm_path, dpi=150)
        print(f"Saved confusion matrix to {cm_path}")
        plt.close()
    
    return {
        'accuracy': accuracy,
        'confusion_matrix': cm,
        'predictions': y_pred
    }


def analyze_feature_importance(model, feature_names, output_dir=None, top_n=20):
    """
    Analyze and visualize feature importance from the Random Forest.
    
    Args:
        model: Trained Random Forest
        feature_names: List of feature names
        output_dir: Directory to save plots
        top_n: Number of top features to show
    """
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    print(f"\nTop {top_n} Most Important Features:")
    print("-" * 50)
    for i in range(min(top_n, len(feature_names))):
        idx = indices[i]
        print(f"{i+1:2d}. {feature_names[idx]:<40} {importances[idx]:.4f}")
    
    if output_dir:
        # Plot top features
        plt.figure(figsize=(10, 8))
        n_plot = min(top_n, len(feature_names))
        plt.barh(range(n_plot), importances[indices[:n_plot]], align='center')
        plt.yticks(range(n_plot), [feature_names[i] for i in indices[:n_plot]])
        plt.xlabel('Feature Importance')
        plt.title(f'Top {n_plot} Feature Importances')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        fi_path = os.path.join(output_dir, 'feature_importance.png')
        plt.savefig(fi_path, dpi=150)
        print(f"\nSaved feature importance plot to {fi_path}")
        plt.close()
        
        # Save all feature importances to CSV
        fi_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)
        fi_csv_path = os.path.join(output_dir, 'feature_importance.csv')
        fi_df.to_csv(fi_csv_path, index=False)
        print(f"Saved feature importance data to {fi_csv_path}")


def cross_subject_validation(X, y, subjects, output_dir=None):
    """
    Perform leave-one-subject-out cross-validation to assess
    generalization to new subjects.
    
    Args:
        X: Feature matrix
        y: Labels
        subjects: Subject IDs
        output_dir: Directory to save results
    
    Returns:
        Dictionary of cross-validation results
    """
    unique_subjects = np.unique(subjects)
    subject_accuracies = {}
    
    print("\n" + "="*50)
    print("Leave-One-Subject-Out Cross-Validation")
    print("="*50)
    
    for test_subject in unique_subjects:
        # Split data
        train_mask = subjects != test_subject
        test_mask = subjects == test_subject
        
        X_train = X[train_mask]
        X_test = X[test_mask]
        y_train = y[train_mask]
        y_test = y[test_mask]
        
        # Train and evaluate
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        model = RandomForestClassifier(
            n_estimators=100, max_depth=20, random_state=42, n_jobs=-1
        )
        model.fit(X_train_scaled, y_train)
        
        accuracy = model.score(X_test_scaled, y_test)
        subject_accuracies[test_subject] = accuracy
        
        print(f"Subject {test_subject}: {accuracy:.4f} ({accuracy*100:.2f}%)")
    
    mean_accuracy = np.mean(list(subject_accuracies.values()))
    std_accuracy = np.std(list(subject_accuracies.values()))
    
    print(f"\nMean accuracy: {mean_accuracy:.4f} ({mean_accuracy*100:.2f}%)")
    print(f"Std deviation: {std_accuracy:.4f}")
    
    if output_dir:
        # Save cross-subject results
        results_df = pd.DataFrame({
            'subject': list(subject_accuracies.keys()),
            'accuracy': list(subject_accuracies.values())
        })
        results_path = os.path.join(output_dir, 'cross_subject_results.csv')
        results_df.to_csv(results_path, index=False)
        print(f"\nSaved cross-subject results to {results_path}")
        
        # Plot cross-subject performance
        plt.figure(figsize=(10, 6))
        subjects_sorted = sorted(subject_accuracies.keys())
        accs = [subject_accuracies[s] for s in subjects_sorted]
        plt.bar(subjects_sorted, accs)
        plt.axhline(y=mean_accuracy, color='r', linestyle='--', label=f'Mean: {mean_accuracy:.3f}')
        plt.xlabel('Subject')
        plt.ylabel('Accuracy')
        plt.title('Cross-Subject Validation Accuracy')
        plt.ylim([0, 1])
        plt.legend()
        plt.tight_layout()
        plot_path = os.path.join(output_dir, 'cross_subject_accuracy.png')
        plt.savefig(plot_path, dpi=150)
        print(f"Saved cross-subject plot to {plot_path}")
        plt.close()
    
    return {
        'subject_accuracies': subject_accuracies,
        'mean_accuracy': mean_accuracy,
        'std_accuracy': std_accuracy
    }


def save_model(model, scaler, feature_names, label_encoder, output_dir, model_name='smart_socks_model'):
    """
    Save the trained model and preprocessing objects.
    
    Args:
        model: Trained classifier
        scaler: Fitted scaler
        feature_names: List of feature names
        label_encoder: Fitted label encoder
        output_dir: Directory to save model
        model_name: Base name for model files
    """
    model_path = os.path.join(output_dir, f'{model_name}.joblib')
    scaler_path = os.path.join(output_dir, f'{model_name}_scaler.joblib')
    metadata_path = os.path.join(output_dir, f'{model_name}_metadata.joblib')
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    joblib.dump({
        'feature_names': feature_names,
        'label_encoder': label_encoder,
        'classes': model.classes_
    }, metadata_path)
    
    print(f"\nSaved model to {model_path}")
    print(f"Saved scaler to {scaler_path}")
    print(f"Saved metadata to {metadata_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Smart Socks Model Training'
    )
    parser.add_argument(
        '--features', '-f',
        required=True,
        help='Path to features CSV file'
    )
    parser.add_argument(
        '--output', '-o',
        default='../05_Analysis/',
        help='Output directory for model and results'
    )
    parser.add_argument(
        '--test-subjects',
        nargs='+',
        default=None,
        help='Specific subjects to use for testing (e.g., S07 S08 S09)'
    )
    parser.add_argument(
        '--cross-subject',
        action='store_true',
        help='Perform leave-one-subject-out cross-validation'
    )
    parser.add_argument(
        '--tune',
        action='store_true',
        help='Perform hyperparameter tuning (slower)'
    )
    parser.add_argument(
        '--model-name',
        default='smart_socks_model',
        help='Base name for saved model files'
    )

    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    # Load features
    print("Loading features...")
    X, y, subjects, feature_names = load_features(args.features)
    
    # Encode labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    if args.cross_subject:
        # Perform cross-subject validation
        cross_subject_validation(X, y, subjects, args.output)
    else:
        # Standard train/test split
        X_train, X_test, y_train, y_test, train_subs, test_subs = train_test_split_by_subject(
            X, y, subjects, test_subjects=args.test_subjects
        )
        
        # Train model
        print("\nTraining model...")
        model, scaler = train_model(X_train, y_train, tune_hyperparams=args.tune)
        
        # Evaluate
        print("\nEvaluating model...")
        results = evaluate_model(model, scaler, X_test, y_test, args.output)
        
        # Analyze feature importance
        analyze_feature_importance(model, feature_names, args.output)
        
        # Save model
        save_model(model, scaler, feature_names, label_encoder, args.output, args.model_name)
    
    print("\n" + "="*50)
    print("Training complete!")
    print("="*50)
    
    return 0


if __name__ == '__main__':
    exit(main())
