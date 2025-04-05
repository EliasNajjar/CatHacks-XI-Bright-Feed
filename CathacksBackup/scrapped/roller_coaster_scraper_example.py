!pip install Wikipedia-API > /dev/null

import pandas as pd
import wikipediaapi
import requests
from bs4 import BeautifulSoup
from tqdm.notebook import tqdm
import json

pd.set_option('display.max_columns', 500)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36 Google-Colab-Scraper/1.0'  # Replace with your own User-Agent string
}

wiki = wikipediaapi.Wikipedia(
    language='en',
    extract_format=wikipediaapi.ExtractFormat.HTML,
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36 Google-Colab-Scraper/1.0'
)

cat = wiki.page('Category:Roller coaster introductions by year')

DEBUG = True
ds = []

counter = 0  # Counter variable to track the number of roller coasters processed
stop_early = False
stop_at = 20

def process_category(category):
    global counter  # Declare the counter as a global variable

    for coaster, page in tqdm(category.categorymembers.items()):
        if not page.exists():
            continue
        if DEBUG:
            print("Page - {}".format(page.title))

        # Scrape and parse the relevant information from the Wikipedia article
        # Customize this code according to the structure and layout of the articles

        coaster_data = {
            'Name': '',
            'Location': '',
            'ParkSection': '',
            'Coordinates': '',
            'Status': '',
            'OpeningDate': '',
            'Replaced': '',
            'Type': '',
            'Manufacturer': '',
            'Designer': '',
            'Model': '',
            'TrackLayout': '',
            'LiftLaunchSystem': '',
            'Height': '',
            'Drop': '',
            'Length': '',
            'Speed': '',
            'Inversions': '',
            'Duration': '',
            'MaxVerticalAngle': '',
            'Capacity': '',
            'HeightRestriction': ''
            # Add more desired attributes here
        }

        # Retrieve the web page of the roller coaster
        url = page.fullurl
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find and extract additional attributes from the web page
        # Customize this code based on the HTML structure of the web page

        coaster_name_element = soup.find('th', {'class': 'infobox-above', 'style': 'fn org'})
        if coaster_name_element:
            coaster_name = coaster_name_element.text.strip()
            coaster_data['Name'] = coaster_name
            
        rows = soup.find_all('tr')
        for row in rows:
            header_element = row.find('th', {'class': 'infobox-header', 'style': 'background-color:lightgray;'})
            if header_element:
                a_element = header_element.find('a')
                if a_element:
                    value_text = a_element.text.strip()
                    coaster_data['Location'] = value_text
            th_element = row.find('th', {'class': 'infobox-label'})
            if th_element:
                label_text = th_element.text.strip()
                td_element = row.find('td', {'class': 'infobox-data'})
                if td_element:
                    value_text = td_element.text.strip()
                    if label_text == 'Location':
                        coaster_data['Location'] = value_text
                    elif label_text == 'Park section':
                        coaster_data['ParkSection'] = value_text
                    elif label_text == 'Coordinates':
                        coaster_data['Coordinates'] = value_text
                    elif label_text == 'Status':
                        coaster_data['Status'] = value_text
                    elif label_text == 'Opening date':
                        coaster_data['OpeningDate'] = value_text
                    elif label_text == 'Replaced':
                        coaster_data['Replaced'] = value_text
                    elif label_text == 'Type':
                        coaster_data['Type'] = value_text
                    elif label_text == 'Manufacturer':
                        coaster_data['Manufacturer'] = value_text
                    elif label_text == 'Designer':
                        coaster_data['Designer'] = value_text
                    elif label_text == 'Model':
                        coaster_data['Model'] = value_text
                    elif label_text == 'Track layout':
                        coaster_data['TrackLayout'] = value_text
                    elif label_text == 'Lift/launch system':
                        coaster_data['LiftLaunchSystem'] = value_text
                    elif label_text == 'Height':
                        coaster_data['Height'] = value_text
                    elif label_text == 'Drop':
                        coaster_data['Drop'] = value_text
                    elif label_text == 'Length':
                        coaster_data['Length'] = value_text
                    elif label_text == 'Speed':
                        coaster_data['Speed'] = value_text
                    elif label_text == 'Inversions':
                        coaster_data['Inversions'] = value_text
                    elif label_text == 'Duration':
                        coaster_data['Duration'] = value_text
                    elif label_text == 'Max vertical angle':
                        coaster_data['MaxVerticalAngle'] = value_text
                    elif label_text == 'Capacity':
                        coaster_data['Capacity'] = value_text
                    elif label_text == 'Height restriction':
                        coaster_data['HeightRestriction'] = value_text

        # Append the coaster data to the list
        ds.append(coaster_data)

        # Increment the counter
        counter += 1

        # Break the loop if the desired number of coasters is reached
        if stop_early and counter == stop_at:
            break

# Process the main category and its subcategories
process_category(cat)

for subcat in cat.categorymembers.values():
    if subcat.namespace == wikipediaapi.Namespace.CATEGORY:
        print("Processing subcategory: {}".format(subcat.title))
        process_category(subcat)

# Convert the coaster data list to a DataFrame
df = pd.DataFrame(ds)

# Export the DataFrame to a JSON file
df.to_json('roller_coasters.json', orient='records')

# Log the completion message
print("Data extraction completed and saved as 'roller_coasters.json'")