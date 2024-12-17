import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
from random import randint
# Initialize a list to store extracted data
all_extracted_data = []

for page in range(10,20):
    headerss = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36', 'Accept-langauge': 'en-US, en;q=0.5'}
    url = f"https://www.nepalhomes.com/search?find_property_purpose=5db2bdb42485621618ecdae6&find_property_category=5d660cb27682d03f547a6c4a&page={page}&sort=1&find_selected_price_min=1&find_selected_price_max=5"
    request = requests.get(url,headers=headerss)
    soup = BeautifulSoup(request.content, "lxml")
    container = soup.find_all("div", class_="property__card property__card-type-sd property__card-type-sd-xl")
    
    for each in container: 
        price_tag = each.find('span', class_='price-tag')
        price = price_tag.text.strip() if price_tag else "None"
        
        href_link = each.find('a', href=True)
        link = href_link.get('href')

        inner_url = f"https://www.nepalhomes.com{link}" 

        inner_request = requests.get(inner_url)
        inner_soup = BeautifulSoup(inner_request.content, "lxml")

        ul_overview = inner_soup.find('div', id='sectionOverview').find('ul', class_='list-overview')
        
        # Define the fields to extract
        fields = {
            'BEDROOM': 'bedroom_number',
            'FLOOR': 'floor_number',
            'BATHROOM': 'bathroom_number',
            'BUILTUP AREA': 'area_number',
            'ROAD ACCESS': 'Road_access_number',
            'FACING' : 'facing_direction',
            'FURNISH STATUS':"Furnish_status",
            'PARKING':'Parking'
        }

        # Initialize an empty dictionary to store the results
        extracted_values = {'price': price}

        # Iterate over the dictionary and extract information
        for keyword, field in fields.items():
            li = ul_overview.find(lambda tag: tag.name == 'li' and keyword in tag.text.upper())
            extracted_values[field] = li.find("h5").text.strip() if li and li.find("h5") else "None"

        # Append the extracted values to the list
        all_extracted_data.append(extracted_values)
    sleep(randint(2,4))    
# Convert the list of extracted data into a DataFrame
df = pd.DataFrame(all_extracted_data)

# Save the DataFrame to an Excel file
df.to_excel('extracted_data.xlsx', index=False)

print("Data has been saved to 'extracted_data1.xlsx'")
