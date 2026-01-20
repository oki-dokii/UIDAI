# Visualization Quality Checklist

## Pre-Publication Validation

Use this checklist before finalizing any visualization for the UIDAI analysis suite.

---

## ✅ Data Normalization Requirements

### Raw Counts vs. Normalized Metrics

- [ ] **Raw counts are PROHIBITED** unless:
  - Explicitly justified in caption
  - Accompanied by per-capita or intensity metrics
  - Used only for context, not primary comparison

- [ ] **State/district comparisons MUST use**:
  - Per-capita rates
  - Intensity metrics (normalized by population or enrolment base)
  - Percentage shares or ratios

- [ ] **Temporal trends MUST specify**:
  - Absolute vs. relative change
  - Growth rates vs. levels
  - Baseline period for index calculations

### When Normalization is Not Required

✓ **Acceptable raw count scenarios:**
- National-level aggregates (total enrolments across all states)
- Within-entity time series (single state's monthly trend)
- Distribution visualizations (histograms of district-level metrics)

---

## 📊 Visualization Type Standards

### Heatmaps

- [ ] Color scale range matches data range (not arbitrary 0-1)
- [ ] Diverging colormaps only when zero is meaningful
- [ ] No excessive numerical overlays (max 20% of cells)
- [ ] Consistent scaling across related heatmaps

### Scatterplots

- [ ] Reference lines added where applicable:
  - Parity lines (y = x) for compositional comparisons
  - Median lines for quadrant analysis
  - Threshold lines for policy benchmarks
- [ ] Overplotting addressed via:
  - Transparency (alpha < 0.7)
  - Jitter for discrete values
  - Density contours for large datasets
- [ ] Axes scaled to data range (not arbitrary limits)

### Histograms

- [ ] Summary statistics annotated:
  - Median (primary measure for skewed distributions)
  - Mean (if distribution is approximately normal)
  - IQR or percentiles (Q1, Q3)
- [ ] Bin width justified (not default)
- [ ] Y-axis labeled as count or density

### Bar Charts

- [ ] Bars ordered logically:
  - Ranked by value (for comparisons)
  - Temporal sequence (for trends)
  - Alphabetical only if no other ordering applies
- [ ] Error bars or confidence intervals where appropriate
- [ ] Baseline at zero unless ratio/index metric

---

## 🎨 Visual Design Standards

### Color Usage

- [ ] Colorblind-safe palettes (avoid red-green combinations)
- [ ] Consistent color mapping across related plots
- [ ] Sufficient contrast between categories (minimum 3:1 ratio)
- [ ] Semantic color use:
  - Red = negative/decline/problem
  - Green = positive/growth/success
  - Blue/gray = neutral

### Typography

- [ ] All axes labeled with units
- [ ] Font size readable at publication scale (minimum 10pt)
- [ ] Consistent font family across suite
- [ ] Bold for emphasis only on titles/section headers

### Layout

- [ ] Adequate white space (margins ≥ 5% of plot area)
- [ ] Legend positioned to not obscure data
- [ ] Gridlines subtle (alpha ≤ 0.3)
- [ ] Aspect ratio appropriate to data structure:
  - Square for x-y correlations
  - Wide for time series
  - Tall for ranked lists

---

## 📝 Annotation Requirements

### Titles

- [ ] Descriptive and self-contained
- [ ] No jargon without definition
- [ ] Includes temporal scope if time-bound
- [ ] Subtitle clarifies interpretation where needed

### Captions (External to Plot)

- [ ] States primary signal extracted
- [ ] Identifies caveats or limitations
- [ ] Avoids causal language (see Interpretation Guardrails)
- [ ] Cites data source and date range

### In-Plot Text

- [ ] Minimized (prefer legend/caption)
- [ ] Only for critical context (e.g., policy change markers)
- [ ] Positioned to not obscure data

---

## 🚫 Anti-Pattern Detection

### Prohibited Practices

- [ ] **Stacked bar charts for compositional time series** → Use stacked area or separate lines
- [ ] **Dual y-axes with >10x scale difference** → Create separate plots
- [ ] **3D charts** → Always use 2D alternatives
- [ ] **Pie charts with >5 slices** → Use bar chart
- [ ] **Arbitrary category thresholds** → Justify cutoffs or use continuous metrics

### Regression-to-Mean Traps

- [ ] Avoid comparing "top N" and "bottom N" without acknowledging selection bias
- [ ] Do not interpret extreme values without checking if they're outliers or measurement errors

---

## 📐 Statistical Rigor

### Distributions

- [ ] Outliers identified and justified (include or exclude with reason)
- [ ] Skewness acknowledged (median vs. mean choice)
- [ ] Sample size stated when n < 30

### Correlations

- [ ] Pearson r only for linear relationships
- [ ] Spearman ρ for monotonic non-linear
- [ ] Scatterplot accompanies correlation coefficient
- [ ] Causality never implied from correlation

### Aggregations

- [ ] Aggregation level stated (district/state/national)
- [ ] Weighting scheme disclosed if applicable
- [ ] Missing data handling documented

---

## 🔍 Cross-Validation Checks

Before finalizing the suite:

1. **Consistency**: Do related plots tell the same story?
2. **Completeness**: Are all findings from one plot reconcilable with others?
3. **Redundancy**: Can any plot be removed without information loss?
4. **Accessibility**: Can a non-expert understand the main message?

---

## Sign-Off

- [ ] All checklist items verified
- [ ] Peer review completed
- [ ] Aligned with Interpretation Guardrails
- [ ] Captions match Analytical Narrative

**Reviewer Name**: ___________________  
**Date**: ___________________  
**Approved for Publication**: ☐ Yes ☐ No (revisions needed)
