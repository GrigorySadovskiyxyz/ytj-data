from yirabot import Yirabot
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

bot = Yirabot()
url = "https://www.volter.fi/"
sitemap_url = "https://www.demach.fi/sitemap-1.xml"
crawl_data = bot.scrape(url, force=True) #Only use force in ethical situations


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


def fetch_subpages(main_url):
    try:
        # Send a request to the main URL
        response = requests.get(main_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve the main page: {e}")
        return []

    # Parse the main page content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all <a> tags
    a_tags = soup.find_all('a')

    # Extract href attributes and join with main URL to form full URLs
    subpages = set()
    for tag in a_tags:
        href = tag.get('href')
        print(tag)
        if href and href.startswith('/'):
            full_url = urljoin(main_url, href)
            subpages.add(full_url)

    return list(subpages)

subpages = fetch_subpages(url)

print(subpages)



# validation_results = bot.validate(sitemap_url)

# Checking and printing inaccessible URLs
# inaccessible_urls = {url: status for url, status in validation_results.items() if status != 200}
# print("Inaccessible URLs:", inaccessible_urls)

# Displaying some extracted data
# print(crawl_data)