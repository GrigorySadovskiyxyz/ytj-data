import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()  # Optional argument, if not specified will search path.
driver.get('https://tietopalvelu.ytj.fi/')
driver.maximize_window()
time.sleep(5)
search_form = driver.find_element(by=By.ID, value="businessIdOrLEI")
search_form.send_keys('2811294-4')
clickable = driver.find_element(By.XPATH, '//button[@class="btn btn-primary false mr-2"]')
clickable.click()

try:
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//tr[@class="current-info-first-row current-info-last-row"]')))
    elements = driver.find_elements(By.XPATH, '//div[@class="pt-3 avoid-break-before desktop"]/table/tbody')
    
    target_element = None
    for element in elements:
        divs = element.find_elements(By.TAG_NAME, "div")
        for div in divs:
            if 'www.' in div.text:
                target_element = div
                break
        if target_element:
            break

    if target_element:
        print(target_element.text)
    else:
        print("null")
except Exception as e:
    print(f"An error occurred: {e}")

driver.quit()

#search_box = driver.find_element("name", "q")

#search_box.send_keys('ChromeDriver')

#search_box.submit()

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
