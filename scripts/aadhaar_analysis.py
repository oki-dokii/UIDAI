
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob

# Configuration - Using relative paths for portability
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)  # Parent directory (UIDAI/)
DATA_DIR = os.path.join(BASE_DIR, "data")
DIRS = {
    "biometric": os.path.join(DATA_DIR, "api_data_aadhar_biometric"),
    "demographic": os.path.join(DATA_DIR, "api_data_aadhar_demographic"),
    "enrolment": os.path.join(DATA_DIR, "api_data_aadhar_enrolment"),
}
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "aadhaar_plots")

def load_data(directory, dataset_name):
    """Loads all CSV files from a directory into a single DataFrame."""
    print(f"Loading {dataset_name} data from {directory}...")
    all_files = glob.glob(os.path.join(directory, "*.csv"))
    
    if not all_files:
        print(f"Warning: No files found in {directory}")
        return pd.DataFrame()
        
    df_list = []
    for filename in all_files:
        try:
            df = pd.read_csv(filename)
            df_list.append(df)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            
    if not df_list:
        return pd.DataFrame()
        
    full_df = pd.concat(df_list, ignore_index=True)
    print(f"Loaded {len(full_df)} rows for {dataset_name}.")
    return full_df

def preprocess_data(df):
    """Standardizes dates and state names with comprehensive cleaning."""
    if df.empty:
        return df
    
    initial_len = len(df)
        
    # parse dates
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
        df = df[df['date'].notna()]  # Remove invalid dates
        
    # clean state names - comprehensive mapping
    if 'state' in df.columns:
        df['state'] = df['state'].astype(str).str.strip().str.title()
        # Comprehensive normalization map
        state_map = {
            "Andaman & Nicobar Islands": "Andaman And Nicobar Islands",
            "Andaman and Nicobar Islands": "Andaman And Nicobar Islands",
            "J & K": "Jammu And Kashmir",
            "J&K": "Jammu And Kashmir",
            "Jammu & Kashmir": "Jammu And Kashmir",
            "Jammu and Kashmir": "Jammu And Kashmir",
            "Dadra & Nagar Haveli": "Dadra And Nagar Haveli And Daman And Diu",
            "Dadra and Nagar Haveli": "Dadra And Nagar Haveli And Daman And Diu",
            "Daman & Diu": "Dadra And Nagar Haveli And Daman And Diu",
            "Daman and Diu": "Dadra And Nagar Haveli And Daman And Diu",
            "Telengana": "Telangana",
            "Telanagana": "Telangana",
            "Orissa": "Odisha",
            "ODISHA": "Odisha",
            "Pondicherry": "Puducherry",
            "Chattisgarh": "Chhattisgarh",
            "Chhatisgarh": "Chhattisgarh",
            "Uttaranchal": "Uttarakhand",
            "Tamilnadu": "Tamil Nadu",
            "WEST BENGAL": "West Bengal",
            "WESTBENGAL": "West Bengal",
            "Westbengal": "West Bengal",
            "West  Bengal": "West Bengal",
        }
        df['state'] = df['state'].replace(state_map)
        
        # Filter out invalid entries (districts/pincodes in state column)
        invalid_states = {"100000", "Balanagar", "Darbhanga", "Jaipur", "Nagpur",
                          "Madanapalle", "Puttenahalli", "Raja Annamalai Puram"}
        df = df[~df['state'].isin(invalid_states)]
        # Filter rows where state is just digits (pincodes)
        df = df[~df['state'].str.match(r'^\d+$', na=False)]
        
    # clean district names
    if 'district' in df.columns:
        df['district'] = df['district'].astype(str).str.strip().str.title()
    
    # Deduplicate
    dup_cols = ['date', 'state', 'district']
    if 'pincode' in df.columns:
        dup_cols.append('pincode')
    dup_cols = [c for c in dup_cols if c in df.columns]
    before_dedup = len(df)
    df = df.drop_duplicates(subset=dup_cols, keep='first')
    dup_count = before_dedup - len(df)
    
    removed = initial_len - len(df)
    if removed > 0:
        print(f"    Cleaned data: removed {removed:,} rows ({dup_count:,} duplicates)")
        
    return df

def aggregate_data(df, group_cols=['date', 'state', 'district']):
    """Aggregates data by state/district/date to remove pincode granularity."""
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if 'pincode' in numeric_cols:
        numeric_cols.remove('pincode')
        
    agg_df = df.groupby(group_cols)[numeric_cols].sum().reset_index()
    return agg_df

def prepare_and_merge_datasets():
    # Load raw data
    df_bio = load_data(DIRS["biometric"], "Biometric")
    df_demo = load_data(DIRS["demographic"], "Demographic")
    df_enrol = load_data(DIRS["enrolment"], "Enrolment")
    
    # Preprocess
    df_bio = preprocess_data(df_bio)
    df_demo = preprocess_data(df_demo)
    df_enrol = preprocess_data(df_enrol)
    
    # Aggregate (removing pincode level)
    agg_bio = aggregate_data(df_bio)
    agg_demo = aggregate_data(df_demo)
    agg_enrol = aggregate_data(df_enrol)
    
    # Merge keys
    merge_keys = ['date', 'state', 'district']
    
    merged = pd.merge(agg_enrol, agg_bio, on=merge_keys, how='outer', suffixes=('_enrol', '_bio'))
    merged = pd.merge(merged, agg_demo, on=merge_keys, how='outer', suffixes=('', '_demo')) 
    
    numeric_cols = merged.select_dtypes(include=['number']).columns
    merged[numeric_cols] = merged[numeric_cols].fillna(0)
    
    # CRITICAL FIX: Filter out rows with no actual activity
    total_before = len(merged)
    merged['_total'] = (merged.get('age_0_5', 0) + merged.get('age_5_17', 0) + 
                        merged.get('age_18_greater', 0) + merged.get('bio_age_5_17', 0) + 
                        merged.get('bio_age_17_', 0) + merged.get('demo_age_5_17', 0) + 
                        merged.get('demo_age_17_', 0))
    merged = merged[merged['_total'] > 0]
    merged = merged.drop(columns=['_total'], errors='ignore')
    
    filtered_count = total_before - len(merged)
    if filtered_count > 0:
        print(f"  Filtered {filtered_count:,} rows with no actual activity")
    
    return merged

def calculate_metrics(df):
    """Calculates core analysis metrics."""
    
    # Total Enrolments
    df['total_enrolments'] = df['age_0_5'] + df['age_5_17'] + df['age_18_greater']
    
    # Total Biometric Updates
    df['total_bio_updates'] = df['bio_age_5_17'] + df['bio_age_17_']
    
    # Total Demographic Updates
    df['total_demo_updates'] = df['demo_age_5_17'] + df['demo_age_17_']
    
    # Total Updates
    df['total_updates'] = df['total_bio_updates'] + df['total_demo_updates']
    
    # Update Intensity
    df['update_intensity'] = df.apply(lambda row: row['total_updates'] / row['total_enrolments'] if row['total_enrolments'] > 0 else 0, axis=1)
    
    # Updates per 1000
    df['updates_per_1000'] = df['update_intensity'] * 1000

    # Shares
    df['bio_share'] = df.apply(lambda row: row['total_bio_updates'] / row['total_updates'] if row['total_updates'] > 0 else 0, axis=1)
    df['demo_share'] = df.apply(lambda row: row['total_demo_updates'] / row['total_updates'] if row['total_updates'] > 0 else 0, axis=1)
    
    return df

def generate_visualizations(df):
    """Generates and saves analysis plots."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    print(f"Generating plots in {OUTPUT_DIR}...")
    sns.set_theme(style="whitegrid")
    
    # 1. National Time Series - FIXED with dual Y-axes
    national = df.groupby('date')[['total_updates', 'total_enrolments']].sum().reset_index()
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()
    
    # Enrolments on left axis (smaller scale)
    line1 = ax1.plot(national['date'], national['total_enrolments'], 's-', 
                     label='Total Enrolments', color='green', linewidth=2)
    ax1.set_ylabel('Enrolments', color='green', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='green')
    
    # Updates on right axis (larger scale)
    line2 = ax2.plot(national['date'], national['total_updates'], 'o-', 
                     label='Total Updates', color='blue', linewidth=2)
    ax2.set_ylabel('Updates', color='blue', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='blue')
    
    ax1.set_title('National Enrolment vs Updates Over Time (Dual Scale)', fontweight='bold')
    ax1.set_xlabel('Date')
    plt.xticks(rotation=45)
    
    # Combined legend
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left')
    
    # Warning about scale difference
    ax1.text(0.02, 0.02, '⚠️ Note: Different Y-scales\nUpdates >> Enrolments in this dataset', 
             transform=ax1.transAxes, fontsize=8, va='bottom',
             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/national_time_series.png")
    plt.close()
    
    # 2. Update Intensity Heatmap (Top 10 States by Volume)
    top_states = df.groupby('state')['total_updates'].sum().nlargest(10).index
    state_df = df[df['state'].isin(top_states)].groupby(['state', 'date'])['update_intensity'].mean().reset_index()
    
    # FIX: Format dates as readable strings before pivoting
    state_df['date_str'] = state_df['date'].dt.strftime('%Y-%m-%d')
    state_pivot = state_df.pivot(index='state', columns='date_str', values='update_intensity')
    
    # Select fewer columns if too many dates (for readability)
    if len(state_pivot.columns) > 20:
        # Sample every Nth date
        n = len(state_pivot.columns) // 15
        selected_cols = state_pivot.columns[::n]
        state_pivot = state_pivot[selected_cols]
    
    plt.figure(figsize=(14, 8))
    sns.heatmap(state_pivot, cmap='YlOrRd', annot=True, fmt=".2f", 
                xticklabels=True, yticklabels=True)
    plt.title('Average Update Intensity Heatmap (Top 10 States)', fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('State')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/state_intensity_heatmap.png", dpi=150)
    plt.close()
    
    # 3. Biometric vs Demographic Composition
    national_comp = df.groupby('date')[['total_bio_updates', 'total_demo_updates']].sum().reset_index()
    # Melt for stacked bar
    
    plt.figure(figsize=(10, 6))
    plt.stackplot(national_comp['date'], national_comp['total_bio_updates'], national_comp['total_demo_updates'], 
                  labels=['Biometric', 'Demographic'], alpha=0.8)
    plt.legend(loc='upper left')
    plt.title('Composition of Updates: Biometric vs Demographic')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/update_composition.png")
    plt.close()

    # 4. Updates Per 1000 - Top 15 Districts (Bar Chart)
    # Aggregated over all time
    district_df = df.groupby(['state', 'district'])[['total_updates', 'total_enrolments']].sum().reset_index()
    district_df['updates_per_1000'] = district_df.apply(lambda row: row['total_updates'] / (row['total_enrolments']/1000) if row['total_enrolments'] > 1000 else 0, axis=1)
    
    top_districts = district_df.sort_values('updates_per_1000', ascending=False).head(15)
    
    plt.figure(figsize=(12, 8))
    sns.barplot(data=top_districts, x='updates_per_1000', y='district', hue='state', dodge=False)
    plt.title('Top 15 Districts by Updates per 1000 Enrolments (Min 1000 Enrolments)')
    plt.xlabel('Updates per 1000 Enrolments')
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/top_districts_intensity.png")
    plt.close()

    # 5. Low Interaction Districts (Bottom 15)
    bottom_districts = district_df[district_df['total_enrolments'] > 1000].sort_values('updates_per_1000', ascending=True).head(15)
    
    plt.figure(figsize=(12, 8))
    sns.barplot(data=bottom_districts, x='updates_per_1000', y='district', hue='state', dodge=False)
    plt.title('Bottom 15 Districts by Updates per 1000 Enrolments (Min 1000 Enrolments)')
    plt.xlabel('Updates per 1000 Enrolments')
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/bottom_districts_intensity.png")
    plt.close()

    # 6. Volatility Analysis (Variance of Update Intensity over time)
    # Filter for districts with sufficient data points (> 3 months)
    district_time_df = df.groupby(['state', 'district', 'date'])['update_intensity'].mean().reset_index()
    volatility_df = district_time_df.groupby(['state', 'district'])['update_intensity'].std().reset_index()
    volatility_df.rename(columns={'update_intensity': 'intensity_std_dev'}, inplace=True)
    
    # Filter out districts with too few observations if needed (implicit in std calculation usually returning NaN, but we fillna previously)
    # Joining with total enrolment to filter out small districts
    district_total_enrol = df.groupby(['state', 'district'])['total_enrolments'].sum().reset_index()
    volatility_df = pd.merge(volatility_df, district_total_enrol, on=['state', 'district'])
    
    # Top 15 Volatile Districts (Min 1000 Enrolments)
    top_volatile = volatility_df[volatility_df['total_enrolments'] > 1000].sort_values('intensity_std_dev', ascending=False).head(15)
    
    plt.figure(figsize=(12, 8))
    sns.barplot(data=top_volatile, x='intensity_std_dev', y='district', hue='state', dodge=False)
    plt.title('Top 15 Most Volatile Districts (Std Dev of Update Intensity)')
    plt.xlabel('Standard Deviation of Update Intensity')
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/top_volatile_districts.png")
    plt.close()

    # 7. Bivariate Scatter: Enrolment vs Updates (Correlation)
    correlation = df[['total_enrolments', 'total_updates']].corr().iloc[0, 1]
    print(f"\nℹ️ Bivariate Correlation (Enrolment vs Updates): {correlation:.4f}")
    
    # NOTE: Low correlation is EXPECTED given data completeness issues
    # Enrolment data is incomplete - updates include historical Aadhaar holders
    if correlation < 0.5:
        print(f"   ⚠️ Low correlation expected: updates likely include historical holders not in enrolment sample")
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.scatterplot(data=district_df, x='total_enrolments', y='total_updates', alpha=0.6, ax=ax)
    ax.set_title(f'Bivariate Analysis: Enrolment vs Updates (r = {correlation:.2f})', fontweight='bold')
    ax.set_xlabel('Total Enrolments')
    ax.set_ylabel('Total Updates')
    
    # Add interpretation note for low correlation
    if correlation < 0.5:
        ax.text(0.02, 0.98, 
                f'⚠️ Low r = {correlation:.2f} is expected:\n'
                'Updates include historical Aadhaar\n'
                'holders not in this enrolment sample',
                transform=ax.transAxes, fontsize=9, va='top',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/bivariate_scatter.png", dpi=150)
    plt.close()

    # 8. Bivariate: Biometric vs Demographic Updates Correlation
    # Re-aggregate specifics for district level
    district_comp_df = df.groupby(['state', 'district'])[['total_bio_updates', 'total_demo_updates']].sum().reset_index()
    bio_demo_corr = district_comp_df[['total_bio_updates', 'total_demo_updates']].corr().iloc[0, 1]
    
    plt.figure(figsize=(10, 8))
    sns.scatterplot(data=district_comp_df, x='total_bio_updates', y='total_demo_updates', alpha=0.6)
    plt.title(f'Bivariate: Biometric vs Demographic Updates (Correlation: {bio_demo_corr:.2f})')
    plt.xlabel('Total Biometric Updates')
    plt.ylabel('Total Demographic Updates')
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/bio_vs_demo_scatter.png")
    plt.close()

    # 9. Bivariate: Enrolment vs Update Intensity
    # Does district size predict intensity?
    
    plt.figure(figsize=(10, 8))
    sns.scatterplot(data=district_df, x='total_enrolments', y='updates_per_1000', alpha=0.6)
    plt.title('Bivariate: Enrolment Size vs Update Intensity')
    plt.xlabel('Total Enrolments')
    plt.ylabel('Updates per 1000 Enrolments')
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/enrol_vs_intensity_scatter.png")
    plt.close()

    # 10. Bivariate Categorical: State vs Intensity Distribution (Box Plot)
    # Filter for top 10 states by volume to keep plot readable
    top_10_states = df.groupby('state')['total_updates'].sum().nlargest(10).index
    subset_df = df[df['state'].isin(top_10_states)]
    
    plt.figure(figsize=(14, 8))
    sns.boxplot(data=subset_df, x='state', y='updates_per_1000')
    plt.title('Distribution of District Update Intensity by Target State')
    plt.xticks(rotation=45)
    plt.ylabel('Updates per 1000 Enrolments')
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/state_intensity_boxplot.png")
    plt.close()

    # 11. Pareto Analysis (Lorenz Curve) - Concentration of Updates
    # Are 20% of districts responsible for 80% of updates?
    dist_sum = df.groupby(['state', 'district'])['total_updates'].sum().sort_values(ascending=False).reset_index()
    dist_sum['cumulative_updates'] = dist_sum['total_updates'].cumsum()
    dist_sum['cumulative_perc'] = dist_sum['cumulative_updates'] / dist_sum['total_updates'].sum()
    dist_sum['district_perc'] = (dist_sum.index + 1) / len(dist_sum)
    
    plt.figure(figsize=(10, 8))
    sns.lineplot(data=dist_sum, x='district_perc', y='cumulative_perc')
    plt.plot([0, 1], [0, 1], linestyle='--', color='red', label='Equality Line')
    plt.title('Pareto Analysis: Concentration of Updates (Lorenz Curve)')
    plt.xlabel('Cumulative % of Districts')
    plt.ylabel('Cumulative % of Updates')
    plt.legend()
    plt.axvline(x=0.2, color='green', linestyle=':', label='20% Districts')
    # Find Y value at X=0.2
    y_at_20 = dist_sum[dist_sum['district_perc'] <= 0.2].tail(1)['cumulative_perc'].values[0] if not dist_sum.empty else 0
    plt.text(0.22, y_at_20, f'{y_at_20:.0%} updates', color='green')
    plt.grid(True)
    plt.savefig(f"{OUTPUT_DIR}/pareto_chart.png")
    plt.close()
    
    # 12. Day of Week Seasonality
    # Extract DOW from date (0=Monday, 6=Sunday)
    weekday_df = df.groupby(df['date'].dt.day_name())[['total_updates']].mean().reindex(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    ).reset_index()
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=weekday_df, x='date', y='total_updates', color='skyblue')
    plt.title('Average Daily Updates by Day of Week (Seasonality)')
    plt.xlabel('Day of Week')
    plt.ylabel('Average Total Updates')
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/weekly_seasonality.png")
    plt.close()

    plt.close()

    # 13. Trivariate: State-wise Time Trends (Time x State x Intensity)
    # Line plot with hue=State
    top_5_states = df.groupby('state')['total_updates'].sum().nlargest(5).index
    state_time_df = df[df['state'].isin(top_5_states)].groupby(['date', 'state'])['total_updates'].sum().reset_index()
    
    plt.figure(figsize=(12, 8))
    sns.lineplot(data=state_time_df, x='date', y='total_updates', hue='state', marker='o')
    plt.title('Time Trends by Top 5 States (Trivariate: Time x State x Updates)')
    plt.ylabel('Total Updates')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/trivariate_time_state.png")
    plt.close()

    # 14. Trivariate Bubble Chart: Enrolment x Updates x Bio Share
    # X=Enrolment, Y=Updates, Size=Bio Share (Visualized via color/hue here for clarity)
    # Aggregated by District
    district_agg = df.groupby(['state', 'district'])[['total_enrolments', 'total_updates', 'total_bio_updates']].sum().reset_index()
    district_agg['bio_share'] = district_agg['total_bio_updates'] / district_agg['total_updates']
    
    plt.figure(figsize=(12, 8))
    scatter = sns.scatterplot(
        data=district_agg, 
        x='total_enrolments', 
        y='total_updates', 
        hue='bio_share', 
        palette='viridis', 
        s=100, 
        alpha=0.7
    )
    plt.title('District Profiles: Enrolment vs Updates vs Bio Share (Color)')
    plt.xlabel('Total Enrolments')
    plt.ylabel('Total Updates')
    plt.legend(title='Biometric Share')
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/trivariate_bubble_composition.png")
    plt.close()

    # 15. Trivariate Risk Matrix: Intensity vs Volatility x State
    # Already computed volatility_df earlier. Reusing that.
    # volatility_df columns: state, district, intensity_std_dev, total_enrolments
    
    # Need mean intensity for X axis
    district_mean_intensity = df.groupby(['state', 'district'])['update_intensity'].mean().reset_index()
    risk_df = pd.merge(volatility_df, district_mean_intensity, on=['state', 'district'])
    
    # Filter for Top 5 States for readability
    risk_df_top5 = risk_df[risk_df['state'].isin(top_5_states)]
    
    plt.figure(figsize=(12, 8))
    sns.scatterplot(
        data=risk_df_top5,
        x='update_intensity',
        y='intensity_std_dev',
        hue='state',
        style='state',
        s=100,
        alpha=0.8
    )
    plt.title('Risk Matrix: Update Intensity vs Volatility (Top 5 States)')
    plt.xlabel('Average Update Intensity')
    plt.ylabel('Volatility (Std Dev of Intensity)')
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/trivariate_risk_matrix.png")
    plt.close()

def verify_results(final_df, df_enrol, df_bio, df_demo):
    """
    Verifies that the aggregation and merging process didn't lose data.
    Comparing sums of key metrics from raw inputs vs final output.
    """
    print("\n--- Data Verification ---")
    
    # 1. Enrolment Check
    # Note: Enrolment raw columns might have different names or need simple sum
    # Raw Enrolment file columns: age_0_5, age_5_17, age_18_greater
    raw_enrol_sum = df_enrol[['age_0_5', 'age_5_17', 'age_18_greater']].sum().sum()
    processed_enrol_sum = final_df['total_enrolments'].sum()
    
    print(f"Total Enrolments (Raw): {raw_enrol_sum:,.0f}")
    print(f"Total Enrolments (Processed): {processed_enrol_sum:,.0f}")
    if abs(raw_enrol_sum - processed_enrol_sum) > 1.0:
        print("❌ Enrolment mismatch!")
    else:
        print("✅ Enrolment totals match.")

    # 2. Update Check
    # Raw Bio: bio_age_5_17 + bio_age_17_
    raw_bio_sum = df_bio[['bio_age_5_17', 'bio_age_17_']].sum().sum()
    processed_bio_sum = final_df['total_bio_updates'].sum()
    
    # Raw Demo: demo_age_5_17 + demo_age_17_
    raw_demo_sum = df_demo[['demo_age_5_17', 'demo_age_17_']].sum().sum()
    processed_demo_sum = final_df['total_demo_updates'].sum()
    
    print(f"Total Biometric Updates (Raw): {raw_bio_sum:,.0f} | Processed: {processed_bio_sum:,.0f}")
    print(f"Total Demographic Updates (Raw): {raw_demo_sum:,.0f} | Processed: {processed_demo_sum:,.0f}")
    
    if abs(raw_bio_sum - processed_bio_sum) < 1.0 and abs(raw_demo_sum - processed_demo_sum) < 1.0:
        print("✅ Update count totals match.")
    else:
        print("❌ Update count mismatch! Check merge logic.")

def check_data_quality(df):
    """
    Performs specific checks for data cleanliness.
    """
    print("\n--- Data Quality Report ---")
    
    # 1. Null Checks
    null_counts = df.isnull().sum().sum()
    if null_counts == 0:
        print("✅ No null values found in final dataset.")
    else:
        print(f"⚠️ Warning: Found {null_counts} null values.")
        
    # 2. Negative Value Checks
    numeric_cols = ['total_enrolments', 'total_updates', 'total_bio_updates', 'total_demo_updates']
    negatives = 0
    for col in numeric_cols:
        if (df[col] < 0).any():
            negatives += (df[col] < 0).sum()
            
    if negatives == 0:
        print("✅ No negative values found in metric columns.")
    else:
        print(f"❌ Critical: Found {negatives} negative values! Data may be corrupted.")

    # 3. State Name Consistency
    unique_states = sorted(df['state'].unique())
    print(f"ℹ️ Found {len(unique_states)} unique state names.")
    # Check for obvious duplicates or lower case issues
    if any(s.islower() for s in unique_states):
        print("⚠️ Warning: Some state names are lowercase.")
    if len(unique_states) > 37: # Approx count including UTs
        print("⚠️ Note: High number of states might indicate duplicate spellings.")
        
    # 4. Date Range Check
    print(f"ℹ️ Date Range: {df['date'].min().date()} to {df['date'].max().date()}")

def main():
    print("Starting Aadhaar Data Analysis Phase 2...")
    
    # Load raw data first for verification later
    df_bio_raw = load_data(DIRS["biometric"], "Biometric")
    df_demo_raw = load_data(DIRS["demographic"], "Demographic")
    df_enrol_raw = load_data(DIRS["enrolment"], "Enrolment")
    
    # Preprocess standalone to simulate pipeline
    df_bio = preprocess_data(df_bio_raw.copy())
    df_demo = preprocess_data(df_demo_raw.copy())
    df_enrol = preprocess_data(df_enrol_raw.copy())
    
    # Aggregate
    agg_bio = aggregate_data(df_bio)
    agg_demo = aggregate_data(df_demo)
    agg_enrol = aggregate_data(df_enrol)
    
    # Merge
    merge_keys = ['date', 'state', 'district']
    merged = pd.merge(agg_enrol, agg_bio, on=merge_keys, how='outer', suffixes=('_enrol', '_bio'))
    merged = pd.merge(merged, agg_demo, on=merge_keys, how='outer', suffixes=('', '_demo')) 
    
    numeric_cols = merged.select_dtypes(include=['number']).columns
    merged[numeric_cols] = merged[numeric_cols].fillna(0)
    
    final_df = calculate_metrics(merged)
    
    print(f"Final Dataset Shape: {final_df.shape}")
    
    # Quality Check
    check_data_quality(final_df)
    
    # Verify
    verify_results(final_df, df_enrol_raw, df_bio_raw, df_demo_raw)
    
    # Generate Visualizations
    generate_visualizations(final_df)
    
    print("Analysis Complete. Plots saved to 'aadhaar_plots' directory.")

if __name__ == "__main__":
    main()
