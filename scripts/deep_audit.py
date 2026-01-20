import pandas as pd
import glob
import os
import datetime

DATA_DIR = 'data'

def deep_audit():
    print("Loading data for deep audit...")
    
    # Load all files
    bio_files = glob.glob(os.path.join(DATA_DIR, 'api_data_aadhar_biometric', '*.csv'))
    demo_files = glob.glob(os.path.join(DATA_DIR, 'api_data_aadhar_demographic', '*.csv'))
    enrol_files = glob.glob(os.path.join(DATA_DIR, 'api_data_aadhar_enrolment', '*.csv'))
    
    # helper to load and concat
    def load_dfs(files, type_name):
        dfs = []
        for f in files:
            try:
                df = pd.read_csv(f)
                # Parse dates immediately
                df['date'] = pd.to_datetime(df['date'], dayfirst=True)
                dfs.append(df)
            except Exception as e:
                print(f"Error loading {f}: {e}")
        if not dfs:
            return pd.DataFrame()
        return pd.concat(dfs, ignore_index=True)

    df_bio = load_dfs(bio_files, "Biometric")
    df_demo = load_dfs(demo_files, "Demographic")
    df_enrol = load_dfs(enrol_files, "Enrolment")
    
    print(f"Loaded: Bio({len(df_bio)}), Demo({len(df_demo)}), Enrol({len(df_enrol)})")

    # --- 1. Temporal Analysis (August Collapse) ---
    print("\n--- 1. Temporal Analysis (August Collapse Check) ---")
    if not df_demo.empty:
        df_demo['month'] = df_demo['date'].dt.to_period('M')
        monthly_counts = df_demo.groupby('month')[['demo_age_5_17', 'demo_age_17_']].sum()
        monthly_counts['total'] = monthly_counts['demo_age_5_17'] + monthly_counts['demo_age_17_']
        print("Monthly Demographic Volume:")
        print(monthly_counts)
        
        # Check collapse
        try:
            july = monthly_counts.loc['2025-07']['total']
            aug = monthly_counts.loc['2025-08']['total']
            sept = monthly_counts.loc['2025-09']['total']
            print(f"\nJuly: {july:,.0f}, Aug: {aug:,.0f}, Sept: {sept:,.0f}")
            if aug < july * 0.5:
                 print("VERIFIED: Significant drop in August (>50%).")
            else:
                 print(f"DISCREPANCY: August drop not catastrophic. Ratio Aug/July = {aug/july:.2f}")
        except KeyError:
             print("Could not find July/Aug 2025 data.")

    # --- 2. Day of Week Analysis (Tuesday Anomaly) ---
    print("\n--- 2. Day of Week Analysis (Tuesday Anomaly) ---")
    if not df_demo.empty:
        df_demo['day_name'] = df_demo['date'].dt.day_name()
        daily_avg = df_demo.groupby('day_name')[['demo_age_5_17', 'demo_age_17_']].sum().sum(axis=1)
        # We need average per occurrence, not sum, because dataset might have different count of Mondays/Tuesdays
        day_counts = df_demo['date'].dt.day_name().value_counts()
        # This is rough because 'date' column in CSV might be unique dates or transaction dates. 
        # Assuming 'date' is the transaction date.
        # Actually, let's just look at the Sum distribution first.
        
        print("Total Volume by Day of Week:")
        print(daily_avg.sort_values(ascending=False))
        
        tue = daily_avg.get('Tuesday', 0)
        mon = daily_avg.get('Monday', 0)
        if mon > 0:
            print(f"Tuesday/Monday Ratio: {tue/mon:.2f} (Claim: 5x)")
        else:
            print("Monday volume is 0.")

    # --- 3. Child Attention Gap ---
    print("\n--- 3. Child Attention Gap Verification ---")
    # Share of updates (Demo)
    minor_update_count = df_demo['demo_age_5_17'].sum()
    total_update_count = df_demo['demo_age_5_17'].sum() + df_demo['demo_age_17_'].sum()
    minor_update_share = minor_update_count / total_update_count if total_update_count else 0
    
    # Share of Enrolment (Population Proxy)
    # Report says: "Minors (5-17)... representing 25-30% of population"
    # Let's see what the *Enrolment* dataset says about share.
    # Dataset cols: age_0_5, age_5_17, age_18_greater
    minor_enrol_count = df_enrol['age_5_17'].sum()
    total_enrol_count = df_enrol['age_0_5'].sum() + df_enrol['age_5_17'].sum() + df_enrol['age_18_greater'].sum()
    minor_enrol_share = minor_enrol_count / total_enrol_count if total_enrol_count else 0
    
    child_attention_gap = minor_update_share - minor_enrol_share
    
    print(f"Minor Update Share: {minor_update_share:.4f} ({minor_update_share*100:.1f}%)")
    print(f"Minor Enrolment Share (in dataset): {minor_enrol_share:.4f} ({minor_enrol_share*100:.1f}%)")
    print(f"Calculated Gap: {child_attention_gap:.4f}")
    print(f"Report Claim Gap: -0.67 (Note: Report might measure gap differently or normalize differently)")
    
    # --- 4. Geographic Extremes ---
    print("\n--- 4. Geographic Extremes (District Intensity) ---")
    # We need to aggregate by district. Using 'district' column.
    # Note: State names might be dirty.
    
    # Group by district and sum updates
    dist_updates = df_demo.groupby('district')[['demo_age_5_17', 'demo_age_17_']].sum()
    dist_updates['total_updates'] = dist_updates['demo_age_5_17'] + dist_updates['demo_age_17_']
    
    # Group by district and sum enrolments (for normalization)
    dist_enrol = df_enrol.groupby('district')[['age_0_5', 'age_5_17', 'age_18_greater']].sum()
    dist_enrol['total_enrol'] = dist_enrol['age_0_5'] + dist_enrol['age_5_17'] + dist_enrol['age_18_greater']
    
    # Merge
    merged = dist_updates.join(dist_enrol, lsuffix='_upd', rsuffix='_enr', how='inner')
    
    # Calculate Intensity: Updates per 1000 Enrolments
    # Use sum of updates / sum of enrolments * 1000
    merged['intensity'] = (merged['total_updates'] / merged['total_enrol']) * 1000
    
    top_15 = merged.sort_values('intensity', ascending=False).head(15)
    print("Top 15 Districts by Intensity (Updates per 1000 Enrolments):")
    print(top_15[['total_updates', 'total_enrol', 'intensity']])
    
    # Check Manipur claim
    # We don't have State in this merged view easily unless we groupby state+district.
    # Let's do a quick check of the indices of Top 15.
    print("\nTop District Names:", top_15.index.tolist())
    
    # Check "13 of 15 lowest show near-zero"
    bottom_15 = merged[merged['total_enrol'] > 1000].sort_values('intensity', ascending=True).head(15)
    print("\nBottom 15 Districts (Enrol > 1000):")
    print(bottom_15[['total_updates', 'total_enrol', 'intensity']])

if __name__ == "__main__":
    deep_audit()
