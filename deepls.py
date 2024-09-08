import json
import re
import time
import os
import requests
from tqdm import tqdm

# Constants for LibreTranslate API limits
API_CALL_LIMIT_PER_MINUTE = 50  # For non-stop requests
CHARACTER_LIMIT_PER_CALL = 2000  # Max characters per API call
LIBRETRANSLATE_API_URL = "https://libretranslate.com/translate"
API_KEY = "7329399d-e2bf-4a2c-929d-ead701fb395e"  # Your provided API key

# File paths
CHECKPOINT_FILE = 'checkpoint_translated_data.json'
OUTPUT_FILE = 'translated_data.json'

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

# Function to translate a chunk using LibreTranslate API with exponential backoff for rate limit hit
def translate_text(text_chunk):
    backoff_time = 60  # Start with 60 seconds
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
                print(f"API rate limit hit: {response.text}. Waiting for {backoff_time} seconds...")
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

# Function to normalize and translate JSON structure using LibreTranslate API with checkpointing
def normalize_translate_json(data):
    # Load from checkpoint if it exists
    checkpoint_data = load_checkpoint()
    api_calls = 0
    # Initialize a progress bar
    with tqdm(total=len(data), desc="Processing, Chunking, and Translating JSON Data") as pbar:
        for domain, subpages in data.items():
            if domain in checkpoint_data:
                # Skip already processed domains
                continue
            translated_domain_content = {}
            
            # Normalize and translate each subpage
            for subpage, content in subpages.items():
                if subpage in checkpoint_data.get(domain, {}):
                    # Skip already processed subpages
                    translated_domain_content[subpage] = checkpoint_data[domain][subpage]
                    continue
                
                cleaned_content = normalize_text(content)
                chunks = chunk_text(cleaned_content)
                translated_chunks = []
                
                for chunk in chunks:
                    translated_text = translate_text(chunk)
                    if translated_text:
                        translated_chunks.append(translated_text)
                    else:
                        print(f"Skipping translation of chunk for subpage: {subpage}")
                    
                    api_calls += 1
                    if api_calls % API_CALL_LIMIT_PER_MINUTE == 0:
                        print("Rate limit reached. Sleeping for 60 seconds...")
                        time.sleep(60)  # Sleep for 60 seconds to avoid rate limit issues
                
                translated_domain_content[subpage] = ' '.join(translated_chunks)  # Join the chunks together
            
            checkpoint_data[domain] = translated_domain_content
            
            # Save progress to checkpoint after each domain
            save_checkpoint(checkpoint_data)
            
            # Update progress bar
            pbar.update(1)
    
    return checkpoint_data

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

if __name__ == "__main__":
    main()
