"""
Environment and ITAM Mapping Script for nfast_rules_cleaned.xlsx

This script performs the following tasks:
1. For each row in nfast_rules_cleaned.xlsx, reads Source IP and Destination IP
2. Looks up each IP in ip.xlsx and each subnet in subnet.xlsx
3. Creates dictionaries mapping IPs/subnets to their environments and ITAMs
4. Adds four new columns: 
   - Source Environment: {"ip1":"env1","subnet1":"env2"}
   - Destination Environment: {"ip1":"env1","subnet1":"env2"}
   - Source ITAM: {"ip1":"itam1","subnet1":"itam2"}
   - Destination ITAM: {"ip1":"itam1","subnet1":"itam2"}

Optimized for performance with large datasets (17,000+ records)

Usage:
    python map_environments.py

Requirements:
    - pandas
    - openpyxl
    - ipaddress (built-in)

Install requirements:
    pip install pandas openpyxl
"""

import pandas as pd
import ast
import ipaddress
from datetime import datetime
import os

# Configuration
INPUT_FILE = 'nfast_rules_cleaned.xlsx'  # Input file
IP_FILE = 'ip.xlsx'  # IP lookup file
SUBNET_FILE = 'subnet.xlsx'  # Subnet lookup file
OUTPUT_FILE = 'nfast_rules_with_environments.xlsx'  # Output file

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


def is_ip_address(s):
    """
    Check if string is a single IP address (not a subnet)
    
    Args:
        s: String to check
        
    Returns:
        bool: True if string is an IP address without CIDR notation
    """
    try:
        # Check if it contains '/'
        if '/' in str(s):
            return False
        # Try to parse as IP address
        ipaddress.ip_address(str(s).strip())
        return True
    except:
        return False


def is_subnet(s):
    """
    Check if string is a subnet (has CIDR notation)
    
    Args:
        s: String to check
        
    Returns:
        bool: True if string is a subnet with CIDR notation
    """
    try:
        # Must contain '/'
        if '/' not in str(s):
            return False
        # Try to parse as network
        ipaddress.ip_network(str(s).strip(), strict=False)
        return True
    except:
        return False


def lookup_ip_info(ip, ip_lookup_dict):
    """
    Look up the environment and ITAM for a given IP address using pre-built dictionary
    
    Args:
        ip: IP address string
        ip_lookup_dict: Dictionary mapping IPs to (environment, itam) tuples
        
    Returns:
        tuple: (environment, itam) or (None, None) if not found
    """
    # Normalize IP (remove any /32 if present)
    clean_ip = ip.split('/')[0].strip()
    
    return ip_lookup_dict.get(clean_ip, (None, None))


def lookup_subnet_info(subnet, subnet_lookup_dict):
    """
    Look up the environment and ITAM for a given subnet using pre-built dictionary
    
    Args:
        subnet: Subnet string (with CIDR notation)
        subnet_lookup_dict: Dictionary mapping subnets to (environment, itam) tuples
        
    Returns:
        tuple: (environment, itam) or (None, None) if not found
    """
    # Normalize subnet
    clean_subnet = subnet.strip()
    
    return subnet_lookup_dict.get(clean_subnet, (None, None))


def build_lookup_dictionaries(ip_df, subnet_df):
    """
    Build optimized lookup dictionaries from IP and subnet DataFrames
    This pre-processing step significantly speeds up lookups
    
    Args:
        ip_df: DataFrame containing IP, environment, and itam columns
        subnet_df: DataFrame containing subnet, environment, and itam columns
        
    Returns:
        tuple: (ip_lookup_dict, subnet_lookup_dict)
    """
    print("\nBuilding optimized lookup dictionaries...")
    
    # Build IP lookup dictionary: {ip: (environment, itam)}
    ip_lookup_dict = {}
    for _, row in ip_df.iterrows():
        ip = str(row['ip']).strip()
        env = row['environment'] if pd.notna(row['environment']) else None
        itam = row['itam'] if pd.notna(row['itam']) else None
        ip_lookup_dict[ip] = (env, itam)
    
    print(f"  ✓ IP lookup dictionary built: {len(ip_lookup_dict)} entries")
    
    # Build subnet lookup dictionary: {subnet: (environment, itam)}
    subnet_lookup_dict = {}
    for _, row in subnet_df.iterrows():
        subnet = str(row['subnet']).strip()
        env = row['environment'] if pd.notna(row['environment']) else None
        itam = row['itam'] if pd.notna(row['itam']) else None
        subnet_lookup_dict[subnet] = (env, itam)
    
    print(f"  ✓ Subnet lookup dictionary built: {len(subnet_lookup_dict)} entries")
    
    return ip_lookup_dict, subnet_lookup_dict


def create_mappings(ip_list, ip_lookup_dict, subnet_lookup_dict):
    """
    Create dictionaries mapping IPs/subnets to their environments and ITAMs
    
    Args:
        ip_list: List of IPs and subnets
        ip_lookup_dict: Dictionary with IP lookups
        subnet_lookup_dict: Dictionary with subnet lookups
        
    Returns:
        tuple: (env_map, itam_map) - Two dictionaries for environment and ITAM mappings
    """
    env_map = {}
    itam_map = {}
    
    for item in ip_list:
        item_str = str(item).strip()
        
        if not item_str:
            continue
        
        # Check if it's an IP address (no CIDR) or has /32
        if is_ip_address(item_str) or (is_subnet(item_str) and item_str.endswith('/32')):
            # Look up in IP dictionary
            env, itam = lookup_ip_info(item_str, ip_lookup_dict)
            if env:
                env_map[item_str] = env
            if itam:
                itam_map[item_str] = itam
        
        # Check if it's a subnet (has CIDR notation and not /32)
        elif is_subnet(item_str):
            # Look up in subnet dictionary
            env, itam = lookup_subnet_info(item_str, subnet_lookup_dict)
            if env:
                env_map[item_str] = env
            if itam:
                itam_map[item_str] = itam
    
    return env_map, itam_map


def map_environments(input_file, ip_file, subnet_file, output_file, create_backup=True):
    """
    Main function to map environments to IPs and subnets
    
    Args:
        input_file: Path to nfast_rules_cleaned.xlsx
        ip_file: Path to ip.xlsx
        subnet_file: Path to subnet.xlsx
        output_file: Path to output file
        create_backup: Whether to create a backup of the input file
    """
    
    print("="*80)
    print("ENVIRONMENT MAPPING SCRIPT")
    print("="*80)
    
    # Check if all input files exist
    missing_files = []
    for file, name in [(input_file, "Rules file"), (ip_file, "IP file"), (subnet_file, "Subnet file")]:
        if not os.path.exists(file):
            missing_files.append(f"{name}: {file}")
    
    if missing_files:
        print("\nERROR: The following files were not found:")
        for file in missing_files:
            print(f"  - {file}")
        print(f"\nCurrent directory: {os.getcwd()}")
        return
    
    print(f"\nInput files:")
    print(f"  Rules file:  {input_file}")
    print(f"  IP file:     {ip_file}")
    print(f"  Subnet file: {subnet_file}")
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
        print(f"✓ Rules file loaded - {len(rules_df)} rows")
        
        ip_df = pd.read_excel(ip_file, engine='openpyxl')
        print(f"✓ IP file loaded - {len(ip_df)} IPs")
        
        subnet_df = pd.read_excel(subnet_file, engine='openpyxl')
        print(f"✓ Subnet file loaded - {len(subnet_df)} subnets")
    except Exception as e:
        print(f"ERROR: Failed to read files - {e}")
        return
    
    # Verify required columns
    if 'Source IP' not in rules_df.columns or 'Destination IP' not in rules_df.columns:
        print("\nERROR: 'Source IP' or 'Destination IP' column not found in rules file")
        print(f"Available columns: {list(rules_df.columns)}")
        return
    
    if 'ip' not in ip_df.columns or 'environment' not in ip_df.columns or 'itam' not in ip_df.columns:
        print("\nERROR: Required columns ('ip', 'environment', 'itam') not found in IP file")
        print(f"Available columns: {list(ip_df.columns)}")
        return
    
    if 'subnet' not in subnet_df.columns or 'environment' not in subnet_df.columns or 'itam' not in subnet_df.columns:
        print("\nERROR: Required columns ('subnet', 'environment', 'itam') not found in subnet file")
        print(f"Available columns: {list(subnet_df.columns)}")
        return
    
    # Build optimized lookup dictionaries (huge performance improvement for large datasets)
    ip_lookup_dict, subnet_lookup_dict = build_lookup_dictionaries(ip_df, subnet_df)
    
    print("\n" + "="*80)
    print("PROCESSING ROWS AND MAPPING ENVIRONMENTS...")
    print("="*80)
    
    stats = {
        'rows_processed': 0,
        'source_env_mappings': 0,
        'dest_env_mappings': 0,
        'source_itam_mappings': 0,
        'dest_itam_mappings': 0,
        'source_ips_found': 0,
        'source_subnets_found': 0,
        'dest_ips_found': 0,
        'dest_subnets_found': 0
    }
    
    # Create new columns lists
    source_env_list = []
    dest_env_list = []
    source_itam_list = []
    dest_itam_list = []
    
    # Process each row - vectorize list parsing for better performance
    print("\nParsing IP lists from all rows...")
    source_ip_lists = rules_df['Source IP'].apply(parse_list_string)
    dest_ip_lists = rules_df['Destination IP'].apply(parse_list_string)
    print(f"  ✓ Parsed IP lists for {len(rules_df)} rows")
    
    print("\nMapping environments and ITAMs...")
    for idx in range(len(rules_df)):
        stats['rows_processed'] += 1
        
        # Get parsed lists
        source_ips = source_ip_lists.iloc[idx]
        dest_ips = dest_ip_lists.iloc[idx]
        
        # Create mappings for source
        source_env_map, source_itam_map = create_mappings(source_ips, ip_lookup_dict, subnet_lookup_dict)
        
        # Count findings
        for key in source_env_map.keys():
            if '/' in key and not key.endswith('/32'):
                stats['source_subnets_found'] += 1
            else:
                stats['source_ips_found'] += 1
        
        stats['source_env_mappings'] += len(source_env_map)
        stats['source_itam_mappings'] += len(source_itam_map)
        
        # Create mappings for destination
        dest_env_map, dest_itam_map = create_mappings(dest_ips, ip_lookup_dict, subnet_lookup_dict)
        
        # Count findings
        for key in dest_env_map.keys():
            if '/' in key and not key.endswith('/32'):
                stats['dest_subnets_found'] += 1
            else:
                stats['dest_ips_found'] += 1
        
        stats['dest_env_mappings'] += len(dest_env_map)
        stats['dest_itam_mappings'] += len(dest_itam_map)
        
        # Store as string representation of dictionary
        source_env_list.append(str(source_env_map) if source_env_map else '{}')
        dest_env_list.append(str(dest_env_map) if dest_env_map else '{}')
        source_itam_list.append(str(source_itam_map) if source_itam_map else '{}')
        dest_itam_list.append(str(dest_itam_map) if dest_itam_map else '{}')
        
        # Print progress for every 1000 rows (adjusted for larger dataset)
        if (idx + 1) % 1000 == 0:
            print(f"  Processed {idx + 1:,} / {len(rules_df):,} rows ({(idx+1)/len(rules_df)*100:.1f}%)...")
    
    # Add new columns to dataframe
    rules_df['Source Environment'] = source_env_list
    rules_df['Destination Environment'] = dest_env_list
    rules_df['Source ITAM'] = source_itam_list
    rules_df['Destination ITAM'] = dest_itam_list
    
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
    print(f"  Rows processed:                   {stats['rows_processed']:,}")
    print(f"\n  SOURCE MAPPINGS:")
    print(f"    Environment mappings found:     {stats['source_env_mappings']:,}")
    print(f"    ITAM mappings found:            {stats['source_itam_mappings']:,}")
    print(f"      - IPs mapped:                 {stats['source_ips_found']:,}")
    print(f"      - Subnets mapped:             {stats['source_subnets_found']:,}")
    print(f"\n  DESTINATION MAPPINGS:")
    print(f"    Environment mappings found:     {stats['dest_env_mappings']:,}")
    print(f"    ITAM mappings found:            {stats['dest_itam_mappings']:,}")
    print(f"      - IPs mapped:                 {stats['dest_ips_found']:,}")
    print(f"      - Subnets mapped:             {stats['dest_subnets_found']:,}")
    print("\n✓ Environment and ITAM mapping completed successfully!")
    print(f"\nNew columns added:")
    print(f"  - Source Environment")
    print(f"  - Destination Environment")
    print(f"  - Source ITAM")
    print(f"  - Destination ITAM")
    print("="*80)


if __name__ == "__main__":
    # Check if required libraries are installed
    try:
        import pandas
        import openpyxl
        import ipaddress
    except ImportError as e:
        print("ERROR: Required library not found!")
        print("\nPlease install required libraries:")
        print("  pip install pandas openpyxl")
        print(f"\nMissing: {e}")
        exit(1)
    
    # Run the mapping process
    map_environments(INPUT_FILE, IP_FILE, SUBNET_FILE, OUTPUT_FILE, CREATE_BACKUP)
