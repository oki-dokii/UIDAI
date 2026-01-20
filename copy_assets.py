import os
import shutil

# Target Directory
DEST_DIR = "dashboard/assets/curated_plots"
os.makedirs(DEST_DIR, exist_ok=True)

# Source Files (Strict List)
files_to_copy = [
    "outputs/actionable_insights/01_worst_child_gaps.png",
    "outputs/actionable_insights/02_child_gap_trend.png",
    "outputs/aadhaar_plots_final/group_a_baseline/01_pareto_lorenz.png",
    "outputs/aadhaar_plots_final/group_a_baseline/02_biometric_demographic_correlation.png",
    "outputs/aadhaar_plots_final/group_a_baseline/03_composition_over_time.png",
    "outputs/aadhaar_plots_final/group_b_spatial/04_top_intensity_districts.png",
    "outputs/aadhaar_plots_final/group_b_spatial/05_bottom_intensity_districts.png",
    "outputs/aadhaar_plots_final/group_b_spatial/06_state_week_heatmap.png",
    "outputs/analysis_output/plots/enhanced_plots/modified_01_national_timeseries_FIXED.png",
    "outputs/analysis_output/plots/enhanced_plots/modified_03_district_intensity_CONSISTENT.png",
    "outputs/analysis_output/plots/enhanced_plots/modified_08_age_disaggregated_ENHANCED.png",
    "outputs/biometric_analysis/plots/05_concentration.png",
    "outputs/biometric_analysis/plots/06_clusters.png",
    "outputs/biometric_analysis/plots/07_top_districts.png",
    "outputs/biometric_analysis/plots/13_weekend_weekday_comparison.png",
    "outputs/demographic_analysis/plots_final/core_10_top_districts_minor.png",
    "outputs/demographic_analysis/plots_final/core_11_volatile_districts.png",
    "outputs/demographic_analysis/plots_final/high_impact_03_weekend_gini_scatter.png",
    "outputs/demographic_analysis/plots_final/high_impact_05_mom_growth_heatmap.png",
    "outputs/demographic_analysis/plots_final/high_impact_06_lorenz_curves.png",
    "outputs/demographic_analysis/plots_final/high_impact_07_spike_detection.png",
    "outputs/demographic_analysis/plots_final/core_02_monthly_minor_share.png",
    "outputs/demographic_analysis/plots_final/core_03_state_month_heatmap.png",
    "outputs/enrolment_analysis/plots_final/core_07_top_districts_child_share.png",
    "outputs/enrolment_analysis/plots_final/core_08_volatility.png",
    "outputs/enrolment_analysis/plots_final/high_impact_11_child_share_acceleration.png",
    "outputs/enrolment_analysis/plots_final/high_impact_10_gini_child_share.png",
    "outputs/enrolment_analysis/plots_final/high_impact_13_campaign_intensity.png",
    "outputs/enrolment_analysis/plots_final/high_impact_14_cohort_trajectories.png",
    "outputs/geospatial_plots/02_child_gap_map.png",
    "outputs/geospatial_plots/08_seasonal_patterns.png",
    "outputs/geospatial_plots/10_lorenz_curve_inequality.png",
    "outputs/geospatial_plots/11_gini_coefficient_analysis.png",
    "outputs/geospatial_plots/12_within_state_heterogeneity.png",
    "outputs/forecast_final/new_analyses/01_decline_vs_volume_scatter.png",
    "outputs/forecast_final/new_analyses/02_state_decline_summary.png",
    "outputs/forecast_final/new_analyses/03_enrolment_update_correlation.png",
    "outputs/integrated_analysis/plots_final/core_01_demo_vs_bio_monthly.png",
    "outputs/integrated_analysis/plots_final/core_08_demo_intensity_heatmap.png",
    "outputs/integrated_analysis/plots_final/core_06_minor_share_scatter.png",
    "outputs/integrated_analysis/plots_final/core_07_district_clusters.png",
    "outputs/plots_final/01_system_shift_ratio.png",
    "outputs/plots_final/02_invisible_economy_weekend_patterns.png",
    "outputs/plots_final/04_healthcare_deserts_infant_gaps.png",
    "outputs/plots_final/bonus_child_attention_gap.png"
]

copied_count = 0
errors = []

print(f"Starting copy of {len(files_to_copy)} files...")

for src in files_to_copy:
    # Handle filename extraction
    filename = os.path.basename(src)
    dest = os.path.join(DEST_DIR, filename)
    
    try:
        if os.path.exists(src):
            shutil.copy2(src, dest)
            copied_count += 1
            # print(f"Copied: {filename}")
        else:
            errors.append(f"MISSING: {src}")
    except Exception as e:
        errors.append(f"ERROR copying {src}: {str(e)}")

print(f"Finished. Successfully copied: {copied_count}/{len(files_to_copy)}")
if errors:
    print("Errors encounterd:")
    for err in errors:
        print(err)
