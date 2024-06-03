import requests
from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector
import lxml
import json

def extract_text_from_urls(json_file_path):
    def extract_text(url):
        try:
            resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            http_encoding = resp.encoding if 'charset' in resp.headers.get('content-type', '').lower() else None
            html_encoding = EncodingDetector.find_declared_encoding(resp.content, is_html=True)
            encoding = html_encoding or http_encoding
            soup = BeautifulSoup(resp.content, 'lxml', from_encoding=encoding)
            return [i.text for i in soup.findAll("div", {"class": "texts"})]
        except Exception as e:
            return f"Error fetching {url}: {str(e)}"
    
    with open(json_file_path, 'r') as file:
        json_urls = json.load(file)
    
    result = {}
    for base_url, urls in json_urls.items():
        if isinstance(urls, list):
            result[base_url] = {url: extract_text(url) for url in urls}
        else:
            result[base_url] = extract_text(urls)
    
    return result

def save_results_to_json(result, output_file_path):
    with open(output_file_path, 'w') as file:
        json.dump(result, file, indent=2)

# Example usage:
json_file_path = 'data.json'
output_file_path = 'data_text.json'
result = extract_text_from_urls(json_file_path)
save_results_to_json(result, output_file_path)

print(f"Results saved to {output_file_path}")
