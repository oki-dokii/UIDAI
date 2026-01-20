# Biometric Analysis Visualization Standards

This document defines methodological standards, data definitions, and quality requirements for all biometric update visualizations.

---

## 1. Age Category Operational Definitions

### Available Age Groups (Source Data)
- **Minor (5-17)**: Children aged 5 years to under 17 years
  - Uses `bio_age_5_17` column from source data
  - Cutoff is based on age at time of biometric update
  - **Inclusion starts at age 5** (school entry age)

- **Adult (17+)**: Individuals aged 17 years and above
  - Uses `bio_age_17_` column from source data  
  - **Note**: Uses 17+ instead of legal majority age (18+), creating 1-year ambiguity for 17-year-olds

### Missing Age Group (CRITICAL LIMITATION)
- **Age 0-5: NOT AVAILABLE IN SOURCE DATA**
  - No `bio_age_0_5` column exists in dataset
  - Early childhood (0-5 years) is completely excluded from all analyses
  - **This is a data limitation, not a visualization choice**
  - All visualizations must explicitly note this absence where relevant

### Implications
- "Minor" in this context means **school-age children (5-17)** only
- Cannot assess biometric update access for early childhood population
- Total age coverage: 5+ years only
- Any references to "child" or "minor" populations exclude infants, toddlers, and preschool children

---

## 2. Minor Share Calculation Formula

### Standard Formula
```
minor_share = bio_age_5_17 / (bio_age_5_17 + bio_age_17_)
            = bio_age_5_17 / total_bio
```

### Critical Specifications

**Denominator**: Total biometric updates including BOTH age groups (5-17 + 17+)
- **0-5 population is excluded from both numerator and denominator**
- This is NOT "children as % of total population"
- This IS "5-17 updates as % of available age group updates"

**Range**: 0.0 to 1.0 (or 0% to 100%)
- 0.50 (50%) means equal number of updates for minors and adults
- **50% has NO normative meaning** (is not inherently "good" or "target")
- Must be benchmarked against population age distribution to assess equity

**Handling Edge Cases**:
- If `total_bio = 0`: Set `minor_share = 0` (avoid division by zero)
- If month has <100 total updates: Filter out (unstable estimate)
- Missing data coded as `NaN`, not zero

**Classification Thresholds** (descriptive only):
- Low minor share: <40%
- Balanced: 40-60%
- High minor share: >60%

---

## 3. Geographic Unit Definitions

### Pincode
- Uses postal code boundaries
- ~19,000 unique pincodes in dataset
- Smallest geographic analysis unit
- Used for concentration metrics (Gini coefficient)

### District
- Administrative district boundaries (as per source data)
- ~1,000 unique districts in dataset
- Primary unit for behavioral analysis and clustering
- Note: District names standardized (Title Case)

### State / Union Territory
- 28 states + Union Territories
- Names standardized using `STATE_FIX` mapping
- Consistent abbreviations used in visualizations:
  ```
  AP  = Andhra Pradesh      MH  = Maharashtra
  AS  = Assam               MP  = Madhya Pradesh
  BR  = Bihar               TN  = Tamil Nadu
  CG  = Chhattisgarh        UP  = Uttar Pradesh
  DL  = Delhi               WB  = West Bengal
  GJ  = Gujarat             JK  = Jammu And Kashmir
  ... (see script for full mapping)
  ```

---

## 4. Temporal Coverage & Data Handling

### Observation Period
- **Primary coverage**: March 1, 2025 - December 31, 2025
- **10 months** of continuous daily data
- Dates parsed as: `DD-MM-YYYY` format

### Temporal Variables
- `day_of_week`: Monday-Sunday (full names)
- `is_weekend`: Boolean (Saturday/Sunday = True)
- `month`: 1-12 (integer)
- `week_of_year`: ISO week number

### Missing Data Handling
- **Zero updates ≠ Missing data**
- True zeros (district had capacity but no updates) are retained
- Missing values coded as `NaN`, NOT zero
- Weekend vs Weekday: Both categories must have data to include district

### Campaign vs Baseline Periods
- March-July 2025: **Active campaign phase** (high volume, 8M+ daily)
- August onward: **Post-campaign residual** (declining volume, <1M daily)
- Visualizations should distinguish these periods where relevant

---

## 5. Statistical Significance Standards

### Required Reporting for All Correlations
```python
# Example
r = 0.45          # Pearson correlation coefficient
R² = 0.20         # R-squared
p = 0.001         # p-value
n = 500           # sample size
CI_95 = [0.38, 0.52]  # 95% confidence interval
```

### Required Reporting for Trends/Regressions
- Slope and intercept
- R² (coefficient of determination)
- p-value for slope
- Residual diagnostics (if claiming linearity)
- Sample size

### Required Reporting for Comparisons
- Test statistic (t, z, F, etc.)
- p-value
- Effect size (Cohen's d, η², etc.)
- Sample sizes for both groups

### Significance Thresholds
- p < 0.05: Statistically significant
- p < 0.01: Highly significant
- p ≥ 0.05: Not significant (must state explicitly)

### Cluster Analysis Requirements
- Algorithm name (e.g., "K-means, k=5, random_state=42")
- K-selection justification (elbow plot, silhouette scores)
- Cluster stability analysis (if claiming robust segments)
- Cluster validation metrics

---

## 6. Color Scale Guidelines

### Prohibited Color Schemes
❌ **DO NOT USE**:
- Red-Yellow-Green (RdYlGn) for non-normative data
  - Green implies "good", red implies "bad"
  - Inappropriate for minor share (neither high nor low is inherently better)
  
- Traffic light colors (red/yellow/green) without justification
- Diverging palettes (e.g., RdBu) for sequential data

### Recommended Color Schemes

**For Sequential Data** (low to high values):
- `viridis` - Perceptually uniform, colorblind-friendly
- `cividis` - Optimized for colorblindness
- `plasma`, `inferno` - High contrast
- `YlOrRd` - Yellow-Orange-Red (acceptable for volume/intensity)

**For Categorical Data**:
- `tab10`, `tab20` - Distinct categorical colors
- `Set2`, `Set3` - Softer categorical palettes

**For Diverging Data** (values with meaningful midpoint):
- Only when comparing to a benchmark (e.g., population average)
- Use `coolwarm`, `bwr`, or custom schemes
- Explicitly label midpoint value

### Heatmap-Specific Rules
- **Annotation limit**: If >100 cells, remove numeric annotations (illegible)
- Use color encoding only for large heatmaps
- Always include colorbar with label
- Consider using `annot_kws={'fontsize': 6}` if annotations essential

---

## 7. Threshold Lines & Reference Values

### The 50% Problem
- **50% minor share has NO inherent normative meaning**
- It is NOT a policy target, performance benchmark, or equity indicator
- Equal distribution (50-50) may indicate under-serving if:
  - 5-17 population comprises >50% of enrolled population, OR
  - 5-17 population has higher legitimate update needs (growing children)

### Acceptable Uses of 50% Line
✅ **IF CONTEXTUALIZED**:
```python
ax.axvline(x=0.5, color='gray', linestyle=':', alpha=0.5, 
           label='50% reference (not a target)')
```

✅ **IF BENCHMARKED**:
```python
# Compare to actual population distribution
population_5_17_share = 0.42  # From Census
ax.axvline(x=population_5_17_share, color='blue', linestyle='--',
           label='Population share (Census)')
ax.axvline(x=0.5, color='gray', linestyle=':', alpha=0.3)
```

❌ **PROHIBITED**:
```python
# Implies 50% is a target
ax.axvline(x=0.5, color='red', linestyle='--', label='Target')

# Using solid red line suggests importance/violation
ax.axvline(x=0.5, color='red', linewidth=2)
```

### General Reference Line Rules
- Use **gray, dotted/dashed, low alpha** for non-normative references
- Always include legend label explaining meaning
- Avoid red/green for non-performance metrics
- If multiple references, distinguish visually

---

## 8. Accessibility & Readability Standards

### Annotations & Labels
- **Minimum font size**: 8pt for annotations, 10pt for axes
- **Contrast ratio**: ≥4.5:1 for normal text, ≥3:1 for large text
- **Log scales**: MUST explicitly state "log scale" in axis label
  ```python
  ax.set_xlabel('Total Updates (log scale)', fontweight='bold')
  ax.set_xscale('log')
  ```

### State/District Abbreviations
- Use **consistent abbreviation scheme** (2-3 letters, see Section 3)
- If space permits, use full names
- Never mix abbreviated and full names in same visualization
- If using abbreviations, provide legend or table

### Title Requirements
- Descriptive, specific (not generic "Analysis")
- Include temporal scope if relevant ("March-December 2025")
- Use title case, bold, fontsize ≥14

### Legend Requirements
- Always include for color/symbol coding
- Position: upper-right unless obstructs data
- Font size ≥10
- Frame: semi-transparent background if over data

---

## 9. Data Limitation Annotations

### Mandatory Annotations

**For Any Age-Related Visualization**:
```python
ax.text(0.98, 0.02,
        'Note: Age 0-5 not included in source data',
        transform=ax.transAxes,
        fontsize=9,
        ha='right',
        va='bottom',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
```

**For Placeholder Visualizations** (using mock data):
```python
ax.text(0.5, 0.05,
        '🚨 PLACEHOLDER VISUALIZATION 🚨\n' +
        'Uses MOCK DATA - requires actual data to complete',
        transform=ax.transAxes,
        fontsize=11,
        ha='center',
        bbox=dict(boxstyle='round', facecolor='yellow', 
                  alpha=0.9, edgecolor='red', linewidth=3))
```

**For Filtered Data**:
- State minimum thresholds (e.g., "Districts with >1000 updates only")
- Note exclusions in subtitle or caption

---

## 10. Export & File Naming Standards

### Resolution
- **Minimum DPI**: 150 for analysis reports
- **Publication DPI**: 300 if submitting to journals/formal reports
- **Format**: PNG (default), PDF (if vector graphics needed)

### File Naming Convention
```
##_descriptive_name.png

Where:
## = Two-digit sequence number (01, 02, ..., 13)
descriptive_name = Lowercase with underscores

Examples:
01_national_timeseries.png
09_age_composition_note.png
12_minor_share_volatility.png
```

### Figure Dimensions
- **Standard**: 14" × 8" (landscape)
- **Tall**: 14" × 12" (for vertical rankings)
- **Wide**: 16" × 8" (for comparison plots)
- **Square**: 12" × 12" (for symmetric matrices)

---

## 11. Interpretation Guardrails

### Claims to AVOID

❌ "System serves minors equitably at 45%"
- Cannot assess equity without population baseline

❌ "Minor share increased from 45% to 55%, showing improved access"
- Compositional increase during volume collapse likely reflects differential dropout

❌ "Northeastern states prioritize children"
- High minor share could reflect demographics, not policy

❌ "50% represents fair distribution"
- No demographic justification for 50% as equity benchmark

❌ "Tuesday is best service day for families"
- Peak may reflect reporting artifacts, not actual service patterns

### Required Qualifications

✅ "45% minor share, **compared to 42% population share (Census)**, suggests slight over-representation"

✅ "Minor share increased while **absolute minor volumes declined**, indicating adult dropout rather than improved child access"

✅ "High minor share in Northeast **may reflect** younger demographics; requires Census benchmarking"

✅ "50% shown **for reference only**; equity requires comparison to enrolled population age structure"

---

## 12. Validation Checklist

Before finalizing any visualization, verify:

**Data Integrity**
- [ ] All calculations produce values in expected ranges (0-1 for shares, positive for counts)
- [ ] No NaN/Inf in final outputs (unless intentional for missing data)
- [ ] Totals sum correctly (minor + adult = total)

**Visual Quality**
- [ ] All text legible at export resolution
- [ ] Color schemes appropriate (no normative red-green)
- [ ] Log scales explicitly annotated
- [ ] Threshold lines contextualized or removed

**Documentation**
- [ ] Title is descriptive and specific
- [ ] All axes labeled with units
- [ ] Legend included for all coding
- [ ] 0-5 absence noted if age-related
- [ ] Data source and date range stated

**Accessibility**
- [ ] Colorblind-friendly palette used
- [ ] Minimum font sizes met
- [ ] Sufficient contrast ratios
- [ ] State abbreviations consistent

**Statistical Rigor**
- [ ] Sample sizes reported
- [ ] Significance levels stated (p-values)
- [ ] Confidence intervals shown where relevant
- [ ] Cluster validation metrics included

---

## 13. Common Errors & Fixes

| Error | Fix |
|-------|-----|
| Heatmap annotations illegible | Remove `annot=True`, use color only |
| Red-green minor share heatmap | Change to `cmap='viridis'` |
| 50% red threshold line | Change to `color='gray', linestyle=':', alpha=0.5, label='reference'` |
| Log scale not annotated | Add "(log scale)" to axis label, bold font |
| Inconsistent state abbreviations | Use standard mapping (Section 3) |
| Missing 0-5 annotation | Add text box noting data limitation |
| Overlapping plot elements | Increase figsize, use `plt.tight_layout()` |
| Unstable estimates from low counts | Filter: districts with <100 or <1000 updates |

---

## 14. Change Log

| Date | Change | Reason |
|------|--------|--------|
| 2026-01-20 | Initial creation | Forensic audit identified need for standards |
| 2026-01-20 | Added 0-5 absence requirements | Critical data limitation must be visible |
| 2026-01-20 | Restricted red-green palettes | Prevent normative misinterpretation |
| 2026-01-20 | Mandated 50% line contextualization | Remove implied target status |

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-20  
**Maintainer**: UIDAI Data Hackathon Team
