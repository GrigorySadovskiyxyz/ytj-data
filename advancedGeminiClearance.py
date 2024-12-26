import json
import re
import hashlib
from langdetect import detect
from tqdm import tqdm
import nltk
from nltk.stem import SnowballStemmer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Download required NLTK resources if not already present
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('punkt')
except LookupError:
    nltk.download('punkt')

def preprocess_text(text):
    """
    Performs text preprocessing:
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
        lang = detect(text)
    except Exception as e:
        lang = 'fi'  # Default to Finnish for very short texts
    return lang

def load_keywords(keyword_group):
    """Loads and processes keywords from a string representing a keyword group."""
    keywords = {}
    lines = keyword_group.strip().split('\n')
    for line in lines:
        parts = line.split()
        group = parts[0]
        keyword = ' '.join(parts[1:]).replace('_', ' ')
        keywords[keyword] = group
    return keywords

def filter_sentences(text, keywords, language='fi'):
    """
    Filters sentences from a text based on language and keyword presence.

    Args:
        text: The input text.
        keywords: A dictionary of keywords with their associated groups.
        language: The target language ('fi' for Finnish).

    Returns:
        A list of sentences that meet the criteria.
    """
    sentences = nltk.sent_tokenize(text)  # Tokenize into sentences
    filtered_sentences = []

    for sentence in sentences:
        if detect_language(sentence) == language:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in keywords):
                filtered_sentences.append(sentence)

    return filtered_sentences

def stem_finnish_text(text):
    """Stems Finnish text using SnowballStemmer."""
    stemmer = SnowballStemmer("finnish")
    words = nltk.word_tokenize(text)
    stemmed_words = [stemmer.stem(word) for word in words]
    return " ".join(stemmed_words)

def clean_and_filter_website_data(input_filepath, output_filepath, sustainability_keywords, technology_keywords):
    """
    Cleans, filters, and deduplicates website text data from a JSON file.

    Args:
        input_filepath: Path to the input JSON file.
        output_filepath: Path to save the cleaned and filtered JSON data.
        sustainability_keywords: Dictionary of sustainability keywords.
        technology_keywords: Dictionary of technology keywords.
    """
    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        logging.error(f"File not found: {input_filepath}")
        return
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from file: {input_filepath}")
        return

    cleaned_data = {}
    total_texts = 0
    duplicates_removed = 0
    language_counts = {}
    all_keywords = {**sustainability_keywords, **technology_keywords}

    for main_url, subpages in tqdm(data.items(), desc="Processing websites"):
        cleaned_data[main_url] = {}
        for subpage_url, text in subpages.items():
            total_texts += 1
            cleaned_text = preprocess_text(text)

            if len(cleaned_text.split()) < 5:
                continue

            lang = detect_language(cleaned_text)
            language_counts[lang] = language_counts.get(lang, 0) + 1

            # Filter sentences based on language and keywords
            filtered_sentences = filter_sentences(cleaned_text, all_keywords, language='fi')

            # Stem the Finnish sentences
            stemmed_sentences = [stem_finnish_text(sentence) for sentence in filtered_sentences]

            # Create a hash of the cleaned text for deduplication
            combined_text = " ".join(stemmed_sentences)
            text_hash = calculate_hash(combined_text)

            # Check for duplicates
            is_duplicate = False
            for existing_main_url, existing_subpages in cleaned_data.items():
                for existing_text_hash in existing_subpages.values():
                    if text_hash == existing_text_hash:
                        is_duplicate = True
                        duplicates_removed += 1
                        break
                if is_duplicate:
                    break
            
            if not is_duplicate and combined_text:
                cleaned_data[main_url][subpage_url] = combined_text

    # Print stats
    logging.info("--- Processing Statistics ---")
    logging.info(f"Total texts processed: {total_texts}")
    logging.info(f"Duplicate texts removed: {duplicates_removed}")
    logging.info(f"Languages detected: {language_counts}")

    # Save the cleaned data
    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"Error saving data to {output_filepath}: {e}")

# --- Main Execution ---
if __name__ == "__main__":
    input_filepath = 'sample.json'  # Replace with your input JSON file
    output_filepath = 'cleaned_filtered_website_data.json'  # Output JSON file

    sustainability_keywords_group = """
Environmental ghg
Environmental co2
Environmental co2_neutral
Environmental pollution
Environmental durability
Environmental restricted
Environmental low_impact
Environmental voc
Environmental pvc
Environmental silica
Environmental reduction
Environmental green
Environmental recycled
Environmental alternative
Environmental regenerative
Environmental environmental
Environmental biobased
Environmental biodegradable
Environmental energy_efficient_production
Environmental non-toxic_materials
Environmental sustainable_manufacturing
Environmental modular_design
Environmental waste_management
Environmental swarf_handling
Environmental coolant_recycling
Environmental machining_fluid_control
Environmental dust_control_systems
Environmental emissions_control_systems
Environmental recycling_of_machine_parts
Environmental water_usage_efficiency
Environmental chemical_waste_disposal

Social fair_wages
Social fair_trade
Social fair
Social coc
Social ranking
Social suppliers
Social operator_training
Social machine_maintenance_schedules
Social safety_standards_compliance
Social ISO_certification
Social worker_safety
Social ergonomics
Social health
Social labor_conditions
Social workplace_wellbeing
Social accident_prevention
Social emergency_shutoff_procedures
Social operator_safety_training
Social robot_operator_skills
Social safety_in_hot_working_environments

Economic longevity
Economic durability
Economic profit
Economic predictability
Economic machine_efficiency
Economic operational_costs
Economic tool_life_management
Economic automation_efficiency
Economic cost_of_ownership
Economic maintenance_costs
Economic quality
Economic production_schedules
Economic cost_efficiency
Economic supply_chain_management
Economic lean_manufacturing
Economic investment_in_special_purpose_machinery
Economic industrial_robot_efficiency
Economic production_of_semiconductor_machinery
Economic balance_equipment_costs
Economic specialized_manufacturing_automation
Economic machinery_for_ceramic_and_tile_production
"""
    technology_keywords_group = """
platform Technologies
rfid Technologies
blockchain Technologies
coc Technologies
passport Technologies
digital Technologies
3D Technologies
ai Technologies
vr Technologies
360_degree Technologies
voice Technologies
big_data Technologies
smart Technologies
cloud Technologies
iot Technologies
sensors Technologies
virtual Technologies
nfc Technologies
machine_learning Technologies
predictive_maintenance Technologies
edge_computing Technologies
augmented_reality Technologies
digital_twins Technologies
automation_software Technologies
robotic_process_automation Technologies
industrial_internet_of_things (IIoT) Technologies
cybersecurity_for_machinery Technologies
additive_manufacturing Technologies
autonomous_machinery Technologies
AI-powered_vision_systems Technologies
5G_connectivity Technologies
multimodal_AI Technologies
multimodal_data_fusion Technologies
digital_product_passport_integration Technologies
traceability_systems Technologies
supply_chain_transparency Technologies
data_provenance Technologies
circular_economy_data Technologies
product_lifecycle_management Technologies
data_interoperability_standards Technologies
ESG_reporting_systems Technologies
material_flow_tracking Technologies
blockchain_for_DPP Technologies
user_access_control Technologies
"""

    sustainability_keywords = load_keywords(sustainability_keywords_group)
    technology_keywords = load_keywords(technology_keywords_group)

    clean_and_filter_website_data(input_filepath, output_filepath, sustainability_keywords, technology_keywords)

    logging.info(f"Cleaned and filtered data saved to: {output_filepath}")