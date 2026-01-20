#!/usr/bin/env python3
"""
UIDAI DISTRICT-LEVEL INEQUALITY ANALYSIS
Addresses audit findings on spatial inequality and sub-state heterogeneity

Creates:
1. District-level choropleth map
2. Lorenz curves for spatial inequality
3. Gini coefficient analysis
4. Within-state heterogeneity analysis
"""

import os
import sys
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_FILE = os.path.join(BASE_DIR, "outputs", "integrated_analysis", "integrated_data.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "geospatial_plots")

FIGURE_DPI = 300

# ============================================================================
# DATA LOADING
# ============================================================================

def load_district_data():
    """Load UIDAI data at district level."""
    print(f"📂 Loading district data from: {DATA_FILE}")
    
    if not os.path.exists(DATA_FILE):
        print(f"❌ Data file not found: {DATA_FILE}")
        sys.exit(1)
    
    df = pd.read_csv(DATA_FILE)
    print(f"   Loaded {len(df):,} district records")
    print(f"   States: {df['state'].nunique()}")
    print(f"   Districts: {df['district'].nunique()}")
    
    return df


# ============================================================================
# GINI COEFFICIENT CALCULATION
# ============================================================================

def calculate_gini(values):
    """
    Calculate Gini coefficient for inequality measurement.
    
    Args:
        values: Array of values (e.g., child attention gap)
        
    Returns:
        Gini coefficient (0 = perfect equality, 1 = perfect inequality)
    """
    values = np.array(values)
    values = values[~np.isnan(values)]
    
    if len(values) == 0:
        return np.nan
    
    # Sort values
    sorted_values = np.sort(values)
    n = len(sorted_values)
    
    # Calculate Gini
    index = np.arange(1, n + 1)
    gini = (2 * np.sum(index * sorted_values)) / (n * np.sum(sorted_values)) - (n + 1) / n
    
    return abs(gini)  # Take absolute value for interpretability


# ============================================================================
# VISUALIZATION 1: District-Level Choropleth
# ============================================================================

def create_district_choropleth(df, output_file):
    """
    Create district-level child attention gap visualization.
    Shows intra-state heterogeneity.
    """
    # Group by district (take most recent month if temporal data exists)
    if 'month' in df.columns:
        latest = df['month'].max()
        df_plot = df[df['month'] == latest].copy()
    else:
        df_plot = df.copy()
    
    # Sort by child attention gap
    df_plot = df_plot.sort_values('child_attention_gap', ascending=True)
    df_plot = df_plot.dropna(subset=['child_attention_gap'])
    
    # Take top and bottom districts for visualization clarity
    n_show = min(50, len(df_plot))
    top_bottom = pd.concat([
        df_plot.head(n_show // 2),
        df_plot.tail(n_show // 2)
    ])
    
    fig, ax = plt.subplots(figsize=(14, 16))
    
    # Color normalization (diverging)
    vmin = top_bottom['child_attention_gap'].min()
    vmax = top_bottom['child_attention_gap'].max()
    norm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)
    colors = plt.cm.get_cmap('RdYlGn')(norm(top_bottom['child_attention_gap']))
    
    # Create labels with state info
    labels = [f"{row['district']}, {row['state'][:3]}" 
             for _, row in top_bottom.iterrows()]
    
    # Horizontal bar chart
    bars = ax.barh(labels, top_bottom['child_attention_gap'], 
                  color=colors, edgecolor='white', linewidth=0.5)
    
    # Add value labels
    for bar, val in zip(bars, top_bottom['child_attention_gap']):
        width = bar.get_width()
        ax.annotate(f'{val:.3f}',
                   xy=(width, bar.get_y() + bar.get_height()/2),
                   xytext=(3 if val >= 0 else -3, 0), 
                   textcoords='offset points',
                   ha='left' if val >= 0 else 'right', 
                   va='center', fontsize=7, color='#333')
    
    # Zero reference line
    ax.axvline(x=0, color='black', linestyle='-', linewidth=2, alpha=0.7)
    
    # Styling
    ax.set_xlabel('Child Attention Gap', fontsize=12, fontweight='bold')
    ax.set_ylabel('')
    ax.set_title(f'🗺️ District-Level Child Attention Gap\\n' +
                f'Top & Bottom {n_show//2} Districts (of {len(df_plot):,} total)',
                fontsize=15, fontweight='bold', pad=15)
    
    # Add interpretation
    note_text = ("📊 District Resolution Analysis:\\n" +
                "Reveals intra-state heterogeneity masked by state aggregates.\\n" +
                "Negative = children under-served | Positive = over-served")
    ax.text(0.02, 0.98, note_text, transform=ax.transAxes,
           fontsize=9, verticalalignment='top', horizontalalignment='left',
           bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
    
    # Colorbar
    sm = plt.cm.ScalarMappable(cmap='RdYlGn', norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.7, aspect=30, pad=0.02)
    cbar.set_label('Child Attention Gap', fontsize=10)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='y', labelsize=7)
    
    plt.tight_layout()
    
    # Save
    output_path = os.path.join(OUTPUT_DIR, output_file)
    plt.savefig(output_path, dpi=FIGURE_DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"   ✅ Saved: {output_path}")
    return output_path


# ============================================================================
# VISUALIZATION 2: Lorenz Curve
# ============================================================================

def create_lorenz_curve(df, output_file):
    """
    Create Lorenz curve showing spatial inequality in child attention gap.
    Compares actual distribution to perfect equality.
    """
    # Get district-level gaps (take absolute values for cumulative distribution)
    gaps = df.groupby('district')['child_attention_gap'].mean().dropna()
    
    # Calculate for both raw gaps and absolute gaps
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # For actual gaps (can be negative)
    values = gaps.values
    values_sorted = np.sort(values)
    n = len(values_sorted)
    
    # Cumulative proportions
    cum_population = np.arange(1, n+1) / n
    cum_gap = np.cumsum(values_sorted) / np.sum(values_sorted) if np.sum(values_sorted) != 0 else np.zeros(n)
    
    # Plot Lorenz curve
    ax1.plot([0, 1], [0, 1], 'k--', linewidth=2, label='Perfect Equality (45° line)')
    ax1.plot(cum_population, cum_gap, 'b-', linewidth=3, label='Actual Distribution')
    ax1.fill_between(cum_population, cum_gap, cum_population, alpha=0.3, color='red', 
                     label='Inequality Area')
    
    # Calculate Gini
    gini = calculate_gini(values)
    
    ax1.set_xlabel('Cumulative Share of Districts', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Cumulative Share of Child Attention Gap', fontsize=12, fontweight='bold')
    ax1.set_title(f'📊 Lorenz Curve: Spatial Inequality\\n' +
                 f'Gini Coefficient = {gini:.3f}',
                 fontsize=14, fontweight='bold', pad=15)
    ax1.legend(loc='upper left', fontsize=10, framealpha=0.9)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    # For absolute gaps (magnitude of under/over-service)
    abs_values = np.abs(values)
    abs_sorted = np.sort(abs_values)
    cum_abs_gap = np.cumsum(abs_sorted) / np.sum(abs_sorted) if np.sum(abs_sorted) != 0 else np.zeros(n)
    
    ax2.plot([0, 1], [0, 1], 'k--', linewidth=2, label='Perfect Equality')
    ax2.plot(cum_population, cum_abs_gap, 'g-', linewidth=3, label='Actual Distribution (Absolute)')
    ax2.fill_between(cum_population, cum_abs_gap, cum_population, alpha=0.3, color='orange')
    
    gini_abs = calculate_gini(abs_values)
    
    ax2.set_xlabel('Cumulative Share of Districts', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Cumulative Share of |Gap| Magnitude', fontsize=12, fontweight='bold')
    ax2.set_title(f'📊 Lorenz Curve: Gap Magnitude\\n' +
                 f'Gini Coefficient = {gini_abs:.3f}',
                 fontsize=14, fontweight='bold', pad=15)
    ax2.legend(loc='upper left', fontsize=10, framealpha=0.9)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    
    # Add interpretation box
    interpretation = ("📍 INTERPRETATION:\\n" +
                     "• Closer to diagonal = more equal distribution across districts\\n" +
                     "• Larger area between curves = greater inequality\\n" +
                     "• Gini ≈ 0: perfect equality | Gini ≈ 1: perfect inequality")
    fig.text(0.5, 0.02, interpretation, transform=fig.transFigure,
            fontsize=10, verticalalignment='bottom', horizontalalignment='center',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
            color='#8B4513', fontweight='bold')
    
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.12)
    
    # Save
    output_path = os.path.join(OUTPUT_DIR, output_file)
    plt.savefig(output_path, dpi=FIGURE_DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"   ✅ Saved: {output_path}")
    return output_path


# ============================================================================
# VISUALIZATION 3: Gini Coefficient by State
# ============================================================================

def create_gini_analysis(df, output_file):
    """
    Calculate and visualize Gini coefficients by state.
    Shows which states have high internal inequality.
    """
    # Calculate Gini for each state (within-state inequality)
    state_ginis = []
    
    for state in df['state'].unique():
        state_data = df[df['state'] == state]['child_attention_gap'].dropna()
        if len(state_data) > 1:
            gini = calculate_gini(state_data.values)
            state_ginis.append({
                'state': state,
                'gini': gini,
                'n_districts': len(state_data),
                'gap_mean': state_data.mean(),
                'gap_std': state_data.std()
            })
    
    gini_df = pd.DataFrame(state_ginis).sort_values('gini', ascending=False)
    
    # Calculate national Gini
    national_gini = calculate_gini(df['child_attention_gap'].dropna().values)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 10), gridspec_kw={'width_ratios': [2, 1]})
    
    # Plot 1: Gini coefficients by state
    colors = plt.cm.YlOrRd(np.linspace(0.3, 0.9, len(gini_df)))
    bars = ax1.barh(gini_df['state'], gini_df['gini'], color=colors, 
                   edgecolor='darkred', linewidth=0.5)
    
    # Add national average line
    ax1.axvline(x=national_gini, color='blue', linestyle='--', linewidth=3, 
               label=f'National Gini = {national_gini:.3f}', alpha=0.7)
    
    # Add value labels
    for bar, val in zip(bars, gini_df['gini']):
        width = bar.get_width()
        ax1.annotate(f'{val:.3f}',
                    xy=(width, bar.get_y() + bar.get_height()/2),
                    xytext=(3, 0), textcoords='offset points',
                    ha='left', va='center', fontsize=8, color='darkred', fontweight='bold')
    
    ax1.set_xlabel('Gini Coefficient (Within-State Inequality)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('')
    ax1.set_title('📊 Within-State Inequality Analysis\\n' +
                 'Gini Coefficients for Child Attention Gap',
                 fontsize=15, fontweight='bold', pad=15)
    ax1.legend(loc='lower right', fontsize=11, framealpha=0.9)
    ax1.grid(axis='x', alpha=0.3, linestyle='--')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    
    # Plot 2: Scatter - Gini vs. Mean Gap
    scatter = ax2.scatter(gini_df['gap_mean'], gini_df['gini'], 
                         s=gini_df['n_districts']*10, 
                         c=gini_df['gini'], cmap='YlOrRd',
                         alpha=0.6, edgecolors='black', linewidths=1)
    
    # Label top 10 by Gini
    top_10 = gini_df.head(10)
    for _, row in top_10.iterrows():
        ax2.annotate(row['state'][:10], 
                    (row['gap_mean'], row['gini']),
                    fontsize=8, alpha=0.9,
                    xytext=(5, 5), textcoords='offset points',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.4))
    
    ax2.axhline(y=national_gini, color='blue', linestyle='--', linewidth=2, alpha=0.7)
    ax2.axvline(x=0, color='red', linestyle='--', linewidth=2, alpha=0.5)
    
    ax2.set_xlabel('Mean Child Attention Gap', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Gini Coefficient', fontsize=11, fontweight='bold')
    ax2.set_title('Inequality vs. Mean Gap\\n(Size = # Districts)', 
                 fontsize=12, fontweight='bold', pad=10)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    
    plt.colorbar(scatter, ax=ax2, label='Gini Coefficient', shrink=0.8)
    
    plt.tight_layout()
    
    # Save
    output_path = os.path.join(OUTPUT_DIR, output_file)
    plt.savefig(output_path, dpi=FIGURE_DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"   ✅ Saved: {output_path}")
    
    return output_path, gini_df


# ============================================================================
# VISUALIZATION 4: Within-State Heterogeneity
# ============================================================================

def create_heterogeneity_analysis(df, output_file):
    """
    Show distribution of child attention gap within each state.
    Box plots reveal intra-state variation.
    """
    # Get top states by number of districts or volume
    state_counts = df.groupby('state').size().sort_values(ascending=False)
    top_states = state_counts.head(15).index
    
    # Prepare data for box plot
    plot_data = []
    state_labels = []
    
    for state in top_states:
        state_gaps = df[df['state'] == state]['child_attention_gap'].dropna()
        if len(state_gaps) > 0:
            plot_data.append(state_gaps)
            state_labels.append(f"{state[:15]}\\n(n={len(state_gaps)})")
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Create box plot
    bp = ax.boxplot(plot_data, labels=state_labels, patch_artist=True,
                   boxprops=dict(facecolor='lightblue', alpha=0.7, linewidth=1.5),
                   medianprops=dict(color='red', linewidth=2.5),
                   whiskerprops=dict(color='blue', linewidth=1.5),
                   capprops=dict(color='blue', linewidth=1.5),
                   flierprops=dict(marker='o', markerfacecolor='orange', markersize=5, alpha=0.5))
    
    # Color boxes by median value
    medians = [np.median(data) for data in plot_data]
    norm = mcolors.TwoSlopeNorm(vmin=min(medians), vcenter=0, vmax=max(medians))
    
    for patch, median in zip(bp['boxes'], medians):
        color = plt.cm.RdYlGn(norm(median))
        patch.set_facecolor(color)
    
    # Zero reference line
    ax.axhline(y=0, color='black', linestyle='--', linewidth=2, alpha=0.7, label='Zero Gap')
    
    # Styling
    ax.set_ylabel('Child Attention Gap', fontsize=13, fontweight='bold')
    ax.set_xlabel('State (with District Count)', fontsize=13, fontweight='bold')
    ax.set_title('📊 Within-State Heterogeneity Analysis\\n' +
                'Distribution of Child Attention Gap Across Districts (Top 15 States)',
                fontsize=15, fontweight='bold', pad=15)
    ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Rotate x labels for readability
    plt.xticks(rotation=45, ha='right')
    
    # Add interpretation
    note_text = ("📍 Box Plot Elements:\\n" +
                "• Box: 25th-75th percentile (IQR)\\n" +
                "• Red line: Median\\n" +
                "• Whiskers: 1.5×IQR range\\n" +
                "• Orange dots: Outliers")
    ax.text(0.02, 0.98, note_text, transform=ax.transAxes,
           fontsize=9, verticalalignment='top', horizontalalignment='left',
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout()
    
    # Save
    output_path = os.path.join(OUTPUT_DIR, output_file)
    plt.savefig(output_path, dpi=FIGURE_DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"   ✅ Saved: {output_path}")
    return output_path


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 70)
    print("🗺️  UIDAI DISTRICT-LEVEL INEQUALITY ANALYSIS")
    print("    Sub-State Heterogeneity & Spatial Inequality Metrics")
    print("=" * 70)
    
    # Load district data
    df = load_district_data()
    
    print("\\n" + "=" * 70)
    print("📊 CREATING DISTRICT-LEVEL VISUALIZATIONS")
    print("=" * 70)
    
    # 1. District choropleth
    print("\\n1️⃣ Creating District-Level Choropleth...")
    create_district_choropleth(df, '09_district_choropleth.png')
    
    # 2. Lorenz curve
    print("\\n2️⃣ Creating Lorenz Curve Analysis...")
    create_lorenz_curve(df, '10_lorenz_curve_inequality.png')
    
    # 3. Gini coefficient analysis
    print("\\n3️⃣ Creating Gini Coefficient Analysis...")
    _, gini_df = create_gini_analysis(df, '11_gini_coefficient_analysis.png')
    
    # 4. Within-state heterogeneity
    print("\\n4️⃣ Creating Within-State Heterogeneity Analysis...")
    create_heterogeneity_analysis(df, '12_within_state_heterogeneity.png')
    
    print("\\n" + "=" * 70)
    print("✅ DISTRICT-LEVEL ANALYSIS COMPLETE")
    print(f"   Output directory: {OUTPUT_DIR}")
    print("=" * 70)
    
    print("\\n📊 INEQUALITY INSIGHTS:")
    print(f"   • Total districts analyzed: {df['district'].nunique():,}")
    print(f"   • States with highest Gini (top 3):")
    for idx, row in gini_df.head(3).iterrows():
        print(f"     {row['state']}: {row['gini']:.3f}")
    print("   ✅ Lorenz curves reveal spatial concentration patterns")
    print("   ✅ Within-state analysis shows heterogeneity masked by aggregates")


if __name__ == "__main__":
    main()
