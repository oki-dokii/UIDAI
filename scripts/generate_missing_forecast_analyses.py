#!/usr/bin/env python3
"""
UIDAI Data Hackathon 2026 - MISSING FORECAST ANALYSES GENERATION
Implements high-impact analyses identified in forensic audit:
1. District Decline Rate vs. Absolute Volume Scatter
2. State-Level Decline Summary (alternative to concentration index)
3. Enrolment-Update Correlation (single-month cross-sectional)

Note: Some analyses from audit cannot be implemented due to data limitations.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================
SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent
DATA_DIR = BASE_DIR / "outputs" / "integrated_analysis"
FORECAST_DIR = BASE_DIR / "outputs" / "forecast_plots"
OUTPUT_DIR = BASE_DIR / "outputs" / "forecast_final" / "new_analyses"

# Create output directory
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# ============================================================================
# DATA LOADING
# ============================================================================

def load_data():
    """Load declining districts and integrated data."""
    print("📂 Loading data...")
    
    # Load declining districts
    declining_path = FORECAST_DIR / "declining_districts.csv"
    declining_df = pd.read_csv(declining_path)
    print(f"   ✅ Loaded {len(declining_df)} declining districts")
    
    # Load integrated data for absolute volumes
    integrated_path = DATA_DIR / "integrated_data.csv"
    integrated_df = pd.read_csv(integrated_path)
    print(f"   ✅ Loaded {len(integrated_df)} integrated records")
    
    return declining_df, integrated_df


# ============================================================================
# ANALYSIS 1: DECLINE RATE VS. ABSOLUTE VOLUME SCATTER
# ============================================================================

def generate_decline_volume_scatter(declining_df, integrated_df):
    """
    Bivariate plot: decline rate (%) vs absolute transaction volume.
    Disambiguates denominator effects from substantive decline.
    """
    print("\n1️⃣ Generating Decline vs. Volume Scatter...")
    
    # Merge to get absolute volumes
    # Use mean_activity from declining_df as proxy for absolute volume
    merged = declining_df.copy()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Create scatter plot
    # Size by mean_activity (volume)
    # Color by state
    states = merged['state'].unique()
    colors = plt.cm.tab20(np.linspace(0, 1, len(states)))
    state_color_map = dict(zip(states, colors))
    
    for state in states:
        state_data = merged[merged['state'] == state]
        ax.scatter(
            state_data['relative_slope'],
            state_data['mean_activity'],
            s=state_data['mean_activity'] / 10,  # Size by volume
            alpha=0.6,
            c=[state_color_map[state]],
            label=state if len(state_data) > 0 else None,
            edgecolors='white',
            linewidth=0.5
        )
    
    # Add quadrant lines
    ax.axvline(x=-50, color='gray', linestyle='--', alpha=0.5, linewidth=1)
    ax.axhline(y=merged['mean_activity'].median(), color='gray', linestyle='--', 
               alpha=0.5, linewidth=1, label='Median Volume')
    
    # Annotations for key districts
    top_concern = merged.nsmallest(5, 'relative_slope')
    for _, row in top_concern.iterrows():
        ax.annotate(
            row['district'][:15],
            (row['relative_slope'], row['mean_activity']),
            xytext=(5, 5),
            textcoords='offset points',
            fontsize=8,
            alpha=0.7,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3)
        )
    
    # Styling
    ax.set_xlabel('Monthly Decline Rate (%)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Absolute Transaction Volume (Mean)', fontsize=13, fontweight='bold')
    ax.set_title(
        '📊 District Decline Rate vs. Transaction Volume\n' +
        'Disambiguating Denominator Effects from Substantive Decline',
        fontsize=15, fontweight='bold', pad=20
    )
    
    # Add interpretive boxes
    textstr = 'High Volume + High Decline\n→ System Capacity Issue'
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    textstr2 = 'Low Volume + High Decline\n→ Service Access Issue'
    ax.text(0.05, 0.85, textstr2, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    
    # Legend (only show states with data, limit to top 10)
    handles, labels = ax.get_legend_handles_labels()
    if len(handles) > 10:
        ax.legend(handles[:10], labels[:10], loc='upper right', fontsize=8, 
                 title='States (top 10)', framealpha=0.9)
    else:
        ax.legend(loc='upper right', fontsize=8, title='States', framealpha=0.9)
    
    ax.grid(True, alpha=0.3, linestyle=':')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    # Save
    output_path = OUTPUT_DIR / "01_decline_vs_volume_scatter.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"   ✅ Saved: {output_path}")
    
    return output_path


# ============================================================================
# ANALYSIS 2: STATE-LEVEL DECLINE SUMMARY
# ============================================================================

def generate_state_decline_summary(declining_df):
    """
    Alternative to concentration index (cannot compute without total district counts).
    Shows number of declining districts per state.
    """
    print("\n2️⃣ Generating State-Level Decline Summary...")
    
    # Count declining districts by state
    state_counts = declining_df.groupby('state').agg({
        'district': 'count',
        'relative_slope': 'mean'
    }).reset_index()
    state_counts.columns = ['state', 'num_declining_districts', 'avg_decline_rate']
    state_counts = state_counts.sort_values('num_declining_districts', ascending=False)
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Plot 1: Number of declining districts
    colors1 = plt.cm.Reds(np.linspace(0.4, 0.9, len(state_counts)))
    bars1 = ax1.barh(state_counts['state'], state_counts['num_declining_districts'], 
                     color=colors1, edgecolor='white', linewidth=0.5)
    
    # Add value labels
    for bar, val in zip(bars1, state_counts['num_declining_districts']):
        ax1.text(val + 0.1, bar.get_y() + bar.get_height()/2, 
                f'{int(val)}', va='center', fontsize=9, fontweight='bold')
    
    ax1.set_xlabel('Number of Declining Districts', fontsize=11, fontweight='bold')
    ax1.set_title('Districts with Declining Activity per State', fontsize=12, fontweight='bold')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.grid(axis='x', alpha=0.3, linestyle=':')
    
    # Plot 2: Average decline rate
    colors2 = plt.cm.YlOrRd(np.linspace(0.4, 0.9, len(state_counts)))
    bars2 = ax2.barh(state_counts['state'], state_counts['avg_decline_rate'], 
                     color=colors2, edgecolor='white', linewidth=0.5)
    
    # Add value labels
    for bar, val in zip(bars2, state_counts['avg_decline_rate']):
        ax2.text(val - 2, bar.get_y() + bar.get_height()/2, 
                f'{val:.1f}%', va='center', ha='right', fontsize=9, fontweight='bold')
    
    ax2.set_xlabel('Average Decline Rate (%)', fontsize=11, fontweight='bold')
    ax2.set_title('Average Decline Rate per State', fontsize=12, fontweight='bold')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.grid(axis='x', alpha=0.3, linestyle=':')
    
    plt.suptitle('🗺️ State-Level Decline Patterns\nIdentifying Systemic vs. Isolated Issues',
                 fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    # Save
    output_path = OUTPUT_DIR / "02_state_decline_summary.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"   ✅ Saved: {output_path}")
    
    return output_path


# ============================================================================
# ANALYSIS 3: ENROLMENT-UPDATE CORRELATION
# ============================================================================

def generate_enrolment_update_correlation(integrated_df):
    """
    Cross-sectional correlation between enrolment and updates at state level.
    Alternative to temporal concordance (requires multi-month data).
    """
    print("\n3️⃣ Generating Enrolment-Update Correlation...")
    
    # Aggregate by state
    state_agg = integrated_df.groupby('state').agg({
        'total_enrol': 'sum',
        'total_updates': 'sum'
    }).reset_index()
    
    # Calculate correlation
    correlation = state_agg['total_enrol'].corr(state_agg['total_updates'])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Scatter plot
    scatter = ax.scatter(
        state_agg['total_enrol'],
        state_agg['total_updates'],
        s=200,
        alpha=0.6,
        c=range(len(state_agg)),
        cmap='viridis',
        edgecolors='white',
        linewidth=1
    )
    
    # Add state labels for outliers
    # Label states with high update or enrolment volume
    threshold_enrol = state_agg['total_enrol'].quantile(0.75)
    threshold_update = state_agg['total_updates'].quantile(0.75)
    
    for _, row in state_agg.iterrows():
        if row['total_enrol'] > threshold_enrol or row['total_updates'] > threshold_update:
            ax.annotate(
                row['state'][:15],
                (row['total_enrol'], row['total_updates']),
                xytext=(5, 5),
                textcoords='offset points',
                fontsize=8,
                alpha=0.7
            )
    
    # Add regression line
    z = np.polyfit(state_agg['total_enrol'], state_agg['total_updates'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(state_agg['total_enrol'].min(), state_agg['total_enrol'].max(), 100)
    ax.plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2, 
            label=f'Linear Fit (r = {correlation:.3f})')
    
    # Styling
    ax.set_xlabel('Total Enrolments', fontsize=12, fontweight='bold')
    ax.set_ylabel('Total Updates', fontsize=12, fontweight='bold')
    ax.set_title(
        f'🔗 Enrolment-Update Correlation by State\n' +
        f'Cross-Sectional Analysis (Correlation: {correlation:.3f})',
        fontsize=14, fontweight='bold', pad=20
    )
    
    # Add interpretation box
    if correlation > 0.5:
        interp = "Strong positive correlation suggests\nbundled service delivery patterns"
    elif correlation > 0:
        interp = "Weak positive correlation suggests\npartially independent demand drivers"
    else:
        interp = "Negative correlation suggests\ninverse demand patterns"
    
    ax.text(0.05, 0.95, interp, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
    
    ax.legend(loc='lower right', fontsize=10, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle=':')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    # Save
    output_path = OUTPUT_DIR / "03_enrolment_update_correlation.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"   ✅ Saved: {output_path}")
    
    return output_path


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 70)
    print("📊 GENERATING MISSING FORECAST ANALYSES")
    print("    Based on Forensic Audit Recommendations")
    print("=" * 70)
    
    # Load data
    declining_df, integrated_df = load_data()
    
    # Generate analyses
    print("\n" + "=" * 70)
    print("🎨 GENERATING VISUALIZATIONS")
    print("=" * 70)
    
    path1 = generate_decline_volume_scatter(declining_df, integrated_df)
    path2 = generate_state_decline_summary(declining_df)
    path3 = generate_enrolment_update_correlation(integrated_df)
    
    print("\n" + "=" * 70)
    print("✅ ANALYSIS GENERATION COMPLETE")
    print(f"    Output directory: {OUTPUT_DIR}")
    print("=" * 70)
    
    print("\n📋 GENERATED FILES:")
    print(f"   1. {path1.name}")
    print(f"   2. {path2.name}")
    print(f"   3. {path3.name}")
    
    print("\n⚠️  DATA LIMITATIONS NOTED:")
    print("   • Population density data not available (Analysis #1 limitation)")
    print("   • Total district counts per state not available (Analysis #2)")
    print("   • 12-month historical data not available (Analysis #3 - volatility)")
    print("   • 24-month time series not available (Analysis #4 - temporal concordance)")
    print("\n   These limitations are documented in audit_summary.md")


if __name__ == "__main__":
    main()
