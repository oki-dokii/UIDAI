#!/usr/bin/env python3
"""
UIDAI Data Hackathon 2026 - Shared Data Utilities
Common data cleaning, normalization, and validation functions.

This module provides:
- Comprehensive state name normalization (30+ variants → 36 standard names)
- Invalid entry filtering (districts/pincodes mistakenly in state column)
- Deduplication utilities
- Safe merge functions that don't create false data
"""

import os
import re
import numpy as np
import pandas as pd

# ============================================================================
# CONFIGURATION - Use relative paths from script location
# ============================================================================
def get_base_dir():
    """Get the base directory (where this script is located)."""
    return os.path.dirname(os.path.abspath(__file__))

def get_data_dirs():
    """Get data directories relative to script location."""
    # scripts/utils/ -> scripts/ -> UIDAI/UIDAI/ (root)
    script_dir = get_base_dir()
    project_root = os.path.dirname(os.path.dirname(script_dir))
    data_root = os.path.join(project_root, "data")
    
    return {
        "biometric": os.path.join(data_root, "api_data_aadhar_biometric"),
        "demographic": os.path.join(data_root, "api_data_aadhar_demographic"),
        "enrolment": os.path.join(data_root, "api_data_aadhar_enrolment"),
    }

# ============================================================================
# COMPREHENSIVE STATE NAME NORMALIZATION
# ============================================================================

# Valid Indian states and UTs (36 total as of 2024)
VALID_STATES = {
    "Andaman And Nicobar Islands",
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chandigarh",
    "Chhattisgarh",
    "Dadra And Nagar Haveli And Daman And Diu",  # Merged UT since 2020
    "Delhi",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jammu And Kashmir",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Ladakh",
    "Lakshadweep",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Puducherry",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
}

# Comprehensive state name mapping - handles 30+ variations
STATE_NAME_MAP = {
    # Andaman & Nicobar Islands variations
    "andaman & nicobar islands": "Andaman And Nicobar Islands",
    "andaman and nicobar islands": "Andaman And Nicobar Islands",
    "a & n islands": "Andaman And Nicobar Islands",
    "a&n islands": "Andaman And Nicobar Islands",
    
    # Chhattisgarh variations
    "chattisgarh": "Chhattisgarh",
    "chhatisgarh": "Chhattisgarh",
    "chatisgarh": "Chhattisgarh",
    
    # Dadra & Nagar Haveli and Daman & Diu (merged UT)
    "dadra & nagar haveli": "Dadra And Nagar Haveli And Daman And Diu",
    "dadra and nagar haveli": "Dadra And Nagar Haveli And Daman And Diu",
    "daman & diu": "Dadra And Nagar Haveli And Daman And Diu",
    "daman and diu": "Dadra And Nagar Haveli And Daman And Diu",
    "dadra and nagar haveli and daman and diu": "Dadra And Nagar Haveli And Daman And Diu",
    "the dadra and nagar haveli and daman and diu": "Dadra And Nagar Haveli And Daman And Diu",
    "d&nh": "Dadra And Nagar Haveli And Daman And Diu",
    "d & d": "Dadra And Nagar Haveli And Daman And Diu",
    
    # Jammu & Kashmir variations
    "j & k": "Jammu And Kashmir",
    "j&k": "Jammu And Kashmir",
    "jammu & kashmir": "Jammu And Kashmir",
    "jammu and kashmir": "Jammu And Kashmir",
    
    # Odisha/Orissa
    "orissa": "Odisha",
    
    # Puducherry/Pondicherry
    "pondicherry": "Puducherry",
    
    # Tamil Nadu variations
    "tamilnadu": "Tamil Nadu",
    "tamil  nadu": "Tamil Nadu",  # Double space
    
    # Telangana variations
    "telengana": "Telangana",
    "telanagana": "Telangana",
    
    # Uttarakhand variations
    "uttaranchal": "Uttarakhand",
    "uttarkhand": "Uttarakhand",
    
    # West Bengal variations
    "west  bengal": "West Bengal",  # Double space
    "westbengal": "West Bengal",
}

# Known invalid entries (districts, cities, or pincodes mistakenly in state column)
INVALID_STATE_ENTRIES = {
    "100000",  # Pincode
    "balanagar",
    "darbhanga",
    "jaipur",
    "nagpur",
    "madanapalle",
    "puttenahalli",
    "raja annamalai puram",
    # Add more as discovered
}


def normalize_state_name(state_name):
    """
    Normalize a state name to standard format.
    
    Args:
        state_name: Raw state name string
        
    Returns:
        Normalized state name or None if invalid
    """
    if pd.isna(state_name):
        return None
    
    # Convert to string and clean
    cleaned = str(state_name).strip()
    
    # Check if numeric (likely a pincode)
    if cleaned.isdigit():
        return None
    
    # Normalize for lookup: lowercase, collapse multiple spaces
    lookup_key = re.sub(r'\s+', ' ', cleaned.lower().strip())
    
    # Check if it's a known invalid entry
    if lookup_key in INVALID_STATE_ENTRIES:
        return None
    
    # Try direct mapping
    if lookup_key in STATE_NAME_MAP:
        return STATE_NAME_MAP[lookup_key]
    
    # Try title case and check if valid
    title_case = cleaned.title()
    # Fix common title case issues
    title_case = title_case.replace(" And ", " And ")
    title_case = re.sub(r'\s+', ' ', title_case)  # Collapse spaces
    
    if title_case in VALID_STATES:
        return title_case
    
    # If still not found, check if it's close to any valid state
    # This catches case variations like "WEST BENGAL" → "West Bengal"
    for valid_state in VALID_STATES:
        if lookup_key == valid_state.lower():
            return valid_state
    
    # Return None for unknown/invalid entries
    return None


def normalize_district_name(district_name):
    """
    Normalize a district name to standard format.
    
    Args:
        district_name: Raw district name string
        
    Returns:
        Normalized district name
    """
    if pd.isna(district_name):
        return "Unknown"
    
    cleaned = str(district_name).strip()
    
    # Check if numeric (likely a pincode)
    if cleaned.isdigit():
        return "Unknown"
    
    # Title case and collapse spaces
    normalized = re.sub(r'\s+', ' ', cleaned.title().strip())
    
    return normalized if normalized else "Unknown"


# ============================================================================
# DATA DEDUPLICATION
# ============================================================================

def deduplicate_data(df, subset_cols=None, keep='first'):
    """
    Remove duplicate rows from a DataFrame.
    
    Args:
        df: Input DataFrame
        subset_cols: Columns to consider for identifying duplicates
                    If None, uses ['date', 'state', 'district', 'pincode']
        keep: Which duplicate to keep ('first', 'last', or False)
        
    Returns:
        DataFrame with duplicates removed and count of removed rows
    """
    if subset_cols is None:
        # Default columns for deduplication
        subset_cols = ['date', 'state', 'district']
        if 'pincode' in df.columns:
            subset_cols.append('pincode')
    
    # Filter to only columns that exist
    subset_cols = [c for c in subset_cols if c in df.columns]
    
    if not subset_cols:
        return df, 0
    
    original_len = len(df)
    df_deduped = df.drop_duplicates(subset=subset_cols, keep=keep)
    removed = original_len - len(df_deduped)
    
    return df_deduped, removed


# ============================================================================
# SAFE DATA MERGING
# ============================================================================

def safe_merge_datasets(dfs, merge_keys, how='outer', fill_strategy='drop'):
    """
    Merge multiple DataFrames with proper handling of missing data.
    
    Unlike naive fillna(0), this function:
    - Tracks which records came from which source
    - Optionally drops rows with no actual data (all zeros after merge)
    - Preserves the distinction between "no data" and "zero activity"
    
    Args:
        dfs: List of DataFrames to merge
        merge_keys: List of column names to merge on
        how: Merge type ('outer', 'inner', 'left', 'right')
        fill_strategy: How to handle NaN after merge
            - 'drop': Remove rows where ALL value columns are NaN
            - 'zero': Fill NaN with 0 (use with caution)
            - 'keep': Keep NaN values as-is
            
    Returns:
        Merged DataFrame with source tracking column
    """
    if not dfs:
        return pd.DataFrame()
    
    if len(dfs) == 1:
        return dfs[0].copy()
    
    # Start with first dataframe
    result = dfs[0].copy()
    result['_source_count'] = 1
    
    # Merge remaining dataframes
    for i, df in enumerate(dfs[1:], start=2):
        df_copy = df.copy()
        df_copy['_temp_source'] = 1
        
        result = result.merge(df_copy, on=merge_keys, how=how, suffixes=('', f'_src{i}'))
        
        # Update source count
        result['_source_count'] = result['_source_count'].fillna(0) + result['_temp_source'].fillna(0)
        result = result.drop(columns=['_temp_source'], errors='ignore')
    
    # Get numeric columns (excluding merge keys and source tracking)
    numeric_cols = result.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c not in merge_keys and c != '_source_count']
    
    if fill_strategy == 'drop':
        # Drop rows where ALL numeric columns are NaN
        mask = result[numeric_cols].notna().any(axis=1)
        result = result[mask]
        result[numeric_cols] = result[numeric_cols].fillna(0)
    elif fill_strategy == 'zero':
        result[numeric_cols] = result[numeric_cols].fillna(0)
    # 'keep' leaves NaN as-is
    
    return result


def filter_valid_activity(df, enrol_col='total_enrolments', update_col='total_updates'):
    """
    Filter to rows with actual activity (non-zero enrolments OR updates).
    
    This prevents the issue where outer joins + fillna(0) create rows 
    with total_enrolments=0 that break intensity calculations.
    
    Args:
        df: Input DataFrame
        enrol_col: Name of enrolment column
        update_col: Name of update column (or list of update columns)
        
    Returns:
        Filtered DataFrame
    """
    df = df.copy()
    
    # Handle update_col as string or list
    if isinstance(update_col, str):
        update_cols = [update_col]
    else:
        update_cols = list(update_col)
    
    # Filter to rows with actual activity
    has_enrol = (df[enrol_col] > 0) if enrol_col in df.columns else False
    has_update = False
    for col in update_cols:
        if col in df.columns:
            has_update = has_update | (df[col] > 0)
    
    if isinstance(has_enrol, bool) and not has_enrol:
        # enrol_col doesn't exist
        mask = has_update
    elif isinstance(has_update, bool) and not has_update:
        # No update cols exist
        mask = has_enrol
    else:
        mask = has_enrol | has_update
    
    return df[mask]


# ============================================================================
# DATA VALIDATION
# ============================================================================

def validate_data_quality(df, dataset_name="Dataset"):
    """
    Run data quality checks and print a summary.
    
    Args:
        df: DataFrame to validate
        dataset_name: Name for reporting
        
    Returns:
        Dictionary with validation results
    """
    results = {
        'name': dataset_name,
        'total_rows': len(df),
        'issues': []
    }
    
    # Check for duplicates
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        results['issues'].append(f"Contains {dup_count:,} duplicate rows")
    results['duplicate_rows'] = dup_count
    
    # Check state column
    if 'state' in df.columns:
        null_states = df['state'].isna().sum()
        if null_states > 0:
            results['issues'].append(f"{null_states:,} rows with null state")
        results['null_states'] = null_states
        
        # Check for invalid states
        unique_states = df['state'].dropna().unique()
        invalid_states = [s for s in unique_states if normalize_state_name(s) is None]
        if invalid_states:
            results['issues'].append(f"{len(invalid_states)} invalid state names found")
            results['invalid_states'] = invalid_states
    
    # Check numeric columns for negative values
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        neg_count = (df[col] < 0).sum()
        if neg_count > 0:
            results['issues'].append(f"Column '{col}' has {neg_count:,} negative values")
    
    # Print summary
    print(f"\n📊 Data Quality Report: {dataset_name}")
    print(f"   Total rows: {results['total_rows']:,}")
    
    if results['issues']:
        print(f"   ⚠️ Issues found ({len(results['issues'])}):")
        for issue in results['issues']:
            print(f"      - {issue}")
    else:
        print("   ✅ No issues found")
    
    return results


def preprocess_and_clean(df, dataset_name="Dataset", verbose=True):
    """
    Full preprocessing pipeline with all fixes applied.
    
    Args:
        df: Raw DataFrame
        dataset_name: Name for logging
        verbose: Whether to print progress
        
    Returns:
        Cleaned DataFrame
    """
    if verbose:
        print(f"\n🔧 Preprocessing {dataset_name}...")
        print(f"   Initial rows: {len(df):,}")
    
    df = df.copy()
    
    # 1. Parse dates
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day_of_week'] = df['date'].dt.day_name()
        
        # Drop rows with invalid dates
        invalid_dates = df['date'].isna().sum()
        if invalid_dates > 0:
            df = df[df['date'].notna()]
            if verbose:
                print(f"   Removed {invalid_dates:,} rows with invalid dates")
    
    # 2. Normalize state names
    if 'state' in df.columns:
        df['state_original'] = df['state']  # Keep original for debugging
        df['state'] = df['state'].apply(normalize_state_name)
        
        # Remove rows with invalid/unknown states
        invalid_states = df['state'].isna().sum()
        if invalid_states > 0:
            df = df[df['state'].notna()]
            if verbose:
                print(f"   Removed {invalid_states:,} rows with invalid states")
    
    # 3. Normalize district names
    if 'district' in df.columns:
        df['district'] = df['district'].apply(normalize_district_name)
    
    # 4. Deduplicate
    df, dup_count = deduplicate_data(df)
    if verbose and dup_count > 0:
        print(f"   Removed {dup_count:,} duplicate rows")
    
    if verbose:
        print(f"   Final rows: {len(df):,}")
    
    return df
