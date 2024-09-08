import json
import re
import time
import os
import requests
from tqdm import tqdm
from datetime import datetime

# Constants for LibreTranslate API limits
API_CALL_LIMIT_PER_MINUTE = 50  # For non-stop requests
CHARACTER_LIMIT_PER_CALL = 2000  # Max characters per API call
LIBRETRANSLATE_API_URL = "https://libretranslate.com/translate"
API_KEY = "7329399d-e2bf-4a2c-929d-ead701fb395e"  # Your provided API key

# File paths
CHECKPOINT_FILE = 'checkpoint_translated_data.json'
OUTPUT_FILE = 'translated_data.json'

# Time tracking
start_time = None

# Function to clean and normalize text, remove repetitive words, and remove unnecessary Finnish repetitive phrases
def normalize_text(text):
    text = re.sub(r'[©™®]', '', text)  # Remove unnecessary symbols
    text = re.sub(r'<.*?>', '', text)  # Remove HTML tags
    text = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '', text)  # Remove email addresses
    text = re.sub(r'http\S+|www\.\S+', '', text)  # Remove URLs
    
    repetitive_phrases = [
        "yhteystiedot", "kuvagalleria", "ota yhteyttä", "lisätietoja", "evästeet", 
        "tietosuojakäytäntö", "käyttöehdot", "kaikki oikeudet pidätetään", "lue lisää",
        "etusivu", "sivukartta", "tilaa uutiskirje", "liity postituslistalle",
        "rekisteriseloste", "palvelut", "yhteistyökumppanit", "asiakaspalvelu", "meistä",
        "usein kysytyt kysymykset"
    ]
    
    for phrase in repetitive_phrases:
        text = re.sub(rf"\b{phrase}\b", '', text, flags=re.IGNORECASE)
    
    text = re.sub(r'\s+', ' ', text).strip()  # Remove excessive whitespace and newlines
    text = remove_repetitive_words(text)
    
    return text

# Function to remove repetitive words within the text without losing sentence meaning
def remove_repetitive_words(text):
    words = text.split()
    new_words = []
    prev_word = None
    
    for word in words:
        if word.lower() != prev_word:
            new_words.append(word)
        prev_word = word.lower()
    
    return ' '.join(new_words)

# Function to chunk text for API calls (max 2,000 characters per call)
def chunk_text(text, chunk_size=CHARACTER_LIMIT_PER_CALL):
    chunks = []
    while len(text) > chunk_size:
        split_at = text.rfind(' ', 0, chunk_size)
        if split_at == -1:
            split_at = chunk_size
        chunks.append(text[:split_at].strip())
        text = text[split_at:].strip()
    if text:
        chunks.append(text)  # Append the remaining part
    return chunks

# Function to translate a chunk using LibreTranslate API with backoff for rate limit hit
def translate_text(text_chunk, subpage_url, current_chunk_index):
    backoff_time = 30  # Start with 30 seconds
    while True:
        try:
            response = requests.post(
                LIBRETRANSLATE_API_URL,
                headers={"Content-Type": "application/json"},
                json={
                    "q": text_chunk,
                    "source": "fi",
                    "target": "en",
                    "format": "text",
                    "alternatives": 3,
                    "api_key": API_KEY
                }
            )
            if response.status_code == 200:
                return response.json().get('translatedText', '')
            elif response.status_code == 429 or "Slowdown" in response.text:
                print(f"Rate limit hit for subpage: {subpage_url}, chunk {current_chunk_index}. Retrying in {backoff_time} seconds...")
                time.sleep(backoff_time)  # Wait for backoff time
                backoff_time = min(backoff_time * 2, 3600)  # Exponential backoff, max 1 hour
            else:
                print(f"Error translating chunk: {response.text}")
                return None
        except Exception as e:
            print(f"Exception occurred during translation: {e}")
            return None

# Function to save progress to a checkpoint file
def save_checkpoint(data):
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Function to load the checkpoint file if it exists
def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Function to estimate completion time in minutes
def estimate_time_remaining(start_time, completed, total):
    elapsed_time = (datetime.now() - start_time).total_seconds()
    if completed == 0:
        return "Estimating..."
    avg_time_per_subpage = elapsed_time / completed
    remaining_subpages = total - completed
    estimated_time_remaining = avg_time_per_subpage * remaining_subpages
    return f"{estimated_time_remaining / 60:.2f} minutes"  # Display in minutes

# Function to normalize and translate JSON structure using LibreTranslate API with checkpointing
def normalize_translate_json(data):
    global start_time
    if start_time is None:
        start_time = datetime.now()

    # Load from checkpoint if it exists
    checkpoint_data = load_checkpoint()
    total_subpages = sum([len(subpages) for subpages in data.values()])
    completed_subpages = sum([len(subpages) for subpages in checkpoint_data.values()])
    
    api_calls = 0
    # Initialize a progress bar
    with tqdm(total=total_subpages, desc="Processing, Chunking, and Translating JSON Data") as pbar:
        pbar.update(completed_subpages)
        for domain, subpages in data.items():
            translated_domain_content = checkpoint_data.get(domain, {})

            # Normalize and translate each subpage
            for subpage, content in subpages.items():
                # If the subpage has empty or incomplete translated content, continue from here
                if subpage in translated_domain_content and translated_domain_content[subpage].strip():
                    continue  # Skip fully translated subpages
                
                cleaned_content = normalize_text(content)
                chunks = chunk_text(cleaned_content)
                translated_chunks = []
                
                for i, chunk in enumerate(chunks):
                    translated_text = translate_text(chunk, subpage, i + 1)
                    if translated_text:
                        translated_chunks.append(translated_text)
                    else:
                        print(f"API limitation encountered. Stopping for subpage: {subpage}. Retrying later.")
                        return checkpoint_data  # Return current progress and stop if API fails

                    api_calls += 1
                    if api_calls % API_CALL_LIMIT_PER_MINUTE == 0:
                        print(f"Rate limit reached. Sleeping for 60 seconds... (Domain: {domain}, Subpage: {subpage}, Chunk: {i + 1})")
                        time.sleep(60)  # Sleep for 60 seconds to avoid rate limit issues
                
                translated_domain_content[subpage] = ' '.join(translated_chunks)  # Join the chunks together
                checkpoint_data[domain] = translated_domain_content

                # Save progress after translating each subpage
                save_checkpoint(checkpoint_data)
                completed_subpages += 1
                pbar.update(1)

                # Display estimated time remaining
                time_estimation = estimate_time_remaining(start_time, completed_subpages, total_subpages)
                print(f"Progress: {completed_subpages}/{total_subpages} subpages completed. Estimated time remaining: {time_estimation}")
    
    return checkpoint_data

# Function to display information about translated text
def display_translated_info(translated_data):
    """Display information about the translated content."""
    if not translated_data:
        print("No translated data found.")
        return
    
    print(f"Number of domains: {len(translated_data)}")
    
    # Iterate through each domain and its subpages
    for domain, subpages in translated_data.items():
        print(f"\nDomain: {domain}")
        print(f"Number of subpages: {len(subpages)}")
        
        for subpage, translated_text in subpages.items():
            print(f"  Subpage: {subpage}")
            print(f"  Translated text length: {len(translated_text)} characters")
            print(f"  Sample translated text: {translated_text[:100]}...")  # Display first 100 chars of translation

def main():
    input_file = 'data_text.json'
    
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
    
    # Normalize, chunk, and translate the JSON structure
    translated_json = normalize_translate_json(original_json)
    
    # Save the translated JSON to a final output file
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(translated_json, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Translated data has been saved to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error while saving the file: {e}")

    # Display translated info
    display_translated_info(translated_json)

if __name__ == "__main__":
    main()
