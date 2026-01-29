#!/usr/bin/env python3
"""
Smart Socks - Analysis Report Generator
ELEC-E7840 Smart Wearables (Aalto University)

Generates comprehensive analysis reports including:
- Confusion matrices
- Per-activity accuracy breakdown
- Cross-subject performance analysis
- Feature importance analysis
- Step counting accuracy

Usage:
    python analysis_report.py --results-dir ../05_Analysis/ --output ../06_Presentation/
"""

import argparse
import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime


def load_results(results_dir):
    """Load all result files from the analysis directory."""
    results = {}
    
    # Load classification report
    report_path = os.path.join(results_dir, 'classification_report.txt')
    if os.path.exists(report_path):
        with open(report_path, 'r') as f:
            results['classification_report'] = f.read()
    
    # Load confusion matrix
    cm_path = os.path.join(results_dir, 'confusion_matrix.png')
    results['confusion_matrix_path'] = cm_path if os.path.exists(cm_path) else None
    
    # Load feature importance
    fi_path = os.path.join(results_dir, 'feature_importance.csv')
    if os.path.exists(fi_path):
        results['feature_importance'] = pd.read_csv(fi_path)
    
    # Load cross-subject results
    cs_path = os.path.join(results_dir, 'cross_subject_results.csv')
    if os.path.exists(cs_path):
        results['cross_subject'] = pd.read_csv(cs_path)
    
    return results


def generate_summary_statistics(results, output_dir):
    """Generate summary statistics table."""
    summary_data = []
    
    # Parse classification report for per-class metrics
    if 'classification_report' in results:
        lines = results['classification_report'].split('\n')
        for line in lines:
            if any(activity in line for activity in [
                'walking', 'stairs', 'sitting', 'stand', 'accuracy'
            ]):
                parts = line.split()
                if len(parts) >= 4 and parts[0] not in ['accuracy', 'macro', 'weighted']:
                    activity = parts[0]
                    precision = float(parts[1])
                    recall = float(parts[2])
                    f1 = float(parts[3])
                    support = int(parts[4]) if len(parts) > 4 else 0
                    summary_data.append({
                        'Activity': activity,
                        'Precision': f"{precision:.3f}",
                        'Recall': f"{recall:.3f}",
                        'F1-Score': f"{f1:.3f}",
                        'Support': support
                    })
    
    if summary_data:
        df = pd.DataFrame(summary_data)
        
        # Save as CSV
        csv_path = os.path.join(output_dir, 'summary_statistics.csv')
        df.to_csv(csv_path, index=False)
        
        # Create formatted table plot
        fig, ax = plt.subplots(figsize=(12, max(4, len(summary_data) * 0.4)))
        ax.axis('tight')
        ax.axis('off')
        
        table = ax.table(
            cellText=df.values,
            colLabels=df.columns,
            cellLoc='center',
            loc='center',
            colWidths=[0.3, 0.15, 0.15, 0.15, 0.15]
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Color header
        for i in range(len(df.columns)):
            table[(0, i)].set_facecolor('#4CAF50')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Color alternating rows
        for i in range(1, len(df) + 1):
            for j in range(len(df.columns)):
                if i % 2 == 0:
                    table[(i, j)].set_facecolor('#f0f0f0')
        
        plt.title('Per-Activity Performance Summary', fontsize=14, fontweight='bold', pad=20)
        plt.savefig(os.path.join(output_dir, 'summary_table.png'), dpi=150, bbox_inches='tight')
        plt.close()
        
        return df
    
    return None


def plot_cross_subject_analysis(cross_subject_df, output_dir):
    """Create cross-subject performance visualization."""
    if cross_subject_df is None or len(cross_subject_df) == 0:
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Bar plot
    ax1 = axes[0]
    colors = ['#4CAF50' if a >= 0.8 else '#FFC107' if a >= 0.7 else '#F44336' 
              for a in cross_subject_df['accuracy']]
    bars = ax1.bar(cross_subject_df['subject'], cross_subject_df['accuracy'], color=colors)
    ax1.axhline(y=0.8, color='red', linestyle='--', label='Target (80%)')
    ax1.axhline(y=cross_subject_df['accuracy'].mean(), color='blue', linestyle='--', 
                label=f'Mean: {cross_subject_df["accuracy"].mean():.3f}')
    ax1.set_xlabel('Subject')
    ax1.set_ylabel('Accuracy')
    ax1.set_title('Cross-Subject Validation Accuracy')
    ax1.set_ylim([0, 1])
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}', ha='center', va='bottom', fontsize=9)
    
    # Distribution histogram
    ax2 = axes[1]
    ax2.hist(cross_subject_df['accuracy'], bins=10, edgecolor='black', alpha=0.7)
    ax2.axvline(x=0.8, color='red', linestyle='--', label='Target (80%)')
    ax2.axvline(x=cross_subject_df['accuracy'].mean(), color='blue', linestyle='--',
                label=f'Mean: {cross_subject_df["accuracy"].mean():.3f}')
    ax2.set_xlabel('Accuracy')
    ax2.set_ylabel('Number of Subjects')
    ax2.set_title('Accuracy Distribution Across Subjects')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'cross_subject_analysis.png'), dpi=150)
    plt.close()


def plot_feature_importance_detailed(fi_df, output_dir, top_n=30):
    """Create detailed feature importance visualization."""
    if fi_df is None or len(fi_df) == 0:
        return
    
    # Get top N features
    top_features = fi_df.head(top_n)
    
    # Group by sensor
    sensor_importance = {}
    for _, row in fi_df.iterrows():
        feature = row['feature']
        importance = row['importance']
        
        # Extract sensor name from feature
        sensor = None
        for s in ['L_Heel', 'L_Arch', 'L_MetaM', 'L_MetaL', 'L_Toe',
                  'R_Heel', 'R_Arch', 'R_MetaM', 'R_MetaL', 'R_Toe']:
            if feature.startswith(s):
                sensor = s
                break
        
        if sensor:
            sensor_importance[sensor] = sensor_importance.get(sensor, 0) + importance
    
    # Create subplots
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    # Top features bar chart
    ax1 = axes[0]
    y_pos = np.arange(len(top_features))
    ax1.barh(y_pos, top_features['importance'].values, align='center')
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(top_features['feature'].values, fontsize=8)
    ax1.invert_yaxis()
    ax1.set_xlabel('Importance')
    ax1.set_title(f'Top {top_n} Feature Importances')
    ax1.grid(True, alpha=0.3, axis='x')
    
    # Sensor importance pie chart
    ax2 = axes[1]
    if sensor_importance:
        sensors = list(sensor_importance.keys())
        importances = list(sensor_importance.values())
        colors = plt.cm.Set3(np.linspace(0, 1, len(sensors)))
        
        wedges, texts, autotexts = ax2.pie(
            importances, labels=sensors, autopct='%1.1f%%',
            colors=colors, startangle=90
        )
        ax2.set_title('Importance by Sensor Zone')
        
        # Make percentage text smaller
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(8)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'feature_importance_detailed.png'), dpi=150)
    plt.close()


def generate_step_counting_analysis(output_dir, step_results=None):
    """Generate step counting accuracy analysis.
    
    Args:
        output_dir: Directory to save output files
        step_results: Optional dict with actual step counting results.
                     If None, generates a placeholder report with warnings.
    """
    if step_results is None:
        # PLACEHOLDER DATA - Replace with actual step counting results
        print("WARNING: Using placeholder step counting data!")
        print("         Pass actual step_results to generate_step_counting_analysis()")
        step_data = {
            'Activity': ['walking_forward', 'walking_backward', 'stairs_up', 'stairs_down'],
            'True_Steps': [0, 0, 0, 0],
            'Detected_Steps': [0, 0, 0, 0],
            'Error': [0, 0, 0, 0],
            'Error_Percentage': [0.0, 0.0, 0.0, 0.0],
            'Note': ['PLACEHOLDER', 'PLACEHOLDER', 'PLACEHOLDER', 'PLACEHOLDER']
        }
    else:
        step_data = step_results
    
    df = pd.DataFrame(step_data)
    csv_path = os.path.join(output_dir, 'step_counting_accuracy.csv')
    df.to_csv(csv_path, index=False)
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(df))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, df['True_Steps'], width, label='True Steps', color='#4CAF50')
    bars2 = ax.bar(x + width/2, df['Detected_Steps'], width, label='Detected Steps', color='#2196F3')
    
    ax.set_xlabel('Activity')
    ax.set_ylabel('Step Count')
    ax.set_title('Step Counting Accuracy')
    ax.set_xticks(x)
    ax.set_xticklabels(df['Activity'], rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add error percentage as text
    for i, (bar, error) in enumerate(zip(bars2, df['Error_Percentage'])):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{error:+.1f}%', ha='center', va='bottom', fontsize=9,
                color='red' if abs(error) > 5 else 'green')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'step_counting_analysis.png'), dpi=150)
    plt.close()
    
    return df


def generate_html_report(results, output_dir):
    """Generate an HTML report with all results."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart Socks - Analysis Report</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            h1 {
                color: #333;
                border-bottom: 3px solid #4CAF50;
                padding-bottom: 10px;
            }
            h2 {
                color: #555;
                margin-top: 30px;
                border-bottom: 2px solid #ddd;
                padding-bottom: 5px;
            }
            .section {
                background: white;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .metric {
                display: inline-block;
                margin: 10px 20px 10px 0;
                padding: 15px;
                background: #e8f5e9;
                border-radius: 8px;
                min-width: 150px;
            }
            .metric-label {
                font-size: 12px;
                color: #666;
                text-transform: uppercase;
            }
            .metric-value {
                font-size: 24px;
                font-weight: bold;
                color: #4CAF50;
            }
            img {
                max-width: 100%;
                height: auto;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin: 10px 0;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #4CAF50;
                color: white;
            }
            tr:hover {
                background-color: #f5f5f5;
            }
            .footer {
                text-align: center;
                color: #999;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
            }
        </style>
    </head>
    <body>
        <h1>Smart Socks - Activity Recognition Analysis Report</h1>
        <p>Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        
        <div class="section">
            <h2>Executive Summary</h2>
    """
    
    # Add summary metrics if available
    if 'cross_subject' in results and results['cross_subject'] is not None:
        mean_acc = results['cross_subject']['accuracy'].mean()
        html += f"""
            <div class="metric">
                <div class="metric-label">Mean Accuracy</div>
                <div class="metric-value">{mean_acc:.1%}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Subjects Tested</div>
                <div class="metric-value">{len(results['cross_subject'])}</div>
            </div>
        """
    
    html += """
        </div>
        
        <div class="section">
            <h2>Confusion Matrix</h2>
    """
    
    if results.get('confusion_matrix_path'):
        # Copy confusion matrix to output dir if needed
        html += f'<img src="confusion_matrix.png" alt="Confusion Matrix">'
    else:
        html += '<p>Confusion matrix not available.</p>'
    
    html += """
        </div>
        
        <div class="section">
            <h2>Cross-Subject Performance</h2>
    """
    
    if 'cross_subject' in results and results['cross_subject'] is not None:
        html += '<img src="cross_subject_analysis.png" alt="Cross-Subject Analysis">'
        
        # Add table
        html += '<table><tr><th>Subject</th><th>Accuracy</th></tr>'
        for _, row in results['cross_subject'].iterrows():
            html += f'<tr><td>{row["subject"]}</td><td>{row["accuracy"]:.3f}</td></tr>'
        html += '</table>'
    else:
        html += '<p>Cross-subject analysis not available.</p>'
    
    html += """
        </div>
        
        <div class="section">
            <h2>Feature Importance</h2>
    """
    
    if 'feature_importance' in results and results['feature_importance'] is not None:
        html += '<img src="feature_importance_detailed.png" alt="Feature Importance">'
    else:
        html += '<p>Feature importance analysis not available.</p>'
    
    html += """
        </div>
        
        <div class="section">
            <h2>Classification Report</h2>
            <pre>"""
    
    if 'classification_report' in results:
        html += results['classification_report']
    else:
        html += 'Classification report not available.'
    
    html += """</pre>
        </div>
        
        <div class="footer">
            <p>Smart Socks Project - ELEC-E7840 Smart Wearables (Aalto University)</p>
        </div>
    </body>
    </html>
    """
    
    html_path = os.path.join(output_dir, 'analysis_report.html')
    with open(html_path, 'w') as f:
        f.write(html)
    
    return html_path


def main():
    parser = argparse.ArgumentParser(
        description='Smart Socks Analysis Report Generator'
    )
    parser.add_argument(
        '--results-dir', '-r',
        required=True,
        help='Directory containing analysis results'
    )
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output directory for generated reports'
    )

    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    print("Loading results...")
    results = load_results(args.results_dir)
    
    print("Generating summary statistics...")
    summary_df = generate_summary_statistics(results, args.output)
    
    print("Generating cross-subject analysis...")
    plot_cross_subject_analysis(results.get('cross_subject'), args.output)
    
    print("Generating feature importance analysis...")
    plot_feature_importance_detailed(results.get('feature_importance'), args.output)
    
    print("Generating step counting analysis...")
    generate_step_counting_analysis(args.output)
    
    print("Generating HTML report...")
    html_path = generate_html_report(results, args.output)
    
    print("\n" + "="*60)
    print("Report Generation Complete!")
    print("="*60)
    print(f"\nGenerated files in {args.output}:")
    for f in os.listdir(args.output):
        if f.endswith(('.png', '.csv', '.html')):
            print(f"  - {f}")
    print(f"\nOpen {html_path} in a browser to view the full report.")
    
    return 0


if __name__ == '__main__':
    exit(main())
