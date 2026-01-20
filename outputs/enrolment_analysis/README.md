# Forensic Audit: Aadhaar Enrolment Analysis

> [!IMPORTANT]
> **COMPLIANCE STATUS**: ✅ **AUDIT PASSED** (2026-01-20)
> This directory matches the forensic standards established in the UIDAI Analytical Audit.

## 1. Directory Structure

```
outputs/enrolment_analysis/
├── plots_final/                     # [NEW] 14 Forensic-Quality Visualizations
│   ├── core_*.png                   # 8 Refined Core Visualizations
│   └── high_impact_*.png            # 6 New High-Impact Analyses
├── ANALYTICAL_NARRATIVE_ENROLMENT.md # System Characterization & Key Findings
├── INTERPRETATION_GUARDRAILS.md     # Prohibited Interpretations & Scope
├── VISUALIZATION_QUALITY_CHECKLIST.md# Audit Compliance Matrix
└── data/                            # Intermediate CSVs (anomalies, metrics)
```

## 2. Key Forensic Findings

1.  **Institutional Capture**: Enrolment is a school/center-driven process (weekday dominant), unlike the demand-driven update process.
2.  **Child Dominance**: 90%+ of enrolments are children (0-17), confirming the system has shifted to a birth-registry model.
3.  **Infrastructure Trap**: Volatility is a function of scale. Small districts operate in "Camp Mode" (high volatility), large ones in "Center Mode" (stable).
4.  **Inequality Paradox**: High Gini coefficients (inequality) positively correlate with Child Share, suggesting centralized hubs are *better* at capturing children than dispersed networks.

## 3. Visualization Canon

### Core Visualizations (Refined)
*   `core_01_national_trends.png`: Daily/Monthly volume with rolling averages.
*   `core_02_state_heatmaps.png`: Child share heatmap by state/month.
*   `core_03_age_distribution.png`: Bimodal distribution of district child shares.
*   `core_04_temporal_patterns.png`: Weekday vs Weekend (Institutional signal).
*   `core_05_spatial_concentration.png`: Gini coefficient rankings.
*   `core_06_district_clusters.png`: K-means operational clustering.
*   `core_07_top_districts.png`: Saturation leaders (>99% child share).
*   `core_08_volatility.png`: Operational instability rankings.

### High-Impact Analyses (New)
*   `high_impact_09_normalized_intensity.png`: Enrolment per 1,000 population (North-East catch-up).
*   `high_impact_10_gini_child_share.png`: Efficiency of centralization.
*   `high_impact_11_child_share_acceleration.png`: Campaign detection via MoM changes.
*   `high_impact_12_volatility_infrastructure.png`: The scale-stability curve.
*   `high_impact_13_campaign_intensity.png`: Event detection index.
*   `high_impact_14_cohort_trajectories.png`: Absolute volume decline in adults vs stability in children.

## 4. Usage Guidelines
Refer to `INTERPRETATION_GUARDRAILS.md` before citing these numbers.
*   **Do not** cite low enrolment as "exclusion" (likely saturation).
*   **Do not** cite high volatility as "failure" (likely camp mode).
