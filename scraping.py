# importing of the required modules 
import requests
from bs4 import BeautifulSoup
import pandas as pd
import concurrent.futures
from time import sleep
from random import uniform
import logging


# Fetch the pages urls and headers 
def fetch_page(url, headers):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.content
    except Exception as e:
        logging.error(f"Error fetching {url}: {str(e)}")
        return None


def parse_property_card(each):
    price_tag = each.find('span', class_='price-tag')
    price = price_tag.text.strip() if price_tag else "None"
    
    location_tag = each.find("p", class_="property__card-location")
    location = location_tag.text.strip() if location_tag else "None"
    
    href_link = each.find('a', href=True)
    link = href_link.get('href') if href_link else None
    
    return price, location, link

def parse_overview_section(inner_soup):
    fields = {
        'BEDROOM': 'bedroom_number',
        'FLOOR': 'floor_number',
        'BATHROOM': 'bathroom_number',
        'BUILTUP AREA': 'area_number',
        'ROAD ACCESS': 'Road_access_number',
        'FACING': 'facing_direction',
        'FURNISH STATUS': "Furnish_status",
        'PARKING': 'Parking',
        'BUILT YEAR': 'Built Year'
    }
    
    extracted_values = {}
    try:
        overview_section = inner_soup.find('div', id='sectionOverview')
        if overview_section:
            ul_overview = overview_section.find('ul', class_='list-overview')
            if ul_overview:
                for keyword, field in fields.items():
                    li = ul_overview.find(lambda tag: tag.name == 'li' and keyword in tag.text.upper())
                    extracted_values[field] = li.find("h5").text.strip() if li and li.find("h5") else "None"
    except Exception as e:
        logging.error(f"Error parsing overview section: {str(e)}")
    
    return extracted_values

def process_property(property_card, base_url, headers):
    try:
        price, location, link = parse_property_card(property_card)
        if not link:
            return None
            
        inner_url = f"{base_url}{link}"
        inner_content = fetch_page(inner_url, headers)
        if not inner_content:
            return None
            
        inner_soup = BeautifulSoup(inner_content, "lxml")
        extracted_values = parse_overview_section(inner_soup)
        extracted_values.update({'price': price, 'location': location})
        
        # Add small random delay to avoid overwhelming the server
        sleep(uniform(0.5, 1.5))
        return extracted_values
        
    except Exception as e:
        logging.error(f"Error processing property: {str(e)}")
        return None

def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US, en;q=0.5'
    }
    
    base_url = "https://www.nepalhomes.com"
    all_extracted_data = []
    
    # Process pages in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for page in range(200,300):
            url = f"{base_url}/search?find_property_purpose=5db2bdb42485621618ecdae6&find_property_category=5d660cb27682d03f547a6c4a&page={page}&sort=1&find_selected_price_min=1&find_selected_price_max=5"
            
            content = fetch_page(url, headers)
            if not content:
                continue
                
            soup = BeautifulSoup(content, "lxml")
            container = soup.find_all("div", class_="property__card property__card-type-sd property__card-type-sd-xl")
            
            # Process properties in parallel
            future_to_property = {executor.submit(process_property, prop, base_url, headers): prop 
                                for prop in container}
            
            for future in concurrent.futures.as_completed(future_to_property):
                result = future.result()
                if result:
                    all_extracted_data.append(result)
            
            logging.info(f"Completed page {page}")
    
    # Convert to DataFrame and save
    df = pd.DataFrame(all_extracted_data)
    df.to_excel('extracted_data_updates4.xlsx', index=False)
    print("Data has been saved to 'extracted_data_updates.xlsx'")

if __name__ == "__main__":
    main()
