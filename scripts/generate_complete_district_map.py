#!/usr/bin/env python3
"""
UIDAI Data Hackathon 2026 - COMPLETE DISTRICT MAP GENERATOR
Creates interactive folium map with ALL districts from the dataset.
"""

import pandas as pd
import folium
from folium import plugins
import os
import numpy as np

# ============================================================================
# CONFIGURATION
# ============================================================================
OUTPUT_DIR = "outputs/interactive_maps"
OUTPUT_FILE = "india_child_gap_map_complete.html"

# District coordinates (comprehensive list for India)
# We'll use approximate coordinates for districts or state centroids as fallback
DISTRICT_COORDS = {
    # Major districts with known coordinates
    'Bengaluru Urban': (12.9716, 77.5946),
    'Mumbai': (19.0760, 72.8777),
    'Mumbai Suburban': (19.1136, 72.8697),
    'Delhi': (28.7041, 77.1025),
    'Kolkata': (22.5726, 88.3639),
    'Chennai': (13.0827, 80.2707),
    'Hyderabad': (17.3850, 78.4867),
    'Pune': (18.5204, 73.8567),
    'Ahmedabad': (23.0225, 72.5714),
    'Jaipur': (26.9124, 75.7873),
    'Lucknow': (26.8467, 80.9462),
    'Kanpur Nagar': (26.4499, 80.3319),
    'Nagpur': (21.1458, 79.0882),
    'Patna': (25.5941, 85.1376),
    'Indore': (22.7196, 75.8577),
    'Bhopal': (23.2599, 77.4126),
    'Thiruvananthapuram': (8.5241, 76.9366),
    'Kochi': (9.9312, 76.2673),
    'Ernakulam': (9.9816, 76.2999),
    'Coimbatore': (11.0168, 76.9558),
    'Visakhapatnam': (17.6868, 83.2185),
    'Guwahati': (26.1445, 91.7362),
    'Surat': (21.1702, 72.8311),
    'Vadodara': (22.3072, 73.1812),
}

# State centroids for fallback
STATE_COORDS = {
    'Andaman And Nicobar Islands': (11.7401, 92.6586),
    'Andhra Pradesh': (15.9129, 79.74),
    'Arunachal Pradesh': (28.218, 94.7278),
    'Assam': (26.2006, 92.9376),
    'Bihar': (25.0961, 85.3131),
    'Chandigarh': (30.7333, 76.7794),
    'Chhattisgarh': (21.2787, 81.8661),
    'Chhatisgarh': (21.2787, 81.8661),
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

# ============================================================================
# DATA LOADING
# ============================================================================
def load_all_data():
    """Load all UIDAI data files."""
    print("Loading enrolment data...")
    enrol_files = [
        'data/api_data_aadhar_enrolment/api_data_aadhar_enrolment_0_500000.csv',
        'data/api_data_aadhar_enrolment/api_data_aadhar_enrolment_500000_1000000.csv',
        'data/api_data_aadhar_enrolment/api_data_aadhar_enrolment_1000000_1006029.csv'
    ]
    
    enrol_dfs = []
    for f in enrol_files:
        df = pd.read_csv(f)
        enrol_dfs.append(df)
    enrol_df = pd.concat(enrol_dfs, ignore_index=True)
    
    print("Loading biometric data...")
    bio_files = [
        'data/api_data_aadhar_biometric/api_data_aadhar_biometric_0_500000.csv',
        'data/api_data_aadhar_biometric/api_data_aadhar_biometric_500000_1000000.csv',
        'data/api_data_aadhar_biometric/api_data_aadhar_biometric_1000000_1500000.csv',
        'data/api_data_aadhar_biometric/api_data_aadhar_biometric_1500000_1861108.csv'
    ]
    
    bio_dfs = []
    for f in bio_files:
        df = pd.read_csv(f)
        bio_dfs.append(df)
    bio_df = pd.concat(bio_dfs, ignore_index=True)
    
    print("Loading demographic data...")
    demo_files = [
        'data/api_data_aadhar_demographic/api_data_aadhar_demographic_0_500000.csv',
        'data/api_data_aadhar_demographic/api_data_aadhar_demographic_500000_1000000.csv',
        'data/api_data_aadhar_demographic/api_data_aadhar_demographic_1000000_1500000.csv',
        'data/api_data_aadhar_demographic/api_data_aadhar_demographic_1500000_2000000.csv',
        'data/api_data_aadhar_demographic/api_data_aadhar_demographic_2000000_2071700.csv'
    ]
    
    demo_dfs = []
    for f in demo_files:
        df = pd.read_csv(f)
        demo_dfs.append(df)
    demo_df = pd.concat(demo_dfs, ignore_index=True)
    
    return enrol_df, bio_df, demo_df

def calculate_district_metrics(enrol_df, bio_df, demo_df):
    """Calculate child attention gap and update intensity for each district."""
    print("Calculating metrics for all districts...")
    
    # Aggregate enrolments by state-district
    enrol_agg = enrol_df.groupby(['state', 'district']).agg({
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum'
    }).reset_index()
    enrol_agg['total_enrol'] = enrol_agg['age_0_5'] + enrol_agg['age_5_17'] + enrol_agg['age_18_greater']
    enrol_agg['child_enrol_share'] = (enrol_agg['age_0_5'] + enrol_agg['age_5_17']) / enrol_agg['total_enrol'].replace(0, 1)
    
    # Aggregate biometric updates by state-district
    bio_agg = bio_df.groupby(['state', 'district']).agg({
        'bio_age_5_17': 'sum',
        'bio_age_17_': 'sum'
    }).reset_index()
    bio_agg.columns = ['state', 'district', 'bio_5_17', 'bio_17_plus']
    bio_agg['total_bio'] = bio_agg['bio_5_17'] + bio_agg['bio_17_plus']
    
    # Aggregate demographic updates by state-district
    demo_agg = demo_df.groupby(['state', 'district']).agg({
        'demo_age_5_17': 'sum',
        'demo_age_17_': 'sum'
    }).reset_index()
    demo_agg.columns = ['state', 'district', 'demo_5_17', 'demo_17_plus']
    demo_agg['total_demo'] = demo_agg['demo_5_17'] + demo_agg['demo_17_plus']
    
    # Merge all data
    merged = enrol_agg.merge(bio_agg, on=['state', 'district'], how='outer')
    merged = merged.merge(demo_agg, on=['state', 'district'], how='outer')
    merged = merged.fillna(0)
    
    # Calculate total updates
    merged['total_updates'] = merged['total_bio'] + merged['total_demo']
    merged['child_updates'] = merged['bio_5_17'] + merged['demo_5_17']
    
    # Calculate child update share
    merged['child_update_share'] = merged['child_updates'] / merged['total_updates'].replace(0, 1)
    
    # Calculate child attention gap (update share - enrolment share)
    # Negative = under-served, Positive = over-served
    merged['child_gap'] = merged['child_update_share'] - merged['child_enrol_share']
    
    # Calculate update intensity
    merged['update_intensity'] = merged['total_updates'] / merged['total_enrol'].replace(0, 1)
    
    print(f"Calculated metrics for {len(merged)} districts")
    return merged

def get_coordinates(state, district):
    """Get coordinates for a district, falling back to state centroid."""
    # Check district-specific coordinates
    if district in DISTRICT_COORDS:
        return DISTRICT_COORDS[district]
    
    # Fall back to state centroid with slight jitter for districts in same state
    if state in STATE_COORDS:
        base_lat, base_lng = STATE_COORDS[state]
        # Add small random offset to prevent overlapping
        np.random.seed(hash(f"{state}_{district}") % 2**32)
        lat_offset = np.random.uniform(-0.5, 0.5)
        lng_offset = np.random.uniform(-0.5, 0.5)
        return (base_lat + lat_offset, base_lng + lng_offset)
    
    return None

def get_gap_color(gap):
    """Get color based on child attention gap value."""
    if gap < -0.5:
        return 'red'  # Critical
    elif gap < -0.2:
        return 'orange'  # Severe
    elif gap < 0:
        return 'yellow'  # Moderate
    else:
        return 'green'  # Good

def get_gap_category(gap):
    """Get gap category label."""
    if gap < -0.5:
        return 'Critical'
    elif gap < -0.2:
        return 'Severe'
    elif gap < 0:
        return 'Moderate'
    else:
        return 'Good'

def create_interactive_map(district_data):
    """Create interactive folium map with all districts."""
    print("Creating interactive map...")
    
    # Create base map
    india_map = folium.Map(
        location=[20.5937, 78.9629],
        zoom_start=5,
        tiles='cartodbpositron'
    )
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; 
                background-color: white; padding: 15px; border-radius: 5px;
                border: 2px solid grey; font-family: Arial;">
        <b style="font-size: 14px;">Child Attention Gap</b><br>
        <span style="color:red; font-size: 20px;">●</span> Critical (&lt; -0.5)<br>
        <span style="color:orange; font-size: 20px;">●</span> Severe (-0.5 to -0.2)<br>
        <span style="color:yellow; font-size: 20px;">●</span> Moderate (-0.2 to 0)<br>
        <span style="color:green; font-size: 20px;">●</span> Good (&gt; 0)<br>
        <hr>
        <small>Total Districts: {}</small>
    </div>
    '''.format(len(district_data))
    india_map.get_root().html.add_child(folium.Element(legend_html))
    
    # Add title
    title_html = '''
    <div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%); 
                z-index: 1000; background-color: white; padding: 10px 20px; 
                border-radius: 5px; border: 2px solid #333; font-family: Arial;">
        <h3 style="margin: 0;">UIDAI Child Attention Gap by District</h3>
        <small>All 1,070 State-District Pairs</small>
    </div>
    '''
    india_map.get_root().html.add_child(folium.Element(title_html))
    
    # Create feature groups for filtering
    critical_group = folium.FeatureGroup(name='Critical (< -0.5)')
    severe_group = folium.FeatureGroup(name='Severe (-0.5 to -0.2)')
    moderate_group = folium.FeatureGroup(name='Moderate (-0.2 to 0)')
    good_group = folium.FeatureGroup(name='Good (> 0)')
    
    # Add markers for each district
    districts_added = 0
    for _, row in district_data.iterrows():
        coords = get_coordinates(row['state'], row['district'])
        if coords is None:
            continue
        
        lat, lng = coords
        gap = row['child_gap']
        color = get_gap_color(gap)
        category = get_gap_category(gap)
        
        # Scale radius based on total enrolments (log scale)
        radius = max(3, min(15, 3 + np.log10(max(1, row['total_enrol']))))
        
        # Create popup content
        popup_html = f'''
        <div style="width:220px; font-family: Arial;">
            <h4 style="margin: 0 0 10px 0;">{row['district']}</h4>
            <b>State:</b> {row['state']}<br>
            <b>Enrolments:</b> {int(row['total_enrol']):,}<br>
            <b>Updates:</b> {int(row['total_updates']):,}<br>
            <b>Child Gap:</b> <span style="color:{color}; font-weight: bold;">
                {'+' if gap > 0 else ''}{gap:.3f} ({category})</span><br>
            <b>Child Enrol Share:</b> {row['child_enrol_share']:.1%}<br>
            <b>Child Update Share:</b> {row['child_update_share']:.1%}
        </div>
        '''
        
        marker = folium.CircleMarker(
            location=[lat, lng],
            radius=radius,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{row['district']}: Gap {gap:.3f}"
        )
        
        # Add to appropriate group
        if gap < -0.5:
            marker.add_to(critical_group)
        elif gap < -0.2:
            marker.add_to(severe_group)
        elif gap < 0:
            marker.add_to(moderate_group)
        else:
            marker.add_to(good_group)
        
        districts_added += 1
    
    # Add groups to map
    critical_group.add_to(india_map)
    severe_group.add_to(india_map)
    moderate_group.add_to(india_map)
    good_group.add_to(india_map)
    
    # Add layer control
    folium.LayerControl().add_to(india_map)
    
    # Add fullscreen option
    plugins.Fullscreen().add_to(india_map)
    
    # Add search functionality
    plugins.Search(
        layer=critical_group,
        search_label='tooltip',
        search_zoom=10,
        position='topright'
    ).add_to(india_map)
    
    print(f"Added {districts_added} districts to map")
    return india_map

def main():
    """Main execution."""
    print("=" * 60)
    print("UIDAI COMPLETE DISTRICT MAP GENERATOR")
    print("=" * 60)
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Load all data
    enrol_df, bio_df, demo_df = load_all_data()
    print(f"Loaded {len(enrol_df)} enrolment records")
    print(f"Loaded {len(bio_df)} biometric records")
    print(f"Loaded {len(demo_df)} demographic records")
    
    # Calculate metrics
    district_data = calculate_district_metrics(enrol_df, bio_df, demo_df)
    
    # Print summary statistics
    print("\n" + "=" * 40)
    print("SUMMARY STATISTICS")
    print("=" * 40)
    print(f"Total districts: {len(district_data)}")
    print(f"Critical (<-0.5): {len(district_data[district_data['child_gap'] < -0.5])}")
    print(f"Severe (-0.5 to -0.2): {len(district_data[(district_data['child_gap'] >= -0.5) & (district_data['child_gap'] < -0.2)])}")
    print(f"Moderate (-0.2 to 0): {len(district_data[(district_data['child_gap'] >= -0.2) & (district_data['child_gap'] < 0)])}")
    print(f"Good (>0): {len(district_data[district_data['child_gap'] >= 0])}")
    
    # Create map
    india_map = create_interactive_map(district_data)
    
    # Save map
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    india_map.save(output_path)
    print(f"\n✓ Map saved to: {output_path}")
    
    # Also save the district data as CSV for reference
    csv_path = os.path.join(OUTPUT_DIR, "district_child_gap_data.csv")
    district_data.to_csv(csv_path, index=False)
    print(f"✓ Data saved to: {csv_path}")
    
    print("\n" + "=" * 60)
    print("COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    main()
