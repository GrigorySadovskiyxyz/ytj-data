import json
import re
import hashlib
from langdetect import detect
from tqdm import tqdm

def preprocess_text(text):
    """
    Performs basic text preprocessing:
    1. Lowercases the text.
    2. Removes special characters, keeps only alphanumeric and spaces.
    3. Removes extra whitespace.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def calculate_hash(text):
    """Calculates the SHA-256 hash of a string."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def detect_language(text):
    """Detects the language of a text string, handling short texts gracefully."""
    try:
        # Attempt to detect the language
        lang = detect(text)
    except Exception as e:
        # Default to Finnish for very short texts
        lang = 'fi'
    return lang

def clean_and_deduplicate_website_data(input_filepath, output_filepath):
    """
    Cleans and deduplicates website text data from a JSON file.

    Args:
        input_filepath: Path to the input JSON file.
        output_filepath: Path to save the cleaned and deduplicated JSON data.
    """
    with open(input_filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cleaned_data = {}
    total_texts = 0
    duplicates_removed = 0
    language_counts = {}

    for main_url, subpages in tqdm(data.items(), desc="Processing websites"):
        cleaned_data[main_url] = {}
        for subpage_url, text in subpages.items():
            total_texts += 1
            
            # Basic preprocessing and language detection
            cleaned_text = preprocess_text(text)

            # Skip very short texts that might be irrelevant
            if len(cleaned_text.split()) < 5:
                continue

            lang = detect_language(cleaned_text)

            # Count languages
            language_counts[lang] = language_counts.get(lang, 0) + 1

            # Create a hash of the cleaned text for deduplication
            text_hash = calculate_hash(cleaned_text)

            # Check for duplicates (using hash)
            is_duplicate = False
            for existing_main_url, existing_subpages in cleaned_data.items():
                for _, existing_text in existing_subpages.items():
                    if text_hash == calculate_hash(preprocess_text(existing_text)):
                        is_duplicate = True
                        duplicates_removed += 1
                        break
                if is_duplicate:
                    break

            if not is_duplicate:
                cleaned_data[main_url][subpage_url] = cleaned_text

    # Print stats
    print("\n--- Processing Statistics ---")
    print(f"Total texts processed: {total_texts}")
    print(f"Duplicate texts removed: {duplicates_removed}")
    print(f"Languages detected: {language_counts}")

    # Save the cleaned data
    with open(output_filepath, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=4)

# --- Main Execution ---
if __name__ == "__main__":
    input_filepath = 'data_text.json'  # Replace with your input JSON file
    output_filepath = 'cleaned_website_data.json'  # Output JSON file

    clean_and_deduplicate_website_data(input_filepath, output_filepath)

    print(f"\nCleaned data saved to: {output_filepath}")