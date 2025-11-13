"""
ITAM ID to Name Mapping Script

This script performs the following tasks:
1. Reads file1 which has an 'itam' column (ITAM ID as string)
2. Reads file2 which has 'itam' (ID) and 'name' columns
3. Maps ITAM IDs from file1 to ITAM Names in file2
4. Adds a new 'itam name' column to file1 with the matched names

Usage:
    python map_itam_id_to_name.py

Requirements:
    - pandas
    - openpyxl

Install requirements:
    pip install pandas openpyxl
"""

import pandas as pd
from datetime import datetime
import os

# Configuration
INPUT_FILE1 = 'file1.xlsx'  # File with 'itam' column (ITAM IDs)
INPUT_FILE2 = 'file2.xlsx'  # File with 'itam' and 'name' columns
OUTPUT_FILE = 'file1_with_names.xlsx'  # Output file

# Create backup flag
CREATE_BACKUP = True


def map_itam_names(file1, file2, output_file, create_backup=True):
    """
    Map ITAM IDs to ITAM Names and add to file1
    
    Args:
        file1: Path to file with ITAM IDs
        file2: Path to file with ITAM IDs and Names
        output_file: Path to output file
        create_backup: Whether to create a backup of file1
    """
    
    print("="*80)
    print("ITAM ID TO NAME MAPPING SCRIPT")
    print("="*80)
    
    # Check if input files exist
    missing_files = []
    for file, name in [(file1, "File 1"), (file2, "File 2")]:
        if not os.path.exists(file):
            missing_files.append(f"{name}: {file}")
    
    if missing_files:
        print("\nERROR: The following files were not found:")
        for file in missing_files:
            print(f"  - {file}")
        print(f"\nCurrent directory: {os.getcwd()}")
        return
    
    print(f"\nInput files:")
    print(f"  File 1 (with ITAM IDs): {file1}")
    print(f"  File 2 (with ITAM Names): {file2}")
    print(f"\nOutput file: {output_file}")
    
    # Create backup if requested
    if create_backup:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{os.path.splitext(file1)[0]}_backup_{timestamp}.xlsx"
        print(f"\nCreating backup: {backup_file}")
        
        try:
            import shutil
            shutil.copy2(file1, backup_file)
            print(f"✓ Backup created successfully")
        except Exception as e:
            print(f"⚠ Warning: Could not create backup - {e}")
    
    # Read files
    print(f"\nReading files...")
    try:
        df1 = pd.read_excel(file1, engine='openpyxl')
        print(f"✓ File 1 loaded - {len(df1):,} rows")
        
        df2 = pd.read_excel(file2, engine='openpyxl')
        print(f"✓ File 2 loaded - {len(df2):,} ITAM mappings")
    except Exception as e:
        print(f"ERROR: Failed to read files - {e}")
        return
    
    # Verify required columns
    if 'itam' not in df1.columns:
        print("\nERROR: 'itam' column not found in File 1")
        print(f"Available columns: {list(df1.columns)}")
        return
    
    if 'itam' not in df2.columns or 'name' not in df2.columns:
        print("\nERROR: 'itam' or 'name' column not found in File 2")
        print(f"Available columns: {list(df2.columns)}")
        return
    
    # Build ITAM ID to Name lookup dictionary
    print("\nBuilding ITAM lookup dictionary...")
    itam_name_dict = {}
    for _, row in df2.iterrows():
        itam_id = str(row['itam']).strip()
        itam_name = row['name'] if pd.notna(row['name']) else None
        if itam_name:
            itam_name_dict[itam_id] = str(itam_name).strip()
    
    print(f"  ✓ ITAM lookup dictionary built: {len(itam_name_dict):,} entries")
    
    # Map ITAM IDs to Names
    print("\nMapping ITAM IDs to Names...")
    itam_names = []
    matched_count = 0
    unmatched_count = 0
    
    for idx, row in df1.iterrows():
        itam_id = row['itam']
        
        # Handle null/empty ITAM IDs
        if pd.isna(itam_id) or str(itam_id).strip() == '':
            itam_names.append(None)
            continue
        
        # Convert to string and look up
        itam_id_str = str(itam_id).strip()
        itam_name = itam_name_dict.get(itam_id_str)
        
        if itam_name:
            itam_names.append(itam_name)
            matched_count += 1
        else:
            itam_names.append(None)
            unmatched_count += 1
        
        # Print progress for every 1000 rows
        if (idx + 1) % 1000 == 0:
            print(f"  Processed {idx + 1:,} / {len(df1):,} rows ({(idx+1)/len(df1)*100:.1f}%)...")
    
    # Add new column to dataframe
    df1['itam name'] = itam_names
    
    print(f"\n✓ All {len(df1):,} rows processed")
    
    # Save to Excel
    print(f"\nSaving results to: {output_file}...")
    try:
        df1.to_excel(output_file, index=False, engine='openpyxl')
        print(f"✓ File saved successfully")
    except Exception as e:
        print(f"ERROR: Failed to save file - {e}")
        return
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY:")
    print("="*80)
    print(f"  Total rows processed:           {len(df1):,}")
    print(f"  ITAM IDs matched:               {matched_count:,}")
    print(f"  ITAM IDs not matched:           {unmatched_count:,}")
    print(f"  Null/empty ITAM IDs:            {len(df1) - matched_count - unmatched_count:,}")
    print(f"\n✓ ITAM name mapping completed successfully!")
    print(f"\nNew column added:")
    print(f"  - itam name")
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
    map_itam_names(INPUT_FILE1, INPUT_FILE2, OUTPUT_FILE, CREATE_BACKUP)
