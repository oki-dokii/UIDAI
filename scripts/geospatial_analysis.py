#!/usr/bin/env python3
"""
UIDAI Data Hackathon 2026 - GEOSPATIAL ANALYSIS
Creates India district-level choropleth maps for:
1. Update Intensity
2. Child Attention Gap

Outputs: High-resolution PNG maps ready for PPT inclusion
"""

import os
import sys
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Patch

warnings.filterwarnings('ignore')

# Try importing geopandas - if unavailable, use fallback visualization
try:
    import geopandas as gpd
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False
    print("⚠️ geopandas not available. Using fallback state-level visualization.")

# ============================================================================
# CONFIGURATION
# ============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_FILE = os.path.join(BASE_DIR, "outputs", "integrated_analysis", "integrated_data.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "geospatial_plots")

# India district shapefile - will download if not present
# Note: For offline use, user should provide their own shapefile
SHAPEFILE_URL = "https://raw.githubusercontent.com/datameet/maps/master/districts/2011-census/india-districts-census-2011.geojson"

# ============================================================================
# DATA LOADING
# ============================================================================

def load_uidai_data():
    """Load and aggregate UIDAI data to state level for mapping."""
    print(f"📂 Loading data from: {DATA_FILE}")
    
    if not os.path.exists(DATA_FILE):
        print(f"❌ Data file not found: {DATA_FILE}")
        print("   Run integrated_analysis.py first to generate this file.")
        sys.exit(1)
    
    df = pd.read_csv(DATA_FILE)
    print(f"   Loaded {len(df):,} records")
    
    # Aggregate to state level (more reliable for mapping than district)
    state_agg = df.groupby('state').agg({
        'total_enrol': 'sum',
        'total_updates': 'sum',
        'total_intensity': 'mean',
        'child_attention_gap': 'mean',
        'demo_intensity': 'mean',
        'bio_intensity': 'mean'
    }).reset_index()
    
    # Normalize state names for matching
    state_agg['state_normalized'] = state_agg['state'].str.upper().str.strip()
    
    print(f"   Aggregated to {len(state_agg)} states/UTs")
    return df, state_agg


def load_india_shapefile():
    """Load India state boundaries."""
    if not HAS_GEOPANDAS:
        return None
    
    try:
        # Try loading from URL
        print("📥 Loading India state boundaries...")
        gdf = gpd.read_file("https://raw.githubusercontent.com/geohacker/india/master/state/india_telengana.geojson")
        print(f"   Loaded {len(gdf)} states/UTs")
        return gdf
    except Exception as e:
        print(f"⚠️ Could not load shapefile: {e}")
        return None


# ============================================================================
# VISUALIZATION: State-Level Heatmap (Fallback)
# ============================================================================

def create_state_heatmap(state_data, metric, title, output_file, cmap='RdYlGn_r', label=''):
    """Create a state-level heatmap visualization."""
    
    # Sort by metric for better visualization
    state_data = state_data.sort_values(metric, ascending=True).copy()
    
    # Remove states with NaN values
    state_data = state_data.dropna(subset=[metric])
    
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # Color normalization
    vmin = state_data[metric].quantile(0.05)
    vmax = state_data[metric].quantile(0.95)
    
    if vmin < 0 and vmax > 0:
        # Diverging colormap centered at 0
        norm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)
        cmap = 'RdYlGn'
    else:
        norm = plt.Normalize(vmin=vmin, vmax=vmax)
    
    colors = plt.cm.get_cmap(cmap)(norm(state_data[metric]))
    
    # Horizontal bar chart (like a simplified map)
    bars = ax.barh(state_data['state'], state_data[metric], color=colors, edgecolor='white', linewidth=0.5)
    
    # Add value labels
    for bar, val in zip(bars, state_data[metric]):
        width = bar.get_width()
        if pd.notna(val):
            ax.annotate(f'{val:.2f}',
                       xy=(width, bar.get_y() + bar.get_height()/2),
                       xytext=(3, 0), textcoords='offset points',
                       ha='left', va='center', fontsize=8, color='#333')
    
    # Add zero line for child attention gap
    if vmin < 0 and vmax > 0:
        ax.axvline(x=0, color='black', linestyle='-', linewidth=1.5, alpha=0.7)
    
    # Styling
    ax.set_xlabel(label if label else metric.replace('_', ' ').title(), fontsize=12, fontweight='bold')
    ax.set_ylabel('')
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    
    # Add colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.6, aspect=30, pad=0.02)
    cbar.set_label(label if label else metric.replace('_', ' ').title(), fontsize=10)
    
    # Remove spines
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


def create_choropleth_map(gdf, state_data, metric, title, output_file, cmap='RdYlGn_r', label=''):
    """Create a geographic choropleth map of India."""
    if gdf is None:
        return None
    
    # Merge GeoDataFrame with UIDAI data
    gdf['state_normalized'] = gdf['NAME_1'].str.upper().str.strip()
    merged = gdf.merge(state_data, on='state_normalized', how='left')
    
    fig, ax = plt.subplots(figsize=(14, 16))
    
    # Color normalization
    vmin = merged[metric].quantile(0.05)
    vmax = merged[metric].quantile(0.95)
    
    if vmin < 0 and vmax > 0:
        # Diverging colormap centered at 0
        norm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)
        cmap = 'RdYlGn'
    else:
        norm = plt.Normalize(vmin=vmin, vmax=vmax)
    
    # Plot choropleth
    merged.plot(column=metric, cmap=cmap, norm=norm, linewidth=0.5, 
                edgecolor='#333', ax=ax, missing_kwds={'color': 'lightgray'})
    
    # Remove axes
    ax.set_axis_off()
    
    # Title
    ax.set_title(title, fontsize=18, fontweight='bold', pad=20)
    
    # Colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.6, aspect=30, pad=0.02)
    cbar.set_label(label if label else metric.replace('_', ' ').title(), fontsize=12)
    
    plt.tight_layout()
    
    # Save
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, output_file)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"   ✅ Saved: {output_path}")
    return output_path


def create_bubble_map(state_data, output_file):
    """Create a bubble map showing update intensity and child attention gap together."""
    
    # Remove rows with NaN
    data = state_data.dropna(subset=['total_intensity', 'child_attention_gap']).copy()
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Normalize bubble sizes
    sizes = (data['total_updates'] - data['total_updates'].min()) / (data['total_updates'].max() - data['total_updates'].min())
    sizes = 100 + sizes * 500  # Scale to reasonable bubble sizes
    
    # Color by child attention gap
    colors = data['child_attention_gap']
    
    scatter = ax.scatter(data['total_intensity'], 
                        data['child_attention_gap'], 
                        s=sizes, 
                        c=colors, 
                        cmap='RdYlGn_r',
                        alpha=0.7,
                        edgecolors='white',
                        linewidths=1)
    
    # Add state labels for top 10 by volume
    top_states = data.nlargest(15, 'total_updates')
    for _, row in top_states.iterrows():
        ax.annotate(row['state'][:10], 
                   (row['total_intensity'], row['child_attention_gap']),
                   fontsize=8, alpha=0.8,
                   xytext=(5, 5), textcoords='offset points')
    
    # Add reference lines
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5, linewidth=1)
    
    # Styling
    ax.set_xlabel('Update Intensity (mean)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Child Attention Gap', fontsize=12, fontweight='bold')
    ax.set_title('State Performance Matrix\nSize = Total Updates | Color = Child Attention Gap', 
                fontsize=14, fontweight='bold', pad=20)
    
    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax, shrink=0.6, aspect=30)
    cbar.set_label('Child Attention Gap', fontsize=10)
    
    # Legend for bubble size
    handles = [
        plt.scatter([], [], s=100, c='gray', alpha=0.5, label='Low Volume'),
        plt.scatter([], [], s=300, c='gray', alpha=0.5, label='Medium Volume'),
        plt.scatter([], [], s=500, c='gray', alpha=0.5, label='High Volume'),
    ]
    ax.legend(handles=handles, title='Update Volume', loc='upper right', framealpha=0.9)
    
    # Remove top and right spines
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
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 60)
    print("🗺️  UIDAI GEOSPATIAL ANALYSIS")
    print("    Creating India State-Level Visualizations")
    print("=" * 60)
    
    # Load data
    df, state_data = load_uidai_data()
    
    # Load shapefile (if available)
    gdf = load_india_shapefile() if HAS_GEOPANDAS else None
    
    print("\n" + "=" * 60)
    print("📊 CREATING VISUALIZATIONS")
    print("=" * 60)
    
    # 1. Update Intensity Map
    print("\n1️⃣ Creating Update Intensity Map...")
    create_state_heatmap(
        state_data, 
        metric='total_intensity',
        title='📊 Update Intensity by State\nUIDAI Data Hackathon 2026',
        output_file='01_update_intensity_map.png',
        cmap='YlOrRd',
        label='Update Intensity (Updates per 1000 Enrolments)'
    )
    
    # 2. Child Attention Gap Map
    print("\n2️⃣ Creating Child Attention Gap Map...")
    create_state_heatmap(
        state_data, 
        metric='child_attention_gap',
        title='⚠️ Child Attention Gap by State\nNegative = Children Under-Served | Positive = Over-Served',
        output_file='02_child_gap_map.png',
        cmap='RdYlGn',
        label='Child Attention Gap (Update Share - Enrolment Share)'
    )
    
    # 3. State Performance Matrix (Bubble Chart)
    print("\n3️⃣ Creating State Performance Matrix...")
    create_bubble_map(state_data, '03_state_performance_matrix.png')
    
    # If shapefile available, create geographic choropleth
    if gdf is not None:
        print("\n4️⃣ Creating Geographic Choropleth...")
        create_choropleth_map(
            gdf, state_data,
            metric='child_attention_gap',
            title='🗺️ Child Attention Gap Across India\nUIDAI Data Hackathon 2026',
            output_file='04_india_choropleth.png',
            cmap='RdYlGn',
            label='Child Attention Gap'
        )
    
    print("\n" + "=" * 60)
    print("✅ GEOSPATIAL ANALYSIS COMPLETE")
    print(f"   Output directory: {OUTPUT_DIR}")
    print("=" * 60)
    
    # Print summary stats
    print("\n📈 KEY STATE-LEVEL INSIGHTS:")
    
    # Worst child attention gaps
    worst_gaps = state_data.nsmallest(5, 'child_attention_gap')[['state', 'child_attention_gap']]
    print("\n   🔴 Worst Child Attention Gaps (Need Priority):")
    for _, row in worst_gaps.iterrows():
        print(f"      {row['state']}: {row['child_attention_gap']:.3f}")
    
    # Highest update intensity
    highest_intensity = state_data.nlargest(5, 'total_intensity')[['state', 'total_intensity']]
    print("\n   🟢 Highest Update Intensity:")
    for _, row in highest_intensity.iterrows():
        print(f"      {row['state']}: {row['total_intensity']:.2f}")


if __name__ == "__main__":
    main()
