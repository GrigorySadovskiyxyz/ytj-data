import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re
import warnings
from tqdm import tqdm  # For the progress bar
import scipy.cluster.hierarchy as sch  # For hierarchical clustering linkage
import os  # To check if files exist
import numpy as np

# Suppress specific warnings about clustering with SciPy
warnings.filterwarnings("ignore", message=".*Clustering large matrix with scipy.*")

# --- Step 1: Load and Process Keywords with Groups ---
def load_keywords_with_groups(file_path):
    keywords_with_groups = {}
    
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:  # Skip empty lines
                continue
            if ' ' not in line:  # Skip lines without a space separating the group and keyword
                continue
            group, keyword = line.split(' ', 1)  # Split into group and keyword
            keywords_with_groups[keyword.lower().replace('_', ' ')] = group.lower()
    
    return keywords_with_groups

# Preprocess the text to remove special characters and convert to lowercase
def preprocess_text(text):
    return re.sub(r'[^\w\s]', '', text.lower())

# Check if keyword or its parts exist in the text
def keyword_in_text(text, keyword):
    keyword_parts = keyword.split()  # Split the keyword into parts
    combined_found = re.search(r'\b{}\b'.format(re.escape(' '.join(keyword_parts))), text)  # Check for full keyword

    # Check for individual parts of the keyword
    parts_found = all(re.search(r'\b{}\b'.format(re.escape(part)), text) for part in keyword_parts)
    
    return combined_found or parts_found

# --- Step 2: Analyze a single subpage and print short analysis ---
def analyze_subpage(url, text, keywords_with_groups):
    text = preprocess_text(text)
    
    found_keywords = [keyword for keyword in keywords_with_groups.keys() if keyword_in_text(text, keyword)]
    
    if found_keywords:
        print(f"\nSubpage URL: {url}")
        print(f"Total Keywords Found: {len(found_keywords)}")
        print(f"Keywords: {', '.join(found_keywords[:5])} ... (and {len(found_keywords) - 5} more)" if len(found_keywords) > 5 else f"Keywords: {', '.join(found_keywords)}")
    else:
        print(f"\nSubpage URL: {url}")
        print("No keywords found.")

# --- Step 3: Create a Co-occurrence Matrix ---
def create_cooccurrence_matrix(df, keywords_with_groups):
    keywords = list(keywords_with_groups.keys())
    # Initialize an empty matrix for keyword co-occurrences
    cooccurrence_matrix = pd.DataFrame(0, index=keywords, columns=keywords)

    # Use tqdm to track progress
    for text in tqdm(df['Cleaned_Text'], desc="Processing texts"):
        text = preprocess_text(text)
        
        # Find keywords present in the text
        present_keywords = [keyword for keyword in keywords if keyword_in_text(text, keyword)]
        
        # Update the co-occurrence matrix
        for i, keyword1 in enumerate(present_keywords):
            for keyword2 in present_keywords[i:]:
                cooccurrence_matrix.at[keyword1, keyword2] += 1
                if keyword1 != keyword2:
                    cooccurrence_matrix.at[keyword2, keyword1] += 1  # Since co-occurrence is symmetric
    
    return cooccurrence_matrix

# --- Step 4: Calculate Pearson Correlation ---
def calculate_correlation(matrix):
    # Replace any NaN values with 0 (e.g., where no co-occurrence happened)
    matrix = matrix.fillna(0)
    # Compute the correlation matrix
    correlation_matrix = matrix.corr()
    return correlation_matrix

# --- Step 5: Plot Correlation Heatmap and Save Linkage Data ---
def plot_correlation_heatmap(correlation_matrix, keywords_with_groups, title, filename):
    # Custom colormap to reflect desired correlation levels
    cmap = sns.color_palette("coolwarm", as_cmap=True)

    plt.figure(figsize=(16, 14))  # Adjust figure size
    
    # Draw the heatmap
    heatmap = sns.heatmap(
        correlation_matrix,
        cmap=cmap,
        annot=False,  # No need for annotation in cells
        vmin=0, vmax=1,  # Scale from 0 (no correlation) to 1 (high correlation)
        cbar_kws={'label': 'Correlation Coefficient'},  # Add label for the color bar
        linewidths=0.5  # Set line width between cells
    )

    # Grouping the keywords by their categories for better analysis
    groups = {group: [] for group in set(keywords_with_groups.values())}
    for keyword, group in keywords_with_groups.items():
        groups[group].append(keyword)

    # Add title
    plt.title(title, fontsize=16)

    # Save the figure
    plt.savefig(filename, format='png')
    plt.close()

# --- Step 6: Plot Frequency of Keyword Groups ---
def plot_keyword_frequencies(df, keywords_with_groups):
    keywords = list(keywords_with_groups.keys())
    group_counts = {group: 0 for group in set(keywords_with_groups.values())}
    
    for text in tqdm(df['Cleaned_Text'], desc="Calculating keyword frequencies"):
        text = preprocess_text(text)
        found_keywords = [keyword for keyword in keywords if keyword_in_text(text, keyword)]
        
        for keyword in found_keywords:
            group = keywords_with_groups[keyword]
            group_counts[group] += 1

    # Plot bar graph of keyword frequencies
    plt.figure(figsize=(10, 6))
    plt.bar(group_counts.keys(), group_counts.values(), color=['#F8766D', '#00B0F6', '#A3A500', '#E76BF3'])
    plt.xlabel('Keyword Group')
    plt.ylabel('Frequency')
    plt.title('Frequency of Keywords by Group')
    plt.savefig("keyword_frequencies.png", format='png')
    plt.close()

# --- Step 7: Load Keywords and Data ---
sustainability_keywords_with_groups = load_keywords_with_groups('28890_keywords_sustainability.txt')
technology_keywords_with_groups = load_keywords_with_groups('28890_keywords_technology.txt')

# Combine all keywords
all_keywords_with_groups = {**sustainability_keywords_with_groups, **technology_keywords_with_groups}

# Load the cleaned data from CSV
df = pd.read_csv('cleaned_translated_data_grouped.csv')

# Check if the co-occurrence matrix already exists to avoid reprocessing the text
if os.path.exists("cooccurrence_matrix.csv"):
    # Load the existing co-occurrence matrix
    cooccurrence_matrix = pd.read_csv("cooccurrence_matrix.csv", index_col=0)
else:
    # --- Step 8: Analyze each subpage and print short analysis with progress bar ---
    for index, row in tqdm(df.iterrows(), desc="Analyzing subpages", total=len(df)):
        url = row['Subpage']
        text = row['Cleaned_Text']
        analyze_subpage(url, text, all_keywords_with_groups)

    # --- Step 9: Create Co-occurrence Matrix for Keywords ---
    cooccurrence_matrix = create_cooccurrence_matrix(df, all_keywords_with_groups)

    # Save the co-occurrence matrix for future use
    cooccurrence_matrix.to_csv("cooccurrence_matrix.csv")

# --- Step 10: Calculate Correlation Matrix ---
correlation_matrix = calculate_correlation(cooccurrence_matrix)

# --- Step 11: Plot the Correlation Heatmap ---
plot_correlation_heatmap(correlation_matrix, all_keywords_with_groups, "Keyword Correlation Heatmap", "keyword_correlation_heatmap.png")

# --- Step 12: Plot the Frequency of Keyword Groups ---
plot_keyword_frequencies(df, all_keywords_with_groups)