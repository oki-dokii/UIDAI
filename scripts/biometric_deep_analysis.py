#!/usr/bin/env python3
"""
UIDAI Data Hackathon 2026 - Deep Biometric Analysis
Focus: Age-Group Dynamics, Concentration Metrics, Temporal Patterns

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
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)  # Parent directory (UIDAI/)
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
def load_biometric_data():
    """Load all biometric CSV files."""
    print("\n" + "="*60)
    print("PHASE 1: DATA LOADING")
    print("="*60)
    
    files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    dfs = []
    
    for f in files:
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
    df['day_of_week'] = df['date'].dt.day_name()
    df['week_of_year'] = df['date'].dt.isocalendar().week
    df['is_weekend'] = df['day_of_week'].isin(['Saturday', 'Sunday'])
    
    # Standardize state names
    df['state'] = df['state'].astype(str).str.strip().str.title()
    df['state'] = df['state'].replace(STATE_FIX)
    
    # Standardize district names
    df['district'] = df['district'].astype(str).str.strip().str.title()
    
    print(f"  ✓ Parsed dates: {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"  ✓ States: {df['state'].nunique()}")
    print(f"  ✓ Districts: {df['district'].nunique()}")
    print(f"  ✓ Pincodes: {df['pincode'].nunique()}")
    
    return df

# ============================================================================
# FEATURE ENGINEERING
# ============================================================================
def engineer_features(df):
    """Create analysis features."""
    print("\n" + "="*60)
    print("PHASE 3: FEATURE ENGINEERING")
    print("="*60)
    
    df = df.copy()
    
    # Total biometric updates
    df['total_bio'] = df['bio_age_5_17'] + df['bio_age_17_']
    
    # Age-group ratios (KEY METRICS)
    df['minor_share'] = np.where(
        df['total_bio'] > 0,
        df['bio_age_5_17'] / df['total_bio'],
        0
    )
    df['adult_share'] = np.where(
        df['total_bio'] > 0,
        df['bio_age_17_'] / df['total_bio'],
        0
    )
    df['minor_to_adult_ratio'] = np.where(
        df['bio_age_17_'] > 0,
        df['bio_age_5_17'] / df['bio_age_17_'],
        0
    )
    
    print(f"  ✓ Created age-group metrics: minor_share, adult_share, ratio")
    return df

def aggregate_levels(df):
    """Create aggregations at different levels."""
    
    # District-Date level
    district_date = df.groupby(['date', 'year', 'month', 'day_of_week', 'is_weekend', 
                                 'state', 'district']).agg({
        'bio_age_5_17': 'sum',
        'bio_age_17_': 'sum',
        'total_bio': 'sum',
        'pincode': 'nunique'
    }).reset_index()
    district_date.rename(columns={'pincode': 'active_pincodes'}, inplace=True)
    
    # Recalculate ratios
    district_date['minor_share'] = np.where(
        district_date['total_bio'] > 0,
        district_date['bio_age_5_17'] / district_date['total_bio'],
        0
    )
    
    # State-Month level
    state_month = df.groupby(['year', 'month', 'state']).agg({
        'bio_age_5_17': 'sum',
        'bio_age_17_': 'sum',
        'total_bio': 'sum',
        'district': 'nunique',
        'pincode': 'nunique'
    }).reset_index()
    state_month.rename(columns={'district': 'active_districts', 'pincode': 'active_pincodes'}, inplace=True)
    state_month['minor_share'] = np.where(
        state_month['total_bio'] > 0,
        state_month['bio_age_5_17'] / state_month['total_bio'],
        0
    )
    
    # National-Date level
    national_date = df.groupby(['date', 'year', 'month', 'day_of_week', 'is_weekend']).agg({
        'bio_age_5_17': 'sum',
        'bio_age_17_': 'sum',
        'total_bio': 'sum'
    }).reset_index()
    national_date['minor_share'] = np.where(
        national_date['total_bio'] > 0,
        national_date['bio_age_5_17'] / national_date['total_bio'],
        0
    )
    
    print(f"  ✓ District-Date: {len(district_date):,} records")
    print(f"  ✓ State-Month: {len(state_month):,} records")
    print(f"  ✓ National-Date: {len(national_date):,} records")
    
    return district_date, state_month, national_date

def calculate_concentration_metrics(df):
    """Calculate Gini coefficient and concentration metrics."""
    
    def gini_coefficient(values):
        """Gini coefficient - zeros included as legitimate data."""
        values = np.array(values)
        # Do NOT filter zeros - they represent legitimate zero-activity
        if len(values) < 2:
            return 0
        if np.sum(values) == 0:
            return 0
        sorted_values = np.sort(values)
        n = len(sorted_values)
        cumsum = np.cumsum(sorted_values)
        return (2 * np.sum((np.arange(1, n+1) * sorted_values))) / (n * cumsum[-1]) - (n + 1) / n
    
    # Calculate Gini per state (pincode concentration)
    state_gini = df.groupby('state')['total_bio'].apply(gini_coefficient).reset_index()
    state_gini.columns = ['state', 'gini_coefficient']
    
    # Top 10% share per state
    def top_10_share(group):
        sorted_vals = group.sort_values(ascending=False)
        top_10_count = max(1, int(len(sorted_vals) * 0.1))
        return sorted_vals.iloc[:top_10_count].sum() / sorted_vals.sum() if sorted_vals.sum() > 0 else 0
    
    state_top10 = df.groupby('state')['total_bio'].apply(top_10_share).reset_index()
    state_top10.columns = ['state', 'top_10_pct_share']
    
    concentration = state_gini.merge(state_top10, on='state')
    return concentration

def calculate_volatility(district_date):
    """Calculate volatility metrics per district."""
    
    volatility = district_date.groupby(['state', 'district']).agg({
        'total_bio': ['mean', 'std', 'count'],
        'minor_share': ['mean', 'std']
    }).reset_index()
    volatility.columns = ['state', 'district', 'avg_daily_bio', 'std_daily_bio', 
                          'observation_count', 'avg_minor_share', 'std_minor_share']
    
    # Coefficient of variation
    volatility['cv'] = np.where(
        volatility['avg_daily_bio'] > 0,
        volatility['std_daily_bio'] / volatility['avg_daily_bio'],
        0
    )
    
    return volatility

# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================
def analyze_age_patterns(df, district_date, state_month):
    """Deep analysis of age-group patterns."""
    print("\n" + "="*60)
    print("ANALYSIS A: AGE-GROUP PATTERNS")
    print("="*60)
    
    results = {}
    
    # 1. States with highest minor share
    state_minor = df.groupby('state').agg({
        'bio_age_5_17': 'sum',
        'bio_age_17_': 'sum',
        'total_bio': 'sum'
    }).reset_index()
    state_minor['minor_share'] = state_minor['bio_age_5_17'] / state_minor['total_bio']
    state_minor = state_minor.sort_values('minor_share', ascending=False)
    
    print(f"\n  Top 5 States by Minor Share:")
    for _, row in state_minor.head(5).iterrows():
        print(f"    • {row['state']}: {row['minor_share']:.1%}")
    
    results['state_minor_share'] = state_minor
    
    # 2. Districts with minor_share > 0.5
    district_agg = df.groupby(['state', 'district']).agg({
        'bio_age_5_17': 'sum',
        'bio_age_17_': 'sum',
        'total_bio': 'sum'
    }).reset_index()
    district_agg['minor_share'] = district_agg['bio_age_5_17'] / district_agg['total_bio']
    district_agg = district_agg[district_agg['total_bio'] > 100]  # Filter low volume
    
    high_minor_districts = district_agg[district_agg['minor_share'] > 0.5]
    print(f"\n  Districts with Minor Share > 50%: {len(high_minor_districts)}")
    
    results['high_minor_districts'] = high_minor_districts
    results['district_minor_share'] = district_agg
    
    # 3. Monthly trend of minor share
    monthly_trend = state_month.groupby('month').agg({
        'bio_age_5_17': 'sum',
        'total_bio': 'sum'
    }).reset_index()
    monthly_trend['minor_share'] = monthly_trend['bio_age_5_17'] / monthly_trend['total_bio']
    
    print(f"\n  Monthly Minor Share Trend:")
    for _, row in monthly_trend.iterrows():
        print(f"    Month {int(row['month'])}: {row['minor_share']:.1%}")
    
    results['monthly_trend'] = monthly_trend
    
    return results

def analyze_temporal_patterns(national_date, district_date):
    """Analyze temporal patterns."""
    print("\n" + "="*60)
    print("ANALYSIS B: TEMPORAL PATTERNS")
    print("="*60)
    
    results = {}
    
    # 1. Weekend vs Weekday
    weekend_stats = national_date.groupby('is_weekend')['total_bio'].agg(['mean', 'sum']).reset_index()
    weekend_mean = weekend_stats[weekend_stats['is_weekend'] == True]['mean'].values[0]
    weekday_mean = weekend_stats[weekend_stats['is_weekend'] == False]['mean'].values[0]
    weekend_drop = (weekday_mean - weekend_mean) / weekday_mean * 100
    
    print(f"\n  Weekend Effect:")
    print(f"    Weekday avg: {weekday_mean:,.0f}")
    print(f"    Weekend avg: {weekend_mean:,.0f}")
    print(f"    Weekend drop: {weekend_drop:.1f}%")
    
    results['weekend_drop'] = weekend_drop
    
    # 2. Day of week pattern
    dow_pattern = national_date.groupby('day_of_week')['total_bio'].mean().reindex([
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    ])
    print(f"\n  Day of Week Pattern:")
    for day, val in dow_pattern.items():
        print(f"    {day}: {val:,.0f}")
    
    results['dow_pattern'] = dow_pattern
    
    # 3. Monthly totals
    monthly_totals = national_date.groupby('month')['total_bio'].sum()
    peak_month = monthly_totals.idxmax()
    print(f"\n  Peak Month: {peak_month} ({monthly_totals[peak_month]:,.0f} updates)")
    
    results['monthly_totals'] = monthly_totals
    
    return results

def analyze_geographic_patterns(df, district_agg):
    """Analyze geographic concentration."""
    print("\n" + "="*60)
    print("ANALYSIS C: GEOGRAPHIC PATTERNS")
    print("="*60)
    
    results = {}
    
    # 1. State ranking
    state_totals = df.groupby('state')['total_bio'].sum().sort_values(ascending=False)
    print(f"\n  Top 10 States by Volume:")
    for state, vol in state_totals.head(10).items():
        pct = vol / state_totals.sum() * 100
        print(f"    {state}: {vol:,.0f} ({pct:.1f}%)")
    
    results['state_totals'] = state_totals
    
    # 2. Top 20% concentration
    total_updates = state_totals.sum()
    cumsum = state_totals.cumsum()
    top_20_pct_states = (cumsum <= total_updates * 0.5).sum() + 1
    print(f"\n  Top {top_20_pct_states} states account for 50%+ of updates")
    
    # 3. District concentration
    district_totals = district_agg.sort_values('total_bio', ascending=False)
    top_50 = district_totals.head(50)
    top_50_share = top_50['total_bio'].sum() / district_totals['total_bio'].sum() * 100
    print(f"\n  Top 50 Districts: {top_50_share:.1f}% of total updates")
    
    results['top_50_districts'] = top_50
    results['top_50_share'] = top_50_share
    
    return results

def detect_anomalies(district_date):
    """Detect anomalous patterns."""
    print("\n" + "="*60)
    print("ANALYSIS D: ANOMALY DETECTION")
    print("="*60)
    
    # Z-score based detection
    mean_bio = district_date['total_bio'].mean()
    std_bio = district_date['total_bio'].std()
    district_date['zscore'] = (district_date['total_bio'] - mean_bio) / std_bio
    
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
    cluster_data = district_agg.merge(volatility[['state', 'district', 'cv']], on=['state', 'district'])
    cluster_data = cluster_data[cluster_data['total_bio'] > 100]
    
    # Features
    features = ['total_bio', 'minor_share', 'cv']
    X = cluster_data[features].fillna(0).values
    
    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Cluster
    kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
    cluster_data['cluster'] = kmeans.fit_predict(X_scaled)
    
    # Describe clusters
    cluster_summary = cluster_data.groupby('cluster').agg({
        'total_bio': 'mean',
        'minor_share': 'mean',
        'cv': 'mean',
        'district': 'count'
    }).reset_index()
    cluster_summary.columns = ['cluster', 'avg_volume', 'avg_minor_share', 'avg_volatility', 'district_count']
    
    print(f"\n  Cluster Summary:")
    for _, row in cluster_summary.iterrows():
        print(f"    Cluster {int(row['cluster'])}: {int(row['district_count'])} districts, "
              f"vol={row['avg_volume']:.0f}, minor={row['avg_minor_share']:.1%}, cv={row['avg_volatility']:.2f}")
    
    return cluster_data, cluster_summary

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================
def setup_plots():
    """Configure plot styling."""
    plt.style.use('seaborn-v0_8-whitegrid')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 11

def plot_national_timeseries(national_date, output_dir):
    """Plot national time series."""
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # Total updates
    axes[0].plot(national_date['date'], national_date['total_bio'], 'b-', linewidth=1.5)
    axes[0].set_title('National Daily Biometric Updates', fontweight='bold', fontsize=14)
    axes[0].set_ylabel('Total Updates')
    axes[0].tick_params(axis='x', rotation=45)
    
    # Minor vs Adult
    axes[1].stackplot(national_date['date'], 
                      national_date['bio_age_5_17'], 
                      national_date['bio_age_17_'],
                      labels=['Minor (5-17)', 'Adult (17+)'], alpha=0.8)
    axes[1].set_title('Age Group Composition Over Time', fontweight='bold', fontsize=14)
    axes[1].set_ylabel('Updates')
    axes[1].legend(loc='upper right')
    axes[1].tick_params(axis='x', rotation=45)
    
    # FIX 6: Add 0-5 absence note
    axes[1].text(0.98, 0.02,
                 'Note: Age 0-5 not included in source data',
                 transform=axes[1].transAxes,
                 fontsize=9,
                 ha='right',
                 va='bottom',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '01_national_timeseries.png'), dpi=150)
    plt.close()
    print("  ✓ 01_national_timeseries.png")

def plot_state_heatmaps(state_month, output_dir):
    """Plot state heatmaps."""
    fig, axes = plt.subplots(1, 2, figsize=(18, 10))
    
    # Total updates heatmap
    pivot1 = state_month.pivot_table(index='state', columns='month', values='total_bio', aggfunc='sum')
    top_states = pivot1.sum(axis=1).nlargest(15).index
    pivot1 = pivot1.loc[top_states]
    
    # FIX 3: Remove illegible annotations from heatmaps
    sns.heatmap(pivot1, cmap='YlOrRd', annot=False, ax=axes[0], linewidths=0.5, cbar_kws={'label': 'Total Updates'})
    axes[0].set_title('Biometric Updates by State × Month', fontweight='bold')
    
    # Minor share heatmap
    pivot2 = state_month.pivot_table(index='state', columns='month', values='minor_share', aggfunc='mean')
    pivot2 = pivot2.loc[top_states]
    
    # FIX 2: Change from red-green to perceptually uniform color scale
    sns.heatmap(pivot2, cmap='viridis', annot=False, ax=axes[1], linewidths=0.5, cbar_kws={'label': 'Minor Share'})
    axes[1].set_title('Minor Share by State × Month', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '02_state_heatmaps.png'), dpi=150)
    plt.close()
    print("  ✓ 02_state_heatmaps.png")

def plot_age_group_analysis(state_minor, district_minor, output_dir):
    """Plot age group analysis."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # Top states by minor share
    top_minor = state_minor.nlargest(15, 'minor_share')
    axes[0,0].barh(top_minor['state'], top_minor['minor_share'], color='coral')
    axes[0,0].set_title('Top 15 States by Minor Share', fontweight='bold')
    axes[0,0].set_xlabel('Minor Share')
    # FIX 1: Add context to 50% threshold line
    axes[0,0].axvline(x=0.5, color='gray', linestyle=':', alpha=0.5, label='50% reference')
    axes[0,0].legend(fontsize=8, loc='lower right')
    
    # Top states by volume
    top_vol = state_minor.nlargest(15, 'total_bio')
    axes[0,1].barh(top_vol['state'], top_vol['total_bio'], color='steelblue')
    axes[0,1].set_title('Top 15 States by Volume', fontweight='bold')
    axes[0,1].set_xlabel('Total Biometric Updates')
    
    # Distribution of minor share
    sns.histplot(data=district_minor, x='minor_share', bins=50, ax=axes[1,0])
    # FIX 1: Add context to 50% reference line
    axes[1,0].axvline(x=0.5, color='gray', linestyle=':', alpha=0.5, label='50% reference (not target)')
    axes[1,0].legend(fontsize=8)
    
    # Scatter: Volume vs Minor Share
    sns.scatterplot(data=district_minor, x='total_bio', y='minor_share', alpha=0.5, ax=axes[1,1])
    axes[1,1].axhline(y=0.5, color='gray', linestyle=':', alpha=0.5)
    axes[1,1].set_title('District Volume vs Minor Share', fontweight='bold')
    # FIX 5: Add explicit log-scale annotation
    axes[1,1].set_xlabel('Total Updates (log scale)', fontweight='bold')
    axes[1,1].set_xscale('log')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '03_age_group_analysis.png'), dpi=150)
    plt.close()
    print("  ✓ 03_age_group_analysis.png")

def plot_temporal_patterns(national_date, dow_pattern, output_dir):
    """Plot temporal patterns."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Day of week
    dow_df = dow_pattern.reset_index()
    dow_df.columns = ['day', 'avg_updates']
    sns.barplot(data=dow_df, x='day', y='avg_updates', ax=axes[0,0], palette='viridis')
    axes[0,0].set_title('Average Updates by Day of Week', fontweight='bold')
    axes[0,0].tick_params(axis='x', rotation=45)
    
    # Weekend vs Weekday
    weekend_data = national_date.groupby('is_weekend')['total_bio'].mean()
    axes[0,1].bar(['Weekday', 'Weekend'], weekend_data.values, color=['steelblue', 'coral'])
    axes[0,1].set_title('Weekday vs Weekend Average', fontweight='bold')
    axes[0,1].set_ylabel('Average Daily Updates')
    
    # Monthly totals
    monthly = national_date.groupby('month')['total_bio'].sum()
    axes[1,0].bar(monthly.index, monthly.values, color='teal')
    axes[1,0].set_title('Monthly Total Updates', fontweight='bold')
    axes[1,0].set_xlabel('Month')
    axes[1,0].set_ylabel('Total Updates')
    
    # Minor share trend
    monthly_minor = national_date.groupby('month')['minor_share'].mean()
    axes[1,1].plot(monthly_minor.index, monthly_minor.values, 'o-', color='purple', linewidth=2)
    axes[1,1].set_title('Monthly Minor Share Trend', fontweight='bold')
    axes[1,1].set_xlabel('Month')
    axes[1,1].set_ylabel('Minor Share')
    # FIX 1: Add context to 50% reference line
    axes[1,1].axhline(y=0.5, color='gray', linestyle=':', alpha=0.5, label='50% reference')
    axes[1,1].legend(fontsize=8)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '04_temporal_patterns.png'), dpi=150)
    plt.close()
    print("  ✓ 04_temporal_patterns.png")

def plot_concentration(concentration, output_dir):
    """Plot concentration metrics."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Gini coefficient
    conc_sorted = concentration.sort_values('gini_coefficient', ascending=True).tail(20)
    axes[0].barh(conc_sorted['state'], conc_sorted['gini_coefficient'], color='crimson')
    axes[0].set_title('Gini Coefficient by State (Pincode Concentration)', fontweight='bold')
    axes[0].set_xlabel('Gini Coefficient (higher = more concentrated)')
    
    # Top 10% share
    axes[1].barh(conc_sorted['state'], conc_sorted['top_10_pct_share'], color='darkorange')
    axes[1].set_title('Top 10% Pincodes Share of Updates', fontweight='bold')
    axes[1].set_xlabel('Share of Total Updates')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '05_concentration.png'), dpi=150)
    plt.close()
    print("  ✓ 05_concentration.png")

def plot_clusters(cluster_data, cluster_summary, output_dir):
    """Plot cluster analysis."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Scatter plot
    scatter = axes[0].scatter(cluster_data['total_bio'], cluster_data['minor_share'],
                              c=cluster_data['cluster'], cmap='viridis', alpha=0.6, s=30)
    axes[0].set_xlabel('Total Updates (log scale)')
    axes[0].set_ylabel('Minor Share')
    axes[0].set_xscale('log')
    axes[0].set_title('District Clusters: Volume vs Minor Share', fontweight='bold')
    plt.colorbar(scatter, ax=axes[0], label='Cluster')
    
    # Cluster sizes
    axes[1].bar(cluster_summary['cluster'], cluster_summary['district_count'], 
                color=plt.cm.viridis(np.linspace(0, 1, 5)))
    axes[1].set_xlabel('Cluster')
    axes[1].set_ylabel('Number of Districts')
    axes[1].set_title('Districts per Cluster', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '06_clusters.png'), dpi=150)
    plt.close()
    print("  ✓ 06_clusters.png")

def plot_top_districts(district_agg, output_dir):
    """Plot top districts."""
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    # FIX 4: Create consistent state abbreviation function
    def abbrev_state(state):
        abbrev = {
            'Andhra Pradesh': 'AP', 'Arunachal Pradesh': 'AR', 'Assam': 'AS', 'Bihar': 'BR',
            'Chhattisgarh': 'CG', 'Goa': 'GA', 'Gujarat': 'GJ', 'Haryana': 'HR',
            'Himachal Pradesh': 'HP', 'Jharkhand': 'JH', 'Karnataka': 'KA', 'Kerala': 'KL',
            'Madhya Pradesh': 'MP', 'Maharashtra': 'MH', 'Manipur': 'MN', 'Meghalaya': 'ML',
            'Mizoram': 'MZ', 'Nagaland': 'NL', 'Odisha': 'OR', 'Punjab': 'PB',
            'Rajasthan': 'RJ', 'Sikkim': 'SK', 'Tamil Nadu': 'TN', 'Telangana': 'TG',
            'Tripura': 'TR', 'Uttar Pradesh': 'UP', 'Uttarakhand': 'UK', 'West Bengal': 'WB',
            'Delhi': 'DL', 'Jammu And Kashmir': 'JK', 'Puducherry': 'PY'
        }
        return abbrev.get(state, state[:3].upper())
    
    # Top 25 by volume
    top_vol = district_agg.nlargest(25, 'total_bio').copy()
    top_vol['label'] = top_vol['district'] + ' (' + top_vol['state'].apply(abbrev_state) + ')'
    axes[0].barh(top_vol['label'], top_vol['total_bio'], color='steelblue')
    axes[0].set_title('Top 25 Districts by Biometric Updates', fontweight='bold')
    axes[0].set_xlabel('Total Updates')
    
    # Top 25 by minor share (min 1000 updates)
    top_minor = district_agg[district_agg['total_bio'] > 1000].nlargest(25, 'minor_share').copy()
    top_minor['label'] = top_minor['district'] + ' (' + top_minor['state'].apply(abbrev_state) + ')'
    axes[1].barh(top_minor['label'], top_minor['minor_share'], color='coral')
    axes[1].set_title('Top 25 Districts by Minor Share (min 1000 updates)', fontweight='bold')
    axes[1].set_xlabel('Minor Share')
    # FIX 1: Add context to 50% reference line
    axes[1].axvline(x=0.5, color='gray', linestyle=':', alpha=0.5, label='50% reference')
    axes[1].legend(fontsize=8, loc='lower right')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '07_top_districts.png'), dpi=150)
    plt.close()
    print("  ✓ 07_top_districts.png")

def plot_volatility(volatility, output_dir):
    """Plot volatility analysis."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Top volatile districts
    top_volatile = volatility.nlargest(20, 'cv').copy()
    # FIX 4: Use consistent state abbreviations
    def abbrev_state(state):
        abbrev = {
            'Andhra Pradesh': 'AP', 'Arunachal Pradesh': 'AR', 'Assam': 'AS', 'Bihar': 'BR',
            'Chhattisgarh': 'CG', 'Goa': 'GA', 'Gujarat': 'GJ', 'Haryana': 'HR',
            'Himachal Pradesh': 'HP', 'Jharkhand': 'JH', 'Karnataka': 'KA', 'Kerala': 'KL',
            'Madhya Pradesh': 'MP', 'Maharashtra': 'MH', 'Manipur': 'MN', 'Meghalaya': 'ML',
            'Mizoram': 'MZ', 'Nagaland': 'NL', 'Odisha': 'OR', 'Punjab': 'PB',
            'Rajasthan': 'RJ', 'Sikkim': 'SK', 'Tamil Nadu': 'TN', 'Telangana': 'TG',
            'Tripura': 'TR', 'Uttar Pradesh': 'UP', 'Uttarakhand': 'UK', 'West Bengal': 'WB',
            'Delhi': 'DL', 'Jammu And Kashmir': 'JK', 'Puducherry': 'PY'
        }
        return abbrev.get(state, state[:3].upper())
    
    top_volatile['label'] = top_volatile['district'] + ' (' + top_volatile['state'].apply(abbrev_state) + ')'
    axes[0].barh(top_volatile['label'], top_volatile['cv'], color='purple')
    axes[0].set_title('Most Volatile Districts (CV of Daily Updates)', fontweight='bold')
    axes[0].set_xlabel('Coefficient of Variation')
    
    # Distribution
    sns.histplot(data=volatility, x='cv', bins=50, ax=axes[1])
    axes[1].set_title('Distribution of Volatility Across Districts', fontweight='bold')
    axes[1].set_xlabel('Coefficient of Variation')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '08_volatility.png'), dpi=150)
    plt.close()
    print("  ✓ 08_volatility.png")

# ============================================================================
# INSIGHT GENERATION
# ============================================================================
def generate_insights(age_results, temporal_results, geo_results, cluster_summary, concentration):
    """Generate structured insights."""
    
    insights = []
    
    # Insight 1: Age-group patterns
    high_minor_count = len(age_results['high_minor_districts'])
    insights.append({
        'title': 'High Minor Update Districts Identified',
        'finding': f"{high_minor_count} districts have >50% minor (5-17) biometric updates",
        'interpretation': 'Indicates active school-based biometric drives or child-focused schemes',
        'action': 'Coordinate with education departments; review capture quality for children'
    })
    
    # Insight 2: Weekend gap
    insights.append({
        'title': 'Significant Weekend Operations Gap',
        'finding': f"{temporal_results['weekend_drop']:.1f}% drop in updates on weekends",
        'interpretation': 'Most update centres operate on weekdays only',
        'action': 'Consider weekend camps in high-demand areas'
    })
    
    # Insight 3: Geographic concentration
    insights.append({
        'title': 'Update Activity Highly Concentrated',
        'finding': f"Top 50 districts account for {geo_results['top_50_share']:.1f}% of total updates",
        'interpretation': 'Urban centres dominate biometric update activity',
        'action': 'Increase outreach in low-activity districts'
    })
    
    # Insight 4: Minor share varies by state
    top_state = age_results['state_minor_share'].iloc[0]
    insights.append({
        'title': 'Minor Share Varies Significantly by State',
        'finding': f"{top_state['state']} has highest minor share at {top_state['minor_share']:.1%}",
        'interpretation': 'State-level policies and school enrollment drives impact age distribution',
        'action': 'Investigate states with unusually high/low minor ratios'
    })
    
    # Insight 5: Clustering
    insights.append({
        'title': 'Districts Form 5 Behavioral Segments',
        'finding': 'K-means clustering reveals distinct district profiles',
        'interpretation': 'Different intervention strategies needed per segment',
        'action': 'Tailor outreach based on cluster characteristics'
    })
    
    return insights

def generate_kpis(df, national_date, age_results):
    """Generate dashboard KPIs."""
    
    kpis = {
        'total_biometric_updates': int(df['total_bio'].sum()),
        'minor_updates': int(df['bio_age_5_17'].sum()),
        'adult_updates': int(df['bio_age_17_'].sum()),
        'national_minor_share': df['bio_age_5_17'].sum() / df['total_bio'].sum(),
        'states_covered': int(df['state'].nunique()),
        'districts_covered': int(df[['state', 'district']].drop_duplicates().shape[0]),
        'high_minor_districts': len(age_results['high_minor_districts']),
        'avg_daily_updates': int(national_date['total_bio'].mean()),
    }
    
    return kpis

# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    print("="*70)
    print("UIDAI DATA HACKATHON 2026 - DEEP BIOMETRIC ANALYSIS")
    print("Focus: Age-Group Dynamics | Concentration | Temporal Patterns")
    print("="*70)
    
    # Create output directories
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PLOTS_DIR, exist_ok=True)
    
    # Load and preprocess
    df = load_biometric_data()
    df = preprocess_data(df)
    df = engineer_features(df)
    
    # Aggregate
    print("\n" + "="*60)
    print("PHASE 4: AGGREGATION")
    print("="*60)
    district_date, state_month, national_date = aggregate_levels(df)
    
    # Concentration metrics
    concentration = calculate_concentration_metrics(df)
    print(f"  ✓ Calculated concentration metrics")
    
    # Volatility
    volatility = calculate_volatility(district_date)
    print(f"  ✓ Calculated volatility for {len(volatility)} districts")
    
    # Analysis
    age_results = analyze_age_patterns(df, district_date, state_month)
    temporal_results = analyze_temporal_patterns(national_date, district_date)
    geo_results = analyze_geographic_patterns(df, age_results['district_minor_share'])
    anomalies = detect_anomalies(district_date)
    cluster_data, cluster_summary = cluster_districts(age_results['district_minor_share'], volatility)
    
    # Visualizations
    print("\n" + "="*60)
    print("PHASE 5: GENERATING VISUALIZATIONS")
    print("="*60)
    setup_plots()
    
    plot_national_timeseries(national_date, PLOTS_DIR)
    plot_state_heatmaps(state_month, PLOTS_DIR)
    plot_age_group_analysis(age_results['state_minor_share'], age_results['district_minor_share'], PLOTS_DIR)
    plot_temporal_patterns(national_date, temporal_results['dow_pattern'], PLOTS_DIR)
    plot_concentration(concentration, PLOTS_DIR)
    plot_clusters(cluster_data, cluster_summary, PLOTS_DIR)
    plot_top_districts(age_results['district_minor_share'], PLOTS_DIR)
    plot_volatility(volatility, PLOTS_DIR)
    
    # Insights
    print("\n" + "="*60)
    print("PHASE 6: GENERATING INSIGHTS")
    print("="*60)
    
    insights = generate_insights(age_results, temporal_results, geo_results, cluster_summary, concentration)
    kpis = generate_kpis(df, national_date, age_results)
    
    print("\n📊 KEY PERFORMANCE INDICATORS:")
    for k, v in kpis.items():
        if isinstance(v, float):
            print(f"  • {k}: {v:.1%}")
        else:
            print(f"  • {k}: {v:,}")
    
    print("\n💡 TOP INSIGHTS:")
    for i, insight in enumerate(insights, 1):
        print(f"\n  {i}. {insight['title']}")
        print(f"     Finding: {insight['finding']}")
        print(f"     Action: {insight['action']}")
    
    # Export
    print("\n" + "="*60)
    print("PHASE 7: EXPORTING RESULTS")
    print("="*60)
    
    cluster_data.to_csv(os.path.join(OUTPUT_DIR, 'district_clusters.csv'), index=False)
    anomalies.to_csv(os.path.join(OUTPUT_DIR, 'anomalies.csv'), index=False)
    concentration.to_csv(os.path.join(OUTPUT_DIR, 'concentration_metrics.csv'), index=False)
    volatility.to_csv(os.path.join(OUTPUT_DIR, 'volatility_metrics.csv'), index=False)
    
    # KPIs
    kpi_df = pd.DataFrame([kpis])
    kpi_df.to_csv(os.path.join(OUTPUT_DIR, 'kpis.csv'), index=False)
    
    print(f"  ✓ Saved all outputs to {OUTPUT_DIR}")
    
    print("\n" + "="*70)
    print("✅ BIOMETRIC DEEP ANALYSIS COMPLETE!")
    print(f"📁 Output: {OUTPUT_DIR}")
    print(f"📊 Plots: {PLOTS_DIR}")
    print("="*70)
    
    return df, insights, kpis

if __name__ == "__main__":
    main()
