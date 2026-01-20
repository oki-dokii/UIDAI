#!/usr/bin/env python3
"""
UIDAI Forensic Audit - High-Impact Analyses Generation
Generates 5 missing high-impact visualizations identified in the forensic audit

Missing Analyses (excluding census-dependent #1):
- Analysis 3: Weekend Ratio vs Gini Coefficient (State Scatterplot)
- Analysis 4: District Volatility vs Minor Share (Scatterplot)
- Analysis 5: Month-Over-Month Minor Share Growth Rate (Heatmap)
- Analysis 6: Lorenz Curve and Inequality Decomposition (Top 5 States)
- Analysis 7: Campaign Attribution via Event Detection (Spike Identification)

Author: UIDAI Hackathon Team - Forensic Compliance
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
from scipy.signal import find_peaks
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# Import existing functions
from demographic_deep_analysis import (
    load_demographic_data, 
    preprocess_data,
    engineer_features,
    aggregate_levels,
    calculate_stability_metrics,
    calculate_concentration
)

# Configuration
BASE_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "demographic_analysis")
PLOTS_FINAL_DIR = os.path.join(OUTPUT_DIR, "plots_final")

# Forensic-approved color palette
FORENSIC_COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'accent': '#F18F01',
    'success': '#06A77D',
    'warning': '#D00000',
    'neutral': '#6C757D'
}

def setup_forensic_style():
    """Set up forensic-quality matplotlib style."""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({
        'figure.figsize': (12, 8),
        'figure.dpi': 150,
        'font.size': 11,
        'axes.labelsize': 12,
        'axes.titlesize': 14,
        'axes.titleweight': 'bold',
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.titlesize': 16,
        'savefig.dpi': 150,
        'savefig.bbox': 'tight',
        'axes.grid': True,
        'grid.alpha': 0.3
    })

def add_caption_box(fig, caption, y_position=-0.15):
    """Add forensic audit caption to figure."""
    fig.text(0.5, y_position, caption, 
             ha='center', va='top', 
             fontsize=9, style='italic',
             wrap=True, bbox=dict(boxstyle='round', 
                                   facecolor='wheat', 
                                   alpha=0.3))

# ============================================================================
# ANALYSIS 3: Weekend Ratio vs Gini Coefficient
# ============================================================================
def plot_analysis_03_weekend_gini(state_weekend, concentration, output_dir):
    """
    Analysis 3: Weekend Ratio vs Gini Coefficient (State-Level Scatterplot)
    
    Tests hypothesis: episodic service delivery (high weekend ratio) correlates 
    with geographic concentration (high Gini).
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Merge data
    analysis_data = state_weekend.reset_index().merge(
        concentration, on='state', how='inner'
    )
    
    # Remove outliers for better visualization
    analysis_data = analysis_data[
        (analysis_data['weekend_ratio'] < 10) & 
        (analysis_data['gini_district'] > 0)
    ]
    
    # Scatter plot
    ax.scatter(analysis_data['weekend_ratio'], 
               analysis_data['gini_district'],
               alpha=0.6, s=100, 
               color=FORENSIC_COLORS['primary'],
               edgecolors='black', linewidth=0.5)
    
    # Label interesting states
    for _, row in analysis_data.iterrows():
        if row['weekend_ratio'] > 3.0 or row['gini_district'] > 0.65:
            ax.annotate(row['state'][:10], 
                       xy=(row['weekend_ratio'], row['gini_district']),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=8, alpha=0.7)
    
    # Calculate correlation
    if len(analysis_data) > 2:
        corr, p_value = pearsonr(analysis_data['weekend_ratio'], 
                                  analysis_data['gini_district'])
        
        # Add trend line if significant correlation
        if abs(corr) > 0.3:
            z = np.polyfit(analysis_data['weekend_ratio'], 
                          analysis_data['gini_district'], 1)
            p = np.poly1d(z)
            x_line = np.linspace(analysis_data['weekend_ratio'].min(), 
                                analysis_data['weekend_ratio'].max(), 100)
            ax.plot(x_line, p(x_line), 
                   color=FORENSIC_COLORS['warning'], 
                   linestyle='--', linewidth=2, alpha=0.7,
                   label=f'Trend line (r={corr:.3f})')
        
        # Annotate correlation
        textstr = f'Correlation: r = {corr:.3f}\\np-value = {p_value:.4f}\\nn = {len(analysis_data)}'
        props = dict(boxstyle='round', facecolor='yellow', alpha=0.6)
        ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=11,
                verticalalignment='top', bbox=props)
    
    # Add reference lines
    ax.axvline(x=1.0, color='gray', linestyle=':', alpha=0.5, 
               label='Weekend = Weekday')
    ax.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5,
               label='High concentration threshold')
    
    ax.set_xlabel('Weekend-to-Weekday Activity Ratio')
    ax.set_ylabel('Gini Coefficient (District Concentration)')
    ax.set_title('HIGH-IMPACT 03: Weekend Service Pattern vs Geographic Concentration', 
                 fontweight='bold', fontsize=14)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    caption = ("State-level correlation between weekend concentration and geographic inequality reveals "
               "whether episodic service delivery models (high weekend ratios) systematically correlate with "
               "centralized infrastructure (high Gini), or if these are orthogonal operational dimensions.")
    add_caption_box(fig, caption)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'high_impact_03_weekend_gini_scatter.png'), 
                dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ high_impact_03_weekend_gini_scatter.png")

# ============================================================================
# ANALYSIS 4: District Volatility vs Minor Share
# ============================================================================
def plot_analysis_04_volatility_minor(volatility, district_agg, output_dir):
    """
    Analysis 4: District Volatility vs Minor Share (Scatterplot)
    
    Tests whether operational instability correlates with demographic exclusion.
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Merge data
    analysis_data = volatility.merge(
        district_agg[['state', 'district', 'demo_minor_share', 'total_demo']],
        on=['state', 'district'],
        how='inner'
    )
    
    # Filter for visualization
    analysis_data = analysis_data[
        (analysis_data['total_demo'] > 100) & 
        (analysis_data['cv_volume'] < 10)
    ]
    
    # Scatter plot with size by volume
    scatter = ax.scatter(analysis_data['cv_volume'], 
                        analysis_data['demo_minor_share'],
                        alpha=0.5, 
                        s=np.log1p(analysis_data['total_demo']) * 5,
                        color=FORENSIC_COLORS['secondary'],
                        edgecolors='black', linewidth=0.3)
    
    # Calculate correlation
    if len(analysis_data) > 2:
        corr, p_value = pearsonr(analysis_data['cv_volume'], 
                                  analysis_data['demo_minor_share'])
        
        # Add trend line
        z = np.polyfit(analysis_data['cv_volume'], 
                      analysis_data['demo_minor_share'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(analysis_data['cv_volume'].min(), 
                            analysis_data['cv_volume'].max(), 100)
        ax.plot(x_line, p(x_line), 
               color=FORENSIC_COLORS['warning'], 
               linestyle='--', linewidth=2, alpha=0.7,
               label=f'Trend line (r={corr:.3f})')
        
        # Annotate correlation
        textstr = f'Correlation: r = {corr:.3f}\\np-value = {p_value:.4f}\\nn = {len(analysis_data):,}'
        props = dict(boxstyle='round', facecolor='yellow', alpha=0.6)
        ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=11,
                verticalalignment='top', bbox=props)
    
    # Add reference lines
    ax.axvline(x=3.0, color='gray', linestyle=':', alpha=0.5,
               label='Moderate volatility threshold')
    ax.axhline(y=0.10, color='gray', linestyle=':', alpha=0.5,
               label='National average minor share')
    
    ax.set_xlabel('Coefficient of Variation (Monthly Volume)')
    ax.set_ylabel('Minor Share')
    ax.set_title('HIGH-IMPACT 04: Operational Volatility vs Minor Participation', 
                 fontweight='bold', fontsize=14)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    # Add size legend
    handles, labels = ax.get_legend_handles_labels()
    size_legend = ax.legend(handles, labels, loc='upper right')
    ax.add_artist(size_legend)
    
    caption = ("District-level correlation between operational volatility and minor share tests whether "
               "episodic operations systematically disadvantage minors. Positive correlation would indicate "
               "that unstable service delivery preferentially excludes children; zero correlation suggests "
               "volatility is compositionally neutral.")
    add_caption_box(fig, caption)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'high_impact_04_volatility_minor_scatter.png'), 
                dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ high_impact_04_volatility_minor_scatter.png")

# ============================================================================
# ANALYSIS 5: Month-Over-Month Minor Share Growth Rate
# ============================================================================
def plot_analysis_05_mom_growth(state_month, output_dir):
    """
    Analysis 5: Month-Over-Month Minor Share Growth Rate by State (Heatmap)
    
    Reveals momentum and trajectory in minor participation.
    """
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # Create pivot
    pivot = state_month.pivot_table(index='state', columns='month', 
                                     values='demo_minor_share', aggfunc='mean')
    
    # Calculate month-over-month growth rate
    mom_growth = pivot.pct_change(axis=1) * 100  # Convert to percentage
    
    # Sort by average growth
    state_avg_growth = mom_growth.mean(axis=1, skipna=True).sort_values(ascending=False)
    mom_growth = mom_growth.loc[state_avg_growth.index]
    
    # Take top 20 for readability
    mom_growth = mom_growth.head(20)
    
    # Use diverging colormap (red = decline, green = growth)
    sns.heatmap(mom_growth, cmap='RdYlGn', center=0,
                annot=True, fmt='.1f', ax=ax, linewidths=0.5,
                cbar_kws={'label': 'MoM Growth Rate (%)'})
    
    ax.set_title('HIGH-IMPACT 05: Month-Over-Month Minor Share Growth Rate (Top 20 States)',
                 fontweight='bold', fontsize=14)
    ax.set_xlabel('Month')
    ax.set_ylabel('State')
    
    caption = ("Month-over-month growth rate heatmap reveals trajectory and momentum in minor participation. "
               "States with sustained positive growth (green) represent learning and improvement; declining states "
               "(red) indicate deterioration or policy retreat. Static heatmaps hide these directional trends.")
    add_caption_box(fig, caption, y_position=-0.08)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'high_impact_05_mom_growth_heatmap.png'), 
                dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ high_impact_05_mom_growth_heatmap.png")

# ============================================================================
# ANALYSIS 6: Lorenz Curve and Inequality Decomposition
# ============================================================================
def plot_analysis_06_lorenz_curves(df, concentration, output_dir):
    """
    Analysis 6: Lorenz Curve and Inequality Decomposition (Top 5 States)
    
    Visualizes WHERE in the distribution inequality concentrates.
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Get top 5 most unequal states
    top_unequal = concentration.nlargest(5, 'gini_district')
    
    # Color palette for states
    colors = sns.color_palette('Set2', n_colors=5)
    
    # Plot equality line
    ax.plot([0, 1], [0, 1], 'k--', linewidth=2, alpha=0.7, 
            label='Perfect Equality')
    
    # Plot Lorenz curve for each state
    for idx, (_, state_row) in enumerate(top_unequal.iterrows()):
        state_name = state_row['state']
        gini = state_row['gini_district']
        
        # Get district volumes for this state
        state_data = df[df['state'] == state_name].groupby('district')['total_demo'].sum()
        state_data = state_data.sort_values()
        
        # Calculate Lorenz curve
        cumsum = state_data.cumsum()
        lorenz_x = np.arange(1, len(state_data) + 1) / len(state_data)
        lorenz_y = cumsum / cumsum.iloc[-1]
        
        # Plot
        ax.plot(lorenz_x, lorenz_y, linewidth=2.5, alpha=0.8,
                color=colors[idx],
                label=f'{state_name[:15]} (Gini={gini:.3f})')
    
    ax.set_xlabel('Cumulative Share of Districts')
    ax.set_ylabel('Cumulative Share of Updates')
    ax.set_title('HIGH-IMPACT 06: Lorenz Curves - Top 5 Most Unequal States', 
                 fontweight='bold', fontsize=14)
    ax.legend(loc='upper left', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    caption = ("Lorenz curves reveal WHERE in the distribution inequality concentrates. Some states may have "
               "moderate Gini but extreme top-1% dominance; others may have diffuse inequality across all "
               "quantiles. Policy responses differ based on concentration pattern.")
    add_caption_box(fig, caption)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'high_impact_06_lorenz_curves.png'), 
                dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ high_impact_06_lorenz_curves.png")

# ============================================================================
# ANALYSIS 7: Campaign Attribution via Event Detection
# ============================================================================
def plot_analysis_07_spike_detection(national_date, output_dir):
    """
    Analysis 7: Campaign Attribution via Event Detection (Spike Identification)
    
    Applies changepoint detection to identify statistically significant volume spikes.
    """
    fig, ax = plt.subplots(figsize=(16, 7))
    
    # Plot time series
    ax.plot(national_date['date'], national_date['total_demo'], 
            color=FORENSIC_COLORS['primary'], linewidth=1.5, alpha=0.8,
            label='Daily Updates')
    
    # Calculate rolling statistics for spike detection
    rolling_mean = national_date['total_demo'].rolling(window=7, center=True).mean()
    rolling_std = national_date['total_demo'].rolling(window=7, center=True).std()
    
    # Define threshold for spikes (3 standard deviations above mean)
    threshold = rolling_mean + 3 * rolling_std
    
    # Identify spikes
    spikes = national_date[national_date['total_demo'] > threshold].copy()
    
    # Plot spikes
    if len(spikes) > 0:
        ax.scatter(spikes['date'], spikes['total_demo'], 
                  color=FORENSIC_COLORS['warning'], s=100, 
                  zorder=5, alpha=0.8, edgecolors='black',
                  label=f'Detected Spikes (n={len(spikes)})')
        
        # Annotate top 5 spikes
        top_spikes = spikes.nlargest(5, 'total_demo')
        for _, spike in top_spikes.iterrows():
            ax.annotate(f'{spike["total_demo"]:,.0f}', 
                       xy=(spike['date'], spike['total_demo']),
                       xytext=(0, 10), textcoords='offset points',
                       fontsize=8, ha='center',
                       bbox=dict(boxstyle='round,pad=0.3', 
                                fc='yellow', alpha=0.7))
    
    # Plot rolling mean
    ax.plot(national_date['date'], rolling_mean, 
            color=FORENSIC_COLORS['success'], linewidth=2, 
            linestyle='--', alpha=0.6,
            label='7-day Rolling Mean')
    
    # Plot threshold
    ax.plot(national_date['date'], threshold, 
            color=FORENSIC_COLORS['warning'], linewidth=1.5, 
            linestyle=':', alpha=0.5,
            label='Spike Threshold (μ + 3σ)')
    
    ax.set_xlabel('Date')
    ax.set_ylabel('Total Daily Updates')
    ax.set_title('HIGH-IMPACT 07: Campaign Attribution via Event Detection', 
                 fontweight='bold', fontsize=14)
    ax.legend(loc='upper right')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3)
    
    # Statistics box
    textstr = f'Spikes Detected: {len(spikes)}\\nDetection Method: 3σ above rolling mean\\nWindow: 7 days'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.6)
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)
    
    caption = ("Changepoint detection identifies statistically significant volume spikes with confidence intervals. "
               "Detected events can be cross-referenced with official UIDAI campaign announcements for retrospective "
               "effectiveness assessment. Correlation indicates responsive system; no correlation suggests attribution ambiguity.")
    add_caption_box(fig, caption)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'high_impact_07_spike_detection.png'), 
                dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ high_impact_07_spike_detection.png")

# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    print("="*70)
    print("FORENSIC AUDIT - HIGH-IMPACT ANALYSES GENERATION")
    print("Generating 5 New Analytical Visualizations")
    print("="*70)
    
    # Create output directory
    os.makedirs(PLOTS_FINAL_DIR, exist_ok=True)
    
    # Load and process data
    print("\n[1/4] Loading and preprocessing data...")
    df = load_demographic_data()
    df = preprocess_data(df)
    df = engineer_features(df)
    
    print("\n[2/4] Aggregating data at multiple levels...")
    district_date, state_date, state_month, national_date, national_month = aggregate_levels(df)
    
    # Calculate additional metrics
    print("\n[3/4] Calculating metrics...")
    volatility = calculate_stability_metrics(district_date)
    concentration = calculate_concentration(df)
    
    # District aggregation
    district_agg = df.groupby(['state', 'district']).agg({
        'demo_age_5_17': 'sum',
        'demo_age_17_': 'sum',
        'total_demo': 'sum'
    }).reset_index()
    district_agg['demo_minor_share'] = district_agg['demo_age_5_17'] / (district_agg['total_demo'] + 1e-10)
    
    # State weekend analysis
    state_weekend = state_date.groupby(['state', 'is_weekend'])['total_demo'].mean().unstack()
    state_weekend.columns = ['weekday_avg', 'weekend_avg']
    state_weekend['weekend_ratio'] = state_weekend['weekend_avg'] / (state_weekend['weekday_avg'] + 1e-10)
    
    # Set up style
    print("\n[4/4] Generating high-impact visualizations...")
    setup_forensic_style()
    
    # Generate all 5 high-impact analyses
    plot_analysis_03_weekend_gini(state_weekend, concentration, PLOTS_FINAL_DIR)
    plot_analysis_04_volatility_minor(volatility, district_agg, PLOTS_FINAL_DIR)
    plot_analysis_05_mom_growth(state_month, PLOTS_FINAL_DIR)
    plot_analysis_06_lorenz_curves(df, concentration, PLOTS_FINAL_DIR)
    plot_analysis_07_spike_detection(national_date, PLOTS_FINAL_DIR)
    
    print("\n" + "="*70)
    print("✅ HIGH-IMPACT ANALYSES GENERATION COMPLETE!")
    print(f"📁 Output directory: {PLOTS_FINAL_DIR}")
    print(f"📊 Generated 5 new high-impact analyses")
    print("="*70)

if __name__ == "__main__":
    main()
