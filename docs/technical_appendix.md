# UIDAI Data Hackathon 2026 - Technical Appendix

## Complete Data Dictionary & Methodology

---

## 1. Data Sources

### 1.1 Raw Datasets

| Dataset | Files | Total Records | Columns |
|---------|-------|---------------|---------|
| Enrolment | 3 CSVs | 1,006,029 | `date, state, district, pincode, age_0_5, age_5_17, age_18_greater` |
| Biometric | 4 CSVs | 1,861,108 | `date, state, district, pincode, bio_age_5_17, bio_age_17_` |
| Demographic | 5 CSVs | 2,071,700 | `date, state, district, pincode, demo_age_5_17, demo_age_17_` |

### 1.2 After Aggregation (District-Date Level)

| Dataset | Records |
|---------|---------|
| Enrolment | 65,174 |
| Biometric | 76,803 |
| Demographic | 82,939 |
| **Merged** | **211,539** |

---

## 2. Data Preprocessing Pipeline

### 2.1 Date Parsing
```python
df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
```

### 2.2 State Name Normalization
```python
STATE_MAP = {
    "Andaman & Nicobar Islands": "Andaman And Nicobar Islands",
    "J & K": "Jammu And Kashmir",
    "Telengana": "Telangana",
    "Orissa": "Odisha",
    # ... additional mappings
}
df['state'] = df['state'].str.strip().str.title().replace(STATE_MAP)
```

### 2.3 Aggregation
- Removed pincode-level granularity
- Aggregated to `state-district-date` level
- Sum of numeric columns per group

### 2.4 Merge Strategy
- Outer join on `['date', 'year', 'month', 'state', 'district']`
- NaN values filled with 0 for numeric columns

---

## 3. Feature Engineering

### 3.1 Base Totals

| Feature | Formula |
|---------|---------|
| `total_enrolments` | `age_0_5 + age_5_17 + age_18_greater` |
| `total_bio_updates` | `bio_age_5_17 + bio_age_17_` |
| `total_demo_updates` | `demo_age_5_17 + demo_age_17_` |
| `total_updates` | `total_bio_updates + total_demo_updates` |

### 3.2 Intensity Ratios

| Feature | Formula | Use Case |
|---------|---------|----------|
| `update_intensity` | `total_updates / total_enrolments` | Overall load indicator |
| `bio_intensity` | `total_bio_updates / total_enrolments` | Biometric demand |
| `demo_intensity` | `total_demo_updates / total_enrolments` | Demographic change |
| `updates_per_1000` | `update_intensity * 1000` | Readable metric |

### 3.3 Composition Metrics

| Feature | Formula |
|---------|---------|
| `bio_share` | `total_bio_updates / total_updates` |
| `demo_share` | `total_demo_updates / total_updates` |
| `young_enrol_share` | `age_0_5 / total_enrolments` |
| `child_enrol_share` | `age_5_17 / total_enrolments` |
| `adult_enrol_share` | `age_18_greater / total_enrolments` |
| `child_update_share` | `(bio_5_17 + demo_5_17) / total_updates` |

### 3.4 Normalization Metrics

| Feature | Formula |
|---------|---------|
| `update_intensity_zscore` | `(intensity - mean) / std` |
| `bio_intensity_zscore` | `(bio_intensity - mean) / std` |
| `demo_intensity_zscore` | `(demo_intensity - mean) / std` |
| `national_percentile` | `rank(intensity) / total * 100` |
| `state_percentile` | `rank within state * 100` |

### 3.5 Temporal Metrics

| Feature | Formula |
|---------|---------|
| `*_mom` | Month-over-month % change |
| `*_roll3` | 3-period rolling average |

### 3.6 Volatility Metrics (District Level)

| Feature | Formula |
|---------|---------|
| `intensity_std` | Std dev of intensity over time |
| `intensity_mean` | Mean intensity over time |
| `cv` | Coefficient of variation |
| `trend_score` | Linear regression slope |

---

## 4. Clustering Methodology

### 4.1 Algorithm: K-Means

```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

features = ['update_intensity', 'bio_share']
X_scaled = StandardScaler().fit_transform(X)
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
clusters = kmeans.fit_predict(X_scaled)
```

### 4.2 Cluster Interpretation

| Cluster | Intensity | Bio Share | Districts |
|---------|-----------|-----------|-----------|
| 0 | Low | Mixed | ~220 |
| 1 | Medium | Low (Demo-heavy) | ~200 |
| 2 | Medium | High (Bio-heavy) | ~230 |
| 3 | High | Mixed | ~240 |

---

## 5. Anomaly Detection

### 5.1 Method: Z-Score Thresholding

```python
threshold = 3  # Standard deviations
anomalies = df[abs(df['update_intensity_zscore']) > threshold]
```

### 5.2 Results
- **Total Anomalies**: 2,383 records
- **High Spikes**: Records with z-score > 3
- **Low Drops**: Records with z-score < -3

---

## 6. Statistical Summary

### 6.1 National Aggregates

| Metric | Value |
|--------|-------|
| Total Enrolments | 5,435,702 |
| Total Updates | 119,058,282 |
| Total Biometric | 69,764,648 (58.6%) |
| Total Demographic | 49,293,634 (41.4%) |
| Avg Update Intensity | 0.1647 |

### 6.2 Correlations

| Pair | Correlation |
|------|-------------|
| Enrolments vs Updates | ~0.85 |
| Biometric vs Demographic | ~0.75 |
| Size vs Intensity | ~0.10 (weak) |

---

## 7. Visualization Catalog

| # | Filename | Description |
|---|----------|-------------|
| 1 | `01_national_timeseries.png` | National trends over time |
| 2 | `02_state_heatmap.png` | State × Time intensity |
| 3 | `03_district_intensity_ranking.png` | Top/Bottom districts |
| 4 | `04_bivariate_analysis.png` | Scatter plots & distributions |
| 5 | `05_cluster_analysis.png` | K-means segmentation |
| 6 | `06_pareto_analysis.png` | Lorenz curve |
| 7 | `07_volatility_analysis.png` | Volatility metrics |
| 8 | `08_age_group_analysis.png` | Age-wise breakdown |
| 9 | `09_state_comparison.png` | Multi-metric state comparison |
| 10 | `10_correlation_matrix.png` | Feature correlations |

---

## 8. Output Files

| File | Records | Description |
|------|---------|-------------|
| `processed_data.csv` | 211,539 | Full merged dataset with features |
| `volatility_metrics.csv` | 1,038 | District-level volatility |
| `district_clusters.csv` | 889 | Cluster assignments |
| `anomalies.csv` | 2,383 | Flagged anomalous records |

---

## 9. Reproducibility Instructions

```bash
# Clone/Navigate to project
cd /path/to/UIDAI

# Install dependencies
pip install pandas numpy matplotlib seaborn scikit-learn

# Run analysis
python uidai_comprehensive_analysis.py

# Outputs saved to:
# - analysis_output/processed_data.csv
# - analysis_output/plots/*.png
```

---

## 10. Limitations & Assumptions

1. **Data Aggregation**: Pincode-level data aggregated to district level
2. **Missing Values**: Filled with 0 (assumed no activity)
3. **State Names**: Normalized using predefined mapping
4. **Clustering**: K=4 chosen for interpretability
5. **Anomaly Threshold**: 3σ standard (may miss subtle anomalies)

---

*Technical Appendix - UIDAI Data Hackathon 2026*
