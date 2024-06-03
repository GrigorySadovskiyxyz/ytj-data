import json
import asyncio
from pyppeteer import launch
from tqdm import tqdm
from bs4 import BeautifulSoup

async def fetch_with_pyppeteer(url, browser_path):
    try:
        browser = await launch(headless=True, executablePath=browser_path)
        page = await browser.newPage()
        await page.goto(url, {'waitUntil': 'networkidle0'})
        content = await page.content()
        await browser.close()
        return content
    except Exception as e:
        return f"Error fetching {url}: {str(e)}"

def extract_text_from_urls(json_file_path, browser_path):
    def extract_text(url):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        html = loop.run_until_complete(fetch_with_pyppeteer(url, browser_path))
        if "Error fetching" in html:
            return html
        soup = BeautifulSoup(html, 'lxml')
        texts = soup.get_text(separator=' ', strip=True)
        return texts

    with open(json_file_path, 'r') as file:
        json_urls = json.load(file)
    
    result = {}
    for base_url, urls in json_urls.items():
        if isinstance(urls, list):
            result[base_url] = {}
            for url in tqdm(urls, desc=f"Fetching URLs from {base_url}", unit="url"):
                result[base_url][url] = extract_text(url)
        else:
            result[base_url] = extract_text(urls)
    
    return result

def save_results_to_json(result, output_file_path):
    with open(output_file_path, 'w') as file:
        json.dump(result, file, indent=2)

# Example usage:
json_file_path = 'data.json'
output_file_path = 'data_text.json'
browser_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'  # Change to the path of your Chrome executable
result = extract_text_from_urls(json_file_path, browser_path)
save_results_to_json(result, output_file_path)

print(f"Results saved to {output_file_path}")
