import csv
import json
import requests
from yirabot import Yirabot

def read_csv(file_path):
    with open(file_path, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        return [row['www_element'] for row in reader]

def check_sitemap(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        is_xml_valid = Yirabot.validate(response.content)
        return 'yes' if is_xml_valid else 'no'
    except requests.RequestException:
        return 'no'

def main(csv_file_path):
    www_elements = read_csv(csv_file_path)
    results = []

    for www_element in www_elements:
        sitemap_url = f"{www_element}/sitemap.xml"
        xml_site_present = check_sitemap(sitemap_url)
        results.append({
            'www_element': www_element,
            'xml_site_present': xml_site_present
        })

    return json.dumps(results, indent=4)

if __name__ == "__main__":
    csv_file_path = 'refined_data_28890.csv'  # CSV file path
    result_json = main(csv_file_path)
    print(result_json)
