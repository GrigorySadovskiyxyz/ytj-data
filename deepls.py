import json
import re
from tqdm import tqdm

# Function to clean and normalize text, and remove unnecessary Finnish repetitive phrases
def normalize_text(text):
    # Remove unnecessary symbols
    text = re.sub(r'[©™®]', '', text)
    
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    
    # Remove email addresses
    text = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '', text)
    
    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '', text)
    
    # Common repetitive Finnish phrases to remove
    repetitive_phrases = [
        "yhteystiedot", "kuvagalleria", "ota yhteyttä", "lisätietoja", "evästeet", 
        "tietosuojakäytäntö", "käyttöehdot", "kaikki oikeudet pidätetään",
        "lue lisää", "etusivu", "sivukartta", "tilaa uutiskirje", 
        "liity postituslistalle", "rekisteriseloste", "palvelut",
        "yhteistyökumppanit", "asiakaspalvelu", "meistä", "usein kysytyt kysymykset"
    ]
    
    # Remove repetitive phrases
    for phrase in repetitive_phrases:
        text = re.sub(rf"\b{phrase}\b", '', text, flags=re.IGNORECASE)
    
    # Remove excessive whitespace and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

# Function to calculate Jaccard similarity between two sets of words
def jaccard_similarity(text1, text2):
    set1 = set(text1.split())
    set2 = set(text2.split())
    
    # Check if both sets are empty
    if not set1 and not set2:
        return 1.0  # Consider two empty texts as identical (100% similar)
    
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    
    # Safeguard against division by zero
    if not union:
        return 0.0  # Return 0 similarity if the union is empty
    
    return len(intersection) / len(union)

# Function to remove subpages with 80% or more content similarity within the same domain
def remove_similar_subpages(domain_content):
    subpages = list(domain_content.keys())
    marked_for_removal = set()
    
    for i in range(len(subpages)):
        for j in range(i + 1, len(subpages)):
            page1 = subpages[i]
            page2 = subpages[j]
            
            # Check similarity between the two subpages
            similarity = jaccard_similarity(domain_content[page1], domain_content[page2])
            if similarity >= 0.80:  # Use 80% similarity threshold
                # Mark the second page for removal (only if it's similar)
                marked_for_removal.add(page2)
    
    # Remove marked subpages
    for page in marked_for_removal:
        del domain_content[page]
    
    return domain_content

# Function to remove subpages with error messages like "Error fetching"
def remove_error_pages(domain_content):
    # A more comprehensive list of error phrases
    error_phrases = [
        "Error fetching", "Page not found", "404", "Unavailable", "service unavailable", "failed to load",
        "could not be retrieved", "temporarily unavailable", "no data", "loading failed", "error loading"
    ]
    
    cleaned_content = {}
    
    for subpage, content in domain_content.items():
        # Normalize the text before checking for error phrases
        normalized_content = normalize_text(content).lower()
        
        # Check for any error phrase in the normalized content
        if not any(error_phrase.lower() in normalized_content for error_phrase in error_phrases):
            cleaned_content[subpage] = content
    
    return cleaned_content

# Function to remove subpages that are empty or only contain insignificant content
def remove_empty_or_insignificant_subpages(domain_content):
    cleaned_content = {}
    
    for subpage, content in domain_content.items():
        # Normalize the content for checking
        normalized_content = normalize_text(content)
        
        # Remove subpages with no content or very short content
        if len(normalized_content) > 20:  # Arbitrary threshold to avoid keeping very short/insignificant pages
            cleaned_content[subpage] = content
    
    return cleaned_content

# Function to remove empty subpages after all processing
def remove_empty_subpages(data):
    cleaned_data = {}
    for domain, subpages in data.items():
        cleaned_subpages = {page: content for page, content in subpages.items() if content.strip()}
        
        if cleaned_subpages:
            cleaned_data[domain] = cleaned_subpages
    
    return cleaned_data

# Function to normalize JSON structure and remove duplicates and errors
def normalize_json(data):
    normalized_data = {}
    
    # Initialize a progress bar
    with tqdm(total=len(data), desc="Processing JSON Data") as pbar:
        for domain, subpages in data.items():
            normalized_domain_content = {}
            
            # Normalize each subpage
            for subpage, content in subpages.items():
                cleaned_content = normalize_text(content)
                normalized_domain_content[subpage] = cleaned_content
            
            # Step 1: Remove subpages with errors like "Error fetching"
            normalized_domain_content = remove_error_pages(normalized_domain_content)
            
            # Step 2: Remove subpages with no content or insignificant content
            normalized_domain_content = remove_empty_or_insignificant_subpages(normalized_domain_content)
            
            # Step 3: Remove similar subpages (>= 80% similarity)
            normalized_domain_content = remove_similar_subpages(normalized_domain_content)
            
            # Add normalized domain content to the result
            normalized_data[domain] = normalized_domain_content
            
            # Update progress bar
            pbar.update(1)
    
    # Step 4: Remove subpages with no content after processing
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
    
    # Normalize the original JSON structure and remove duplicates and error pages
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
