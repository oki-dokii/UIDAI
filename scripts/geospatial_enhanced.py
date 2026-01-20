#!/usr/bin/env python3
"""
UIDAI ENHANCED GEOSPATIAL ANALYSIS
Addresses all audit findings with:
- Data quality annotations
- Confidence intervals
- Interpretation warnings
- Enhanced visualizations
"""

import os
import sys
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from matplotlib.patches import Patch, Rectangle
from scipy import stats

# Import data quality validator
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
from data_quality_validator import validate_state_data

warnings.filterwarnings('ignore')

# Try importing geopandas
try:
    import geopandas as gpd
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False
    print("⚠️  geopandas not available. Using fallback visualizations.")

# ============================================================================
# CONFIGURATION
# ============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_FILE = os.path.join(BASE_DIR, "outputs", "integrated_analysis", "integrated_data.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "geospatial_plots")

# Visualization settings
FIGURE_DPI = 300
COLOR_PALETTE = {
    'diverging': 'RdYlGn',
    'sequential': 'YlOrRd',
    'quality_issue': 'lightgray'
}

# ============================================================================
# DATA LOADING WITH QUALITY VALIDATION
# ============================================================================

def load_and_validate_data():
    """Load UIDAI data and perform quality validation."""
    print(f"📂 Loading data from: {DATA_FILE}")
    
    if not os.path.exists(DATA_FILE):
        print(f"❌ Data file not found: {DATA_FILE}")
        sys.exit(1)
    
    df = pd.read_csv(DATA_FILE)
    print(f"   Loaded {len(df):,} records")
    
    # Aggregate to state level
    state_agg = df.groupby('state').agg({
        'total_enrol': 'sum',
        'total_updates': 'sum',
        'total_intensity': 'mean',
        'child_attention_gap': 'mean',
        'demo_intensity': 'mean',
        'bio_intensity': 'mean'
    }).reset_index()
    
    # Perform quality validation
    print("\n🔍 Performing data quality validation...")
    state_annotated, quality_report = validate_state_data(state_agg)
    
    print(f"   Mean Quality Score: {quality_report['mean_quality_score']:.1f}/100")
    print(f"   Records with Issues: {quality_report['records_below_80']}/{len(state_annotated)}")
    
    # Save quality report
    report_path = os.path.join(OUTPUT_DIR, "data_quality_report.txt")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(report_path, 'w') as f:
        f.write("UIDAI GEOSPATIAL DATA QUALITY REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total Records: {quality_report['total_records']}\n")
        f.write(f"Mean Quality Score: {quality_report['mean_quality_score']:.1f}/100\n")
        f.write(f"Records Below 80: {quality_report['records_below_80']}\n\n")
        f.write("SUSPICIOUS VALUE DETECTION:\n")
        f.write("-" * 60 + "\n")
        for col, stats in quality_report['details'].items():
            if isinstance(stats, dict) and 'flagged_total' in stats:
                f.write(f"\n{col}:\n")
                f.write(f"  Flagged: {stats['flagged_total']} ({stats['flagged_percentage']:.1f}%)\n")
                f.write(f"  Round Numbers: {stats['round_numbers']}\n")
                f.write(f"  Outliers: {stats['outliers']}\n")
    
    print(f"   ✅ Quality report saved: {report_path}")
    
    return df, state_annotated, quality_report


# ============================================================================
# ENHANCED VISUALIZATION: Update Intensity with Quality Annotations
# ============================================================================

def create_enhanced_intensity_map(state_data, quality_report, output_file):
    """
    Create update intensity map with data quality annotations.
    Addresses Audit Finding: Ambiguous interpretation & missing data quality transparency
    """
    # Sort by metric
    data = state_data.sort_values('total_intensity', ascending=True).copy()
    data = data.dropna(subset=['total_intensity'])
    
    fig, ax = plt.subplots(figsize=(15, 13))
    
    # Color normalization
    vmin = data['total_intensity'].quantile(0.05)
    vmax = data['total_intensity'].quantile(0.95)
    norm = plt.Normalize(vmin=vmin, vmax=vmax)
    
    # Create colors - use gray for suspicious values
    colors = []
    for idx, row in data.iterrows():
        if row.get('total_intensity_suspicious', False):
            colors.append(COLOR_PALETTE['quality_issue'])
        else:
            colors.append(plt.cm.get_cmap(COLOR_PALETTE['sequential'])(norm(row['total_intensity'])))
    
    # Horizontal bar chart
    bars = ax.barh(data['state'], data['total_intensity'], color=colors, 
                   edgecolor='white', linewidth=0.5)
    
    # Add hatching for suspicious values
    for bar, (idx, row) in zip(bars, data.iterrows()):
        if row.get('total_intensity_suspicious', False):
            bar.set_hatch('///')
            bar.set_edgecolor('red')
            bar.set_linewidth(1.5)
    
    # Add value labels with quality indicators
    for bar, (idx, row) in zip(bars, data.iterrows()):
        width = bar.get_width()
        if pd.notna(row['total_intensity']):
            quality_marker = " ⚠️" if row.get('total_intensity_suspicious', False) else ""
            ax.annotate(f'{row["total_intensity"]:.2f}{quality_marker}',
                       xy=(width, bar.get_y() + bar.get_height()/2),
                       xytext=(3, 0), textcoords='offset points',
                       ha='left', va='center', fontsize=8, 
                       color='red' if row.get('total_intensity_suspicious', False) else '#333')
    
    # Styling
    ax.set_xlabel('Update Intensity (Updates per 1000 Enrollments)', 
                 fontsize=12, fontweight='bold')
    ax.set_ylabel('')
    ax.set_title('📊 Update Intensity by State (Quality-Annotated)\\n' +
                'UIDAI Data Hackathon 2026',
                fontsize=16, fontweight='bold', pad=20)
    
    # Add interpretation warning box
    warning_text = ("⚠️ INTERPRETATION CAUTION:\\n" +
                   "High intensity may indicate routine corrections OR expansion activity.\\n" +
                   "Values marked with ⚠️ are flagged for data quality concerns.\\n" +
                   "Hatched bars indicate suspiciously round numbers (likely placeholders).")
    ax.text(0.98, 0.02, warning_text, transform=ax.transAxes,
           fontsize=9, verticalalignment='bottom', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8, edgecolor='orange', linewidth=2),
           color='#8B4513', fontweight='bold')
    
    # Colorbar
    sm = plt.cm.ScalarMappable(cmap=COLOR_PALETTE['sequential'], norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.6, aspect=30, pad=0.02)
    cbar.set_label('Update Intensity', fontsize=10)
    
    # Custom legend for data quality
    legend_elements = [
        Patch(facecolor=COLOR_PALETTE['quality_issue'], edgecolor='red', 
              hatch='///', linewidth=1.5, label='Data Quality Concern'),
        Patch(facecolor='orange', edgecolor='white', label='Valid Data')
    ]
    ax.legend(handles=legend_elements, loc='lower right', framealpha=0.9, fontsize=9)
    
    # Remove spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    # Save
    output_path = os.path.join(OUTPUT_DIR, output_file)
    plt.savefig(output_path, dpi=FIGURE_DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"   ✅ Saved: {output_path}")
    return output_path


# ============================================================================
# ENHANCED VISUALIZATION: Child Gap with Confidence Intervals
# ============================================================================

def create_enhanced_child_gap_map(state_data, quality_report, output_file):
    """
    Create child attention gap map with confidence intervals.
    Addresses Audit Finding: Missing confidence intervals
    """
    # Extract CI data
    ci_data = pd.DataFrame(quality_report['gap_confidence_intervals'])
    
    # Merge with state data
    data = state_data.merge(ci_data, left_on='state', right_on='state', how='left')
    data = data.sort_values('child_attention_gap', ascending=True).dropna(subset=['child_attention_gap'])
    
    fig, ax = plt.subplots(figsize=(15, 13))
    
    # Color normalization (diverging centered at 0)
    vmin = data['child_attention_gap'].min()
    vmax = data['child_attention_gap'].max()
    norm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)
    colors = plt.cm.get_cmap(COLOR_PALETTE['diverging'])(norm(data['child_attention_gap']))
    
    # Horizontal bar chart
    bars = ax.barh(data['state'], data['child_attention_gap'], color=colors, 
                   edgecolor='white', linewidth=0.5)
    
    # Add confidence interval error bars
    if 'child_attention_gap_ci_lower' in data.columns:
        xerr_lower = data['child_attention_gap'] - data['child_attention_gap_ci_lower']
        xerr_upper = data['child_attention_gap_ci_upper'] - data['child_attention_gap']
        
        ax.errorbar(data['child_attention_gap'], 
                   range(len(data)),
                   xerr=[xerr_lower, xerr_upper],
                   fmt='none', ecolor='black', elinewidth=1, capsize=3, alpha=0.6)
    
    # Add value labels
    for idx, (_, row) in enumerate(data.iterrows()):
        val = row['child_attention_gap']
        ci_lower = row.get('child_attention_gap_ci_lower', np.nan)
        ci_upper = row.get('child_attention_gap_ci_upper', np.nan)
        
        label_text = f'{val:.3f}'
        if pd.notna(ci_lower) and pd.notna(ci_upper):
            label_text += f'\\n[{ci_lower:.3f}, {ci_upper:.3f}]'
        
        ax.annotate(label_text,
                   xy=(val, idx),
                   xytext=(5 if val >= 0 else -5, 0), textcoords='offset points',
                   ha='left' if val >= 0 else 'right', va='center', 
                   fontsize=7, color='#333')
    
    # Add zero reference line
    ax.axvline(x=0, color='black', linestyle='-', linewidth=2, alpha=0.7, zorder=0)
    
    # Styling
    ax.set_xlabel('Child Attention Gap (Update Share - Enrollment Share)', 
                 fontsize=12, fontweight='bold')
    ax.set_ylabel('')
    ax.set_title('⚠️ Child Attention Gap by State (with 95% CI)\\n' +
                'Negative = Children Under-Served | Positive = Over-Served',
                fontsize=16, fontweight='bold', pad=20)
    
    # Add interpretation notes
    note_text = ("📊 Confidence Intervals (95%):\\n" +
                "Shown as error bars and brackets.\\n" +
                "Negative values indicate minors participate below population proportion.")
    ax.text(0.02, 0.98, note_text, transform=ax.transAxes,
           fontsize=9, verticalalignment='top', horizontalalignment='left',
           bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7),
           color='#00008B')
    
    # Colorbar
    sm = plt.cm.ScalarMappable(cmap=COLOR_PALETTE['diverging'], norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.6, aspect=30, pad=0.02)
    cbar.set_label('Child Attention Gap', fontsize=10)
    
    # Remove spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    # Save
    output_path = os.path.join(OUTPUT_DIR, output_file)
    plt.savefig(output_path, dpi=FIGURE_DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"   ✅ Saved: {output_path}")
    return output_path


# ============================================================================
# ENHANCED VISUALIZATION: Performance Matrix with Interpretation Warning
# ============================================================================

def create_enhanced_performance_matrix(state_data, output_file):
    """
    Create state performance matrix with interpretation warnings.
    Addresses Audit Finding: Need for interpretation guardrails
    """
    data = state_data.dropna(subset=['total_intensity', 'child_attention_gap']).copy()
    
    fig, ax = plt.subplots(figsize=(15, 11))
    
    # Normalize bubble sizes
    sizes = (data['total_updates'] - data['total_updates'].min()) / \
            (data['total_updates'].max() - data['total_updates'].min())
    sizes = 150 + sizes * 600
    
    # Color by child attention gap
    scatter = ax.scatter(data['total_intensity'], 
                        data['child_attention_gap'], 
                        s=sizes, 
                        c=data['child_attention_gap'], 
                        cmap=COLOR_PALETTE['diverging'],
                        norm=mcolors.TwoSlopeNorm(vmin=data['child_attention_gap'].min(),
                                                  vcenter=0,
                                                  vmax=data['child_attention_gap'].max()),
                        alpha=0.7,
                        edgecolors='white',
                        linewidths=1.5)
    
    # Add reference lines
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.6, linewidth=1.5, label='Zero Gap')
    median_intensity = data['total_intensity'].median()
    ax.axvline(x=median_intensity, color='gray', linestyle=':', alpha=0.6, 
              linewidth=1.5, label=f'Median Intensity ({median_intensity:.1f})')
    
    # Label top states by volume
    top_states = data.nlargest(15, 'total_updates')
    for _, row in top_states.iterrows():
        ax.annotate(row['state'][:12], 
                   ( row['total_intensity'], row['child_attention_gap']),
                   fontsize=8, alpha=0.9, fontweight='bold',
                   xytext=(5, 5), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3))
    
    # Styling
    ax.set_xlabel('Update Intensity (mean)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Child Attention Gap', fontsize=13, fontweight='bold')
    ax.set_title('State Performance Matrix\\n' +
                'Size = Total Updates | Color = Child Attention Gap', 
                fontsize=15, fontweight='bold', pad=20)
    
    # Critical interpretation warning
    warning_box = ("⚠️⚠️ CRITICAL INTERPRETATION WARNING ⚠️⚠️\\n\\n" +
                  "1. Bubble Size (Volume) ≠ Performance Quality\\n" +
                  "   Large volume may reflect population size, not efficiency.\\n\\n" +
                  "2. Update Intensity requires demographic controls\\n" +
                  "   Raw intensity does NOT measure coverage or effectiveness.\\n\\n" +
                  "3. This plot describes system behavior ONLY\\n" +
                  "   No causal or policy conclusions without further analysis.")
    ax.text(0.98, 0.02, warning_box, transform=ax.transAxes,
           fontsize=9, verticalalignment='bottom', horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='#FFE4E1', alpha=0.95, 
                    edgecolor='darkred', linewidth=2.5),
           color='darkred', fontweight='bold', family='monospace')
    
    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax, shrink=0.7, aspect=30, pad=0.02)
    cbar.set_label('Child Attention Gap', fontsize=11, fontweight='bold')
    
    # Legend for bubble size
    legend_sizes = [
        (100 + 150, 'Low Volume'),
        (350 + 150, 'Medium Volume'),
        (600 + 150, 'High Volume')
    ]
    legend_handles = [plt.scatter([], [], s=s, c='gray', alpha=0.5, edgecolors='white', 
                                 linewidths=1, label=label) 
                     for s, label in legend_sizes]
    
    leg1 = ax.legend(handles=legend_handles, title='Update Volume', 
                    loc='upper left', framealpha=0.9, fontsize=9)
    ax.add_artist(leg1)
    
    # Add reference line legend
    ax.legend(loc='upper right', framealpha=0.9, fontsize=9)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Grid
    ax.grid(True, alpha=0.2, linestyle='--')
    
    plt.tight_layout()
    
    # Save
    output_path = os.path.join(OUTPUT_DIR, output_file)
    plt.savefig(output_path, dpi=FIGURE_DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"   ✅ Saved: {output_path}")
    return output_path


# ============================================================================
# GEOGRAPHIC CHOROPLETH (if available)
# ============================================================================

def load_india_shapefile():
    """Load India state boundaries."""
    if not HAS_GEOPANDAS:
        return None
    
    try:
        print("📥 Loading India state boundaries...")
        gdf = gpd.read_file("https://raw.githubusercontent.com/geohacker/india/master/state/india_telengana.geojson")
        print(f"   Loaded {len(gdf)} states/UTs")
        return gdf
    except Exception as e:
        print(f"⚠️ Could not load shapefile: {e}")
        return None


def create_enhanced_choropleth(gdf, state_data, output_file):
    """Create enhanced India choropleth with data quality indicators."""
    if gdf is None:
        return None
    
    # Merge data
    gdf['state_normalized'] = gdf['NAME_1'].str.upper().str.strip()
    state_data['state_normalized'] = state_data['state'].str.upper().str.strip()
    merged = gdf.merge(state_data, on='state_normalized', how='left')
    
    fig, ax = plt.subplots(figsize=(14, 16))
    
    # Color normalization (diverging)
    vmin = merged['child_attention_gap'].quantile(0.05)
    vmax = merged['child_attention_gap'].quantile(0.95)
    norm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)
    
    # Plot choropleth
    merged.plot(column='child_attention_gap', cmap=COLOR_PALETTE['diverging'], 
               norm=norm, linewidth=0.8, edgecolor='#333', ax=ax, 
               missing_kwds={'color': 'lightgray', 'label': 'No Data'})
    
    # Add hatching for states with data quality concerns
    if 'quality_score' in merged.columns:
        low_quality = merged[merged['quality_score'] < 80]
        if not low_quality.empty:
            low_quality.plot(ax=ax, facecolor='none', edgecolor='red', 
                           linewidth=2, linestyle='--', alpha=0.7)
    
    # Remove axes
    ax.set_axis_off()
    
    # Title
    ax.set_title('🗺️ Child Attention Gap Across India\\n' +
                'UIDAI Data Hackathon 2026 (Quality-Annotated)',
                fontsize=18, fontweight='bold', pad=20)
    
    # Colorbar
    sm = plt.cm.ScalarMappable(cmap=COLOR_PALETTE['diverging'], norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.6, aspect=30, pad=0.02)
    cbar.set_label('Child Attention Gap', fontsize=12, fontweight='bold')
    
    # Legend
    legend_elements = [
        Patch(facecolor='lightgray', edgecolor='black', label='No Data'),
        Patch(facecolor='none', edgecolor='red', linestyle='--', linewidth=2, label='Data Quality Concern')
    ]
    ax.legend(handles=legend_elements, loc='lower left', framealpha=0.95, fontsize=10)
    
    plt.tight_layout()
    
    # Save
    output_path = os.path.join(OUTPUT_DIR, output_file)
    plt.savefig(output_path, dpi=FIGURE_DPI, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"   ✅ Saved: {output_path}")
    return output_path


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 70)
    print("🗺️  UIDAI ENHANCED GEOSPATIAL ANALYSIS")
    print("    Audit-Compliant Visualizations with Quality Annotations")
    print("=" * 70)
    
    # Load and validate data
    df, state_data, quality_report = load_and_validate_data()
    
    print("\\n" + "=" * 70)
    print("📊 CREATING ENHANCED VISUALIZATIONS")
    print("=" * 70)
    
    # 1. Enhanced Update Intensity Map (FIXED VERSION)
    print("\\n1️⃣ Creating Enhanced Update Intensity Map (Quality-Annotated)...")
    create_enhanced_intensity_map(
        state_data, 
        quality_report,
        '01_update_intensity_map_enhanced.png'
    )
    
    # 2. Enhanced Child Attention Gap Map (with CIs)
    print("\\n2️⃣ Creating Enhanced Child Attention Gap Map (with Confidence Intervals)...")
    create_enhanced_child_gap_map(
        state_data,
        quality_report,
        '02_child_gap_map_enhanced.png'
    )
    
    # 3. Enhanced State Performance Matrix (with warnings)
    print("\\n3️⃣ Creating Enhanced State Performance Matrix (with Interpretation Warnings)...")
    create_enhanced_performance_matrix(
        state_data,
        '03_state_performance_matrix_enhanced.png'
    )
    
    # 4. Enhanced Geographic Choropleth (if available)
    gdf = load_india_shapefile() if HAS_GEOPANDAS else None
    if gdf is not None:
        print("\\n4️⃣ Creating Enhanced Geographic Choropleth...")
        create_enhanced_choropleth(
            gdf,
            state_data,
            '04_india_choropleth_enhanced.png'
        )
    
    print("\\n" + "=" * 70)
    print("✅ ENHANCED GEOSPATIAL ANALYSIS COMPLETE")
    print(f"   Output directory: {OUTPUT_DIR}")
    print("=" * 70)
    
    print("\\n📈 AUDIT COMPLIANCE SUMMARY:")
    print("   ✅ Data quality annotations added")
    print("   ✅ Confidence intervals displayed")
    print("   ✅ Interpretation warnings included")
    print("   ✅ Suspicious values clearly marked")
    print(f"   ✅ Quality report generated")


if __name__ == "__main__":
    main()
