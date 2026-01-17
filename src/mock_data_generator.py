import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# Configuration
DATA_DIR = '../data/raw'
START_DATE = datetime(2018, 1, 1)
END_DATE = datetime(2023, 12, 31)
STATES = ['Maharashtra', 'Uttar Pradesh', 'Karnataka', 'Bihar', 'West Bengal']
DISTRICTS_PER_STATE = 5

np.random.seed(42)

def generate_dates(start, end):
    current = start
    dates = []
    while current <= end:
        dates.append(current)
        current += timedelta(days=32)
        current = current.replace(day=1)
    return dates

dates = generate_dates(START_DATE, END_DATE)
months_years = [(d.month, d.year) for d in dates]

def get_districts(state):
    return [f"{state}_District_{i+1}" for i in range(DISTRICTS_PER_STATE)]

print("Generating Synthetic Data...")

# ---------------------------------------------------------
# 1. Enrolment Data
# ---------------------------------------------------------
enrolment_records = []
for state in STATES:
    for district in get_districts(state):
        for month, year in months_years:
            # Trend: Slow decline in enrolments as saturation is reached, but steady for 0-5 age group
            base_enrolment = np.random.randint(100, 1000)
            
            # Age Groups: 0-5 (high), 5-18 (med), 18+ (low - mostly updates)
            for age_group in ['0-5', '5-18', '18+']:
                count = base_enrolment
                if age_group == '0-5':
                    count = int(count * 1.5)
                elif age_group == '18+':
                    count = int(count * 0.2)
                
                # Gender Split
                m_count = int(count * 0.52)
                f_count = count - m_count
                
                enrolment_records.append({
                    'State': state,
                    'District': district,
                    'Year': year,
                    'Month': month,
                    'AgeGroup': age_group,
                    'Gender': 'Male',
                    'Count': m_count
                })
                enrolment_records.append({
                    'State': state,
                    'District': district,
                    'Year': year,
                    'Month': month,
                    'AgeGroup': age_group,
                    'Gender': 'Female',
                    'Count': f_count
                })

df_enrol = pd.DataFrame(enrolment_records)
os.makedirs(DATA_DIR, exist_ok=True)
df_enrol.to_csv(os.path.join(DATA_DIR, 'enrolment_data.csv'), index=False)
print(f"Enrolment Data: {len(df_enrol)} rows saved.")

# ---------------------------------------------------------
# 2. Demographic Update Data
# ---------------------------------------------------------
# Signals: 
# - Address updates spike during COVID (2020/2021) for urban centers (Reverse migration?)
# - Mobile updates increasing over time (Digital India push)

demo_update_records = []
for state in STATES:
    is_urban_heavy = state in ['Maharashtra', 'Karnataka']
    
    for district in get_districts(state):
        for month, year in months_years:
            base_updates = np.random.randint(50, 500)
            
            # Update Types
            types = ['Address', 'DoB', 'Mobile', 'Name', 'Gender']
            
            for utype in types:
                vol = base_updates
                
                # SIGNAL: Mobile updates trend up
                if utype == 'Mobile':
                    vol = int(vol * (1 + (year - 2018) * 0.2))
                    
                # SIGNAL: Address updates spike in 2020-2021 for urban states
                if utype == 'Address' and year in [2020, 2021] and is_urban_heavy:
                    vol = int(vol * 2.5)
                
                demo_update_records.append({
                    'State': state,
                    'District': district,
                    'Year': year,
                    'Month': month,
                    'UpdateType': utype,
                    'Count': vol
                })

df_demo = pd.DataFrame(demo_update_records)
df_demo.to_csv(os.path.join(DATA_DIR, 'demographic_update_data.csv'), index=False)
print(f"Demographic Update Data: {len(df_demo)} rows saved.")

# ---------------------------------------------------------
# 3. Biometric Update Data
# ---------------------------------------------------------
# Signals:
# - Mandatory updates at age 5 and 15 causes clear spikes if we had age-wise data. 
# - Since this dataset is aggregated, we might just see volume.
# - Let's assume Biometric updates are generally consistent but gathered in 'Camps' (random spikes).

bio_update_records = []
for state in STATES:
    for district in get_districts(state):
        for month, year in months_years:
            base_bio = np.random.randint(20, 200)
            
            # Random "Camp" event in a district
            if np.random.random() > 0.95:
                base_bio = base_bio * 5
            
            for btype in ['Fingerprint', 'Iris', 'Photo']:
                count = int(base_bio / 3)
                bio_update_records.append({
                    'State': state,
                    'District': district,
                    'Year': year,
                    'Month': month,
                    'UpdateType': btype,
                    'Count': count
                })

df_bio = pd.DataFrame(bio_update_records)
df_bio.to_csv(os.path.join(DATA_DIR, 'biometric_update_data.csv'), index=False)
print(f"Biometric Update Data: {len(df_bio)} rows saved.")
