#!/usr/bin/env python3
"""
Generate 4 New High-Impact Analyses for UIDAI Integrated Analysis
Based on Forensic Audit Recommendations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy.stats import pearsonr

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Load data
DATA_DIR = Path('outputs/integrated_analysis')
OUTPUT_DIR = DATA_DIR / 'plots_final'
OUTPUT_DIR.mkdir(exist_ok=True)

print("Loading data...")
df = pd.read_csv(DATA_DIR / 'integrated_data.csv')
print(f"Data loaded: {len(df)} rows")

# ============================================================================
# NEW ANALYSIS 1: Update Intensity Growth Rate (State × Month)
# ============================================================================
print("\n" + "="*70)
print("Generating Analysis 1: Update Intensity Growth Rate...")
print("="*70)

# Calculate state-month total intensity
state_month = df.groupby(['state', 'month'])['total_intensity'].sum().reset_index()
state_month = state_month.sort_values(['state', 'month'])

# Calculate growth rate
state_month['growth_rate'] = state_month.groupby('state')['total_intensity'].pct_change() * 100

# Pivot for heatmap
pivot_growth = state_month.pivot(index='state', columns='month', values='growth_rate')

# Select top 20 states by total intensity for readability
top_states_total = df.groupby('state')['total_intensity'].sum().nlargest(20).index
pivot_growth = pivot_growth.loc[pivot_growth.index.intersection(top_states_total)]

# Create heatmap
fig, ax = plt.subplots(figsize=(14, 10))
sns.heatmap(pivot_growth, cmap='RdYlGn', center=0, annot=False, 
            cbar_kws={'label': 'Month-over-Month Growth Rate (%)'}, 
            vmin=-100, vmax=100, ax=ax)
ax.set_xlabel('Month', fontsize=12, fontweight='bold')
ax.set_ylabel('State', fontsize=12, fontweight='bold')
ax.set_title('Update Intensity Growth Rate: State × Month\n(Green = Acceleration, Red = Deceleration)', 
             fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'new_01_intensity_growth_rate.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: new_01_intensity_growth_rate.png")

# ============================================================================
# NEW ANALYSIS 2: Demographic-Biometric Update Coupling Coefficient
# ============================================================================
print("\n" + "="*70)
print("Generating Analysis 2: Demographic-Biometric Coupling Coefficient...")
print("="*70)

# Calculate correlation by district
def calculate_coupling(group):
    if len(group) < 3:  # Need at least 3 points for meaningful correlation
        return np.nan
    demo = group['demo_intensity'].values
    bio = group['bio_intensity'].values
    if np.std(demo) == 0 or np.std(bio) == 0:
        return np.nan
    corr, _ = pearsonr(demo, bio)
    return corr

district_coupling = df.groupby('district').apply(calculate_coupling).reset_index()
district_coupling.columns = ['district', 'coupling_coefficient']
district_coupling = district_coupling.dropna()

# Classify districts
district_coupling['coupling_category'] = pd.cut(
    district_coupling['coupling_coefficient'],
    bins=[-1, 0.3, 0.7, 1],
    labels=['Low Coupling (< 0.3)', 'Medium Coupling (0.3-0.7)', 'High Coupling (> 0.7)']
)

# Create visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Histogram
ax1.hist(district_coupling['coupling_coefficient'], bins=40, 
         color='#2E86AB', alpha=0.7, edgecolor='black')
ax1.axvline(district_coupling['coupling_coefficient'].median(), 
            color='#E63946', linewidth=2.5, linestyle='--', 
            label=f"Median: {district_coupling['coupling_coefficient'].median():.3f}")
ax1.axvline(district_coupling['coupling_coefficient'].mean(), 
            color='#2A9D8F', linewidth=2.5, linestyle='--', 
            label=f"Mean: {district_coupling['coupling_coefficient'].mean():.3f}")
ax1.set_xlabel('Coupling Coefficient (ρ)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Number of Districts', fontsize=12, fontweight='bold')
ax1.set_title('Distribution of Demo-Bio Coupling Coefficients', 
              fontsize=13, fontweight='bold')
ax1.legend(fontsize=10, frameon=True, shadow=True)
ax1.grid(True, alpha=0.3, axis='y')

# Category breakdown
category_counts = district_coupling['coupling_category'].value_counts()
colors_pie = ['#D62828', '#F77F00', '#52B788']
ax2.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%',
        colors=colors_pie, startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
ax2.set_title('District Classification by Coupling Strength', 
              fontsize=13, fontweight='bold')

plt.suptitle('Demographic-Biometric Update Coupling Analysis\n(High ρ = Synchronized campaigns, Low ρ = Decoupled processes)', 
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'new_02_demo_bio_coupling.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: new_02_demo_bio_coupling.png")

# ============================================================================
# NEW ANALYSIS 3: Child Attention Gap × Update Intensity Quadrant Plot
# ============================================================================
print("\n" + "="*70)
print("Generating Analysis 3: Gap-Intensity Quadrant Analysis...")
print("="*70)

# Aggregate to district level
district_metrics = df.groupby('district').agg({
    'child_attention_gap': 'mean',
    'total_intensity': 'mean'
}).dropna()

# Calculate quadrant boundaries (using medians)
gap_threshold = district_metrics['child_attention_gap'].median()
intensity_threshold = district_metrics['total_intensity'].median()

# Classify into quadrants
def classify_quadrant(row):
    gap = row['child_attention_gap']
    intensity = row['total_intensity']
    
    if intensity >= intensity_threshold and gap >= gap_threshold:
        return 'Q1: High-Intensity + Child-Balanced'
    elif intensity >= intensity_threshold and gap < gap_threshold:
        return 'Q2: High-Intensity + Child-Underserved'
    elif intensity < intensity_threshold and gap < gap_threshold:
        return 'Q3: Low-Intensity + Child-Underserved'
    else:
        return 'Q4: Low-Intensity + Child-Balanced'

district_metrics['quadrant'] = district_metrics.apply(classify_quadrant, axis=1)

# Create scatter plot
fig, ax = plt.subplots(figsize=(14, 10))

quadrant_colors = {
    'Q1: High-Intensity + Child-Balanced': '#52B788',
    'Q2: High-Intensity + Child-Underserved': '#E63946',
    'Q3: Low-Intensity + Child-Underserved': '#F77F00',
    'Q4: Low-Intensity + Child-Balanced': '#457B9D'
}

for quadrant, color in quadrant_colors.items():
    mask = district_metrics['quadrant'] == quadrant
    ax.scatter(district_metrics.loc[mask, 'child_attention_gap'],
               np.log10(district_metrics.loc[mask, 'total_intensity'] + 1),
               label=f"{quadrant} (n={mask.sum()})",
               color=color, alpha=0.6, s=60, edgecolors='black', linewidth=0.5)

# Add quadrant lines
ax.axvline(gap_threshold, color='black', linewidth=2, linestyle='--', alpha=0.7)
ax.axhline(np.log10(intensity_threshold + 1), color='black', linewidth=2, linestyle='--', alpha=0.7)

# Annotate quadrants
ax.text(0.2, np.log10(intensity_threshold + 1) + 1, 'Q1: Equity Success', 
        fontsize=11, fontweight='bold', ha='center', 
        bbox=dict(boxstyle='round', facecolor='#52B788', alpha=0.3))
ax.text(-0.2, np.log10(intensity_threshold + 1) + 1, 'Q2: Policy Failure', 
        fontsize=11, fontweight='bold', ha='center',
        bbox=dict(boxstyle='round', facecolor='#E63946', alpha=0.3))
ax.text(-0.2, np.log10(intensity_threshold + 1) - 1, 'Q3: Resource Scarcity', 
        fontsize=11, fontweight='bold', ha='center',
        bbox=dict(boxstyle='round', facecolor='#F77F00', alpha=0.3))
ax.text(0.2, np.log10(intensity_threshold + 1) - 1, 'Q4: Low-Need Equilibrium', 
        fontsize=11, fontweight='bold', ha='center',
        bbox=dict(boxstyle='round', facecolor='#457B9D', alpha=0.3))

ax.set_xlabel('Child Attention Gap\n(Negative = Children Underserved)', 
              fontsize=12, fontweight='bold')
ax.set_ylabel('Log₁₀(Total Update Intensity)', fontsize=12, fontweight='bold')
ax.set_title('Child Attention Gap × Update Intensity Quadrant Analysis\n(Q2 = Most Actionable: High resources but child exclusion)', 
             fontsize=14, fontweight='bold', pad=15)
ax.legend(fontsize=9, frameon=True, shadow=True, loc='lower left')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'new_03_gap_intensity_quadrants.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: new_03_gap_intensity_quadrants.png")

# ============================================================================
# NEW ANALYSIS 4: Temporal Stability Index
# ============================================================================
print("\n" + "="*70)
print("Generating Analysis 4: Temporal Stability Index...")
print("="*70)

# Calculate CV for each state
state_stability = df.groupby('state')['total_intensity'].agg(['mean', 'std']).reset_index()
state_stability['cv'] = state_stability['std'] / state_stability['mean']
state_stability = state_stability.dropna()
state_stability = state_stability[state_stability['mean'] > 0]

# Classify stability
state_stability['stability_category'] = pd.cut(
    state_stability['cv'],
    bins=[0, 0.3, 0.8, np.inf],
    labels=['Stable (CV < 0.3)', 'Moderate (CV 0.3-0.8)', 'Volatile (CV > 0.8)']
)

# Sort by CV
state_stability = state_stability.sort_values('cv', ascending=True)

# Select top 25 states for readability
top_25_states = state_stability.head(25)

# Create bar chart
fig, ax = plt.subplots(figsize=(12, 10))

colors = ['#52B788' if cv < 0.3 else '#F77F00' if cv < 0.8 else '#E63946' 
          for cv in top_25_states['cv']]

bars = ax.barh(range(len(top_25_states)), top_25_states['cv'], color=colors, alpha=0.8)
ax.set_yticks(range(len(top_25_states)))
ax.set_yticklabels(top_25_states['state'])
ax.set_xlabel('Coefficient of Variation (CV)', fontsize=12, fontweight='bold')
ax.set_ylabel('State', fontsize=12, fontweight='bold')
ax.set_title('Temporal Stability Index by State\n(Low CV = Stable operations, High CV = Campaign-driven episodic systems)', 
             fontsize=14, fontweight='bold', pad=15)

# Add threshold lines
ax.axvline(0.3, color='#52B788', linewidth=2, linestyle='--', alpha=0.7, label='Stable threshold (0.3)')
ax.axvline(0.8, color='#E63946', linewidth=2, linestyle='--', alpha=0.7, label='Volatile threshold (0.8)')

ax.legend(fontsize=10, frameon=True, shadow=True)
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'new_04_temporal_stability_index.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: new_04_temporal_stability_index.png")

# Print summary statistics
print("\n" + "="*70)
print("SUMMARY STATISTICS")
print("="*70)
print(f"\nAnalysis 1 - Growth Rate:")
print(f"  Average monthly growth: {state_month['growth_rate'].mean():.2f}%")
print(f"  Max growth observed: {state_month['growth_rate'].max():.2f}%")
print(f"  Max decline observed: {state_month['growth_rate'].min():.2f}%")

print(f"\nAnalysis 2 - Coupling Coefficient:")
print(f"  Mean coupling: {district_coupling['coupling_coefficient'].mean():.3f}")
print(f"  Districts with high coupling (ρ > 0.7): {(district_coupling['coupling_coefficient'] > 0.7).sum()}")
print(f"  Districts with low coupling (ρ < 0.3): {(district_coupling['coupling_coefficient'] < 0.3).sum()}")

print(f"\nAnalysis 3 - Quadrant Distribution:")
for quadrant in district_metrics['quadrant'].value_counts().index:
    count = (district_metrics['quadrant'] == quadrant).sum()
    pct = count / len(district_metrics) * 100
    print(f"  {quadrant}: {count} districts ({pct:.1f}%)")

print(f"\nAnalysis 4 - Stability:")
print(f"  Stable states (CV < 0.3): {(state_stability['cv'] < 0.3).sum()}")
print(f"  Moderate states (CV 0.3-0.8): {((state_stability['cv'] >= 0.3) & (state_stability['cv'] < 0.8)).sum()}")
print(f"  Volatile states (CV > 0.8): {(state_stability['cv'] >= 0.8).sum()}")

print("\n" + "="*70)
print("✓ All 4 new high-impact analyses generated successfully!")
print(f"✓ Output directory: {OUTPUT_DIR}")
print("="*70)
