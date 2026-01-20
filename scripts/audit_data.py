import pandas as pd
import glob
import os

DATA_DIR = 'data'

def audit_data():
    biometric_files = glob.glob(os.path.join(DATA_DIR, 'api_data_aadhar_biometric', '*.csv'))
    demographic_files = glob.glob(os.path.join(DATA_DIR, 'api_data_aadhar_demographic', '*.csv'))
    enrolment_files = glob.glob(os.path.join(DATA_DIR, 'api_data_aadhar_enrolment', '*.csv'))

    print(f"Found {len(biometric_files)} biometric files")
    print(f"Found {len(demographic_files)} demographic files")
    print(f"Found {len(enrolment_files)} enrolment files")

    # Counters
    total_biometric = 0
    total_demographic = 0
    total_enrolment = 0
    
    total_demo_minor = 0 # demo_age_5_17
    
    unique_states = set()
    unique_districts = set()
    unique_pincodes = set()
    
    min_date = None
    max_date = None

    # Biometric Processing
    print("\nProcessing Biometric Data...")
    for f in biometric_files:
        try:
            df = pd.read_csv(f)
            # Columns: date,state,district,pincode,bio_age_5_17,bio_age_17_
            total_biometric += df['bio_age_5_17'].sum() + df['bio_age_17_'].sum()
            
            unique_states.update(df['state'].unique())
            unique_districts.update(df['district'].unique())
            unique_pincodes.update(df['pincode'].unique())
            
            dates = pd.to_datetime(df['date'], dayfirst=True)
            if min_date is None or dates.min() < min_date:
                min_date = dates.min()
            if max_date is None or dates.max() > max_date:
                max_date = dates.max()
        except Exception as e:
            print(f"Error processing {f}: {e}")

    # Demographic Processing
    print("Processing Demographic Data...")
    for f in demographic_files:
        try:
            df = pd.read_csv(f)
            # Columns: date,state,district,pincode,demo_age_5_17,demo_age_17_
            batch_demo_minor = df['demo_age_5_17'].sum()
            total_demo_minor += batch_demo_minor
            total_demographic += batch_demo_minor + df['demo_age_17_'].sum()
            
            unique_states.update(df['state'].unique())
            unique_districts.update(df['district'].unique())
            unique_pincodes.update(df['pincode'].unique())
            
            dates = pd.to_datetime(df['date'], dayfirst=True)
            if min_date is None or dates.min() < min_date:
                min_date = dates.min()
            if max_date is None or dates.max() > max_date:
                max_date = dates.max()
        except Exception as e:
            print(f"Error processing {f}: {e}")

    # Enrolment Processing
    print("Processing Enrolment Data...")
    for f in enrolment_files:
        try:
            df = pd.read_csv(f)
            # Columns: date,state,district,pincode,age_0_5,age_5_17,age_18_greater
            total_enrolment += df['age_0_5'].sum() + df['age_5_17'].sum() + df['age_18_greater'].sum()
            
            unique_states.update(df['state'].unique())
            unique_districts.update(df['district'].unique())
            unique_pincodes.update(df['pincode'].unique())
            
            dates = pd.to_datetime(df['date'], dayfirst=True)
            if min_date is None or dates.min() < min_date:
                min_date = dates.min()
            if max_date is None or dates.max() > max_date:
                max_date = dates.max()
        except Exception as e:
            print(f"Error processing {f}: {e}")

    print("\n--- AUDIT RESULTS ---")
    print(f"Total Biometric Transactions: {total_biometric:,}")
    print(f"Total Demographic Transactions: {total_demographic:,}")
    print(f"Total Enrolment Transactions: {total_enrolment:,}")
    print(f"Total Transactions (Sum): {total_biometric + total_demographic + total_enrolment:,}")

    # Ratios
    biometric_share = total_biometric / (total_biometric + total_demographic + total_enrolment) * 100
    demographic_share = total_demographic / (total_biometric + total_demographic + total_enrolment) * 100
    
    print(f"\nBiometric Share of Total: {biometric_share:.2f}% (Report claims 85%)")
    print(f"Demographic Share of Total: {demographic_share:.2f}%")


    # Minor Share Calculation (Demographic)
    if total_demographic > 0:
        minor_share = (total_demo_minor / total_demographic) * 100
        print(f"Minor (5-17) Share of Demographic Updates: {minor_share:.2f}% (Report claims 9.7%)")
    else:
        print("No demographic data found.")

    print(f"\nUnique States Count: {len(unique_states)}")
    print(f"Unique Districts Count: {len(unique_districts)}")
    print(f"Unique Pincodes Count: {len(unique_pincodes)}")
    
    print(f"\nDate Range: {min_date} to {max_date}")
    
    print("\nStates Found:")
    for s in sorted(list(unique_states)):
        print(f" - {s}")

if __name__ == "__main__":
    audit_data()
