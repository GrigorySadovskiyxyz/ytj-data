from yirabot import Yirabot
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
from usp.tree import sitemap_tree_for_homepage
import csv
from urllib.parse import urlparse, urljoin


# def get_subpage_links(main_url):
#     """
#     Given a main URL, this function returns a list of unique subpage links
#     that belong to the same domain.
    
#     Parameters:
#     main_url (str): The main URL to scrape.
    
#     Returns:
#     list: A list of unique subpage links belonging to the same domain.
#     """
#     # Send a GET request to the main URL
#     response = requests.get(main_url)
    
#     # Check if the request was successful
#     if response.status_code != 200:
#         raise Exception(f"Failed to fetch the page. Status code: {response.status_code}")
    
#     # Parse the content of the page
#     soup = BeautifulSoup(response.content, 'html.parser')
    
#     # Get the domain of the main URL
#     main_domain = urlparse(main_url).netloc
    
#     # Find all anchor tags
#     a_tags = soup.find_all('a', href=True)
    
#     # Extract and collect the links
#     links = set()
#     for tag in a_tags:
#         href = tag['href']
#         # Construct full URL from relative paths if necessary
#         full_url = urljoin(main_url, href)
#         # Filter out links that are not in the same domain
#         if urlparse(full_url).netloc == main_domain:
#             links.add(full_url)
    
#     return list(links)

# def process_csv(file_path):
#     data = {}
#     with open(file_path, mode='r', newline='', encoding='utf-8') as file:
#         reader = csv.DictReader(file)
#         for row in reader:
#             business_id = row['businessId']
#             main_url = row['www_element']
#             subsections = get_subpage_links(main_url)
#             data[main_url] = subsections
#     return data

# def save_to_json(data, output_file):
#     with open(output_file, 'w', encoding='utf-8') as json_file:
#         json.dump(data, json_file, indent=4)

# # Specify the path to your CSV file
# csv_file_path = 'refined_data_28890.csv'
# # Specify the output JSON file path
# json_output_path = 'data.json'

# # Process the CSV file and get the data
# data = process_csv(csv_file_path)

# # Save the data to a JSON file
# save_to_json(data, json_output_path)

# print(f"Data has been saved to {json_output_path}")


bot = Yirabot()
sitemap_url = "https://www.demach.fi/sitemap-1.xml"
crawl_data = bot.validate(url, force=True) #Only use force in ethical situations






# Displaying some extracted data
# print(crawl_data)


# tree = sitemap_tree_for_homepage("https://www.nipema.fi/")
# print(tree)

# def fetch_subpages(main_url):
#     try:
#         # Send a request to the main URL
#         response = requests.get(main_url)
#         response.raise_for_status()
#     except requests.exceptions.RequestException as e:
#         print(f"Failed to retrieve the main page: {e}")
#         return {}

#     # Parse the main page content
#     soup = BeautifulSoup(response.content, 'html.parser')

#     # Find all <a> tags
#     a_tags = soup.find_all('a')

#     # Extract href attributes and join with main URL to form full URLs
#     subpages = set()
#     for tag in a_tags:
#         href = tag.get('href')
#         if href and href.startswith('/'):
#             full_url = urljoin(main_url, href)
#             subpages.add(full_url)

#     # Create the JSON structure
#     json_structure = {
#         "main_url": main_url,
#         "subpages": {}
#     }

#     for subpage in subpages:
#         json_structure["subpages"][subpage] = {
#             "scraped_data": []
#         }

#     return json_structure


# def fetch_subpages(main_url):
#     try:
#         # Send a request to the main URL
#         response = requests.get(main_url)
#         response.raise_for_status()
#     except requests.exceptions.RequestException as e:
#         print(f"Failed to retrieve the main page: {e}")
#         return []

#     # Parse the main page content
#     soup = BeautifulSoup(response.content, 'html.parser')

#     # Find all <a> tags
#     a_tags = soup.find_all('a')

#     # Extract href attributes and join with main URL to form full URLs
#     subpages = set()
#     for tag in a_tags:
#         href = tag.get('href')
#         print(tag)
#         if href and href.startswith('/'):
#             full_url = urljoin(main_url, href)
#             subpages.add(full_url)

#     return list(subpages)

# subpages = fetch_subpages(url)

# print(subpages)



# validation_results = bot.validate(sitemap_url)

# Checking and printing inaccessible URLs
# inaccessible_urls = {url: status for url, status in validation_results.items() if status != 200}
# print("Inaccessible URLs:", inaccessible_urls)

# Displaying some extracted data
# print(crawl_data)