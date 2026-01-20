#!/usr/bin/env python3
"""
Generate 9 Core Visualizations for UIDAI Integrated Analysis
Based on Forensic Audit Recommendations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.cluster import KMeans

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Load data
DATA_DIR = Path('outputs/integrated_analysis')
OUTPUT_DIR = DATA_DIR / 'plots_final'
OUTPUT_DIR.mkdir(exist_ok=True)

print("Loading data...")
df = pd.read_csv(DATA_DIR / 'integrated_data.csv')
state_summary = pd.read_csv(DATA_DIR / 'state_summary.csv')

# Clean state names
major_states = [
    'Uttar Pradesh', 'Bihar', 'Madhya Pradesh', 'West Bengal', 'Maharashtra',
    'Rajasthan', 'Gujarat', 'Assam', 'Karnataka', 'Tamil Nadu'
]
state_summary = state_summary[state_summary['state'].isin(major_states + [
    'Jharkhand', 'Telangana', 'Andhra Pradesh', 'Odisha', 'Meghalaya',
    'Chhattisgarh', 'Haryana', 'Delhi', 'Punjab', 'Kerala', 'Jammu And Kashmir',
    'Uttarakhand', 'Himachal Pradesh', 'Nagaland', 'Manipur', 'Tripura',
    'Mizoram', 'Arunachal Pradesh', 'Puducherry', 'Chandigarh', 'Goa', 'Sikkim'
])]

print(f"Data loaded: {len(df)} rows, {df['state'].nunique()} states, {df['district'].nunique()} districts")

# ============================================================================
# PLOT 1.4: Demographic vs Biometric Updates (Monthly)
# ============================================================================
print("\nGenerating Plot 1.4: Demographic vs Biometric Updates (Monthly)...")

monthly_data = df.groupby('month').agg({
    'total_demo': 'sum',
    'total_bio': 'sum',
    'total_enrol': 'sum'
}).reset_index()

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(monthly_data['month'], monthly_data['total_demo'], 
        marker='o', linewidth=2.5, label='Demographic Updates', color='#2E86AB')
ax.plot(monthly_data['month'], monthly_data['total_bio'], 
        marker='s', linewidth=2.5, label='Biometric Updates', color='#A23B72')
ax.set_xlabel('Month', fontsize=12, fontweight='bold')
ax.set_ylabel('Update Volume', fontsize=12, fontweight='bold')
ax.set_title('Demographic vs Biometric Updates: Monthly Trends', 
             fontsize=14, fontweight='bold', pad=15)
ax.legend(fontsize=11, frameon=True, shadow=True)
ax.grid(True, alpha=0.3)
ax.ticklabel_format(style='plain', axis='y')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'core_01_demo_vs_bio_monthly.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: core_01_demo_vs_bio_monthly.png")

# ============================================================================
# PLOT 2.2: Top 10 States: Update Intensity
# ============================================================================
print("\nGenerating Plot 2.2: Top 10 States Update Intensity...")

top10_states = state_summary.nlargest(10, 'total_intensity')

fig, ax = plt.subplots(figsize=(12, 7))
x = np.arange(len(top10_states))
width = 0.35

bars1 = ax.bar(x - width/2, top10_states['demo_intensity']/1e13, width, 
               label='Demographic Intensity', color='#06A77D', alpha=0.8)
bars2 = ax.bar(x + width/2, top10_states['bio_intensity']/1e13, width, 
               label='Biometric Intensity', color='#F15152', alpha=0.8)

ax.set_xlabel('State', fontsize=12, fontweight='bold')
ax.set_ylabel('Update Intensity (×10¹³)', fontsize=12, fontweight='bold')
ax.set_title('Top 10 States: Update Intensity Comparison', 
             fontsize=14, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(top10_states['state'], rotation=45, ha='right')
ax.legend(fontsize=11, frameon=True, shadow=True)
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'core_02_state_intensity.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: core_02_state_intensity.png")

# ============================================================================
# PLOT 2.3: Child Attention Gap by State
# ============================================================================
print("\nGenerating Plot 2.3: Child Attention Gap by State...")

top10_gap = state_summary.nlargest(10, 'total_intensity')

fig, ax = plt.subplots(figsize=(12, 7))
colors = ['#D62828' if gap < 0 else '#52B788' for gap in top10_gap['child_attention_gap']]
bars = ax.barh(range(len(top10_gap)), top10_gap['child_attention_gap'], color=colors, alpha=0.8)

ax.set_xlabel('Child Attention Gap', fontsize=12, fontweight='bold')
ax.set_ylabel('State', fontsize=12, fontweight='bold')
ax.set_title('Child Attention Gap by State\n(Negative = Children Underserved)', 
             fontsize=14, fontweight='bold', pad=15)
ax.set_yticks(range(len(top10_gap)))
ax.set_yticklabels(top10_gap['state'])
ax.axvline(0, color='black', linewidth=1.5, linestyle='--', alpha=0.7)
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'core_03_child_gap_state.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: core_03_child_gap_state.png")

# ============================================================================
# PLOT 4.1: Distribution of Child Attention Gap
# ============================================================================
print("\nGenerating Plot 4.1: Distribution of Child Attention Gap...")

# District-level child gap
district_gaps = df.groupby('district')['child_attention_gap'].mean().dropna()

fig, ax = plt.subplots(figsize=(12, 6))
n, bins, patches = ax.hist(district_gaps, bins=50, color='#457B9D', alpha=0.7, edgecolor='black')

# Add statistics
median_gap = district_gaps.median()
mean_gap = district_gaps.mean()
q1 = district_gaps.quantile(0.25)
q3 = district_gaps.quantile(0.75)

ax.axvline(median_gap, color='#E63946', linewidth=2.5, linestyle='--', label=f'Median: {median_gap:.3f}')
ax.axvline(mean_gap, color='#2A9D8F', linewidth=2.5, linestyle='--', label=f'Mean: {mean_gap:.3f}')
ax.axvline(q1, color='#F77F00', linewidth=1.5, linestyle=':', label=f'Q1: {q1:.3f}')
ax.axvline(q3, color='#F77F00', linewidth=1.5, linestyle=':', label=f'Q3: {q3:.3f}')

ax.set_xlabel('Child Attention Gap', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Districts', fontsize=12, fontweight='bold')
ax.set_title('Distribution of Child Attention Gap Across Districts', 
             fontsize=14, fontweight='bold', pad=15)
ax.legend(fontsize=10, frameon=True, shadow=True)
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'core_04_gap_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: core_04_gap_distribution.png")

# ============================================================================
# PLOT 4.2: Child Share: Enrolment vs Updates
# ============================================================================
print("\nGenerating Plot 4.2: Child Share Enrolment vs Updates...")

district_child = df.groupby('district').agg({
    'child_share_enrol': 'mean',
    'child_share_updates': 'mean'
}).dropna()

fig, ax = plt.subplots(figsize=(10, 10))
ax.scatter(district_child['child_share_enrol'], 
           district_child['child_share_updates'],
           alpha=0.5, s=50, color='#6A4C93', edgecolors='black', linewidth=0.5)

# Add parity line
max_val = max(district_child['child_share_enrol'].max(), 
              district_child['child_share_updates'].max())
ax.plot([0, max_val], [0, max_val], 'r--', linewidth=2.5, 
        label='Parity Line (Equal Shares)', alpha=0.8)

ax.set_xlabel('Child Share in Enrolment', fontsize=12, fontweight='bold')
ax.set_ylabel('Child Share in Updates', fontsize=12, fontweight='bold')
ax.set_title('Child Share: Enrolment vs Updates\n(Below parity = Children underserved in updates)', 
             fontsize=14, fontweight='bold', pad=15)
ax.legend(fontsize=11, frameon=True, shadow=True)
ax.grid(True, alpha=0.3)
ax.set_xlim(0, max_val * 1.05)
ax.set_ylim(0, max_val * 1.05)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'core_05_child_share_scatter.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: core_05_child_share_scatter.png")

# ============================================================================
# PLOT 4.3: Minor Share: Demographic vs Biometric
# ============================================================================
print("\nGenerating Plot 4.3: Minor Share Demographic vs Biometric...")

district_minor = df.groupby('district').agg({
    'demo_minor_share': 'mean',
    'bio_minor_share': 'mean'
}).replace([np.inf, -np.inf], np.nan).dropna()

fig, ax = plt.subplots(figsize=(10, 10))
ax.scatter(district_minor['demo_minor_share'], 
           district_minor['bio_minor_share'],
           alpha=0.5, s=50, color='#BC6C25', edgecolors='black', linewidth=0.5)

# Add parity line
max_val = max(district_minor['demo_minor_share'].max(), 
              district_minor['bio_minor_share'].max())
ax.plot([0, max_val], [0, max_val], 'r--', linewidth=2.5, 
        label='Parity Line', alpha=0.8)

ax.set_xlabel('Minor Share in Demographic Updates', fontsize=12, fontweight='bold')
ax.set_ylabel('Minor Share in Biometric Updates', fontsize=12, fontweight='bold')
ax.set_title('Minor Share: Demographic vs Biometric Updates\n(Below parity = Minors underrepresented in biometric)', 
             fontsize=14, fontweight='bold', pad=15)
ax.legend(fontsize=11, frameon=True, shadow=True)
ax.grid(True, alpha=0.3)
ax.set_xlim(0, max_val * 1.05)
ax.set_ylim(0, max_val * 1.05)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'core_06_minor_share_scatter.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: core_06_minor_share_scatter.png")

# ============================================================================
# PLOT 5.1: District Clusters: Enrolment vs Update Intensity
# ============================================================================
print("\nGenerating Plot 5.1: District Clusters...")

district_summary = df.groupby('district').agg({
    'total_enrol': 'sum',
    'total_intensity': 'mean'
}).reset_index()

# Remove extreme outliers for better visualization
district_summary = district_summary[
    (district_summary['total_enrol'] > 0) & 
    (district_summary['total_intensity'] > 0)
]

# K-means clustering
X = np.log1p(district_summary[['total_enrol', 'total_intensity']].values)
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
district_summary['cluster'] = kmeans.fit_predict(X)

fig, ax = plt.subplots(figsize=(12, 8))
scatter = ax.scatter(np.log10(district_summary['total_enrol'] + 1), 
                     np.log10(district_summary['total_intensity'] + 1),
                     c=district_summary['cluster'], 
                     cmap='viridis', s=60, alpha=0.6, edgecolors='black', linewidth=0.5)

ax.set_xlabel('Log₁₀(Enrolment)', fontsize=12, fontweight='bold')
ax.set_ylabel('Log₁₀(Update Intensity)', fontsize=12, fontweight='bold')
ax.set_title('District Clusters: Enrolment vs Update Intensity', 
             fontsize=14, fontweight='bold', pad=15)
plt.colorbar(scatter, label='Cluster', ax=ax)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'core_07_district_clusters.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: core_07_district_clusters.png")

# ============================================================================
# PLOT 6.1: Demographic Update Intensity Heatmap (State × Month)
# ============================================================================
print("\nGenerating Plot 6.1: Demographic Intensity Heatmap...")

# Aggregate to state-month level
state_month_demo = df.groupby(['state', 'month'])['demo_intensity'].sum().reset_index()
pivot_demo = state_month_demo.pivot(index='state', columns='month', values='demo_intensity')

# Select top 20 states by total intensity for readability
top_states = pivot_demo.sum(axis=1).nlargest(20).index
pivot_demo = pivot_demo.loc[top_states]

fig, ax = plt.subplots(figsize=(14, 10))
sns.heatmap(pivot_demo / 1e13, cmap='YlOrRd', annot=False, fmt='.1f', 
            cbar_kws={'label': 'Demographic Intensity (×10¹³)'}, ax=ax)
ax.set_xlabel('Month', fontsize=12, fontweight='bold')
ax.set_ylabel('State', fontsize=12, fontweight='bold')
ax.set_title('Demographic Update Intensity: State × Month', 
             fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'core_08_demo_intensity_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: core_08_demo_intensity_heatmap.png")

# ============================================================================
# PLOT 6.2: Biometric Update Intensity Heatmap (State × Month)
# ============================================================================
print("\nGenerating Plot 6.2: Biometric Intensity Heatmap...")

state_month_bio = df.groupby(['state', 'month'])['bio_intensity'].sum().reset_index()
pivot_bio = state_month_bio.pivot(index='state', columns='month', values='bio_intensity')

# Select same top 20 states
pivot_bio = pivot_bio.loc[top_states]

fig, ax = plt.subplots(figsize=(14, 10))
sns.heatmap(pivot_bio / 1e13, cmap='YlGnBu', annot=False, fmt='.1f', 
            cbar_kws={'label': 'Biometric Intensity (×10¹³)'}, ax=ax)
ax.set_xlabel('Month', fontsize=12, fontweight='bold')
ax.set_ylabel('State', fontsize=12, fontweight='bold')
ax.set_title('Biometric Update Intensity: State × Month', 
             fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'core_09_bio_intensity_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: core_09_bio_intensity_heatmap.png")

print("\n" + "="*70)
print("✓ All 9 core visualizations generated successfully!")
print(f"✓ Output directory: {OUTPUT_DIR}")
print("="*70)
