#!/usr/bin/env python3
"""
UIDAI Data Hackathon 2026 - Deep Enrolment Analysis
Focus: Age-Profile Dynamics, Regional Gaps, New Enrollee Patterns

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
DATA_DIR = "/Users/ayushpatel/Documents/Projects/UIDAI/UIDAI/api_data_aadhar_enrolment"
OUTPUT_DIR = "/Users/ayushpatel/Documents/Projects/UIDAI/UIDAI/enrolment_analysis"
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
def load_enrolment_data():
    """Load all enrolment CSV files."""
    print("\n" + "="*60)
    print("PHASE 1: DATA LOADING")
    print("="*60)
    
    files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    dfs = []
    
    for f in sorted(files):
        df = pd.read_csv(f)
        print(f"  ✓ Loaded {os.path.basename(f)}: {len(df):,} rows")
        dfs.append(df)
    
    data = pd.concat(dfs, ignore_index=True)
    print(f"\n  📊 Total records: {len(data):,}")
    return data

def preprocess_data(df):
    """Clean and prepare data."""
    print("\n" + "="*60)
    print("PHASE 2: DATA PREPROCESSING")
    print("="*60)
    
    df = df.copy()
    
    # Parse dates
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['month_name'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['week'] = df['date'].dt.isocalendar().week
    df['day_of_week'] = df['date'].dt.day_name()
    df['is_weekend'] = df['day_of_week'].isin(['Saturday', 'Sunday'])
    
    # Standardize state names
    df['state'] = df['state'].astype(str).str.strip().str.title()
    df['state'] = df['state'].replace(STATE_FIX)
    
    # Standardize district names
    df['district'] = df['district'].astype(str).str.strip().str.title()
    
    # Check for missing/negative values
    for col in ['age_0_5', 'age_5_17', 'age_18_greater']:
        negatives = (df[col] < 0).sum()
        if negatives > 0:
            print(f"  ⚠️ {negatives} negative values in {col} (set to 0)")
            df.loc[df[col] < 0, col] = 0
    
    # Check for duplicates
    dupes = df.duplicated(subset=['date', 'pincode']).sum()
    if dupes > 0:
        print(f"  ⚠️ {dupes} duplicate date-pincode rows (keeping first)")
        df = df.drop_duplicates(subset=['date', 'pincode'], keep='first')
    
    # Check for extreme outliers
    for col in ['age_0_5', 'age_5_17', 'age_18_greater']:
        q99 = df[col].quantile(0.99)
        outliers = (df[col] > q99 * 10).sum()
        if outliers > 0:
            print(f"  ⚠️ {outliers} extreme outliers in {col} (capped)")
            df[col] = df[col].clip(upper=q99 * 10)
    
    print(f"\n  ✓ Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"  ✓ States: {df['state'].nunique()}")
    print(f"  ✓ Districts: {df['district'].nunique()}")
    print(f"  ✓ Pincodes: {df['pincode'].nunique()}")
    
    return df

# ============================================================================
# FEATURE ENGINEERING
# ============================================================================
def engineer_features(df):
    """Create enrolment-specific features."""
    print("\n" + "="*60)
    print("PHASE 3: FEATURE ENGINEERING")
    print("="*60)
    
    df = df.copy()
    eps = 1e-10
    
    # Total enrolments
    df['total_enrol'] = df['age_0_5'] + df['age_5_17'] + df['age_18_greater']
    
    # Age shares
    df['share_0_5'] = df['age_0_5'] / (df['total_enrol'] + eps)
    df['share_5_17'] = df['age_5_17'] / (df['total_enrol'] + eps)
    df['share_18_plus'] = df['age_18_greater'] / (df['total_enrol'] + eps)
    
    # Cap shares where total is 0
    df.loc[df['total_enrol'] == 0, ['share_0_5', 'share_5_17', 'share_18_plus']] = 0
    
    # Ratios
    df['child_to_adult_ratio'] = (df['age_0_5'] + df['age_5_17']) / (df['age_18_greater'] + eps)
    df['infant_to_child_ratio'] = df['age_0_5'] / (df['age_5_17'] + eps)
    
    # Cap extreme ratios
    df['child_to_adult_ratio'] = df['child_to_adult_ratio'].clip(upper=100)
    df['infant_to_child_ratio'] = df['infant_to_child_ratio'].clip(upper=100)
    
    print(f"  ✓ Created age-share metrics: share_0_5, share_5_17, share_18_plus")
    print(f"  ✓ Created ratio metrics: child_to_adult_ratio, infant_to_child_ratio")
    return df

def aggregate_levels(df):
    """Create aggregations at different levels."""
    print("\n" + "="*60)
    print("PHASE 4: AGGREGATION")
    print("="*60)
    
    eps = 1e-10
    
    # District-Date level
    district_date = df.groupby(['date', 'year', 'month', 'day_of_week', 'is_weekend', 
                                 'state', 'district']).agg({
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum',
        'total_enrol': 'sum',
        'pincode': 'nunique'
    }).reset_index()
    district_date.rename(columns={'pincode': 'active_pincodes'}, inplace=True)
    
    # Recalculate shares
    district_date['share_0_5'] = district_date['age_0_5'] / (district_date['total_enrol'] + eps)
    district_date['share_5_17'] = district_date['age_5_17'] / (district_date['total_enrol'] + eps)
    district_date['share_18_plus'] = district_date['age_18_greater'] / (district_date['total_enrol'] + eps)
    district_date['child_to_adult_ratio'] = (district_date['age_0_5'] + district_date['age_5_17']) / (district_date['age_18_greater'] + eps)
    
    # State-Month level
    state_month = df.groupby(['year', 'month', 'state']).agg({
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum',
        'total_enrol': 'sum',
        'district': 'nunique',
        'pincode': 'nunique'
    }).reset_index()
    state_month.rename(columns={'district': 'active_districts', 'pincode': 'active_pincodes'}, inplace=True)
    state_month['share_0_5'] = state_month['age_0_5'] / (state_month['total_enrol'] + eps)
    state_month['share_5_17'] = state_month['age_5_17'] / (state_month['total_enrol'] + eps)
    state_month['share_18_plus'] = state_month['age_18_greater'] / (state_month['total_enrol'] + eps)
    
    # State-Date level
    state_date = df.groupby(['date', 'year', 'month', 'day_of_week', 'is_weekend', 'state']).agg({
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum',
        'total_enrol': 'sum'
    }).reset_index()
    
    # National-Date level
    national_date = df.groupby(['date', 'year', 'month', 'day_of_week', 'is_weekend']).agg({
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum',
        'total_enrol': 'sum'
    }).reset_index()
    national_date['share_0_5'] = national_date['age_0_5'] / (national_date['total_enrol'] + eps)
    national_date['share_5_17'] = national_date['age_5_17'] / (national_date['total_enrol'] + eps)
    national_date['share_18_plus'] = national_date['age_18_greater'] / (national_date['total_enrol'] + eps)
    
    # National-Month level
    national_month = df.groupby(['year', 'month']).agg({
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum',
        'total_enrol': 'sum'
    }).reset_index()
    national_month['share_0_5'] = national_month['age_0_5'] / (national_month['total_enrol'] + eps)
    national_month['share_5_17'] = national_month['age_5_17'] / (national_month['total_enrol'] + eps)
    national_month['share_18_plus'] = national_month['age_18_greater'] / (national_month['total_enrol'] + eps)
    
    print(f"  ✓ District-Date: {len(district_date):,} records")
    print(f"  ✓ State-Date: {len(state_date):,} records")
    print(f"  ✓ State-Month: {len(state_month):,} records")
    print(f"  ✓ National-Date: {len(national_date):,} records")
    print(f"  ✓ National-Month: {len(national_month):,} records")
    
    return district_date, state_date, state_month, national_date, national_month

def calculate_stability_metrics(district_date):
    """Calculate stability and volatility metrics."""
    
    volatility = district_date.groupby(['state', 'district']).agg({
        'total_enrol': ['mean', 'std', 'count'],
        'share_0_5': ['mean', 'std'],
        'share_5_17': ['mean', 'std']
    }).reset_index()
    volatility.columns = ['state', 'district', 'avg_enrol', 'std_enrol', 'obs_count',
                          'avg_share_0_5', 'std_share_0_5', 'avg_share_5_17', 'std_share_5_17']
    
    # CV
    volatility['cv_enrol'] = volatility['std_enrol'] / (volatility['avg_enrol'] + 1e-10)
    
    return volatility

def calculate_concentration(df):
    """Calculate Gini/HHI concentration metrics."""
    
    def gini(values):
        values = np.array(values)
        values = values[values > 0]
        if len(values) < 2:
            return 0
        sorted_values = np.sort(values)
        n = len(sorted_values)
        cumsum = np.cumsum(sorted_values)
        return (2 * np.sum((np.arange(1, n+1) * sorted_values))) / (n * cumsum[-1]) - (n + 1) / n
    
    # Gini per state (pincode concentration)
    state_gini = df.groupby('state').apply(
        lambda x: gini(x.groupby('pincode')['total_enrol'].sum().values)
    ).reset_index()
    state_gini.columns = ['state', 'gini_pincode']
    
    return state_gini

# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================
def analyze_age_profile(df, district_date, state_month):
    """Analyze age-profile of enrolments."""
    print("\n" + "="*60)
    print("ANALYSIS A: AGE-PROFILE OF ENROLMENTS")
    print("="*60)
    
    results = {}
    eps = 1e-10
    
    # 1. State-level age shares
    state_agg = df.groupby('state').agg({
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum',
        'total_enrol': 'sum'
    }).reset_index()
    state_agg['share_0_5'] = state_agg['age_0_5'] / state_agg['total_enrol']
    state_agg['share_5_17'] = state_agg['age_5_17'] / state_agg['total_enrol']
    state_agg['share_18_plus'] = state_agg['age_18_greater'] / state_agg['total_enrol']
    state_agg['child_share'] = (state_agg['age_0_5'] + state_agg['age_5_17']) / state_agg['total_enrol']
    
    print(f"\n  Top 5 States by Infant (0-5) Share:")
    for _, row in state_agg.nlargest(5, 'share_0_5').iterrows():
        print(f"    • {row['state']}: {row['share_0_5']:.1%}")
    
    print(f"\n  Top 5 States by School-age (5-17) Share:")
    for _, row in state_agg.nlargest(5, 'share_5_17').iterrows():
        print(f"    • {row['state']}: {row['share_5_17']:.1%}")
    
    results['state_agg'] = state_agg
    
    # 2. District-level age profile
    district_agg = df.groupby(['state', 'district']).agg({
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum',
        'total_enrol': 'sum'
    }).reset_index()
    district_agg = district_agg[district_agg['total_enrol'] > 50]  # Filter low volume
    district_agg['share_0_5'] = district_agg['age_0_5'] / district_agg['total_enrol']
    district_agg['share_5_17'] = district_agg['age_5_17'] / district_agg['total_enrol']
    district_agg['share_18_plus'] = district_agg['age_18_greater'] / district_agg['total_enrol']
    district_agg['child_to_adult_ratio'] = (district_agg['age_0_5'] + district_agg['age_5_17']) / (district_agg['age_18_greater'] + eps)
    
    # Classify districts
    median_ratio = district_agg['child_to_adult_ratio'].median()
    district_agg['age_category'] = pd.cut(
        district_agg['child_to_adult_ratio'],
        bins=[0, 0.5, 1.5, np.inf],
        labels=['Adult-Heavy', 'Balanced', 'Child-Heavy']
    )
    
    category_counts = district_agg['age_category'].value_counts()
    print(f"\n  District Age Categories:")
    for cat, count in category_counts.items():
        print(f"    • {cat}: {count} districts")
    
    results['district_agg'] = district_agg
    
    # 3. Outliers (high child share)
    q75 = district_agg['share_0_5'].quantile(0.75)
    q25 = district_agg['share_0_5'].quantile(0.25)
    iqr = q75 - q25
    high_infant_threshold = q75 + 1.5 * iqr
    
    high_infant_districts = district_agg[district_agg['share_0_5'] > high_infant_threshold]
    print(f"\n  High Infant (0-5) Share Outliers: {len(high_infant_districts)} districts")
    
    results['high_infant_districts'] = high_infant_districts
    
    # 4. Monthly trend
    monthly = state_month.groupby('month').agg({
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum',
        'total_enrol': 'sum'
    }).reset_index()
    monthly['share_0_5'] = monthly['age_0_5'] / monthly['total_enrol']
    monthly['share_5_17'] = monthly['age_5_17'] / monthly['total_enrol']
    
    print(f"\n  Monthly Age Share Trend:")
    for _, row in monthly.iterrows():
        print(f"    Month {int(row['month'])}: 0-5={row['share_0_5']:.1%}, 5-17={row['share_5_17']:.1%}")
    
    results['monthly_trend'] = monthly
    
    return results

def analyze_temporal_patterns(national_date, state_date):
    """Analyze temporal patterns."""
    print("\n" + "="*60)
    print("ANALYSIS B: TEMPORAL PATTERNS")
    print("="*60)
    
    results = {}
    
    # 1. Weekend effect
    weekend_stats = national_date.groupby('is_weekend')['total_enrol'].mean()
    weekday_avg = weekend_stats.get(False, 0)
    weekend_avg = weekend_stats.get(True, 0)
    weekend_change = (weekend_avg - weekday_avg) / weekday_avg * 100 if weekday_avg > 0 else 0
    
    print(f"\n  Weekend Effect:")
    print(f"    Weekday avg: {weekday_avg:,.0f}")
    print(f"    Weekend avg: {weekend_avg:,.0f}")
    print(f"    Weekend change: {weekend_change:+.1f}%")
    
    results['weekend_change'] = weekend_change
    
    # 2. Day of week
    dow_pattern = national_date.groupby('day_of_week')['total_enrol'].mean().reindex([
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    ])
    print(f"\n  Day of Week Pattern:")
    for day, val in dow_pattern.items():
        print(f"    {day}: {val:,.0f}")
    
    results['dow_pattern'] = dow_pattern
    
    # 3. Monthly totals
    monthly = national_date.groupby('month')['total_enrol'].sum()
    peak_month = monthly.idxmax()
    print(f"\n  Peak Month: {peak_month} ({monthly[peak_month]:,.0f} enrolments)")
    
    results['monthly_totals'] = monthly
    
    return results

def analyze_spatial_patterns(df, district_agg, concentration):
    """Analyze spatial patterns."""
    print("\n" + "="*60)
    print("ANALYSIS C: SPATIAL PATTERNS")
    print("="*60)
    
    results = {}
    
    # 1. State ranking
    state_totals = df.groupby('state')['total_enrol'].sum().sort_values(ascending=False)
    national_total = state_totals.sum()
    
    print(f"\n  Top 10 States by Enrolment:")
    for state, vol in state_totals.head(10).items():
        pct = vol / national_total * 100
        print(f"    {state}: {vol:,.0f} ({pct:.1f}%)")
    
    results['state_totals'] = state_totals
    
    # 2. Low enrolment districts
    bottom_decile = district_agg['total_enrol'].quantile(0.1)
    low_enrol_districts = district_agg[district_agg['total_enrol'] <= bottom_decile]
    print(f"\n  Low-Enrolment Districts (bottom 10%): {len(low_enrol_districts)}")
    
    results['low_enrol_districts'] = low_enrol_districts
    
    # 3. Concentration
    high_conc = concentration[concentration['gini_pincode'] > 0.6]
    print(f"\n  States with high pincode concentration (Gini>0.6): {len(high_conc)}")
    
    results['concentration'] = concentration
    
    return results

def detect_anomalies(district_date, national_date):
    """Detect anomalies."""
    print("\n" + "="*60)
    print("ANALYSIS D: ANOMALY DETECTION")
    print("="*60)
    
    # Z-score detection
    mean_val = district_date['total_enrol'].mean()
    std_val = district_date['total_enrol'].std()
    district_date = district_date.copy()
    district_date['zscore'] = (district_date['total_enrol'] - mean_val) / std_val
    
    anomalies = district_date[abs(district_date['zscore']) > 3].copy()
    anomalies['anomaly_type'] = np.where(anomalies['zscore'] > 0, 'High Spike', 'Low Drop')
    
    print(f"\n  Anomalies detected: {len(anomalies)}")
    print(f"    High Spikes: {(anomalies['anomaly_type'] == 'High Spike').sum()}")
    print(f"    Low Drops: {(anomalies['anomaly_type'] == 'Low Drop').sum()}")
    
    return anomalies

def cluster_districts(district_agg, volatility):
    """Cluster districts by behavior."""
    print("\n" + "="*60)
    print("ANALYSIS E: DISTRICT CLUSTERING")
    print("="*60)
    
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    
    # Merge data
    cluster_data = district_agg.merge(
        volatility[['state', 'district', 'cv_enrol']],
        on=['state', 'district'],
        how='left'
    )
    cluster_data = cluster_data[cluster_data['total_enrol'] > 50]
    cluster_data['cv_enrol'] = cluster_data['cv_enrol'].fillna(0)
    
    # Features
    cluster_data['child_share'] = cluster_data['share_0_5'] + cluster_data['share_5_17']
    features = ['total_enrol', 'child_share', 'cv_enrol']
    X = cluster_data[features].values
    
    # Log transform volume
    X[:, 0] = np.log1p(X[:, 0])
    
    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Cluster
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    cluster_data['cluster'] = kmeans.fit_predict(X_scaled)
    
    # Summary
    cluster_summary = cluster_data.groupby('cluster').agg({
        'total_enrol': 'mean',
        'child_share': 'mean',
        'cv_enrol': 'mean',
        'district': 'count'
    }).reset_index()
    cluster_summary.columns = ['cluster', 'avg_enrol', 'avg_child_share', 'avg_cv', 'count']
    
    # Labels
    labels = []
    for _, row in cluster_summary.iterrows():
        vol = "High-Vol" if row['avg_enrol'] > cluster_summary['avg_enrol'].median() else "Low-Vol"
        age = "Child-Heavy" if row['avg_child_share'] > 0.5 else "Adult-Heavy"
        stab = "Volatile" if row['avg_cv'] > cluster_summary['avg_cv'].median() else "Stable"
        labels.append(f"{vol}, {age}, {stab}")
    cluster_summary['label'] = labels
    
    print(f"\n  Cluster Summary:")
    for _, row in cluster_summary.iterrows():
        print(f"    Cluster {int(row['cluster'])}: {int(row['count'])} districts")
        print(f"        {row['label']}")
        print(f"        Avg enrol={row['avg_enrol']:,.0f}, child={row['avg_child_share']:.1%}, CV={row['avg_cv']:.2f}")
    
    return cluster_data, cluster_summary

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================
def setup_plots():
    plt.style.use('seaborn-v0_8-whitegrid')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 11

def plot_national_timeseries(national_date, national_month, output_dir):
    """National time series."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Daily total
    axes[0,0].plot(national_date['date'], national_date['total_enrol'], 'b-', linewidth=1)
    axes[0,0].set_title('National Daily Enrolments', fontweight='bold')
    axes[0,0].set_ylabel('Total Enrolments')
    axes[0,0].tick_params(axis='x', rotation=45)
    
    # Age composition stacked
    axes[0,1].stackplot(national_date['date'],
                        national_date['age_0_5'],
                        national_date['age_5_17'],
                        national_date['age_18_greater'],
                        labels=['0-5', '5-17', '18+'], alpha=0.8)
    axes[0,1].set_title('Age Group Composition Over Time', fontweight='bold')
    axes[0,1].legend(loc='upper right')
    axes[0,1].tick_params(axis='x', rotation=45)
    
    # Monthly totals
    axes[1,0].bar(national_month['month'], national_month['total_enrol'], color='teal')
    axes[1,0].set_title('Monthly Total Enrolments', fontweight='bold')
    axes[1,0].set_xlabel('Month')
    
    # Age share evolution
    axes[1,1].plot(national_month['month'], national_month['share_0_5'], 'o-', label='0-5', linewidth=2)
    axes[1,1].plot(national_month['month'], national_month['share_5_17'], 's-', label='5-17', linewidth=2)
    axes[1,1].plot(national_month['month'], national_month['share_18_plus'], '^-', label='18+', linewidth=2)
    axes[1,1].set_title('Monthly Age Share Evolution', fontweight='bold')
    axes[1,1].set_xlabel('Month')
    axes[1,1].set_ylabel('Share')
    axes[1,1].legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '01_national_timeseries.png'), dpi=150)
    plt.close()
    print("  ✓ 01_national_timeseries.png")

def plot_state_heatmaps(state_month, output_dir):
    """State heatmaps."""
    fig, axes = plt.subplots(1, 2, figsize=(18, 12))
    
    # Volume heatmap
    pivot1 = state_month.pivot_table(index='state', columns='month', values='total_enrol', aggfunc='sum')
    top_states = pivot1.sum(axis=1).nlargest(15).index
    pivot1 = pivot1.loc[top_states]
    
    sns.heatmap(pivot1, cmap='YlOrRd', annot=True, fmt='.0f', ax=axes[0], linewidths=0.5)
    axes[0].set_title('Enrolments by State × Month', fontweight='bold', fontsize=14)
    
    # Child share heatmap
    state_month['child_share'] = state_month['share_0_5'] + state_month['share_5_17']
    pivot2 = state_month.pivot_table(index='state', columns='month', values='child_share', aggfunc='mean')
    pivot2 = pivot2.loc[top_states]
    
    sns.heatmap(pivot2, cmap='RdYlGn', annot=True, fmt='.1%', ax=axes[1], linewidths=0.5)
    axes[1].set_title('Child Share (0-17) by State × Month', fontweight='bold', fontsize=14)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '02_state_heatmaps.png'), dpi=150)
    plt.close()
    print("  ✓ 02_state_heatmaps.png")

def plot_age_analysis(state_agg, district_agg, output_dir):
    """Age analysis plots."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Top states by infant share
    top_infant = state_agg.nlargest(15, 'share_0_5')
    axes[0,0].barh(top_infant['state'], top_infant['share_0_5'], color='salmon')
    axes[0,0].set_title('Top 15 States by Infant (0-5) Share', fontweight='bold')
    axes[0,0].set_xlabel('Share 0-5')
    
    # Top states by volume
    top_vol = state_agg.nlargest(15, 'total_enrol')
    axes[0,1].barh(top_vol['state'], top_vol['total_enrol'], color='steelblue')
    axes[0,1].set_title('Top 15 States by Enrolment Volume', fontweight='bold')
    axes[0,1].set_xlabel('Total Enrolments')
    
    # Distribution of child-to-adult ratio
    sns.histplot(data=district_agg, x='child_to_adult_ratio', bins=50, ax=axes[1,0])
    axes[1,0].axvline(x=1.0, color='red', linestyle='--', alpha=0.7, label='Balanced')
    axes[1,0].set_title('Distribution of Child-to-Adult Ratio', fontweight='bold')
    axes[1,0].set_xlim(0, 10)
    axes[1,0].legend()
    
    # Scatter: Volume vs Child Share
    district_agg['child_share'] = district_agg['share_0_5'] + district_agg['share_5_17']
    sns.scatterplot(data=district_agg, x='total_enrol', y='child_share', alpha=0.4, ax=axes[1,1])
    axes[1,1].axhline(y=0.5, color='red', linestyle='--', alpha=0.5)
    axes[1,1].set_title('District Volume vs Child Share', fontweight='bold')
    axes[1,1].set_xscale('log')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '03_age_analysis.png'), dpi=150)
    plt.close()
    print("  ✓ 03_age_analysis.png")

def plot_temporal_patterns(national_date, dow_pattern, output_dir):
    """Temporal patterns."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Day of week
    dow_df = dow_pattern.reset_index()
    dow_df.columns = ['day', 'avg']
    sns.barplot(data=dow_df, x='day', y='avg', ax=axes[0,0], palette='viridis')
    axes[0,0].set_title('Average Enrolments by Day of Week', fontweight='bold')
    axes[0,0].tick_params(axis='x', rotation=45)
    
    # Weekend comparison
    weekend_comp = national_date.groupby('is_weekend')['total_enrol'].mean()
    axes[0,1].bar(['Weekday', 'Weekend'], weekend_comp.values, color=['steelblue', 'coral'])
    axes[0,1].set_title('Weekday vs Weekend Average', fontweight='bold')
    
    # Monthly by age
    monthly = national_date.groupby('month').agg({
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum'
    })
    monthly.plot(kind='bar', ax=axes[1,0], stacked=True)
    axes[1,0].set_title('Monthly Enrolments by Age Band', fontweight='bold')
    axes[1,0].legend(['0-5', '5-17', '18+'])
    
    # Monthly share evolution
    monthly_share = national_date.groupby('month')[['share_0_5', 'share_5_17', 'share_18_plus']].mean()
    monthly_share.plot(ax=axes[1,1], marker='o')
    axes[1,1].set_title('Monthly Age Share Evolution', fontweight='bold')
    axes[1,1].legend(['0-5', '5-17', '18+'])
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '04_temporal_patterns.png'), dpi=150)
    plt.close()
    print("  ✓ 04_temporal_patterns.png")

def plot_concentration(concentration, output_dir):
    """Concentration analysis."""
    conc_sorted = concentration.sort_values('gini_pincode', ascending=True).tail(20)
    
    plt.figure(figsize=(12, 8))
    plt.barh(conc_sorted['state'], conc_sorted['gini_pincode'], color='crimson')
    plt.title('Pincode Concentration by State (Gini Coefficient)', fontweight='bold', fontsize=14)
    plt.xlabel('Gini (higher = more concentrated)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '05_concentration.png'), dpi=150)
    plt.close()
    print("  ✓ 05_concentration.png")

def plot_clusters(cluster_data, cluster_summary, output_dir):
    """Cluster visualization."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    scatter = axes[0].scatter(
        np.log1p(cluster_data['total_enrol']),
        cluster_data['child_share'],
        c=cluster_data['cluster'],
        cmap='viridis',
        alpha=0.5,
        s=20
    )
    axes[0].set_xlabel('Log(Total Enrolments)')
    axes[0].set_ylabel('Child Share (0-17)')
    axes[0].set_title('District Clusters: Volume vs Child Share', fontweight='bold')
    plt.colorbar(scatter, ax=axes[0], label='Cluster')
    
    axes[1].bar(cluster_summary['cluster'], cluster_summary['count'],
                color=plt.cm.viridis(np.linspace(0, 1, 5)))
    axes[1].set_xlabel('Cluster')
    axes[1].set_ylabel('Number of Districts')
    axes[1].set_title('Districts per Cluster', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '06_clusters.png'), dpi=150)
    plt.close()
    print("  ✓ 06_clusters.png")

def plot_top_districts(district_agg, output_dir):
    """Top districts."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    # Top by volume
    top = district_agg.nlargest(25, 'total_enrol')
    top['label'] = top['district'] + ' (' + top['state'].str[:3] + ')'
    axes[0].barh(top['label'], top['total_enrol'], color='steelblue')
    axes[0].set_title('Top 25 Districts by Enrolment', fontweight='bold')
    
    # Top by child share
    district_agg['child_share'] = district_agg['share_0_5'] + district_agg['share_5_17']
    top_child = district_agg[district_agg['total_enrol'] > 100].nlargest(25, 'child_share')
    top_child['label'] = top_child['district'] + ' (' + top_child['state'].str[:3] + ')'
    axes[1].barh(top_child['label'], top_child['child_share'], color='coral')
    axes[1].axvline(x=0.5, color='red', linestyle='--', alpha=0.7)
    axes[1].set_title('Top 25 Districts by Child Share (min 100 enrolments)', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '07_top_districts.png'), dpi=150)
    plt.close()
    print("  ✓ 07_top_districts.png")

def plot_volatility(volatility, output_dir):
    """Volatility analysis."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    top_volatile = volatility.nlargest(20, 'cv_enrol')
    top_volatile['label'] = top_volatile['district'] + ' (' + top_volatile['state'].str[:3] + ')'
    
    axes[0].barh(top_volatile['label'], top_volatile['cv_enrol'], color='purple')
    axes[0].set_title('Most Volatile Districts (CV of Enrolments)', fontweight='bold')
    
    sns.histplot(data=volatility, x='cv_enrol', bins=50, ax=axes[1])
    axes[1].set_title('Distribution of Enrolment Volatility', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '08_volatility.png'), dpi=150)
    plt.close()
    print("  ✓ 08_volatility.png")

# ============================================================================
# INSIGHT GENERATION
# ============================================================================
def generate_insights(age_results, temporal_results, spatial_results, cluster_summary):
    """Generate insights."""
    insights = []
    
    # 1. Child enrolment patterns
    state_agg = age_results['state_agg']
    top_child_state = state_agg.nlargest(1, 'child_share').iloc[0]
    insights.append({
        'title': 'Child Enrolment Leadership',
        'finding': f"{top_child_state['state']} leads with {top_child_state['child_share']:.1%} child (0-17) enrolment share",
        'interpretation': 'Strong early-life enrolment capture in this state',
        'action': 'Study and replicate successful child enrolment strategies'
    })
    
    # 2. Adult-heavy regions
    adult_districts = age_results['district_agg'][age_results['district_agg']['age_category'] == 'Adult-Heavy']
    insights.append({
        'title': 'Adult Catch-up Zones Identified',
        'finding': f"{len(adult_districts)} districts are adult-heavy (child:adult ratio < 0.5)",
        'interpretation': 'These areas are still enrolling significant adult population',
        'action': 'Adult catch-up campaigns may be most effective here'
    })
    
    # 3. Weekend patterns
    weekend_change = temporal_results['weekend_change']
    insights.append({
        'title': 'Weekend Enrolment Pattern',
        'finding': f"Weekend enrolments are {weekend_change:+.1f}% vs weekdays",
        'interpretation': 'Indicates weekend service availability and demand',
        'action': 'Optimize weekend staffing based on demand patterns'
    })
    
    # 4. Low enrolment gaps
    low_count = len(spatial_results['low_enrol_districts'])
    insights.append({
        'title': 'Persistent Low-Enrolment Districts',
        'finding': f"{low_count} districts in bottom 10% of enrolments",
        'interpretation': 'Potential geographic barriers, limited centres, or awareness issues',
        'action': 'Targeted enrolment drives and mobile centre deployment'
    })
    
    # 5. Behavioral segments
    insights.append({
        'title': 'District Behavioral Segmentation',
        'finding': '5 distinct behavioral clusters identified',
        'interpretation': 'Different regions require different intervention strategies',
        'action': 'Tailor outreach: child-focus for adult-heavy, catch-up for low-vol areas'
    })
    
    return insights

def generate_kpis(df, national_date):
    """Generate KPIs."""
    kpis = {
        'total_enrolments': int(df['total_enrol'].sum()),
        'infant_enrolments': int(df['age_0_5'].sum()),
        'child_enrolments': int(df['age_5_17'].sum()),
        'adult_enrolments': int(df['age_18_greater'].sum()),
        'infant_share': df['age_0_5'].sum() / df['total_enrol'].sum(),
        'child_share': df['age_5_17'].sum() / df['total_enrol'].sum(),
        'adult_share': df['age_18_greater'].sum() / df['total_enrol'].sum(),
        'states_covered': int(df['state'].nunique()),
        'districts_covered': int(df[['state', 'district']].drop_duplicates().shape[0]),
        'avg_daily_enrolments': int(national_date['total_enrol'].mean()),
    }
    return kpis

# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    print("="*70)
    print("UIDAI DATA HACKATHON 2026 - DEEP ENROLMENT ANALYSIS")
    print("Focus: Age-Profile | Regional Gaps | New Enrollee Patterns")
    print("="*70)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PLOTS_DIR, exist_ok=True)
    
    # Load and preprocess
    df = load_enrolment_data()
    df = preprocess_data(df)
    df = engineer_features(df)
    
    # Aggregate
    district_date, state_date, state_month, national_date, national_month = aggregate_levels(df)
    
    # Metrics
    volatility = calculate_stability_metrics(district_date)
    print(f"  ✓ Calculated stability metrics for {len(volatility)} districts")
    
    concentration = calculate_concentration(df)
    print(f"  ✓ Calculated concentration metrics")
    
    # Analyses
    age_results = analyze_age_profile(df, district_date, state_month)
    temporal_results = analyze_temporal_patterns(national_date, state_date)
    spatial_results = analyze_spatial_patterns(df, age_results['district_agg'], concentration)
    anomalies = detect_anomalies(district_date, national_date)
    cluster_data, cluster_summary = cluster_districts(age_results['district_agg'], volatility)
    
    # Visualizations
    print("\n" + "="*60)
    print("PHASE 5: GENERATING VISUALIZATIONS")
    print("="*60)
    setup_plots()
    
    plot_national_timeseries(national_date, national_month, PLOTS_DIR)
    plot_state_heatmaps(state_month, PLOTS_DIR)
    plot_age_analysis(age_results['state_agg'], age_results['district_agg'], PLOTS_DIR)
    plot_temporal_patterns(national_date, temporal_results['dow_pattern'], PLOTS_DIR)
    plot_concentration(concentration, PLOTS_DIR)
    plot_clusters(cluster_data, cluster_summary, PLOTS_DIR)
    plot_top_districts(age_results['district_agg'], PLOTS_DIR)
    plot_volatility(volatility, PLOTS_DIR)
    
    # Insights
    print("\n" + "="*60)
    print("PHASE 6: GENERATING INSIGHTS")
    print("="*60)
    
    insights = generate_insights(age_results, temporal_results, spatial_results, cluster_summary)
    kpis = generate_kpis(df, national_date)
    
    print("\n📊 KEY PERFORMANCE INDICATORS:")
    for k, v in kpis.items():
        if isinstance(v, float):
            print(f"  • {k}: {v:.1%}")
        else:
            print(f"  • {k}: {v:,}")
    
    print("\n💡 TOP INSIGHTS:")
    for i, ins in enumerate(insights, 1):
        print(f"\n  {i}. {ins['title']}")
        print(f"     Finding: {ins['finding']}")
        print(f"     Action: {ins['action']}")
    
    # Export
    print("\n" + "="*60)
    print("PHASE 7: EXPORTING RESULTS")
    print("="*60)
    
    cluster_data.to_csv(os.path.join(OUTPUT_DIR, 'district_clusters.csv'), index=False)
    anomalies.to_csv(os.path.join(OUTPUT_DIR, 'anomalies.csv'), index=False)
    concentration.to_csv(os.path.join(OUTPUT_DIR, 'concentration_metrics.csv'), index=False)
    volatility.to_csv(os.path.join(OUTPUT_DIR, 'volatility_metrics.csv'), index=False)
    pd.DataFrame([kpis]).to_csv(os.path.join(OUTPUT_DIR, 'kpis.csv'), index=False)
    
    print(f"  ✓ Saved all outputs to {OUTPUT_DIR}")
    
    print("\n" + "="*70)
    print("✅ ENROLMENT DEEP ANALYSIS COMPLETE!")
    print(f"📁 Output: {OUTPUT_DIR}")
    print(f"📊 Plots: {PLOTS_DIR}")
    print("="*70)
    
    return df, insights, kpis

if __name__ == "__main__":
    main()
