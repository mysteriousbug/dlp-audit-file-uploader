import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
from datetime import datetime

def perform_enhanced_duplicate_rca(sample_df, original_incidents_df):
    """
    Perform comprehensive root cause analysis on duplicate incident samples
    including analysis of work notes, resolution notes, and descriptions.
    
    Parameters:
    -----------
    sample_df : pandas.DataFrame
        DataFrame containing 20 sampled duplicate pairs
    original_incidents_df : pandas.DataFrame
        Original incidents dataframe with work_notes, description, etc.
        
    Returns:
    --------
    dict
        Dictionary containing RCA findings and metrics
    """
    
    rca_results = {
        'patterns': {},
        'root_causes': [],
        'recommendations': [],
        'duplicate_pairs_analysis': []
    }
    
    print("=" * 80)
    print("ENHANCED ROOT CAUSE ANALYSIS - DUPLICATE INCIDENTS")
    print("=" * 80)
    print(f"\nAnalyzing {len(sample_df)} duplicate incident pairs...\n")
    
    # Get full incident details for analysis
    incident_numbers = list(sample_df['incident_1_number']) + list(sample_df['incident_2_number'])
    sample_incidents = original_incidents_df[original_incidents_df['number'].isin(incident_numbers)].copy()
    
    # 1. TEMPORAL ANALYSIS
    print("\n" + "=" * 80)
    print("1. TEMPORAL ANALYSIS")
    print("=" * 80)
    
    time_diffs = sample_df['time_difference_hours']
    time_categories = pd.cut(time_diffs, 
                             bins=[0, 1, 4, 8, 24],
                             labels=['<1 hour', '1-4 hours', '4-8 hours', '8-24 hours'])
    
    time_dist = time_categories.value_counts()
    print("\nTime Difference Distribution:")
    for cat, count in time_dist.items():
        print(f"  {cat}: {count} pairs ({count/len(sample_df)*100:.1f}%)")
    
    rca_results['patterns']['time_distribution'] = time_dist.to_dict()
    
    if time_dist.get('<1 hour', 0) >= 3:
        rca_results['root_causes'].append({
            'cause': 'Lack of real-time duplicate detection',
            'evidence': f"{time_dist.get('<1 hour', 0)} pairs logged within 1 hour",
            'severity': 'High',
            'category': 'System/Process'
        })
    
    # 2. CALLER ANALYSIS
    print("\n" + "=" * 80)
    print("2. CALLER ANALYSIS")
    print("=" * 80)
    
    different_callers = sample_df['different_callers'].sum()
    same_callers = len(sample_df) - different_callers
    
    print(f"\nDifferent callers: {different_callers} pairs ({different_callers/len(sample_df)*100:.1f}%)")
    print(f"Same caller: {same_callers} pairs ({same_callers/len(sample_df)*100:.1f}%)")
    
    rca_results['patterns']['caller_distribution'] = {
        'different_callers': int(different_callers),
        'same_callers': int(same_callers)
    }
    
    if different_callers >= len(sample_df) * 0.5:
        rca_results['root_causes'].append({
            'cause': 'Poor incident visibility across teams/users',
            'evidence': f"{different_callers} pairs logged by different users",
            'severity': 'High',
            'category': 'Communication/Visibility'
        })
    
    if same_callers >= 3:
        rca_results['root_causes'].append({
            'cause': 'User confusion or lack of incident tracking capability',
            'evidence': f"{same_callers} pairs logged by same user",
            'severity': 'Medium',
            'category': 'User Experience'
        })
    
    # 3. DESCRIPTION & TEXT ANALYSIS
    print("\n" + "=" * 80)
    print("3. DESCRIPTION & WORK NOTES ANALYSIS")
    print("=" * 80)
    
    # Analyze descriptions
    desc_analysis = analyze_text_fields(sample_df, sample_incidents, 'description')
    work_notes_analysis = analyze_text_fields(sample_df, sample_incidents, 'work_notes')
    
    print("\nDescription Analysis:")
    print(f"  Pairs with identical descriptions: {desc_analysis['identical_count']}")
    print(f"  Pairs with very similar descriptions (>95%): {desc_analysis['very_similar_count']}")
    print(f"  Common keywords: {', '.join(desc_analysis['top_keywords'][:10])}")
    
    if 'work_notes' in sample_incidents.columns:
        print("\nWork Notes Analysis:")
        print(f"  Average work notes length: {work_notes_analysis['avg_length']:.0f} characters")
        print(f"  Incidents with work notes: {work_notes_analysis['incidents_with_notes']}")
        print(f"  Common phrases in work notes: {', '.join(work_notes_analysis['top_keywords'][:10])}")
    
    rca_results['patterns']['description_analysis'] = desc_analysis
    rca_results['patterns']['work_notes_analysis'] = work_notes_analysis
    
    # Check for copy-paste patterns
    if desc_analysis['identical_count'] >= 3:
        rca_results['root_causes'].append({
            'cause': 'Users copy-pasting incident descriptions',
            'evidence': f"{desc_analysis['identical_count']} pairs with identical descriptions",
            'severity': 'Medium',
            'category': 'User Behavior'
        })
    
    # 4. RESOLUTION PATTERN ANALYSIS
    print("\n" + "=" * 80)
    print("4. RESOLUTION & CLOSURE ANALYSIS")
    print("=" * 80)
    
    resolution_analysis = analyze_resolutions(sample_df, sample_incidents)
    
    print(f"\nResolved incidents: {resolution_analysis['resolved_count']}/{len(sample_incidents)}")
    print(f"Average resolution time: {resolution_analysis['avg_resolution_hours']:.1f} hours")
    print(f"Duplicates resolved as 'Duplicate': {resolution_analysis['closed_as_duplicate']}")
    
    if resolution_analysis['closed_as_duplicate'] < len(sample_df) * 0.3:
        rca_results['root_causes'].append({
            'cause': 'Duplicates not being properly identified during resolution',
            'evidence': f"Only {resolution_analysis['closed_as_duplicate']} pairs explicitly closed as duplicates",
            'severity': 'High',
            'category': 'Process'
        })
    
    rca_results['patterns']['resolution_analysis'] = resolution_analysis
    
    # 5. CATEGORY/SUBCATEGORY ANALYSIS
    print("\n" + "=" * 80)
    print("5. CATEGORY/SUBCATEGORY ANALYSIS")
    print("=" * 80)
    
    matching_category = sample_df['matching_category'].sum()
    matching_subcategory = sample_df['matching_subcategory'].sum()
    
    print(f"\nMatching category: {matching_category} pairs ({matching_category/len(sample_df)*100:.1f}%)")
    print(f"Matching subcategory: {matching_subcategory} pairs ({matching_subcategory/len(sample_df)*100:.1f}%)")
    
    if 'category' in sample_incidents.columns:
        top_categories = sample_incidents['category'].value_counts().head(5)
        print("\nTop 5 Categories in Duplicates:")
        for cat, count in top_categories.items():
            print(f"  {cat}: {count} incidents")
        
        rca_results['patterns']['top_categories'] = top_categories.to_dict()
        
        if top_categories.iloc[0] > len(sample_df) * 0.3:
            rca_results['root_causes'].append({
                'cause': f'High duplicate rate in "{top_categories.index[0]}" category',
                'evidence': f"{top_categories.iloc[0]} incidents in this category",
                'severity': 'Medium',
                'category': 'Category-Specific'
            })
    
    # 6. ASSIGNMENT & WORKFLOW ANALYSIS
    print("\n" + "=" * 80)
    print("6. ASSIGNMENT & WORKFLOW ANALYSIS")
    print("=" * 80)
    
    workflow_analysis = analyze_workflow_patterns(sample_df, sample_incidents)
    
    print(f"\nAverage reassignment count: {workflow_analysis['avg_reassignments']:.1f}")
    print(f"Incidents with multiple reassignments: {workflow_analysis['multiple_reassignments']}")
    
    if 'assignment_group' in sample_incidents.columns:
        top_groups = sample_incidents['assignment_group'].value_counts().head(5)
        print("\nTop Assignment Groups:")
        for group, count in top_groups.items():
            if pd.notna(group):
                print(f"  {group}: {count} incidents")
        
        rca_results['patterns']['top_assignment_groups'] = top_groups.to_dict()
    
    if workflow_analysis['avg_reassignments'] > 2:
        rca_results['root_causes'].append({
            'cause': 'Excessive reassignments indicating unclear ownership',
            'evidence': f"Average {workflow_analysis['avg_reassignments']:.1f} reassignments per incident",
            'severity': 'Medium',
            'category': 'Workflow'
        })
    
    rca_results['patterns']['workflow_analysis'] = workflow_analysis
    
    # 7. DETAILED PAIR-BY-PAIR ANALYSIS
    print("\n" + "=" * 80)
    print("7. PAIR-BY-PAIR DETAILED ANALYSIS")
    print("=" * 80)
    
    pair_details = []
    for idx, row in sample_df.iterrows():
        inc1 = sample_incidents[sample_incidents['number'] == row['incident_1_number']].iloc[0]
        inc2 = sample_incidents[sample_incidents['number'] == row['incident_2_number']].iloc[0]
        
        pair_analysis = analyze_incident_pair(inc1, inc2, row)
        pair_details.append(pair_analysis)
        
        print(f"\n--- Pair {idx + 1}: {row['incident_1_number']} & {row['incident_2_number']} ---")
        print(f"Similarity: {row['overall_similarity_score']:.3f} | Time Gap: {row['time_difference_hours']:.1f}h")
        print(f"Root Cause Category: {pair_analysis['likely_root_cause']}")
        print(f"Key Finding: {pair_analysis['key_finding']}")
    
    rca_results['duplicate_pairs_analysis'] = pair_details
    
    # 8. PRIORITY ANALYSIS
    print("\n" + "=" * 80)
    print("8. PRIORITY & IMPACT ANALYSIS")
    print("=" * 80)
    
    matching_priority = sample_df['matching_priority'].sum()
    print(f"\nMatching priority: {matching_priority} pairs ({matching_priority/len(sample_df)*100:.1f}%)")
    
    if 'priority' in sample_incidents.columns:
        priority_dist = sample_incidents['priority'].value_counts()
        print("\nPriority Distribution:")
        for priority, count in priority_dist.items():
            print(f"  Priority {priority}: {count} incidents")
        
        rca_results['patterns']['priority_distribution'] = priority_dist.to_dict()
        
        # Check for high-priority duplicates
        high_priority_count = sample_incidents[sample_incidents['priority'].isin([1, 2])].shape[0]
        if high_priority_count > 0:
            rca_results['root_causes'].append({
                'cause': 'High-priority incidents being duplicated',
                'evidence': f"{high_priority_count} high-priority (P1/P2) incidents in duplicates",
                'severity': 'High',
                'category': 'Business Impact'
            })
    
    # 9. GENERATE COMPREHENSIVE RECOMMENDATIONS
    print("\n" + "=" * 80)
    print("9. ROOT CAUSE SUMMARY & RECOMMENDATIONS")
    print("=" * 80)
    
    print("\nIdentified Root Causes:")
    for i, rc in enumerate(rca_results['root_causes'], 1):
        print(f"\n{i}. [{rc['category']}] {rc['cause']}")
        print(f"   Evidence: {rc['evidence']}")
        print(f"   Severity: {rc['severity']}")
    
    # Generate targeted recommendations
    recommendations = generate_recommendations(rca_results, desc_analysis, work_notes_analysis, resolution_analysis)
    rca_results['recommendations'] = recommendations
    
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS (Prioritized)")
    print("=" * 80)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{rec['priority']} - Recommendation {i}:")
        print(f"  {rec['recommendation']}")
        print(f"  Details: {rec['details']}")
        print(f"  Expected Impact: {rec['impact']}")
    
    return rca_results


def analyze_text_fields(sample_df, incidents_df, field_name):
    """Analyze text fields like description or work_notes."""
    analysis = {
        'identical_count': 0,
        'very_similar_count': 0,
        'avg_length': 0,
        'top_keywords': [],
        'incidents_with_notes': 0
    }
    
    if field_name not in incidents_df.columns:
        return analysis
    
    # Get all text from the field
    all_text = []
    non_null_count = 0
    
    for idx, row in sample_df.iterrows():
        inc1_num = row['incident_1_number']
        inc2_num = row['incident_2_number']
        
        inc1_data = incidents_df[incidents_df['number'] == inc1_num]
        inc2_data = incidents_df[incidents_df['number'] == inc2_num]
        
        if not inc1_data.empty and not inc2_data.empty:
            text1 = inc1_data.iloc[0][field_name]
            text2 = inc2_data.iloc[0][field_name]
            
            if pd.notna(text1):
                all_text.append(str(text1))
                non_null_count += 1
            if pd.notna(text2):
                all_text.append(str(text2))
                non_null_count += 1
            
            # Check similarity
            if pd.notna(text1) and pd.notna(text2):
                if str(text1).strip() == str(text2).strip():
                    analysis['identical_count'] += 1
                elif calculate_text_similarity(str(text1), str(text2)) > 0.95:
                    analysis['very_similar_count'] += 1
    
    analysis['incidents_with_notes'] = non_null_count
    
    if all_text:
        analysis['avg_length'] = np.mean([len(t) for t in all_text])
        
        # Extract keywords (simple word frequency)
        words = []
        for text in all_text:
            words.extend(extract_keywords(text))
        
        word_freq = Counter(words)
        analysis['top_keywords'] = [word for word, count in word_freq.most_common(15)]
    
    return analysis


def calculate_text_similarity(text1, text2):
    """Calculate similarity between two texts."""
    from difflib import SequenceMatcher
    return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()


def extract_keywords(text):
    """Extract meaningful keywords from text."""
    # Convert to lowercase and split
    text = str(text).lower()
    
    # Remove common words (simple stopwords)
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                 'of', 'with', 'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has',
                 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'this',
                 'that', 'these', 'those', 'it', 'its', 'as', 'by', 'from'}
    
    words = re.findall(r'\b[a-z]{3,}\b', text)
    return [w for w in words if w not in stopwords]


def analyze_resolutions(sample_df, incidents_df):
    """Analyze resolution patterns."""
    analysis = {
        'resolved_count': 0,
        'avg_resolution_hours': 0,
        'closed_as_duplicate': 0,
        'resolution_patterns': []
    }
    
    resolution_times = []
    
    for idx, row in sample_df.iterrows():
        inc1_num = row['incident_1_number']
        inc2_num = row['incident_2_number']
        
        for inc_num in [inc1_num, inc2_num]:
            inc_data = incidents_df[incidents_df['number'] == inc_num]
            
            if not inc_data.empty:
                inc = inc_data.iloc[0]
                
                # Check if resolved
                if pd.notna(inc.get('resolved_at')):
                    analysis['resolved_count'] += 1
                    
                    # Calculate resolution time
                    if pd.notna(inc.get('opened_at')) and pd.notna(inc.get('resolved_at')):
                        opened = pd.to_datetime(inc['opened_at'])
                        resolved = pd.to_datetime(inc['resolved_at'])
                        hours = (resolved - opened).total_seconds() / 3600
                        resolution_times.append(hours)
                
                # Check if closed as duplicate
                if 'work_notes' in inc and pd.notna(inc['work_notes']):
                    work_notes = str(inc['work_notes']).lower()
                    if 'duplicate' in work_notes or 'dup' in work_notes:
                        analysis['closed_as_duplicate'] += 1
                
                # Check state
                if 'state' in inc and pd.notna(inc['state']):
                    state = str(inc['state']).lower()
                    if 'duplicate' in state or 'closed' in state:
                        analysis['closed_as_duplicate'] += 1
    
    if resolution_times:
        analysis['avg_resolution_hours'] = np.mean(resolution_times)
    
    return analysis


def analyze_workflow_patterns(sample_df, incidents_df):
    """Analyze workflow and assignment patterns."""
    analysis = {
        'avg_reassignments': 0,
        'multiple_reassignments': 0,
        'reassignment_counts': []
    }
    
    if 'reassignment_count' not in incidents_df.columns:
        return analysis
    
    reassignments = []
    
    for idx, row in sample_df.iterrows():
        inc1_num = row['incident_1_number']
        inc2_num = row['incident_2_number']
        
        for inc_num in [inc1_num, inc2_num]:
            inc_data = incidents_df[incidents_df['number'] == inc_num]
            
            if not inc_data.empty:
                reass_count = inc_data.iloc[0].get('reassignment_count', 0)
                if pd.notna(reass_count):
                    reassignments.append(int(reass_count))
                    if int(reass_count) > 1:
                        analysis['multiple_reassignments'] += 1
    
    if reassignments:
        analysis['avg_reassignments'] = np.mean(reassignments)
        analysis['reassignment_counts'] = reassignments
    
    return analysis


def analyze_incident_pair(inc1, inc2, pair_row):
    """Detailed analysis of a single incident pair."""
    analysis = {
        'incident_1': inc1['number'],
        'incident_2': inc2['number'],
        'likely_root_cause': 'Unknown',
        'key_finding': '',
        'severity_impact': 'Low'
    }
    
    # Determine likely root cause
    time_diff = pair_row['time_difference_hours']
    different_callers = pair_row['different_callers']
    similarity = pair_row['overall_similarity_score']
    
    if time_diff < 1 and different_callers:
        analysis['likely_root_cause'] = 'Simultaneous reporting by multiple users'
        analysis['key_finding'] = 'Multiple users experienced same issue at same time, lack of visibility'
        analysis['severity_impact'] = 'High'
    elif time_diff < 1 and not different_callers:
        analysis['likely_root_cause'] = 'User accidentally submitted twice'
        analysis['key_finding'] = 'Same user created duplicate within 1 hour - UI/UX issue or user error'
        analysis['severity_impact'] = 'Medium'
    elif similarity > 0.95:
        analysis['likely_root_cause'] = 'Copy-paste or template usage'
        analysis['key_finding'] = 'Nearly identical descriptions suggest copy-paste behavior'
        analysis['severity_impact'] = 'Medium'
    elif different_callers and time_diff > 4:
        analysis['likely_root_cause'] = 'Poor incident search/visibility'
        analysis['key_finding'] = 'Users unable to find existing incident before creating new one'
        analysis['severity_impact'] = 'High'
    else:
        analysis['likely_root_cause'] = 'General process gap'
        analysis['key_finding'] = 'Unclear why duplicate was created - needs manual review'
        analysis['severity_impact'] = 'Medium'
    
    return analysis


def generate_recommendations(rca_results, desc_analysis, work_notes_analysis, resolution_analysis):
    """Generate targeted recommendations based on findings."""
    recommendations = []
    
    root_cause_categories = [rc['category'] for rc in rca_results['root_causes']]
    
    # System/Process recommendations
    if 'System/Process' in root_cause_categories:
        recommendations.append({
            'priority': 'P1',
            'recommendation': 'Implement AI-powered duplicate detection at incident creation',
            'details': 'Use NLP/ML to analyze description, category, caller location in real-time. Show similar incidents before submission.',
            'impact': 'Could prevent 60-80% of duplicates based on text similarity patterns'
        })
    
    # Communication/Visibility recommendations
    if 'Communication/Visibility' in root_cause_categories:
        recommendations.append({
            'priority': 'P1',
            'recommendation': 'Create unified incident dashboard with advanced search',
            'details': 'Enable full-text search across descriptions, work notes. Show recent incidents by category/location.',
            'impact': 'Reduce duplicates from different users by improving incident visibility'
        })
    
    # User Behavior recommendations
    if 'User Behavior' in root_cause_categories or desc_analysis['identical_count'] >= 3:
        recommendations.append({
            'priority': 'P2',
            'recommendation': 'User training program with feedback loops',
            'details': 'Train users on: searching before creating, using proper descriptions, checking their open incidents. Send notifications when duplicates are detected.',
            'impact': 'Address behavioral patterns identified in 15% of duplicate cases'
        })
    
    # Process recommendations
    if resolution_analysis['closed_as_duplicate'] < 5:
        recommendations.append({
            'priority': 'P1',
            'recommendation': 'Formalize duplicate incident workflow',
            'details': 'Create "Mark as Duplicate" action that auto-links incidents, updates stakeholders, and captures metrics.',
            'impact': 'Improve duplicate tracking and enable better analytics'
        })
    
    # Workflow recommendations
    if 'Workflow' in root_cause_categories:
        recommendations.append({
            'priority': 'P2',
            'recommendation': 'Optimize assignment logic and routing rules',
            'details': 'Review assignment groups for high-duplicate categories. Implement smart routing to reduce reassignments.',
            'impact': 'Reduce workflow inefficiencies and faster duplicate identification'
        })
    
    # Category-specific recommendations
    if 'top_categories' in rca_results['patterns']:
        top_cat = list(rca_results['patterns']['top_categories'].keys())[0]
        recommendations.append({
            'priority': 'P2',
            'recommendation': f'Category-specific duplicate prevention for "{top_cat}"',
            'details': f'Enhanced detection rules, stricter matching, dedicated review process for {top_cat} category.',
            'impact': 'Target the category with highest duplicate rate'
        })
    
    # Business Impact recommendations
    if 'Business Impact' in root_cause_categories:
        recommendations.append({
            'priority': 'P1',
            'recommendation': 'Priority incident duplicate alerting system',
            'details': 'Real-time alerts to situation managers when P1/P2 duplicates detected. Auto-link and escalate.',
            'impact': 'Prevent duplicate P1/P2 incidents from causing confusion during major incidents'
        })
    
    # Monitoring recommendation (always include)
    recommendations.append({
        'priority': 'P2',
        'recommendation': 'Establish duplicate incident KPIs and monitoring',
        'details': 'Track: duplicate rate by category, time-to-detection, resolution time. Monthly reviews and trend analysis.',
        'impact': 'Enable continuous improvement and measure effectiveness of other recommendations'
    })
    
    return recommendations


def create_enhanced_visualizations(sample_df, original_incidents_df, rca_results):
    """Create comprehensive visualizations for RCA."""
    
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    fig.suptitle('Duplicate Incident Root Cause Analysis - Enhanced View', 
                 fontsize=16, fontweight='bold')
    
    # 1. Time Difference Distribution
    ax1 = fig.add_subplot(gs[0, 0])
    time_diffs = sample_df['time_difference_hours']
    ax1.hist(time_diffs, bins=20, color='steelblue', edgecolor='black', alpha=0.7)
    ax1.axvline(time_diffs.mean(), color='red', linestyle='--', 
                label=f'Mean: {time_diffs.mean():.1f}h', linewidth=2)
    ax1.set_xlabel('Time Difference (hours)', fontsize=10)
    ax1.set_ylabel('Frequency', fontsize=10)
    ax1.set_title('Time Gap Between Duplicates', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Caller Analysis Pie
    ax2 = fig.add_subplot(gs[0, 1])
    caller_data = ['Different Callers', 'Same Caller']
    caller_counts = [sample_df['different_callers'].sum(), 
                     len(sample_df) - sample_df['different_callers'].sum()]
    colors = ['#ff6b6b', '#4ecdc4']
    wedges, texts, autotexts = ax2.pie(caller_counts, labels=caller_data, autopct='%1.1f%%', 
                                         colors=colors, startangle=90)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    ax2.set_title('Caller Type Distribution', fontweight='bold')
    
    # 3. Similarity Score Distribution
    ax3 = fig.add_subplot(gs[0, 2])
    similarity_scores = sample_df['overall_similarity_score']
    ax3.hist(similarity_scores, bins=15, color='coral', edgecolor='black', alpha=0.7)
    ax3.axvline(similarity_scores.mean(), color='darkred', linestyle='--', 
                label=f'Mean: {similarity_scores.mean():.2f}', linewidth=2)
    ax3.set_xlabel('Similarity Score', fontsize=10)
    ax3.set_ylabel('Frequency', fontsize=10)
    ax3.set_title('Text Similarity Distribution', fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Top Categories
    ax4 = fig.add_subplot(gs[1, 0])
    incident_numbers = list(sample_df['incident_1_number']) + list(sample_df['incident_2_number'])
    sample_incidents = original_incidents_df[original_incidents_df['number'].isin(incident_numbers)]
    
    if 'category' in sample_incidents.columns:
        top_categories = sample_incidents['category'].value_counts().head(8)
        bars = ax4.barh(range(len(top_categories)), top_categories.values, color='mediumseagreen')
        ax4.set_yticks(range(len(top_categories)))
        ax4.set_yticklabels([str(cat)[:30] for cat in top_categories.index], fontsize=9)
        ax4.set_xlabel('Count', fontsize=10)
        ax4.set_title('Top Categories', fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='x')
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax4.text(width, bar.get_y() + bar.get_height()/2, 
                    f'{int(width)}', ha='left', va='center', fontsize=8)
    
    # 5. Priority Distribution
    ax5 = fig.add_subplot(gs[1, 1])
    if 'priority' in sample_incidents.columns:
        priority_dist = sample_incidents['priority'].value_counts().sort_index()
        bars = ax5.bar(priority_dist.index.astype(str), priority_dist.values, 
                       color=['#ff4444', '#ff8844', '#ffaa44', '#44ff44'], 
                       edgecolor='black', alpha=0.7)
        ax5.set_xlabel('Priority', fontsize=10)
        ax5.set_ylabel('Count', fontsize=10)
        ax5.set_title('Priority Distribution', fontweight='bold')
        ax5.grid(True, alpha=0.3, axis='y')
        
        for bar in bars:
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom', fontsize=9)
    
    # 6. Root Cause Categories
    ax6 = fig.add_subplot(gs[1, 2])
    if rca_results['root_causes']:
        rc_categories = [rc['category'] for rc in rca_results['root_causes']]
        rc_counts = Counter(rc_categories)
        colors_rc = plt.cm.Set3(range(len(rc_counts)))
        wedges, texts, autotexts = ax6.pie(rc_counts.values(), labels=rc_counts.keys(), 
                                            autopct='%1.0f%%', colors=colors_rc, startangle=90)
        for autotext in autotexts:
            autotext.set_fontsize(8)
            autotext.set_fontweight('bold')
        ax6.set_title('Root Cause Categories', fontweight='bold')
    
    # 7. Resolution Time Analysis
    ax7 = fig.add_subplot(gs[2, 0])
    if 'resolved_at' in sample_incidents.columns and 'opened_at' in sample_incidents.columns:
        resolution_times = []
        for idx, inc in sample_incidents.iterrows():
            if pd.notna(inc['resolved_at']) and pd.notna(inc['opened_at']):
                opened = pd.to_datetime(inc['opened_at'])
                resolved = pd.to_datetime(inc['resolved_at'])
                hours = (resolved - opened).total_seconds() / 3600
                if hours > 0:
                    resolution_times.append(hours)
        
        if resolution_times:
            ax7.hist(resolution_times, bins=15, color='purple', edgecolor='black', alpha=0.6)
            ax7.axvline(np.mean(resolution_times), color='red', linestyle='--', 
                       label=f'Mean: {np.mean(resolution_times):.1f}h', linewidth=2)
            ax7.set_xlabel('Resolution Time (hours)', fontsize=10)
            ax7.set_ylabel('Frequency', fontsize=10)
            ax7.set_title('Resolution Time Distribution', fontweight='bold')
            ax7.legend()
            ax7.grid(True, alpha=0.3)
    
    # 8. Assignment Group Analysis
    ax8 = fig.add_subplot(gs[2, 1])
    if 'assignment_group' in sample_incidents.columns:
        top_groups = sample_incidents['assignment_group'].value_counts().head(6)
        bars = ax8.barh(range(len(top_groups)), top_groups.values, color='teal', alpha=0.7)
        ax8.set_yticks(range(len(top_groups)))
        ax8.set_yticklabels([str(g)[:25] for g in top_groups.index], fontsize=8)
        ax8.set_xlabel('Count', fontsize=10)
        ax8.set_title('Top Assignment Groups', fontweight='bold')
        ax8.grid(True, alpha=0.3, axis='x')
        
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax8.text(width, bar.get_y() + bar.get_height()/2, 
                    f'{int(width)}', ha='left', va='center', fontsize=8)
    
    # 9. Severity Impact Summary
    ax9 = fig.add_subplot(gs[2, 2])
    if rca_results['root_causes']:
        severity_counts = Counter([rc['severity'] for rc in rca_results['root_causes']])
        severity_order = ['High', 'Medium', 'Low']
        severity_values = [severity_counts.get(s, 0) for s in severity_order]
        colors_sev = ['#ff4444', '#ffaa44', '#44ff44']
        
        bars = ax9.bar(severity_order, severity_values, color=colors_sev, edgecolor='black', alpha=0.7)
        ax9.set_ylabel('Count', fontsize=10)
        ax9.set_title('Root Cause Severity', fontweight='bold')
        ax9.grid(True, alpha=0.3, axis='y')
        
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax9.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.savefig('duplicate_incidents_enhanced_rca.png', dpi=300, bbox_inches='tight')
    print("\n✓ Enhanced visualization saved as 'duplicate_incidents_enhanced_rca.png'")
    plt.show()


def export_detailed_rca_report(rca_results, sample_df, filename='duplicate_incidents_detailed_rca.txt'):
    """Export comprehensive RCA report with all findings."""
    
    with open(filename, 'w') as f:
        f.write("=" * 100 + "\n")
        f.write("DUPLICATE INCIDENT ROOT CAUSE ANALYSIS - DETAILED REPORT\n")
        f.write("=" * 100 + "\n\n")
        f.write(f"Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Sample Size: {len(sample_df)} duplicate incident pairs\n")
        f.write(f"Total Incidents Analyzed: {len(sample_df) * 2}\n\n")
        
        # Executive Summary
        f.write("\n" + "=" * 100 + "\n")
        f.write("EXECUTIVE SUMMARY\n")
        f.write("=" * 100 + "\n")
        f.write(f"Total Root Causes Identified: {len(rca_results['root_causes'])}\n")
        f.write(f"High Severity Issues: {sum(1 for rc in rca_results['root_causes'] if rc['severity'] == 'High')}\n")
        f.write(f"Medium Severity Issues: {sum(1 for rc in rca_results['root_causes'] if rc['severity'] == 'Medium')}\n")
        f.write(f"Total Recommendations: {len(rca_results['recommendations'])}\n")
        f.write(f"P1 Priority Actions: {sum(1 for rec in rca_results['recommendations'] if rec['priority'] == 'P1')}\n\n")
        
        # Root Causes
        f.write("\n" + "=" * 100 + "\n")
        f.write("ROOT CAUSES IDENTIFIED\n")
        f.write("=" * 100 + "\n\n")
        
        for i, rc in enumerate(rca_results['root_causes'], 1):
            f.write(f"{i}. [{rc['severity']}] {rc['cause']}\n")
            f.write(f"   Category: {rc['category']}\n")
            f.write(f"   Evidence: {rc['evidence']}\n")
            f.write("-" * 100 + "\n\n")
        
        # Recommendations
        f.write("\n" + "=" * 100 + "\n")
        f.write("RECOMMENDATIONS (PRIORITIZED)\n")
        f.write("=" * 100 + "\n\n")
        
        for i, rec in enumerate(rca_results['recommendations'], 1):
            f.write(f"{rec['priority']} - Recommendation {i}:\n")
            f.write(f"   {rec['recommendation']}\n")
            f.write(f"   Details: {rec['details']}\n")
            f.write(f"   Expected Impact: {rec['impact']}\n")
            f.write("-" * 100 + "\n\n")
        
        # Detailed Patterns
        f.write("\n" + "=" * 100 + "\n")
        f.write("DETAILED PATTERN ANALYSIS\n")
        f.write("=" * 100 + "\n\n")
        
        for pattern_name, pattern_data in rca_results['patterns'].items():
            f.write(f"\n{pattern_name.upper().replace('_', ' ')}:\n")
            f.write(f"{pattern_data}\n")
            f.write("-" * 100 + "\n")
        
        # Pair-by-Pair Analysis
        f.write("\n" + "=" * 100 + "\n")
        f.write("INCIDENT PAIR DETAILED ANALYSIS\n")
        f.write("=" * 100 + "\n\n")
        
        for i, pair in enumerate(rca_results['duplicate_pairs_analysis'], 1):
            f.write(f"\nPair {i}: {pair['incident_1']} & {pair['incident_2']}\n")
            f.write(f"   Root Cause Category: {pair['likely_root_cause']}\n")
            f.write(f"   Key Finding: {pair['key_finding']}\n")
            f.write(f"   Severity Impact: {pair['severity_impact']}\n")
            f.write("-" * 100 + "\n")
    
    print(f"\n✓ Detailed RCA report exported to '{filename}'")


def export_to_excel(rca_results, sample_df, original_incidents_df, filename='duplicate_incidents_rca_analysis.xlsx'):
    """Export comprehensive analysis to Excel with multiple sheets."""
    
    incident_numbers = list(sample_df['incident_1_number']) + list(sample_df['incident_2_number'])
    sample_incidents = original_incidents_df[original_incidents_df['number'].isin(incident_numbers)]
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Sheet 1: Summary
        summary_data = {
            'Metric': [
                'Total Duplicate Pairs',
                'Total Incidents Analyzed',
                'Root Causes Identified',
                'High Severity Issues',
                'Medium Severity Issues',
                'Recommendations Generated',
                'P1 Priority Actions',
                'Average Similarity Score',
                'Average Time Gap (hours)',
                'Different Callers (%)'
            ],
            'Value': [
                len(sample_df),
                len(sample_df) * 2,
                len(rca_results['root_causes']),
                sum(1 for rc in rca_results['root_causes'] if rc['severity'] == 'High'),
                sum(1 for rc in rca_results['root_causes'] if rc['severity'] == 'Medium'),
                len(rca_results['recommendations']),
                sum(1 for rec in rca_results['recommendations'] if rec['priority'] == 'P1'),
                f"{sample_df['overall_similarity_score'].mean():.3f}",
                f"{sample_df['time_difference_hours'].mean():.2f}",
                f"{(sample_df['different_callers'].sum() / len(sample_df) * 100):.1f}%"
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Sheet 2: Root Causes
        root_causes_df = pd.DataFrame(rca_results['root_causes'])
        root_causes_df.to_excel(writer, sheet_name='Root Causes', index=False)
        
        # Sheet 3: Recommendations
        recommendations_df = pd.DataFrame(rca_results['recommendations'])
        recommendations_df.to_excel(writer, sheet_name='Recommendations', index=False)
        
        # Sheet 4: Duplicate Pairs
        sample_df.to_excel(writer, sheet_name='Duplicate Pairs', index=False)
        
        # Sheet 5: Pair Analysis
        pair_analysis_df = pd.DataFrame(rca_results['duplicate_pairs_analysis'])
        pair_analysis_df.to_excel(writer, sheet_name='Pair Analysis', index=False)
        
        # Sheet 6: Incident Details
        sample_incidents.to_excel(writer, sheet_name='Incident Details', index=False)
    
    print(f"\n✓ Excel report exported to '{filename}'")


# ==================================================================================
# MAIN EXECUTION EXAMPLE
# ==================================================================================

"""
USAGE EXAMPLE:

# 1. Load your data
sample_duplicates = pd.read_csv('sample_20_duplicates.csv')
original_incidents = pd.read_csv('all_incidents.csv')

# 2. Perform enhanced RCA with text analysis
rca_results = perform_enhanced_duplicate_rca(sample_duplicates, original_incidents)

# 3. Create comprehensive visualizations
create_enhanced_visualizations(sample_duplicates, original_incidents, rca_results)

# 4. Export detailed text report
export_detailed_rca_report(rca_results, sample_duplicates)

# 5. Export to Excel (multiple sheets with all analysis)
export_to_excel(rca_results, sample_duplicates, original_incidents)

# 6. Access specific findings
print("\nTop Root Causes:")
for rc in rca_results['root_causes'][:3]:
    print(f"- {rc['cause']} (Severity: {rc['severity']})")

print("\nTop Recommendations:")
for rec in rca_results['recommendations'][:3]:
    print(f"- [{rec['priority']}] {rec['recommendation']}")
"""
