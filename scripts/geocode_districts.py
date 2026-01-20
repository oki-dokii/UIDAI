#!/usr/bin/env python3
"""
UIDAI Data Hackathon 2026 - DISTRICT GEOCODING SCRIPT
Geocodes all districts from the dataset using geopy/Nominatim.
Creates a comprehensive coordinates file for accurate map generation.
"""

import pandas as pd
import json
import os
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# ============================================================================
# CONFIGURATION
# ============================================================================
DATA_DIR = "data"
OUTPUT_FILE = os.path.join(DATA_DIR, "all_district_coordinates.json")
ENROL_DIR = os.path.join(DATA_DIR, "api_data_aadhar_enrolment")

# Rate limiting - Nominatim requires 1 request per second max
RATE_LIMIT_SECONDS = 1.1

# ============================================================================
# STATE NAME STANDARDIZATION
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
    'Chattisgarh': 'Chhattisgarh',
    'Chhatisgarh': 'Chhattisgarh',
    'NCT of Delhi': 'Delhi',
    'NCT OF DELHI': 'Delhi',
    'New Delhi': 'Delhi',
    'Pondicherry': 'Puducherry',
    'Uttaranchal': 'Uttarakhand',
}

# State centroids as fallback
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


def standardize_state(state):
    """Standardize state name."""
    if pd.isna(state):
        return state
    state = str(state).strip()
    return STATE_NAME_MAPPING.get(state, state)


def clean_district(district):
    """Clean district name."""
    if pd.isna(district):
        return district
    district = str(district).strip()
    # Remove asterisks and extra whitespace
    import re
    district = re.sub(r'\s*\*+$', '', district)
    district = re.sub(r'\s+', ' ', district)
    return district


def load_all_districts():
    """Load all unique state-district pairs from enrolment data."""
    print("Loading enrolment data to get all districts...")
    
    all_districts = set()
    
    for filename in os.listdir(ENROL_DIR):
        if filename.endswith('.csv'):
            filepath = os.path.join(ENROL_DIR, filename)
            df = pd.read_csv(filepath)
            
            for _, row in df.iterrows():
                state = standardize_state(row['state'])
                district = clean_district(row['district'])
                if state and district:
                    all_districts.add((state, district))
    
    print(f"Found {len(all_districts)} unique state-district pairs")
    return sorted(list(all_districts))


def geocode_district(geolocator, district, state, retries=3):
    """Geocode a single district with multiple search strategies."""
    
    # Search strategies in order of preference
    search_queries = [
        f"{district} District, {state}, India",
        f"{district}, {state}, India",
        f"{district} city, {state}, India",
        f"{district}, India",
    ]
    
    for query in search_queries:
        for attempt in range(retries):
            try:
                location = geolocator.geocode(query, timeout=10)
                if location:
                    # Verify it's in India (rough bounds check)
                    lat, lon = location.latitude, location.longitude
                    if 6.0 <= lat <= 37.0 and 68.0 <= lon <= 98.0:
                        return (round(lat, 4), round(lon, 4))
            except GeocoderTimedOut:
                print(f"    Timeout for '{query}' (attempt {attempt + 1}/{retries})")
                time.sleep(2)
            except GeocoderServiceError as e:
                print(f"    Service error for '{query}': {e}")
                time.sleep(2)
            except Exception as e:
                print(f"    Error for '{query}': {e}")
                break
    
    return None


def geocode_all_districts(districts):
    """Geocode all districts with progress tracking."""
    
    # Initialize geocoder with a user agent
    geolocator = Nominatim(user_agent="uidai_hackathon_2026_district_mapper")
    
    coordinates = {}
    success_count = 0
    fail_count = 0
    
    # Load existing coordinates if available (to resume)
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as f:
            coordinates = json.load(f)
        print(f"Loaded {len(coordinates)} existing coordinates")
    
    total = len(districts)
    
    for i, (state, district) in enumerate(districts):
        key = f"{state}|{district}"
        
        # Skip if already geocoded
        if key in coordinates:
            success_count += 1
            continue
        
        print(f"[{i+1}/{total}] Geocoding: {district}, {state}")
        
        coords = geocode_district(geolocator, district, state)
        
        if coords:
            coordinates[key] = list(coords)
            success_count += 1
            print(f"    ✓ Found: {coords}")
        else:
            # Use state centroid as fallback
            if state in STATE_COORDS:
                fallback = STATE_COORDS[state]
                coordinates[key] = list(fallback)
                print(f"    ⚠ Fallback to state centroid: {fallback}")
            else:
                print(f"    ✗ Failed - no fallback available")
            fail_count += 1
        
        # Save progress every 50 districts
        if (i + 1) % 50 == 0:
            with open(OUTPUT_FILE, 'w') as f:
                json.dump(coordinates, f, indent=2)
            print(f"    [Progress saved: {len(coordinates)} districts]")
        
        # Rate limiting
        time.sleep(RATE_LIMIT_SECONDS)
    
    return coordinates, success_count, fail_count


def main():
    """Main execution."""
    print("=" * 60)
    print("UIDAI DISTRICT GEOCODING SCRIPT")
    print("=" * 60)
    print()
    
    # Load districts
    districts = load_all_districts()
    
    print(f"\nGeocoding {len(districts)} districts...")
    print(f"Estimated time: ~{len(districts) * RATE_LIMIT_SECONDS / 60:.0f} minutes")
    print("(Progress will be saved incrementally)")
    print()
    
    # Geocode
    coordinates, success, fail = geocode_all_districts(districts)
    
    # Save final results
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(coordinates, f, indent=2)
    
    print()
    print("=" * 60)
    print("GEOCODING COMPLETE")
    print("=" * 60)
    print(f"Total districts: {len(districts)}")
    print(f"Successfully geocoded: {success}")
    print(f"Used state fallback: {fail}")
    print(f"Coordinates saved to: {OUTPUT_FILE}")
    print()


if __name__ == "__main__":
    main()
