#!/usr/bin/env python3
"""
Smart Socks - Sensor Characterization
ELEC-E7840 Smart Wearables (Aalto University)

Analyzes sensor calibration data to characterize the pressure-to-ADC response.
Generates calibration curves and computes sensor parameters.

Usage:
    python sensor_characterization.py --data ../03_Data/calibration/
"""

import argparse
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats


# Sensor channel names
SENSOR_NAMES = [
    "L_Heel", "L_Arch", "L_MetaM", "L_MetaL", "L_Toe",
    "R_Heel", "R_Arch", "R_MetaM", "R_MetaL", "R_Toe"
]

# Reference weights for calibration (in grams)
CALIBRATION_WEIGHTS = [0, 100, 200, 500, 1000, 2000, 5000]


def load_calibration_data(data_dir):
    """
    Load calibration CSV files from directory.

    Expected file naming: <weight_grams>.csv
    Each file contains steady-state readings at that weight.
    """
    calibration_data = {}

    for weight in CALIBRATION_WEIGHTS:
        filepath = os.path.join(data_dir, f"{weight}g.csv")
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            calibration_data[weight] = df
            print(f"Loaded {weight}g: {len(df)} samples")
        else:
            print(f"Warning: {filepath} not found")

    return calibration_data


def compute_sensor_statistics(calibration_data):
    """
    Compute mean and std for each sensor at each weight level.
    """
    results = []

    for weight, df in calibration_data.items():
        for sensor in SENSOR_NAMES:
            if sensor in df.columns:
                mean_val = df[sensor].mean()
                std_val = df[sensor].std()
                results.append({
                    'weight_g': weight,
                    'sensor': sensor,
                    'mean_adc': mean_val,
                    'std_adc': std_val
                })

    return pd.DataFrame(results)


def fit_calibration_curves(stats_df):
    """
    Fit linear/polynomial curves to pressure vs ADC data for each sensor.
    """
    fits = {}

    for sensor in SENSOR_NAMES:
        sensor_data = stats_df[stats_df['sensor'] == sensor].sort_values('weight_g')

        if len(sensor_data) >= 2:
            weights = sensor_data['weight_g'].values
            adc_values = sensor_data['mean_adc'].values

            # Linear fit
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                weights, adc_values
            )

            fits[sensor] = {
                'slope': slope,
                'intercept': intercept,
                'r_squared': r_value ** 2,
                'weights': weights,
                'adc_values': adc_values
            }

            print(f"{sensor}: ADC = {slope:.4f} * weight + {intercept:.2f} "
                  f"(R² = {r_value**2:.4f})")

    return fits


def plot_calibration_curves(fits, output_dir):
    """
    Generate calibration curve plots for all sensors.
    """
    fig, axes = plt.subplots(2, 5, figsize=(15, 6))
    axes = axes.flatten()

    for idx, sensor in enumerate(SENSOR_NAMES):
        ax = axes[idx]

        if sensor in fits:
            fit = fits[sensor]
            weights = fit['weights']
            adc_values = fit['adc_values']

            # Scatter plot of measured data
            ax.scatter(weights, adc_values, color='blue', label='Measured')

            # Fitted line
            x_fit = np.linspace(min(weights), max(weights), 100)
            y_fit = fit['slope'] * x_fit + fit['intercept']
            ax.plot(x_fit, y_fit, 'r-', label=f"R²={fit['r_squared']:.3f}")

            ax.set_xlabel('Weight (g)')
            ax.set_ylabel('ADC Value')
            ax.set_title(sensor)
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)

    plt.tight_layout()

    # Save plot
    output_path = os.path.join(output_dir, 'calibration_curves.png')
    plt.savefig(output_path, dpi=150)
    print(f"Saved calibration curves to {output_path}")

    plt.show()


def generate_calibration_report(stats_df, fits, output_dir):
    """
    Generate a summary report of sensor characteristics.
    """
    report_path = os.path.join(output_dir, 'calibration_report.txt')

    with open(report_path, 'w') as f:
        f.write("Smart Socks Sensor Characterization Report\n")
        f.write("=" * 50 + "\n\n")

        f.write("Sensor Calibration Parameters (Linear Fit)\n")
        f.write("-" * 50 + "\n")
        f.write(f"{'Sensor':<12} {'Slope':>10} {'Intercept':>12} {'R²':>8}\n")
        f.write("-" * 50 + "\n")

        for sensor in SENSOR_NAMES:
            if sensor in fits:
                fit = fits[sensor]
                f.write(f"{sensor:<12} {fit['slope']:>10.4f} "
                       f"{fit['intercept']:>12.2f} {fit['r_squared']:>8.4f}\n")

        f.write("\n\nSensor Statistics by Weight\n")
        f.write("-" * 50 + "\n")

        for weight in sorted(stats_df['weight_g'].unique()):
            f.write(f"\nWeight: {weight}g\n")
            weight_data = stats_df[stats_df['weight_g'] == weight]
            for _, row in weight_data.iterrows():
                f.write(f"  {row['sensor']:<12}: "
                       f"mean={row['mean_adc']:.1f}, std={row['std_adc']:.2f}\n")

    print(f"Saved calibration report to {report_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Smart Socks Sensor Characterization'
    )
    parser.add_argument(
        '--data', '-d',
        required=True,
        help='Directory containing calibration CSV files'
    )
    parser.add_argument(
        '--output', '-o',
        default=None,
        help='Output directory for plots and reports (default: same as data)'
    )

    args = parser.parse_args()

    output_dir = args.output if args.output else args.data
    os.makedirs(output_dir, exist_ok=True)

    print("Loading calibration data...")
    calibration_data = load_calibration_data(args.data)

    if not calibration_data:
        print("Error: No calibration data found.")
        print(f"Expected files like: 0g.csv, 100g.csv, etc. in {args.data}")
        return 1

    print("\nComputing sensor statistics...")
    stats_df = compute_sensor_statistics(calibration_data)

    print("\nFitting calibration curves...")
    fits = fit_calibration_curves(stats_df)

    print("\nGenerating plots...")
    plot_calibration_curves(fits, output_dir)

    print("\nGenerating report...")
    generate_calibration_report(stats_df, fits, output_dir)

    print("\nCharacterization complete!")
    return 0


if __name__ == '__main__':
    exit(main())
