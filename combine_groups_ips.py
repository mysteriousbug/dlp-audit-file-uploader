"""
Simple Combination Script for nfast_rules.xlsx

This script performs the following task:
- Combines all entries from Source Groups with Source IP (no filtering, no cleaning)
- Combines all entries from Destination Groups with Destination IP (no filtering, no cleaning)

Usage:
    python combine_groups_ips.py

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
INPUT_FILE = 'nfast_rules.xlsx'  # Change this to your input file path
OUTPUT_FILE = 'nfast_rules_combined.xlsx'  # Change this to your desired output file path

# Create backup flag
CREATE_BACKUP = True


def parse_list_string(s):
    """
    Parse string representation of list into actual list
    
    Args:
        s: String representation of a list
        
    Returns:
        list: Parsed list or empty list if parsing fails
    """
    if pd.isna(s) or s == '' or s == '[]':
        return []
    
    # If it's already a list, return it
    if isinstance(s, list):
        return s
    
    try:
        # Try to evaluate as Python literal
        result = ast.literal_eval(str(s))
        if isinstance(result, list):
            return result
        else:
            return [result]
    except:
        # If evaluation fails, return empty list
        return []


def combine_data(input_file, output_file, create_backup=True):
    """
    Main function to combine Source Groups with Source IP and Destination Groups with Destination IP
    
    Args:
        input_file: Path to input Excel file
        output_file: Path to output Excel file
        create_backup: Whether to create a backup of the original file
    """
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"ERROR: Input file '{input_file}' not found!")
        print(f"Current directory: {os.getcwd()}")
        print("Please ensure the file is in the same directory as this script,")
        print("or update the INPUT_FILE variable with the correct path.")
        return
    
    print("="*80)
    print("SIMPLE COMBINATION SCRIPT FOR NFAST_RULES.XLSX")
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
    print("COMBINING GROUPS WITH IPS...")
    print("="*80)
    
    stats = {
        'rows_processed': 0,
        'source_items_added': 0,
        'dest_items_added': 0
    }
    
    # Process each row
    for idx, row in df.iterrows():
        stats['rows_processed'] += 1
        
        # Parse Source Groups and Source IP
        source_groups = parse_list_string(row['Source Groups'])
        source_ips = parse_list_string(row['Source IP'])
        
        # Combine all items (no filtering, no checking)
        combined_source = source_groups + source_ips
        
        # Remove duplicates while preserving order
        seen = set()
        combined_source_unique = []
        for item in combined_source:
            item_str = str(item)
            if item_str not in seen:
                seen.add(item_str)
                combined_source_unique.append(item)
        
        stats['source_items_added'] += len(source_groups)
        
        # Parse Destination Groups and Destination IP
        dest_groups = parse_list_string(row['Destination Groups'])
        dest_ips = parse_list_string(row['Destination IP'])
        
        # Combine all items (no filtering, no checking)
        combined_dest = dest_groups + dest_ips
        
        # Remove duplicates while preserving order
        seen = set()
        combined_dest_unique = []
        for item in combined_dest:
            item_str = str(item)
            if item_str not in seen:
                seen.add(item_str)
                combined_dest_unique.append(item)
        
        stats['dest_items_added'] += len(dest_groups)
        
        # Update the dataframe (convert back to string representation of list)
        df.at[idx, 'Source IP'] = str(combined_source_unique)
        df.at[idx, 'Destination IP'] = str(combined_dest_unique)
        
        # Print progress for every 1000 rows
        if (idx + 1) % 1000 == 0:
            print(f"  Processed {idx + 1:,} / {len(df):,} rows ({(idx+1)/len(df)*100:.1f}%)...")
    
    print(f"\n✓ All {stats['rows_processed']:,} rows processed")
    
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
    print("SUMMARY OF CHANGES:")
    print("="*80)
    print(f"  Rows processed:                {stats['rows_processed']:,}")
    print(f"  Source Groups items added:     {stats['source_items_added']:,}")
    print(f"  Destination Groups items added: {stats['dest_items_added']:,}")
    print("\n✓ Combination completed successfully!")
    print("\nWhat was done:")
    print("  - All items from Source Groups were added to Source IP")
    print("  - All items from Destination Groups were added to Destination IP")
    print("  - Duplicates were removed from the combined lists")
    print("  - No filtering or cleaning was applied")
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
    
    # Run the combination process
    combine_data(INPUT_FILE, OUTPUT_FILE, CREATE_BACKUP)
