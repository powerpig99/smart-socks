#!/usr/bin/env python3
"""
Smart Socks - Model Manager
ELEC-E7840 Smart Wearables (Aalto University)

Utilities for managing trained models: versioning, comparison, and deployment.

Usage:
    python model_manager.py --list
    python model_manager.py --compare
    python model_manager.py --deploy ../../05_Analysis/smart_socks_model.joblib
    python model_manager.py --cleanup --keep 5
"""

import argparse
import json
import shutil
import sys
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from tabulate import tabulate
import matplotlib.pyplot as plt

from config import MODEL, PATHS


class ModelManager:
    """Manage trained models with versioning and comparison."""
    
    def __init__(self, models_dir=None):
        self.models_dir = Path(models_dir or PATHS['models'])
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.registry_file = self.models_dir / "model_registry.json"
        self.registry = self._load_registry()
    
    def _load_registry(self):
        """Load model registry."""
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                return json.load(f)
        return {'models': [], 'active_model': None}
    
    def _save_registry(self):
        """Save model registry."""
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def _get_model_info(self, model_path):
        """Extract model information."""
        path = Path(model_path)
        
        info = {
            'path': str(path.absolute()),
            'filename': path.name,
            'created': datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            'size_mb': round(path.stat().st_size / (1024 * 1024), 2),
        }
        
        # Try to load metadata
        metadata_path = path.parent / (path.stem + '_metadata.joblib')
        if metadata_path.exists():
            try:
                metadata = joblib.load(metadata_path)
                info['classes'] = metadata.get('classes', [])
                info['n_features'] = len(metadata.get('feature_names', []))
            except:
                pass
        
        # Try to load evaluation results
        eval_path = path.parent / 'classification_report.txt'
        if eval_path.exists():
            try:
                with open(eval_path, 'r') as f:
                    content = f.read()
                    # Parse accuracy from report
                    if 'accuracy' in content.lower():
                        lines = content.split('\n')
                        for line in lines:
                            if 'accuracy' in line.lower():
                                try:
                                    # Handle both percentage (84.56%) and decimal (0.8456) formats
                                    if '%' in line:
                                        acc = float(line.split('%')[0].split()[-1])
                                        info['accuracy'] = acc / 100
                                    else:
                                        # Try to extract decimal accuracy (sklearn default format)
                                        parts = line.split()
                                        for part in parts:
                                            try:
                                                val = float(part)
                                                if 0 <= val <= 1:
                                                    info['accuracy'] = val
                                                    break
                                            except:
                                                continue
                                    break
                                except:
                                    pass
            except:
                pass
        
        return info
    
    def register_model(self, model_path):
        """
        Register a new model.
        
        Args:
            model_path: Path to model file
            
        Returns:
            Model info dictionary
        """
        path = Path(model_path)
        if not path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        # Get model info
        info = self._get_model_info(model_path)
        
        # Generate version name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        acc_str = f"{info.get('accuracy', 0):.3f}"
        version_name = f"model_v{timestamp}_acc{acc_str}"
        
        # Copy to models directory
        dest_path = self.models_dir / f"{version_name}.joblib"
        shutil.copy2(model_path, dest_path)
        
        # Copy associated files
        for suffix in ['_scaler.joblib', '_metadata.joblib']:
            src = path.parent / (path.stem + suffix)
            if src.exists():
                dst = self.models_dir / (version_name + suffix)
                shutil.copy2(src, dst)
        
        # Update info
        info['version'] = version_name
        info['path'] = str(dest_path)
        info['filename'] = dest_path.name
        
        # Add to registry
        self.registry['models'].append(info)
        self._save_registry()
        
        print(f"Registered model: {version_name}")
        return info
    
    def list_models(self):
        """List all registered models."""
        if not self.registry['models']:
            print("No models registered")
            return []
        
        # Sort by accuracy (descending)
        models = sorted(
            self.registry['models'],
            key=lambda x: x.get('accuracy', 0),
            reverse=True
        )
        
        # Prepare table
        table_data = []
        for i, model in enumerate(models, 1):
            row = [
                i,
                model.get('version', 'unknown')[:30],
                f"{model.get('accuracy', 0):.3f}",
                model.get('n_features', '-'),
                len(model.get('classes', [])),
                model.get('size_mb', 0),
                model.get('created', '')[:10],
                '★' if model.get('version') == self.registry.get('active_model') else ''
            ]
            table_data.append(row)
        
        headers = ['#', 'Version', 'Accuracy', 'Features', 'Classes', 'Size (MB)', 'Created', 'Active']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        
        return models
    
    def compare_models(self, model_versions=None):
        """
        Compare multiple models.
        
        Args:
            model_versions: List of model versions to compare (None = all)
        """
        models = self.registry['models']
        
        if model_versions:
            models = [m for m in models if m.get('version') in model_versions]
        
        if len(models) < 2:
            print("Need at least 2 models to compare")
            return
        
        # Sort by accuracy
        models = sorted(models, key=lambda x: x.get('accuracy', 0), reverse=True)
        
        print("\nModel Comparison")
        print("=" * 70)
        
        for i, model in enumerate(models, 1):
            print(f"\n{i}. {model.get('version')}")
            print(f"   Accuracy: {model.get('accuracy', 0):.3f}")
            print(f"   Features: {model.get('n_features', '-')}")
            print(f"   Classes: {', '.join(model.get('classes', []))}")
            print(f"   Size: {model.get('size_mb', 0)} MB")
            print(f"   Created: {model.get('created', '')}")
        
        # Plot comparison
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # Accuracy comparison
        versions = [m.get('version', 'unknown')[:20] for m in models]
        accuracies = [m.get('accuracy', 0) for m in models]
        
        axes[0].barh(versions, accuracies)
        axes[0].set_xlabel('Accuracy')
        axes[0].set_title('Model Accuracy Comparison')
        axes[0].set_xlim(0, 1)
        axes[0].invert_yaxis()
        
        # Model size
        sizes = [m.get('size_mb', 0) for m in models]
        axes[1].barh(versions, sizes, color='orange')
        axes[1].set_xlabel('Size (MB)')
        axes[1].set_title('Model Size Comparison')
        axes[1].invert_yaxis()
        
        plt.tight_layout()
        plt.savefig(self.models_dir / 'model_comparison.png', dpi=150)
        print(f"\nComparison plot saved to: {self.models_dir / 'model_comparison.png'}")
        plt.close()
    
    def set_active_model(self, version):
        """
        Set the active model for deployment.
        
        Args:
            version: Model version name
        """
        model = next(
            (m for m in self.registry['models'] if m.get('version') == version),
            None
        )
        
        if model is None:
            print(f"Model not found: {version}")
            return False
        
        self.registry['active_model'] = version
        self._save_registry()
        
        print(f"Active model set to: {version}")
        return True
    
    def get_active_model_path(self):
        """Get path to active model."""
        if self.registry.get('active_model'):
            model = next(
                (m for m in self.registry['models'] 
                 if m.get('version') == self.registry['active_model']),
                None
            )
            if model:
                return model['path']
        
        # Return most accurate model
        if self.registry['models']:
            best = max(self.registry['models'], key=lambda x: x.get('accuracy', 0))
            return best['path']
        
        return None
    
    def cleanup_old_models(self, keep_n=5):
        """
        Remove old models, keeping only the top N by accuracy.
        
        Args:
            keep_n: Number of models to keep
        """
        models = self.registry['models']
        
        if len(models) <= keep_n:
            print(f"Only {len(models)} models, nothing to clean")
            return
        
        # Sort by accuracy
        models_sorted = sorted(
            models,
            key=lambda x: x.get('accuracy', 0),
            reverse=True
        )
        
        # Keep top N
        to_keep = models_sorted[:keep_n]
        to_remove = models_sorted[keep_n:]
        
        print(f"Keeping top {keep_n} models, removing {len(to_remove)} old models")
        
        for model in to_remove:
            version = model.get('version')
            
            # Remove files
            path = Path(model['path'])
            if path.exists():
                path.unlink()
            
            for suffix in ['_scaler.joblib', '_metadata.joblib']:
                file = path.parent / (version + suffix)
                if file.exists():
                    file.unlink()
            
            print(f"  Removed: {version}")
        
        # Update registry
        self.registry['models'] = to_keep
        self._save_registry()
        
        print("Cleanup complete")
    
    def export_model(self, version, export_dir):
        """
        Export model for deployment.
        
        Args:
            version: Model version to export
            export_dir: Directory to export to
        """
        model = next(
            (m for m in self.registry['models'] if m.get('version') == version),
            None
        )
        
        if model is None:
            print(f"Model not found: {version}")
            return
        
        export_path = Path(export_dir)
        export_path.mkdir(parents=True, exist_ok=True)
        
        # Copy files
        src_path = Path(model['path'])
        for suffix in ['.joblib', '_scaler.joblib', '_metadata.joblib']:
            src = src_path.parent / (model['version'] + suffix)
            if src.exists():
                dst = export_path / f"smart_socks_model{suffix}"
                shutil.copy2(src, dst)
        
        # Create info file
        info = {
            'version': version,
            'exported': datetime.now().isoformat(),
            'accuracy': model.get('accuracy'),
            'classes': model.get('classes'),
        }
        
        with open(export_path / 'model_info.json', 'w') as f:
            json.dump(info, f, indent=2)
        
        print(f"Model exported to: {export_path}")


def main():
    parser = argparse.ArgumentParser(description='Smart Socks Model Manager')
    parser.add_argument('--models-dir', default=PATHS['models'],
                       help='Directory containing models')
    
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # List command
    subparsers.add_parser('list', help='List all models')
    
    # Register command
    register_parser = subparsers.add_parser('register', help='Register a new model')
    register_parser.add_argument('model_path', help='Path to model file')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare models')
    compare_parser.add_argument('--versions', nargs='+', help='Specific versions to compare')
    
    # Set-active command
    active_parser = subparsers.add_parser('set-active', help='Set active model')
    active_parser.add_argument('version', help='Model version')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Remove old models')
    cleanup_parser.add_argument('--keep', type=int, default=5, help='Number of models to keep')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export model for deployment')
    export_parser.add_argument('version', help='Model version')
    export_parser.add_argument('--dir', default='./deploy', help='Export directory')
    
    # Get-active command
    subparsers.add_parser('get-active', help='Get path to active model')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    manager = ModelManager(args.models_dir)
    
    if args.command == 'list':
        manager.list_models()
    
    elif args.command == 'register':
        manager.register_model(args.model_path)
    
    elif args.command == 'compare':
        manager.compare_models(args.versions)
    
    elif args.command == 'set-active':
        manager.set_active_model(args.version)
    
    elif args.command == 'cleanup':
        manager.cleanup_old_models(args.keep)
    
    elif args.command == 'export':
        manager.export_model(args.version, args.dir)
    
    elif args.command == 'get-active':
        path = manager.get_active_model_path()
        if path:
            print(path)
        else:
            print("No active model found")
            return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
