# UIDAI Data Hackathon 2026 - Enhanced Slide Deck Structure

## Presentation Guidelines
- **10 slides maximum** (one insight per slide)
- **Large visuals, minimal text**
- Lead with geospatial map (wow factor)
- Close with forecast (forward-looking)

---

## Slide 1: Title & Hook
**Title**: Unlocking Societal Trends in Aadhaar Data

**Hook Stat** (massive font):
> "For every 1 new Aadhaar, there are 22 updates"

**Visual**: India choropleth map (background, faded)

**Content**:
- Team name
- "124M+ Records Analyzed | 1,038 Districts | Actionable Insights"

---

## Slide 2: The Child Attention Gap 🚨

**Visual**: `/geospatial_plots/02_child_gap_map.png`

**Headline**: "Children are 97% of enrolments but only 30% of updates"

**Key Stat**: National average gap: **-0.228**

**Callout**: 20 districts need IMMEDIATE intervention

---

## Slide 3: Geographic Hotspots

**Visual**: `/geospatial_plots/04_india_choropleth.png`

**Headline**: "Not All States Are Equal"

**3 bullets (color-coded)**:
- 🔴 Critical: Delhi, West Bengal, Dadra & Nagar Haveli
- 🟠 Severe: 15 states with gap < -0.3
- 🟢 Model: States with positive gap

---

## Slide 4: Top 20 Priority Districts

**Visual**: `/actionable_insights/01_worst_child_gaps.png`

**Headline**: "Specific Targets for Policy Action"

**Table snippet**: Top 5 districts with severity rating

**Callout box**: "Downloadable CSV with all 20 districts"

---

## Slide 5: District Segmentation (Clusters)

**Visual**: `/actionable_insights/03_cluster_profiles.png`

**Headline**: "5 Behavioral Clusters"

| Cluster | Districts | Action |
|---------|-----------|--------|
| 📍 Saturated Urban | 200+ | Maintain infrastructure |
| 🌱 Emerging Growth | 150+ | Update awareness campaigns |
| 🔄 Migration Corridors | 180+ | Flexible service delivery |
| 🏘️ Under-served Rural | 280+ | Mobile camps needed |
| ⭐ High-Performing | 60+ | Best practice models |

---

## Slide 6: The Weekend Paradox

**Visual**: Bar chart showing weekend vs weekday patterns

**Headline**: "When People Actually Update"

| Service | Weekend Effect |
|---------|----------------|
| Enrolments | -34% (institutional) |
| Demographics | +69% (personal choice) |
| Biometrics | -31% (operational) |

**Action**: Extend weekend hours for demographic updates

---

## Slide 7: Trend Analysis

**Visual**: `/actionable_insights/02_child_gap_trend.png`

**Headline**: "Is It Getting Better?"

**Insight**: Monthly trend with slope indicator
- Negative trend = situation worsening
- Recommendation based on direction

---

## Slide 8: 6-Month Forecast 📈

**Visual**: `/forecast_plots/04_forecast_summary.png`

**Headline**: "Predictive Analytics for Planning"

**Key Predictions**:
- Enrolment trajectory (with confidence interval)
- Update volume projection
- 134 districts showing >5% monthly decline

**Callout**: "Prophet ML model used for forecasting"

---

## Slide 9: Districts at Risk

**Visual**: `/forecast_plots/03_declining_districts.png`

**Headline**: "20 Districts with Steepest Decline"

**Action**: Pre-emptive resource allocation needed

**Table**: Top 5 declining districts with % decline

---

## Slide 10: Recommendations & KPIs

**No visual** - text focus slide

### Immediate Actions (0-3 months)
| Priority | Action | Target |
|----------|--------|--------|
| 🔴 High | Child update campaigns | 20 districts |
| 🔴 High | Weekend biometric services | States with -30%+ drop |
| 🟠 Medium | Mobile camps | Under-served cluster |

### Monitoring KPIs
1. Update-to-Enrolment Ratio (target: 15-20*)
2. Child Attention Gap (target: > -0.1)
3. Weekend Activity Ratio (target: > 0.7)
4. Under-served District % (target: < 20%)

**Closing statement**: "Data-driven policy for 1.4 billion citizens"

---

## Design Tips

### Do's ✅
- Use UIDAI orange accent (#FF6B00)
- Dark theme for dramatic impact
- Embed actual plot images
- One insight per slide
- Large fonts (minimum 24pt for body)

### Don'ts ❌
- No walls of text
- No methodology slides (save for appendix)
- No more than 3 bullets per slide
- No generic recommendations

---

## Appendix Slides (if time permits)

### A1: Methodology
- Pipeline diagram
- Data sources
- ML techniques

### A2: Data Caveats
- 21.9x ratio based on sample data
- Age bucket misalignment noted
- State normalization applied

### A3: Full District Table
- Sortable CSV available
- All 1,038 districts

---

## Files to Include in PPT

| Slide | Image Path |
|-------|------------|
| 2 | `geospatial_plots/02_child_gap_map.png` |
| 3 | `geospatial_plots/04_india_choropleth.png` |
| 4 | `actionable_insights/01_worst_child_gaps.png` |
| 5 | `actionable_insights/03_cluster_profiles.png` |
| 7 | `actionable_insights/02_child_gap_trend.png` |
| 8 | `forecast_plots/04_forecast_summary.png` |
| 9 | `forecast_plots/03_declining_districts.png` |

---

*Enhanced slide deck structure for UIDAI Data Hackathon 2026*
*Updated: January 19, 2026*
