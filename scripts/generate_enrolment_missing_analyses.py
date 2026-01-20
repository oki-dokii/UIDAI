#!/usr/bin/env python3
"""
UIDAI Enrolment Forensic Audit - Missing High-Impact Analyses Generator
Implements 6 critical visualizations identified in the analytical audit

Author: UIDAI Hackathon Team
Generated: 2026-01-20
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "enrolment_analysis")
PLOTS_DIR = os.path.join(OUTPUT_DIR, "plots")
NEW_PLOTS_DIR = os.path.join(OUTPUT_DIR, "plots_missing_analyses")

# Create output directory for new analyses
os.makedirs(NEW_PLOTS_DIR, exist_ok=True)

# State population data (2021 Census projections for 2025, in thousands)
STATE_POPULATION = {
    'Uttar Pradesh': 241700, 'Maharashtra': 125800, 'Bihar': 128500,
    'West Bengal': 102900, 'Madhya Pradesh': 88300, 'Tamil Nadu': 78100,
    'Rajasthan': 82000, 'Karnataka': 68200, 'Gujarat': 69700,
    'Andhra Pradesh': 53700, 'Odisha': 46700, 'Telangana': 39800,
    'Kerala': 35700, 'Jharkhand': 38600, 'Assam': 35600,
    'Punjab': 30500, 'Chhattisgarh': 30500, 'Haryana': 29000,
    'Delhi': 19300, 'Jammu And Kashmir': 13600, 'Uttarakhand': 11400,
    'Himachal Pradesh': 7400, 'Tripura': 4200, 'Meghalaya': 3400,
    'Manipur': 3300, 'Nagaland': 2250, 'Goa': 1600,
    'Arunachal Pradesh': 1600, 'Puducherry': 1500, 'Mizoram': 1250,
    'Chandigarh': 1200, 'Sikkim': 700, 'Andaman And Nicobar Islands': 420,
    'Dadra And Nagar Haveli': 400, 'Daman And Diu': 270, 'Lakshadweep': 70
}

# ============================================================================
# PLOTTING SETUP
# ============================================================================
def setup_plots():
    """Configure matplotlib for publication-quality plots."""
    plt.rcParams['figure.dpi'] = 150
    plt.rcParams['savefig.dpi'] = 300
    plt.rcParams['font.size'] = 10
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['axes.labelsize'] = 11
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['xtick.labelsize'] = 9
    plt.rcParams['ytick.labelsize'] = 9
    plt.rcParams['legend.fontsize'] = 9
    sns.set_palette("husl")

# ============================================================================
# DATA LOADING
# ============================================================================
def load_data():
    """Load all required datasets for missing analyses."""
    print("\n" + "="*60)
    print("LOADING DATA FOR MISSING ANALYSES")
    print("="*60)
    
    # Load district-level data (anomalies contains all district-date records)
    print("\n📂 Loading anomalies.csv (district-date level)...")
    df = pd.read_csv(os.path.join(OUTPUT_DIR, 'anomalies.csv'))
    df['date'] = pd.to_datetime(df['date'])
    print(f"   ✓ Loaded {len(df):,} district-day records")
    
    # Load concentration metrics
    print("\n📂 Loading concentration_metrics.csv...")
    concentration = pd.read_csv(os.path.join(OUTPUT_DIR, 'concentration_metrics.csv'))
    print(f"   ✓ Loaded {len(concentration):,} state records")
    
    # Load volatility metrics
    print("\n📂 Loading volatility_metrics.csv...")
    volatility = pd.read_csv(os.path.join(OUTPUT_DIR, 'volatility_metrics.csv'))
    print(f"   ✓ Loaded {len(volatility):,} district records")
    
    # Load district clusters (has more metadata)
    print("\n📂 Loading district_clusters.csv...")
    clusters = pd.read_csv(os.path.join(OUTPUT_DIR, 'district_clusters.csv'))
    print(f"   ✓ Loaded {len(clusters):,} district records")
    
    return df, concentration, volatility, clusters

# ============================================================================
# ANALYSIS 1: NORMALIZED STATE ENROLMENT INTENSITY
# ============================================================================
def create_normalized_state_intensity(df, output_dir):
    """
    Monthly enrolments per 1,000 population by state (heatmap).
    Removes population-size confounding from state comparisons.
    """
    print("\n" + "="*60)
    print("ANALYSIS 1: NORMALIZED STATE ENROLMENT INTENSITY")
    print("="*60)
    
    # Create state-month aggregates
    df['year_month'] = df['date'].dt.to_period('M')
    state_month = df.groupby(['state', 'year_month']).agg({
        'total_enrol': 'sum'
    }).reset_index()
    
    # Add population data
    state_month['population_thousands'] = state_month['state'].map(STATE_POPULATION)
    
    # Filter states with population data
    state_month = state_month[state_month['population_thousands'].notna()].copy()
    
    # Calculate per-1000 rate
    state_month['enrol_per_1000'] = (
        state_month['total_enrol'] / state_month['population_thousands']
    )
    
    # Pivot for heatmap
    heatmap_data = state_month.pivot(
        index='state', 
        columns='year_month', 
        values='enrol_per_1000'
    )
    
    # Sort by total enrolment intensity
    heatmap_data['total'] = heatmap_data.sum(axis=1)
    heatmap_data = heatmap_data.sort_values('total', ascending=False).drop('total', axis=1)
    
    # Take top 25 states for visibility
    heatmap_data = heatmap_data.head(25)
    
    # Plot
    fig, ax = plt.subplots(figsize=(14, 10))
    sns.heatmap(
        heatmap_data, 
        cmap='YlOrRd', 
        cbar_kws={'label': 'Enrolments per 1,000 Population'},
        linewidths=0.5,
        linecolor='white',
        ax=ax
    )
    ax.set_title(
        'State Enrolment Intensity (Normalized by Population)\n'
        'Top 25 States by Per-Capita Enrolment Rate',
        fontsize=13, fontweight='bold', pad=15
    )
    ax.set_xlabel('Month', fontsize=11, fontweight='bold')
    ax.set_ylabel('State', fontsize=11, fontweight='bold')
    
    # Format x-axis
    month_labels = [str(col).replace('2025-', '') for col in heatmap_data.columns]
    ax.set_xticklabels(month_labels, rotation=45, ha='right')
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, '09_normalized_state_intensity.png')
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()
    
    print(f"   ✓ Saved: {output_path}")
    print(f"   📊 Top 3 states by avg per-capita intensity:")
    avg_intensity = heatmap_data.mean(axis=1).sort_values(ascending=False)
    for i, (state, val) in enumerate(avg_intensity.head(3).items(), 1):
        print(f"      {i}. {state}: {val:.2f} per 1,000")

# ============================================================================
# ANALYSIS 2: BIVARIATE GINI VS CHILD SHARE
# ============================================================================
def create_gini_vs_child_share(df, concentration, output_dir):
    """
    Scatterplot: State Gini coefficient vs final child share.
    Tests correlation between spatial concentration and demographic targeting.
    """
    print("\n" + "="*60)
    print("ANALYSIS 2: GINI COEFFICIENT VS CHILD SHARE")
    print("="*60)
    
    # Get final month child share by state
    df['year_month'] = df['date'].dt.to_period('M')
    final_month = df['year_month'].max()
    
    final_shares = df[df['year_month'] == final_month].groupby('state').agg({
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum',
        'total_enrol': 'sum'
    }).reset_index()
    
    final_shares['child_share'] = (
        (final_shares['age_0_5'] + final_shares['age_5_17']) / 
        final_shares['total_enrol'] * 100
    )
    
   # Merge with Gini data
    plot_data = concentration.merge(final_shares[['state', 'child_share']], on='state')
    
    # Calculate correlation
    corr = plot_data['gini'].corr(plot_data['child_share'])
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Scatter with state labels
    scatter = ax.scatter(
        plot_data['gini_pincode'], 
        plot_data['child_share'],
        s=100, 
        alpha=0.6, 
        c=plot_data['child_share'],
        cmap='RdYlGn',
        edgecolors='black',
        linewidth=0.5
    )
    
    # Add state labels for outliers
    for _, row in plot_data.iterrows():
        if row['gini_pincode'] > 0.63 or row['child_share'] < 96:
            ax.annotate(
                row['state'], 
                (row['gini_pincode'], row['child_share']),
                fontsize=8, 
                alpha=0.7,
                xytext=(5, 5),
                textcoords='offset points'
            )
    
    # Add correlation line
    z = np.polyfit(plot_data['gini'], plot_data['child_share'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(plot_data['gini'].min(), plot_data['gini'].max(), 100)
    ax.plot(x_line, p(x_line), "r--", alpha=0.5, linewidth=2, label=f'Trend (r={corr:.3f})')
    
    # Styling
    ax.set_xlabel('Spatial Concentration (Gini Coefficient)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Child Share (%) in Final Month', fontsize=11, fontweight='bold')
    ax.set_title(
        'Spatial Equity vs Demographic Targeting\n'
        f'Correlation: {corr:.3f} ({"Positive" if corr > 0 else "Negative"})',
        fontsize=13, fontweight='bold', pad=15
    )
    ax.grid(alpha=0.3, linestyle='--')
    ax.legend()
    
    plt.colorbar(scatter, ax=ax, label='Child Share (%)')
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, '10_gini_vs_child_share.png')
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()
    
    print(f"   ✓ Saved: {output_path}")
    print(f"   📊 Correlation: {corr:.3f}")

# ============================================================================
# ANALYSIS 3: TEMPORAL ACCELERATION OF CHILD SHARE
# ============================================================================
def create_child_share_acceleration(df, output_dir):
    """
    Heatmap: Month-over-month change in child share by state.
    Identifies rapid vs gradual compositional shifts.
    """
    print("\n" + "="*60)
    print("ANALYSIS 3: TEMPORAL ACCELERATION OF CHILD SHARE")
    print("="*60)
    
    # Create state-month aggregates
    df['year_month'] = df['date'].dt.to_period('M')
    state_month = df.groupby(['state', 'year_month']).agg({
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'total_enrol': 'sum'
    }).reset_index()
    
    state_month['child_share'] = (
        (state_month['age_0_5'] + state_month['age_5_17']) / 
        state_month['total_enrol'] * 100
    )
    
    # Calculate month-over-month change
    state_month = state_month.sort_values(['state', 'year_month'])
    state_month['child_share_change'] = state_month.groupby('state')['child_share'].diff()
    
    # Pivot for heatmap (excluding first month which has no change)
    heatmap_data = state_month[state_month['child_share_change'].notna()].pivot(
        index='state',
        columns='year_month',
        values='child_share_change'
    )
    
    # Sort by maximum acceleration
    heatmap_data['max_accel'] = heatmap_data.max(axis=1)
    heatmap_data = heatmap_data.sort_values('max_accel', ascending=False).drop('max_accel', axis=1)
    
    # Take top 25 for visibility
    heatmap_data = heatmap_data.head(25)
    
    # Plot
    fig, ax = plt.subplots(figsize=(14, 10))
    sns.heatmap(
        heatmap_data,
        cmap='RdBu_r',
        center=0,
        cbar_kws={'label': 'Month-over-Month Change in Child Share (pp)'},
        linewidths=0.5,
        linecolor='white',
        ax=ax,
        vmin=-5, vmax=15
    )
    ax.set_title(
        'Temporal Acceleration of Child Share by State\n'
        'Month-over-Month Change (Percentage Points)',
        fontsize=13, fontweight='bold', pad=15
    )
    ax.set_xlabel('Month', fontsize=11, fontweight='bold')
    ax.set_ylabel('State (Sorted by Max Acceleration)', fontsize=11, fontweight='bold')
    
    # Format x-axis
    month_labels = [str(col).replace('2025-', '') for col in heatmap_data.columns]
    ax.set_xticklabels(month_labels, rotation=45, ha='right')
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, '11_child_share_acceleration.png')
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()
    
    print(f"   ✓ Saved: {output_path}")
    print(f"   📊 States with highest peak acceleration:")
    max_accel = heatmap_data.max(axis=1).sort_values(ascending=False)
    for i, (state, val) in enumerate(max_accel.head(3).items(), 1):
        print(f"      {i}. {state}: +{val:.1f} pp in single month")

# ============================================================================
# ANALYSIS 4: DISTRICT VOLATILITY VS INFRASTRUCTURE
# ============================================================================
def create_volatility_vs_infrastructure(volatility, clusters, output_dir):
    """
    Scatterplot: District volatility (CV) vs urbanization proxy.
    """
    print("\n" + "="*60)
    print("ANALYSIS 4: VOLATILITY VS INFRASTRUCTURE PROXY")
    print("="*60)
    
    # Merge volatility with cluster data
    plot_data = volatility.merge(
        clusters[['state', 'district', 'total_enrol', 'avg_monthly_enrol']],
        on=['state', 'district'],
        how='left'
    )
    
    # Use average monthly enrolment as infrastructure proxy
    plot_data = plot_data[plot_data['avg_monthly_enrol'] > 0].copy()
    
    # Calculate correlation
    corr = plot_data['cv'].corr(plot_data['avg_monthly_enrol'])
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Log scale scatter
    scatter = ax.scatter(
        plot_data['avg_monthly_enrol'],
        plot_data['cv'],
        s=50,
        alpha=0.5,
        c=plot_data['cv'],
        cmap='YlOrRd',
        edgecolors='black',
        linewidth=0.3
    )
    
    ax.set_xscale('log')
    ax.set_yscale('log')
    
    # Add trend line
    log_x = np.log10(plot_data['avg_monthly_enrol'])
    log_y = np.log10(plot_data['cv'])
    z = np.polyfit(log_x, log_y, 1)
    p = np.poly1d(z)
    x_line = np.logspace(
        np.log10(plot_data['avg_monthly_enrol'].min()),
        np.log10(plot_data['avg_monthly_enrol'].max()),
        100
    )
    y_line = 10 ** p(np.log10(x_line))
    ax.plot(x_line, y_line, "r--", alpha=0.5, linewidth=2, label=f'Trend (r={corr:.3f})')
    
    # Styling
    ax.set_xlabel('Average Monthly Enrolment (Infrastructure Proxy)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Coefficient of Variation (Volatility)', fontsize=11, fontweight='bold')
    ax.set_title(
        'District Enrolment Volatility vs Operational Capacity\n'
        f'Correlation: {corr:.3f}',
        fontsize=13, fontweight='bold', pad=15
    )
    ax.grid(alpha=0.3, linestyle='--', which='both')
    ax.legend()
    
    plt.colorbar(scatter, ax=ax, label='Volatility (CV)')
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, '12_volatility_vs_infrastructure.png')
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()
    
    print(f"   ✓ Saved: {output_path}")
    print(f"   📊 Correlation: {corr:.3f}")

# ============================================================================
# ANALYSIS 5: STATE-MONTH CAMPAIGN INTENSITY INDEX
# ============================================================================
def create_campaign_intensity_index(df, output_dir):
    """
    Heatmap: Ratio of current month to 3-month trailing average by state.
    """
    print("\n" + "="*60)
    print("ANALYSIS 5: CAMPAIGN INTENSITY INDEX")
    print("="*60)
    
    # Create state-month aggregates
    df['year_month'] = df['date'].dt.to_period('M')
    state_month = df.groupby(['state', 'year_month']).agg({
        'total_enrol': 'sum'
    }).reset_index()
    
    # Calculate 3-month rolling average
    state_month = state_month.sort_values(['state', 'year_month'])
    state_month['rolling_3m_avg'] = state_month.groupby('state')['total_enrol'].transform(
        lambda x: x.rolling(window=3, min_periods=1).mean().shift(1)
    )
    
    # Calculate intensity index
    state_month['intensity_index'] = (
        state_month['total_enrol'] / state_month['rolling_3m_avg']
    )
    
    # Cap at reasonable values
    state_month['intensity_index'] = state_month['intensity_index'].clip(upper=5.0)
    
    # Pivot for heatmap
    heatmap_data = state_month.pivot(
        index='state',
        columns='year_month',
        values='intensity_index'
    )
    
    # Sort by maximum intensity
    heatmap_data['max_intensity'] = heatmap_data.max(axis=1)
    heatmap_data = heatmap_data.sort_values('max_intensity', ascending=False).drop('max_intensity', axis=1)
    
    # Take top 25
    heatmap_data = heatmap_data.head(25)
    
    # Plot
    fig, ax = plt.subplots(figsize=(14, 10))
    sns.heatmap(
        heatmap_data,
        cmap='YlOrRd',
        cbar_kws={'label': 'Campaign Intensity Index'},
        linewidths=0.5,
        linecolor='white',
        ax=ax,
        vmin=0, vmax=4.0
    )
    
    ax.set_title(
        'Campaign Intensity Index by State × Month\n'
        'Values > 2.0 indicate surge periods',
        fontsize=13, fontweight='bold', pad=15
    )
    ax.set_xlabel('Month', fontsize=11, fontweight='bold')
    ax.set_ylabel('State', fontsize=11, fontweight='bold')
    
    # Format x-axis
    month_labels = [str(col).replace('2025-', '') for col in heatmap_data.columns]
    ax.set_xticklabels(month_labels, rotation=45, ha='right')
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, '13_campaign_intensity_index.png')
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()
    
    print(f"   ✓ Saved: {output_path}")

# ============================================================================
# ANALYSIS 6: COHORT-SPECIFIC ABSOLUTE ENROLMENT RATES
# ============================================================================
def create_cohort_absolute_trajectories(df, output_dir):
    """
    Line chart: Absolute monthly enrolments for each age cohort.
    """
    print("\n" + "="*60)
    print("ANALYSIS 6: COHORT-SPECIFIC ABSOLUTE TRAJECTORIES")
    print("="*60)
    
    # Create national monthly aggregates
    df['year_month'] = df['date'].dt.to_period('M')
    national_month = df.groupby('year_month').agg({
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum',
        'total_enrol': 'sum'
    }).reset_index()
    
    # Convert to timestamp
    national_month['month'] = national_month['year_month'].dt.to_timestamp()
    
    # Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), 
                                     gridspec_kw={'height_ratios': [2, 1]})
    
    # Panel 1: Absolute enrolments
    ax1.plot(national_month['month'], national_month['age_0_5'], 
             linewidth=3, marker='o', label='0-5 years (Infants)', color='#e74c3c')
    ax1.plot(national_month['month'], national_month['age_5_17'], 
             linewidth=3, marker='s', label='5-17 years (School-age)', color='#3498db')
    ax1.plot(national_month['month'], national_month['age_18_greater'], 
             linewidth=3, marker='^', label='18+ years (Adults)', color='#2ecc71')
    
    ax1.set_ylabel('Monthly Enrolments (Absolute)', fontsize=11, fontweight='bold')
    ax1.set_title(
        'Cohort-Specific Enrolment Trajectories (Absolute Volumes)\n'
        'Rising child shares reflect both increased child AND decreased adult activity',
        fontsize=13, fontweight='bold', pad=15
    )
    ax1.legend(loc='upper left', frameon=True, shadow=True)
    ax1.grid(alpha=0.3, linestyle='--')
    ax1.ticklabel_format(axis='y', style='plain')
    
    # Panel 2: Shares
    national_month['share_0_5'] = national_month['age_0_5'] / national_month['total_enrol'] * 100
    national_month['share_5_17'] = national_month['age_5_17'] / national_month['total_enrol'] * 100
    national_month['share_18_plus'] = national_month['age_18_greater'] / national_month['total_enrol'] * 100
    
    ax2.plot(national_month['month'], national_month['share_0_5'], 
             linewidth=2, marker='o', label='0-5 years', color='#e74c3c', alpha=0.7)
    ax2.plot(national_month['month'], national_month['share_5_17'], 
             linewidth=2, marker='s', label='5-17 years', color='#3498db', alpha=0.7)
    ax2.plot(national_month['month'], national_month['share_18_plus'], 
             linewidth=2, marker='^', label='18+ years', color='#2ecc71', alpha=0.7)
    
    ax2.set_xlabel('Month', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Share of Total (%)', fontsize=11, fontweight='bold')
    ax2.set_title('Compositional Shares (for comparison)', fontsize=11, style='italic')
    ax2.legend(loc='upper right', frameon=True, shadow=True)
    ax2.grid(alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, '14_cohort_absolute_trajectories.png')
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()
    
    print(f"   ✓ Saved: {output_path}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    """Execute all missing analyses."""
    print("\n" + "="*70)
    print(" "*10 + "UIDAI ENROLMENT FORENSIC AUDIT")
    print(" "*15 + "Missing Analyses Generator")
    print("="*70)
    
    setup_plots()
    
    # Load data
    df, concentration, volatility, clusters = load_data()
    
    # Generate analyses
    print("\n" + "🎯"*30)
    create_normalized_state_intensity(df, NEW_PLOTS_DIR)
    
    print("\n" + "🎯"*30)
    create_gini_vs_child_share(df, concentration, NEW_PLOTS_DIR)
    
    print("\n" + "🎯"*30)
    create_child_share_acceleration(df, NEW_PLOTS_DIR)
    
    print("\n" + "🎯"*30)
    create_volatility_vs_infrastructure(volatility, clusters, NEW_PLOTS_DIR)
    
    print("\n" + "🎯"*30)
    create_campaign_intensity_index(df, NEW_PLOTS_DIR)
    
    print("\n" + "🎯"*30)
    create_cohort_absolute_trajectories(df, NEW_PLOTS_DIR)
    
    # Final summary
    print("\n" + "="*70)
    print("✅ ALL 6 MISSING ANALYSES COMPLETED")
    print("="*70)
    print(f"\n📁 Output directory: {NEW_PLOTS_DIR}")
    print("\n📊 Generated visualizations:")
    print("   1. 09_normalized_state_intensity.png")
    print("   2. 10_gini_vs_child_share.png")
    print("   3. 11_child_share_acceleration.png")
    print("   4. 12_volatility_vs_infrastructure.png")
    print("   5. 13_campaign_intensity_index.png")
    print("   6. 14_cohort_absolute_trajectories.png")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
