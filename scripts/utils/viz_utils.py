#!/usr/bin/env python3
"""
UIDAI Data Hackathon 2026 - Visualization Utilities
Common visualization helpers for better, more informative plots.

Addresses review feedback:
1. Confidence intervals on trends
2. Sample size annotations
3. Population normalization options
4. Better date axis formatting
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from scipy import stats


# ============================================================================
# DATE AXIS FORMATTING
# ============================================================================
def format_date_axis(ax, date_range_days=None, rotation=45):
    """
    Apply smart date formatting to x-axis.
    
    Args:
        ax: Matplotlib axes object
        date_range_days: Approximate number of days in the data
        rotation: Rotation angle for labels (default 45)
    """
    if date_range_days is None:
        # Try to infer from axis limits
        try:
            xlim = ax.get_xlim()
            date_range_days = int(xlim[1] - xlim[0])
        except:
            date_range_days = 365  # Default to year
    
    if date_range_days <= 30:
        # Daily data for a month
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    elif date_range_days <= 90:
        # 3 months
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    elif date_range_days <= 365:
        # Up to a year
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    else:
        # Multiple years
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=rotation, ha='right')


# ============================================================================
# CONFIDENCE INTERVALS
# ============================================================================
def plot_with_confidence_interval(ax, x, y, confidence=0.95, color='blue', 
                                   label=None, alpha_fill=0.2, **kwargs):
    """
    Plot a line with confidence interval shading.
    
    For time series with repeated measurements, computes CI from data.
    For single measurements, uses moving window bootstrap.
    
    Args:
        ax: Matplotlib axes
        x: X values (dates or numeric)
        y: Y values
        confidence: Confidence level (default 0.95 for 95% CI)
        color: Line color
        label: Line label for legend
        alpha_fill: Alpha for CI shading
        **kwargs: Additional kwargs for plot()
    """
    # Sort by x
    sort_idx = np.argsort(x)
    x = np.array(x)[sort_idx]
    y = np.array(y)[sort_idx]
    
    # Plot the main line
    line, = ax.plot(x, y, color=color, label=label, **kwargs)
    
    # Calculate rolling statistics for CI
    # Using a window of 7 for daily data
    window = min(7, len(y) // 5) if len(y) > 15 else 3
    
    if window >= 3:
        y_series = pd.Series(y)
        rolling_mean = y_series.rolling(window=window, center=True, min_periods=1).mean()
        rolling_std = y_series.rolling(window=window, center=True, min_periods=1).std()
        
        # z-value for confidence level
        z = stats.norm.ppf((1 + confidence) / 2)
        
        # CI bounds (adjust for sample size)
        se = rolling_std / np.sqrt(window)
        ci_lower = rolling_mean - z * se
        ci_upper = rolling_mean + z * se
        
        # Fill between
        ax.fill_between(x, ci_lower, ci_upper, color=color, alpha=alpha_fill)
    
    return line


def add_sample_size_annotation(ax, n, position='upper right', fontsize=10):
    """
    Add sample size annotation to a plot.
    
    Args:
        ax: Matplotlib axes
        n: Sample size (int or dict of category: size)
        position: Text position ('upper right', 'upper left', etc.)
        fontsize: Font size for annotation
    """
    if isinstance(n, dict):
        text = '\n'.join([f'{k}: n={v:,}' for k, v in n.items()])
    else:
        text = f'n = {n:,}'
    
    # Position mapping
    positions = {
        'upper right': (0.98, 0.98),
        'upper left': (0.02, 0.98),
        'lower right': (0.98, 0.02),
        'lower left': (0.02, 0.02),
        'center': (0.5, 0.5),
    }
    
    x, y = positions.get(position, (0.98, 0.98))
    ha = 'right' if 'right' in position else 'left' if 'left' in position else 'center'
    va = 'top' if 'upper' in position else 'bottom' if 'lower' in position else 'center'
    
    ax.text(x, y, text, transform=ax.transAxes, fontsize=fontsize,
            ha=ha, va=va, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))


# ============================================================================
# POPULATION NORMALIZATION
# ============================================================================

# State population estimates (2024, in lakhs)
STATE_POPULATION_LAKHS = {
    'Uttar Pradesh': 2350,
    'Maharashtra': 1300,
    'Bihar': 1300,
    'West Bengal': 1000,
    'Madhya Pradesh': 870,
    'Tamil Nadu': 830,
    'Rajasthan': 820,
    'Karnataka': 710,
    'Gujarat': 720,
    'Andhra Pradesh': 530,
    'Odisha': 470,
    'Telangana': 400,
    'Kerala': 360,
    'Jharkhand': 400,
    'Assam': 360,
    'Punjab': 310,
    'Chhattisgarh': 310,
    'Haryana': 300,
    'Delhi': 210,
    'Jammu And Kashmir': 140,
    'Uttarakhand': 120,
    'Himachal Pradesh': 80,
    'Tripura': 45,
    'Meghalaya': 40,
    'Manipur': 35,
    'Nagaland': 25,
    'Goa': 20,
    'Arunachal Pradesh': 18,
    'Puducherry': 16,
    'Mizoram': 14,
    'Chandigarh': 13,
    'Sikkim': 7,
    'Andaman And Nicobar Islands': 4,
    'Dadra And Nagar Haveli And Daman And Diu': 7,
    'Ladakh': 3,
    'Lakshadweep': 0.7,
}


def normalize_by_population(df, value_col, state_col='state', per_lakh=True):
    """
    Add population-normalized column to DataFrame.
    
    Args:
        df: DataFrame with state column
        value_col: Column to normalize
        state_col: Name of state column
        per_lakh: If True, returns per lakh (100k) population
        
    Returns:
        DataFrame with new column '{value_col}_per_capita'
    """
    df = df.copy()
    new_col = f'{value_col}_per_lakh' if per_lakh else f'{value_col}_per_capita'
    
    df['_pop_lakh'] = df[state_col].map(STATE_POPULATION_LAKHS)
    
    if per_lakh:
        df[new_col] = df[value_col] / df['_pop_lakh']
    else:
        df[new_col] = df[value_col] / (df['_pop_lakh'] * 100000)
    
    df = df.drop(columns=['_pop_lakh'])
    return df


def add_per_capita_comparison(ax, df, state_col, value_col, top_n=15, color='coral'):
    """
    Create side-by-side comparison: absolute vs per-capita.
    
    Args:
        ax: Matplotlib axes (or tuple of two axes)
        df: DataFrame with state and value columns
        state_col: Name of state column
        value_col: Name of value column
        top_n: Number of top states to show
        color: Bar color
    """
    # Add per-capita column
    df = normalize_by_population(df, value_col, state_col)
    per_capita_col = f'{value_col}_per_lakh'
    
    if isinstance(ax, tuple) and len(ax) == 2:
        ax1, ax2 = ax
    else:
        # Create subplots if only one ax given
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Top by absolute
    top_abs = df.nlargest(top_n, value_col)
    ax1.barh(top_abs[state_col], top_abs[value_col], color=color)
    ax1.set_title(f'Top {top_n} by Volume', fontweight='bold')
    ax1.set_xlabel(value_col)
    
    # Top by per-capita
    df_valid = df[df[per_capita_col].notna() & (df[per_capita_col] > 0)]
    top_pc = df_valid.nlargest(top_n, per_capita_col)
    ax2.barh(top_pc[state_col], top_pc[per_capita_col], color='steelblue')
    ax2.set_title(f'Top {top_n} by Per Lakh Population', fontweight='bold')
    ax2.set_xlabel(per_capita_col)
    
    return ax1, ax2


# ============================================================================
# ENHANCED PLOT TEMPLATES
# ============================================================================
def plot_timeseries_with_enhancements(df, date_col, value_col, ax=None, 
                                       title=None, ylabel=None,
                                       add_ci=True, add_n=True,
                                       color='steelblue', **kwargs):
    """
    Plot a time series with all enhancements applied.
    
    Args:
        df: DataFrame with date and value columns
        date_col: Name of date column
        value_col: Name of value column
        ax: Matplotlib axes (creates new if None)
        title: Plot title
        ylabel: Y-axis label
        add_ci: Add confidence interval shading
        add_n: Add sample size annotation
        color: Line color
        **kwargs: Additional kwargs for plot
        
    Returns:
        Matplotlib axes
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 6))
    
    df = df.sort_values(date_col)
    x = df[date_col]
    y = df[value_col]
    
    if add_ci:
        plot_with_confidence_interval(ax, x, y, color=color, label=value_col, **kwargs)
    else:
        ax.plot(x, y, color=color, label=value_col, **kwargs)
    
    # Format date axis
    if pd.api.types.is_datetime64_any_dtype(x):
        date_range = (x.max() - x.min()).days
        format_date_axis(ax, date_range)
    
    # Add sample size
    if add_n:
        add_sample_size_annotation(ax, len(df))
    
    # Labels
    if title:
        ax.set_title(title, fontweight='bold', fontsize=12)
    if ylabel:
        ax.set_ylabel(ylabel)
    
    ax.grid(True, alpha=0.3)
    
    return ax


def plot_state_comparison_normalized(df, state_col, value_col, ax=None,
                                      top_n=15, title=None, add_n=True):
    """
    Plot state comparison with population-normalized alternative.
    
    Args:
        df: DataFrame aggregated by state
        state_col: Name of state column
        value_col: Name of value column
        ax: Matplotlib axes tuple (ax1, ax2) or creates new
        top_n: Number of states to show
        title: Overall title
        add_n: Add sample size annotations
        
    Returns:
        Tuple of (ax1, ax2)
    """
    if ax is None:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    else:
        ax1, ax2 = ax
    
    # Normalize
    df = normalize_by_population(df, value_col, state_col)
    per_capita_col = f'{value_col}_per_lakh'
    
    # Top by absolute volume
    top_abs = df.nlargest(top_n, value_col)
    ax1.barh(top_abs[state_col], top_abs[value_col], color='coral')
    ax1.set_title('By Absolute Volume', fontweight='bold')
    ax1.set_xlabel(value_col)
    
    if add_n:
        total_n = df[value_col].sum()
        add_sample_size_annotation(ax1, int(total_n), position='lower right')
    
    # Top by per-capita
    df_valid = df[df[per_capita_col].notna() & (df[per_capita_col] > 0)]
    top_pc = df_valid.nlargest(top_n, per_capita_col)
    ax2.barh(top_pc[state_col], top_pc[per_capita_col], color='steelblue')
    ax2.set_title('Per Lakh Population', fontweight='bold')
    ax2.set_xlabel(per_capita_col)
    
    if add_n:
        add_sample_size_annotation(ax2, int(total_n), position='lower right')
    
    if title:
        plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    return ax1, ax2


# ============================================================================
# PLOT STYLING
# ============================================================================
def apply_professional_style():
    """Apply professional plot styling."""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({
        'figure.figsize': (12, 8),
        'figure.dpi': 100,
        'font.size': 11,
        'axes.titlesize': 14,
        'axes.titleweight': 'bold',
        'axes.labelsize': 12,
        'legend.fontsize': 10,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
        'axes.grid': True,
        'grid.alpha': 0.3,
    })
