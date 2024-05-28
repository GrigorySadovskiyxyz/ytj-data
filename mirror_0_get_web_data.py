import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import chardet
import pandas as pd
import json
import time
import urllib3

# Suppress only the single InsecureRequestWarning from urllib3 needed for requests.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_subpage_links(main_url):
    """
    Given a main URL, this function returns a list of unique subpage links
    that belong to the same domain.
    
    Parameters:
    main_url (str): The main URL to scrape.
    
    Returns:
    list: A list of unique subpage links belonging to the same domain.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    # Send a GET request to the main URL
    response = requests.get(main_url, headers=headers, verify=False)
    
    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(f"Failed to fetch the page. Status code: {response.status_code}")
    
    # Parse the content of the page
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Get the domain of the main URL
    main_domain = urlparse(main_url).netloc
    
    # Find all anchor tags
    a_tags = soup.find_all('a', href=True)
    
    # Extract and collect the links
    links = set()
    for tag in a_tags:
        href = tag['href']
        # Construct full URL from relative paths if necessary
        full_url = urljoin(main_url, href)
        # Filter out links that are not in the same domain
        if urlparse(full_url).netloc == main_domain:
            links.add(full_url)
    
    return list(links)

##############################################################################
##  MAIN PROGRAM STARTS HERE
##############################################################################

# 1) Open Tab Separated File, detect encoding, load as dataframe
file_name = "Data set jclepro.txt"
# Extra code to detect encoding
with open(file_name, 'rb') as f:
    result = chardet.detect(f.read())
df = pd.read_csv(file_name, sep='\t', encoding=result['encoding'])

# 2) Create dictionary of website URLs, set status as 'Not-checked'
url_list = df['URL']
dict_links = dict(zip(url_list, ["Not-checked"] * len(url_list)))

# Set base variables
min_time_interval = 12 # Minimally wait 10 seconds to query site

# 3) For each website start with base level URL, get sub_urls and content
all_results = {}

# Process each URL once
for one in dict_links.keys():
    if dict_links[one] == "Not-checked":
        try:
            result = get_subpage_links(one)
            dict_links[one] = "Checked"
            all_results[one] = result
        except Exception as e:
            print(f"Error processing {one}: {e}")
        # Sleep to avoid burdening websites too much
        time.sleep(min_time_interval)

# Write results to JSON file
with open("data.json", "w") as json_fileout:
    json.dump(all_results, json_fileout, indent=4)

print("Finished processing all base URLs.")
