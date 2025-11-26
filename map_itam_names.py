import pandas as pd
import numpy as np
from datetime import timedelta
from difflib import SequenceMatcher

def detect_duplicate_incidents(df, time_window_hours=24, similarity_threshold=0.8):
    """
    Detect duplicate or similar incidents in the incident management data.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The incident data
    time_window_hours : int
        Time window in hours to consider incidents as potentially duplicate (default: 24)
    similarity_threshold : float
        Similarity score threshold (0-1) for text comparison (default: 0.8)
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame containing potential duplicate incident groups
    """
    
    # Convert date columns to datetime
    df = df.copy()
    df['opened_at'] = pd.to_datetime(df['opened_at'])
    
    # Sort by opened_at for efficient comparison
    df = df.sort_values('opened_at').reset_index(drop=True)
    
    duplicate_groups = []
    
    # Compare each incident with subsequent incidents within the time window
    for i in range(len(df)):
        incident = df.iloc[i]
        
        # Define time window
        end_time = incident['opened_at'] + timedelta(hours=time_window_hours)
        
        # Get incidents within time window
        mask = (df['opened_at'] > incident['opened_at']) & (df['opened_at'] <= end_time)
        candidates = df[mask]
        
        for j, candidate in candidates.iterrows():
            # Check if incidents are from different users
            different_users = incident['caller_id'] != candidate['caller_id']
            
            # Calculate similarity scores
            similarities = {}
            
            # Short description similarity
            if pd.notna(incident['short_description']) and pd.notna(candidate['short_description']):
                similarities['short_description'] = text_similarity(
                    str(incident['short_description']), 
                    str(candidate['short_description'])
                )
            
            # Description similarity
            if pd.notna(incident['description']) and pd.notna(candidate['description']):
                similarities['description'] = text_similarity(
                    str(incident['description']), 
                    str(candidate['description'])
                )
            
            # Check for matching attributes
            matching_attrs = {
                'category': incident['category'] == candidate['category'],
                'subcategory': incident['subcategory'] == candidate['subcategory'],
                'priority': incident['priority'] == candidate['priority'],
                'caller_location': incident['caller_id.location'] == candidate['caller_id.location'],
                'business_service': incident['business_service'] == candidate['business_service'],
                'affected_country': incident['u_affected_country'] == candidate['u_affected_country']
            }
            
            # Calculate overall similarity score
            text_sim = np.mean([s for s in similarities.values() if s is not None]) if similarities else 0
            attr_match = sum(matching_attrs.values()) / len(matching_attrs)
            overall_score = (text_sim * 0.6 + attr_match * 0.4)
            
            # If similarity exceeds threshold, flag as potential duplicate
            if overall_score >= similarity_threshold:
                time_diff = (candidate['opened_at'] - incident['opened_at']).total_seconds() / 3600
                
                duplicate_groups.append({
                    'incident_1_number': incident['number'],
                    'incident_2_number': candidate['number'],
                    'incident_1_caller': incident['caller_id.user_name'],
                    'incident_2_caller': candidate['caller_id.user_name'],
                    'different_callers': different_users,
                    'time_difference_hours': round(time_diff, 2),
                    'opened_1': incident['opened_at'],
                    'opened_2': candidate['opened_at'],
                    'short_desc_similarity': round(similarities.get('short_description', 0), 3),
                    'description_similarity': round(similarities.get('description', 0), 3),
                    'overall_similarity_score': round(overall_score, 3),
                    'matching_category': matching_attrs['category'],
                    'matching_subcategory': matching_attrs['subcategory'],
                    'matching_priority': matching_attrs['priority'],
                    'short_desc_1': str(incident['short_description'])[:100],
                    'short_desc_2': str(candidate['short_description'])[:100]
                })
    
    # Convert to DataFrame
    duplicates_df = pd.DataFrame(duplicate_groups)
    
    if len(duplicates_df) > 0:
        # Sort by similarity score (descending) and time difference (ascending)
        duplicates_df = duplicates_df.sort_values(
            ['overall_similarity_score', 'time_difference_hours'],
            ascending=[False, True]
        )
    
    return duplicates_df


def text_similarity(text1, text2):
    """Calculate similarity between two text strings using SequenceMatcher."""
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


def generate_duplicate_report(duplicates_df):
    """Generate a summary report of duplicate incidents."""
    if len(duplicates_df) == 0:
        print("No duplicate incidents detected.")
        return
    
    print("=" * 80)
    print("DUPLICATE INCIDENT DETECTION REPORT")
    print("=" * 80)
    print(f"\nTotal potential duplicate pairs found: {len(duplicates_df)}")
    
    # Summary statistics
    print(f"\nDuplicates by different callers: {duplicates_df['different_callers'].sum()}")
    print(f"Duplicates by same caller: {(~duplicates_df['different_callers']).sum()}")
    print(f"\nAverage similarity score: {duplicates_df['overall_similarity_score'].mean():.3f}")
    print(f"Average time difference: {duplicates_df['time_difference_hours'].mean():.2f} hours")
    
    # High confidence duplicates (>90% similarity)
    high_conf = duplicates_df[duplicates_df['overall_similarity_score'] >= 0.9]
    print(f"\nHigh confidence duplicates (≥90% similarity): {len(high_conf)}")
    
    # Show top 10 most similar
    print("\n" + "=" * 80)
    print("TOP 10 MOST SIMILAR INCIDENT PAIRS")
    print("=" * 80)
    
    for idx, row in duplicates_df.head(10).iterrows():
        print(f"\n{idx + 1}. Incidents: {row['incident_1_number']} & {row['incident_2_number']}")
        print(f"   Similarity Score: {row['overall_similarity_score']:.3f}")
        print(f"   Time Difference: {row['time_difference_hours']:.2f} hours")
        print(f"   Callers: {row['incident_1_caller']} & {row['incident_2_caller']}")
        print(f"   Short Desc 1: {row['short_desc_1']}")
        print(f"   Short Desc 2: {row['short_desc_2']}")


# Example usage:
# duplicates = detect_duplicate_incidents(df, time_window_hours=24, similarity_threshold=0.8)
# generate_duplicate_report(duplicates)
# duplicates.to_csv('duplicate_incidents.csv', index=False)
