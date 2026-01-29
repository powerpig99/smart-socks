#!/usr/bin/env python3
"""
Smart Socks - Data Augmentation
ELEC-E7840 Smart Wearables (Aalto University)

Data augmentation techniques for improving model robustness.
Generates synthetic training samples from existing data.

Usage:
    python data_augmentation.py --input ../../03_Data/processed/ --output ../../03_Data/augmented/
"""

import argparse
import numpy as np
import pandas as pd
from scipy import signal
from scipy.interpolate import interp1d
import os
from pathlib import Path
from tqdm import tqdm

from config import SENSORS, HARDWARE


class DataAugmenter:
    """Data augmentation for sensor data."""
    
    def __init__(self, random_state=42):
        self.rng = np.random.RandomState(random_state)
        self.sensor_names = SENSORS['names']
        
    def add_noise(self, df, noise_level=0.01):
        """
        Add Gaussian noise to sensor readings.
        
        Args:
            df: DataFrame with sensor data
            noise_level: Standard deviation of noise as fraction of signal range
            
        Returns:
            Augmented DataFrame
        """
        df_aug = df.copy()
        
        for sensor in self.sensor_names:
            if sensor in df.columns:
                signal_range = df[sensor].max() - df[sensor].min()
                noise = self.rng.normal(0, noise_level * signal_range, len(df))
                df_aug[sensor] = df[sensor] + noise
                # Clip to valid ADC range
                df_aug[sensor] = df_aug[sensor].clip(0, HARDWARE['adc_max_value'])
        
        return df_aug
    
    def time_shift(self, df, max_shift_ms=100):
        """
        Shift data in time (circular shift).
        
        Args:
            df: DataFrame with sensor data
            max_shift_ms: Maximum time shift in milliseconds
            
        Returns:
            Augmented DataFrame
        """
        df_aug = df.copy()
        
        # Calculate shift in samples
        max_shift_samples = int(max_shift_ms / HARDWARE['sample_interval_ms'])
        shift = self.rng.randint(-max_shift_samples, max_shift_samples)
        
        for sensor in self.sensor_names:
            if sensor in df.columns:
                df_aug[sensor] = np.roll(df[sensor].values, shift)
        
        # Adjust timestamps
        if 'time_ms' in df.columns:
            df_aug['time_ms'] = df['time_ms'] + shift * HARDWARE['sample_interval_ms']
        
        return df_aug
    
    def scale_amplitude(self, df, scale_range=(0.9, 1.1)):
        """
        Scale signal amplitude.
        
        Args:
            df: DataFrame with sensor data
            scale_range: Range of scaling factors
            
        Returns:
            Augmented DataFrame
        """
        df_aug = df.copy()
        
        for sensor in self.sensor_names:
            if sensor in df.columns:
                scale = self.rng.uniform(*scale_range)
                mean = df[sensor].mean()
                df_aug[sensor] = (df[sensor] - mean) * scale + mean
                df_aug[sensor] = df_aug[sensor].clip(0, HARDWARE['adc_max_value'])
        
        return df_aug
    
    def time_stretch(self, df, stretch_range=(0.9, 1.1)):
        """
        Stretch or compress time axis (change speed).
        
        Args:
            df: DataFrame with sensor data
            stretch_range: Range of stretch factors (<1 = faster, >1 = slower)
            
        Returns:
            Augmented DataFrame
        """
        stretch = self.rng.uniform(*stretch_range)
        n_samples = len(df)
        n_new = int(n_samples * stretch)
        
        # Original time indices
        old_indices = np.arange(n_samples)
        new_indices = np.linspace(0, n_samples - 1, n_new)
        
        df_aug = pd.DataFrame()
        
        for sensor in self.sensor_names:
            if sensor in df.columns:
                # Interpolate
                f = interp1d(old_indices, df[sensor].values, kind='linear', 
                            fill_value='extrapolate')
                df_aug[sensor] = f(new_indices)
        
        # Adjust timestamps
        if 'time_ms' in df.columns:
            df_aug['time_ms'] = np.linspace(
                df['time_ms'].iloc[0],
                df['time_ms'].iloc[0] + n_new * HARDWARE['sample_interval_ms'] * stretch,
                n_new
            )
        
        return df_aug
    
    def random_crop(self, df, crop_ratio=0.9):
        """
        Randomly crop a portion of the signal.
        
        Args:
            df: DataFrame with sensor data
            crop_ratio: Ratio of data to keep
            
        Returns:
            Augmented DataFrame
        """
        n_samples = len(df)
        crop_length = int(n_samples * crop_ratio)
        
        start_idx = self.rng.randint(0, n_samples - crop_length)
        end_idx = start_idx + crop_length
        
        return df.iloc[start_idx:end_idx].reset_index(drop=True)
    
    def permute_segments(self, df, n_segments=4):
        """
        Permute segments of the signal (shuffle order).
        
        Args:
            df: DataFrame with sensor data
            n_segments: Number of segments to create
            
        Returns:
            Augmented DataFrame
        """
        n_samples = len(df)
        segment_length = n_samples // n_segments
        
        segments = []
        for i in range(n_segments):
            start = i * segment_length
            end = start + segment_length if i < n_segments - 1 else n_samples
            segments.append(df.iloc[start:end])
        
        # Shuffle segments
        self.rng.shuffle(segments)
        
        # Concatenate
        df_aug = pd.concat(segments, ignore_index=True)
        
        # Update timestamps
        if 'time_ms' in df.columns:
            time_diff = df['time_ms'].iloc[1] - df['time_ms'].iloc[0]
            df_aug['time_ms'] = df['time_ms'].iloc[0] + np.arange(len(df_aug)) * time_diff
        
        return df_aug
    
    def add_sensor_dropout(self, df, dropout_prob=0.1):
        """
        Randomly drop sensor readings (simulate disconnected sensor).
        
        Args:
            df: DataFrame with sensor data
            dropout_prob: Probability of dropping a sensor at each timestep
            
        Returns:
            Augmented DataFrame
        """
        df_aug = df.copy()
        
        for sensor in self.sensor_names:
            if sensor in df.columns:
                mask = self.rng.random(len(df)) < dropout_prob
                df_aug.loc[mask, sensor] = 0  # Or could use NaN
        
        return df_aug
    
    def smooth_signal(self, df, window_length=5):
        """
        Apply smoothing filter.
        
        Args:
            df: DataFrame with sensor data
            window_length: Window size for smoothing
            
        Returns:
            Augmented DataFrame
        """
        df_aug = df.copy()
        
        for sensor in self.sensor_names:
            if sensor in df.columns:
                df_aug[sensor] = signal.savgol_filter(
                    df[sensor], window_length=window_length, polyorder=2
                )
        
        return df_aug
    
    def augment(self, df, techniques=None, n_augmentations=3):
        """
        Apply multiple augmentation techniques.
        
        Args:
            df: Original DataFrame
            techniques: List of technique names (None = use all)
            n_augmentations: Number of augmented samples to generate
            
        Returns:
            List of augmented DataFrames
        """
        all_techniques = {
            'noise': self.add_noise,
            'time_shift': self.time_shift,
            'scale': self.scale_amplitude,
            'stretch': self.time_stretch,
            'crop': self.random_crop,
            'permute': self.permute_segments,
            'dropout': self.add_sensor_dropout,
            'smooth': self.smooth_signal,
        }
        
        if techniques is None:
            techniques = list(all_techniques.keys())
        
        augmented = []
        
        for i in range(n_augmentations):
            # Select random technique
            tech_name = self.rng.choice(techniques)
            tech_func = all_techniques[tech_name]
            
            try:
                df_aug = tech_func(df)
                augmented.append(df_aug)
            except Exception as e:
                print(f"Augmentation failed: {e}")
                continue
        
        return augmented


def augment_dataset(input_dir, output_dir, n_augmentations=3, techniques=None):
    """
    Augment entire dataset.
    
    Args:
        input_dir: Directory with original CSV files
        output_dir: Directory to save augmented files
        n_augmentations: Number of augmented samples per file
        techniques: List of augmentation techniques to use
    """
    from glob import glob
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all CSV files
    csv_files = glob(os.path.join(input_dir, '**/*.csv'), recursive=True)
    
    if not csv_files:
        print(f"No CSV files found in {input_dir}")
        return
    
    augmenter = DataAugmenter()
    
    print(f"Found {len(csv_files)} files to augment")
    print(f"Generating {n_augmentations} augmentations per file...")
    
    total_created = 0
    
    for filepath in tqdm(csv_files, desc="Augmenting"):
        try:
            # Load data
            df = pd.read_csv(filepath)
            
            # Generate augmentations
            augmented_dfs = augmenter.augment(df, techniques, n_augmentations)
            
            # Save augmented files
            basename = Path(filepath).stem
            for i, df_aug in enumerate(augmented_dfs):
                aug_name = f"{basename}_aug{i+1}.csv"
                output_path = os.path.join(output_dir, aug_name)
                df_aug.to_csv(output_path, index=False)
                total_created += 1
                
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            continue
    
    print(f"\nCreated {total_created} augmented files")
    print(f"Output directory: {output_dir}")


def main():
    parser = argparse.ArgumentParser(description='Smart Socks Data Augmentation')
    parser.add_argument('--input', '-i', required=True, help='Input directory with CSV files')
    parser.add_argument('--output', '-o', required=True, help='Output directory for augmented files')
    parser.add_argument('--n-augmentations', '-n', type=int, default=3,
                       help='Number of augmentations per file (default: 3)')
    parser.add_argument('--techniques', nargs='+',
                       choices=['noise', 'time_shift', 'scale', 'stretch', 'crop', 
                               'permute', 'dropout', 'smooth'],
                       help='Augmentation techniques to use (default: all)')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    
    args = parser.parse_args()
    
    # Set random seed
    np.random.seed(args.seed)
    
    # Run augmentation
    augment_dataset(
        input_dir=args.input,
        output_dir=args.output,
        n_augmentations=args.n_augmentations,
        techniques=args.techniques
    )


if __name__ == '__main__':
    main()
