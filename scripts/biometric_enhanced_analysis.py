#!/usr/bin/env python3
"""
UIDAI Data Hackathon 2026 - Enhanced Biometric Analysis
Missing High-Impact Analyses from Forensic Audit

Implements:
1. Three-Age-Category Compositional Time Series (with 0-5 absence note)
2. State Minor Share vs Population Age Structure (placeholder)
3. District Urbanization vs Minor Share Correlation (placeholder)
4. Temporal Stability of Minor Share (CV)
5. Weekend vs Weekday Minor Share Comparison

Author: UIDAI Hackathon Team - Enhanced Edition
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import glob
from datetime import datetime
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(BASE_DIR, "data", "api_data_aadhar_biometric")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "biometric_analysis")
PLOTS_DIR = os.path.join(OUTPUT_DIR, "plots")

# State name normalization
STATE_FIX = {
    "Orissa": "Odisha",
    "Pondicherry": "Puducherry",
    "Andaman & Nicobar Islands": "Andaman And Nicobar Islands",
    "J & K": "Jammu And Kashmir",
    "Jammu & Kashmir": "Jammu And Kashmir",
    "Dadra & Nagar Haveli": "Dadra And Nagar Haveli",
    "Daman & Diu": "Daman And Diu",
    "Telengana": "Telangana",
}

# ============================================================================
# DATA LOADING & PREPARATION
# ============================================================================
def load_and_prepare_data():
    """Load and prepare biometric data."""
    print("\n" + "="*70)
    print("ENHANCED ANALYSIS - DATA LOADING")
    print("="*70)
    
    # Load all CSV files
    files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    dfs = []
    
    for f in files:
        df = pd.read_csv(f)
        dfs.append(df)
    
    data = pd.concat(dfs, ignore_index=True)
    print(f"  ✓ Loaded {len(data):,} records from {len(files)} files")
    
    # Parse dates
    data['date'] = pd.to_datetime(data['date'], format='%d-%m-%Y', errors='coerce')
    data['year'] = data['date'].dt.year
    data['month'] = data['date'].dt.month
    data['month_name'] = data['date'].dt.month_name()
    data['day_of_week'] = data['date'].dt.day_name()
    data['is_weekend'] = data['day_of_week'].isin(['Saturday', 'Sunday'])
    
    # Standardize names
    data['state'] = data['state'].astype(str).str.strip().str.title()
    data['state'] = data['state'].replace(STATE_FIX)
    data['district'] = data['district'].astype(str).str.strip().str.title()
    
    # Calculate metrics
    data['total_bio'] = data['bio_age_5_17'] + data['bio_age_17_']
    data['minor_share'] = np.where(
        data['total_bio'] > 0,
        data['bio_age_5_17'] / data['total_bio'],
        0
    )
    
    print(f"  ✓ Date range: {data['date'].min().date()} to {data['date'].max().date()}")
    print(f"  ✓ States: {data['state'].nunique()}, Districts: {data['district'].nunique()}")
    
    return data

# ============================================================================
# ANALYSIS 1: THREE-AGE-CATEGORY TIME SERIES (WITH 0-5 ABSENCE NOTE)
# ============================================================================
def analysis_1_age_composition_with_note(df, output_dir):
    """
    Reproduce national daily time series with explicit 0-5 absence annotation.
    Shows three visual layers: 0% (gray, "NO DATA"), 5-17, 17+
    """
    print("\n" + "="*70)
    print("ANALYSIS 1: Three-Age-Category Composition (with 0-5 absence note)")
    print("="*70)
    
    # Aggregate to national daily level
    national_date = df.groupby('date').agg({
        'bio_age_5_17': 'sum',
        'bio_age_17_': 'sum',
        'total_bio': 'sum'
    }).reset_index()
    
    national_date['minor_share'] = np.where(
        national_date['total_bio'] > 0,
        national_date['bio_age_5_17'] / national_date['total_bio'],
        0
    )
    
    # Create visualization
    fig, ax = plt.subplots(figsize=(16, 8))
    
    # Stack plot with three conceptual layers
    # Layer 1: 0-5 (represented as 0, with gray shading for visual presence)
    # Layer 2: 5-17 (actual data)
    # Layer 3: 17+ (actual data)
    
    ax.stackplot(national_date['date'], 
                 national_date['bio_age_5_17'], 
                 national_date['bio_age_17_'],
                 labels=['Age 5-17 (Minor)', 'Age 17+ (Adult)'],
                 colors=['#FF9999', '#FFD700'],
                 alpha=0.85)
    
    # Add zero baseline with annotation for 0-5
    ax.axhline(y=0, color='gray', linewidth=3, alpha=0.3)
    
    # Title and labels
    ax.set_title('National Daily Biometric Updates: Age Group Composition Over Time',
                 fontweight='bold', fontsize=16, pad=20)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Daily Biometric Updates', fontsize=12)
    
    # Legend
    legend = ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
    
    # Critical annotation about 0-5 absence
    ax.text(0.02, 0.98, 
            '⚠️  CRITICAL DATA LIMITATION:\n' +
            'Age 0-5 group NOT INCLUDED in source data\n' +
            '(only 5-17 and 17+ available)\n\n' +
            'Gray baseline represents 0% for age 0-5',
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8, edgecolor='red', linewidth=2))
    
    # Format x-axis
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, '09_age_composition_note.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Saved: 09_age_composition_note.png")
    print(f"  ✓ Annotation clearly states 0-5 data absence")
    
    return national_date

# ============================================================================
# ANALYSIS 2: STATE MINOR SHARE VS POPULATION AGE STRUCTURE (PLACEHOLDER)
# ============================================================================
def analysis_2_state_demographics_placeholder(df, output_dir):
    """
    Placeholder visualization for state-level minor share vs population structure.
    Uses mock Census data to demonstrate the concept.
    """
    print("\n" + "="*70)
    print("ANALYSIS 2: State Minor Share vs Population Age Structure (PLACEHOLDER)")
    print("="*70)
    
    # Calculate actual minor share by state
    state_minor = df.groupby('state').agg({
        'bio_age_5_17': 'sum',
        'bio_age_17_': 'sum',
        'total_bio': 'sum'
    }).reset_index()
    state_minor['minor_share'] = state_minor['bio_age_5_17'] / state_minor['total_bio']
    state_minor = state_minor[state_minor['total_bio'] > 10000]  # Filter low volume
    
    # MOCK DATA: Generate placeholder population age structure
    # In reality, this would come from Census data
    np.random.seed(42)
    state_minor['population_5_17_pct'] = np.random.uniform(0.20, 0.35, len(state_minor))
    
    # Create scatter plot
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Scatter points
    scatter = ax.scatter(state_minor['population_5_17_pct'], 
                        state_minor['minor_share'],
                        s=state_minor['total_bio'] / 1000,  # Size by volume
                        alpha=0.6,
                        c=np.arange(len(state_minor)),
                        cmap='viridis',
                        edgecolors='black',
                        linewidth=0.5)
    
    # 45-degree equality line
    ax.plot([0.15, 0.40], [0.15, 0.40], 'r--', linewidth=2, alpha=0.7,
            label='Equality line (update share = population share)')
    
    # Labels for select points
    for idx, row in state_minor.head(10).iterrows():
        ax.annotate(row['state'][:10], 
                   (row['population_5_17_pct'], row['minor_share']),
                   fontsize=8, alpha=0.7)
    
    ax.set_xlabel('State Population Aged 5-17 (%) [MOCK CENSUS DATA]', fontsize=12, fontweight='bold')
    ax.set_ylabel('Minor Share in Biometric Updates (%) [ACTUAL DATA]', fontsize=12, fontweight='bold')
    ax.set_title('State-Level Minor Share vs Population Age Structure\n(PLACEHOLDER - REQUIRES ACTUAL CENSUS DATA)',
                 fontsize=14, fontweight='bold', color='red')
    
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Add prominent warning
    ax.text(0.5, 0.05,
            '🚨 THIS IS A PLACEHOLDER VISUALIZATION 🚨\n' +
            'X-axis uses MOCK DATA (random values)\n' +
            'To complete: provide Census state-level population age structure',
            transform=ax.transAxes,
            fontsize=11,
            ha='center',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.9, edgecolor='red', linewidth=3))
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, '10_state_demographics_placeholder.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Saved: 10_state_demographics_placeholder.png")
    print(f"  ⚠️  WARNING: Uses mock Census data - requires real data to complete")
    
# ============================================================================
# ANALYSIS 3: DISTRICT URBANIZATION VS MINOR SHARE (PLACEHOLDER)
# ============================================================================
def analysis_3_urbanization_correlation_placeholder(df, output_dir):
    """
    Placeholder for district urbanization vs minor share correlation.
    Uses mock urbanization data to demonstrate concept.
    """
    print("\n" + "="*70)
    print("ANALYSIS 3: District Urbanization vs Minor Share (PLACEHOLDER)")
    print("="*70)
    
    # Calculate district minor share
    district_agg = df.groupby(['state', 'district']).agg({
        'bio_age_5_17': 'sum',
        'bio_age_17_': 'sum',
        'total_bio': 'sum'
    }).reset_index()
    district_agg['minor_share'] = district_agg['bio_age_5_17'] / district_agg['total_bio']
    district_agg = district_agg[district_agg['total_bio'] > 1000]  # Filter
    
    # MOCK DATA: Generate placeholder urbanization percentages
    np.random.seed(43)
    district_agg['urbanization_pct'] = np.random.uniform(10, 90, len(district_agg))
    
    # Create scatter with regression
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Scatter points colored by state
    states = district_agg['state'].unique()[:10]  # Top 10 states
    colors = plt.cm.tab10(np.linspace(0, 1, len(states)))
    
    for state, color in zip(states, colors):
        mask = district_agg['state'] == state
        ax.scatter(district_agg[mask]['urbanization_pct'],
                  district_agg[mask]['minor_share'],
                  label=state[:15],
                  alpha=0.6,
                  s=50,
                  color=color)
    
    # Regression line (with mock data)
    x = district_agg['urbanization_pct'].values
    y = district_agg['minor_share'].values
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    line_x = np.array([x.min(), x.max()])
    line_y = slope * line_x + intercept
    
    ax.plot(line_x, line_y, 'r--', linewidth=2, alpha=0.8,
            label=f'Regression: r={r_value:.3f}, R²={r_value**2:.3f}, p={p_value:.3e}')
    
    # Confidence band
    conf_interval = 1.96 * std_err * np.sqrt(1/len(x) + (line_x - x.mean())**2 / ((x - x.mean())**2).sum())
    ax.fill_between(line_x, line_y - conf_interval, line_y + conf_interval, 
                     alpha=0.2, color='red')
    
    ax.set_xlabel('District Urbanization (%) [MOCK CENSUS DATA]', fontsize=12, fontweight='bold')
    ax.set_ylabel('District Minor Share [ACTUAL DATA]', fontsize=12, fontweight='bold')
    ax.set_title('District-Level Correlation: Minor Share × Urbanization Rate\n(PLACEHOLDER - REQUIRES ACTUAL CENSUS DATA)',
                 fontsize=14, fontweight='bold', color='red')
    
    ax.legend(loc='best', fontsize=9, ncol=2)
    ax.grid(True, alpha=0.3)
    
    # Warning annotation
    ax.text(0.5, 0.05,
            '🚨 THIS IS A PLACEHOLDER VISUALIZATION 🚨\n' +
            'X-axis uses MOCK DATA (random values)\n' +
            'To complete: provide Census district-level urbanization rates',
            transform=ax.transAxes,
            fontsize=11,
            ha='center',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.9, edgecolor='red', linewidth=3))
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, '11_urbanization_correlation_placeholder.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Saved: 11_urbanization_correlation_placeholder.png")
    print(f"  ⚠️  WARNING: Uses mock Census data - requires real data to complete")

# ============================================================================
# ANALYSIS 4: TEMPORAL STABILITY OF MINOR SHARE (CV)
# ============================================================================
def analysis_4_minor_share_volatility(df, output_dir):
    """
    Calculate coefficient of variation for minor share (compositional volatility)
    distinct from volume volatility.
    """
    print("\n" + "="*70)
    print("ANALYSIS 4: Temporal Stability of Minor Share (Compositional CV)")
    print("="*70)
    
    # Calculate monthly minor share per district
    district_month = df.groupby(['state', 'district', 'year', 'month']).agg({
        'bio_age_5_17': 'sum',
        'bio_age_17_': 'sum',
        'total_bio': 'sum'
    }).reset_index()
    
    district_month['minor_share'] = np.where(
        district_month['total_bio'] > 100,  # Filter low volume months
        district_month['bio_age_5_17'] / district_month['total_bio'],
        np.nan
    )
    
    # Calculate CV per district
    composition_cv = district_month.groupby(['state', 'district']).agg({
        'minor_share': ['mean', 'std', 'count']
    }).reset_index()
    
    composition_cv.columns = ['state', 'district', 'avg_minor_share', 'std_minor_share', 'month_count']
    
    # Filter: need at least 3 months of data
    composition_cv = composition_cv[composition_cv['month_count'] >= 3]
    
    # Calculate CV
    composition_cv['composition_cv'] = np.where(
        composition_cv['avg_minor_share'] > 0,
        composition_cv['std_minor_share'] / composition_cv['avg_minor_share'],
        0
    )
    
    # Remove outliers
    composition_cv = composition_cv[composition_cv['composition_cv'] < 2]  # Cap at 200%
    
    print(f"  ✓ Analyzed {len(composition_cv)} districts")
    print(f"  ✓ Median compositional CV: {composition_cv['composition_cv'].median():.3f}")
    print(f"  ✓ Mean compositional CV: {composition_cv['composition_cv'].mean():.3f}")
    
    # Create visualization
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # Histogram
    axes[0].hist(composition_cv['composition_cv'], bins=50, color='teal', alpha=0.7, edgecolor='black')
    axes[0].axvline(composition_cv['composition_cv'].median(), color='red', linestyle='--', 
                   linewidth=2, label=f'Median: {composition_cv["composition_cv"].median():.3f}')
    axes[0].set_xlabel('Coefficient of Variation (Minor Share)', fontsize=12)
    axes[0].set_ylabel('Number of Districts', fontsize=12)
    axes[0].set_title('Distribution of Minor Share Volatility Across Districts',
                     fontweight='bold', fontsize=13)
    axes[0].legend(fontsize=11)
    axes[0].grid(True, alpha=0.3)
    
    # Top 20 most volatile
    top_volatile = composition_cv.nlargest(20, 'composition_cv')
    top_volatile['label'] = top_volatile['district'] + '\n(' + top_volatile['state'].str[:10] + ')'
    
    axes[1].barh(range(len(top_volatile)), top_volatile['composition_cv'], color='crimson', alpha=0.8)
    axes[1].set_yticks(range(len(top_volatile)))
    axes[1].set_yticklabels(top_volatile['label'], fontsize=9)
    axes[1].set_xlabel('Compositional CV (higher = more unstable)', fontsize=12)
    axes[1].set_title('Top 20 Most Volatile Districts (Minor Share Composition)',
                     fontweight='bold', fontsize=13)
    axes[1].grid(True, alpha=0.3, axis='x')
    
    # Add note
    fig.text(0.5, 0.02,
             'Note: Compositional CV measures variability in minor share (%), distinct from volume volatility.\n' +
             'High CV indicates district alternates between child-focused and adult-focused campaigns.',
             ha='center', fontsize=10, style='italic',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    output_path = os.path.join(output_dir, '12_minor_share_volatility.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Saved: 12_minor_share_volatility.png")
    
    return composition_cv

# ============================================================================
# ANALYSIS 5: WEEKEND VS WEEKDAY MINOR SHARE
# ============================================================================
def analysis_5_weekend_weekday_comparison(df, output_dir):
    """
    Compare minor share on weekends vs weekdays at district level.
    """
    print("\n" + "="*70)
    print("ANALYSIS 5: Weekend vs Weekday Minor Share Comparison")
    print("="*70)
    
    # Separate weekend and weekday
    df_weekend = df[df['is_weekend'] == True]
    df_weekday = df[df['is_weekend'] == False]
    
    # Calculate minor share by district for each
    weekend_minor = df_weekend.groupby(['state', 'district']).agg({
        'bio_age_5_17': 'sum',
        'bio_age_17_': 'sum',
        'total_bio': 'sum'
    }).reset_index()
    weekend_minor['weekend_minor_share'] = weekend_minor['bio_age_5_17'] / weekend_minor['total_bio']
    
    weekday_minor = df_weekday.groupby(['state', 'district']).agg({
        'bio_age_5_17': 'sum',
        'bio_age_17_': 'sum',
        'total_bio': 'sum'
    }).reset_index()
    weekday_minor['weekday_minor_share'] = weekday_minor['bio_age_5_17'] / weekday_minor['total_bio']
    
    # Merge
    comparison = weekend_minor[['state', 'district', 'weekend_minor_share']].merge(
        weekday_minor[['state', 'district', 'weekday_minor_share']],
        on=['state', 'district'],
        how='inner'
    )
    
    # Merge with total volume for sizing
    district_totals = df.groupby(['state', 'district'])['total_bio'].sum().reset_index()
    comparison = comparison.merge(district_totals, on=['state', 'district'])
    
    # Filter: at least 1000 total updates
    comparison = comparison[comparison['total_bio'] > 1000]
    
    print(f"  ✓ Analyzed {len(comparison)} districts")
    
    # Classify quadrants
    def classify_quadrant(row):
        if row['weekday_minor_share'] >= 0.5 and row['weekend_minor_share'] >= 0.5:
            return 'High Both'
        elif row['weekday_minor_share'] >= 0.5 and row['weekend_minor_share'] < 0.5:
            return 'High Weekday, Low Weekend'
        elif row['weekday_minor_share'] < 0.5 and row['weekend_minor_share'] >= 0.5:
            return 'Low Weekday, High Weekend'
        else:
            return 'Low Both'
    
    comparison['quadrant'] = comparison.apply(classify_quadrant, axis=1)
    
    # Visualization
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # Color by quadrant
    colors_map = {
        'High Both': 'green',
        'High Weekday, Low Weekend': 'blue',
        'Low Weekday, High Weekend': 'orange',
        'Low Both': 'red'
    }
    
    for quadrant, color in colors_map.items():
        mask = comparison['quadrant'] == quadrant
        ax.scatter(comparison[mask]['weekday_minor_share'],
                  comparison[mask]['weekend_minor_share'],
                  c=color,
                  label=f'{quadrant} (n={mask.sum()})',
                  alpha=0.6,
                  s=comparison[mask]['total_bio'] / 500,
                  edgecolors='black',
                  linewidth=0.3)
    
    # 45-degree equality line
    ax.plot([0, 1], [0, 1], 'k--', linewidth=2, alpha=0.5, 
            label='Equality (weekend = weekday)')
    
    # Reference lines at 50%
    ax.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5)
    ax.axvline(x=0.5, color='gray', linestyle=':', alpha=0.5)
    
    ax.set_xlabel('Weekday Minor Share', fontsize=13, fontweight='bold')
    ax.set_ylabel('Weekend Minor Share', fontsize=13, fontweight='bold')
    ax.set_title('Weekend vs Weekday Minor Share by District\n(Bubble size = Total Update Volume)',
                 fontsize=14, fontweight='bold')
    
    ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    # Add interpretation note
    ax.text(0.98, 0.02,
            'Interpretation:\n' +
            '• Points above line: More minors on weekends\n' +
            '• Points below line: More minors on weekdays\n' +
            '• Points on line: Same pattern both periods',
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='bottom',
            horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, '13_weekend_weekday_comparison.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Saved: 13_weekend_weekday_comparison.png")
    print(f"\n  📊 Quadrant Distribution:")
    for quadrant in colors_map.keys():
        count = (comparison['quadrant'] == quadrant).sum()
        pct = count / len(comparison) * 100
        print(f"    {quadrant}: {count} districts ({pct:.1f}%)")
    
    return comparison

# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    print("="*70)
    print("UIDAI DATA HACKATHON 2026 - ENHANCED BIOMETRIC ANALYSIS")
    print("Missing High-Impact Analyses from Forensic Audit")
    print("="*70)
    
    # Create output directories
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PLOTS_DIR, exist_ok=True)
    
    # Load data
    df = load_and_prepare_data()
    
    # Run all 5 analyses
    print("\n" + "="*70)
    print("RUNNING 5 ENHANCED ANALYSES")
    print("="*70)
    
    analysis_1_age_composition_with_note(df, PLOTS_DIR)
    analysis_2_state_demographics_placeholder(df, PLOTS_DIR)
    analysis_3_urbanization_correlation_placeholder(df, PLOTS_DIR)
    composition_cv = analysis_4_minor_share_volatility(df, PLOTS_DIR)
    weekend_comparison = analysis_5_weekend_weekday_comparison(df, PLOTS_DIR)
    
    # Export results
    print("\n" + "="*70)
    print("EXPORTING ANALYTICAL RESULTS")
    print("="*70)
    
    composition_cv.to_csv(os.path.join(OUTPUT_DIR, 'minor_share_volatility.csv'), index=False)
    print(f"  ✓ Saved: minor_share_volatility.csv")
    
    weekend_comparison.to_csv(os.path.join(OUTPUT_DIR, 'weekend_weekday_comparison.csv'), index=False)
    print(f"  ✓ Saved: weekend_weekday_comparison.csv")
    
    print("\n" + "="*70)
    print("✅ ENHANCED ANALYSIS COMPLETE")
    print("="*70)
    print(f"\n  Generated 5 new visualizations:")
    print(f"    • 09_age_composition_note.png")
    print(f"    • 10_state_demographics_placeholder.png")
    print(f"    • 11_urbanization_correlation_placeholder.png")
    print(f"    • 12_minor_share_volatility.png")
    print(f"    • 13_weekend_weekday_comparison.png")
    print(f"\n  All outputs saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
