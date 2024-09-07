import json
import re
from tqdm import tqdm

# Function to clean and normalize text
def normalize_text(text):
    # Remove unnecessary symbols
    text = re.sub(r'[©™®]', '', text)
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

# Function to calculate Jaccard similarity between two sets of words
def jaccard_similarity(text1, text2):
    set1 = set(text1.split())
    set2 = set(text2.split())
    
    # Calculate intersection and union of the two sets
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    
    # Check if the union is empty to avoid division by zero
    if len(union) == 0:
        return 0  # No similarity if both sets are empty
    
    # Return the Jaccard similarity
    return len(intersection) / len(union)

# Function to remove subpages with 95% or more content similarity within the same domain
def remove_similar_subpages(domain_content):
    subpages = list(domain_content.keys())
    marked_for_removal = set()
    
    for i in range(len(subpages)):
        for j in range(i + 1, len(subpages)):
            page1 = subpages[i]
            page2 = subpages[j]
            
            # Check similarity between the two subpages
            similarity = jaccard_similarity(domain_content[page1], domain_content[page2])
            if similarity >= 0.95:
                # Mark the second page for removal (only if it's similar)
                marked_for_removal.add(page2)
    
    # Remove marked subpages
    for page in marked_for_removal:
        del domain_content[page]
    
    return domain_content

# Function to remove empty subpages after comparison
def remove_empty_subpages(data):
    cleaned_data = {}
    for domain, subpages in data.items():
        # Remove subpages that are empty or contain only whitespace
        cleaned_subpages = {page: content for page, content in subpages.items() if content.strip()}
        
        if cleaned_subpages:
            cleaned_data[domain] = cleaned_subpages
    
    return cleaned_data

# Function to normalize and clean up the JSON structure
def normalize_json(data):
    normalized_data = {}
    
    # Initialize a progress bar
    with tqdm(total=len(data), desc="Processing JSON Data") as pbar:
        for domain, subpages in data.items():
            normalized_domain_content = {}
            
            # Normalize each subpage's content
            for subpage, content in subpages.items():
                cleaned_content = normalize_text(content)
                normalized_domain_content[subpage] = cleaned_content
            
            # Remove similar subpages (>= 95% similarity)
            normalized_domain_content = remove_similar_subpages(normalized_domain_content)
            
            # Add the normalized domain content back to the result
            normalized_data[domain] = normalized_domain_content
            
            # Update progress bar
            pbar.update(1)
    
    # Remove subpages with no content left
    normalized_data = remove_empty_subpages(normalized_data)
    
    return normalized_data

def main():
    input_file = 'data_text.json'
    output_file = 'normalized_data.json'
    
    # Load the original JSON from the file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            original_json = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {input_file} was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: The file {input_file} is not a valid JSON.")
        return
    
    # Normalize the original JSON structure and remove duplicates
    normalized_json = normalize_json(original_json)
    
    # Save the normalized JSON to a new file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(normalized_json, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Normalized data has been saved to {output_file}")
    except Exception as e:
        print(f"Error while saving the file: {e}")

if __name__ == "__main__":
    main()
