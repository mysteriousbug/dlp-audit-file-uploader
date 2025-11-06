"""
ITAM Name Mapping Script

This script performs the following tasks:
1. Reads the output from map_environments.py (with Source ITAM and Destination ITAM columns)
2. Reads itam.xlsx which contains ITAM to Name mappings
3. Extracts all ITAM values from Source ITAM and Destination ITAM columns
4. Looks up each ITAM in itam.xlsx to get its name
5. Creates two new columns:
   - Source ITAM Name: {"itam1":"name1","itam2":"name2"}
   - Destination ITAM Name: {"itam1":"name1","itam2":"name2"}

Optimized for performance with large datasets (17,000+ records)

Usage:
    python map_itam_names.py

Requirements:
    - pandas
    - openpyxl

Install requirements:
    pip install pandas openpyxl
"""

import pandas as pd
import ast
from datetime import datetime
import os

# Configuration
INPUT_FILE = 'nfast_rules_with_environments.xlsx'  # Output from map_environments.py
ITAM_FILE = 'itam.xlsx'  # ITAM lookup file
OUTPUT_FILE = 'nfast_rules_with_itam_names.xlsx'  # Final output file

# Create backup flag
CREATE_BACKUP = True


def parse_dict_string(s):
    """
    Parse string representation of dictionary into actual dictionary
    
    Args:
        s: String representation of a dictionary
        
    Returns:
        dict: Parsed dictionary or empty dict if parsing fails
    """
    if pd.isna(s) or s == '' or s == '{}':
        return {}
    
    # If it's already a dict, return it
    if isinstance(s, dict):
        return s
    
    try:
        # Try to evaluate as Python literal
        result = ast.literal_eval(str(s))
        if isinstance(result, dict):
            return result
        else:
            return {}
    except:
        # If evaluation fails, return empty dict
        return {}


def extract_itam_values(itam_dict):
    """
    Extract all ITAM values from a dictionary
    
    Args:
        itam_dict: Dictionary with format {ip/subnet: itam}
        
    Returns:
        set: Set of unique ITAM values
    """
    if not itam_dict:
        return set()
    
    # Extract all values (ITAMs) from the dictionary
    return set(str(v) for v in itam_dict.values() if pd.notna(v) and str(v).strip() != '')


def build_itam_lookup_dict(itam_df):
    """
    Build optimized lookup dictionary from ITAM DataFrame
    This pre-processing step significantly speeds up lookups
    
    Args:
        itam_df: DataFrame containing itam and name columns
        
    Returns:
        dict: Dictionary mapping ITAM to name
    """
    print("\nBuilding ITAM lookup dictionary...")
    
    # Build ITAM lookup dictionary: {itam: name}
    itam_lookup_dict = {}
    for _, row in itam_df.iterrows():
        itam = str(row['itam']).strip()
        name = row['name'] if pd.notna(row['name']) else None
        if name:
            itam_lookup_dict[itam] = str(name).strip()
    
    print(f"  ✓ ITAM lookup dictionary built: {len(itam_lookup_dict)} entries")
    
    return itam_lookup_dict


def create_itam_name_mapping(itam_dict, itam_lookup_dict):
    """
    Create a dictionary mapping ITAMs to their names
    
    Args:
        itam_dict: Dictionary with format {ip/subnet: itam}
        itam_lookup_dict: Dictionary mapping ITAM to name
        
    Returns:
        dict: Dictionary mapping ITAM to name {itam: name}
    """
    itam_name_map = {}
    
    if not itam_dict:
        return itam_name_map
    
    # Extract unique ITAMs from the dictionary values
    unique_itams = extract_itam_values(itam_dict)
    
    # Look up each ITAM
    for itam in unique_itams:
        name = itam_lookup_dict.get(itam)
        if name:
            itam_name_map[itam] = name
    
    return itam_name_map


def map_itam_names(input_file, itam_file, output_file, create_backup=True):
    """
    Main function to map ITAMs to their names
    
    Args:
        input_file: Path to input file (output from map_environments.py)
        itam_file: Path to itam.xlsx
        output_file: Path to output file
        create_backup: Whether to create a backup of the input file
    """
    
    print("="*80)
    print("ITAM NAME MAPPING SCRIPT")
    print("="*80)
    
    # Check if all input files exist
    missing_files = []
    for file, name in [(input_file, "Input file"), (itam_file, "ITAM file")]:
        if not os.path.exists(file):
            missing_files.append(f"{name}: {file}")
    
    if missing_files:
        print("\nERROR: The following files were not found:")
        for file in missing_files:
            print(f"  - {file}")
        print(f"\nCurrent directory: {os.getcwd()}")
        return
    
    print(f"\nInput files:")
    print(f"  Rules file: {input_file}")
    print(f"  ITAM file:  {itam_file}")
    print(f"\nOutput file: {output_file}")
    
    # Create backup if requested
    if create_backup:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{os.path.splitext(input_file)[0]}_backup_{timestamp}.xlsx"
        print(f"\nCreating backup: {backup_file}")
        
        try:
            import shutil
            shutil.copy2(input_file, backup_file)
            print(f"✓ Backup created successfully")
        except Exception as e:
            print(f"⚠ Warning: Could not create backup - {e}")
    
    # Read all files
    print(f"\nReading files...")
    try:
        rules_df = pd.read_excel(input_file, engine='openpyxl')
        print(f"✓ Rules file loaded - {len(rules_df):,} rows")
        
        itam_df = pd.read_excel(itam_file, engine='openpyxl')
        print(f"✓ ITAM file loaded - {len(itam_df):,} ITAMs")
    except Exception as e:
        print(f"ERROR: Failed to read files - {e}")
        return
    
    # Verify required columns
    if 'Source ITAM' not in rules_df.columns or 'Destination ITAM' not in rules_df.columns:
        print("\nERROR: 'Source ITAM' or 'Destination ITAM' column not found in input file")
        print(f"Available columns: {list(rules_df.columns)}")
        print("\nMake sure you're using the output file from map_environments.py")
        return
    
    if 'itam' not in itam_df.columns or 'name' not in itam_df.columns:
        print("\nERROR: 'itam' or 'name' column not found in ITAM file")
        print(f"Available columns: {list(itam_df.columns)}")
        return
    
    # Build optimized lookup dictionary (huge performance improvement for large datasets)
    itam_lookup_dict = build_itam_lookup_dict(itam_df)
    
    print("\n" + "="*80)
    print("PROCESSING ROWS AND MAPPING ITAM NAMES...")
    print("="*80)
    
    stats = {
        'rows_processed': 0,
        'source_itam_names_found': 0,
        'dest_itam_names_found': 0,
        'unique_source_itams': set(),
        'unique_dest_itams': set()
    }
    
    # Create new columns lists
    source_itam_name_list = []
    dest_itam_name_list = []
    
    # Process each row - vectorize dictionary parsing for better performance
    print("\nParsing ITAM dictionaries from all rows...")
    source_itam_dicts = rules_df['Source ITAM'].apply(parse_dict_string)
    dest_itam_dicts = rules_df['Destination ITAM'].apply(parse_dict_string)
    print(f"  ✓ Parsed ITAM dictionaries for {len(rules_df):,} rows")
    
    print("\nMapping ITAM names...")
    for idx in range(len(rules_df)):
        stats['rows_processed'] += 1
        
        # Get parsed dictionaries
        source_itam_dict = source_itam_dicts.iloc[idx]
        dest_itam_dict = dest_itam_dicts.iloc[idx]
        
        # Create ITAM to Name mappings for source
        source_itam_name_map = create_itam_name_mapping(source_itam_dict, itam_lookup_dict)
        stats['source_itam_names_found'] += len(source_itam_name_map)
        stats['unique_source_itams'].update(source_itam_name_map.keys())
        
        # Create ITAM to Name mappings for destination
        dest_itam_name_map = create_itam_name_mapping(dest_itam_dict, itam_lookup_dict)
        stats['dest_itam_names_found'] += len(dest_itam_name_map)
        stats['unique_dest_itams'].update(dest_itam_name_map.keys())
        
        # Store as string representation of dictionary
        source_itam_name_list.append(str(source_itam_name_map) if source_itam_name_map else '{}')
        dest_itam_name_list.append(str(dest_itam_name_map) if dest_itam_name_map else '{}')
        
        # Print progress for every 1000 rows
        if (idx + 1) % 1000 == 0:
            print(f"  Processed {idx + 1:,} / {len(rules_df):,} rows ({(idx+1)/len(rules_df)*100:.1f}%)...")
    
    # Add new columns to dataframe
    rules_df['Source ITAM Name'] = source_itam_name_list
    rules_df['Destination ITAM Name'] = dest_itam_name_list
    
    print(f"\n✓ All {stats['rows_processed']:,} rows processed")
    
    # Save to Excel
    print(f"\nSaving results to: {output_file}...")
    try:
        rules_df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"✓ File saved successfully")
    except Exception as e:
        print(f"ERROR: Failed to save file - {e}")
        return
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY:")
    print("="*80)
    print(f"  Rows processed:                      {stats['rows_processed']:,}")
    print(f"\n  SOURCE ITAM NAME MAPPINGS:")
    print(f"    Total mappings found:              {stats['source_itam_names_found']:,}")
    print(f"    Unique ITAMs mapped:               {len(stats['unique_source_itams']):,}")
    print(f"\n  DESTINATION ITAM NAME MAPPINGS:")
    print(f"    Total mappings found:              {stats['dest_itam_names_found']:,}")
    print(f"    Unique ITAMs mapped:               {len(stats['unique_dest_itams']):,}")
    print("\n✓ ITAM name mapping completed successfully!")
    print(f"\nNew columns added:")
    print(f"  - Source ITAM Name")
    print(f"  - Destination ITAM Name")
    print("\nAll original columns have been preserved.")
    print("="*80)


if __name__ == "__main__":
    # Check if required libraries are installed
    try:
        import pandas
        import openpyxl
    except ImportError as e:
        print("ERROR: Required library not found!")
        print("\nPlease install required libraries:")
        print("  pip install pandas openpyxl")
        print(f"\nMissing: {e}")
        exit(1)
    
    # Run the mapping process
    map_itam_names(INPUT_FILE, ITAM_FILE, OUTPUT_FILE, CREATE_BACKUP)
