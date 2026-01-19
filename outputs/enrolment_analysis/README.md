# 🆕 Enrolment Analysis

## Deep Dive into New Aadhaar Enrolment Patterns

This analysis explores **4.4 million new Aadhaar enrolments** across India, revealing who is getting enrolled for the first time, their age profile, and where gaps exist.

---

## 📊 Key Findings at a Glance

| Metric | Value |
|--------|-------|
| **Total New Enrolments** | 4,433,039 |
| **Infant (0-5) Enrolments** | 2,965,831 (**66.9%**) |
| **School-age (5-17)** | 1,354,766 (30.6%) |
| **Adult (18+)** | 112,442 (**Only 2.5%**) |
| **States Analyzed** | 43 |
| **Districts Analyzed** | 980 |
| **Low-Enrolment Districts** | 90 (bottom 10%) |

---

## 🎯 Unique Insights

### 1. New Enrolments are Almost Entirely Children

> **97.5% of all new Aadhaar enrolments are children (0-17 years)**

This is the most striking finding across all three datasets:

| Dataset | Child/Minor Share |
|---------|-------------------|
| **Enrolment** | **97.5%** |
| Biometric Updates | 49.1% |
| Demographic Updates | 9.7% |

**Interpretation**: Adult Aadhaar saturation is near-complete. New enrolments are almost exclusively:
- Newborns being enrolled at birth
- School children being enrolled at admission
- Previously unenrolled minors

### 2. Infant Enrolment is Accelerating

Monthly infant (0-5) share trending upward:

| Month | 0-5 Share | 5-17 Share |
|-------|-----------|------------|
| March | 35.5% | 47.0% |
| June | 53.2% | 40.5% |
| September | 67.0% | 32.0% |
| December | **73.5%** | 24.7% |

**Interpretation**: Infant enrolment is increasingly dominant, suggesting strong hospital/birth-registration linkage.

### 3. 895 of 897 Districts are Child-Heavy
- Almost all districts have child-to-adult ratio > 1.5
- Only **1 district** is adult-heavy
- **Interpretation**: Aadhaar has achieved near-universal adult coverage

### 4. Weekend Drop in Enrolments
- **-33.7% fewer enrolments on weekends**
- Tuesday is the peak day (72,007 avg)
- Sunday is lowest (33,214 avg)
- **Interpretation**: Enrolments are primarily through schools/hospitals (closed on weekends)

### 5. 90 Low-Enrolment Districts Identified
- Bottom 10% districts with persistently low enrolments
- May indicate geographic barriers, limited centre density, or awareness issues
- **Action**: Targeted mobile enrolment drives needed

---

## 📁 Output Files

| File | Description |
|------|-------------|
| `district_clusters.csv` | District segmentation with cluster labels |
| `anomalies.csv` | Records with z-score > 3 (539 spikes) |
| `concentration_metrics.csv` | Gini coefficient by state |
| `volatility_metrics.csv` | CV and stability scores per district |
| `kpis.csv` | Dashboard-ready KPI summary |

---

## 📈 Visualizations

### 1. National Time Series (`01_national_timeseries.png`)
- Daily enrolment trends
- Age composition stacked (0-5, 5-17, 18+)
- Monthly totals
- Age share evolution over months

### 2. State Heatmaps (`02_state_heatmaps.png`)
- State × Month enrolment volume
- State × Month child share (0-17)

### 3. Age Analysis (`03_age_analysis.png`)
- Top 15 states by infant (0-5) share
- Top 15 states by volume
- Distribution of child-to-adult ratio
- Volume vs Child Share scatter

### 4. Temporal Patterns (`04_temporal_patterns.png`)
- Day-of-week patterns (Tuesday peak)
- Weekend vs Weekday comparison
- Monthly enrolments by age band (stacked)
- Age share evolution

### 5. Concentration (`05_concentration.png`)
- Pincode concentration (Gini) by state
- High Gini = enrolments concentrated in few areas

### 6. Clusters (`06_clusters.png`)
- 2D scatter of district clusters
- Cluster size distribution

### 7. Top Districts (`07_top_districts.png`)
- Top 25 districts by enrolment volume
- Top 25 districts by child share

### 8. Volatility (`08_volatility.png`)
- Most volatile districts
- Volatility distribution

---

## 🔧 How to Regenerate

```bash
cd /path/to/UIDAI
python3 enrolment_deep_analysis.py
```

**Dependencies**: `pandas`, `numpy`, `matplotlib`, `seaborn`, `scikit-learn`

---

## 🔍 Complete Cross-Dataset Comparison

| Metric | Biometric | Demographic | Enrolment |
|--------|-----------|-------------|-----------|
| **Total Volume** | 69.8M | 47.3M | 4.4M |
| **Minor/Child Share** | 49.1% | 9.7% | **97.5%** |
| **Weekend Effect** | -30.5% | +68.8% | -33.7% |
| **Peak Day** | Tuesday | Saturday | Tuesday |
| **Driver** | Mixed | Personal | **Institutional** |
| **Primary Use Case** | Fingerprint/Iris refresh | Address/Name changes | **New registrations** |

---

## 🎯 Recommendations for UIDAI

1. **Birth Registration Integration**: Continue strengthening hospital-based newborn enrolment
2. **School Enrollment Drives**: Leverage school admissions for 5-17 age group
3. **Target 90 Low-Enrolment Districts**: Deploy mobile enrolment camps
4. **Adult Outreach is Complete**: Focus resources on child enrolment infrastructure
5. **Monitor Infant Trend**: Ensure 0-5 enrolment continues growing

---

## 📊 5 Behavioral Clusters

| Cluster | Profile | Districts | Recommended Action |
|---------|---------|-----------|-------------------|
| 0 | High-Vol, Child-Heavy, Stable | 521 | Maintain current operations |
| 1 | High-Vol, Child-Heavy, Volatile | 91 | Investigate volatility causes |
| 2 | Adult-Heavy (rare) | 1 | Special adult catch-up drive |
| 3 | Low-Vol, Child-Heavy, Volatile | 20 | Stabilize with consistent camps |
| 4 | Low-Vol, Child-Heavy, Stable | 264 | Increase centre capacity |

---

*Generated by UIDAI Data Hackathon 2026 Analysis Pipeline*
