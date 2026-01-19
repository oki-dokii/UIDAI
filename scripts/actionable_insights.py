#!/usr/bin/env python3
"""
UIDAI Data Hackathon 2026 - ACTIONABLE INSIGHTS
Deep-dive analysis generating specific recommendations:
1. Top 20 Districts with Worst Child Attention Gap
2. Child Attention Gap Trend Analysis
3. District-Level Recommendations Table
4. Enhanced Cluster Profiling

Outputs: Actionable tables and visualizations for PPT
"""

import os
import sys
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_FILE = os.path.join(BASE_DIR, "outputs", "integrated_analysis", "integrated_data.csv")
CLUSTER_FILE = os.path.join(BASE_DIR, "outputs", "integrated_analysis", "district_clusters.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "actionable_insights")

# ============================================================================
# DATA LOADING
# ============================================================================

def load_data():
    """Load integrated data and cluster data."""
    print(f"📂 Loading data...")
    
    if not os.path.exists(DATA_FILE):
        print(f"❌ Data file not found: {DATA_FILE}")
        sys.exit(1)
    
    df = pd.read_csv(DATA_FILE)
    print(f"   Loaded {len(df):,} records from integrated_data.csv")
    
    # Load clusters if available
    clusters = None
    if os.path.exists(CLUSTER_FILE):
        clusters = pd.read_csv(CLUSTER_FILE)
        print(f"   Loaded {len(clusters):,} district clusters")
    
    return df, clusters


# ============================================================================
# TOP 20 WORST CHILD ATTENTION GAP
# ============================================================================

def analyze_worst_child_gaps(df, n=20):
    """Identify districts with worst child attention gap."""
    
    # Aggregate to district level
    district_agg = df.groupby(['state', 'district']).agg({
        'total_enrol': 'sum',
        'total_updates': 'sum',
        'child_attention_gap': 'mean',
        'enrol_child_share': 'mean',
        'child_share_updates': 'mean'
    }).reset_index()
    
    # Filter out districts with no data
    district_agg = district_agg[district_agg['total_enrol'] + district_agg['total_updates'] > 0]
    
    # Get worst gaps (most negative = children most under-served)
    worst = district_agg.nsmallest(n, 'child_attention_gap').copy()
    
    # Add interpretive columns
    worst['gap_severity'] = pd.cut(
        worst['child_attention_gap'], 
        bins=[-np.inf, -0.5, -0.3, -0.1, 0],
        labels=['🔴 Critical', '🟠 Severe', '🟡 Moderate', '🟢 Mild']
    )
    
    worst['recommendation'] = worst.apply(
        lambda x: f"Increase child update campaigns in {x['district']}, {x['state'][:3].upper()}", 
        axis=1
    )
    
    return worst


def plot_worst_child_gaps(worst_gaps, output_file):
    """Visualize worst child attention gaps."""
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Create district labels
    worst_gaps = worst_gaps.copy()
    worst_gaps['label'] = worst_gaps['district'] + '\n(' + worst_gaps['state'].str[:15] + ')'
    
    # Color by severity
    colors = {
        '🔴 Critical': '#d62728',
        '🟠 Severe': '#ff7f0e',
        '🟡 Moderate': '#bcbd22',
        '🟢 Mild': '#2ca02c'
    }
    bar_colors = [colors.get(str(s), '#7f7f7f') for s in worst_gaps['gap_severity']]
    
    # Sort for visualization
    worst_gaps = worst_gaps.sort_values('child_attention_gap', ascending=True)
    
    bars = ax.barh(worst_gaps['label'], worst_gaps['child_attention_gap'], 
                  color=bar_colors, edgecolor='white', linewidth=0.5)
    
    # Add value labels
    for bar, val in zip(bars, worst_gaps['child_attention_gap']):
        ax.annotate(f'{val:.3f}', 
                   xy=(val, bar.get_y() + bar.get_height()/2),
                   xytext=(-5, 0), textcoords='offset points',
                   ha='right', va='center', fontsize=9, fontweight='bold', color='white')
    
    # Zero line
    ax.axvline(x=0, color='black', linewidth=1.5)
    
    # Styling
    ax.set_xlabel('Child Attention Gap\n(Negative = Children Under-Served in Updates)', fontsize=12, fontweight='bold')
    ax.set_ylabel('')
    ax.set_title('🚨 Top 20 Districts with Worst Child Attention Gap\nPriority Targets for UIDAI Intervention', 
                fontsize=14, fontweight='bold', pad=20)
    
    # Legend
    legend_patches = [Patch(facecolor=c, edgecolor='white', label=l) 
                      for l, c in colors.items()]
    ax.legend(handles=legend_patches, loc='lower right', title='Severity', framealpha=0.9)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    # Save
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, output_file)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"   ✅ Saved: {output_path}")
    return output_path


# ============================================================================
# CHILD GAP TREND ANALYSIS
# ============================================================================

def analyze_child_gap_trend(df):
    """Analyze trend of child attention gap over time."""
    
    # Create date column if not present
    if 'date' not in df.columns:
        df['date'] = pd.to_datetime(df['year'].astype(str) + '-' + df['month'].astype(str).str.zfill(2) + '-01')
    
    # Monthly aggregation
    monthly = df.groupby('date').agg({
        'child_attention_gap': 'mean',
        'enrol_child_share': 'mean',
        'child_share_updates': 'mean'
    }).reset_index()
    
    monthly = monthly.sort_values('date')
    
    return monthly


def plot_child_gap_trend(monthly, output_file):
    """Visualize child attention gap trend."""
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Main gap line
    ax.plot(monthly['date'], monthly['child_attention_gap'], 
            'o-', color='#d62728', linewidth=2.5, markersize=8, label='Child Attention Gap')
    
    # Fill area
    ax.fill_between(monthly['date'], 0, monthly['child_attention_gap'], 
                   where=monthly['child_attention_gap'] < 0, 
                   alpha=0.3, color='#d62728', label='Under-Served Zone')
    
    ax.fill_between(monthly['date'], 0, monthly['child_attention_gap'], 
                   where=monthly['child_attention_gap'] >= 0, 
                   alpha=0.3, color='#2ca02c', label='Well-Served Zone')
    
    # Zero line
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1.5)
    
    # Calculate trend
    x = np.arange(len(monthly))
    y = monthly['child_attention_gap'].values
    mask = np.isfinite(y)
    if mask.sum() >= 2:
        coeffs = np.polyfit(x[mask], y[mask], 1)
        trend_line = np.polyval(coeffs, x)
        ax.plot(monthly['date'], trend_line, '--', color='navy', linewidth=2, 
               label=f'Trend ({coeffs[0]:+.4f}/month)')
    
    # Styling
    ax.set_xlabel('Month', fontsize=12, fontweight='bold')
    ax.set_ylabel('Child Attention Gap', fontsize=12, fontweight='bold')
    ax.set_title('📈 Child Attention Gap Over Time\nIs the System Improving?', 
                fontsize=14, fontweight='bold', pad=20)
    
    ax.legend(loc='lower right', framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    # Save
    output_path = os.path.join(OUTPUT_DIR, output_file)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"   ✅ Saved: {output_path}")
    return output_path


# ============================================================================
# ENHANCED CLUSTER PROFILING
# ============================================================================

CLUSTER_NAMES = {
    0: "📍 Saturated Urban Centers",
    1: "🌱 Emerging Growth Hubs", 
    2: "🔄 Migration Corridors",
    3: "🏘️ Under-served Rural Areas",
    4: "⭐ High-Performing Districts"
}

CLUSTER_DESCRIPTIONS = {
    0: "Low enrolment, high updates - mature Aadhaar penetration, focus on maintenance",
    1: "High enrolment, low updates - new Aadhaar growth areas, need update awareness",
    2: "High demographic churn - population mobility, need flexible service delivery",
    3: "Low activity overall - require mobile camps and awareness campaigns",
    4: "Balanced high activity - model districts for best practices"
}


def enhance_cluster_profiles(df, clusters):
    """Create meaningful cluster profiles."""
    
    if clusters is None:
        print("   ⚠️ No cluster data available. Skipping cluster enhancement.")
        return None
    
    # Merge cluster info
    if 'cluster' not in df.columns:
        df = df.merge(clusters[['district', 'state', 'cluster']], on=['district', 'state'], how='left')
    
    # Aggregate by cluster
    cluster_profiles = df.groupby('cluster').agg({
        'total_enrol': 'sum',
        'total_updates': 'sum',
        'total_intensity': 'mean',
        'child_attention_gap': 'mean',
        'demo_minor_share': 'mean',
        'bio_minor_share': 'mean',
        'district': 'nunique'
    }).reset_index()
    
    cluster_profiles.columns = ['Cluster', 'Total Enrol', 'Total Updates', 
                                'Avg Intensity', 'Avg Child Gap', 
                                'Demo Minor %', 'Bio Minor %', 'N Districts']
    
    # Add cluster names and descriptions
    cluster_profiles['Cluster Name'] = cluster_profiles['Cluster'].map(
        lambda x: CLUSTER_NAMES.get(x, f"Cluster {x}")
    )
    cluster_profiles['Description'] = cluster_profiles['Cluster'].map(
        lambda x: CLUSTER_DESCRIPTIONS.get(x, "Mixed characteristics")
    )
    
    # Calculate recommendation priority
    cluster_profiles['Priority'] = cluster_profiles['Avg Child Gap'].abs() * cluster_profiles['N Districts']
    
    return cluster_profiles


def plot_cluster_profiles(profiles, output_file):
    """Visualize enhanced cluster profiles."""
    
    if profiles is None:
        return None
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # 1. District count by cluster
    ax1 = axes[0, 0]
    colors = plt.cm.Set2(np.linspace(0, 1, len(profiles)))
    bars = ax1.bar(profiles['Cluster Name'].str[:15], profiles['N Districts'], color=colors)
    ax1.set_ylabel('Number of Districts')
    ax1.set_title('District Distribution by Cluster', fontweight='bold')
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Update Intensity
    ax2 = axes[0, 1]
    ax2.bar(profiles['Cluster Name'].str[:15], profiles['Avg Intensity'], color=colors)
    ax2.set_ylabel('Average Update Intensity')
    ax2.set_title('Update Intensity by Cluster', fontweight='bold')
    ax2.tick_params(axis='x', rotation=45)
    
    # 3. Child Attention Gap
    ax3 = axes[1, 0]
    bar_colors = ['#d62728' if x < 0 else '#2ca02c' for x in profiles['Avg Child Gap']]
    ax3.bar(profiles['Cluster Name'].str[:15], profiles['Avg Child Gap'], color=bar_colors)
    ax3.axhline(y=0, color='black', linewidth=1)
    ax3.set_ylabel('Average Child Attention Gap')
    ax3.set_title('Child Attention Gap by Cluster', fontweight='bold')
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. Total Volume (Enrol + Updates)
    ax4 = axes[1, 1]
    ax4.bar(profiles['Cluster Name'].str[:15], 
           (profiles['Total Enrol'] + profiles['Total Updates']) / 1e6, 
           color=colors)
    ax4.set_ylabel('Total Activity (Millions)')
    ax4.set_title('Total Activity Volume by Cluster', fontweight='bold')
    ax4.tick_params(axis='x', rotation=45)
    
    plt.suptitle('🏷️ Enhanced Cluster Profiles\nMeaningful Segmentation for Policy Action', 
                fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    # Save
    output_path = os.path.join(OUTPUT_DIR, output_file)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"   ✅ Saved: {output_path}")
    return output_path


# ============================================================================
# RECOMMENDATION TABLE
# ============================================================================

def generate_recommendations(worst_gaps, cluster_profiles):
    """Generate actionable recommendation table."""
    
    recommendations = []
    
    # From worst child gaps
    for _, row in worst_gaps.head(10).iterrows():
        recommendations.append({
            'Priority': '🔴 High',
            'District': row['district'],
            'State': row['state'],
            'Issue': f"Child Gap: {row['child_attention_gap']:.3f}",
            'Action': 'Launch targeted child update campaign',
            'Timeline': '0-3 months'
        })
    
    # From cluster analysis if available
    if cluster_profiles is not None:
        worst_cluster = cluster_profiles.nsmallest(1, 'Avg Child Gap').iloc[0]
        recommendations.append({
            'Priority': '🟠 Medium',
            'District': f"All {int(worst_cluster['N Districts'])} districts",
            'State': f"Cluster: {worst_cluster['Cluster Name'][:20]}",
            'Issue': f"Cluster-wide child gap: {worst_cluster['Avg Child Gap']:.3f}",
            'Action': 'Deploy mobile update camps',
            'Timeline': '3-6 months'
        })
    
    return pd.DataFrame(recommendations)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 60)
    print("📋 UIDAI ACTIONABLE INSIGHTS ANALYSIS")
    print("    Generating Specific Recommendations")
    print("=" * 60)
    
    # Load data
    df, clusters = load_data()
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("\n" + "=" * 60)
    print("📊 GENERATING INSIGHTS")
    print("=" * 60)
    
    # 1. Top 20 Worst Child Gaps
    print("\n1️⃣ Analyzing Worst Child Attention Gaps...")
    worst_gaps = analyze_worst_child_gaps(df, n=20)
    plot_worst_child_gaps(worst_gaps, '01_worst_child_gaps.png')
    
    # Save to CSV
    worst_gaps_path = os.path.join(OUTPUT_DIR, 'top_20_child_gap_districts.csv')
    worst_gaps[['state', 'district', 'child_attention_gap', 'gap_severity', 
                'enrol_child_share', 'child_share_updates', 'recommendation']].to_csv(worst_gaps_path, index=False)
    print(f"   ✅ Saved: {worst_gaps_path}")
    
    # 2. Child Gap Trend
    print("\n2️⃣ Analyzing Child Gap Trend Over Time...")
    monthly_gap = analyze_child_gap_trend(df)
    plot_child_gap_trend(monthly_gap, '02_child_gap_trend.png')
    
    # 3. Enhanced Cluster Profiles
    print("\n3️⃣ Enhancing Cluster Profiles...")
    cluster_profiles = enhance_cluster_profiles(df, clusters)
    if cluster_profiles is not None:
        plot_cluster_profiles(cluster_profiles, '03_cluster_profiles.png')
        
        # Save cluster profiles
        cluster_path = os.path.join(OUTPUT_DIR, 'enhanced_cluster_profiles.csv')
        cluster_profiles.to_csv(cluster_path, index=False)
        print(f"   ✅ Saved: {cluster_path}")
    
    # 4. Recommendation Table
    print("\n4️⃣ Generating Recommendation Table...")
    recommendations = generate_recommendations(worst_gaps, cluster_profiles)
    rec_path = os.path.join(OUTPUT_DIR, 'priority_recommendations.csv')
    recommendations.to_csv(rec_path, index=False)
    print(f"   ✅ Saved: {rec_path}")
    
    # 5. Summary visualization
    print("\n5️⃣ Creating Summary Dashboard...")
    
    fig = plt.figure(figsize=(16, 12))
    
    # Title
    fig.suptitle('📋 UIDAI Actionable Insights Summary\nKey Recommendations for Policy Action', 
                fontsize=16, fontweight='bold', y=0.98)
    
    # Create grid
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
    
    # Panel 1: Worst gaps bar chart (simplified)
    ax1 = fig.add_subplot(gs[0, 0])
    top10 = worst_gaps.nsmallest(10, 'child_attention_gap')
    ax1.barh(top10['district'], top10['child_attention_gap'], color='#d62728')
    ax1.axvline(x=0, color='black', linewidth=1)
    ax1.set_xlabel('Child Attention Gap')
    ax1.set_title('🚨 Top 10 Priority Districts', fontweight='bold')
    
    # Panel 2: Gap distribution
    ax2 = fig.add_subplot(gs[0, 1])
    gap_counts = worst_gaps['gap_severity'].value_counts()
    colors_pie = ['#d62728', '#ff7f0e', '#bcbd22', '#2ca02c']
    ax2.pie(gap_counts.values, labels=gap_counts.index, colors=colors_pie[:len(gap_counts)],
           autopct='%1.0f%%', startangle=90)
    ax2.set_title('📊 Gap Severity Distribution', fontweight='bold')
    
    # Panel 3: Monthly trend (simplified)
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(monthly_gap['date'], monthly_gap['child_attention_gap'], 'o-', color='#d62728', linewidth=2)
    ax3.axhline(y=0, color='gray', linestyle='--')
    ax3.fill_between(monthly_gap['date'], 0, monthly_gap['child_attention_gap'], 
                    where=monthly_gap['child_attention_gap'] < 0, alpha=0.3, color='#d62728')
    ax3.set_xlabel('Month')
    ax3.set_ylabel('Gap')
    ax3.set_title('📈 Gap Trend Over Time', fontweight='bold')
    
    # Panel 4: Key stats
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.axis('off')
    
    stats_text = f"""
    📊 KEY STATISTICS
    
    🔢 Total Districts Analyzed: {len(df['district'].unique()):,}
    
    🔴 Critical Gap Districts: {len(worst_gaps[worst_gaps['gap_severity'] == '🔴 Critical'])}
    
    🟠 Severe Gap Districts: {len(worst_gaps[worst_gaps['gap_severity'] == '🟠 Severe'])}
    
    📉 Worst Gap: {worst_gaps['child_attention_gap'].min():.3f}
       ({worst_gaps.iloc[0]['district']}, {worst_gaps.iloc[0]['state'][:20]})
    
    📈 National Avg Gap: {df['child_attention_gap'].mean():.3f}
    """
    
    ax4.text(0.1, 0.5, stats_text, transform=ax4.transAxes, fontsize=12,
            verticalalignment='center', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='#f0f0f0', alpha=0.8))
    
    plt.tight_layout()
    
    output_path = os.path.join(OUTPUT_DIR, '00_insights_summary.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"   ✅ Saved: {output_path}")
    
    print("\n" + "=" * 60)
    print("✅ ACTIONABLE INSIGHTS COMPLETE")
    print(f"   Output directory: {OUTPUT_DIR}")
    print("=" * 60)
    
    # Print key findings
    print("\n🎯 KEY ACTIONABLE FINDINGS:")
    print(f"\n   1. {len(worst_gaps[worst_gaps['gap_severity'] == '🔴 Critical'])} districts need IMMEDIATE child update campaigns")
    print(f"   2. Worst gap: {worst_gaps.iloc[0]['district']}, {worst_gaps.iloc[0]['state']}")
    print(f"      Gap value: {worst_gaps.iloc[0]['child_attention_gap']:.3f}")
    print(f"   3. National average gap: {df['child_attention_gap'].mean():.3f}")
    
    if cluster_profiles is not None:
        worst_cluster = cluster_profiles.nsmallest(1, 'Avg Child Gap').iloc[0]
        print(f"   4. Cluster needing most attention: {worst_cluster['Cluster Name']}")
        print(f"      ({int(worst_cluster['N Districts'])} districts, avg gap: {worst_cluster['Avg Child Gap']:.3f})")


if __name__ == "__main__":
    main()
