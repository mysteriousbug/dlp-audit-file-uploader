"""
String-Based Combination Script for nfast_rules.xlsx

This script preserves the EXACT string format by manipulating strings directly
instead of parsing to lists and back. This ensures Excel filtering works correctly.

Usage:
    python combine_groups_ips_string.py

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
INPUT_FILE = 'nfast_rules.xlsx'
OUTPUT_FILE = 'nfast_rules_combined.xlsx'
CREATE_BACKUP = True


def combine_list_strings(groups_str, ips_str):
    """
    Combine two string representations of lists by direct string manipulation
    This preserves the exact format for Excel filtering
    
    Args:
        groups_str: String like "['item1', 'item2']"
        ips_str: String like "['item3', 'item4']"
        
    Returns:
        Combined string like "['item1', 'item2', 'item3', 'item4']"
    """
    # Handle empty/null values
    if pd.isna(groups_str) or str(groups_str).strip() in ['', '[]', 'nan']:
        groups_str = '[]'
    if pd.isna(ips_str) or str(ips_str).strip() in ['', '[]', 'nan']:
        ips_str = '[]'
    
    groups_str = str(groups_str).strip()
    ips_str = str(ips_str).strip()
    
    # If both are empty
    if groups_str == '[]' and ips_str == '[]':
        return '[]'
    
    # If groups is empty, return ips as is
    if groups_str == '[]':
        return ips_str
    
    # If ips is empty, return groups as is
    if ips_str == '[]':
        return groups_str
    
    # Both have content - combine them
    # Remove the trailing ']' from groups and leading '[' from ips
    groups_content = groups_str.rstrip(']').strip()
    ips_content = ips_str.lstrip('[').strip()
    
    # Combine with a comma separator
    combined = groups_content + ', ' + ips_content
    
    return combined


def combine_data(input_file, output_file, create_backup=True):
    """
    Main function to combine groups with IPs using string manipulation
    """
    
    if not os.path.exists(input_file):
        print(f"ERROR: Input file '{input_file}' not found!")
        print(f"Current directory: {os.getcwd()}")
        return
    
    print("="*80)
    print("STRING-BASED COMBINATION SCRIPT FOR NFAST_RULES.XLSX")
    print("="*80)
    print(f"\nInput file: {input_file}")
    print(f"Output file: {output_file}")
    
    # Create backup if requested
    if create_backup:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{os.path.splitext(input_file)[0]}_backup_{timestamp}.xlsx"
        print(f"Creating backup: {backup_file}")
        
        try:
            import shutil
            shutil.copy2(input_file, backup_file)
            print(f"✓ Backup created successfully")
        except Exception as e:
            print(f"⚠ Warning: Could not create backup - {e}")
    
    # Read the Excel file
    print(f"\nReading file: {input_file}...")
    try:
        df = pd.read_excel(input_file, engine='openpyxl')
        print(f"✓ File loaded successfully - {len(df):,} rows found")
    except Exception as e:
        print(f"ERROR: Failed to read file - {e}")
        return
    
    # Verify required columns exist
    required_columns = ['Source Groups', 'Source IP', 'Destination Groups', 'Destination IP']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"\nERROR: Missing required columns: {missing_columns}")
        print(f"Available columns: {list(df.columns)}")
        return
    
    print("\n" + "="*80)
    print("COMBINING GROUPS WITH IPS (STRING-BASED)...")
    print("="*80)
    
    # Show sample before processing
    print("\nSample BEFORE (first row):")
    print(f"  Source Groups: {df.iloc[0]['Source Groups']}")
    print(f"  Source IP: {df.iloc[0]['Source IP']}")
    
    stats = {
        'rows_processed': 0
    }
    
    # Process each row using string manipulation
    new_source_ips = []
    new_dest_ips = []
    
    for idx, row in df.iterrows():
        stats['rows_processed'] += 1
        
        # Combine Source Groups with Source IP (string-based)
        combined_source = combine_list_strings(row['Source Groups'], row['Source IP'])
        new_source_ips.append(combined_source)
        
        # Combine Destination Groups with Destination IP (string-based)
        combined_dest = combine_list_strings(row['Destination Groups'], row['Destination IP'])
        new_dest_ips.append(combined_dest)
        
        # Print progress for every 1000 rows
        if (idx + 1) % 1000 == 0:
            print(f"  Processed {idx + 1:,} / {len(df):,} rows ({(idx+1)/len(df)*100:.1f}%)...")
    
    # Update the dataframe with new values
    df['Source IP'] = new_source_ips
    df['Destination IP'] = new_dest_ips
    
    print(f"\n✓ All {stats['rows_processed']:,} rows processed")
    
    # Show sample after processing
    print("\nSample AFTER (first row):")
    print(f"  Source IP: {df.iloc[0]['Source IP']}")
    
    # Save to Excel
    print(f"\nSaving combined data to: {output_file}...")
    try:
        df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"✓ File saved successfully")
    except Exception as e:
        print(f"ERROR: Failed to save file - {e}")
        return
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY:")
    print("="*80)
    print(f"  Rows processed:                {stats['rows_processed']:,}")
    print("\n✓ Combination completed successfully!")
    print("\nWhat was done:")
    print("  - Source Groups and Source IP were combined by string concatenation")
    print("  - Destination Groups and Destination IP were combined by string concatenation")
    print("  - Original string format preserved for Excel filtering")
    print("  - All items kept (no filtering, no duplicate removal)")
    print("\nYou can now filter in Excel and the counts should match!")
    print("="*80)


if __name__ == "__main__":
    try:
        import pandas
        import openpyxl
    except ImportError as e:
        print("ERROR: Required library not found!")
        print("\nPlease install required libraries:")
        print("  pip install pandas openpyxl")
        print(f"\nMissing: {e}")
        exit(1)
    
    combine_data(INPUT_FILE, OUTPUT_FILE, CREATE_BACKUP)
