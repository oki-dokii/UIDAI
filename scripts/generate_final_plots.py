#!/usr/bin/env python3
"""
UIDAI Datathon 2026 - Final Presentation Plots
Generates publication-quality visualizations for top 5 insights

Insights covered:
1. System Shift (21.9× Update-to-Enrolment Ratio)
2. Invisible Economy (Weekend Update Patterns)
3. Monsoon Migration (Seasonal Bimodal Patterns) - HERO INSIGHT
4. Healthcare Deserts (Infant Enrolment Gaps)
5. Digital Divide (Bio/Demo Ratio)

Author: UIDAI Datathon Team
Date: January 18, 2026
"""

import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

# Directories - Using relative paths for portability
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)  # Parent directory (UIDAI/)
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_DIR_ENROL = os.path.join(DATA_DIR, "api_data_aadhar_enrolment")
DATA_DIR_BIO = os.path.join(DATA_DIR, "api_data_aadhar_biometric")
DATA_DIR_DEMO = os.path.join(DATA_DIR, "api_data_aadhar_demographic")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "plots_final")

# Visual theme
sns.set_style("whitegrid")
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e', 
    'accent': '#2ca02c',
    'warning': '#d62728',
    'neutral': '#7f7f7f'
}

plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9

# ============================================================================
# DATA LOADING
# ============================================================================

def load_dataset(directory, name):
    """Load all CSVs from a directory and concatenate."""
    print(f"Loading {name} data from {directory}/...")
    files = sorted(glob.glob(f'{directory}/*.csv'))
    if not files:
        print(f"  WARNING: No files found in {directory}/")
        return pd.DataFrame()
    
    dfs = []
    for file in files:
        try:
            df = pd.read_csv(file)
            dfs.append(df)
        except Exception as e:
            print(f"  ERROR loading {file}: {e}")
    
    if not dfs:
        return pd.DataFrame()
    
    combined = pd.concat(dfs, ignore_index=True)
    print(f"  Loaded {len(combined):,} records from {len(files)} files")
    return combined

def preprocess_data(df, name):
    """Clean and prepare dataset."""
    if df.empty:
        return df
    
    # Parse dates
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
    df = df.dropna(subset=['date'])
    
    # Extract time components
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['dayofweek'] = df['date'].dt.dayofweek  # 0=Monday, 6=Sunday
    df['is_weekend'] = df['dayofweek'].isin([5, 6])
    
    # Clean state names
    df['state'] = df['state'].str.strip().str.title()
    df['district'] = df['district'].str.strip().str.title()
    
    print(f"  Preprocessed {name}: {len(df):,} valid records")
    return df

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_output_dir():
    """Create output directory if it doesn't exist."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}/")

def save_plot(filename, tight=True):
    """Save plot with consistent settings."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if tight:
        plt.tight_layout()
    plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"  Saved: {filepath}")
    plt.close()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("="*80)
    print("UIDAI DATATHON 2026 - FINAL PRESENTATION PLOTS")
    print("="*80)
    print()
    
    create_output_dir()
    
    # Load datasets
    print("STEP 1: Loading Data")
    print("-"*80)
    enrol_df = load_dataset(DATA_DIR_ENROL, 'Enrolment')
    bio_df = load_dataset(DATA_DIR_BIO, 'Biometric')
    demo_df = load_dataset(DATA_DIR_DEMO, 'Demographic')
    print()
    
    # Preprocess
    print("STEP 2: Preprocessing")
    print("-"*80)
    enrol_df = preprocess_data(enrol_df, 'Enrolment')
    bio_df = preprocess_data(bio_df, 'Biometric')
    demo_df = preprocess_data(demo_df, 'Demographic')
    print()
    
    # Validate
    if enrol_df.empty or bio_df.empty or demo_df.empty:
        print("ERROR: One or more datasets failed to load. Exiting.")
        return
    
    # ========================================================================
    # PLOT 1: SYSTEM SHIFT - 21.9× Update-to-Enrolment Ratio
    # ========================================================================
    print("STEP 3: Generating Plots")
    print("-"*80)
    print("Plot 1: System Shift (Update-to-Enrolment Ratio)")
    
    # Aggregate by date
    enrol_daily = enrol_df.groupby('date').agg({
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum'
    }).reset_index()
    enrol_daily['total_enrolments'] = (enrol_daily['age_0_5'] + 
                                        enrol_daily['age_5_17'] + 
                                        enrol_daily['age_18_greater'])
    
    bio_daily = bio_df.groupby('date').agg({
        'bio_age_5_17': 'sum',
        'bio_age_17_': 'sum'
    }).reset_index()
    bio_daily['total_bio'] = bio_daily['bio_age_5_17'] + bio_daily['bio_age_17_']
    
    demo_daily = demo_df.groupby('date').agg({
        'demo_age_5_17': 'sum',
        'demo_age_17_': 'sum'
    }).reset_index()
    demo_daily['total_demo'] = demo_daily['demo_age_5_17'] + demo_daily['demo_age_17_']
    
    # Merge
    national_daily = enrol_daily[['date', 'total_enrolments']].merge(
        bio_daily[['date', 'total_bio']], on='date', how='outer'
    ).merge(
        demo_daily[['date', 'total_demo']], on='date', how='outer'
    ).fillna(0)
    
    national_daily['total_updates'] = national_daily['total_bio'] + national_daily['total_demo']
    national_daily = national_daily.sort_values('date')
    
    # Plot
    fig, ax1 = plt.subplots(figsize=(14, 6))
    
    ax1.plot(national_daily['date'], national_daily['total_enrolments'], 
             color=COLORS['primary'], linewidth=2, label='Total Enrolments')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Enrolments', color=COLORS['primary'])
    ax1.tick_params(axis='y', labelcolor=COLORS['primary'])
    ax1.grid(True, alpha=0.3)
    
    ax2 = ax1.twinx()
    ax2.plot(national_daily['date'], national_daily['total_updates'], 
             color=COLORS['secondary'], linewidth=2, label='Total Updates')
    ax2.set_ylabel('Updates', color=COLORS['secondary'])
    ax2.tick_params(axis='y', labelcolor=COLORS['secondary'])
    
    # Calculate ratio
    total_enrol = national_daily['total_enrolments'].sum()
    total_updates = national_daily['total_updates'].sum()
    ratio = total_updates / total_enrol if total_enrol > 0 else 0
    
    plt.title(f'System Shift: {ratio:.1f}× More Updates Than Enrolments\nNational Time Series (Mar 2025 - Jan 2026)', 
              fontsize=14, fontweight='bold', pad=20)
    
    # Add ratio annotation
    ax1.annotate(f'21.9× Ratio', xy=(0.98, 0.95), xycoords='axes fraction',
                ha='right', va='top', fontsize=16, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))
    
    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    save_plot('01_system_shift_ratio.png')
    
    # ========================================================================
    # PLOT 2: INVISIBLE ECONOMY - Weekend Update Patterns
    # ========================================================================
    print("Plot 2: Invisible Economy (Weekend Patterns)")
    
    # Aggregate demographic updates by day of week
    demo_dow = demo_df.groupby(['dayofweek', 'is_weekend']).agg({
        'demo_age_5_17': 'sum',
        'demo_age_17_': 'sum'
    }).reset_index()
    demo_dow['total_demo'] = demo_dow['demo_age_5_17'] + demo_dow['demo_age_17_']
    
    # Day names
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    demo_dow['day_name'] = demo_dow['dayofweek'].apply(lambda x: day_names[x])
    
    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Subplot 1: By day of week
    colors_dow = [COLORS['secondary'] if w else COLORS['primary'] 
                  for w in demo_dow['is_weekend']]
    ax1.bar(demo_dow['day_name'], demo_dow['total_demo'], color=colors_dow, alpha=0.8)
    ax1.set_xlabel('Day of Week')
    ax1.set_ylabel('Total Demographic Updates')
    ax1.set_title('Demographic Updates by Day of Week\n(Orange = Weekend)', fontweight='bold')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(axis='y', alpha=0.3)
    
    # Subplot 2: Weekend vs Weekday comparison
    weekend_total = demo_dow[demo_dow['is_weekend']]['total_demo'].sum()
    weekday_total = demo_dow[~demo_dow['is_weekend']]['total_demo'].sum()
    
    weekend_days = demo_dow[demo_dow['is_weekend']]['dayofweek'].nunique()
    weekday_days = demo_dow[~demo_dow['is_weekend']]['dayofweek'].nunique()
    
    weekend_avg = weekend_total / weekend_days if weekend_days > 0 else 0
    weekday_avg = weekday_total / weekday_days if weekday_days > 0 else 0
    
    pct_diff = ((weekend_avg - weekday_avg) / weekday_avg * 100) if weekday_avg > 0 else 0
    
    ax2.bar(['Weekday\nAverage', 'Weekend\nAverage'], [weekday_avg, weekend_avg],
            color=[COLORS['primary'], COLORS['secondary']], alpha=0.8, width=0.6)
    ax2.set_ylabel('Average Updates per Day')
    ax2.set_title(f'Weekend Spike: +{pct_diff:.1f}%\nInformal Employment Signal', fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for i, v in enumerate([weekday_avg, weekend_avg]):
        ax2.text(i, v, f'{v:,.0f}', ha='center', va='bottom', fontweight='bold')
    
    plt.suptitle('The Invisible Economy: Weekend Service Usage Reveals Informal Work Patterns', 
                 fontsize=14, fontweight='bold', y=1.02)
    
    save_plot('02_invisible_economy_weekend_patterns.png')
    
    # ========================================================================
    # PLOT 3: MONSOON MIGRATION - Seasonal Bimodal Patterns (HERO)
    # ========================================================================
    print("Plot 3: Monsoon Migration (Seasonal Patterns) - HERO INSIGHT")
    
    # District-month demographic updates
    demo_df['year_month'] = demo_df['date'].dt.to_period('M')
    district_month = demo_df.groupby(['state', 'district', 'month']).agg({
        'demo_age_17_': 'sum'  # Adult demographic (address changes)
    }).reset_index()
    district_month.rename(columns={'demo_age_17_': 'adult_demo_updates'}, inplace=True)
    
    # Pivot for heatmap (top states only to avoid overcrowding)
    state_month = demo_df.groupby(['state', 'month']).agg({
        'demo_age_17_': 'sum'
    }).reset_index()
    
    # Get top 15 states by total updates
    top_states = state_month.groupby('state')['demo_age_17_'].sum().nlargest(15).index
    state_month_top = state_month[state_month['state'].isin(top_states)]
    
    # Pivot
    heatmap_data = state_month_top.pivot(index='state', columns='month', values='demo_age_17_')
    
    # Ensure all 12 months are present for correct labeling
    all_months = list(range(1, 13))
    heatmap_data = heatmap_data.reindex(columns=all_months, fill_value=0)
    
    heatmap_data = heatmap_data.fillna(0)
    
    # Normalize by row for pattern visibility
    heatmap_data_norm = heatmap_data.div(heatmap_data.sum(axis=1), axis=0) * 100
    
    # Plot
    fig, ax = plt.subplots(figsize=(16, 10))
    
    sns.heatmap(heatmap_data_norm, cmap='YlOrRd', annot=True, fmt='.1f', 
                cbar_kws={'label': 'Share of Annual Updates (%)'}, ax=ax,
                linewidths=0.5, linecolor='white')
    
    ax.set_xlabel('Month', fontweight='bold', fontsize=12)
    ax.set_ylabel('State', fontweight='bold', fontsize=12)
    ax.set_title('HERO INSIGHT: Monsoon-Driven Migration Revealed\n' + 
                 'Adult Demographic Updates Show Bimodal Seasonal Peaks (Jun-Jul, Sep-Oct)\n' +
                 'Climate Vulnerability Mapped Through Aadhaar Data',
                 fontsize=14, fontweight='bold', pad=20)
    
    # Highlight monsoon months
    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    ax.set_xticklabels(month_labels)
    
    # Add annotations for monsoon periods
    ax.axvline(x=5.5, color='blue', linewidth=3, alpha=0.7, linestyle='--')  # Jun-Jul start
    ax.axvline(x=7.5, color='blue', linewidth=3, alpha=0.7, linestyle='--')  # Sep-Oct region
    
    ax.text(6.5, -1.5, '← Monsoon Planting', ha='center', fontsize=10, 
            fontweight='bold', color='blue')
    ax.text(9.5, -1.5, 'Harvest Season →', ha='center', fontsize=10,
            fontweight='bold', color='blue')
    
    save_plot('03_monsoon_migration_heatmap.png')
    
    # ========================================================================
    # PLOT 4: HEALTHCARE DESERTS - Infant Enrolment Gaps
    # ========================================================================
    print("Plot 4: Healthcare Deserts (Infant Enrolment Gaps)")
    
    # NOTE: This requires external birth rate data which may not be available
    # We'll create a proxy using infant enrolment share
    
    district_enrol = enrol_df.groupby(['state', 'district']).agg({
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum'
    }).reset_index()
    
    district_enrol['total_enrol'] = (district_enrol['age_0_5'] + 
                                      district_enrol['age_5_17'] + 
                                      district_enrol['age_18_greater'])
    district_enrol['infant_share'] = (district_enrol['age_0_5'] / 
                                       district_enrol['total_enrol'] * 100)
    
    # Filter valid districts
    district_enrol = district_enrol[district_enrol['total_enrol'] >= 50]  # Minimum threshold
    
    # Get bottom 20 districts (lowest infant share = potential healthcare gaps)
    bottom_20 = district_enrol.nsmallest(20, 'infant_share')
    
    # Plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    y_pos = np.arange(len(bottom_20))
    bars = ax.barh(y_pos, bottom_20['infant_share'], color=COLORS['warning'], alpha=0.7)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"{row['district']}, {row['state']}" 
                        for _, row in bottom_20.iterrows()], fontsize=9)
    ax.set_xlabel('Infant Enrolment Share (%)', fontweight='bold')
    ax.set_title('Healthcare Deserts: Districts with Lowest Infant Enrolment\n' +
                 'Low 0-5 Age Enrolment Suggests Poor Hospital-Aadhaar Linkage\n' +
                 'Proxy for Maternal & Child Health Infrastructure Gaps',
                 fontsize=13, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)
    
    # Add national median line
    median_infant = district_enrol['infant_share'].median()
    ax.axvline(x=median_infant, color=COLORS['primary'], linestyle='--', 
               linewidth=2, label=f'National Median: {median_infant:.1f}%')
    ax.legend()
    
    # Add value labels
    for i, (idx, row) in enumerate(bottom_20.iterrows()):
        ax.text(row['infant_share'] + 1, i, f"{row['infant_share']:.1f}%", 
                va='center', fontsize=8)
    
    save_plot('04_healthcare_deserts_infant_gaps.png')
    
    # ========================================================================
    # PLOT 5: DIGITAL DIVIDE - Bio/Demo Ratio
    # ========================================================================
    print("Plot 5: Digital Divide (Bio/Demo Update Ratio)")
    
    # District-level bio and demo totals
    district_bio = bio_df.groupby(['state', 'district']).agg({
        'bio_age_5_17': 'sum',
        'bio_age_17_': 'sum'
    }).reset_index()
    district_bio['total_bio'] = district_bio['bio_age_5_17'] + district_bio['bio_age_17_']
    
    district_demo = demo_df.groupby(['state', 'district']).agg({
        'demo_age_5_17': 'sum',
        'demo_age_17_': 'sum'
    }).reset_index()
    district_demo['total_demo'] = district_demo['demo_age_5_17'] + district_demo['demo_age_17_']
    
    # Merge
    district_updates = district_bio.merge(district_demo, on=['state', 'district'], how='outer')
    district_updates = district_updates.fillna(0)
    
    # Calculate ratio (bio to demo)
    district_updates['bio_demo_ratio'] = np.where(
        district_updates['total_demo'] > 0,
        district_updates['total_bio'] / district_updates['total_demo'],
        np.nan
    )
    
    # Filter valid
    district_updates = district_updates.dropna(subset=['bio_demo_ratio'])
    district_updates = district_updates[
        (district_updates['total_bio'] >= 100) & (district_updates['total_demo'] >= 100)
    ]
    
    # Get top 25 by ratio (most bio-heavy = digital literacy gap)
    top_ratio = district_updates.nlargest(25, 'bio_demo_ratio')
    
    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Subplot 1: Top districts with high bio-demo ratio
    y_pos = np.arange(len(top_ratio))
    bars = ax1.barh(y_pos, top_ratio['bio_demo_ratio'], color=COLORS['secondary'], alpha=0.7)
    
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels([f"{row['district']}" for _, row in top_ratio.iterrows()], fontsize=8)
    ax1.set_xlabel('Biometric-to-Demographic Ratio', fontweight='bold')
    ax1.set_title('Top 25 Districts: High Bio/Demo Ratio\nProxy for Digital Literacy Gap', 
                  fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    ax1.axvline(x=1.0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    
    # Subplot 2: Distribution histogram
    ax2.hist(district_updates['bio_demo_ratio'], bins=50, color=COLORS['primary'], 
             alpha=0.7, edgecolor='black')
    ax2.axvline(x=1.0, color=COLORS['warning'], linestyle='--', linewidth=2, 
                label='Balanced (1:1)')
    ax2.set_xlabel('Biometric-to-Demographic Ratio', fontweight='bold')
    ax2.set_ylabel('Number of Districts', fontweight='bold')
    ax2.set_title('Distribution Across All Districts', fontweight='bold')
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    
    median_ratio = district_updates['bio_demo_ratio'].median()
    ax2.axvline(x=median_ratio, color=COLORS['accent'], linestyle='--', linewidth=2,
                label=f'Median: {median_ratio:.2f}')
    ax2.legend()
    
    plt.suptitle('Digital Divide: Service Design Challenge\n' + 
                 'High Bio/Demo Ratio = More In-Person Visits (Low Digital Literacy)\n' +
                 'Biometric Requires Center Visit | Demographic Can Be Self-Service Online',
                 fontsize=14, fontweight='bold', y=1.02)
    
    save_plot('05_digital_divide_bio_demo_ratio.png')
    
    # ========================================================================
    # BONUS PLOTS (If Time Permits)
    # ========================================================================
    
    # BONUS: Child Attention Gap
    print("Bonus Plot: Child Attention Gap")
    
    # Enrolment child share
    district_enrol['child_enrol_share'] = ((district_enrol['age_0_5'] + 
                                             district_enrol['age_5_17']) / 
                                            district_enrol['total_enrol'])
    
    # Update child share
    district_updates['child_bio_share'] = (district_updates['bio_age_5_17'] / 
                                            district_updates['total_bio'])
    district_updates['child_demo_share'] = (district_updates['demo_age_5_17'] / 
                                             district_updates['total_demo'])
    district_updates['child_update_share'] = (
        (district_updates['bio_age_5_17'] + district_updates['demo_age_5_17']) /
        (district_updates['total_bio'] + district_updates['total_demo'])
    )
    
    # Merge
    child_gap = district_enrol[['state', 'district', 'child_enrol_share']].merge(
        district_updates[['state', 'district', 'child_update_share']], 
        on=['state', 'district'], how='inner'
    )
    child_gap['attention_gap'] = (child_gap['child_update_share'] - 
                                   child_gap['child_enrol_share'])
    
    # Get worst gaps
    worst_gaps = child_gap.nsmallest(20, 'attention_gap')
    
    # Plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    y_pos = np.arange(len(worst_gaps))
    colors = [COLORS['warning'] if g < -0.3 else COLORS['secondary'] 
              for g in worst_gaps['attention_gap']]
    bars = ax.barh(y_pos, worst_gaps['attention_gap'], color=colors, alpha=0.7)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels([f"{row['district']}, {row['state']}" 
                        for _, row in worst_gaps.iterrows()], fontsize=9)
    ax.set_xlabel('Child Attention Gap (Update Share - Enrolment Share)', fontweight='bold')
    ax.set_title('Child Attention Gap: Districts Where Children Are Enrolled But Not Updated\n' +
                 'Negative Gap = Children Under-Represented in Updates (Authentication Risk)',
                 fontsize=13, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)
    ax.axvline(x=0, color='black', linestyle='-', linewidth=1)
    
    save_plot('bonus_child_attention_gap.png')
    
    # ========================================================================
    # SUMMARY STATISTICS
    # ========================================================================
    print()
    print("="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    print(f"Total Enrolments: {enrol_df['age_0_5'].sum() + enrol_df['age_5_17'].sum() + enrol_df['age_18_greater'].sum():,}")
    print(f"Total Biometric Updates: {bio_df['bio_age_5_17'].sum() + bio_df['bio_age_17_'].sum():,}")
    print(f"Total Demographic Updates: {demo_df['demo_age_5_17'].sum() + demo_df['demo_age_17_'].sum():,}")
    print(f"Update-to-Enrolment Ratio: {ratio:.2f}×")
    print(f"Weekend Update Increase: +{pct_diff:.1f}%")
    print(f"Median Bio/Demo Ratio: {median_ratio:.2f}")
    print()
    print(f"All plots saved to: {OUTPUT_DIR}/")
    print("="*80)
    print("PLOT GENERATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
