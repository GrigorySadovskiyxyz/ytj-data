import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

def get_subpage_links(main_url):
    """
    Given a main URL, this function returns a list of unique subpage links
    that belong to the same domain.
    
    Parameters:
    main_url (str): The main URL to scrape.
    
    Returns:
    list: A list of unique subpage links belonging to the same domain.
    """
    # Send a GET request to the main URL
    response = requests.get(main_url)
    
    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(f"Failed to fetch the page. Status code: {response.status_code}")
    
    # Parse the content of the page
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Get the domain of the main URL
    main_domain = urlparse(main_url).netloc
    print(main_domain)
    
    # Find all anchor tags
    a_tags = soup.find_all('a', href=True)
    print(a_tags)
    
    # Extract and collect the links
    links = set()
    for tag in a_tags:
        href = tag['href']
        print(href)
        # Construct full URL from relative paths if necessary
        full_url = urljoin(main_url, href)
        # Filter out links that are not in the same domain
        if urlparse(full_url).netloc == main_domain:
            links.add(full_url)
    
    return list(links)

# Example usage:
main_url = "https://kuyichi.com/"
subpage_links = get_subpage_links(main_url)
print(subpage_links)