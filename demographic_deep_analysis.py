#!/usr/bin/env python3
"""
UIDAI Data Hackathon 2026 - Deep Demographic Update Analysis
Focus: Age-Group Dynamics, Spatial Patterns, Operational Signals

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
DATA_DIR = "/Users/ayushpatel/Documents/Projects/UIDAI/UIDAI/api_data_aadhar_demographic"
OUTPUT_DIR = "/Users/ayushpatel/Documents/Projects/UIDAI/UIDAI/demographic_analysis"
PLOTS_DIR = os.path.join(OUTPUT_DIR, "plots")

# State name normalization (same as biometric)
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
def load_demographic_data():
    """Load all demographic CSV files."""
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
    
    # Check for missing values
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print(f"  ⚠️ Missing values detected:")
        for col, count in missing[missing > 0].items():
            print(f"      {col}: {count}")
    
    # Check for outliers (extreme values)
    for col in ['demo_age_5_17', 'demo_age_17_']:
        q99 = df[col].quantile(0.99)
        outliers = (df[col] > q99 * 10).sum()
        if outliers > 0:
            print(f"  ⚠️ {outliers} extreme outliers in {col} (capped at 99th percentile × 10)")
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
    """Create demographic-specific features."""
    print("\n" + "="*60)
    print("PHASE 3: FEATURE ENGINEERING")
    print("="*60)
    
    df = df.copy()
    
    # Total demographic updates
    df['total_demo'] = df['demo_age_5_17'] + df['demo_age_17_']
    
    # Age-group ratios (with epsilon to avoid division by zero)
    eps = 1e-10
    df['demo_minor_share'] = df['demo_age_5_17'] / (df['total_demo'] + eps)
    df['demo_adult_share'] = df['demo_age_17_'] / (df['total_demo'] + eps)
    df['demo_minor_to_adult_ratio'] = df['demo_age_5_17'] / (df['demo_age_17_'] + eps)
    
    # Cap ratios where total is 0
    df.loc[df['total_demo'] == 0, ['demo_minor_share', 'demo_adult_share']] = 0
    df.loc[df['demo_age_17_'] == 0, 'demo_minor_to_adult_ratio'] = 0
    
    print(f"  ✓ Created age-group metrics: demo_minor_share, demo_adult_share, ratio")
    return df

def aggregate_levels(df):
    """Create aggregations at different levels."""
    print("\n" + "="*60)
    print("PHASE 4: AGGREGATION")
    print("="*60)
    
    # District-Date level
    district_date = df.groupby(['date', 'year', 'month', 'day_of_week', 'is_weekend', 
                                 'state', 'district']).agg({
        'demo_age_5_17': 'sum',
        'demo_age_17_': 'sum',
        'total_demo': 'sum',
        'pincode': 'nunique'
    }).reset_index()
    district_date.rename(columns={'pincode': 'active_pincodes'}, inplace=True)
    
    # Recalculate ratios at aggregated level
    eps = 1e-10
    district_date['demo_minor_share'] = district_date['demo_age_5_17'] / (district_date['total_demo'] + eps)
    district_date.loc[district_date['total_demo'] == 0, 'demo_minor_share'] = 0
    
    # State-Month level
    state_month = df.groupby(['year', 'month', 'state']).agg({
        'demo_age_5_17': 'sum',
        'demo_age_17_': 'sum',
        'total_demo': 'sum',
        'district': 'nunique',
        'pincode': 'nunique'
    }).reset_index()
    state_month.rename(columns={'district': 'active_districts', 'pincode': 'active_pincodes'}, inplace=True)
    state_month['demo_minor_share'] = state_month['demo_age_5_17'] / (state_month['total_demo'] + eps)
    state_month.loc[state_month['total_demo'] == 0, 'demo_minor_share'] = 0
    
    # State-Date level
    state_date = df.groupby(['date', 'year', 'month', 'day_of_week', 'is_weekend', 'state']).agg({
        'demo_age_5_17': 'sum',
        'demo_age_17_': 'sum',
        'total_demo': 'sum'
    }).reset_index()
    state_date['demo_minor_share'] = state_date['demo_age_5_17'] / (state_date['total_demo'] + eps)
    
    # National-Date level
    national_date = df.groupby(['date', 'year', 'month', 'day_of_week', 'is_weekend']).agg({
        'demo_age_5_17': 'sum',
        'demo_age_17_': 'sum',
        'total_demo': 'sum'
    }).reset_index()
    national_date['demo_minor_share'] = national_date['demo_age_5_17'] / (national_date['total_demo'] + eps)
    
    # National-Month level
    national_month = df.groupby(['year', 'month']).agg({
        'demo_age_5_17': 'sum',
        'demo_age_17_': 'sum',
        'total_demo': 'sum'
    }).reset_index()
    national_month['demo_minor_share'] = national_month['demo_age_5_17'] / (national_month['total_demo'] + eps)
    
    print(f"  ✓ District-Date: {len(district_date):,} records")
    print(f"  ✓ State-Date: {len(state_date):,} records")
    print(f"  ✓ State-Month: {len(state_month):,} records")
    print(f"  ✓ National-Date: {len(national_date):,} records")
    print(f"  ✓ National-Month: {len(national_month):,} records")
    
    return district_date, state_date, state_month, national_date, national_month

def calculate_normalized_metrics(df, district_date, state_month):
    """Calculate normalized and comparative metrics."""
    
    # District share of state total
    state_totals = df.groupby('state')['total_demo'].sum().reset_index()
    state_totals.columns = ['state', 'state_total_demo']
    
    district_totals = df.groupby(['state', 'district'])['total_demo'].sum().reset_index()
    district_totals = district_totals.merge(state_totals, on='state')
    district_totals['district_share_of_state'] = district_totals['total_demo'] / district_totals['state_total_demo']
    
    # Z-score of district volume vs state mean
    state_means = district_totals.groupby('state')['total_demo'].agg(['mean', 'std']).reset_index()
    state_means.columns = ['state', 'state_mean', 'state_std']
    district_totals = district_totals.merge(state_means, on='state')
    district_totals['zscore_vs_state'] = (district_totals['total_demo'] - district_totals['state_mean']) / (district_totals['state_std'] + 1e-10)
    
    # State share of national
    national_total = df['total_demo'].sum()
    state_share = state_totals.copy()
    state_share['state_share_of_national'] = state_share['state_total_demo'] / national_total
    
    # Percentile ranks
    district_totals['volume_percentile'] = district_totals['total_demo'].rank(pct=True) * 100
    
    return district_totals, state_share

def calculate_stability_metrics(district_date):
    """Calculate stability and concentration metrics."""
    
    # Volatility per district
    volatility = district_date.groupby(['state', 'district']).agg({
        'total_demo': ['mean', 'std', 'count'],
        'demo_minor_share': ['mean', 'std']
    }).reset_index()
    volatility.columns = ['state', 'district', 'avg_demo', 'std_demo', 'obs_count',
                          'avg_minor_share', 'std_minor_share']
    
    # Coefficient of variation
    volatility['cv_volume'] = volatility['std_demo'] / (volatility['avg_demo'] + 1e-10)
    volatility['cv_minor_share'] = volatility['std_minor_share'] / (volatility['avg_minor_share'] + 1e-10)
    
    return volatility

def calculate_concentration(df):
    """Calculate Gini and concentration metrics per state."""
    
    def gini(values):
        """Calculate Gini coefficient.
        
        Note: We do NOT filter out zeros because zero-activity districts
        are legitimate data points. Excluding them would inflate the Gini
        coefficient and make concentration appear higher than it is.
        """
        values = np.array(values)
        # Do NOT filter zeros - they represent legitimate zero-activity districts
        # values = values[values > 0]  # REMOVED - this was inflating Gini
        if len(values) < 2:
            return 0
        if np.sum(values) == 0:
            return 0  # All zeros means perfect equality
        sorted_values = np.sort(values)
        n = len(sorted_values)
        cumsum = np.cumsum(sorted_values)
        return (2 * np.sum((np.arange(1, n+1) * sorted_values))) / (n * cumsum[-1]) - (n + 1) / n
    
    # Gini per state (district concentration)
    state_gini = df.groupby('state').apply(
        lambda x: gini(x.groupby('district')['total_demo'].sum().values)
    ).reset_index()
    state_gini.columns = ['state', 'gini_district']
    
    # Top 10% share
    def top_10_share(group):
        district_totals = group.groupby('district')['total_demo'].sum().sort_values(ascending=False)
        top_n = max(1, int(len(district_totals) * 0.1))
        return district_totals.iloc[:top_n].sum() / district_totals.sum() if district_totals.sum() > 0 else 0
    
    state_top10 = df.groupby('state').apply(top_10_share).reset_index()
    state_top10.columns = ['state', 'top_10_district_share']
    
    concentration = state_gini.merge(state_top10, on='state')
    return concentration

# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================
def analyze_age_patterns(df, district_totals, state_month):
    """Analyze age-group patterns in demographic updates."""
    print("\n" + "="*60)
    print("ANALYSIS A: AGE-GROUP PATTERNS")
    print("="*60)
    
    results = {}
    
    # 1. States by minor share
    state_agg = df.groupby('state').agg({
        'demo_age_5_17': 'sum',
        'demo_age_17_': 'sum',
        'total_demo': 'sum'
    }).reset_index()
    state_agg['demo_minor_share'] = state_agg['demo_age_5_17'] / state_agg['total_demo']
    state_agg = state_agg.sort_values('demo_minor_share', ascending=False)
    
    print(f"\n  Top 5 States by Minor Share (Demographic):")
    for _, row in state_agg.head(5).iterrows():
        print(f"    • {row['state']}: {row['demo_minor_share']:.1%}")
    
    results['state_minor_share'] = state_agg
    
    # 2. Districts by minor share
    district_agg = df.groupby(['state', 'district']).agg({
        'demo_age_5_17': 'sum',
        'demo_age_17_': 'sum',
        'total_demo': 'sum'
    }).reset_index()
    district_agg['demo_minor_share'] = district_agg['demo_age_5_17'] / (district_agg['total_demo'] + 1e-10)
    district_agg = district_agg[district_agg['total_demo'] > 100]  # Filter low volume
    
    # Flag outliers (>75th percentile + 1.5*IQR)
    q75 = district_agg['demo_minor_share'].quantile(0.75)
    q25 = district_agg['demo_minor_share'].quantile(0.25)
    iqr = q75 - q25
    high_threshold = q75 + 1.5 * iqr
    
    high_minor_districts = district_agg[district_agg['demo_minor_share'] > high_threshold]
    print(f"\n  Districts with unusually high Minor Share: {len(high_minor_districts)}")
    print(f"    (Threshold: >{high_threshold:.1%})")
    
    # Low minor share districts
    low_threshold = q25 - 1.5 * iqr
    low_minor_districts = district_agg[district_agg['demo_minor_share'] < max(0.05, low_threshold)]
    print(f"\n  Districts with very low Minor Share (<5%): {len(low_minor_districts)}")
    
    results['district_minor_share'] = district_agg
    results['high_minor_districts'] = high_minor_districts
    results['low_minor_districts'] = low_minor_districts
    
    # 3. Monthly trend
    monthly = state_month.groupby('month').agg({
        'demo_age_5_17': 'sum',
        'demo_age_17_': 'sum',
        'total_demo': 'sum'
    }).reset_index()
    monthly['demo_minor_share'] = monthly['demo_age_5_17'] / monthly['total_demo']
    
    print(f"\n  Monthly Minor Share Trend:")
    for _, row in monthly.iterrows():
        print(f"    Month {int(row['month'])}: {row['demo_minor_share']:.1%}")
    
    results['monthly_trend'] = monthly
    
    return results

def analyze_temporal_patterns(national_date, state_date):
    """Analyze temporal patterns."""
    print("\n" + "="*60)
    print("ANALYSIS B: TEMPORAL PATTERNS")
    print("="*60)
    
    results = {}
    
    # 1. Weekend vs Weekday
    weekend_stats = national_date.groupby('is_weekend')['total_demo'].mean()
    weekday_avg = weekend_stats.get(False, 0)
    weekend_avg = weekend_stats.get(True, 0)
    weekend_change = (weekend_avg - weekday_avg) / weekday_avg * 100 if weekday_avg > 0 else 0
    
    print(f"\n  Weekend Effect:")
    print(f"    Weekday avg: {weekday_avg:,.0f}")
    print(f"    Weekend avg: {weekend_avg:,.0f}")
    print(f"    Weekend change: {weekend_change:+.1f}%")
    
    results['weekend_change'] = weekend_change
    
    # 2. Day of week pattern
    dow_pattern = national_date.groupby('day_of_week')['total_demo'].mean().reindex([
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    ])
    print(f"\n  Day of Week Pattern:")
    for day, val in dow_pattern.items():
        print(f"    {day}: {val:,.0f}")
    
    results['dow_pattern'] = dow_pattern
    
    # 3. States with weak weekend service
    state_weekend = state_date.groupby(['state', 'is_weekend'])['total_demo'].mean().unstack()
    state_weekend.columns = ['weekday_avg', 'weekend_avg']
    state_weekend['weekend_ratio'] = state_weekend['weekend_avg'] / state_weekend['weekday_avg']
    weak_weekend_states = state_weekend[state_weekend['weekend_ratio'] < 0.5]
    
    print(f"\n  States with weak weekend service (<50% of weekday): {len(weak_weekend_states)}")
    
    results['state_weekend'] = state_weekend
    results['weak_weekend_states'] = weak_weekend_states
    
    # 4. Monthly totals
    monthly = national_date.groupby('month')['total_demo'].sum()
    peak_month = monthly.idxmax()
    print(f"\n  Peak Month: {peak_month} ({monthly[peak_month]:,.0f} updates)")
    
    results['monthly_totals'] = monthly
    
    return results

def analyze_spatial_patterns(df, district_agg, concentration):
    """Analyze spatial and structural patterns."""
    print("\n" + "="*60)
    print("ANALYSIS C: SPATIAL PATTERNS")
    print("="*60)
    
    results = {}
    
    # 1. State ranking by volume
    state_totals = df.groupby('state')['total_demo'].sum().sort_values(ascending=False)
    national_total = state_totals.sum()
    
    print(f"\n  Top 10 States by Volume:")
    for state, vol in state_totals.head(10).items():
        pct = vol / national_total * 100
        print(f"    {state}: {vol:,.0f} ({pct:.1f}%)")
    
    results['state_totals'] = state_totals
    
    # 2. Concentration analysis
    high_concentration = concentration[concentration['gini_district'] > 0.5]
    print(f"\n  States with high district concentration (Gini>0.5): {len(high_concentration)}")
    
    results['concentration'] = concentration
    
    # 3. Top/Bottom districts
    top_50 = district_agg.nlargest(50, 'total_demo')
    bottom_50 = district_agg[district_agg['total_demo'] > 0].nsmallest(50, 'total_demo')
    
    top_50_share = top_50['total_demo'].sum() / district_agg['total_demo'].sum() * 100
    print(f"\n  Top 50 Districts: {top_50_share:.1f}% of total updates")
    
    results['top_50_districts'] = top_50
    results['bottom_50_districts'] = bottom_50
    
    return results

def detect_anomalies(district_date, national_date):
    """Detect temporal anomalies and structural breaks."""
    print("\n" + "="*60)
    print("ANALYSIS D: ANOMALY DETECTION")
    print("="*60)
    
    # Z-score based detection at district level
    mean_val = district_date['total_demo'].mean()
    std_val = district_date['total_demo'].std()
    district_date = district_date.copy()
    district_date['zscore'] = (district_date['total_demo'] - mean_val) / std_val
    
    anomalies = district_date[abs(district_date['zscore']) > 3].copy()
    anomalies['anomaly_type'] = np.where(anomalies['zscore'] > 0, 'High Spike', 'Low Drop')
    
    print(f"\n  Anomalies detected: {len(anomalies)}")
    print(f"    High Spikes (z>3): {(anomalies['anomaly_type'] == 'High Spike').sum()}")
    print(f"    Low Drops (z<-3): {(anomalies['anomaly_type'] == 'Low Drop').sum()}")
    
    # Monthly structural breaks
    national_monthly = national_date.groupby('month')['total_demo'].sum()
    mom_change = national_monthly.pct_change() * 100
    structural_breaks = mom_change[abs(mom_change) > 30]
    
    if len(structural_breaks) > 0:
        print(f"\n  Monthly Structural Breaks (>30% MoM change):")
        for month, change in structural_breaks.items():
            print(f"    Month {month}: {change:+.1f}%")
    
    return anomalies, structural_breaks

def cluster_districts(district_agg, volatility):
    """Cluster districts by behavior."""
    print("\n" + "="*60)
    print("ANALYSIS E: DISTRICT CLUSTERING")
    print("="*60)
    
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    
    # Merge data
    cluster_data = district_agg.merge(
        volatility[['state', 'district', 'cv_volume']], 
        on=['state', 'district'],
        how='left'
    )
    cluster_data = cluster_data[cluster_data['total_demo'] > 100]
    cluster_data['cv_volume'] = cluster_data['cv_volume'].fillna(0)
    
    # Features for clustering
    features = ['total_demo', 'demo_minor_share', 'cv_volume']
    X = cluster_data[features].values
    
    # Log transform volume for better clustering
    X[:, 0] = np.log1p(X[:, 0])
    
    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Cluster
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    cluster_data['cluster'] = kmeans.fit_predict(X_scaled)
    
    # Describe clusters
    cluster_summary = cluster_data.groupby('cluster').agg({
        'total_demo': 'mean',
        'demo_minor_share': 'mean',
        'cv_volume': 'mean',
        'district': 'count'
    }).reset_index()
    cluster_summary.columns = ['cluster', 'avg_volume', 'avg_minor_share', 'avg_cv', 'count']
    
    # Assign labels based on characteristics
    cluster_labels = []
    for _, row in cluster_summary.iterrows():
        if row['avg_volume'] > cluster_summary['avg_volume'].median():
            vol_label = "High-Vol"
        else:
            vol_label = "Low-Vol"
        
        if row['avg_minor_share'] > 0.3:
            age_label = "Child-Heavy"
        else:
            age_label = "Adult-Dom"
        
        if row['avg_cv'] > cluster_summary['avg_cv'].median():
            stab_label = "Volatile"
        else:
            stab_label = "Stable"
        
        cluster_labels.append(f"{vol_label}, {age_label}, {stab_label}")
    
    cluster_summary['label'] = cluster_labels
    
    print(f"\n  Cluster Summary:")
    for _, row in cluster_summary.iterrows():
        print(f"    Cluster {int(row['cluster'])}: {int(row['count'])} districts")
        print(f"        {row['label']}")
        print(f"        Avg vol={row['avg_volume']:,.0f}, minor={row['avg_minor_share']:.1%}, CV={row['avg_cv']:.2f}")
    
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
    axes[0,0].plot(national_date['date'], national_date['total_demo'], 'b-', linewidth=1)
    axes[0,0].set_title('National Daily Demographic Updates', fontweight='bold')
    axes[0,0].set_ylabel('Total Updates')
    axes[0,0].tick_params(axis='x', rotation=45)
    
    # Age composition
    axes[0,1].stackplot(national_date['date'],
                        national_date['demo_age_5_17'],
                        national_date['demo_age_17_'],
                        labels=['Minor (5-17)', 'Adult (17+)'], alpha=0.8)
    axes[0,1].set_title('Age Group Composition Over Time', fontweight='bold')
    axes[0,1].legend(loc='upper right')
    axes[0,1].tick_params(axis='x', rotation=45)
    
    # Monthly totals
    axes[1,0].bar(national_month['month'], national_month['total_demo'], color='teal')
    axes[1,0].set_title('Monthly Total Demographic Updates', fontweight='bold')
    axes[1,0].set_xlabel('Month')
    axes[1,0].set_ylabel('Total Updates')
    
    # Monthly minor share
    axes[1,1].plot(national_month['month'], national_month['demo_minor_share'], 'o-', color='coral', linewidth=2)
    axes[1,1].axhline(y=0.5, color='red', linestyle='--', alpha=0.5)
    axes[1,1].set_title('Monthly Minor Share Trend', fontweight='bold')
    axes[1,1].set_xlabel('Month')
    axes[1,1].set_ylabel('Minor Share')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '01_national_timeseries.png'), dpi=150)
    plt.close()
    print("  ✓ 01_national_timeseries.png")

def plot_state_heatmaps(state_month, output_dir):
    """State heatmaps."""
    fig, axes = plt.subplots(1, 2, figsize=(18, 12))
    
    # Volume heatmap
    pivot1 = state_month.pivot_table(index='state', columns='month', values='total_demo', aggfunc='sum')
    top_states = pivot1.sum(axis=1).nlargest(15).index
    pivot1 = pivot1.loc[top_states]
    
    sns.heatmap(pivot1, cmap='YlOrRd', annot=True, fmt='.0f', ax=axes[0], linewidths=0.5)
    axes[0].set_title('Demographic Updates by State × Month', fontweight='bold', fontsize=14)
    
    # Minor share heatmap
    pivot2 = state_month.pivot_table(index='state', columns='month', values='demo_minor_share', aggfunc='mean')
    pivot2 = pivot2.loc[top_states]
    
    sns.heatmap(pivot2, cmap='RdYlGn_r', annot=True, fmt='.1%', ax=axes[1], linewidths=0.5)
    axes[1].set_title('Minor Share by State × Month', fontweight='bold', fontsize=14)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '02_state_heatmaps.png'), dpi=150)
    plt.close()
    print("  ✓ 02_state_heatmaps.png")

def plot_age_analysis(state_agg, district_agg, output_dir):
    """Age group analysis plots."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Top states by minor share
    top_minor = state_agg.nlargest(15, 'demo_minor_share')
    axes[0,0].barh(top_minor['state'], top_minor['demo_minor_share'], color='coral')
    axes[0,0].axvline(x=0.5, color='red', linestyle='--', alpha=0.7)
    axes[0,0].set_title('Top 15 States by Minor Share', fontweight='bold')
    axes[0,0].set_xlabel('Minor Share')
    
    # Top states by volume
    top_vol = state_agg.nlargest(15, 'total_demo')
    axes[0,1].barh(top_vol['state'], top_vol['total_demo'], color='steelblue')
    axes[0,1].set_title('Top 15 States by Volume', fontweight='bold')
    axes[0,1].set_xlabel('Total Demographic Updates')
    
    # Distribution of minor share
    sns.histplot(data=district_agg, x='demo_minor_share', bins=50, ax=axes[1,0], color='purple')
    axes[1,0].axvline(x=0.5, color='red', linestyle='--', alpha=0.7)
    axes[1,0].set_title('Distribution of Minor Share Across Districts', fontweight='bold')
    
    # Scatter: Volume vs Minor Share
    sns.scatterplot(data=district_agg, x='total_demo', y='demo_minor_share', alpha=0.4, ax=axes[1,1])
    axes[1,1].axhline(y=0.5, color='red', linestyle='--', alpha=0.5)
    axes[1,1].set_title('District Volume vs Minor Share', fontweight='bold')
    axes[1,1].set_xscale('log')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '03_age_analysis.png'), dpi=150)
    plt.close()
    print("  ✓ 03_age_analysis.png")

def plot_temporal_patterns(national_date, dow_pattern, state_weekend, output_dir):
    """Temporal pattern plots."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Day of week
    dow_df = dow_pattern.reset_index()
    dow_df.columns = ['day', 'avg']
    sns.barplot(data=dow_df, x='day', y='avg', ax=axes[0,0], palette='viridis')
    axes[0,0].set_title('Average Updates by Day of Week', fontweight='bold')
    axes[0,0].tick_params(axis='x', rotation=45)
    
    # Weekend comparison
    weekend_comp = national_date.groupby('is_weekend')['total_demo'].mean()
    axes[0,1].bar(['Weekday', 'Weekend'], weekend_comp.values, color=['steelblue', 'coral'])
    axes[0,1].set_title('Weekday vs Weekend Average', fontweight='bold')
    
    # States by weekend ratio
    top_weekend = state_weekend.nlargest(15, 'weekend_ratio')
    axes[1,0].barh(top_weekend.index, top_weekend['weekend_ratio'], color='teal')
    axes[1,0].axvline(x=1.0, color='red', linestyle='--', alpha=0.7)
    axes[1,0].set_title('Top 15 States by Weekend Activity Ratio', fontweight='bold')
    axes[1,0].set_xlabel('Weekend/Weekday Ratio')
    
    # Monthly totals
    monthly = national_date.groupby('month')['total_demo'].sum()
    axes[1,1].bar(monthly.index, monthly.values, color='purple')
    axes[1,1].set_title('Monthly Total Updates', fontweight='bold')
    axes[1,1].set_xlabel('Month')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '04_temporal_patterns.png'), dpi=150)
    plt.close()
    print("  ✓ 04_temporal_patterns.png")

def plot_concentration(concentration, output_dir):
    """Concentration analysis."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    conc_sorted = concentration.sort_values('gini_district', ascending=True).tail(20)
    
    axes[0].barh(conc_sorted['state'], conc_sorted['gini_district'], color='crimson')
    axes[0].set_title('Gini Coefficient by State (District Concentration)', fontweight='bold')
    axes[0].set_xlabel('Gini (higher = more concentrated)')
    
    axes[1].barh(conc_sorted['state'], conc_sorted['top_10_district_share'], color='darkorange')
    axes[1].set_title('Top 10% Districts Share of State Updates', fontweight='bold')
    axes[1].set_xlabel('Share')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '05_concentration.png'), dpi=150)
    plt.close()
    print("  ✓ 05_concentration.png")

def plot_clusters(cluster_data, cluster_summary, output_dir):
    """Cluster visualization."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    scatter = axes[0].scatter(
        np.log1p(cluster_data['total_demo']),
        cluster_data['demo_minor_share'],
        c=cluster_data['cluster'],
        cmap='viridis',
        alpha=0.5,
        s=20
    )
    axes[0].set_xlabel('Log(Total Updates)')
    axes[0].set_ylabel('Minor Share')
    axes[0].set_title('District Clusters: Volume vs Minor Share', fontweight='bold')
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
    """Top/Bottom districts."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    # Top by volume
    top = district_agg.nlargest(25, 'total_demo')
    top['label'] = top['district'] + ' (' + top['state'].str[:3] + ')'
    axes[0].barh(top['label'], top['total_demo'], color='steelblue')
    axes[0].set_title('Top 25 Districts by Volume', fontweight='bold')
    
    # Top by minor share (min 1000)
    top_minor = district_agg[district_agg['total_demo'] > 1000].nlargest(25, 'demo_minor_share')
    top_minor['label'] = top_minor['district'] + ' (' + top_minor['state'].str[:3] + ')'
    axes[1].barh(top_minor['label'], top_minor['demo_minor_share'], color='coral')
    axes[1].axvline(x=0.5, color='red', linestyle='--', alpha=0.7)
    axes[1].set_title('Top 25 Districts by Minor Share (min 1000 updates)', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '07_top_districts.png'), dpi=150)
    plt.close()
    print("  ✓ 07_top_districts.png")

def plot_volatility(volatility, output_dir):
    """Volatility analysis."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    top_volatile = volatility.nlargest(20, 'cv_volume')
    top_volatile['label'] = top_volatile['district'] + ' (' + top_volatile['state'].str[:3] + ')'
    
    axes[0].barh(top_volatile['label'], top_volatile['cv_volume'], color='purple')
    axes[0].set_title('Most Volatile Districts (CV)', fontweight='bold')
    
    sns.histplot(data=volatility, x='cv_volume', bins=50, ax=axes[1])
    axes[1].set_title('Distribution of District Volatility', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '08_volatility.png'), dpi=150)
    plt.close()
    print("  ✓ 08_volatility.png")

# ============================================================================
# INSIGHT GENERATION
# ============================================================================
def generate_insights(age_results, temporal_results, spatial_results, cluster_summary):
    """Generate structured insights."""
    insights = []
    
    # 1. High minor share regions
    high_minor_count = len(age_results['high_minor_districts'])
    insights.append({
        'title': 'Child-Heavy Demographic Update Regions',
        'finding': f"{high_minor_count} districts have unusually high child (5-17) demographic update share",
        'interpretation': 'Strong education-linked update drives, scholarship schemes, or youth documentation corrections',
        'action': 'Investigate drivers; replicate successful models in low-minor regions'
    })
    
    # 2. Low minor share gaps
    low_minor_count = len(age_results['low_minor_districts'])
    insights.append({
        'title': 'Child Update Gap Identified',
        'finding': f"{low_minor_count} districts have very low child demographic update share (<5%)",
        'interpretation': 'Children may be missing from update drives; potential awareness or access gap',
        'action': 'Target school-based and Anganwadi outreach in these districts'
    })
    
    # 3. Weekend service
    weekend_change = temporal_results['weekend_change']
    insights.append({
        'title': 'Weekend Service Pattern',
        'finding': f"Weekend updates are {weekend_change:+.1f}% compared to weekdays",
        'interpretation': 'Indicates weekend service availability/demand pattern',
        'action': 'Align staffing with demand; consider extended weekend hours in high-demand areas'
    })
    
    # 4. Geographic concentration
    top_50_share = spatial_results['top_50_districts']['total_demo'].sum() / age_results['state_minor_share']['total_demo'].sum() * 100
    insights.append({
        'title': 'Geographic Concentration',
        'finding': f"Top 50 districts account for {top_50_share:.1f}% of all demographic updates",
        'interpretation': 'Update activity concentrated in specific urban/administrative hubs',
        'action': 'Expand access in underserved districts'
    })
    
    # 5. Behavioral clusters
    insights.append({
        'title': 'District Behavioral Segments',
        'finding': '5 distinct behavioral clusters identified among districts',
        'interpretation': 'Different regions need different intervention strategies',
        'action': 'Tailor outreach per cluster: awareness for low-vol, quality for volatile, child-focus for adult-dom'
    })
    
    return insights

def generate_kpis(df, national_date):
    """Generate KPIs."""
    kpis = {
        'total_demographic_updates': int(df['total_demo'].sum()),
        'minor_updates': int(df['demo_age_5_17'].sum()),
        'adult_updates': int(df['demo_age_17_'].sum()),
        'national_minor_share': df['demo_age_5_17'].sum() / df['total_demo'].sum(),
        'states_covered': int(df['state'].nunique()),
        'districts_covered': int(df[['state', 'district']].drop_duplicates().shape[0]),
        'avg_daily_updates': int(national_date['total_demo'].mean()),
    }
    return kpis

# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    print("="*70)
    print("UIDAI DATA HACKATHON 2026 - DEEP DEMOGRAPHIC ANALYSIS")
    print("Focus: Age Dynamics | Spatial Patterns | Operational Signals")
    print("="*70)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PLOTS_DIR, exist_ok=True)
    
    # Load and preprocess
    df = load_demographic_data()
    df = preprocess_data(df)
    df = engineer_features(df)
    
    # Aggregate
    district_date, state_date, state_month, national_date, national_month = aggregate_levels(df)
    
    # Normalized metrics
    district_totals, state_share = calculate_normalized_metrics(df, district_date, state_month)
    print(f"  ✓ Calculated normalized metrics")
    
    # Stability metrics
    volatility = calculate_stability_metrics(district_date)
    print(f"  ✓ Calculated stability metrics for {len(volatility)} districts")
    
    # Concentration
    concentration = calculate_concentration(df)
    print(f"  ✓ Calculated concentration metrics")
    
    # Analyses
    age_results = analyze_age_patterns(df, district_totals, state_month)
    temporal_results = analyze_temporal_patterns(national_date, state_date)
    spatial_results = analyze_spatial_patterns(df, age_results['district_minor_share'], concentration)
    anomalies, breaks = detect_anomalies(district_date, national_date)
    cluster_data, cluster_summary = cluster_districts(age_results['district_minor_share'], volatility)
    
    # Visualizations
    print("\n" + "="*60)
    print("PHASE 5: GENERATING VISUALIZATIONS")
    print("="*60)
    setup_plots()
    
    plot_national_timeseries(national_date, national_month, PLOTS_DIR)
    plot_state_heatmaps(state_month, PLOTS_DIR)
    plot_age_analysis(age_results['state_minor_share'], age_results['district_minor_share'], PLOTS_DIR)
    plot_temporal_patterns(national_date, temporal_results['dow_pattern'], temporal_results['state_weekend'], PLOTS_DIR)
    plot_concentration(concentration, PLOTS_DIR)
    plot_clusters(cluster_data, cluster_summary, PLOTS_DIR)
    plot_top_districts(age_results['district_minor_share'], PLOTS_DIR)
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
    print("✅ DEMOGRAPHIC DEEP ANALYSIS COMPLETE!")
    print(f"📁 Output: {OUTPUT_DIR}")
    print(f"📊 Plots: {PLOTS_DIR}")
    print("="*70)
    
    return df, insights, kpis

if __name__ == "__main__":
    main()
