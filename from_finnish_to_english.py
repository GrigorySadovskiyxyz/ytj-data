import pandas as pd
import json
import deepl
from tqdm import tqdm

# Function to translate text from Finnish to English using DeepL
def translate_fi_to_en(text, translator):
    try:
        translated_text = translator.translate_text(text, source_lang="FI", target_lang="EN-GB")
        return translated_text.text
    except deepl.DeepLException as e:
        print(f"Translation error: {e}")
        return text  # Return the original text in case of an error

# Load JSON data from file
with open('data_text.json', 'r') as f:
    data = json.load(f)

# Your DeepL API key
api_key = "XXX"
translator = deepl.Translator(api_key)

# Create lists to hold the data
base_urls = []
texts = []

# Iterate through the JSON data, translate Finnish text to English, and extract base URLs and translated texts
for base_url, url_data in tqdm(data.items(), desc="Translating"):
    for url, text in url_data.items():
        if any(keyword in url for keyword in ['fi', 'suomi']):  # Check if the URL indicates Finnish language
            text = translate_fi_to_en(text, translator)
        base_urls.append(base_url)
        texts.append(text)

# Create a DataFrame from the lists
df = pd.DataFrame({'base_url': base_urls, 'text': texts})

# Group by base_url and aggregate the text
df_grouped = df.groupby('base_url')['text'].apply(lambda x: ' ;;; '.join(x)).reset_index()

# Save the DataFrame to a TSV file
df_grouped.to_csv('results_per_base_url.tsv', sep='\t', index=False)

# Display the DataFrame to the user
import ace_tools as tools; tools.display_dataframe_to_user(name="Grouped DataFrame", dataframe=df_grouped)
