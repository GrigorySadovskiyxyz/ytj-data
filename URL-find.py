from selenium.webdriver import Chrome

from selenium.webdriver.chrome.options import Options as ChromeOptions

options = ChromeOptions()
options.headless = True
assert options.headless  # Operating in headless mode
browser = Chrome(options=options)
browser.get('https://tietopalvelu.ytj.fi/')

search_form = browser.find_element_by_id("businessIdOrLEI")
search_form.send_keys('0162133-5')
search_form.submit()

search_box = driver.find_element("name", "q")

search_box.send_keys('ChromeDriver')

search_box.submit()

# import requests
# import csv
# from bs4 import BeautifulSoup
# import time

# def fetch_company_url(business_id):
#     search_url = "https://tietopalvelu.ytj.fi/"
#     params = {"kieli": "en", "path": "/yrityshaku/toimipaikat"}
    
#     with requests.Session() as session:
#         # Perform the search
#         response = session.get(search_url, params=params)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.text, 'html.parser')

#         # Find the form and add the business ID to the search field
#         form = soup.find('form', id='searchform')
#         if not form:
#             return None

#         search_url = form['action']
#         data = {input_tag['name']: input_tag.get('value', '') for input_tag in form.find_all('input')}
#         data.update({'search_term': business_id})

#         # Submit the form
#         response = session.post(search_url, data=data)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.text, 'html.parser')

#         # Find the "Website" field
#         website_field = soup.find(text='Website')
#         if website_field:
#             url = website_field.find_next('a').get('href')
#             return url
#         return None

# def read_csv(file_path):
#     with open(file_path, mode='r', encoding='utf-8') as file:
#         reader = csv.DictReader(file)
#         data = [row for row in reader]
#     return data

# def write_csv(file_path, data):
#     with open(file_path, mode='w', newline='', encoding='utf-8') as file:
#         fieldnames = ['businessId', 'name', 'url']
#         writer = csv.DictWriter(file, fieldnames=fieldnames)
#         writer.writeheader()
#         writer.writerows(data)

# # Read the initial CSV file
# input_csv = 'business_data.csv'
# business_data = read_csv(input_csv)

# # Process each business and fetch the URL
# for company in business_data:
#     business_id = company['businessId']
#     url = fetch_company_url(business_id)
#     company['url'] = url if url else ''  # Set to empty string if URL is not found
#     time.sleep(1)  # Be respectful of the website's rate limits

# # Write the new data to a CSV file
# output_csv = 'business_data_with_urls.csv'
# write_csv(output_csv, business_data)

# print(f"Data with URLs has been written to {output_csv}")
