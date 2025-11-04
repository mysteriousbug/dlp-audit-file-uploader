"""
Data Cleaning Script for nfast_rules.xlsx

This script performs the following tasks:
1a. Extracts IP addresses/subnets from Source Groups and Destination Groups columns
    and appends them to Source IP and Destination IP columns respectively
1b. Removes any entries with IP ranges like '0.0.0.0-9.255.255.255' from IP columns

Usage:
    python clean_nfast_rules.py

Requirements:
    - pandas
    - openpyxl

Install requirements:
    pip install pandas openpyxl
"""

import pandas as pd
import re
import ast
import os
from datetime import datetime

# Configuration
INPUT_FILE = 'nfast_rules.xlsx'  # Change this to your input file path
OUTPUT_FILE = 'nfast_rules_cleaned.xlsx'  # Change this to your desired output file path

# Create backup flag
CREATE_BACKUP = True


def is_ip_or_subnet(s):
    """
    Check if string is an IP address or subnet (CIDR notation)
    
    Args:
        s: String to check
        
    Returns:
        bool: True if string is an IP address or subnet, False otherwise
    """
    # Pattern for IP address (with or without CIDR)
    ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(/\d{1,2})?$'
    return bool(re.match(ip_pattern, str(s).strip()))


def is_ip_range(s):
    """
    Check if string is an IP range in format 'x.x.x.x-y.y.y.y'
    
    Args:
        s: String to check
        
    Returns:
        bool: True if string is an IP range, False otherwise
    """
    range_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    return bool(re.match(range_pattern, str(s).strip()))


def parse_list_string(s):
    """
    Parse string representation of list into actual list
    
    Args:
        s: String representation of a list
        
    Returns:
        list: Parsed list or empty list if parsing fails
    """
    if pd.isna(s) or s == '':
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


def extract_ips_from_groups(groups_list):
    """
    Extract IP addresses and subnets from a list of group entries
    
    Args:
        groups_list: List of group entries (may contain IPs/subnets mixed with group names)
        
    Returns:
        list: List of extracted IP addresses and subnets
    """
    ips = []
    
    if not isinstance(groups_list, list):
        return ips
    
    for item in groups_list:
        item_str = str(item).strip()
        if is_ip_or_subnet(item_str):
            ips.append(item_str)
    
    return ips


def clean_data(input_file, output_file, create_backup=True):
    """
    Main function to clean the nfast_rules data
    
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
    print("DATA CLEANING SCRIPT FOR NFAST_RULES.XLSX")
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
        print(f"✓ File loaded successfully - {len(df)} rows found")
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
    print("TASK 1A: Extracting IPs from Groups and appending to IP columns...")
    print("="*80)
    
    stats = {
        'rows_processed': 0,
        'source_ips_added': 0,
        'dest_ips_added': 0,
        'ip_ranges_removed': 0
    }
    
    # Process each row
    for idx, row in df.iterrows():
        stats['rows_processed'] += 1
        
        # Process Source Groups and Source IP
        source_groups = parse_list_string(row['Source Groups'])
        source_ips = parse_list_string(row['Source IP'])
        
        # Extract IPs from Source Groups
        extracted_source_ips = extract_ips_from_groups(source_groups)
        stats['source_ips_added'] += len(extracted_source_ips)
        
        if extracted_source_ips:
            print(f"  Row {idx+1}: Found {len(extracted_source_ips)} IP(s) in Source Groups: {extracted_source_ips}")
        
        # Combine and remove duplicates (preserve as list of strings)
        combined_source_ips = list(set(source_ips + extracted_source_ips))
        
        # Process Destination Groups and Destination IP
        dest_groups = parse_list_string(row['Destination Groups'])
        dest_ips = parse_list_string(row['Destination IP'])
        
        # Extract IPs from Destination Groups
        extracted_dest_ips = extract_ips_from_groups(dest_groups)
        stats['dest_ips_added'] += len(extracted_dest_ips)
        
        if extracted_dest_ips:
            print(f"  Row {idx+1}: Found {len(extracted_dest_ips)} IP(s) in Destination Groups: {extracted_dest_ips}")
        
        # Combine and remove duplicates (preserve as list of strings)
        combined_dest_ips = list(set(dest_ips + extracted_dest_ips))
        
        # Task 1b: Remove IP ranges like '0.0.0.0-9.255.255.255'
        source_ranges = [ip for ip in combined_source_ips if is_ip_range(ip)]
        dest_ranges = [ip for ip in combined_dest_ips if is_ip_range(ip)]
        
        if source_ranges:
            print(f"  Row {idx+1}: Removing {len(source_ranges)} IP range(s) from Source IP: {source_ranges}")
            stats['ip_ranges_removed'] += len(source_ranges)
        
        if dest_ranges:
            print(f"  Row {idx+1}: Removing {len(dest_ranges)} IP range(s) from Destination IP: {dest_ranges}")
            stats['ip_ranges_removed'] += len(dest_ranges)
        
        combined_source_ips = [ip for ip in combined_source_ips if not is_ip_range(ip)]
        combined_dest_ips = [ip for ip in combined_dest_ips if not is_ip_range(ip)]
        
        # Update the dataframe (convert back to string representation of list)
        df.at[idx, 'Source IP'] = str(combined_source_ips)
        df.at[idx, 'Destination IP'] = str(combined_dest_ips)
    
    print("\n" + "="*80)
    print("TASK 1B: Removed IP ranges from IP columns")
    print("="*80)
    
    # Save to Excel
    print(f"\nSaving cleaned data to: {output_file}...")
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
    print(f"  Rows processed:              {stats['rows_processed']}")
    print(f"  Source IPs added:            {stats['source_ips_added']}")
    print(f"  Destination IPs added:       {stats['dest_ips_added']}")
    print(f"  IP ranges removed:           {stats['ip_ranges_removed']}")
    print("\n✓ Data cleaning completed successfully!")
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
    
    # Run the cleaning process
    clean_data(INPUT_FILE, OUTPUT_FILE, CREATE_BACKUP)
