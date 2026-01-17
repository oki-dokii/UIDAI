#!/usr/bin/env python3
"""
UIDAI Data Hackathon 2026 - INTEGRATED ANALYSIS
Combining Enrolment + Demographic + Biometric for Cross-Domain Insights

This is the ULTIMATE analysis that reveals how enrolment and updates
interact across age groups, regions, and time.

Author: UIDAI Hackathon Team
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import glob
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================
BASE_DIR = "/Users/ayushpatel/Documents/Projects/UIDAI/UIDAI"
ENROL_DIR = os.path.join(BASE_DIR, "api_data_aadhar_enrolment")
DEMO_DIR = os.path.join(BASE_DIR, "api_data_aadhar_demographic")
BIO_DIR = os.path.join(BASE_DIR, "api_data_aadhar_biometric")
OUTPUT_DIR = os.path.join(BASE_DIR, "integrated_analysis")
PLOTS_DIR = os.path.join(OUTPUT_DIR, "plots")

# State normalization
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

EPS = 1e-10  # Small epsilon for division

# ============================================================================
# DATA LOADING
# ============================================================================
def load_dataset(data_dir, name):
    """Load all CSVs from a directory."""
    files = glob.glob(os.path.join(data_dir, "*.csv"))
    dfs = []
    for f in sorted(files):
        df = pd.read_csv(f)
        dfs.append(df)
    data = pd.concat(dfs, ignore_index=True)
    print(f"  ✓ Loaded {name}: {len(data):,} rows from {len(files)} files")
    return data

def load_all_data():
    """Load all three datasets."""
    print("\n" + "="*70)
    print("PHASE 1: DATA LOADING")
    print("="*70)
    
    enrol = load_dataset(ENROL_DIR, "Enrolment")
    demo = load_dataset(DEMO_DIR, "Demographic")
    bio = load_dataset(BIO_DIR, "Biometric")
    
    return enrol, demo, bio

# ============================================================================
# DATA PREPROCESSING
# ============================================================================
def preprocess(df, name):
    """Clean and standardize a dataset."""
    df = df.copy()
    
    # Parse dates
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day_of_week'] = df['date'].dt.day_name()
    df['is_weekend'] = df['day_of_week'].isin(['Saturday', 'Sunday'])
    
    # Standardize geography
    df['state'] = df['state'].astype(str).str.strip().str.title().replace(STATE_FIX)
    df['district'] = df['district'].astype(str).str.strip().str.title()
    
    # Create geo_key
    df['geo_key'] = df['state'] + '|' + df['district']
    
    return df

def preprocess_all(enrol, demo, bio):
    """Preprocess all datasets."""
    print("\n" + "="*70)
    print("PHASE 2: DATA PREPROCESSING")
    print("="*70)
    
    enrol = preprocess(enrol, "Enrolment")
    demo = preprocess(demo, "Demographic")
    bio = preprocess(bio, "Biometric")
    
    print(f"  ✓ Date ranges:")
    print(f"      Enrolment: {enrol['date'].min().date()} to {enrol['date'].max().date()}")
    print(f"      Demographic: {demo['date'].min().date()} to {demo['date'].max().date()}")
    print(f"      Biometric: {bio['date'].min().date()} to {bio['date'].max().date()}")
    
    return enrol, demo, bio

# ============================================================================
# AGGREGATION
# ============================================================================
def aggregate_enrolment(df):
    """Aggregate enrolment to state-month level."""
    df['total_enrol'] = df['age_0_5'] + df['age_5_17'] + df['age_18_greater']
    
    agg = df.groupby(['year', 'month', 'state', 'district']).agg({
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum',
        'total_enrol': 'sum'
    }).reset_index()
    
    # Shares
    agg['enrol_share_0_5'] = agg['age_0_5'] / (agg['total_enrol'] + EPS)
    agg['enrol_share_5_17'] = agg['age_5_17'] / (agg['total_enrol'] + EPS)
    agg['enrol_share_18_plus'] = agg['age_18_greater'] / (agg['total_enrol'] + EPS)
    agg['enrol_child_share'] = (agg['age_0_5'] + agg['age_5_17']) / (agg['total_enrol'] + EPS)
    
    return agg

def aggregate_demographic(df):
    """Aggregate demographic to state-month level."""
    df['total_demo'] = df['demo_age_5_17'] + df['demo_age_17_']
    
    agg = df.groupby(['year', 'month', 'state', 'district']).agg({
        'demo_age_5_17': 'sum',
        'demo_age_17_': 'sum',
        'total_demo': 'sum'
    }).reset_index()
    
    agg['demo_minor_share'] = agg['demo_age_5_17'] / (agg['total_demo'] + EPS)
    
    return agg

def aggregate_biometric(df):
    """Aggregate biometric to state-month level."""
    df['total_bio'] = df['bio_age_5_17'] + df['bio_age_17_']
    
    agg = df.groupby(['year', 'month', 'state', 'district']).agg({
        'bio_age_5_17': 'sum',
        'bio_age_17_': 'sum',
        'total_bio': 'sum'
    }).reset_index()
    
    agg['bio_minor_share'] = agg['bio_age_5_17'] / (agg['total_bio'] + EPS)
    
    return agg

def aggregate_all(enrol, demo, bio):
    """Aggregate all datasets."""
    print("\n" + "="*70)
    print("PHASE 3: AGGREGATION")
    print("="*70)
    
    enrol_agg = aggregate_enrolment(enrol)
    demo_agg = aggregate_demographic(demo)
    bio_agg = aggregate_biometric(bio)
    
    print(f"  ✓ Enrolment: {len(enrol_agg):,} district-month records")
    print(f"  ✓ Demographic: {len(demo_agg):,} district-month records")
    print(f"  ✓ Biometric: {len(bio_agg):,} district-month records")
    
    return enrol_agg, demo_agg, bio_agg

# ============================================================================
# CROSS-DOMAIN INTEGRATION
# ============================================================================
def integrate_datasets(enrol_agg, demo_agg, bio_agg):
    """Merge all three datasets on common keys."""
    print("\n" + "="*70)
    print("PHASE 4: CROSS-DOMAIN INTEGRATION")
    print("="*70)
    
    # Merge on year, month, state, district
    merged = enrol_agg.merge(
        demo_agg,
        on=['year', 'month', 'state', 'district'],
        how='outer'
    )
    merged = merged.merge(
        bio_agg,
        on=['year', 'month', 'state', 'district'],
        how='outer'
    )
    
    # Fill NaN with 0
    numeric_cols = merged.select_dtypes(include=[np.number]).columns
    merged[numeric_cols] = merged[numeric_cols].fillna(0)
    
    print(f"  ✓ Integrated dataset: {len(merged):,} records")
    print(f"  ✓ States: {merged['state'].nunique()}")
    print(f"  ✓ Districts: {merged[['state', 'district']].drop_duplicates().shape[0]}")
    
    return merged

def compute_cross_domain_metrics(df):
    """Compute cross-domain interaction metrics."""
    print("\n" + "="*70)
    print("PHASE 5: CROSS-DOMAIN METRICS")
    print("="*70)
    
    df = df.copy()
    
    # Total updates
    df['total_updates'] = df['total_demo'] + df['total_bio']
    
    # Update intensity relative to enrolment
    df['demo_intensity'] = df['total_demo'] / (df['total_enrol'] + EPS)
    df['bio_intensity'] = df['total_bio'] / (df['total_enrol'] + EPS)
    df['total_intensity'] = df['total_updates'] / (df['total_enrol'] + EPS)
    
    # Age-wise intensities
    df['demo_intensity_5_17'] = df['demo_age_5_17'] / (df['age_5_17'] + EPS)
    df['bio_intensity_5_17'] = df['bio_age_5_17'] / (df['age_5_17'] + EPS)
    df['demo_intensity_adult'] = df['demo_age_17_'] / (df['age_18_greater'] + EPS)
    df['bio_intensity_adult'] = df['bio_age_17_'] / (df['age_18_greater'] + EPS)
    
    # Child share in enrolment vs updates
    df['child_share_enrol'] = (df['age_0_5'] + df['age_5_17']) / (df['total_enrol'] + EPS)
    df['child_share_updates'] = (df['demo_age_5_17'] + df['bio_age_5_17']) / (df['total_updates'] + EPS)
    
    # Child attention gap (positive = children over-represented in updates)
    df['child_attention_gap'] = df['child_share_updates'] - df['child_share_enrol']
    
    # Adult share comparison
    df['adult_share_enrol'] = df['age_18_greater'] / (df['total_enrol'] + EPS)
    df['adult_share_updates'] = (df['demo_age_17_'] + df['bio_age_17_']) / (df['total_updates'] + EPS)
    df['adult_attention_gap'] = df['adult_share_updates'] - df['adult_share_enrol']
    
    # Interaction category
    median_enrol = df[df['total_enrol'] > 0]['total_enrol'].median()
    median_intensity = df[df['total_intensity'] > 0]['total_intensity'].median()
    
    def categorize(row):
        high_enrol = row['total_enrol'] > median_enrol
        high_intensity = row['total_intensity'] > median_intensity
        
        if high_enrol and high_intensity:
            return 'Mature (High E, High U)'
        elif high_enrol and not high_intensity:
            return 'Emerging (High E, Low U)'
        elif not high_enrol and high_intensity:
            return 'Legacy (Low E, High U)'
        else:
            return 'Under-served (Low E, Low U)'
    
    df['interaction_category'] = df.apply(categorize, axis=1)
    
    print(f"  ✓ Computed intensity metrics")
    print(f"  ✓ Computed child attention gap")
    print(f"  ✓ Assigned interaction categories")
    
    # Category distribution
    cat_dist = df['interaction_category'].value_counts()
    print(f"\n  Interaction Categories:")
    for cat, count in cat_dist.items():
        print(f"    • {cat}: {count:,} ({count/len(df)*100:.1f}%)")
    
    return df

# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================
def analyze_cross_domain_patterns(df):
    """Analyze cross-domain patterns."""
    print("\n" + "="*70)
    print("ANALYSIS A: CROSS-DOMAIN PATTERNS")
    print("="*70)
    
    results = {}
    
    # 1. State-level summary
    state_summary = df.groupby('state').agg({
        'total_enrol': 'sum',
        'total_demo': 'sum',
        'total_bio': 'sum',
        'total_updates': 'sum',
        'demo_intensity': 'mean',
        'bio_intensity': 'mean',
        'child_attention_gap': 'mean'
    }).reset_index()
    
    state_summary['total_intensity'] = state_summary['total_updates'] / (state_summary['total_enrol'] + EPS)
    state_summary = state_summary.sort_values('total_enrol', ascending=False)
    
    print(f"\n  Top 10 States by Enrolment:")
    for _, row in state_summary.head(10).iterrows():
        print(f"    {row['state']}: E={row['total_enrol']:,.0f}, D={row['total_demo']:,.0f}, B={row['total_bio']:,.0f}")
    
    results['state_summary'] = state_summary
    
    # 2. Child attention gap leaders
    child_gap_pos = state_summary[state_summary['child_attention_gap'] > 0].nlargest(5, 'child_attention_gap')
    child_gap_neg = state_summary[state_summary['child_attention_gap'] < 0].nsmallest(5, 'child_attention_gap')
    
    print(f"\n  States with POSITIVE child attention gap (children over-served in updates):")
    for _, row in child_gap_pos.iterrows():
        print(f"    {row['state']}: gap = {row['child_attention_gap']:+.2f}")
    
    print(f"\n  States with NEGATIVE child attention gap (children under-served in updates):")
    for _, row in child_gap_neg.iterrows():
        print(f"    {row['state']}: gap = {row['child_attention_gap']:+.2f}")
    
    results['child_gap_pos'] = child_gap_pos
    results['child_gap_neg'] = child_gap_neg
    
    return results

def analyze_temporal_joint(df):
    """Joint temporal analysis."""
    print("\n" + "="*70)
    print("ANALYSIS B: JOINT TEMPORAL PATTERNS")
    print("="*70)
    
    # Monthly national trends
    monthly = df.groupby('month').agg({
        'total_enrol': 'sum',
        'total_demo': 'sum',
        'total_bio': 'sum'
    }).reset_index()
    
    print(f"\n  Monthly National Volumes:")
    for _, row in monthly.iterrows():
        print(f"    Month {int(row['month'])}: E={row['total_enrol']:,.0f}, D={row['total_demo']:,.0f}, B={row['total_bio']:,.0f}")
    
    return monthly

def cluster_districts(df):
    """Cluster districts based on cross-domain features."""
    print("\n" + "="*70)
    print("ANALYSIS C: CROSS-DOMAIN CLUSTERING")
    print("="*70)
    
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    
    # District-level summary
    district_summary = df.groupby(['state', 'district']).agg({
        'total_enrol': 'sum',
        'total_demo': 'sum',
        'total_bio': 'sum',
        'demo_intensity': 'mean',
        'bio_intensity': 'mean',
        'enrol_child_share': 'mean',
        'demo_minor_share': 'mean',
        'bio_minor_share': 'mean',
        'child_attention_gap': 'mean'
    }).reset_index()
    
    # Filter low volume
    district_summary = district_summary[district_summary['total_enrol'] > 50]
    
    # Features for clustering
    features = ['total_enrol', 'demo_intensity', 'bio_intensity', 
                'enrol_child_share', 'child_attention_gap']
    
    X = district_summary[features].fillna(0).values
    X[:, 0] = np.log1p(X[:, 0])  # Log transform volume
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Cluster
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    district_summary['cluster'] = kmeans.fit_predict(X_scaled)
    
    # Cluster summary
    cluster_summary = district_summary.groupby('cluster').agg({
        'total_enrol': 'mean',
        'demo_intensity': 'mean',
        'bio_intensity': 'mean',
        'enrol_child_share': 'mean',
        'child_attention_gap': 'mean',
        'district': 'count'
    }).reset_index()
    cluster_summary.columns = ['cluster', 'avg_enrol', 'avg_demo_int', 'avg_bio_int',
                               'avg_child_share', 'avg_child_gap', 'count']
    
    # Assign labels
    labels = []
    for _, row in cluster_summary.iterrows():
        parts = []
        if row['avg_enrol'] > cluster_summary['avg_enrol'].median():
            parts.append("High-Enrol")
        else:
            parts.append("Low-Enrol")
        
        total_int = row['avg_demo_int'] + row['avg_bio_int']
        if total_int > (cluster_summary['avg_demo_int'] + cluster_summary['avg_bio_int']).median():
            parts.append("High-Update")
        else:
            parts.append("Low-Update")
        
        if row['avg_child_gap'] > 0.1:
            parts.append("Child-Over")
        elif row['avg_child_gap'] < -0.1:
            parts.append("Child-Under")
        else:
            parts.append("Balanced")
        
        labels.append(", ".join(parts))
    
    cluster_summary['label'] = labels
    
    print(f"\n  Cross-Domain Cluster Summary:")
    for _, row in cluster_summary.iterrows():
        print(f"    Cluster {int(row['cluster'])}: {int(row['count'])} districts")
        print(f"        {row['label']}")
        print(f"        Enrol={row['avg_enrol']:,.0f}, Demo_Int={row['avg_demo_int']:.2f}, "
              f"Bio_Int={row['avg_bio_int']:.2f}, Child_Gap={row['avg_child_gap']:+.2f}")
    
    return district_summary, cluster_summary

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================
def setup_plots():
    plt.style.use('seaborn-v0_8-whitegrid')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = (14, 10)
    plt.rcParams['font.size'] = 11

def plot_national_overview(monthly, output_dir):
    """National overview plot."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Line chart: all three domains
    axes[0,0].plot(monthly['month'], monthly['total_enrol'], 'o-', label='Enrolment', linewidth=2)
    axes[0,0].plot(monthly['month'], monthly['total_demo'], 's-', label='Demographic', linewidth=2)
    axes[0,0].plot(monthly['month'], monthly['total_bio'], '^-', label='Biometric', linewidth=2)
    axes[0,0].set_title('Monthly National Volume: Enrolment vs Updates', fontweight='bold', fontsize=14)
    axes[0,0].set_xlabel('Month')
    axes[0,0].set_ylabel('Total Count')
    axes[0,0].legend()
    
    # Stacked bar
    x = monthly['month']
    axes[0,1].bar(x, monthly['total_enrol'], label='Enrolment', alpha=0.8)
    axes[0,1].bar(x, monthly['total_demo'], bottom=monthly['total_enrol'], label='Demo Updates', alpha=0.8)
    axes[0,1].bar(x, monthly['total_bio'], bottom=monthly['total_enrol']+monthly['total_demo'], 
                  label='Bio Updates', alpha=0.8)
    axes[0,1].set_title('Stacked Monthly Volume', fontweight='bold', fontsize=14)
    axes[0,1].set_xlabel('Month')
    axes[0,1].legend()
    
    # Ratio comparison
    monthly['update_to_enrol'] = (monthly['total_demo'] + monthly['total_bio']) / (monthly['total_enrol'] + EPS)
    axes[1,0].bar(monthly['month'], monthly['update_to_enrol'], color='purple')
    axes[1,0].set_title('Update-to-Enrolment Ratio by Month', fontweight='bold', fontsize=14)
    axes[1,0].set_xlabel('Month')
    axes[1,0].set_ylabel('Ratio')
    
    # Demo vs Bio comparison
    axes[1,1].bar(monthly['month'] - 0.2, monthly['total_demo'], width=0.4, label='Demographic', color='teal')
    axes[1,1].bar(monthly['month'] + 0.2, monthly['total_bio'], width=0.4, label='Biometric', color='coral')
    axes[1,1].set_title('Demographic vs Biometric Updates', fontweight='bold', fontsize=14)
    axes[1,1].set_xlabel('Month')
    axes[1,1].legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '01_national_overview.png'), dpi=150)
    plt.close()
    print("  ✓ 01_national_overview.png")

def plot_state_comparison(state_summary, output_dir):
    """State comparison plots."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    top_10 = state_summary.head(10)
    
    # Volume comparison
    x = np.arange(len(top_10))
    width = 0.25
    axes[0,0].bar(x - width, top_10['total_enrol']/1e6, width, label='Enrolment')
    axes[0,0].bar(x, top_10['total_demo']/1e6, width, label='Demographic')
    axes[0,0].bar(x + width, top_10['total_bio']/1e6, width, label='Biometric')
    axes[0,0].set_xticks(x)
    axes[0,0].set_xticklabels(top_10['state'], rotation=45, ha='right')
    axes[0,0].set_title('Top 10 States: Volume Comparison (Millions)', fontweight='bold')
    axes[0,0].legend()
    
    # Intensity comparison
    axes[0,1].bar(x - 0.2, top_10['demo_intensity'], 0.4, label='Demo Intensity')
    axes[0,1].bar(x + 0.2, top_10['bio_intensity'], 0.4, label='Bio Intensity')
    axes[0,1].set_xticks(x)
    axes[0,1].set_xticklabels(top_10['state'], rotation=45, ha='right')
    axes[0,1].set_title('Top 10 States: Update Intensity', fontweight='bold')
    axes[0,1].legend()
    
    # Child attention gap
    colors = ['green' if g > 0 else 'red' for g in top_10['child_attention_gap']]
    axes[1,0].barh(top_10['state'], top_10['child_attention_gap'], color=colors)
    axes[1,0].axvline(x=0, color='black', linestyle='-', linewidth=1)
    axes[1,0].set_title('Child Attention Gap (+ = over-served in updates)', fontweight='bold')
    
    # Scatter: Enrolment vs Total Intensity
    scatter = axes[1,1].scatter(
        np.log1p(state_summary['total_enrol']),
        state_summary['total_intensity'],
        c=state_summary['child_attention_gap'],
        cmap='RdYlGn',
        s=100,
        alpha=0.7
    )
    axes[1,1].set_xlabel('Log(Total Enrolment)')
    axes[1,1].set_ylabel('Update Intensity')
    axes[1,1].set_title('States: Enrolment vs Update Intensity', fontweight='bold')
    plt.colorbar(scatter, ax=axes[1,1], label='Child Gap')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '02_state_comparison.png'), dpi=150)
    plt.close()
    print("  ✓ 02_state_comparison.png")

def plot_interaction_categories(df, output_dir):
    """Interaction category analysis."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Category distribution
    cat_counts = df['interaction_category'].value_counts()
    axes[0].pie(cat_counts, labels=cat_counts.index, autopct='%1.1f%%', startangle=90)
    axes[0].set_title('Distribution of Interaction Categories', fontweight='bold')
    
    # Category by average metrics
    cat_summary = df.groupby('interaction_category').agg({
        'total_enrol': 'mean',
        'total_intensity': 'mean',
        'child_attention_gap': 'mean'
    }).reset_index()
    
    x = np.arange(len(cat_summary))
    axes[1].bar(x, cat_summary['total_intensity'], color='steelblue')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(cat_summary['interaction_category'], rotation=45, ha='right')
    axes[1].set_title('Average Update Intensity by Category', fontweight='bold')
    axes[1].set_ylabel('Update Intensity')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '03_interaction_categories.png'), dpi=150)
    plt.close()
    print("  ✓ 03_interaction_categories.png")

def plot_child_gap_analysis(df, output_dir):
    """Child attention gap analysis."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Distribution of child gap
    sns.histplot(data=df, x='child_attention_gap', bins=50, ax=axes[0,0])
    axes[0,0].axvline(x=0, color='red', linestyle='--')
    axes[0,0].set_title('Distribution of Child Attention Gap', fontweight='bold')
    
    # Child share in enrol vs updates
    sample = df[df['total_enrol'] > 100].sample(min(1000, len(df)))
    axes[0,1].scatter(sample['child_share_enrol'], sample['child_share_updates'], alpha=0.3)
    axes[0,1].plot([0, 1], [0, 1], 'r--', label='Parity Line')
    axes[0,1].set_xlabel('Child Share in Enrolment')
    axes[0,1].set_ylabel('Child Share in Updates')
    axes[0,1].set_title('Child Share: Enrolment vs Updates', fontweight='bold')
    axes[0,1].legend()
    
    # Demo vs Bio minor share
    axes[1,0].scatter(sample['demo_minor_share'], sample['bio_minor_share'], alpha=0.3)
    axes[1,0].plot([0, 1], [0, 1], 'r--')
    axes[1,0].set_xlabel('Demo Minor Share')
    axes[1,0].set_ylabel('Bio Minor Share')
    axes[1,0].set_title('Minor Share: Demographic vs Biometric', fontweight='bold')
    
    # Intensity comparison by child gap
    df_filtered = df[df['total_enrol'] > 100]
    df_filtered['gap_category'] = pd.cut(
        df_filtered['child_attention_gap'],
        bins=[-np.inf, -0.2, 0.2, np.inf],
        labels=['Child Under-served', 'Balanced', 'Child Over-served']
    )
    gap_summary = df_filtered.groupby('gap_category').agg({
        'demo_intensity': 'mean',
        'bio_intensity': 'mean'
    }).reset_index()
    
    x = np.arange(len(gap_summary))
    axes[1,1].bar(x - 0.2, gap_summary['demo_intensity'], 0.4, label='Demo')
    axes[1,1].bar(x + 0.2, gap_summary['bio_intensity'], 0.4, label='Bio')
    axes[1,1].set_xticks(x)
    axes[1,1].set_xticklabels(gap_summary['gap_category'])
    axes[1,1].set_title('Update Intensity by Child Gap Category', fontweight='bold')
    axes[1,1].legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '04_child_gap_analysis.png'), dpi=150)
    plt.close()
    print("  ✓ 04_child_gap_analysis.png")

def plot_cross_domain_clusters(district_summary, cluster_summary, output_dir):
    """Cross-domain cluster visualization."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # 2D scatter
    scatter = axes[0].scatter(
        np.log1p(district_summary['total_enrol']),
        district_summary['demo_intensity'] + district_summary['bio_intensity'],
        c=district_summary['cluster'],
        cmap='viridis',
        alpha=0.5,
        s=20
    )
    axes[0].set_xlabel('Log(Total Enrolment)')
    axes[0].set_ylabel('Total Update Intensity')
    axes[0].set_title('District Clusters: Enrolment vs Update Intensity', fontweight='bold')
    plt.colorbar(scatter, ax=axes[0], label='Cluster')
    
    # Cluster sizes
    axes[1].bar(cluster_summary['cluster'], cluster_summary['count'],
                color=plt.cm.viridis(np.linspace(0, 1, 5)))
    axes[1].set_xlabel('Cluster')
    axes[1].set_ylabel('Number of Districts')
    axes[1].set_title('Districts per Cluster', fontweight='bold')
    
    # Add labels
    for i, row in cluster_summary.iterrows():
        axes[1].text(row['cluster'], row['count'] + 10, 
                    row['label'].split(',')[0], ha='center', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '05_cross_domain_clusters.png'), dpi=150)
    plt.close()
    print("  ✓ 05_cross_domain_clusters.png")

def plot_intensity_heatmap(df, output_dir):
    """Intensity heatmaps."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    # State x Month demo intensity
    pivot1 = df.pivot_table(index='state', columns='month', values='demo_intensity', aggfunc='mean')
    top_states = df.groupby('state')['total_enrol'].sum().nlargest(15).index
    pivot1 = pivot1.loc[pivot1.index.isin(top_states)]
    
    sns.heatmap(pivot1, cmap='YlOrRd', annot=True, fmt='.2f', ax=axes[0], linewidths=0.5)
    axes[0].set_title('Demographic Update Intensity: State × Month', fontweight='bold')
    
    # State x Month bio intensity
    pivot2 = df.pivot_table(index='state', columns='month', values='bio_intensity', aggfunc='mean')
    pivot2 = pivot2.loc[pivot2.index.isin(top_states)]
    
    sns.heatmap(pivot2, cmap='YlOrRd', annot=True, fmt='.2f', ax=axes[1], linewidths=0.5)
    axes[1].set_title('Biometric Update Intensity: State × Month', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '06_intensity_heatmaps.png'), dpi=150)
    plt.close()
    print("  ✓ 06_intensity_heatmaps.png")

# ============================================================================
# INSIGHT GENERATION
# ============================================================================
def generate_integrated_insights(df, analysis_results, cluster_summary):
    """Generate integrated insights."""
    insights = []
    
    # 1. Enrolment vs Update balance
    total_enrol = df['total_enrol'].sum()
    total_updates = df['total_updates'].sum()
    ratio = total_updates / total_enrol
    
    insights.append({
        'title': 'Aadhaar Interaction Intensity',
        'finding': f"For every enrolment, there are {ratio:.1f}x updates (Demo + Bio combined)",
        'interpretation': 'High update intensity indicates active ongoing engagement with Aadhaar system',
        'action': 'Monitor regions deviating significantly from this ratio'
    })
    
    # 2. Child attention gap
    child_gap_neg = analysis_results['child_gap_neg']
    if len(child_gap_neg) > 0:
        worst_state = child_gap_neg.iloc[0]['state']
        worst_gap = child_gap_neg.iloc[0]['child_attention_gap']
        insights.append({
            'title': 'Child Update Gap Identified',
            'finding': f"{worst_state} has worst child attention gap ({worst_gap:.2f})",
            'interpretation': 'Children form large share of enrolments but small share of updates',
            'action': 'Target child update drives in under-served states'
        })
    
    # 3. Mature vs Emerging
    cat_dist = df['interaction_category'].value_counts()
    mature_pct = cat_dist.get('Mature (High E, High U)', 0) / len(df) * 100
    emerging_pct = cat_dist.get('Emerging (High E, Low U)', 0) / len(df) * 100
    
    insights.append({
        'title': 'Regional Maturity Distribution',
        'finding': f'{mature_pct:.1f}% mature (high enrol + high updates), {emerging_pct:.1f}% emerging (high enrol + low updates)',
        'interpretation': 'Emerging regions have onboarded users but need update awareness',
        'action': 'Focus update campaigns in emerging regions'
    })
    
    # 4. Demo vs Bio split
    total_demo = df['total_demo'].sum()
    total_bio = df['total_bio'].sum()
    bio_share = total_bio / (total_demo + total_bio) * 100
    
    insights.append({
        'title': 'Update Type Distribution',
        'finding': f'Biometric: {bio_share:.1f}%, Demographic: {100-bio_share:.1f}%',
        'interpretation': 'Biometric updates dominate, indicating fingerprint/iris refresh activity',
        'action': 'Review biometric capture quality in high-bio regions'
    })
    
    # 5. Cluster insights
    insights.append({
        'title': 'Five Distinct Behavioral Patterns',
        'finding': f'{len(cluster_summary)} cross-domain clusters identified across districts',
        'interpretation': 'Districts can be grouped by enrolment-update interaction patterns',
        'action': 'Tailor interventions based on cluster characteristics'
    })
    
    return insights

def generate_integrated_kpis(df):
    """Generate integrated KPIs."""
    kpis = {
        'total_enrolments': int(df['total_enrol'].sum()),
        'total_demo_updates': int(df['total_demo'].sum()),
        'total_bio_updates': int(df['total_bio'].sum()),
        'total_updates': int(df['total_updates'].sum()),
        'update_to_enrol_ratio': df['total_updates'].sum() / df['total_enrol'].sum(),
        'avg_demo_intensity': df[df['demo_intensity'] < 100]['demo_intensity'].mean(),
        'avg_bio_intensity': df[df['bio_intensity'] < 100]['bio_intensity'].mean(),
        'avg_child_attention_gap': df['child_attention_gap'].mean(),
        'states_analyzed': int(df['state'].nunique()),
        'districts_analyzed': int(df[['state', 'district']].drop_duplicates().shape[0]),
        'mature_regions_pct': (df['interaction_category'] == 'Mature (High E, High U)').mean() * 100,
        'underserved_regions_pct': (df['interaction_category'] == 'Under-served (Low E, Low U)').mean() * 100,
    }
    return kpis

# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    print("="*80)
    print("UIDAI DATA HACKATHON 2026 - INTEGRATED CROSS-DOMAIN ANALYSIS")
    print("Combining Enrolment + Demographic + Biometric for Ultimate Insights")
    print("="*80)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PLOTS_DIR, exist_ok=True)
    
    # Load data
    enrol, demo, bio = load_all_data()
    
    # Preprocess
    enrol, demo, bio = preprocess_all(enrol, demo, bio)
    
    # Aggregate
    enrol_agg, demo_agg, bio_agg = aggregate_all(enrol, demo, bio)
    
    # Integrate
    merged = integrate_datasets(enrol_agg, demo_agg, bio_agg)
    
    # Cross-domain metrics
    merged = compute_cross_domain_metrics(merged)
    
    # Analyses
    analysis_results = analyze_cross_domain_patterns(merged)
    monthly = analyze_temporal_joint(merged)
    district_clusters, cluster_summary = cluster_districts(merged)
    
    # Visualizations
    print("\n" + "="*70)
    print("PHASE 6: GENERATING VISUALIZATIONS")
    print("="*70)
    setup_plots()
    
    plot_national_overview(monthly, PLOTS_DIR)
    plot_state_comparison(analysis_results['state_summary'], PLOTS_DIR)
    plot_interaction_categories(merged, PLOTS_DIR)
    plot_child_gap_analysis(merged, PLOTS_DIR)
    plot_cross_domain_clusters(district_clusters, cluster_summary, PLOTS_DIR)
    plot_intensity_heatmap(merged, PLOTS_DIR)
    
    # Insights
    print("\n" + "="*70)
    print("PHASE 7: GENERATING INTEGRATED INSIGHTS")
    print("="*70)
    
    insights = generate_integrated_insights(merged, analysis_results, cluster_summary)
    kpis = generate_integrated_kpis(merged)
    
    print("\n📊 INTEGRATED KEY PERFORMANCE INDICATORS:")
    for k, v in kpis.items():
        if isinstance(v, float):
            if 'pct' in k or 'ratio' in k:
                print(f"  • {k}: {v:.2f}")
            else:
                print(f"  • {k}: {v:.4f}")
        else:
            print(f"  • {k}: {v:,}")
    
    print("\n💡 TOP INTEGRATED INSIGHTS:")
    for i, ins in enumerate(insights, 1):
        print(f"\n  {i}. {ins['title']}")
        print(f"     Finding: {ins['finding']}")
        print(f"     Action: {ins['action']}")
    
    # Export
    print("\n" + "="*70)
    print("PHASE 8: EXPORTING RESULTS")
    print("="*70)
    
    merged.to_csv(os.path.join(OUTPUT_DIR, 'integrated_data.csv'), index=False)
    district_clusters.to_csv(os.path.join(OUTPUT_DIR, 'district_clusters.csv'), index=False)
    analysis_results['state_summary'].to_csv(os.path.join(OUTPUT_DIR, 'state_summary.csv'), index=False)
    pd.DataFrame([kpis]).to_csv(os.path.join(OUTPUT_DIR, 'kpis.csv'), index=False)
    
    print(f"  ✓ Saved all outputs to {OUTPUT_DIR}")
    
    print("\n" + "="*80)
    print("✅ INTEGRATED CROSS-DOMAIN ANALYSIS COMPLETE!")
    print(f"📁 Output: {OUTPUT_DIR}")
    print(f"📊 Plots: {PLOTS_DIR}")
    print("="*80)
    
    return merged, insights, kpis

if __name__ == "__main__":
    main()
