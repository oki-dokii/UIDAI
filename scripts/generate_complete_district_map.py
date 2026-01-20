#!/usr/bin/env python3
"""
UIDAI Data Hackathon 2026 - ENHANCED DISTRICT MAP GENERATOR
Creates interactive folium map with ALL districts from the dataset.
Includes data cleaning, name standardization, and comprehensive geocoding.
"""

import pandas as pd
import folium
from folium import plugins
import os
import numpy as np
import re

# ============================================================================
# CONFIGURATION
# ============================================================================
OUTPUT_DIR = "outputs/interactive_maps"
OUTPUT_FILE = "india_child_gap_map_complete.html"

# ============================================================================
# NAME STANDARDIZATION MAPPINGS
# ============================================================================
STATE_NAME_MAPPING = {
    'Orissa': 'Odisha',
    'orissa': 'Odisha',
    'ORISSA': 'Odisha',
    'west Bengal': 'West Bengal',
    'WEST BENGAL': 'West Bengal',
    'Tamilnadu': 'Tamil Nadu',
    'Tamil nadu': 'Tamil Nadu',
    'TAMILNADU': 'Tamil Nadu',
    'TAMIL NADU': 'Tamil Nadu',
    'Andhra pradesh': 'Andhra Pradesh',
    'ANDHRA PRADESH': 'Andhra Pradesh',
    'Jammu and Kashmir': 'Jammu And Kashmir',
    'Jammu & Kashmir': 'Jammu And Kashmir',
    'jammu and kashmir': 'Jammu And Kashmir',
    'JAMMU AND KASHMIR': 'Jammu And Kashmir',
    'Dadra & Nagar Haveli': 'Dadra And Nagar Haveli',
    'Dadra and Nagar Haveli': 'Dadra And Nagar Haveli',
    'Dadra and Nagar Haveli and Daman and Diu': 'Dadra And Nagar Haveli And Daman And Diu',
    'Daman and Diu': 'Daman And Diu',
    'Daman & Diu': 'Daman And Diu',
    'Andaman and Nicobar Islands': 'Andaman And Nicobar Islands',
    'Andaman And Nicobar': 'Andaman And Nicobar Islands',
    'A & N Islands': 'Andaman And Nicobar Islands',
    'Arunachal pradesh': 'Arunachal Pradesh',
    'ARUNACHAL PRADESH': 'Arunachal Pradesh',
    'Himachal pradesh': 'Himachal Pradesh',
    'HIMACHAL PRADESH': 'Himachal Pradesh',
    'Madhya pradesh': 'Madhya Pradesh',
    'MADHYA PRADESH': 'Madhya Pradesh',
    'Uttar pradesh': 'Uttar Pradesh',
    'UTTAR PRADESH': 'Uttar Pradesh',
    'Chattisgarh': 'Chhattisgarh',
    'Chhatisgarh': 'Chhattisgarh',
    'CHHATTISGARH': 'Chhattisgarh',
    'NCT of Delhi': 'Delhi',
    'NCT OF DELHI': 'Delhi',
    'New Delhi': 'Delhi',
    'Pondicherry': 'Puducherry',
    'PUDUCHERRY': 'Puducherry',
    'Uttaranchal': 'Uttarakhand',
    'UTTARAKHAND': 'Uttarakhand',
}

# State centroids (comprehensive)
STATE_COORDS = {
    'Andaman And Nicobar Islands': (11.7401, 92.6586),
    'Andhra Pradesh': (15.9129, 79.74),
    'Arunachal Pradesh': (28.218, 94.7278),
    'Assam': (26.2006, 92.9376),
    'Bihar': (25.0961, 85.3131),
    'Chandigarh': (30.7333, 76.7794),
    'Chhattisgarh': (21.2787, 81.8661),
    'Dadra And Nagar Haveli': (20.1809, 73.0169),
    'Dadra And Nagar Haveli And Daman And Diu': (20.1809, 73.0169),
    'Daman And Diu': (20.4283, 72.8397),
    'Delhi': (28.7041, 77.1025),
    'Goa': (15.2993, 74.124),
    'Gujarat': (22.2587, 71.1924),
    'Haryana': (29.0588, 76.0856),
    'Himachal Pradesh': (31.1048, 77.1734),
    'Jammu And Kashmir': (33.7782, 76.5762),
    'Jharkhand': (23.6102, 85.2799),
    'Karnataka': (15.3173, 75.7139),
    'Kerala': (10.8505, 76.2711),
    'Ladakh': (34.1526, 77.5771),
    'Lakshadweep': (10.5667, 72.6417),
    'Madhya Pradesh': (22.9734, 78.6569),
    'Maharashtra': (19.7515, 75.7139),
    'Manipur': (24.6637, 93.9063),
    'Meghalaya': (25.467, 91.3662),
    'Mizoram': (23.1645, 92.9376),
    'Nagaland': (26.1584, 94.5624),
    'Odisha': (20.9517, 85.0985),
    'Puducherry': (11.9416, 79.8083),
    'Punjab': (31.1471, 75.3412),
    'Rajasthan': (27.0238, 74.2179),
    'Sikkim': (27.533, 88.5122),
    'Tamil Nadu': (11.1271, 78.6569),
    'Telangana': (18.1124, 79.0193),
    'Tripura': (23.9408, 91.9882),
    'Uttar Pradesh': (26.8467, 80.9462),
    'Uttarakhand': (30.0668, 79.0193),
    'West Bengal': (22.9868, 87.855),
}

# Major district coordinates
DISTRICT_COORDS = {
    # Metros
    ('Maharashtra', 'Mumbai'): (19.0760, 72.8777),
    ('Maharashtra', 'Mumbai Suburban'): (19.1136, 72.8697),
    ('Maharashtra', 'Pune'): (18.5204, 73.8567),
    ('Maharashtra', 'Nagpur'): (21.1458, 79.0882),
    ('Maharashtra', 'Thane'): (19.2183, 72.9781),
    ('Delhi', 'New Delhi'): (28.6139, 77.2090),
    ('Delhi', 'North Delhi'): (28.7545, 77.1173),
    ('Delhi', 'South Delhi'): (28.5245, 77.1855),
    ('Delhi', 'East Delhi'): (28.6687, 77.3103),
    ('Delhi', 'West Delhi'): (28.6519, 77.0467),
    ('Delhi', 'Central Delhi'): (28.6508, 77.2227),
    ('Delhi', 'North West Delhi'): (28.7372, 77.0731),
    ('Delhi', 'North East Delhi'): (28.7279, 77.2688),
    ('Delhi', 'South West Delhi'): (28.5725, 77.0429),
    ('Delhi', 'South East Delhi'): (28.5460, 77.2728),
    ('Delhi', 'Shahdara'): (28.6681, 77.2951),
    ('Karnataka', 'Bengaluru Urban'): (12.9716, 77.5946),
    ('Karnataka', 'Bengaluru Rural'): (13.2257, 77.4024),
    ('Tamil Nadu', 'Chennai'): (13.0827, 80.2707),
    ('Telangana', 'Hyderabad'): (17.3850, 78.4867),
    ('West Bengal', 'Kolkata'): (22.5726, 88.3639),
    ('Gujarat', 'Ahmedabad'): (23.0225, 72.5714),
    ('Gujarat', 'Surat'): (21.1702, 72.8311),
    ('Rajasthan', 'Jaipur'): (26.9124, 75.7873),
    ('Uttar Pradesh', 'Lucknow'): (26.8467, 80.9462),
    ('Madhya Pradesh', 'Bhopal'): (23.2599, 77.4126),
    ('Madhya Pradesh', 'Indore'): (22.7196, 75.8577),
    ('Bihar', 'Patna'): (25.5941, 85.1376),
    ('Jharkhand', 'Ranchi'): (23.3441, 85.3096),
    ('Odisha', 'Bhubaneswar'): (20.2961, 85.8245),
    ('Assam', 'Guwahati'): (26.1445, 91.7362),
    ('Kerala', 'Thiruvananthapuram'): (8.5241, 76.9366),
    ('Kerala', 'Ernakulam'): (9.9816, 76.2999),
    ('Kerala', 'Kozhikode'): (11.2588, 75.7804),
    ('Andhra Pradesh', 'Visakhapatnam'): (17.6868, 83.2185),
    ('Andhra Pradesh', 'Vijayawada'): (16.5062, 80.6480),
    ('Punjab', 'Ludhiana'): (30.9010, 75.8573),
    ('Punjab', 'Amritsar'): (31.6340, 74.8723),
    ('Haryana', 'Gurugram'): (28.4595, 77.0266),
    ('Haryana', 'Faridabad'): (28.4089, 77.3178),
    ('Uttar Pradesh', 'Kanpur Nagar'): (26.4499, 80.3319),
    ('Uttar Pradesh', 'Varanasi'): (25.3176, 82.9739),
    ('Uttar Pradesh', 'Agra'): (27.1767, 78.0081),
    ('Uttar Pradesh', 'Ghaziabad'): (28.6692, 77.4538),
    ('Uttar Pradesh', 'Noida'): (28.5355, 77.3910),
    ('Uttar Pradesh', 'Gautam Buddha Nagar'): (28.5355, 77.3910),
    ('Uttar Pradesh', 'Meerut'): (28.9845, 77.7064),
    ('Uttar Pradesh', 'Prayagraj'): (25.4358, 81.8463),
    ('Uttar Pradesh', 'Aligarh'): (27.8974, 78.0880),
    ('Chandigarh', 'Chandigarh'): (30.7333, 76.7794),
    ('Goa', 'North Goa'): (15.5469, 73.7897),
    ('Goa', 'South Goa'): (15.1215, 74.0849),
    # Northeast
    ('Arunachal Pradesh', 'Itanagar'): (27.0844, 93.6053),
    ('Manipur', 'Imphal East'): (24.8074, 94.0275),
    ('Manipur', 'Imphal West'): (24.8033, 93.9174),
    ('Meghalaya', 'East Khasi Hills'): (25.5788, 91.8933),
    ('Mizoram', 'Aizawl'): (23.7271, 92.7176),
    ('Nagaland', 'Kohima'): (25.6586, 94.1055),
    ('Sikkim', 'Gangtok'): (27.3389, 88.6065),
    ('Tripura', 'West Tripura'): (23.9408, 91.3115),
}

# ============================================================================
# DATA LOADING AND CLEANING
# ============================================================================
def standardize_name(name, mapping):
    """Standardize a name using the provided mapping."""
    if pd.isna(name):
        return name
    name = str(name).strip()
    return mapping.get(name, name)

def clean_district_name(district):
    """Clean district name by removing special characters and standardizing."""
    if pd.isna(district):
        return district
    district = str(district).strip()
    # Remove trailing asterisks or special chars
    district = re.sub(r'\s*\*+$', '', district)
    district = re.sub(r'\s+', ' ', district)
    return district

def load_all_data():
    """Load all UIDAI data files with name standardization."""
    print("Loading enrolment data...")
    enrol_files = [
        'data/api_data_aadhar_enrolment/api_data_aadhar_enrolment_0_500000.csv',
        'data/api_data_aadhar_enrolment/api_data_aadhar_enrolment_500000_1000000.csv',
        'data/api_data_aadhar_enrolment/api_data_aadhar_enrolment_1000000_1006029.csv'
    ]
    enrol_df = pd.concat([pd.read_csv(f) for f in enrol_files], ignore_index=True)
    
    print("Loading biometric data...")
    bio_files = [
        'data/api_data_aadhar_biometric/api_data_aadhar_biometric_0_500000.csv',
        'data/api_data_aadhar_biometric/api_data_aadhar_biometric_500000_1000000.csv',
        'data/api_data_aadhar_biometric/api_data_aadhar_biometric_1000000_1500000.csv',
        'data/api_data_aadhar_biometric/api_data_aadhar_biometric_1500000_1861108.csv'
    ]
    bio_df = pd.concat([pd.read_csv(f) for f in bio_files], ignore_index=True)
    
    print("Loading demographic data...")
    demo_files = [
        'data/api_data_aadhar_demographic/api_data_aadhar_demographic_0_500000.csv',
        'data/api_data_aadhar_demographic/api_data_aadhar_demographic_500000_1000000.csv',
        'data/api_data_aadhar_demographic/api_data_aadhar_demographic_1000000_1500000.csv',
        'data/api_data_aadhar_demographic/api_data_aadhar_demographic_1500000_2000000.csv',
        'data/api_data_aadhar_demographic/api_data_aadhar_demographic_2000000_2071700.csv'
    ]
    demo_df = pd.concat([pd.read_csv(f) for f in demo_files], ignore_index=True)
    
    # Standardize names
    print("Standardizing state and district names...")
    for df in [enrol_df, bio_df, demo_df]:
        df['state'] = df['state'].apply(lambda x: standardize_name(x, STATE_NAME_MAPPING))
        df['district'] = df['district'].apply(clean_district_name)
    
    return enrol_df, bio_df, demo_df

def calculate_district_metrics(enrol_df, bio_df, demo_df):
    """Calculate metrics for each district."""
    print("Calculating metrics for all districts...")
    
    # Aggregate enrolments
    enrol_agg = enrol_df.groupby(['state', 'district']).agg({
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum'
    }).reset_index()
    enrol_agg['total_enrol'] = enrol_agg['age_0_5'] + enrol_agg['age_5_17'] + enrol_agg['age_18_greater']
    enrol_agg['child_enrol'] = enrol_agg['age_0_5'] + enrol_agg['age_5_17']
    enrol_agg['child_enrol_share'] = enrol_agg['child_enrol'] / enrol_agg['total_enrol'].replace(0, 1)
    
    # Aggregate biometric updates
    bio_agg = bio_df.groupby(['state', 'district']).agg({
        'bio_age_5_17': 'sum',
        'bio_age_17_': 'sum'
    }).reset_index()
    bio_agg.columns = ['state', 'district', 'bio_child', 'bio_adult']
    bio_agg['total_bio'] = bio_agg['bio_child'] + bio_agg['bio_adult']
    bio_agg['bio_child_share'] = bio_agg['bio_child'] / bio_agg['total_bio'].replace(0, 1)
    
    # Aggregate demographic updates
    demo_agg = demo_df.groupby(['state', 'district']).agg({
        'demo_age_5_17': 'sum',
        'demo_age_17_': 'sum'
    }).reset_index()
    demo_agg.columns = ['state', 'district', 'demo_child', 'demo_adult']
    demo_agg['total_demo'] = demo_agg['demo_child'] + demo_agg['demo_adult']
    demo_agg['demo_child_share'] = demo_agg['demo_child'] / demo_agg['total_demo'].replace(0, 1)
    
    # Merge all data - use outer join to include ALL districts
    merged = enrol_agg.merge(bio_agg, on=['state', 'district'], how='outer')
    merged = merged.merge(demo_agg, on=['state', 'district'], how='outer')
    merged = merged.fillna(0)
    
    # Calculate combined metrics
    merged['total_updates'] = merged['total_bio'] + merged['total_demo']
    merged['child_updates'] = merged['bio_child'] + merged['demo_child']
    merged['adult_updates'] = merged['bio_adult'] + merged['demo_adult']
    
    # Child update share (within updates)
    merged['child_update_share'] = merged['child_updates'] / merged['total_updates'].replace(0, 1)
    
    # BIOMETRIC child share is the key metric - this captures school-based drives
    # Use biometric child share as the primary indicator (higher = better)
    merged['bio_child_share'] = merged['bio_child'] / merged['total_bio'].replace(0, 1)
    
    # Child attention gap: biometric child share - 0.5 (parity benchmark)
    # Positive = more children than adults in biometric updates
    # Negative = fewer children than adults  
    merged['child_gap'] = merged['bio_child_share'] - 0.5
    
    # For districts without biometric data, use demographic child share
    mask_no_bio = merged['total_bio'] == 0
    merged.loc[mask_no_bio, 'child_gap'] = merged.loc[mask_no_bio, 'demo_child_share'] - 0.5
    
    # For districts with no update data at all, use enrolment child share
    mask_no_updates = (merged['total_bio'] == 0) & (merged['total_demo'] == 0)
    merged.loc[mask_no_updates, 'child_gap'] = merged.loc[mask_no_updates, 'child_enrol_share'] - 0.5
    
    print(f"Calculated metrics for {len(merged)} districts")
    return merged

def get_coordinates(state, district):
    """Get coordinates for a district."""
    # Check exact state-district match
    key = (state, district)
    if key in DISTRICT_COORDS:
        return DISTRICT_COORDS[key]
    
    # Check just district name in DISTRICT_COORDS
    for (s, d), coords in DISTRICT_COORDS.items():
        if d.lower() == district.lower():
            return coords
    
    # Fall back to state centroid with jitter
    if state in STATE_COORDS:
        base_lat, base_lng = STATE_COORDS[state]
        np.random.seed(hash(f"{state}_{district}") % 2**32)
        lat_offset = np.random.uniform(-1.0, 1.0)
        lng_offset = np.random.uniform(-1.0, 1.0)
        return (base_lat + lat_offset, base_lng + lng_offset)
    
    return None

def get_gap_color(gap):
    """Get color based on child attention gap."""
    if gap < -0.3:
        return 'red'  # Critical
    elif gap < -0.1:
        return 'orange'  # Severe  
    elif gap < 0.1:
        return 'yellow'  # Moderate
    else:
        return 'green'  # Good

def get_gap_category(gap):
    """Get gap category label."""
    if gap < -0.3:
        return 'Critical'
    elif gap < -0.1:
        return 'Severe'
    elif gap < 0.1:
        return 'Moderate'
    else:
        return 'Good'

def create_interactive_map(district_data):
    """Create interactive folium map."""
    print("Creating interactive map...")
    
    # Create base map
    india_map = folium.Map(
        location=[22.5, 82.5],
        zoom_start=5,
        tiles='cartodbpositron'
    )
    
    # Count categories
    critical_count = len(district_data[district_data['child_gap'] < -0.3])
    severe_count = len(district_data[(district_data['child_gap'] >= -0.3) & (district_data['child_gap'] < -0.1)])
    moderate_count = len(district_data[(district_data['child_gap'] >= -0.1) & (district_data['child_gap'] < 0.1)])
    good_count = len(district_data[district_data['child_gap'] >= 0.1])
    
    # Add legend
    legend_html = f'''
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; 
                background-color: white; padding: 15px; border-radius: 8px;
                border: 2px solid #333; font-family: Arial; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
        <b style="font-size: 14px;">Child Attention Gap</b><br>
        <small>(Biometric Child Share - 50%)</small><br><br>
        <span style="color:red; font-size: 18px;">●</span> Critical (&lt; -0.3): <b>{critical_count}</b><br>
        <span style="color:orange; font-size: 18px;">●</span> Severe (-0.3 to -0.1): <b>{severe_count}</b><br>
        <span style="color:yellow; font-size: 18px;">●</span> Moderate (-0.1 to 0.1): <b>{moderate_count}</b><br>
        <span style="color:green; font-size: 18px;">●</span> Good (&gt; 0.1): <b>{good_count}</b><br>
        <hr>
        <small>Total Districts: <b>{len(district_data)}</b></small>
    </div>
    '''
    india_map.get_root().html.add_child(folium.Element(legend_html))
    
    # Add title
    title_html = '''
    <div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%); 
                z-index: 1000; background-color: white; padding: 10px 25px; 
                border-radius: 8px; border: 2px solid #333; font-family: Arial;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.3);">
        <h3 style="margin: 0; color: #333;">UIDAI District-Level Child Attention Analysis</h3>
        <small style="color: #666;">All 1,132 Districts | Biometric Update Patterns | UIDAI Datathon 2026</small>
    </div>
    '''
    india_map.get_root().html.add_child(folium.Element(title_html))
    
    # Create feature groups
    critical_group = folium.FeatureGroup(name=f'Critical ({critical_count})')
    severe_group = folium.FeatureGroup(name=f'Severe ({severe_count})')
    moderate_group = folium.FeatureGroup(name=f'Moderate ({moderate_count})')
    good_group = folium.FeatureGroup(name=f'Good ({good_count})')
    
    # Add markers
    districts_added = 0
    for _, row in district_data.iterrows():
        coords = get_coordinates(row['state'], row['district'])
        if coords is None:
            continue
        
        lat, lng = coords
        gap = row['child_gap']
        color = get_gap_color(gap)
        category = get_gap_category(gap)
        
        # Scale radius
        total_activity = max(1, row['total_enrol'] + row['total_updates'])
        radius = max(4, min(12, 4 + np.log10(total_activity) * 1.5))
        
        # Create popup
        popup_html = f'''
        <div style="width:250px; font-family: Arial;">
            <h4 style="margin: 0 0 10px 0; color: #333;">{row['district']}</h4>
            <b>State:</b> {row['state']}<br>
            <hr style="margin: 5px 0;">
            <b>Enrolments:</b> {int(row['total_enrol']):,}<br>
            <b>Biometric Updates:</b> {int(row['total_bio']):,}<br>
            <b>Demographic Updates:</b> {int(row['total_demo']):,}<br>
            <hr style="margin: 5px 0;">
            <b>Bio Child Share:</b> {row['bio_child_share']:.1%}<br>
            <b>Demo Child Share:</b> {row['demo_child_share']:.1%}<br>
            <b>Child Gap:</b> <span style="color:{color}; font-weight: bold;">
                {'+' if gap > 0 else ''}{gap:.3f} ({category})</span>
        </div>
        '''
        
        marker = folium.CircleMarker(
            location=[lat, lng],
            radius=radius,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=1,
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"{row['district']}, {row['state']}: {gap:+.3f}"
        )
        
        if gap < -0.3:
            marker.add_to(critical_group)
        elif gap < -0.1:
            marker.add_to(severe_group)
        elif gap < 0.1:
            marker.add_to(moderate_group)
        else:
            marker.add_to(good_group)
        
        districts_added += 1
    
    # Add groups to map
    critical_group.add_to(india_map)
    severe_group.add_to(india_map)
    moderate_group.add_to(india_map)
    good_group.add_to(india_map)
    
    # Add controls
    folium.LayerControl(collapsed=False).add_to(india_map)
    plugins.Fullscreen().add_to(india_map)
    
    print(f"Added {districts_added} districts to map")
    return india_map

def main():
    """Main execution."""
    print("=" * 60)
    print("UIDAI ENHANCED DISTRICT MAP GENERATOR")
    print("=" * 60)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Load data
    enrol_df, bio_df, demo_df = load_all_data()
    print(f"Loaded {len(enrol_df):,} enrolment records")
    print(f"Loaded {len(bio_df):,} biometric records")
    print(f"Loaded {len(demo_df):,} demographic records")
    
    # Calculate metrics
    district_data = calculate_district_metrics(enrol_df, bio_df, demo_df)
    
    # Summary
    print("\n" + "=" * 40)
    print("SUMMARY STATISTICS")
    print("=" * 40)
    print(f"Total districts: {len(district_data)}")
    print(f"Critical (<-0.3): {len(district_data[district_data['child_gap'] < -0.3])}")
    print(f"Severe (-0.3 to -0.1): {len(district_data[(district_data['child_gap'] >= -0.3) & (district_data['child_gap'] < -0.1)])}")
    print(f"Moderate (-0.1 to 0.1): {len(district_data[(district_data['child_gap'] >= -0.1) & (district_data['child_gap'] < 0.1)])}")
    print(f"Good (>0.1): {len(district_data[district_data['child_gap'] >= 0.1])}")
    
    # Create map
    india_map = create_interactive_map(district_data)
    
    # Save
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    india_map.save(output_path)
    print(f"\n✓ Map saved to: {output_path}")
    
    csv_path = os.path.join(OUTPUT_DIR, "district_child_gap_data.csv")
    district_data.to_csv(csv_path, index=False)
    print(f"✓ Data saved to: {csv_path}")
    
    print("\n" + "=" * 60)
    print("COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    main()
