"""
MyVoice 2025 Survey - NLP Sentiment Analysis Script
Analyzes free-text responses using NLP techniques including sentiment analysis,
theme identification, and visualization.

Requirements: Run locally only, input CSV with questions in Column 1 and responses in Column 2
"""

import pandas as pd
import numpy as np
import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns
from collections import Counter
import warnings
import os
import re

warnings.filterwarnings('ignore')

# Set style for visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)


class MyVoiceNLPAnalyzer:
    """
    Comprehensive NLP analyzer for MyVoice survey responses
    """
    
    def __init__(self, csv_file_path):
        """
        Initialize the analyzer with CSV file path
        
        Args:
            csv_file_path (str): Path to CSV file with questions and responses
        """
        self.csv_path = csv_file_path
        self.df = None
        self.all_responses = []
        self.processed_responses = []
        self.nlp = None
        self.vader = SentimentIntensityAnalyzer()
        self.vectorizer = None
        self.tfidf_matrix = None
        self.clusters = None
        self.output_dir = "myvoice_analysis_output"
        
        # Create output directory
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def load_data(self):
        """Load and parse CSV data"""
        print("Loading data from CSV...")
        self.df = pd.read_csv(self.csv_path)
        
        # Assuming Column 0 is questions, Column 1 is responses
        self.df.columns = ['Question', 'Responses']
        
        # Parse responses - assuming each cell contains multiple responses separated by newlines or delimiters
        all_responses_list = []
        
        for idx, row in self.df.iterrows():
            question = row['Question']
            responses_text = str(row['Responses'])
            
            # Split responses (adjust delimiter based on your data format)
            # Common delimiters: newline, semicolon, pipe
            individual_responses = self._split_responses(responses_text)
            
            for response in individual_responses:
                if response.strip():  # Only add non-empty responses
                    all_responses_list.append({
                        'question_id': idx + 1,
                        'question': question,
                        'response': response.strip()
                    })
        
        self.all_responses = pd.DataFrame(all_responses_list)
        print(f"Loaded {len(self.all_responses)} total responses from {len(self.df)} questions")
        
        return self.all_responses
    
    def _split_responses(self, text):
        """Split response text into individual responses"""
        # Try multiple delimiters
        if '\n' in text:
            return text.split('\n')
        elif ';' in text:
            return text.split(';')
        elif '|' in text:
            return text.split('|')
        else:
            # If no delimiter found, treat as single response
            return [text]
    
    def initialize_nlp(self):
        """Initialize spaCy model"""
        print("Initializing spaCy NLP model...")
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Downloading spaCy model...")
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        print("NLP model loaded successfully")
    
    def preprocess_text(self, text):
        """
        Preprocess text using spaCy
        
        Args:
            text (str): Raw text
            
        Returns:
            str: Preprocessed text
        """
        doc = self.nlp(text.lower())
        
        # Remove stopwords, punctuation, and lemmatize
        tokens = [token.lemma_ for token in doc 
                 if not token.is_stop 
                 and not token.is_punct 
                 and not token.is_space
                 and len(token.text) > 2]
        
        return ' '.join(tokens)
    
    def perform_sentiment_analysis(self):
        """Perform VADER sentiment analysis on all responses"""
        print("Performing sentiment analysis...")
        
        sentiments = []
        for text in self.all_responses['response']:
            scores = self.vader.polarity_scores(text)
            sentiments.append({
                'negative': scores['neg'],
                'neutral': scores['neu'],
                'positive': scores['pos'],
                'compound': scores['compound'],
                'sentiment': self._classify_sentiment(scores['compound'])
            })
        
        sentiment_df = pd.DataFrame(sentiments)
        self.all_responses = pd.concat([self.all_responses, sentiment_df], axis=1)
        
        print(f"Sentiment analysis complete:")
        print(f"  Positive: {len(sentiment_df[sentiment_df['sentiment'] == 'Positive'])}")
        print(f"  Neutral: {len(sentiment_df[sentiment_df['sentiment'] == 'Neutral'])}")
        print(f"  Negative: {len(sentiment_df[sentiment_df['sentiment'] == 'Negative'])}")
        
        return self.all_responses
    
    def _classify_sentiment(self, compound_score):
        """Classify sentiment based on compound score"""
        if compound_score >= 0.05:
            return 'Positive'
        elif compound_score <= -0.05:
            return 'Negative'
        else:
            return 'Neutral'
    
    def extract_features(self):
        """Extract TF-IDF features from preprocessed text"""
        print("Extracting TF-IDF features...")
        
        # Preprocess all responses
        self.processed_responses = [
            self.preprocess_text(text) for text in self.all_responses['response']
        ]
        
        # Create TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=100,
            min_df=2,
            max_df=0.8,
            ngram_range=(1, 2)
        )
        
        self.tfidf_matrix = self.vectorizer.fit_transform(self.processed_responses)
        
        print(f"Extracted {self.tfidf_matrix.shape[1]} features from {self.tfidf_matrix.shape[0]} responses")
        
        return self.tfidf_matrix
    
    def identify_themes_kmeans(self, n_clusters=5):
        """
        Identify themes using KMeans clustering
        
        Args:
            n_clusters (int): Number of clusters/themes to identify
        """
        print(f"Identifying {n_clusters} themes using KMeans clustering...")
        
        # Perform KMeans clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.clusters = kmeans.fit_predict(self.tfidf_matrix)
        
        # Add cluster labels to dataframe
        self.all_responses['theme_cluster'] = self.clusters
        
        # Get top terms per cluster
        feature_names = self.vectorizer.get_feature_names_out()
        cluster_centers = kmeans.cluster_centers_
        
        themes = {}
        for i in range(n_clusters):
            top_indices = cluster_centers[i].argsort()[-10:][::-1]
            top_terms = [feature_names[idx] for idx in top_indices]
            themes[f'Theme {i+1}'] = top_terms
            
            print(f"\nTheme {i+1} - Top terms: {', '.join(top_terms[:5])}")
            print(f"  Number of responses: {len(self.all_responses[self.all_responses['theme_cluster'] == i])}")
        
        return themes
    
    def perform_lda_topic_modeling(self, n_topics=5):
        """
        Perform LDA topic modeling
        
        Args:
            n_topics (int): Number of topics to extract
        """
        print(f"\nPerforming LDA topic modeling with {n_topics} topics...")
        
        lda = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42,
            max_iter=20
        )
        
        lda_output = lda.fit_transform(self.tfidf_matrix)
        
        # Get top words for each topic
        feature_names = self.vectorizer.get_feature_names_out()
        topics = {}
        
        for topic_idx, topic in enumerate(lda.components_):
            top_indices = topic.argsort()[-10:][::-1]
            top_words = [feature_names[i] for i in top_indices]
            topics[f'Topic {topic_idx + 1}'] = top_words
            
            print(f"\nTopic {topic_idx + 1}: {', '.join(top_words[:5])}")
        
        # Assign dominant topic to each response
        dominant_topics = lda_output.argmax(axis=1)
        self.all_responses['lda_topic'] = dominant_topics
        
        return topics, lda_output
    
    def generate_wordcloud(self, cluster_id=None):
        """
        Generate word cloud for all responses or specific cluster
        
        Args:
            cluster_id (int): Specific cluster to generate wordcloud for (None for all)
        """
        if cluster_id is not None:
            text_data = ' '.join(
                self.all_responses[self.all_responses['theme_cluster'] == cluster_id]['response']
            )
            title = f'Word Cloud - Theme {cluster_id + 1}'
            filename = f'wordcloud_theme_{cluster_id + 1}.png'
        else:
            text_data = ' '.join(self.all_responses['response'])
            title = 'Word Cloud - All Responses'
            filename = 'wordcloud_all.png'
        
        wordcloud = WordCloud(
            width=1200,
            height=600,
            background_color='white',
            colormap='viridis',
            max_words=100
        ).generate(text_data)
        
        plt.figure(figsize=(15, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(title, fontsize=20, pad=20)
        plt.tight_layout()
        
        output_path = os.path.join(self.output_dir, filename)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Word cloud saved: {output_path}")
        plt.close()
    
    def visualize_sentiment_distribution(self):
        """Visualize sentiment distribution across responses"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Overall sentiment distribution
        sentiment_counts = self.all_responses['sentiment'].value_counts()
        axes[0, 0].bar(sentiment_counts.index, sentiment_counts.values, 
                       color=['green', 'gray', 'red'])
        axes[0, 0].set_title('Overall Sentiment Distribution', fontsize=14, fontweight='bold')
        axes[0, 0].set_ylabel('Number of Responses')
        
        # Sentiment by question
        sentiment_by_q = self.all_responses.groupby(['question_id', 'sentiment']).size().unstack(fill_value=0)
        sentiment_by_q.plot(kind='bar', stacked=True, ax=axes[0, 1], 
                           color=['green', 'gray', 'red'])
        axes[0, 1].set_title('Sentiment Distribution by Question', fontsize=14, fontweight='bold')
        axes[0, 1].set_xlabel('Question ID')
        axes[0, 1].set_ylabel('Number of Responses')
        axes[0, 1].legend(title='Sentiment')
        
        # Compound score distribution
        axes[1, 0].hist(self.all_responses['compound'], bins=30, color='steelblue', alpha=0.7)
        axes[1, 0].axvline(x=0, color='red', linestyle='--', linewidth=2)
        axes[1, 0].set_title('Compound Sentiment Score Distribution', fontsize=14, fontweight='bold')
        axes[1, 0].set_xlabel('Compound Score')
        axes[1, 0].set_ylabel('Frequency')
        
        # Average sentiment by question
        avg_sentiment = self.all_responses.groupby('question_id')['compound'].mean().sort_values()
        colors = ['red' if x < 0 else 'green' for x in avg_sentiment.values]
        axes[1, 1].barh(range(len(avg_sentiment)), avg_sentiment.values, color=colors)
        axes[1, 1].set_yticks(range(len(avg_sentiment)))
        axes[1, 1].set_yticklabels([f'Q{i}' for i in avg_sentiment.index])
        axes[1, 1].set_title('Average Sentiment Score by Question', fontsize=14, fontweight='bold')
        axes[1, 1].set_xlabel('Average Compound Score')
        axes[1, 1].axvline(x=0, color='black', linestyle='--', linewidth=1)
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'sentiment_analysis.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Sentiment visualization saved: {output_path}")
        plt.close()
    
    def visualize_themes(self):
        """Visualize theme distribution"""
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Theme distribution
        theme_counts = self.all_responses['theme_cluster'].value_counts().sort_index()
        axes[0].bar([f'Theme {i+1}' for i in theme_counts.index], theme_counts.values, 
                   color='steelblue', alpha=0.7)
        axes[0].set_title('Theme Distribution (KMeans Clustering)', fontsize=14, fontweight='bold')
        axes[0].set_ylabel('Number of Responses')
        axes[0].tick_params(axis='x', rotation=45)
        
        # Sentiment by theme
        sentiment_by_theme = self.all_responses.groupby(['theme_cluster', 'sentiment']).size().unstack(fill_value=0)
        sentiment_by_theme.index = [f'Theme {i+1}' for i in sentiment_by_theme.index]
        sentiment_by_theme.plot(kind='bar', stacked=True, ax=axes[1], 
                               color=['green', 'gray', 'red'])
        axes[1].set_title('Sentiment Distribution by Theme', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Theme')
        axes[1].set_ylabel('Number of Responses')
        axes[1].legend(title='Sentiment')
        axes[1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, 'theme_analysis.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Theme visualization saved: {output_path}")
        plt.close()
    
    def generate_insights_report(self):
        """Generate comprehensive insights report"""
        print("\n" + "="*80)
        print("MYVOICE 2025 - NLP ANALYSIS INSIGHTS REPORT")
        print("="*80)
        
        report = []
        
        # Overall statistics
        report.append("\n1. OVERALL STATISTICS")
        report.append("-" * 40)
        report.append(f"Total Responses Analyzed: {len(self.all_responses)}")
        report.append(f"Number of Questions: {self.all_responses['question_id'].nunique()}")
        report.append(f"Average Responses per Question: {len(self.all_responses) / self.all_responses['question_id'].nunique():.1f}")
        
        # Sentiment summary
        report.append("\n2. SENTIMENT ANALYSIS SUMMARY")
        report.append("-" * 40)
        sentiment_dist = self.all_responses['sentiment'].value_counts()
        for sentiment, count in sentiment_dist.items():
            pct = (count / len(self.all_responses)) * 100
            report.append(f"{sentiment}: {count} ({pct:.1f}%)")
        
        avg_compound = self.all_responses['compound'].mean()
        report.append(f"\nAverage Compound Sentiment Score: {avg_compound:.3f}")
        
        # Most positive and negative questions
        report.append("\n3. QUESTION-LEVEL INSIGHTS")
        report.append("-" * 40)
        avg_by_question = self.all_responses.groupby('question_id')['compound'].mean().sort_values()
        
        report.append("\nMost Negative Question:")
        most_neg_q = avg_by_question.index[0]
        report.append(f"  Question {most_neg_q}: {self.df.iloc[most_neg_q-1]['Question']}")
        report.append(f"  Average Score: {avg_by_question.iloc[0]:.3f}")
        
        report.append("\nMost Positive Question:")
        most_pos_q = avg_by_question.index[-1]
        report.append(f"  Question {most_pos_q}: {self.df.iloc[most_pos_q-1]['Question']}")
        report.append(f"  Average Score: {avg_by_question.iloc[-1]:.3f}")
        
        # Theme analysis
        report.append("\n4. THEME IDENTIFICATION (KMeans Clustering)")
        report.append("-" * 40)
        for theme_id in sorted(self.all_responses['theme_cluster'].unique()):
            theme_responses = self.all_responses[self.all_responses['theme_cluster'] == theme_id]
            count = len(theme_responses)
            pct = (count / len(self.all_responses)) * 100
            avg_sentiment = theme_responses['compound'].mean()
            
            report.append(f"\nTheme {theme_id + 1}:")
            report.append(f"  Responses: {count} ({pct:.1f}%)")
            report.append(f"  Average Sentiment: {avg_sentiment:.3f}")
            report.append(f"  Dominant Sentiment: {theme_responses['sentiment'].mode()[0]}")
        
        # Key terms analysis
        report.append("\n5. MOST FREQUENT TERMS (Across All Responses)")
        report.append("-" * 40)
        all_terms = ' '.join(self.processed_responses).split()
        term_freq = Counter(all_terms).most_common(20)
        for term, freq in term_freq:
            report.append(f"  {term}: {freq}")
        
        # Critical issues
        report.append("\n6. CRITICAL ISSUES IDENTIFIED")
        report.append("-" * 40)
        negative_responses = self.all_responses[self.all_responses['sentiment'] == 'Negative']
        
        # Get most common terms in negative responses
        negative_processed = [self.preprocess_text(text) for text in negative_responses['response']]
        negative_terms = ' '.join(negative_processed).split()
        negative_freq = Counter(negative_terms).most_common(10)
        
        report.append("\nTop concerns (from negative responses):")
        for term, freq in negative_freq:
            report.append(f"  {term}: mentioned {freq} times")
        
        # Sample negative responses
        report.append("\nSample negative responses:")
        for idx, row in negative_responses.head(3).iterrows():
            report.append(f"  - Q{row['question_id']}: {row['response'][:100]}...")
        
        # Recommendations
        report.append("\n7. RECOMMENDATIONS")
        report.append("-" * 40)
        report.append("Based on the analysis:")
        
        # Identify themes with most negative sentiment
        theme_sentiment = self.all_responses.groupby('theme_cluster')['compound'].mean().sort_values()
        worst_theme = theme_sentiment.index[0]
        
        report.append(f"  • Priority Focus: Theme {worst_theme + 1} (most negative sentiment)")
        report.append(f"  • Questions needing attention: Question {most_neg_q}")
        
        if avg_compound < -0.05:
            report.append("  • URGENT: Overall sentiment is negative - immediate action required")
        elif avg_compound < 0.2:
            report.append("  • CAUTION: Overall sentiment is neutral - monitoring and improvement needed")
        else:
            report.append("  • POSITIVE: Overall sentiment is good - maintain current practices")
        
        report.append("\n" + "="*80)
        
        # Print and save report
        report_text = '\n'.join(report)
        print(report_text)
        
        output_path = os.path.join(self.output_dir, 'insights_report.txt')
        with open(output_path, 'w') as f:
            f.write(report_text)
        print(f"\nReport saved: {output_path}")
        
        return report_text
    
    def export_results(self):
        """Export analyzed data to CSV"""
        output_path = os.path.join(self.output_dir, 'analyzed_responses.csv')
        self.all_responses.to_csv(output_path, index=False)
        print(f"Analyzed data exported: {output_path}")
        
        # Export summary by question
        summary_by_q = self.all_responses.groupby('question_id').agg({
            'compound': ['mean', 'std'],
            'sentiment': lambda x: x.value_counts().to_dict(),
            'theme_cluster': lambda x: x.mode()[0] if len(x) > 0 else None
        }).round(3)
        
        summary_output = os.path.join(self.output_dir, 'question_summary.csv')
        summary_by_q.to_csv(summary_output)
        print(f"Question summary exported: {summary_output}")
    
    def run_full_analysis(self, n_clusters=5, n_topics=5):
        """
        Run complete NLP analysis pipeline
        
        Args:
            n_clusters (int): Number of clusters for KMeans
            n_topics (int): Number of topics for LDA
        """
        print("\n" + "="*80)
        print("STARTING MYVOICE 2025 NLP ANALYSIS PIPELINE")
        print("="*80 + "\n")
        
        # Step 1: Load data
        self.load_data()
        
        # Step 2: Initialize NLP
        self.initialize_nlp()
        
        # Step 3: Sentiment analysis
        self.perform_sentiment_analysis()
        
        # Step 4: Feature extraction
        self.extract_features()
        
        # Step 5: Theme identification
        self.identify_themes_kmeans(n_clusters=n_clusters)
        
        # Step 6: Topic modeling
        self.perform_lda_topic_modeling(n_topics=n_topics)
        
        # Step 7: Visualizations
        print("\nGenerating visualizations...")
        self.visualize_sentiment_distribution()
        self.visualize_themes()
        
        # Generate word clouds
        print("\nGenerating word clouds...")
        self.generate_wordcloud()  # All responses
        for i in range(n_clusters):
            self.generate_wordcloud(cluster_id=i)  # Each theme
        
        # Step 8: Generate insights report
        self.generate_insights_report()
        
        # Step 9: Export results
        self.export_results()
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE!")
        print(f"All outputs saved to: {self.output_dir}/")
        print("="*80)


def main():
    """Main execution function"""
    # File path to your CSV
    csv_file = "myvoice_responses.csv"  # Change this to your file path
    
    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"ERROR: File '{csv_file}' not found!")
        print("Please ensure the CSV file is in the same directory as this script.")
        print("\nExpected CSV format:")
        print("Column 1: Question text")
        print("Column 2: Responses (multiple responses separated by newlines or semicolons)")
        return
    
    # Initialize analyzer
    analyzer = MyVoiceNLPAnalyzer(csv_file)
    
    # Run full analysis
    analyzer.run_full_analysis(
        n_clusters=5,  # Number of themes to identify
        n_topics=5     # Number of LDA topics
    )
    
    print("\n✓ Analysis pipeline completed successfully!")
    print(f"✓ Check '{analyzer.output_dir}' folder for all results")


if __name__ == "__main__":
    main()
