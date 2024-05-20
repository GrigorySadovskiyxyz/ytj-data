from googletrans import Translator
import os

# Define the filename (relative path)
filename = "output.txt"

# Get the current working directory
current_directory = os.getcwd()

# Create the full path to the file using the relative path
file_path = os.path.join(current_directory, filename)

def read_file(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"The file {file_name} does not exist.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file {file_name}: {e}")
        return None

def clean_text(text):
    # Remove or replace unsupported characters
    cleaned_text = ''.join(char if char.isprintable() else ' ' for char in text)
    return cleaned_text

def translate_text(text, src_lang='fi', dest_lang='en'):
    translator = Translator()
    try:
        translated = translator.translate(text, src=src_lang, dest=dest_lang)
        return translated.text
    except Exception as e:
        print(f"An error occurred during translation: {e}")
        return None

def write_file(file_name, content):
    try:
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        print(f"An error occurred while writing to the file {file_name}: {e}")

# File paths
output_file_path = 'translated_output.txt'

# Read the input file
finnish_text = read_file(file_path)

if finnish_text:
    # Clean the text
    cleaned_text = clean_text(finnish_text)
    
    # Translate the text
    translated_text = translate_text(cleaned_text, src_lang='fi', dest_lang='en')
    
    if translated_text:
        # Write the translated text to the output file
        write_file(output_file_path, translated_text)
        print(f"Translation complete. Translated content written to {output_file_path}")
    else:
        print("Translation failed.")
