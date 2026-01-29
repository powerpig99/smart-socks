#!/usr/bin/env python3
"""
Smart Socks - Full ML Pipeline
ELEC-E7840 Smart Wearables (Aalto University)

Runs the complete ML pipeline from raw data to trained model:
1. Data preprocessing
2. Feature extraction
3. Model training with cross-validation
4. Evaluation and report generation

Usage:
    python run_full_pipeline.py --raw-data ../03_Data/raw/ --output ../05_Analysis/
"""

import argparse
import os
import sys
import subprocess
import time
from datetime import datetime


def run_command(cmd, description):
    """Run a command and print status."""
    print("\n" + "="*60)
    print(f"STEP: {description}")
    print("="*60)
    print(f"Command: {cmd}")
    print()
    
    start_time = time.time()
    result = subprocess.run(cmd, shell=True)
    elapsed = time.time() - start_time
    
    if result.returncode != 0:
        print(f"❌ FAILED after {elapsed:.1f}s (exit code: {result.returncode})")
        return False
    else:
        print(f"✅ COMPLETED in {elapsed:.1f}s")
        return True


def main():
    parser = argparse.ArgumentParser(
        description='Smart Socks Full ML Pipeline'
    )
    parser.add_argument(
        '--raw-data', '-i',
        required=True,
        help='Directory containing raw CSV files'
    )
    parser.add_argument(
        '--output', '-o',
        default='../05_Analysis/',
        help='Output directory for all results'
    )
    parser.add_argument(
        '--skip-preprocessing',
        action='store_true',
        help='Skip preprocessing step (use existing processed data)'
    )
    parser.add_argument(
        '--test-subjects',
        nargs='+',
        default=None,
        help='Specific subjects for testing (e.g., S07 S08 S09)'
    )

    args = parser.parse_args()

    start_time = time.time()
    
    # Create output directories
    processed_dir = os.path.join(os.path.dirname(args.raw_data), 'processed')
    features_dir = os.path.join(os.path.dirname(args.raw_data), 'features')
    
    os.makedirs(args.output, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(features_dir, exist_ok=True)

    print("\n" + "🧦"*30)
    print("  SMART SOCKS - FULL ML PIPELINE")
    print("🧦"*30)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Raw data: {args.raw_data}")
    print(f"Output: {args.output}")
    print()

    steps_completed = 0
    total_steps = 3 if not args.skip_preprocessing else 2

    # Step 1: Data Preprocessing
    if not args.skip_preprocessing:
        cmd = f'python data_preprocessing.py --input "{args.raw_data}" --output "{processed_dir}" --report "{args.output}/quality_report.csv"'
        if run_command(cmd, "Data Preprocessing"):
            steps_completed += 1
        else:
            print("\n⚠️  Preprocessing failed. Continuing with existing data...")
    else:
        print("\n⏭️  Skipping preprocessing (using existing processed data)")
        steps_completed += 1

    # Step 2: Feature Extraction
    features_file = os.path.join(features_dir, 'features_all.csv')
    cmd = f'python feature_extraction.py --input "{processed_dir if not args.skip_preprocessing else args.raw_data}" --output "{features_dir}"'
    if run_command(cmd, "Feature Extraction"):
        steps_completed += 1
    else:
        print("\n❌ Feature extraction failed!")
        return 1

    # Step 3: Model Training
    if not os.path.exists(features_file):
        print(f"\n❌ Features file not found: {features_file}")
        return 1
    
    test_subjects_arg = f'--test-subjects {" ".join(args.test_subjects)}' if args.test_subjects else ''
    cmd = f'python train_model.py --features "{features_file}" --output "{args.output}" {test_subjects_arg}'
    if run_command(cmd, "Model Training"):
        steps_completed += 1
    else:
        print("\n❌ Model training failed!")
        return 1

    # Step 4: Cross-Subject Validation (optional but recommended)
    print("\n" + "="*60)
    print("BONUS: Cross-Subject Validation")
    print("="*60)
    cmd = f'python train_model.py --features "{features_file}" --output "{args.output}" --cross-subject'
    if run_command(cmd, "Cross-Subject Validation"):
        print("✅ Cross-subject validation completed")

    # Step 5: Generate Report
    print("\n" + "="*60)
    print("FINAL: Report Generation")
    print("="*60)
    report_dir = os.path.join(args.output, 'report')
    os.makedirs(report_dir, exist_ok=True)
    cmd = f'python analysis_report.py --results-dir "{args.output}" --output "{report_dir}"'
    if run_command(cmd, "Report Generation"):
        print("✅ Report generated")

    # Summary
    total_time = time.time() - start_time
    
    print("\n" + "="*60)
    print("PIPELINE SUMMARY")
    print("="*60)
    print(f"Steps completed: {steps_completed}/{total_steps}")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if steps_completed == total_steps:
        print("\n✅ PIPELINE COMPLETED SUCCESSFULLY!")
        print(f"\nResults saved to: {args.output}")
        print(f"Model file: {os.path.join(args.output, 'smart_socks_model.joblib')}")
        print(f"Report: {os.path.join(report_dir, 'analysis_report.html')}")
        return 0
    else:
        print("\n⚠️  PIPELINE COMPLETED WITH WARNINGS")
        return 1


if __name__ == '__main__':
    exit(main())
