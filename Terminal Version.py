import subprocess
import sys
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

# Check if requests and beautifulsoup4 modules are installed
reqs = subprocess.check_output([sys.executable, "-m", "pip", "freeze"])
installed_packages = [r.decode().split("==")[0] for r in reqs.split()]
if "requests" not in installed_packages or "beautifulsoup4" not in installed_packages:
    # Install the missing modules
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4"])

# Now you can import the modules and use them in your script
import requests
from bs4 import BeautifulSoup

def is_valid_url(url, base_url):
    """Check if a URL is valid and within the same domain as the base URL."""
    parsed_base_url = urlparse(base_url)
    parsed_url = urlparse(url)
    return parsed_url.netloc == '' or parsed_url.netloc == parsed_base_url.netloc

def is_finnish_url(url):
    """Check if the URL is a Finnish page URL."""
    parsed_url = urlparse(url)
    return '/fi/' in parsed_url.path or parsed_url.path.endswith('/fi') or '.fi' in parsed_url.netloc

def get_visible_text(soup):
    """Extract visible text from a BeautifulSoup object."""
    texts = soup.stripped_strings
    return " ".join(texts)

def scrape_page(url, base_url, visited):
    """Scrape a page and return the visible text and subpage links."""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    text = get_visible_text(soup)

    # Find all subpage links
    links = soup.find_all("a")
    hrefs = [link.get("href") for link in links]
    subpages = [href for href in hrefs if href and is_valid_url(href, base_url) and is_finnish_url(urljoin(base_url, href))]
    full_links = [urljoin(base_url, subpage) for subpage in subpages]
    unique_links = sorted(list(set(full_links)))

    # Filter out already visited links
    new_links = [link for link in unique_links if link not in visited]

    return text, new_links

def scrape_website(start_url):
    """Scrape the entire website starting from the given URL."""
    visited = set()
    to_visit = [start_url]
    all_texts = []

    while to_visit:
        current_url = to_visit.pop(0)
        if current_url in visited:
            continue

        visited.add(current_url)
        print(f"Scraping {current_url}...")

        try:
            text, subpages = scrape_page(current_url, start_url, visited)
            all_texts.append(text)
            to_visit.extend(subpages)
        except Exception as e:
            print(f"Failed to scrape {current_url}: {e}")

    return "\n\n".join(all_texts)

# Prompt the user for the website URL to scrape
start_url = input("Enter the website URL to scrape: ").strip()

# Ensure the URL starts with http:// or https://
if not start_url.startswith("http://") and not start_url.startswith("https://"):
    start_url = "http://" + start_url

# Scrape the website
scraped_text = scrape_website(start_url)

# Prompt the user for the output mode
output_mode = input("Enter the output mode (terminal or file): ").strip().lower()

# Print the scraped text to the terminal or write it to a file
if output_mode == "file":
    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(scraped_text)
    print("Output written to output.txt")
else:
    print(scraped_text)
