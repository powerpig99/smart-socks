#!/usr/bin/env python3
"""
Smart Socks - Feature Importance Analysis
ELEC-E7840 Smart Wearables (Aalto University)

Analyzes feature importance from trained Random Forest to identify
minimal feature set for edge deployment.

Usage:
    python feature_importance.py --model ../../05_Analysis/smart_socks_model.joblib --output ./results/
"""

import argparse
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from pathlib import Path
from typing import Dict, List, Tuple


def analyze_feature_importance(model, feature_names: List[str], top_n: int = 30) -> Dict:
    """
    Analyze feature importance from trained Random Forest.
    
    Args:
        model: Trained sklearn RandomForestClassifier
        feature_names: List of feature names in order
        top_n: Number of top features to return
    
    Returns:
        Dictionary with importance rankings and recommendations
    """
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    # Calculate cumulative importance
    cumulative = np.cumsum(importances[indices])
    
    # Find thresholds
    n_90 = np.argmax(cumulative >= 0.90) + 1
    n_95 = np.argmax(cumulative >= 0.95) + 1
    n_99 = np.argmax(cumulative >= 0.99) + 1
    
    results = {
        'total_features': len(feature_names),
        'top_features': [
            {
                'name': feature_names[i],
                'importance': float(importances[i]),
                'cumulative': float(cumulative[idx])
            }
            for idx, i in enumerate(indices[:top_n])
        ],
        'thresholds': {
            '90_percent': {
                'n_features': int(n_90),
                'features': [feature_names[i] for i in indices[:n_90]]
            },
            '95_percent': {
                'n_features': int(n_95),
                'features': [feature_names[i] for i in indices[:n_95]]
            },
            '99_percent': {
                'n_features': int(n_99),
                'features': [feature_names[i] for i in indices[:n_99]]
            }
        },
        'feature_groups': group_features_by_sensor([feature_names[i] for i in indices[:n_95]])
    }
    
    return results


def group_features_by_sensor(feature_names: List[str]) -> Dict[str, List[str]]:
    """
    Group features by sensor and feature type.
    
    Helps identify which sensors and feature types matter most.
    """
    groups = {
        'by_sensor': {},
        'by_type': {}
    }
    
    for feature in feature_names:
        # Extract sensor name (e.g., "L_P_Heel_mean" -> "L_P_Heel")
        parts = feature.split('_')
        if len(parts) >= 4:
            sensor = '_'.join(parts[:3])  # L_P_Heel
            feature_type = '_'.join(parts[3:])  # mean, std, etc.
        else:
            sensor = 'cross_sensor'
            feature_type = feature
        
        if sensor not in groups['by_sensor']:
            groups['by_sensor'][sensor] = []
        groups['by_sensor'][sensor].append(feature)
        
        if feature_type not in groups['by_type']:
            groups['by_type'][feature_type] = []
        groups['by_type'][feature_type].append(feature)
    
    # Sort by count
    groups['by_sensor'] = dict(sorted(groups['by_sensor'].items(), 
                                       key=lambda x: len(x[1]), reverse=True))
    groups['by_type'] = dict(sorted(groups['by_type'].items(),
                                     key=lambda x: len(x[1]), reverse=True))
    
    return groups


def plot_importance_analysis(results: Dict, output_dir: Path):
    """
    Generate comprehensive visualization of feature importance.
    """
    fig = plt.figure(figsize=(16, 12))
    
    # 1. Top features bar chart
    ax1 = plt.subplot(2, 2, 1)
    top_n = min(20, len(results['top_features']))
    features = [f['name'][:25] for f in results['top_features'][:top_n]]
    importances = [f['importance'] for f in results['top_features'][:top_n]]
    
    y_pos = np.arange(len(features))
    ax1.barh(y_pos, importances, color='#5E81AC')
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(features, fontsize=8)
    ax1.invert_yaxis()
    ax1.set_xlabel('Importance Score')
    ax1.set_title(f'Top {top_n} Most Important Features', fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    
    # 2. Cumulative importance curve
    ax2 = plt.subplot(2, 2, 2)
    cumsum = [f['cumulative'] for f in results['top_features']]
    ax2.plot(range(1, len(cumsum) + 1), cumsum, 'b-', linewidth=2)
    ax2.axhline(y=0.90, color='g', linestyle='--', label='90%')
    ax2.axhline(y=0.95, color='orange', linestyle='--', label='95%')
    ax2.axhline(y=0.99, color='r', linestyle='--', label='99%')
    
    # Mark thresholds
    for threshold, color in [(0.90, 'green'), (0.95, 'orange'), (0.99, 'red')]:
        n = results['thresholds'][f'{int(threshold*100)}_percent']['n_features']
        ax2.axvline(x=n, color=color, linestyle=':', alpha=0.5)
        ax2.annotate(f'{n} features', xy=(n, threshold), 
                    xytext=(n+5, threshold-0.05),
                    fontsize=8, color=color)
    
    ax2.set_xlabel('Number of Features')
    ax2.set_ylabel('Cumulative Importance')
    ax2.set_title('Cumulative Feature Importance', fontweight='bold')
    ax2.legend()
    ax2.grid(alpha=0.3)
    ax2.set_xlim(0, len(cumsum))
    ax2.set_ylim(0, 1.05)
    
    # 3. Importance by sensor
    ax3 = plt.subplot(2, 2, 3)
    sensor_counts = {k: len(v) for k, v in results['feature_groups']['by_sensor'].items()}
    sensors = list(sensor_counts.keys())[:10]  # Top 10
    counts = [sensor_counts[s] for s in sensors]
    
    ax3.bar(range(len(sensors)), counts, color='#88C0D0')
    ax3.set_xticks(range(len(sensors)))
    ax3.set_xticklabels(sensors, rotation=45, ha='right', fontsize=8)
    ax3.set_ylabel('Number of Important Features')
    ax3.set_title('Important Features by Sensor', fontweight='bold')
    ax3.grid(axis='y', alpha=0.3)
    
    # 4. Importance by feature type
    ax4 = plt.subplot(2, 2, 4)
    type_counts = {k: len(v) for k, v in results['feature_groups']['by_type'].items()}
    types = list(type_counts.keys())[:10]
    t_counts = [type_counts[t] for t in types]
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(types)))
    ax4.pie(t_counts, labels=types, autopct='%1.1f%%', startangle=90, colors=colors)
    ax4.set_title('Distribution by Feature Type', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'feature_importance_analysis.png', dpi=150, bbox_inches='tight')
    print(f"Saved analysis plot to {output_dir / 'feature_importance_analysis.png'}")


def generate_edge_config(results: Dict, output_path: Path):
    """
    Generate configuration file for edge deployment with reduced features.
    
    This creates a config that can be used by the rolling extractor
    to compute only the essential features.
    """
    essential_features = results['thresholds']['95_percent']['features']
    
    # Categorize features
    sensor_features = []
    cross_sensor_features = []
    
    for feature in essential_features:
        if any(sensor in feature for sensor in ['L_P_', 'L_S_', 'R_P_', 'R_S_']):
            sensor_features.append(feature)
        else:
            cross_sensor_features.append(feature)
    
    edge_config = {
        'metadata': {
            'description': 'Edge-optimized feature configuration',
            'generated_from': 'feature_importance.py',
            'original_features': results['total_features'],
            'edge_features': len(essential_features),
            'reduction_percent': round(
                (1 - len(essential_features) / results['total_features']) * 100, 1
            ),
            'retained_importance': '95%'
        },
        'features': {
            'all': essential_features,
            'per_sensor': sensor_features,
            'cross_sensor': cross_sensor_features
        },
        'sensors_required': list(results['feature_groups']['by_sensor'].keys()),
        'computational_savings': {
            'features_reduced': results['total_features'] - len(essential_features),
            'estimated_speedup': round(results['total_features'] / len(essential_features), 1)
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(edge_config, f, indent=2)
    
    print(f"Saved edge config to {output_path}")
    return edge_config


def print_summary(results: Dict):
    """Print human-readable summary of analysis."""
    print("\n" + "="*60)
    print("FEATURE IMPORTANCE ANALYSIS SUMMARY")
    print("="*60)
    
    print(f"\nTotal features: {results['total_features']}")
    
    print("\nTop 10 Most Important Features:")
    for i, feat in enumerate(results['top_features'][:10], 1):
        print(f"  {i:2d}. {feat['name'][:40]:40s} {feat['importance']:.4f}")
    
    print("\nOptimization Thresholds:")
    for threshold in [90, 95, 99]:
        info = results['thresholds'][f'{threshold}_percent']
        print(f"  {threshold}% importance: {info['n_features']} features "
              f"({info['n_features']/results['total_features']*100:.1f}%)")
    
    print("\nTop Sensors by Important Feature Count:")
    for sensor, features in list(results['feature_groups']['by_sensor'].items())[:6]:
        print(f"  {sensor}: {len(features)} features")
    
    print("\nTop Feature Types:")
    for ftype, features in list(results['feature_groups']['by_type'].items())[:5]:
        print(f"  {ftype}: {len(features)} features")
    
    print("\nRecommendation:")
    n_95 = results['thresholds']['95_percent']['n_features']
    print(f"  → Use {n_95} features for edge deployment")
    print(f"  → Achieves 95% of model performance")
    print(f"  → {(1 - n_95/results['total_features'])*100:.1f}% reduction in computation")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze feature importance for edge deployment'
    )
    parser.add_argument('--model', '-m', required=True,
                       help='Path to trained model .joblib file')
    parser.add_argument('--output', '-o', default='./results',
                       help='Output directory for results')
    parser.add_argument('--metadata',
                       help='Path to model metadata (optional)')
    
    args = parser.parse_args()
    
    # Load model
    print(f"Loading model from {args.model}...")
    model = joblib.load(args.model)
    
    # Load feature names
    if args.metadata:
        metadata = joblib.load(args.metadata)
        feature_names = metadata['feature_names']
    else:
        # Try to infer from model
        metadata_path = args.model.replace('.joblib', '_metadata.joblib')
        if Path(metadata_path).exists():
            metadata = joblib.load(metadata_path)
            feature_names = metadata['feature_names']
        else:
            # Generate generic names
            n_features = model.n_features_in_
            feature_names = [f'feature_{i}' for i in range(n_features)]
            print(f"Warning: No metadata found. Using generic feature names.")
    
    # Analyze
    print(f"Analyzing {len(feature_names)} features...")
    results = analyze_feature_importance(model, feature_names)
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate outputs
    print_summary(results)
    plot_importance_analysis(results, output_dir)
    
    # Generate edge config
    edge_config = generate_edge_config(results, output_dir / 'edge_feature_config.json')
    
    # Save full results
    with open(output_dir / 'feature_importance_results.json', 'w') as f:
        # Convert to serializable format
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Analysis complete. Results saved to {output_dir}/")
    print(f"   - edge_feature_config.json: Use this for edge deployment")
    print(f"   - feature_importance_analysis.png: Visualization")
    print(f"   - feature_importance_results.json: Full analysis data")


if __name__ == '__main__':
    main()
