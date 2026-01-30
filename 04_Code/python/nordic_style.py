"""
Smart Socks - Nordic Design System
ELEC-E7840 Smart Wearables (Aalto University)

Minimalist, professional styling for all visualizations.
Nordic design principles: clean, muted colors, whitespace, functionality.
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, Circle
import numpy as np

# Nordic Color Palette
COLORS = {
    # Primary
    'nord0': '#2E3440',   # Dark gray (background)
    'nord1': '#3B4252',   # Darker gray
    'nord2': '#434C5E',   # Medium gray
    'nord3': '#4C566A',   # Light gray
    
    # Snow Storm (whites)
    'nord4': '#D8DEE9',   # Lightest
    'nord5': '#E5E9F0',   # Lighter
    'nord6': '#ECEFF4',   # White
    
    # Frost (blues)
    'nord7': '#8FBCBB',   # Teal
    'nord8': '#88C0D0',   # Light blue
    'nord9': '#81A1C1',   # Blue
    'nord10': '#5E81AC',  # Dark blue
    
    # Aurora (accents)
    'nord11': '#BF616A',  # Red
    'nord12': '#D08770',  # Orange
    'nord13': '#EBCB8B',  # Yellow
    'nord14': '#A3BE8C',  # Green
    'nord15': '#B48EAD',  # Purple
}

# Sensor Colors (Nordic palette) - auto-generated from config
# Order matches SENSORS['names']: L_P_Heel, L_P_Ball, L_S_Knee, R_P_Heel, R_P_Ball, R_S_Knee
SENSOR_COLORS = [
    COLORS['nord8'],   # L_P_Heel - Light blue
    COLORS['nord9'],   # L_P_Ball - Blue
    COLORS['nord14'],  # L_S_Knee - Green
    COLORS['nord12'],  # R_P_Heel - Orange
    COLORS['nord13'],  # R_P_Ball - Yellow
    COLORS['nord15'],  # R_S_Knee - Purple
]


def apply_nordic_style():
    """Apply Nordic design style to matplotlib."""
    plt.style.use('default')
    
    # Figure settings
    plt.rcParams['figure.facecolor'] = COLORS['nord0']
    plt.rcParams['axes.facecolor'] = COLORS['nord1']
    plt.rcParams['axes.edgecolor'] = COLORS['nord3']
    plt.rcParams['axes.labelcolor'] = COLORS['nord4']
    plt.rcParams['text.color'] = COLORS['nord4']
    
    # Grid
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.2
    plt.rcParams['grid.color'] = COLORS['nord4']
    plt.rcParams['grid.linestyle'] = '-'
    plt.rcParams['grid.linewidth'] = 0.5
    
    # Ticks
    plt.rcParams['xtick.color'] = COLORS['nord4']
    plt.rcParams['ytick.color'] = COLORS['nord4']
    plt.rcParams['xtick.labelcolor'] = COLORS['nord4']
    plt.rcParams['ytick.labelcolor'] = COLORS['nord4']
    
    # Lines
    plt.rcParams['lines.linewidth'] = 1.5
    plt.rcParams['lines.color'] = COLORS['nord8']
    
    # Font
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['axes.labelsize'] = 10
    
    # Legend
    plt.rcParams['legend.facecolor'] = COLORS['nord2']
    plt.rcParams['legend.edgecolor'] = COLORS['nord3']
    plt.rcParams['legend.labelcolor'] = COLORS['nord4']


def create_sensor_card(ax, sensor_name, value, min_val, max_val, color):
    """Create a Nordic-style sensor display card."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    # Background card
    card = FancyBboxPatch((0.05, 0.05), 0.9, 0.9,
                          boxstyle="round,pad=0.02,rounding_size=0.05",
                          facecolor=COLORS['nord1'],
                          edgecolor=COLORS['nord3'],
                          linewidth=1,
                          transform=ax.transAxes)
    ax.add_patch(card)
    
    # Sensor name
    ax.text(0.5, 0.75, sensor_name, 
            ha='center', va='center',
            fontsize=11, fontweight='bold',
            color=COLORS['nord4'],
            transform=ax.transAxes)
    
    # Value
    value_color = COLORS['nord6'] if value > 2000 else color
    ax.text(0.5, 0.45, str(int(value)), 
            ha='center', va='center',
            fontsize=24, fontweight='bold',
            color=value_color,
            transform=ax.transAxes,
            family='monospace')
    
    # Min/Max
    range_text = f"{int(min_val)} – {int(max_val)}"
    ax.text(0.5, 0.18, range_text, 
            ha='center', va='center',
            fontsize=8,
            color=COLORS['nord3'],
            transform=ax.transAxes)
    
    # Progress bar background
    bar_bg = FancyBboxPatch((0.1, 0.05), 0.8, 0.04,
                            boxstyle="round,pad=0.005,rounding_size=0.02",
                            facecolor=COLORS['nord0'],
                            edgecolor='none',
                            transform=ax.transAxes)
    ax.add_patch(bar_bg)
    
    # Progress bar fill
    progress = (value - min_val) / (max_val - min_val + 1) if max_val > min_val else 0
    bar_fill = FancyBboxPatch((0.1, 0.05), 0.8 * progress, 0.04,
                              boxstyle="round,pad=0.005,rounding_size=0.02",
                              facecolor=color,
                              edgecolor='none',
                              transform=ax.transAxes)
    ax.add_patch(bar_fill)


def create_header(ax, title, subtitle=""):
    """Create a Nordic-style header."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    # Title
    ax.text(0.5, 0.6, title, 
            ha='center', va='center',
            fontsize=16, fontweight='bold',
            color=COLORS['nord6'],
            transform=ax.transAxes)
    
    # Subtitle
    if subtitle:
        ax.text(0.5, 0.25, subtitle, 
                ha='center', va='center',
                fontsize=10,
                color=COLORS['nord3'],
                transform=ax.transAxes)
    
    # Decorative line
    ax.plot([0.2, 0.8], [0.05, 0.05], 
            color=COLORS['nord8'], linewidth=2,
            transform=ax.transAxes)


def create_status_bar(ax, status_text, is_recording=False):
    """Create a Nordic-style status bar."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    # Background
    bg = FancyBboxPatch((0, 0), 1, 1,
                        facecolor=COLORS['nord2'] if not is_recording else COLORS['nord11'],
                        edgecolor='none',
                        transform=ax.transAxes)
    ax.add_patch(bg)
    
    # Status text
    ax.text(0.5, 0.5, status_text, 
            ha='center', va='center',
            fontsize=9,
            color=COLORS['nord6'],
            transform=ax.transAxes,
            family='monospace')
    
    # Recording indicator
    if is_recording:
        circle = Circle((0.05, 0.5), 0.15, 
                        facecolor=COLORS['nord6'],
                        edgecolor='none',
                        transform=ax.transAxes)
        ax.add_patch(circle)


# Apply style on import
apply_nordic_style()
