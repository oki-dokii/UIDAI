#!/usr/bin/env python3
"""
UIDAI Datathon 2026 - Missing High-Impact Analyses
Generates 5 additional visualizations identified in forensic analytical audit

Analyses:
1. Update Intensity by Population Density Quintiles
2. Temporal Autocorrelation of District Update Intensity
3. Biometric Share vs District Age (Time Since First Enrolment)
4. State-Level Gini Coefficient for Update Intensity Distribution
5. Update Type Transition Matrix (Biometric vs Demographic)

Author: UIDAI Datathon Team
Date: January 20, 2026
"""

import os
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from scipy import stats

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_FILE = os.path.join(BASE_DIR, "outputs", "integrated_analysis", "integrated_data.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "aadhaar_plots_enhanced")

# Visual settings
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9

COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'accent': '#2ca02c',
    'warning': '#d62728',
    'neutral': '#7f7f7f'
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_output_dir():
    """Create output directory if it doesn't exist."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"✓ Created output directory: {OUTPUT_DIR}/")

def save_plot(filename, tight=True):
    """Save plot with consistent settings."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if tight:
        plt.tight_layout()
    plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"  ✓ Saved: {filename}")
    plt.close()

def load_integrated_data():
    """Load and validate integrated dataset."""
    print(f"Loading data from: {DATA_FILE}")
    
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(
            f"Data file not found: {DATA_FILE}\n"
            "Please run scripts/integrated_analysis.py first."
        )
    
    df = pd.read_csv(DATA_FILE)
    
    # Create date column from year/month if not present
    if 'date' not in df.columns and 'year' in df.columns and 'month' in df.columns:
        print("  Creating date column from year/month...")
        df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))
    elif 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Create year_month period for temporal analysis
    if 'date' in df.columns:
        df['year_month'] = df['date'].dt.to_period('M')
    
    print(f"  ✓ Loaded {len(df):,} records")
    print(f"  ✓ Columns: {', '.join(df.columns[:10])}...")
    if 'date' in df.columns:
        print(f"  ✓ Date range: {df['date'].min()} to {df['date'].max()}")
    
    return df

def compute_gini(x):
    """
    Compute Gini coefficient for an array.
    Returns value in [0, 1] where 0 = perfect equality, 1 = perfect inequality.
    """
    # Remove NaN and sort
    x = np.array(x)
    x = x[~np.isnan(x)]
    
    if len(x) == 0:
        return np.nan
    
    x = np.sort(x)
    n = len(x)
    
    # Gini coefficient formula
    index = np.arange(1, n + 1)
    gini = (2 * np.sum(index * x)) / (n * np.sum(x)) - (n + 1) / n
    
    return gini

# ============================================================================
# ANALYSIS 1: UPDATE INTENSITY BY POPULATION DENSITY QUINTILES
# ============================================================================

def analysis_1_density_quintiles(df):
    """
    Stratify districts by enrolment size (proxy for population density)
    and compare update intensity distributions across quintiles.
    """
    print("\n" + "="*80)
    print("ANALYSIS 1: Update Intensity by Population Density Quintiles")
    print("="*80)
    
    # Aggregate to district level
    district_agg = df.groupby(['state', 'district']).agg({
        'total_enrol': 'sum',
        'total_updates': 'sum'
    }).reset_index()
    
    # Calculate update intensity
    district_agg['update_intensity'] = (
        district_agg['total_updates'] / (district_agg['total_enrol'] + 1) * 1000
    )
    
    # Create quintiles based on total enrolment (proxy for density)
    district_agg['density_quintile'] = pd.qcut(
        district_agg['total_enrol'], 
        q=5, 
        labels=['Q1 (Smallest)', 'Q2', 'Q3', 'Q4', 'Q5 (Largest)']
    )
    
    print(f"  Districts per quintile: {len(district_agg) // 5}")
    
    # Create visualization
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Grouped violin plots
    sns.violinplot(
        data=district_agg,
        x='density_quintile',
        y='update_intensity',
        palette='Blues',
        ax=ax,
        cut=0
    )
    
    # Overlay box plots for quartiles
    sns.boxplot(
        data=district_agg,
        x='density_quintile',
        y='update_intensity',
        width=0.3,
        palette='Set2',
        ax=ax,
        showfliers=False,
        boxprops=dict(alpha=0.7)
    )
    
    ax.set_xlabel('District Size Quintile (by Total Enrolments)', fontweight='bold')
    ax.set_ylabel('Update Intensity (per 1,000 Enrolments)', fontweight='bold')
    ax.set_title(
        'Update Intensity Declines with District Size\n'
        'Small Districts Exhibit Extreme Variance in Administrative Engagement\n'
        f'(n={len(district_agg)} districts, grouped by enrolment quintiles)',
        fontsize=13,
        fontweight='bold',
        pad=20
    )
    
    # Add median values as text
    medians = district_agg.groupby('density_quintile')['update_intensity'].median()
    for i, (quintile, median) in enumerate(medians.items()):
        ax.text(i, ax.get_ylim()[1] * 0.95, f'Median: {median:.0f}', 
                ha='center', fontsize=9, fontweight='bold')
    
    ax.grid(axis='y', alpha=0.3)
    
    # Add source attribution
    plt.figtext(0.99, 0.01, 'Source: UIDAI Integrated Analysis Dataset, 2025',
                ha='right', fontsize=8, style='italic')
    
    save_plot('analysis_1_density_quintiles.png')
    
    # Print summary statistics
    print("\n  Summary Statistics by Quintile:")
    summary = district_agg.groupby('density_quintile')['update_intensity'].agg([
        ('Median', 'median'),
        ('IQR', lambda x: x.quantile(0.75) - x.quantile(0.25)),
        ('CV', lambda x: x.std() / x.mean())
    ])
    print(summary)

# ============================================================================
# ANALYSIS 2: TEMPORAL AUTOCORRELATION OF DISTRICT UPDATE INTENSITY
# ============================================================================

def analysis_2_temporal_autocorrelation(df):
    """
    Compute lag-1 autocorrelation of update intensity for each district
    to distinguish persistent vs episodic patterns.
    """
    print("\n" + "="*80)
    print("ANALYSIS 2: Temporal Autocorrelation of District Update Intensity")
    print("="*80)
    
    # Check if we have temporal data
    if 'date' not in df.columns or 'year_month' not in df.columns:
        print("  ⚠ WARNING: No temporal columns found. Creating year_month from date.")
        if 'date' in df.columns:
            df['year_month'] = pd.to_datetime(df['date']).dt.to_period('M')
        else:
            print("  ⚠ ERROR: Cannot perform temporal analysis without date column.")
            return
    
    # Aggregate by district and month
    district_month = df.groupby(['state', 'district', 'year_month']).agg({
        'total_updates': 'sum',
        'total_enrol': 'sum'
    }).reset_index()
    
    # Calculate update intensity
    district_month['update_intensity'] = (
        district_month['total_updates'] / (district_month['total_enrol'] + 1) * 1000
    )
    
    # Compute lag-1 autocorrelation for each district
    autocorr_results = []
    
    for (state, district), group in district_month.groupby(['state', 'district']):
        if len(group) < 3:  # Need at least 3 time points
            continue
        
        # Sort by time
        group = group.sort_values('year_month')
        
        # Compute autocorrelation
        intensity_series = group['update_intensity'].values
        
        if len(intensity_series) >= 3 and intensity_series.std() > 0:
            # Pearson correlation between t and t-1
            lag1_corr = np.corrcoef(intensity_series[:-1], intensity_series[1:])[0, 1]
            
            autocorr_results.append({
                'state': state,
                'district': district,
                'autocorr_lag1': lag1_corr,
                'n_periods': len(group)
            })
    
    autocorr_df = pd.DataFrame(autocorr_results)
    
    if len(autocorr_df) == 0:
        print("  ⚠ WARNING: Insufficient temporal data for autocorrelation analysis.")
        print("  Creating placeholder visualization...")
        
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.text(0.5, 0.5, 
                'Insufficient Temporal Data\n\n'
                'Temporal autocorrelation analysis requires\n'
                'multiple time periods per district.\n\n'
                'Current dataset appears to have limited temporal coverage.',
                ha='center', va='center', fontsize=14, color='gray')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        save_plot('analysis_2_temporal_autocorrelation.png')
        return
    
    print(f"  Computed autocorrelation for {len(autocorr_df)} districts")
    
    # Create visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Subplot 1: Histogram of autocorrelations
    ax1.hist(autocorr_df['autocorr_lag1'].dropna(), bins=30, 
             color=COLORS['primary'], alpha=0.7, edgecolor='black')
    ax1.axvline(x=0, color='red', linestyle='--', linewidth=2, label='No Persistence')
    ax1.axvline(x=autocorr_df['autocorr_lag1'].median(), 
                color='orange', linestyle='--', linewidth=2,
                label=f"Median: {autocorr_df['autocorr_lag1'].median():.2f}")
    ax1.set_xlabel('Lag-1 Autocorrelation Coefficient', fontweight='bold')
    ax1.set_ylabel('Number of Districts', fontweight='bold')
    ax1.set_title('Distribution of Temporal Persistence', fontweight='bold')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Subplot 2: Top persistent vs episodic districts
    top_persistent = autocorr_df.nlargest(10, 'autocorr_lag1')
    top_episodic = autocorr_df.nsmallest(10, 'autocorr_lag1')
    
    combined = pd.concat([
        top_persistent.assign(category='High Persistence (Stable)'),
        top_episodic.assign(category='Low Persistence (Episodic)')
    ])
    
    y_labels = [f"{row['district'][:15]}" for _, row in combined.iterrows()]
    y_pos = np.arange(len(combined))
    colors_cat = [COLORS['accent'] if cat == 'High Persistence (Stable)' 
                  else COLORS['warning'] for cat in combined['category']]
    
    ax2.barh(y_pos, combined['autocorr_lag1'], color=colors_cat, alpha=0.7)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(y_labels, fontsize=8)
    ax2.set_xlabel('Lag-1 Autocorrelation', fontweight='bold')
    ax2.set_title('Top 10 Persistent vs Episodic Districts', fontweight='bold')
    ax2.axvline(x=0, color='black', linestyle='-', linewidth=1)
    ax2.grid(axis='x', alpha=0.3)
    
    # Add legend for colors
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=COLORS['accent'], alpha=0.7, label='High Persistence'),
        Patch(facecolor=COLORS['warning'], alpha=0.7, label='Low Persistence')
    ]
    ax2.legend(handles=legend_elements, loc='lower right')
    
    plt.suptitle(
        'Temporal Persistence Analysis: Distinguishing Structural vs Episodic Update Patterns\n'
        f'Lag-1 Autocorrelation of Monthly Update Intensity (n={len(autocorr_df)} districts)',
        fontsize=13,
        fontweight='bold',
        y=1.02
    )
    
    plt.figtext(0.99, 0.01, 'Source: UIDAI Integrated Analysis Dataset, 2025',
                ha='right', fontsize=8, style='italic')
    
    save_plot('analysis_2_temporal_autocorrelation.png')
    
    # Print summary
    print(f"\n  Mean autocorrelation: {autocorr_df['autocorr_lag1'].mean():.3f}")
    print(f"  Median autocorrelation: {autocorr_df['autocorr_lag1'].median():.3f}")
    print(f"  High persistence districts (ρ > 0.7): {(autocorr_df['autocorr_lag1'] > 0.7).sum()}")
    print(f"  Low persistence districts (ρ < 0.2): {(autocorr_df['autocorr_lag1'] < 0.2).sum()}")

# ============================================================================
# ANALYSIS 3: BIOMETRIC SHARE VS DISTRICT AGE
# ============================================================================

def analysis_3_bio_share_vs_age(df):
    """
    Correlate biometric share with district maturity (time since first enrolment)
    to test lifecycle hypothesis.
    """
    print("\n" + "="*80)
    print("ANALYSIS 3: Biometric Share vs District Age")
    print("="*80)
    
    # Calculate district age (time since first enrolment)
    district_age = df.groupby(['state', 'district']).agg({
        'date': ['min', 'max'],
        'total_bio': 'sum',
        'total_demo': 'sum',
        'total_updates': 'sum'
    }).reset_index()
    
    district_age.columns = ['state', 'district', 'first_date', 'last_date', 
                            'total_bio', 'total_demo', 'total_updates']
    
    # Calculate age in days
    district_age['age_days'] = (district_age['last_date'] - district_age['first_date']).dt.days
    
    # Calculate biometric share
    district_age['bio_share'] = (
        district_age['total_bio'] / (district_age['total_updates'] + 1)
    )
    
    # Filter valid districts (have both bio and demo updates)
    district_age = district_age[
        (district_age['total_bio'] > 0) & 
        (district_age['total_demo'] > 0) &
        (district_age['age_days'] > 0)
    ]
    
    print(f"  Valid districts for analysis: {len(district_age)}")
    
    if len(district_age) < 10:
        print("  ⚠ WARNING: Insufficient districts with both update types.")
        fig, ax = plt.subplots(figsize=(12, 7))
        ax.text(0.5, 0.5, 
                'Insufficient Data\n\n'
                'Analysis requires districts with both\n'
                'biometric and demographic updates.',
                ha='center', va='center', fontsize=14, color='gray')
        ax.axis('off')
        save_plot('analysis_3_bio_share_vs_age.png')
        return
    
    # Compute correlation
    corr, p_value = stats.pearsonr(district_age['age_days'], district_age['bio_share'])
    
    # Create visualization
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Scatter plot with regression line
    ax.scatter(district_age['age_days'], district_age['bio_share'], 
               alpha=0.5, s=50, color=COLORS['primary'], edgecolors='black', linewidth=0.5)
    
    # Add regression line
    z = np.polyfit(district_age['age_days'], district_age['bio_share'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(district_age['age_days'].min(), district_age['age_days'].max(), 100)
    ax.plot(x_line, p(x_line), color=COLORS['warning'], linewidth=2, 
            linestyle='--', label=f'Linear Fit (r={corr:.3f}, p={p_value:.4f})')
    
    ax.set_xlabel('District Age (Days Since First Enrolment)', fontweight='bold')
    ax.set_ylabel('Biometric Share of Total Updates', fontweight='bold')
    ax.set_title(
        'Lifecycle Dynamics: Biometric vs Demographic Update Preferences\n'
        f'Testing Hypothesis that Older Enrolment Cohorts Require More Biometric Updates (n={len(district_age)} districts)',
        fontsize=13,
        fontweight='bold',
        pad=20
    )
    
    # Add reference line at 0.5 (balanced)
    ax.axhline(y=0.5, color='gray', linestyle=':', linewidth=1, label='Balanced (50/50)')
    
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Add correlation annotation
    ax.annotate(
        f'Correlation: r = {corr:.3f}\n'
        f'p-value: {p_value:.4f}\n'
        f'{"Significant" if p_value < 0.05 else "Not Significant"} at α=0.05',
        xy=(0.05, 0.95), xycoords='axes fraction',
        fontsize=10, va='top',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7)
    )
    
    plt.figtext(0.99, 0.01, 'Source: UIDAI Integrated Analysis Dataset, 2025',
                ha='right', fontsize=8, style='italic')
    
    save_plot('analysis_3_bio_share_vs_age.png')
    
    # Print summary
    print(f"  Correlation: r = {corr:.3f}, p = {p_value:.4f}")
    print(f"  Mean bio share: {district_age['bio_share'].mean():.3f}")
    print(f"  Age range: {district_age['age_days'].min()}-{district_age['age_days'].max()} days")

# ============================================================================
# ANALYSIS 4: STATE-LEVEL GINI COEFFICIENT FOR UPDATE INTENSITY
# ============================================================================

def analysis_4_state_gini(df):
    """
    Compute Gini coefficient of district-level update intensity within each state
    to quantify within-state inequality.
    """
    print("\n" + "="*80)
    print("ANALYSIS 4: State-Level Gini Coefficient for Update Intensity")
    print("="*80)
    
    # Aggregate to district level
    district_agg = df.groupby(['state', 'district']).agg({
        'total_updates': 'sum',
        'total_enrol': 'sum'
    }).reset_index()
    
    # Calculate update intensity
    district_agg['update_intensity'] = (
        district_agg['total_updates'] / (district_agg['total_enrol'] + 1) * 1000
    )
    
    # Compute Gini coefficient for each state
    state_gini = district_agg.groupby('state').agg({
        'update_intensity': [compute_gini, 'count']
    }).reset_index()
    
    state_gini.columns = ['state', 'gini_coefficient', 'n_districts']
    
    # Filter states with at least 5 districts
    state_gini = state_gini[state_gini['n_districts'] >= 5]
    
    # Sort by Gini
    state_gini = state_gini.sort_values('gini_coefficient', ascending=False)
    
    print(f"  States analyzed: {len(state_gini)}")
    
    # Create visualization
    fig, ax = plt.subplots(figsize=(12, 10))
    
    y_pos = np.arange(len(state_gini))
    colors = [COLORS['warning'] if g > 0.5 else COLORS['primary'] 
              for g in state_gini['gini_coefficient']]
    
    bars = ax.barh(y_pos, state_gini['gini_coefficient'], color=colors, alpha=0.7)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(state_gini['state'], fontsize=9)
    ax.set_xlabel('Gini Coefficient (0 = Perfect Equality, 1 = Perfect Inequality)', fontweight='bold')
    ax.set_title(
        'Within-State Inequality in District Update Intensity\n'
        'Gini Coefficient Identifies States Requiring District-Targeted vs State-Wide Interventions\n'
        f'(n={len(state_gini)} states with ≥5 districts)',
        fontsize=13,
        fontweight='bold',
        pad=20
    )
    
    # Add reference lines
    ax.axvline(x=0.4, color='orange', linestyle='--', linewidth=1, label='Moderate Inequality (0.4)')
    ax.axvline(x=0.5, color='red', linestyle='--', linewidth=1, label='High Inequality (0.5)')
    
    # Add value labels
    for i, (_, row) in enumerate(state_gini.iterrows()):
        ax.text(row['gini_coefficient'] + 0.01, i, 
                f"{row['gini_coefficient']:.3f} (n={int(row['n_districts'])})",
                va='center', fontsize=8)
    
    ax.legend(loc='lower right')
    ax.grid(axis='x', alpha=0.3)
    ax.set_xlim(0, min(1.0, state_gini['gini_coefficient'].max() * 1.1))
    
    plt.figtext(0.99, 0.01, 'Source: UIDAI Integrated Analysis Dataset, 2025',
                ha='right', fontsize=8, style='italic')
    
    save_plot('analysis_4_state_gini.png')
    
    # Print summary
    print(f"\n  Mean Gini: {state_gini['gini_coefficient'].mean():.3f}")
    print(f"  Highest inequality: {state_gini.iloc[0]['state']} ({state_gini.iloc[0]['gini_coefficient']:.3f})")
    print(f"  Lowest inequality: {state_gini.iloc[-1]['state']} ({state_gini.iloc[-1]['gini_coefficient']:.3f})")

# ============================================================================
# ANALYSIS 5: UPDATE TYPE TRANSITION MATRIX
# ============================================================================

def analysis_5_transition_matrix(df):
    """
    Build transition matrix for update type preferences (bio-heavy vs demo-heavy)
    across consecutive time periods.
    """
    print("\n" + "="*80)
    print("ANALYSIS 5: Update Type Transition Matrix")
    print("="*80)
    
    # Check temporal data
    if 'year_month' not in df.columns:
        print("  Creating year_month from date...")
        if 'date' in df.columns:
            df['year_month'] = pd.to_datetime(df['date']).dt.to_period('M')
        else:
            print("  ⚠ ERROR: Cannot perform transition analysis without date column.")
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.text(0.5, 0.5, 
                    'Insufficient Temporal Data\n\n'
                    'Transition matrix requires multiple time periods.',
                    ha='center', va='center', fontsize=14, color='gray')
            ax.axis('off')
            save_plot('analysis_5_transition_matrix.png')
            return
    
    # Aggregate by district and month
    district_month = df.groupby(['state', 'district', 'year_month']).agg({
        'total_bio': 'sum',
        'total_demo': 'sum'
    }).reset_index()
    
    # Calculate biometric share
    district_month['bio_share'] = (
        district_month['total_bio'] / 
        (district_month['total_bio'] + district_month['total_demo'] + 1)
    )
    
    # Classify as bio-heavy or demo-heavy
    threshold = 0.6
    district_month['update_type'] = district_month['bio_share'].apply(
        lambda x: 'Bio-Heavy' if x >= threshold else 'Demo-Heavy'
    )
    
    # Build transition matrix
    transitions = []
    
    for (state, district), group in district_month.groupby(['state', 'district']):
        group = group.sort_values('year_month')
        
        if len(group) < 2:
            continue
        
        # Get consecutive pairs
        for i in range(len(group) - 1):
            from_type = group.iloc[i]['update_type']
            to_type = group.iloc[i + 1]['update_type']
            
            transitions.append({
                'from': from_type,
                'to': to_type
            })
    
    if len(transitions) == 0:
        print("  ⚠ WARNING: Insufficient temporal data for transition analysis.")
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.text(0.5, 0.5, 
                'Insufficient Transitions\n\n'
                'Requires multiple consecutive periods per district.',
                ha='center', va='center', fontsize=14, color='gray')
        ax.axis('off')
        save_plot('analysis_5_transition_matrix.png')
        return
    
    transitions_df = pd.DataFrame(transitions)
    
    # Create contingency table
    transition_matrix = pd.crosstab(
        transitions_df['from'], 
        transitions_df['to'], 
        normalize='index'
    ) * 100  # Convert to percentages
    
    print(f"  Total transitions observed: {len(transitions_df)}")
    print(f"\n  Transition Matrix (%):")
    print(transition_matrix)
    
    # Create visualization
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Heatmap
    sns.heatmap(
        transition_matrix,
        annot=True,
        fmt='.1f',
        cmap='YlOrRd',
        cbar_kws={'label': 'Transition Probability (%)'},
        linewidths=2,
        linecolor='white',
        ax=ax,
        vmin=0,
        vmax=100
    )
    
    ax.set_xlabel('Update Type at Time t+1', fontweight='bold', fontsize=12)
    ax.set_ylabel('Update Type at Time t', fontweight='bold', fontsize=12)
    ax.set_title(
        'Update Type Preference Stability\n'
        f'Transition Matrix Reveals Whether Districts Maintain Consistent Update Preferences (n={len(transitions_df)} transitions)\n'
        f'Threshold: Biometric Share ≥ {threshold*100:.0f}% = Bio-Heavy',
        fontsize=13,
        fontweight='bold',
        pad=20
    )
    
    # Add interpretation text
    persistence = (
        transition_matrix.loc['Bio-Heavy', 'Bio-Heavy'] + 
        transition_matrix.loc['Demo-Heavy', 'Demo-Heavy']
    ) / 2
    
    ax.text(
        0.5, -0.15,
        f'Average Diagonal Persistence: {persistence:.1f}%\n'
        f'{"High diagonal values indicate stable preferences" if persistence > 70 else "High off-diagonal values indicate campaign-induced shifts"}',
        ha='center',
        transform=ax.transAxes,
        fontsize=10,
        bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8)
    )
    
    plt.figtext(0.99, 0.01, 'Source: UIDAI Integrated Analysis Dataset, 2025',
                ha='right', fontsize=8, style='italic')
    
    save_plot('analysis_5_transition_matrix.png')

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("="*80)
    print("UIDAI DATATHON 2026 - MISSING HIGH-IMPACT ANALYSES")
    print("Forensic Audit Enhancement Suite")
    print("="*80)
    print()
    
    create_output_dir()
    
    # Load data
    print("\nStep 1: Loading Data")
    print("-"*80)
    df = load_integrated_data()
    
    # Run analyses
    print("\nStep 2: Generating Analyses")
    print("-"*80)
    
    try:
        analysis_1_density_quintiles(df)
    except Exception as e:
        print(f"  ⚠ ERROR in Analysis 1: {e}")
    
    try:
        analysis_2_temporal_autocorrelation(df)
    except Exception as e:
        print(f"  ⚠ ERROR in Analysis 2: {e}")
    
    try:
        analysis_3_bio_share_vs_age(df)
    except Exception as e:
        print(f"  ⚠ ERROR in Analysis 3: {e}")
    
    try:
        analysis_4_state_gini(df)
    except Exception as e:
        print(f"  ⚠ ERROR in Analysis 4: {e}")
    
    try:
        analysis_5_transition_matrix(df)
    except Exception as e:
        print(f"  ⚠ ERROR in Analysis 5: {e}")
    
    print("\n" + "="*80)
    print("ANALYSIS GENERATION COMPLETE")
    print("="*80)
    print(f"\nAll outputs saved to: {OUTPUT_DIR}/")
    print("\nNext steps:")
    print("  1. Review visualizations for quality")
    print("  2. Run reorganize_visualizations.py to create final canon")
    print("  3. Validate against visualization_quality_checklist.md")
    print("="*80)

if __name__ == "__main__":
    main()
