import requests
import csv

# URL to the JSON data
url = "https://avoindata.prh.fi/bis/v1?totalResults=false&maxResults=1000&resultsFrom=0&businessLineCode=28990&companyRegistrationFrom=1900-02-28"

try:
    # Fetching the JSON data from the URL
    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful

    # Parsing JSON data
    data = response.json()

    # Extracting objects with 'businessId' and 'name'
    filtered_data = [
        {"businessId": item["businessId"], "name": item["name"]}
        for item in data.get('results', [])
        if 'businessId' in item and 'name' in item
    ]

    # Writing the filtered data to a CSV file
    with open("business_data.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["businessId", "name"])
        writer.writeheader()
        writer.writerows(filtered_data)

    print(f"Data has been written to business_data.csv")

except requests.exceptions.RequestException as e:
    print(f"Error fetching data: {e}")


