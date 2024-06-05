import json
import asyncio
import signal
import sys
from pyppeteer import launch
from tqdm import tqdm
from bs4 import BeautifulSoup
from langdetect import detect, LangDetectException

result = {}  # Global variable to hold the result

async def fetch_with_pyppeteer(url):
    try:
        browser = await launch(headless=True)
        page = await browser.newPage()
        await page.goto(url, {'waitUntil': 'networkidle0'})
        content = await page.content()
        await browser.close()
        return content
    except Exception as e:
        return f"Error fetching {url}: {str(e)}"

def extract_text_from_urls(json_file_path):
    global result

    def extract_text(url):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        html = loop.run_until_complete(fetch_with_pyppeteer(url))
        if "Error fetching" in html:
            return html
        soup = BeautifulSoup(html, 'lxml')
        texts = soup.get_text(separator=' ', strip=True)
        return texts

    with open(json_file_path, 'r') as file:
        json_urls = json.load(file)

    language_preference = {}

    for base_url, urls in json_urls.items():
        if base_url not in result:
            result[base_url] = {}

        if not urls:  # If there are no subpages, scrape the main URL
            urls = [base_url]

        preferred_language_set = False
        for url in tqdm(urls, desc=f"Fetching URLs from {base_url}", unit="url"):
            if url in result[base_url]:
                continue  # Skip already processed URLs
            text_content = extract_text(url)
            if "Error fetching" in text_content:
                result[base_url][url] = text_content
            else:
                try:
                    lang = detect(text_content)
                    if not preferred_language_set:
                        language_preference[base_url] = lang
                        preferred_language_set = True
                        result[base_url][url] = text_content
                    else:
                        if language_preference[base_url] == lang:
                            result[base_url][url] = text_content
                        else:
                            print(f"Skipping {url} as it is in {lang} language, and we already have content in {language_preference[base_url]}")
                except LangDetectException as e:
                    result[base_url][url] = f"Error detecting language for {url}: {str(e)}"

def save_results_to_json(output_file_path):
    global result
    with open(output_file_path, 'w') as file:
        json.dump(result, file, indent=2)

def signal_handler(sig, frame):
    print('Interrupt received, saving progress...')
    save_results_to_json(output_file_path)
    sys.exit(0)

# Register the signal handler for graceful termination
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Example usage:
json_file_path = 'data.json'
output_file_path = 'data_text.json'

try:
    extract_text_from_urls(json_file_path)
finally:
    save_results_to_json(output_file_path)
    print(f"Results saved to {output_file_path}")
