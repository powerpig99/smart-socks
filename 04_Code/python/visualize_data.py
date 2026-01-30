#!/usr/bin/env python3
"""
Smart Socks - Data Visualization Tool
ELEC-E7840 Smart Wearables (Aalto University)

Visualizes sensor data from CSV files for quick inspection and analysis.

Usage:
    python visualize_data.py --file ../03_Data/raw/S01_walking_forward_*.csv
    python visualize_data.py --dir ../03_Data/raw/ --activity walking_forward
"""

import argparse
import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import seaborn as sns

from config import SENSORS, ACTIVITIES

# Backwards compatibility
SENSOR_NAMES = SENSORS['names']


def extract_activity_from_filename(filename):
    """Extract activity name from filename by matching against known activities.
    
    Args:
        filename: Filename like 'S01_walking_forward_20260115_143022.csv'
    
    Returns:
        Activity name string, or 'unknown' if not found
    """
    # Remove extension
    name = filename.replace('.csv', '')
    
    # Try to match each known activity
    for activity in ACTIVITIES['all']:
        if activity in name:
            return activity
    
    # Fallback: old parsing method
    parts = name.split('_')
    if len(parts) >= 3:
        return '_'.join(parts[1:-2])
    
    return 'unknown'

# Color scheme for sensors (auto-generated from config)
SENSOR_COLORS = {
    name: color for name, color in zip(
        SENSORS['names'],
        ["#e41a1c", "#4daf4a", "#ff7f00", "#377eb8", "#984ea3", "#ffff33"]
    )
}

LINE_STYLES = {
    name: "-" if name.startswith("L_") else "--"
    for name in SENSORS['names']
}


def load_data(filepath):
    """Load and validate sensor data."""
    df = pd.read_csv(filepath)
    
    # Check required columns
    missing = [col for col in SENSOR_NAMES if col not in df.columns]
    if missing:
        print(f"Warning: Missing columns: {missing}")
    
    # Convert time to seconds
    if 'time_ms' in df.columns:
        df['time_sec'] = df['time_ms'] / 1000
    
    return df


def plot_time_series(df, title=None, save_path=None):
    """
    Plot sensor values over time.
    """
    ncols = 2
    nrows = (len(SENSOR_NAMES) + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, nrows * 3.2))
    axes = axes.flatten()
    
    time_col = 'time_sec' if 'time_sec' in df.columns else 'time_ms'
    
    for idx, sensor in enumerate(SENSOR_NAMES):
        ax = axes[idx]
        if sensor in df.columns:
            ax.plot(df[time_col], df[sensor], 
                   color=SENSOR_COLORS.get(sensor, 'blue'),
                   linestyle=LINE_STYLES.get(sensor, '-'),
                   linewidth=0.8, label=sensor)
            ax.set_ylabel('ADC Value')
            ax.set_xlabel('Time (s)' if 'sec' in time_col else 'Time (ms)')
            ax.set_title(sensor)
            ax.grid(True, alpha=0.3)
            ax.legend(loc='upper right')
    
    if title:
        fig.suptitle(title, fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Saved plot to {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_pressure_heatmap(df, save_path=None):
    """
    Create a heatmap showing pressure distribution over time.
    """
    # Create matrix for heatmap
    sensor_data = df[SENSOR_NAMES].values.T
    
    # Downsample for visualization if needed
    if len(df) > 1000:
        step = len(df) // 1000
        sensor_data = sensor_data[:, ::step]
        time_labels = df['time_sec'].iloc[::step].values if 'time_sec' in df.columns else df['time_ms'].iloc[::step].values
    else:
        time_labels = df['time_sec'].values if 'time_sec' in df.columns else df['time_ms'].values
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    im = ax.imshow(sensor_data, aspect='auto', cmap='YlOrRd', interpolation='nearest')
    
    ax.set_yticks(range(len(SENSOR_NAMES)))
    ax.set_yticklabels(SENSOR_NAMES)
    ax.set_xlabel('Time')
    ax.set_title('Pressure Distribution Heatmap')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('ADC Value')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Saved heatmap to {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_average_pressure(df, save_path=None):
    """
    Plot average pressure per sensor zone as a bar chart.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Left foot (pressure sensors only)
    left_sensors = SENSORS['left_pressure']
    left_means = [df[s].mean() if s in df.columns else 0 for s in left_sensors]
    left_stds = [df[s].std() if s in df.columns else 0 for s in left_sensors]
    
    axes[0].bar(range(len(left_sensors)), left_means, yerr=left_stds, 
               color=[SENSOR_COLORS[s] for s in left_sensors],
               capsize=5, alpha=0.8)
    axes[0].set_xticks(range(len(left_sensors)))
    axes[0].set_xticklabels(left_sensors, rotation=45, ha='right')
    axes[0].set_ylabel('Average ADC Value')
    axes[0].set_title('Left Foot - Average Pressure')
    axes[0].grid(True, alpha=0.3, axis='y')
    
    # Right foot (pressure sensors only)
    right_sensors = SENSORS['right_pressure']
    right_means = [df[s].mean() if s in df.columns else 0 for s in right_sensors]
    right_stds = [df[s].std() if s in df.columns else 0 for s in right_sensors]
    
    axes[1].bar(range(len(right_sensors)), right_means, yerr=right_stds,
               color=[SENSOR_COLORS[s] for s in right_sensors],
               capsize=5, alpha=0.8)
    axes[1].set_xticks(range(len(right_sensors)))
    axes[1].set_xticklabels(right_sensors, rotation=45, ha='right')
    axes[1].set_ylabel('Average ADC Value')
    axes[1].set_title('Right Foot - Average Pressure')
    axes[1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Saved average pressure plot to {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_correlation_matrix(df, save_path=None):
    """
    Plot correlation matrix between sensors.
    """
    # Compute correlation matrix
    corr_matrix = df[SENSOR_NAMES].corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm',
                center=0, vmin=-1, vmax=1, ax=ax,
                square=True, linewidths=0.5)
    
    ax.set_title('Sensor Correlation Matrix')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Saved correlation matrix to {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_foot_pressure_map(df, time_idx=None, save_path=None):
    """
    Create a visual representation of pressure on foot.
    
    Updated for 6-sensor design (Jan 2026):
    - 2 pressure sensors per foot: Heel and Ball
    - 1 stretch sensor per leg: Knee
    """
    if time_idx is None:
        time_idx = len(df) // 2  # Use middle time point
    
    # Extract values at specific time
    row = df.iloc[time_idx]
    
    # 6-sensor layout: L_P_Heel, L_P_Ball, L_S_Knee, R_P_Heel, R_P_Ball, R_S_Knee
    # Map to current sensor names from config
    from config import SENSORS
    
    # Get pressure values (default to 0 if column missing)
    left_heel = row.get('L_P_Heel', 0)
    left_ball = row.get('L_P_Ball', 0)
    left_knee = row.get('L_S_Knee', 0)
    right_heel = row.get('R_P_Heel', 0)
    right_ball = row.get('R_P_Ball', 0)
    right_knee = row.get('R_S_Knee', 0)
    
    fig, axes = plt.subplots(1, 2, figsize=(12, 8))
    
    # Left foot (Heel + Ball pressure + Knee stretch indicator)
    left_values = [left_heel, left_ball, left_knee]
    # Positions: Heel at bottom, Ball at top, Knee shown separately
    left_positions = [(0.5, 0.25), (0.5, 0.75)]  # Heel, Ball
    left_labels = ['Heel', 'Ball']
    
    ax = axes[0]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(f'Left Foot Pressure Map\nKnee: {left_knee:.0f}')
    
    # Draw foot outline (simplified)
    foot_outline = plt.Rectangle((0.2, 0.1), 0.6, 0.8, fill=False, linewidth=2)
    ax.add_patch(foot_outline)
    
    # Draw pressure circles (heel and ball only)
    max_val = max(left_values[:2]) if max(left_values[:2]) > 0 else 1
    for (x, y), val, name in zip(left_positions, left_values[:2], left_labels):
        size = (val / max_val) * 800
        color = plt.cm.YlOrRd(val / 4095)
        ax.scatter(x, y, s=size, c=[color], alpha=0.7, edgecolors='black')
        ax.annotate(f'{name}\n{val:.0f}', (x, y), ha='center', va='center', fontsize=9)
    
    # Right foot
    right_values = [right_heel, right_ball, right_knee]
    right_positions = [(0.5, 0.25), (0.5, 0.75)]  # Heel, Ball
    right_labels = ['Heel', 'Ball']
    
    ax = axes[1]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(f'Right Foot Pressure Map\nKnee: {right_knee:.0f}')
    
    foot_outline = plt.Rectangle((0.2, 0.1), 0.6, 0.8, fill=False, linewidth=2)
    ax.add_patch(foot_outline)
    
    max_val = max(right_values[:2]) if max(right_values[:2]) > 0 else 1
    for (x, y), val, name in zip(right_positions, right_values[:2], right_labels):
        size = (val / max_val) * 800
        color = plt.cm.YlOrRd(val / 4095)
        ax.scatter(x, y, s=size, c=[color], alpha=0.7, edgecolors='black')
        ax.annotate(f'{name}\n{val:.0f}', (x, y), ha='center', va='center', fontsize=9)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Saved pressure map to {save_path}")
    else:
        plt.show()
    
    plt.close()


def compare_activities(data_dict, save_path=None):
    """
    Compare sensor patterns across different activities.
    
    Args:
        data_dict: Dictionary mapping activity names to DataFrames
    """
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes = axes.flatten()
    
    # Select a representative sensor for each zone
    plot_sensors = SENSORS['pressure_sensors']  # Plot pressure sensors by default
    
    for idx, sensor in enumerate(plot_sensors):
        ax = axes[idx]
        
        for activity, df in data_dict.items():
            if sensor in df.columns:
                time_col = 'time_sec' if 'time_sec' in df.columns else 'time_ms'
                # Normalize time to start from 0
                t = df[time_col] - df[time_col].iloc[0]
                # Limit to first 10 seconds
                mask = t <= 10
                ax.plot(t[mask], df[sensor][mask], label=activity, alpha=0.7, linewidth=1)
        
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('ADC Value')
        ax.set_title(sensor)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    
    fig.suptitle('Activity Comparison', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Saved comparison plot to {save_path}")
    else:
        plt.show()
    
    plt.close()


def main():
    parser = argparse.ArgumentParser(
        description='Smart Socks Data Visualization'
    )
    parser.add_argument(
        '--file', '-f',
        help='Single CSV file to visualize'
    )
    parser.add_argument(
        '--dir', '-d',
        help='Directory of CSV files to visualize'
    )
    parser.add_argument(
        '--activity',
        help='Filter files by activity name'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output directory for plots (if not specified, display interactively)'
    )
    parser.add_argument(
        '--plot-type',
        choices=['timeseries', 'heatmap', 'average', 'correlation', 'pressure_map', 'all'],
        default='all',
        help='Type of plot to generate'
    )
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Compare multiple activities (requires --dir)'
    )

    args = parser.parse_args()

    if args.output:
        os.makedirs(args.output, exist_ok=True)

    # Get list of files
    files = []
    if args.file:
        files = [args.file]
    elif args.dir:
        pattern = os.path.join(args.dir, '**/*.csv')
        files = glob.glob(pattern, recursive=True)
        if args.activity:
            files = [f for f in files if args.activity in f]
    else:
        print("Error: Specify either --file or --dir")
        return 1

    if not files:
        print("No files found")
        return 1

    print(f"Found {len(files)} file(s)")

    if args.compare and len(files) > 1:
        # Load all files for comparison
        data_dict = {}
        for filepath in files[:6]:  # Limit to 6 activities
            activity = extract_activity_from_filename(os.path.basename(filepath))
            df = load_data(filepath)
            data_dict[activity] = df
        
        save_path = os.path.join(args.output, 'activity_comparison.png') if args.output else None
        compare_activities(data_dict, save_path)
    else:
        # Process single file
        filepath = files[0]
        print(f"Processing: {filepath}")
        
        df = load_data(filepath)
        basename = os.path.basename(filepath).replace('.csv', '')
        
        if args.plot_type in ['timeseries', 'all']:
            save_path = os.path.join(args.output, f'{basename}_timeseries.png') if args.output else None
            plot_time_series(df, title=basename, save_path=save_path)
        
        if args.plot_type in ['heatmap', 'all']:
            save_path = os.path.join(args.output, f'{basename}_heatmap.png') if args.output else None
            plot_pressure_heatmap(df, save_path=save_path)
        
        if args.plot_type in ['average', 'all']:
            save_path = os.path.join(args.output, f'{basename}_average.png') if args.output else None
            plot_average_pressure(df, save_path=save_path)
        
        if args.plot_type in ['correlation', 'all']:
            save_path = os.path.join(args.output, f'{basename}_correlation.png') if args.output else None
            plot_correlation_matrix(df, save_path=save_path)
        
        if args.plot_type in ['pressure_map', 'all']:
            save_path = os.path.join(args.output, f'{basename}_pressure_map.png') if args.output else None
            plot_foot_pressure_map(df, save_path=save_path)

    print("\nVisualization complete!")
    return 0


if __name__ == '__main__':
    exit(main())
