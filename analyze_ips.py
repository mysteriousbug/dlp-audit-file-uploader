"""
Comprehensive IP and Subnet Analysis Script for nfast_rules.xlsx

This script performs the following tasks:
1. For each row in nfast_rules.xlsx, reads Source IP and Destination IP
2. For IPs: Looks up in ip.xlsx
3. For Subnets: Looks up in ipam_subnet.xlsx, then dev_subnet.xlsx, then staging_subnet.xlsx
4. Creates two new columns with comprehensive mapping information:
   - Source IP Analysis: {"ip/subnet": {"File Name": "...", "Environment": "...", ...}}
   - Destination IP Analysis: {"ip/subnet": {"File Name": "...", "Environment": "...", ...}}

Each mapping includes: File Name, Environment, Function, Location, Infra, ITAM ID, ITAM Name

Optimized for performance with large datasets (17,000+ records)

Usage:
    python analyze_ips.py

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
INPUT_FILE = 'nfast_rules.xlsx'  # Base input file
IP_FILE = 'ip.xlsx'  # IP lookup file
IPAM_SUBNET_FILE = 'ipam_subnet.xlsx'  # Primary subnet lookup file
DEV_SUBNET_FILE = 'dev_subnet.xlsx'  # Secondary subnet lookup file
STAGING_SUBNET_FILE = 'staging_subnet.xlsx'  # Tertiary subnet lookup file
ITAM_FILE = 'itam.xlsx'  # ITAM to Name mapping file
OUTPUT_FILE = 'nfast_rules_analyzed.xlsx'  # Output file

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


def build_ip_lookup_dict(ip_df):
    """
    Build optimized lookup dictionary from IP DataFrame
    
    Args:
        ip_df: DataFrame containing IP and related columns
        
    Returns:
        dict: Dictionary mapping IP to info tuple
    """
    print("  Building IP lookup dictionary...")
    
    ip_lookup_dict = {}
    for _, row in ip_df.iterrows():
        ip = str(row['ip']).strip()
        environment = row.get('environment', None) if pd.notna(row.get('environment')) else None
        function = row.get('function', None) if pd.notna(row.get('function')) else None
        location = row.get('location', None) if pd.notna(row.get('location')) else None
        infra = row.get('infra', None) if pd.notna(row.get('infra')) else None
        itam = row.get('itam', None) if pd.notna(row.get('itam')) else None
        
        ip_lookup_dict[ip] = {
            'file_name': 'ip.xlsx',
            'environment': environment,
            'function': function,
            'location': location,
            'infra': infra,
            'itam': itam
        }
    
    print(f"    ✓ IP lookup dictionary built: {len(ip_lookup_dict)} entries")
    return ip_lookup_dict


def build_subnet_lookup_dict(subnet_df, file_name):
    """
    Build optimized lookup dictionary from Subnet DataFrame
    
    Args:
        subnet_df: DataFrame containing subnet and related columns
        file_name: Name of the source file
        
    Returns:
        dict: Dictionary mapping subnet to info tuple
    """
    print(f"  Building subnet lookup dictionary from {file_name}...")
    
    subnet_lookup_dict = {}
    for _, row in subnet_df.iterrows():
        subnet = str(row['subnet']).strip()
        environment = row.get('environment', None) if pd.notna(row.get('environment')) else None
        function = row.get('function', None) if pd.notna(row.get('function')) else None
        location = row.get('location', None) if pd.notna(row.get('location')) else None
        infra = row.get('infra', None) if pd.notna(row.get('infra')) else None
        itam = row.get('itam', None) if pd.notna(row.get('itam')) else None
        
        subnet_lookup_dict[subnet] = {
            'file_name': file_name,
            'environment': environment,
            'function': function,
            'location': location,
            'infra': infra,
            'itam': itam
        }
    
    print(f"    ✓ Subnet lookup dictionary built: {len(subnet_lookup_dict)} entries")
    return subnet_lookup_dict


def build_itam_name_lookup_dict(itam_df):
    """
    Build optimized ITAM to Name lookup dictionary
    
    Args:
        itam_df: DataFrame containing itam and name columns
        
    Returns:
        dict: Dictionary mapping ITAM to Name
    """
    print("  Building ITAM name lookup dictionary...")
    
    itam_name_dict = {}
    for _, row in itam_df.iterrows():
        itam = str(row['itam']).strip()
        name = row.get('name', None) if pd.notna(row.get('name')) else None
        if name:
            itam_name_dict[itam] = str(name).strip()
    
    print(f"    ✓ ITAM name lookup dictionary built: {len(itam_name_dict)} entries")
    return itam_name_dict


def lookup_ip_info(ip, ip_lookup_dict, itam_name_dict):
    """
    Look up information for a given IP address
    
    Args:
        ip: IP address string
        ip_lookup_dict: Dictionary with IP lookups
        itam_name_dict: Dictionary mapping ITAM to Name
        
    Returns:
        dict: Dictionary with all info or None if not found
    """
    # Normalize IP (remove any /32 if present)
    clean_ip = ip.split('/')[0].strip()
    
    info = ip_lookup_dict.get(clean_ip)
    if info:
        # Add ITAM name if ITAM exists
        result = info.copy()
        if result.get('itam'):
            result['itam_name'] = itam_name_dict.get(str(result['itam']))
        else:
            result['itam_name'] = None
        return result
    
    return None


def lookup_subnet_info(subnet, subnet_lookup_dicts, itam_name_dict):
    """
    Look up information for a given subnet in multiple subnet files
    
    Args:
        subnet: Subnet string (with CIDR notation)
        subnet_lookup_dicts: List of subnet lookup dictionaries to search
        itam_name_dict: Dictionary mapping ITAM to Name
        
    Returns:
        dict: Dictionary with all info or None if not found
    """
    # Normalize subnet
    clean_subnet = subnet.strip()
    
    # Search in all subnet dictionaries in order
    for subnet_dict in subnet_lookup_dicts:
        info = subnet_dict.get(clean_subnet)
        if info:
            # Add ITAM name if ITAM exists
            result = info.copy()
            if result.get('itam'):
                result['itam_name'] = itam_name_dict.get(str(result['itam']))
            else:
                result['itam_name'] = None
            return result
    
    return None


def create_ip_analysis(ip_list, ip_lookup_dict, subnet_lookup_dicts, itam_name_dict):
    """
    Create comprehensive analysis mapping for IPs and subnets
    
    Args:
        ip_list: List of IPs and subnets
        ip_lookup_dict: Dictionary with IP lookups
        subnet_lookup_dicts: List of subnet lookup dictionaries
        itam_name_dict: Dictionary mapping ITAM to Name
        
    Returns:
        dict: Dictionary mapping each IP/subnet to its complete info
    """
    analysis_map = {}
    
    for item in ip_list:
        item_str = str(item).strip()
        
        if not item_str:
            continue
        
        info = None
        
        # Check if it's an IP address (no CIDR) or has /32
        if is_ip_address(item_str) or (is_subnet(item_str) and item_str.endswith('/32')):
            # Look up in IP file
            info = lookup_ip_info(item_str, ip_lookup_dict, itam_name_dict)
        
        # Check if it's a subnet (has CIDR notation and not /32)
        elif is_subnet(item_str):
            # Look up in subnet files
            info = lookup_subnet_info(item_str, subnet_lookup_dicts, itam_name_dict)
        
        # Store the information if found
        if info:
            analysis_map[item_str] = {
                'File Name': info.get('file_name'),
                'Environment': info.get('environment'),
                'Function': info.get('function'),
                'Location': info.get('location'),
                'Infra': info.get('infra'),
                'ITAM ID': info.get('itam'),
                'ITAM Name': info.get('itam_name')
            }
    
    return analysis_map


def analyze_ips(input_file, ip_file, ipam_subnet_file, dev_subnet_file, staging_subnet_file, 
                itam_file, output_file, create_backup=True):
    """
    Main function to analyze IPs and subnets
    
    Args:
        input_file: Path to nfast_rules.xlsx
        ip_file: Path to ip.xlsx
        ipam_subnet_file: Path to ipam_subnet.xlsx
        dev_subnet_file: Path to dev_subnet.xlsx
        staging_subnet_file: Path to staging_subnet.xlsx
        itam_file: Path to itam.xlsx
        output_file: Path to output file
        create_backup: Whether to create a backup of the input file
    """
    
    print("="*80)
    print("COMPREHENSIVE IP AND SUBNET ANALYSIS SCRIPT")
    print("="*80)
    
    # Check if all input files exist
    missing_files = []
    for file, name in [
        (input_file, "Rules file"),
        (ip_file, "IP file"),
        (ipam_subnet_file, "IPAM Subnet file"),
        (dev_subnet_file, "Dev Subnet file"),
        (staging_subnet_file, "Staging Subnet file"),
        (itam_file, "ITAM file")
    ]:
        if not os.path.exists(file):
            missing_files.append(f"{name}: {file}")
    
    if missing_files:
        print("\nERROR: The following files were not found:")
        for file in missing_files:
            print(f"  - {file}")
        print(f"\nCurrent directory: {os.getcwd()}")
        return
    
    print(f"\nInput files:")
    print(f"  Rules file:          {input_file}")
    print(f"  IP file:             {ip_file}")
    print(f"  IPAM Subnet file:    {ipam_subnet_file}")
    print(f"  Dev Subnet file:     {dev_subnet_file}")
    print(f"  Staging Subnet file: {staging_subnet_file}")
    print(f"  ITAM file:           {itam_file}")
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
        
        ip_df = pd.read_excel(ip_file, engine='openpyxl')
        print(f"✓ IP file loaded - {len(ip_df):,} IPs")
        
        ipam_subnet_df = pd.read_excel(ipam_subnet_file, engine='openpyxl')
        print(f"✓ IPAM Subnet file loaded - {len(ipam_subnet_df):,} subnets")
        
        dev_subnet_df = pd.read_excel(dev_subnet_file, engine='openpyxl')
        print(f"✓ Dev Subnet file loaded - {len(dev_subnet_df):,} subnets")
        
        staging_subnet_df = pd.read_excel(staging_subnet_file, engine='openpyxl')
        print(f"✓ Staging Subnet file loaded - {len(staging_subnet_df):,} subnets")
        
        itam_df = pd.read_excel(itam_file, engine='openpyxl')
        print(f"✓ ITAM file loaded - {len(itam_df):,} ITAMs")
    except Exception as e:
        print(f"ERROR: Failed to read files - {e}")
        return
    
    # Verify required columns in rules file
    if 'Source IP' not in rules_df.columns or 'Destination IP' not in rules_df.columns:
        print("\nERROR: 'Source IP' or 'Destination IP' column not found in rules file")
        print(f"Available columns: {list(rules_df.columns)}")
        return
    
    # Build optimized lookup dictionaries
    print("\nBuilding optimized lookup dictionaries...")
    ip_lookup_dict = build_ip_lookup_dict(ip_df)
    
    ipam_subnet_lookup_dict = build_subnet_lookup_dict(ipam_subnet_df, 'ipam_subnet.xlsx')
    dev_subnet_lookup_dict = build_subnet_lookup_dict(dev_subnet_df, 'dev_subnet.xlsx')
    staging_subnet_lookup_dict = build_subnet_lookup_dict(staging_subnet_df, 'staging_subnet.xlsx')
    
    # Order matters: search in IPAM first, then Dev, then Staging
    subnet_lookup_dicts = [ipam_subnet_lookup_dict, dev_subnet_lookup_dict, staging_subnet_lookup_dict]
    
    itam_name_dict = build_itam_name_lookup_dict(itam_df)
    
    print("\n" + "="*80)
    print("PROCESSING ROWS AND ANALYZING IPs/SUBNETS...")
    print("="*80)
    
    stats = {
        'rows_processed': 0,
        'source_ips_found': 0,
        'source_subnets_found': 0,
        'source_total_mapped': 0,
        'dest_ips_found': 0,
        'dest_subnets_found': 0,
        'dest_total_mapped': 0,
        'source_from_ip_file': 0,
        'source_from_ipam': 0,
        'source_from_dev': 0,
        'source_from_staging': 0,
        'dest_from_ip_file': 0,
        'dest_from_ipam': 0,
        'dest_from_dev': 0,
        'dest_from_staging': 0
    }
    
    # Create new columns lists
    source_analysis_list = []
    dest_analysis_list = []
    
    # Process each row - vectorize list parsing for better performance
    print("\nParsing IP lists from all rows...")
    source_ip_lists = rules_df['Source IP'].apply(parse_list_string)
    dest_ip_lists = rules_df['Destination IP'].apply(parse_list_string)
    print(f"  ✓ Parsed IP lists for {len(rules_df):,} rows")
    
    print("\nAnalyzing IPs and subnets...")
    for idx in range(len(rules_df)):
        stats['rows_processed'] += 1
        
        # Get parsed lists
        source_ips = source_ip_lists.iloc[idx]
        dest_ips = dest_ip_lists.iloc[idx]
        
        # Create analysis for source
        source_analysis = create_ip_analysis(source_ips, ip_lookup_dict, subnet_lookup_dicts, itam_name_dict)
        
        # Count findings for source
        for key, val in source_analysis.items():
            stats['source_total_mapped'] += 1
            file_name = val.get('File Name', '')
            
            if '/' in key and not key.endswith('/32'):
                stats['source_subnets_found'] += 1
                if file_name == 'ipam_subnet.xlsx':
                    stats['source_from_ipam'] += 1
                elif file_name == 'dev_subnet.xlsx':
                    stats['source_from_dev'] += 1
                elif file_name == 'staging_subnet.xlsx':
                    stats['source_from_staging'] += 1
            else:
                stats['source_ips_found'] += 1
                if file_name == 'ip.xlsx':
                    stats['source_from_ip_file'] += 1
        
        # Create analysis for destination
        dest_analysis = create_ip_analysis(dest_ips, ip_lookup_dict, subnet_lookup_dicts, itam_name_dict)
        
        # Count findings for destination
        for key, val in dest_analysis.items():
            stats['dest_total_mapped'] += 1
            file_name = val.get('File Name', '')
            
            if '/' in key and not key.endswith('/32'):
                stats['dest_subnets_found'] += 1
                if file_name == 'ipam_subnet.xlsx':
                    stats['dest_from_ipam'] += 1
                elif file_name == 'dev_subnet.xlsx':
                    stats['dest_from_dev'] += 1
                elif file_name == 'staging_subnet.xlsx':
                    stats['dest_from_staging'] += 1
            else:
                stats['dest_ips_found'] += 1
                if file_name == 'ip.xlsx':
                    stats['dest_from_ip_file'] += 1
        
        # Store as string representation of dictionary
        source_analysis_list.append(str(source_analysis) if source_analysis else '{}')
        dest_analysis_list.append(str(dest_analysis) if dest_analysis else '{}')
        
        # Print progress for every 1000 rows
        if (idx + 1) % 1000 == 0:
            print(f"  Processed {idx + 1:,} / {len(rules_df):,} rows ({(idx+1)/len(rules_df)*100:.1f}%)...")
    
    # Add new columns to dataframe
    rules_df['Source IP Analysis'] = source_analysis_list
    rules_df['Destination IP Analysis'] = dest_analysis_list
    
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
    print(f"\n  SOURCE IP/SUBNET ANALYSIS:")
    print(f"    Total mapped:                      {stats['source_total_mapped']:,}")
    print(f"    IPs found:                         {stats['source_ips_found']:,}")
    print(f"      - From ip.xlsx:                  {stats['source_from_ip_file']:,}")
    print(f"    Subnets found:                     {stats['source_subnets_found']:,}")
    print(f"      - From ipam_subnet.xlsx:         {stats['source_from_ipam']:,}")
    print(f"      - From dev_subnet.xlsx:          {stats['source_from_dev']:,}")
    print(f"      - From staging_subnet.xlsx:      {stats['source_from_staging']:,}")
    print(f"\n  DESTINATION IP/SUBNET ANALYSIS:")
    print(f"    Total mapped:                      {stats['dest_total_mapped']:,}")
    print(f"    IPs found:                         {stats['dest_ips_found']:,}")
    print(f"      - From ip.xlsx:                  {stats['dest_from_ip_file']:,}")
    print(f"    Subnets found:                     {stats['dest_subnets_found']:,}")
    print(f"      - From ipam_subnet.xlsx:         {stats['dest_from_ipam']:,}")
    print(f"      - From dev_subnet.xlsx:          {stats['dest_from_dev']:,}")
    print(f"      - From staging_subnet.xlsx:      {stats['dest_from_staging']:,}")
    print("\n✓ IP and Subnet analysis completed successfully!")
    print(f"\nNew columns added:")
    print(f"  - Source IP Analysis")
    print(f"  - Destination IP Analysis")
    print("\nAll original columns have been preserved.")
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
    
    # Run the analysis process
    analyze_ips(INPUT_FILE, IP_FILE, IPAM_SUBNET_FILE, DEV_SUBNET_FILE, 
                STAGING_SUBNET_FILE, ITAM_FILE, OUTPUT_FILE, CREATE_BACKUP)
