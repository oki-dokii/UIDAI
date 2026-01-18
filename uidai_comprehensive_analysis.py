#!/usr/bin/env python3
"""
UIDAI Data Hackathon 2026 - Comprehensive Analysis Pipeline
Unlocking Societal Trends in Aadhaar Enrolment and Updates

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
# CONFIGURATION - Using relative paths for portability
# ============================================================================
DATA_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIRS = {
    "biometric": os.path.join(DATA_BASE_DIR, "api_data_aadhar_biometric"),
    "demographic": os.path.join(DATA_BASE_DIR, "api_data_aadhar_demographic"),
    "enrolment": os.path.join(DATA_BASE_DIR, "api_data_aadhar_enrolment"),
}
OUTPUT_DIR = os.path.join(DATA_BASE_DIR, "analysis_output")
PLOTS_DIR = os.path.join(OUTPUT_DIR, "plots")

# Comprehensive state name normalization mapping (30+ variations)
STATE_MAP = {
    # Andaman & Nicobar variations
    "Andaman & Nicobar Islands": "Andaman And Nicobar Islands",
    "Andaman and Nicobar Islands": "Andaman And Nicobar Islands",
    
    # J&K variations
    "J & K": "Jammu And Kashmir",
    "J&K": "Jammu And Kashmir",
    "Jammu & Kashmir": "Jammu And Kashmir",
    "Jammu and Kashmir": "Jammu And Kashmir",
    
    # Dadra/Daman (merged UT)
    "Dadra & Nagar Haveli": "Dadra And Nagar Haveli And Daman And Diu",
    "Dadra and Nagar Haveli": "Dadra And Nagar Haveli And Daman And Diu",
    "Daman & Diu": "Dadra And Nagar Haveli And Daman And Diu",
    "Daman and Diu": "Dadra And Nagar Haveli And Daman And Diu",
    "The Dadra And Nagar Haveli And Daman And Diu": "Dadra And Nagar Haveli And Daman And Diu",
    
    # Other variations
    "Telengana": "Telangana",
    "Telanagana": "Telangana",
    "Orissa": "Odisha",
    "ODISHA": "Odisha",
    "Pondicherry": "Puducherry",
    "Chattisgarh": "Chhattisgarh",
    "Chhatisgarh": "Chhattisgarh",
    "Uttaranchal": "Uttarakhand",
    "Tamilnadu": "Tamil Nadu",
    "Tamil  Nadu": "Tamil Nadu",
    
    # West Bengal variations
    "WEST BENGAL": "West Bengal",
    "WESTBENGAL": "West Bengal",
    "Westbengal": "West Bengal",
    "West  Bengal": "West Bengal",
}

# Invalid entries to filter (districts/pincodes mistakenly in state column)
INVALID_STATE_ENTRIES = {
    "100000", "Balanagar", "Darbhanga", "Jaipur", "Nagpur",
    "Madanapalle", "Puttenahalli", "Raja Annamalai Puram",
}

# ============================================================================
# DATA LOADING
# ============================================================================
def load_dataset(directory, name):
    """Load all CSV files from directory into single DataFrame."""
    print(f"\n📂 Loading {name} data...")
    files = glob.glob(os.path.join(directory, "*.csv"))
    
    if not files:
        print(f"  ⚠️ No files found in {directory}")
        return pd.DataFrame()
    
    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f)
            dfs.append(df)
            print(f"  ✓ Loaded {os.path.basename(f)}: {len(df):,} rows")
        except Exception as e:
            print(f"  ✗ Error loading {f}: {e}")
    
    result = pd.concat(dfs, ignore_index=True)
    print(f"  📊 Total {name} records: {len(result):,}")
    return result

def load_all_data():
    """Load all three datasets."""
    return {
        'biometric': load_dataset(DIRS['biometric'], 'Biometric'),
        'demographic': load_dataset(DIRS['demographic'], 'Demographic'),
        'enrolment': load_dataset(DIRS['enrolment'], 'Enrolment')
    }

# ============================================================================
# DATA PREPROCESSING
# ============================================================================
def preprocess_dataset(df, dataset_type):
    """Clean and standardize a dataset with comprehensive normalization."""
    if df.empty:
        return df
    
    df = df.copy()
    initial_len = len(df)
    
    # Parse dates
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
        # Remove rows with invalid dates
        df = df[df['date'].notna()]
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['month_name'] = df['date'].dt.month_name()
        df['day_of_week'] = df['date'].dt.day_name()
    
    # Normalize state names
    if 'state' in df.columns:
        df['state'] = df['state'].astype(str).str.strip().str.title()
        df['state'] = df['state'].replace(STATE_MAP)
        # Filter out invalid entries (districts/pincodes in state column)
        df = df[~df['state'].isin(INVALID_STATE_ENTRIES)]
        # Filter rows where state is just digits (pincodes)
        df = df[~df['state'].str.match(r'^\d+$', na=False)]
    
    # Normalize district names
    if 'district' in df.columns:
        df['district'] = df['district'].astype(str).str.strip().str.title()
    
    # Deduplicate: keep first occurrence of each date-state-district-pincode combo
    dup_cols = ['date', 'state', 'district']
    if 'pincode' in df.columns:
        dup_cols.append('pincode')
    dup_cols = [c for c in dup_cols if c in df.columns]
    before_dedup = len(df)
    df = df.drop_duplicates(subset=dup_cols, keep='first')
    dup_count = before_dedup - len(df)
    
    removed = initial_len - len(df)
    if removed > 0:
        print(f"    Cleaned {dataset_type}: removed {removed:,} rows ({dup_count:,} duplicates)")
    
    return df

def aggregate_to_district_level(df):
    """Aggregate from pincode to state-district-date level."""
    group_cols = ['date', 'year', 'month', 'state', 'district']
    group_cols = [c for c in group_cols if c in df.columns]
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if 'pincode' in numeric_cols:
        numeric_cols.remove('pincode')
    
    return df.groupby(group_cols, as_index=False)[numeric_cols].sum()

def merge_datasets(enrol, bio, demo):
    """Merge all datasets at state-district-date level with proper handling of missing data."""
    merge_keys = ['date', 'year', 'month', 'state', 'district']
    
    # Merge enrolment with biometric
    merged = pd.merge(enrol, bio, on=merge_keys, how='outer', suffixes=('', '_bio'))
    # Merge with demographic
    merged = pd.merge(merged, demo, on=merge_keys, how='outer', suffixes=('', '_demo'))
    
    # Track which source each record came from (before fillna)
    has_enrol = merged.get('age_0_5', pd.Series([np.nan]*len(merged))).notna()
    has_bio = merged.get('bio_age_5_17', pd.Series([np.nan]*len(merged))).notna()
    has_demo = merged.get('demo_age_5_17', pd.Series([np.nan]*len(merged))).notna()
    
    # Fill NaN with 0 for numeric columns
    numeric_cols = merged.select_dtypes(include=[np.number]).columns
    merged[numeric_cols] = merged[numeric_cols].fillna(0)
    
    # CRITICAL FIX: Filter out rows with no actual activity
    # This prevents false data from outer join + fillna(0)
    total_before = len(merged)
    
    # Calculate totals for filtering
    merged['_total_enrol'] = merged.get('age_0_5', 0) + merged.get('age_5_17', 0) + merged.get('age_18_greater', 0)
    merged['_total_bio'] = merged.get('bio_age_5_17', 0) + merged.get('bio_age_17_', 0)
    merged['_total_demo'] = merged.get('demo_age_5_17', 0) + merged.get('demo_age_17_', 0)
    
    has_activity = (merged['_total_enrol'] > 0) | (merged['_total_bio'] > 0) | (merged['_total_demo'] > 0)
    merged = merged[has_activity]
    
    # Clean up temp columns
    merged = merged.drop(columns=['_total_enrol', '_total_bio', '_total_demo'], errors='ignore')
    
    filtered_count = total_before - len(merged)
    if filtered_count > 0:
        print(f"  ✓ Filtered {filtered_count:,} rows with no actual activity")
    
    return merged

# ============================================================================
# FEATURE ENGINEERING
# ============================================================================
def engineer_features(df):
    """Create all analytical features."""
    df = df.copy()
    
    # ------ BASE TOTALS ------
    df['total_enrolments'] = df['age_0_5'] + df['age_5_17'] + df['age_18_greater']
    df['total_bio_updates'] = df['bio_age_5_17'] + df['bio_age_17_']
    df['total_demo_updates'] = df['demo_age_5_17'] + df['demo_age_17_']
    df['total_updates'] = df['total_bio_updates'] + df['total_demo_updates']
    
    # ------ INTENSITY RATIOS ------
    df['update_intensity'] = np.where(
        df['total_enrolments'] > 0,
        df['total_updates'] / df['total_enrolments'],
        0
    )
    df['bio_intensity'] = np.where(
        df['total_enrolments'] > 0,
        df['total_bio_updates'] / df['total_enrolments'],
        0
    )
    df['demo_intensity'] = np.where(
        df['total_enrolments'] > 0,
        df['total_demo_updates'] / df['total_enrolments'],
        0
    )
    df['updates_per_1000'] = df['update_intensity'] * 1000
    
    # ------ COMPOSITION METRICS ------
    df['bio_share'] = np.where(
        df['total_updates'] > 0,
        df['total_bio_updates'] / df['total_updates'],
        0
    )
    df['demo_share'] = np.where(
        df['total_updates'] > 0,
        df['total_demo_updates'] / df['total_updates'],
        0
    )
    
    # Age group shares in enrolment
    df['young_enrol_share'] = np.where(
        df['total_enrolments'] > 0,
        df['age_0_5'] / df['total_enrolments'],
        0
    )
    df['child_enrol_share'] = np.where(
        df['total_enrolments'] > 0,
        df['age_5_17'] / df['total_enrolments'],
        0
    )
    df['adult_enrol_share'] = np.where(
        df['total_enrolments'] > 0,
        df['age_18_greater'] / df['total_enrolments'],
        0
    )
    
    # Age group shares in updates
    total_update_by_age = df['bio_age_5_17'] + df['demo_age_5_17'] + df['bio_age_17_'] + df['demo_age_17_']
    df['child_update_share'] = np.where(
        total_update_by_age > 0,
        (df['bio_age_5_17'] + df['demo_age_5_17']) / total_update_by_age,
        0
    )
    
    return df

def add_zscore_features(df):
    """Add z-score normalization for key metrics."""
    for col in ['update_intensity', 'bio_intensity', 'demo_intensity']:
        mean_val = df[col].mean()
        std_val = df[col].std()
        if std_val > 0:
            df[f'{col}_zscore'] = (df[col] - mean_val) / std_val
        else:
            df[f'{col}_zscore'] = 0
    return df

def add_temporal_features(df):
    """Add month-over-month and rolling metrics."""
    df = df.sort_values(['state', 'district', 'date'])
    
    # Group by state-district for temporal calculations
    for col in ['total_enrolments', 'total_updates', 'update_intensity']:
        # Month-over-month change
        df[f'{col}_mom'] = df.groupby(['state', 'district'])[col].pct_change() * 100
        # 3-period rolling average
        df[f'{col}_roll3'] = df.groupby(['state', 'district'])[col].transform(
            lambda x: x.rolling(3, min_periods=1).mean()
        )
    
    return df

def add_volatility_features(df):
    """Calculate volatility (std dev) for each district."""
    volatility = df.groupby(['state', 'district']).agg({
        'update_intensity': ['std', 'mean', 'count']
    }).reset_index()
    volatility.columns = ['state', 'district', 'intensity_std', 'intensity_mean', 'observation_count']
    
    # Coefficient of variation
    volatility['cv'] = np.where(
        volatility['intensity_mean'] > 0,
        volatility['intensity_std'] / volatility['intensity_mean'],
        0
    )
    
    # Trend score using simple linear regression approximation
    def calc_trend(group):
        if len(group) < 2:
            return 0
        x = np.arange(len(group))
        y = group['update_intensity'].values
        if np.std(y) == 0:
            return 0
        slope = np.polyfit(x, y, 1)[0]
        return slope
    
    trend = df.groupby(['state', 'district']).apply(calc_trend).reset_index()
    trend.columns = ['state', 'district', 'trend_score']
    
    volatility = volatility.merge(trend, on=['state', 'district'])
    return volatility

def add_percentile_ranks(df):
    """Add state and national percentile rankings."""
    # National percentile
    df['national_percentile'] = df['update_intensity'].rank(pct=True) * 100
    
    # State percentile
    df['state_percentile'] = df.groupby('state')['update_intensity'].rank(pct=True) * 100
    
    return df

# ============================================================================
# CLUSTERING & SEGMENTATION
# ============================================================================
def segment_districts(df, k_range=(2, 8)):
    """Segment districts into behavioral clusters with validated k selection.
    
    Uses silhouette score to determine optimal cluster count instead of
    arbitrary k=4. Prints validation metrics for transparency.
    """
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import silhouette_score
    
    # Aggregate to district level
    district_agg = df.groupby(['state', 'district']).agg({
        'total_enrolments': 'sum',
        'total_updates': 'sum',
        'update_intensity': 'mean',
        'bio_share': 'mean',
        'demo_share': 'mean'
    }).reset_index()
    
    # Filter districts with sufficient data
    district_agg = district_agg[district_agg['total_enrolments'] > 100]
    
    if len(district_agg) < 10:
        print("  ⚠️ Not enough districts for clustering")
        district_agg['cluster'] = 0
        return district_agg
    
    # Features for clustering
    features = ['update_intensity', 'bio_share']
    X = district_agg[features].values
    
    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Find optimal k using silhouette score
    print("  📊 Cluster validation (silhouette scores):")
    best_k = 4  # default fallback
    best_score = -1
    scores = {}
    
    k_min, k_max = k_range
    k_max = min(k_max, len(district_agg) - 1)  # Can't have more clusters than samples
    
    for k in range(k_min, k_max + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        score = silhouette_score(X_scaled, labels)
        scores[k] = score
        print(f"      k={k}: silhouette={score:.3f}")
        
        if score > best_score:
            best_score = score
            best_k = k
    
    print(f"  ✓ Optimal k={best_k} (silhouette={best_score:.3f})")
    
    # Final clustering with optimal k
    kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    district_agg['cluster'] = kmeans.fit_predict(X_scaled)
    
    # Reorder clusters by mean intensity for consistency
    cluster_means = district_agg.groupby('cluster')['update_intensity'].mean().sort_values()
    label_map = {old: new for new, old in enumerate(cluster_means.index)}
    district_agg['cluster'] = district_agg['cluster'].map(label_map)
    
    # Store validation metadata
    district_agg.attrs['optimal_k'] = best_k
    district_agg.attrs['silhouette_score'] = best_score
    district_agg.attrs['validation_scores'] = scores
    
    return district_agg

# ============================================================================
# ANOMALY DETECTION
# ============================================================================
def detect_anomalies(df, method='combined', zscore_threshold=3, iqr_multiplier=1.5):
    """Detect anomalous districts using multiple methods.
    
    Args:
        df: DataFrame with update_intensity and update_intensity_zscore columns
        method: Detection method - 'zscore', 'iqr', 'mad', or 'combined'
        zscore_threshold: Threshold for z-score method (default 3)
        iqr_multiplier: Multiplier for IQR method (default 1.5)
    
    Returns:
        DataFrame of anomalies with detection metadata
    
    Note: Z-score method may miss anomalies in skewed distributions.
    IQR is more robust for skewed data. 'combined' catches both.
    """
    df = df.copy()
    
    # Z-score based detection (existing method)
    df['is_zscore_anomaly'] = abs(df['update_intensity_zscore']) > zscore_threshold
    
    # IQR-based detection (more robust for skewed distributions)
    q75 = df['update_intensity'].quantile(0.75)
    q25 = df['update_intensity'].quantile(0.25)
    iqr = q75 - q25
    lower_bound = q25 - (iqr_multiplier * iqr)
    upper_bound = q75 + (iqr_multiplier * iqr)
    df['is_iqr_anomaly'] = (df['update_intensity'] < lower_bound) | (df['update_intensity'] > upper_bound)
    
    # MAD-based detection (robust to outliers)
    median = df['update_intensity'].median()
    mad = (df['update_intensity'] - median).abs().median()
    if mad > 0:
        df['mad_zscore'] = 0.6745 * (df['update_intensity'] - median) / mad
        df['is_mad_anomaly'] = abs(df['mad_zscore']) > zscore_threshold
    else:
        df['is_mad_anomaly'] = False
        df['mad_zscore'] = 0
    
    # Select anomalies based on method
    if method == 'zscore':
        mask = df['is_zscore_anomaly']
        detection_method = 'Z-score'
    elif method == 'iqr':
        mask = df['is_iqr_anomaly']
        detection_method = 'IQR'
    elif method == 'mad':
        mask = df['is_mad_anomaly']
        detection_method = 'MAD'
    else:  # 'combined' - union of all methods
        mask = df['is_zscore_anomaly'] | df['is_iqr_anomaly']
        detection_method = 'Combined (Z-score + IQR)'
    
    anomalies = df[mask].copy()
    anomalies['anomaly_type'] = np.where(
        anomalies['update_intensity_zscore'] > 0, 'High Spike', 'Low Drop'
    )
    anomalies['detection_method'] = detection_method
    
    # Print detection summary
    print(f"  📊 Anomaly Detection Summary:")
    print(f"      Z-score (>{zscore_threshold}σ): {df['is_zscore_anomaly'].sum():,} records")
    print(f"      IQR (>{iqr_multiplier}×IQR): {df['is_iqr_anomaly'].sum():,} records")
    print(f"      Combined: {mask.sum():,} records")
    
    return anomalies

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================
def setup_plots():
    """Configure matplotlib and seaborn."""
    plt.style.use('seaborn-v0_8-whitegrid')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 11
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 12

def plot_national_timeseries(df, output_dir):
    """Plot national-level time series."""
    national = df.groupby('date')[['total_enrolments', 'total_updates', 
                                    'total_bio_updates', 'total_demo_updates']].sum().reset_index()
    
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # Enrolments vs Updates
    ax1 = axes[0]
    ax1.plot(national['date'], national['total_enrolments'], 'b-o', label='Enrolments', linewidth=2)
    ax1.plot(national['date'], national['total_updates'], 'r-s', label='Updates', linewidth=2)
    ax1.set_title('National Aadhaar Activity: Enrolments vs Updates', fontweight='bold')
    ax1.set_ylabel('Volume')
    ax1.legend()
    ax1.tick_params(axis='x', rotation=45)
    
    # Bio vs Demo Updates
    ax2 = axes[1]
    ax2.stackplot(national['date'], national['total_bio_updates'], national['total_demo_updates'],
                  labels=['Biometric', 'Demographic'], alpha=0.8)
    ax2.set_title('Update Composition Over Time', fontweight='bold')
    ax2.set_ylabel('Volume')
    ax2.legend(loc='upper left')
    ax2.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '01_national_timeseries.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ Generated: 01_national_timeseries.png")

def plot_state_heatmap(df, output_dir):
    """Plot state-level intensity heatmap."""
    state_time = df.groupby(['state', 'date'])['update_intensity'].mean().reset_index()
    pivot = state_time.pivot(index='state', columns='date', values='update_intensity')
    
    # Top 15 states by volume
    top_states = df.groupby('state')['total_updates'].sum().nlargest(15).index
    pivot = pivot.loc[pivot.index.isin(top_states)]
    
    plt.figure(figsize=(16, 10))
    sns.heatmap(pivot, cmap='YlOrRd', annot=True, fmt='.2f', linewidths=0.5)
    plt.title('Update Intensity Heatmap by State Over Time', fontweight='bold', fontsize=16)
    plt.xlabel('Date')
    plt.ylabel('State')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '02_state_heatmap.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ Generated: 02_state_heatmap.png")

def plot_top_bottom_districts(df, output_dir):
    """Plot top and bottom districts by intensity."""
    district_agg = df.groupby(['state', 'district']).agg({
        'total_enrolments': 'sum',
        'total_updates': 'sum'
    }).reset_index()
    district_agg['intensity'] = district_agg['total_updates'] / district_agg['total_enrolments'] * 1000
    district_agg = district_agg[district_agg['total_enrolments'] > 1000]
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    # Top 15
    top15 = district_agg.nlargest(15, 'intensity')
    sns.barplot(data=top15, y='district', x='intensity', hue='state', ax=axes[0], dodge=False)
    axes[0].set_title('Top 15 High-Intensity Districts', fontweight='bold')
    axes[0].set_xlabel('Updates per 1000 Enrolments')
    axes[0].legend(title='State', fontsize=8)
    
    # Bottom 15
    bottom15 = district_agg.nsmallest(15, 'intensity')
    sns.barplot(data=bottom15, y='district', x='intensity', hue='state', ax=axes[1], dodge=False)
    axes[1].set_title('Bottom 15 Low-Intensity Districts', fontweight='bold')
    axes[1].set_xlabel('Updates per 1000 Enrolments')
    axes[1].legend(title='State', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '03_district_intensity_ranking.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ Generated: 03_district_intensity_ranking.png")

def plot_bivariate_analysis(df, output_dir):
    """Create bivariate scatter plots."""
    district_agg = df.groupby(['state', 'district']).agg({
        'total_enrolments': 'sum',
        'total_updates': 'sum',
        'total_bio_updates': 'sum',
        'total_demo_updates': 'sum',
        'update_intensity': 'mean'
    }).reset_index()
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # Enrolment vs Updates
    corr1 = district_agg['total_enrolments'].corr(district_agg['total_updates'])
    sns.scatterplot(data=district_agg, x='total_enrolments', y='total_updates', alpha=0.5, ax=axes[0,0])
    axes[0,0].set_title(f'Enrolments vs Updates (r={corr1:.2f})', fontweight='bold')
    
    # Bio vs Demo
    corr2 = district_agg['total_bio_updates'].corr(district_agg['total_demo_updates'])
    sns.scatterplot(data=district_agg, x='total_bio_updates', y='total_demo_updates', alpha=0.5, ax=axes[0,1])
    axes[0,1].set_title(f'Biometric vs Demographic (r={corr2:.2f})', fontweight='bold')
    
    # Size vs Intensity
    sns.scatterplot(data=district_agg, x='total_enrolments', y='update_intensity', alpha=0.5, ax=axes[1,0])
    axes[1,0].set_title('District Size vs Update Intensity', fontweight='bold')
    
    # Update Intensity Distribution
    sns.histplot(data=district_agg, x='update_intensity', bins=50, ax=axes[1,1])
    axes[1,1].set_title('Distribution of Update Intensity', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '04_bivariate_analysis.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ Generated: 04_bivariate_analysis.png")

def plot_cluster_analysis(clustered_df, output_dir):
    """Visualize district clusters."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Scatter plot
    scatter = axes[0].scatter(clustered_df['update_intensity'], clustered_df['bio_share'],
                              c=clustered_df['cluster'], cmap='viridis', alpha=0.6)
    axes[0].set_xlabel('Update Intensity')
    axes[0].set_ylabel('Biometric Share')
    axes[0].set_title('District Segmentation: Intensity vs Bio Share', fontweight='bold')
    plt.colorbar(scatter, ax=axes[0], label='Cluster')
    
    # Cluster sizes
    cluster_counts = clustered_df['cluster'].value_counts().sort_index()
    axes[1].bar(cluster_counts.index, cluster_counts.values, color=plt.cm.viridis(np.linspace(0, 1, 4)))
    axes[1].set_xlabel('Cluster')
    axes[1].set_ylabel('Number of Districts')
    axes[1].set_title('District Count by Cluster', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '05_cluster_analysis.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ Generated: 05_cluster_analysis.png")

def plot_pareto_analysis(df, output_dir):
    """Create Pareto/Lorenz curve for update concentration."""
    district_sum = df.groupby(['state', 'district'])['total_updates'].sum().sort_values(ascending=False).reset_index()
    district_sum['cumulative'] = district_sum['total_updates'].cumsum()
    district_sum['cum_pct'] = district_sum['cumulative'] / district_sum['total_updates'].sum()
    district_sum['district_pct'] = (district_sum.index + 1) / len(district_sum)
    
    plt.figure(figsize=(10, 8))
    plt.plot(district_sum['district_pct'], district_sum['cum_pct'], 'b-', linewidth=2, label='Actual')
    plt.plot([0, 1], [0, 1], 'r--', linewidth=1.5, label='Perfect Equality')
    plt.axvline(x=0.2, color='green', linestyle=':', alpha=0.7)
    
    y_at_20 = district_sum[district_sum['district_pct'] <= 0.2]['cum_pct'].iloc[-1] if len(district_sum) > 0 else 0
    plt.annotate(f'Top 20% → {y_at_20:.0%} of updates', xy=(0.2, y_at_20), 
                 xytext=(0.35, y_at_20-0.1), fontsize=11,
                 arrowprops=dict(arrowstyle='->', color='green'))
    
    plt.title('Update Concentration Analysis (Lorenz Curve)', fontweight='bold', fontsize=14)
    plt.xlabel('Cumulative % of Districts')
    plt.ylabel('Cumulative % of Updates')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '06_pareto_analysis.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ Generated: 06_pareto_analysis.png")

def plot_volatility_analysis(volatility_df, output_dir):
    """Plot volatility analysis."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Top volatile districts
    top_volatile = volatility_df.nlargest(15, 'intensity_std')
    sns.barplot(data=top_volatile, y='district', x='intensity_std', hue='state', ax=axes[0], dodge=False)
    axes[0].set_title('Most Volatile Districts (Std Dev of Intensity)', fontweight='bold')
    axes[0].set_xlabel('Standard Deviation')
    
    # Trend score distribution
    sns.histplot(data=volatility_df, x='trend_score', bins=30, ax=axes[1])
    axes[1].axvline(x=0, color='red', linestyle='--')
    axes[1].set_title('Distribution of Trend Scores', fontweight='bold')
    axes[1].set_xlabel('Trend Score (slope)')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '07_volatility_analysis.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ Generated: 07_volatility_analysis.png")

def plot_age_group_analysis(df, output_dir):
    """Analyze patterns by age group."""
    national = df.groupby('date').agg({
        'age_0_5': 'sum', 'age_5_17': 'sum', 'age_18_greater': 'sum',
        'bio_age_5_17': 'sum', 'bio_age_17_': 'sum',
        'demo_age_5_17': 'sum', 'demo_age_17_': 'sum'
    }).reset_index()
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Enrolment by age
    axes[0].stackplot(national['date'], national['age_0_5'], national['age_5_17'], national['age_18_greater'],
                      labels=['0-5 yrs', '5-17 yrs', '18+ yrs'], alpha=0.8)
    axes[0].set_title('Enrolments by Age Group', fontweight='bold')
    axes[0].legend(loc='upper left')
    axes[0].tick_params(axis='x', rotation=45)
    
    # Updates by age
    child_updates = national['bio_age_5_17'] + national['demo_age_5_17']
    adult_updates = national['bio_age_17_'] + national['demo_age_17_']
    axes[1].stackplot(national['date'], child_updates, adult_updates,
                      labels=['5-17 yrs', '17+ yrs'], alpha=0.8)
    axes[1].set_title('Updates by Age Group', fontweight='bold')
    axes[1].legend(loc='upper left')
    axes[1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '08_age_group_analysis.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ Generated: 08_age_group_analysis.png")

def plot_state_comparison(df, output_dir):
    """Compare key states."""
    state_agg = df.groupby('state').agg({
        'total_enrolments': 'sum',
        'total_updates': 'sum',
        'total_bio_updates': 'sum',
        'total_demo_updates': 'sum',
        'update_intensity': 'mean'
    }).reset_index()
    state_agg = state_agg.nlargest(15, 'total_updates')
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # Total Updates
    state_agg_sorted = state_agg.sort_values('total_updates', ascending=True)
    axes[0,0].barh(state_agg_sorted['state'], state_agg_sorted['total_updates'], color='steelblue')
    axes[0,0].set_title('Total Updates by State', fontweight='bold')
    axes[0,0].set_xlabel('Updates')
    
    # Update Intensity
    state_agg_sorted = state_agg.sort_values('update_intensity', ascending=True)
    axes[0,1].barh(state_agg_sorted['state'], state_agg_sorted['update_intensity'], color='coral')
    axes[0,1].set_title('Average Update Intensity by State', fontweight='bold')
    axes[0,1].set_xlabel('Intensity')
    
    # Bio vs Demo split
    state_agg['bio_pct'] = state_agg['total_bio_updates'] / state_agg['total_updates'] * 100
    state_agg_sorted = state_agg.sort_values('bio_pct', ascending=True)
    axes[1,0].barh(state_agg_sorted['state'], state_agg_sorted['bio_pct'], color='seagreen')
    axes[1,0].axvline(x=50, color='red', linestyle='--', alpha=0.7)
    axes[1,0].set_title('Biometric Update Share (%)', fontweight='bold')
    axes[1,0].set_xlabel('% Biometric')
    
    # Enrolment vs Updates scatter
    sns.scatterplot(data=state_agg, x='total_enrolments', y='total_updates', size='update_intensity',
                    sizes=(100, 1000), alpha=0.7, ax=axes[1,1])
    for i, row in state_agg.iterrows():
        axes[1,1].annotate(row['state'][:10], (row['total_enrolments'], row['total_updates']), fontsize=8)
    axes[1,1].set_title('State Profile: Size vs Activity', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '09_state_comparison.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ Generated: 09_state_comparison.png")

def plot_correlation_matrix(df, output_dir):
    """Plot correlation matrix of key metrics."""
    cols = ['total_enrolments', 'total_updates', 'total_bio_updates', 'total_demo_updates',
            'update_intensity', 'bio_share', 'young_enrol_share', 'child_enrol_share']
    corr_matrix = df[cols].corr()
    
    plt.figure(figsize=(10, 8))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r', 
                center=0, linewidths=0.5, square=True)
    plt.title('Feature Correlation Matrix', fontweight='bold', fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '10_correlation_matrix.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✓ Generated: 10_correlation_matrix.png")

# ============================================================================
# INSIGHT GENERATION
# ============================================================================
def generate_insights(df, volatility_df, clustered_df):
    """Generate key insights from analysis."""
    insights = []
    
    # 1. Concentration insight
    district_sum = df.groupby(['state', 'district'])['total_updates'].sum().sort_values(ascending=False)
    top_20_pct = len(district_sum) * 0.2
    top_20_updates = district_sum.iloc[:int(top_20_pct)].sum() / district_sum.sum() * 100
    insights.append({
        'title': 'Update Concentration',
        'finding': f"Top 20% of districts account for {top_20_updates:.1f}% of all updates",
        'implication': 'A small set of high-activity districts drives system load',
        'action': 'Prioritize infrastructure investment in top districts'
    })
    
    # 2. Bio vs Demo balance
    bio_total = df['total_bio_updates'].sum()
    demo_total = df['total_demo_updates'].sum()
    bio_pct = bio_total / (bio_total + demo_total) * 100
    insights.append({
        'title': 'Update Type Distribution',
        'finding': f"Biometric updates: {bio_pct:.1f}%, Demographic: {100-bio_pct:.1f}%",
        'implication': 'Higher demographic updates suggest population mobility',
        'action': 'Mobile update camps for high-demo regions'
    })
    
    # 3. Low interaction zones
    district_intensity = df.groupby(['state', 'district'])['update_intensity'].mean()
    low_interaction = (district_intensity < district_intensity.quantile(0.1)).sum()
    insights.append({
        'title': 'Low Interaction Zones',
        'finding': f"{low_interaction} districts show very low update activity",
        'implication': 'Potential awareness or accessibility issues',
        'action': 'Target outreach programs in these districts'
    })
    
    # 4. Volatility hotspots
    high_volatile = volatility_df[volatility_df['intensity_std'] > volatility_df['intensity_std'].quantile(0.9)]
    insights.append({
        'title': 'Volatility Hotspots',
        'finding': f"{len(high_volatile)} districts show high intensity volatility",
        'implication': 'Possible seasonal patterns or operational inconsistency',
        'action': 'Investigate infrastructure and campaign timing'
    })
    
    # 5. Age group patterns
    child_enrol = df['age_5_17'].sum()
    adult_enrol = df['age_18_greater'].sum()
    child_ratio = child_enrol / (child_enrol + adult_enrol) * 100
    insights.append({
        'title': 'Age Group Distribution',
        'finding': f"School-age (5-17) enrolments: {child_ratio:.1f}% of total",
        'implication': 'School-based enrolment drives significant volume',
        'action': 'Coordinate with education departments for enrollment drives'
    })
    
    return insights

def generate_kpis(df):
    """Generate monitoring KPIs."""
    kpis = []
    
    # National metrics
    total_enrol = df['total_enrolments'].sum()
    total_updates = df['total_updates'].sum()
    avg_intensity = df['update_intensity'].mean()
    
    kpis.append({'name': 'Total Enrolments', 'value': f"{total_enrol:,.0f}"})
    kpis.append({'name': 'Total Updates', 'value': f"{total_updates:,.0f}"})
    kpis.append({'name': 'Avg Update Intensity', 'value': f"{avg_intensity:.4f}"})
    kpis.append({'name': 'Updates per 1000', 'value': f"{avg_intensity*1000:.2f}"})
    
    # Bio/Demo split
    bio_share = df['total_bio_updates'].sum() / total_updates * 100
    kpis.append({'name': 'Biometric Share', 'value': f"{bio_share:.1f}%"})
    kpis.append({'name': 'Demographic Share', 'value': f"{100-bio_share:.1f}%"})
    
    # Coverage
    unique_states = df['state'].nunique()
    unique_districts = df[['state', 'district']].drop_duplicates().shape[0]
    kpis.append({'name': 'States Covered', 'value': str(unique_states)})
    kpis.append({'name': 'Districts Covered', 'value': str(unique_districts)})
    
    return kpis

# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    print("=" * 70)
    print("UIDAI DATA HACKATHON 2026 - COMPREHENSIVE ANALYSIS PIPELINE")
    print("Unlocking Societal Trends in Aadhaar Enrolment and Updates")
    print("=" * 70)
    
    # Create output directories
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PLOTS_DIR, exist_ok=True)
    
    # --------------- DATA LOADING ---------------
    print("\n" + "="*50)
    print("PHASE 1: DATA LOADING")
    print("="*50)
    data = load_all_data()
    
    # --------------- PREPROCESSING ---------------
    print("\n" + "="*50)
    print("PHASE 2: DATA PREPROCESSING")
    print("="*50)
    for key in data:
        data[key] = preprocess_dataset(data[key], key)
        data[key] = aggregate_to_district_level(data[key])
        print(f"  ✓ Preprocessed {key}: {len(data[key]):,} district-date records")
    
    # Merge datasets
    print("\n  🔗 Merging datasets...")
    merged_df = merge_datasets(data['enrolment'], data['biometric'], data['demographic'])
    print(f"  ✓ Merged dataset: {len(merged_df):,} records")
    
    # --------------- FEATURE ENGINEERING ---------------
    print("\n" + "="*50)
    print("PHASE 3: FEATURE ENGINEERING")
    print("="*50)
    merged_df = engineer_features(merged_df)
    merged_df = add_zscore_features(merged_df)
    merged_df = add_temporal_features(merged_df)
    merged_df = add_percentile_ranks(merged_df)
    print(f"  ✓ Created {len([c for c in merged_df.columns if c not in data['enrolment'].columns])} new features")
    
    # Volatility features
    volatility_df = add_volatility_features(merged_df)
    print(f"  ✓ Computed volatility metrics for {len(volatility_df)} districts")
    
    # --------------- SEGMENTATION ---------------
    print("\n" + "="*50)
    print("PHASE 4: DISTRICT SEGMENTATION")
    print("="*50)
    try:
        clustered_df = segment_districts(merged_df)
        print(f"  ✓ Segmented {len(clustered_df)} districts into 4 clusters")
    except Exception as e:
        print(f"  ⚠️ Clustering skipped: {e}")
        clustered_df = None
    
    # --------------- ANOMALY DETECTION ---------------
    print("\n" + "="*50)
    print("PHASE 5: ANOMALY DETECTION")
    print("="*50)
    anomalies = detect_anomalies(merged_df)
    print(f"  ✓ Detected {len(anomalies)} anomalous records (z-score > 3)")
    
    # --------------- VISUALIZATION ---------------
    print("\n" + "="*50)
    print("PHASE 6: GENERATING VISUALIZATIONS")
    print("="*50)
    setup_plots()
    
    plot_national_timeseries(merged_df, PLOTS_DIR)
    plot_state_heatmap(merged_df, PLOTS_DIR)
    plot_top_bottom_districts(merged_df, PLOTS_DIR)
    plot_bivariate_analysis(merged_df, PLOTS_DIR)
    if clustered_df is not None:
        plot_cluster_analysis(clustered_df, PLOTS_DIR)
    plot_pareto_analysis(merged_df, PLOTS_DIR)
    plot_volatility_analysis(volatility_df, PLOTS_DIR)
    plot_age_group_analysis(merged_df, PLOTS_DIR)
    plot_state_comparison(merged_df, PLOTS_DIR)
    plot_correlation_matrix(merged_df, PLOTS_DIR)
    
    # --------------- INSIGHTS ---------------
    print("\n" + "="*50)
    print("PHASE 7: GENERATING INSIGHTS")
    print("="*50)
    insights = generate_insights(merged_df, volatility_df, clustered_df)
    kpis = generate_kpis(merged_df)
    
    print("\n📊 KEY PERFORMANCE INDICATORS:")
    for kpi in kpis:
        print(f"  • {kpi['name']}: {kpi['value']}")
    
    print("\n💡 TOP INSIGHTS:")
    for i, insight in enumerate(insights, 1):
        print(f"\n  {i}. {insight['title']}")
        print(f"     Finding: {insight['finding']}")
        print(f"     Action: {insight['action']}")
    
    # --------------- EXPORT ---------------
    print("\n" + "="*50)
    print("PHASE 8: EXPORTING RESULTS")
    print("="*50)
    
    # Save processed data
    merged_df.to_csv(os.path.join(OUTPUT_DIR, 'processed_data.csv'), index=False)
    volatility_df.to_csv(os.path.join(OUTPUT_DIR, 'volatility_metrics.csv'), index=False)
    if clustered_df is not None:
        clustered_df.to_csv(os.path.join(OUTPUT_DIR, 'district_clusters.csv'), index=False)
    anomalies.to_csv(os.path.join(OUTPUT_DIR, 'anomalies.csv'), index=False)
    
    print(f"  ✓ Saved processed_data.csv ({len(merged_df):,} rows)")
    print(f"  ✓ Saved volatility_metrics.csv")
    print(f"  ✓ Saved district_clusters.csv")
    print(f"  ✓ Saved anomalies.csv")
    
    print("\n" + "="*70)
    print("✅ ANALYSIS COMPLETE!")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print(f"📊 Plots saved to: {PLOTS_DIR}")
    print("="*70)
    
    return merged_df, volatility_df, clustered_df, insights, kpis

if __name__ == "__main__":
    main()

