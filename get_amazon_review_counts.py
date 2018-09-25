from lxml import html  
import os
import requests

from time import sleep
from datetime import date

import pandas as pd
 
def Parse_Amazon(asin):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
    url = "http://www.amazon.com/dp/" + asin
	
    tries = 0
    NAME = None

    while ((tries <= 3) and (NAME == None)):
        tries = tries + 1

        try:
            page = requests.get(url, headers = headers)
            sleep(3)
            doc = html.fromstring(page.content)
			
            XPATH_NAME = '//h1[@id="title"]//text()'
            XPATH_SALE_PRICE = '//span[contains(@id,"ourprice") or contains(@id,"saleprice")]/text()'
            XPATH_ORIGINAL_PRICE = '//td[contains(text(),"List Price") or contains(text(),"M.R.P") or contains(text(),"Price")]/following-sibling::td/text()'
            XPATH_CATEGORY = '//a[@class="a-link-normal a-color-tertiary"]//text()'
            XPATH_AVAILABILITY = '//div[@id="availability"]//text()'
            XPATH_AGGREGATE_RATING = '//span[contains(@id,"CustomerReviewText")]//text()'
 
            RAW_NAME = doc.xpath(XPATH_NAME)
            RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
            RAW_CATEGORY = doc.xpath(XPATH_CATEGORY)
            RAW_ORIGINAL_PRICE = doc.xpath(XPATH_ORIGINAL_PRICE)
            RAW_AVAILABILITY = doc.xpath(XPATH_AVAILABILITY)
            RAW_RATINGS  = doc.xpath(XPATH_AGGREGATE_RATING)
 
            NAME = ' '.join(''.join(RAW_NAME).split()) if RAW_NAME else None
            SALE_PRICE = ' '.join(''.join(RAW_SALE_PRICE).split()).strip() if RAW_SALE_PRICE else None
            CATEGORY = ' > '.join([i.strip() for i in RAW_CATEGORY]) if RAW_CATEGORY else None
            ORIGINAL_PRICE = ''.join(RAW_ORIGINAL_PRICE).strip() if RAW_ORIGINAL_PRICE else None
            AVAILABILITY = ''.join(RAW_AVAILABILITY).strip() if RAW_AVAILABILITY else None
            RATINGS = ''.join(RAW_RATINGS).strip() if RAW_RATINGS else None
 
            if not ORIGINAL_PRICE:
                ORIGINAL_PRICE = SALE_PRICE
 
            if page.status_code != 200:
                raise ValueError('captcha')
            
            data = {
                    'DATE': date.today(),
                    'ASIN': asin,
                    'NAME': NAME,
                    'SALE_PRICE': SALE_PRICE,
                    'CATEGORY': CATEGORY,
                    'ORIGINAL_PRICE': ORIGINAL_PRICE,
                    'AVAILABILITY': AVAILABILITY,
                    'RATINGS': RATINGS,
                    'URL': url,
                    }
					
            print(data)
		
        except Exception as e:
            print(e)
            
            error_delay = 10
            
            print('Sleeping for {} seconds'.format(error_delay))
            sleep(error_delay)
	
    return data
			
		

AsinList = [
# A few furnace filters
'B002CJN0H2', # Filtrete Clean Living Basic Dust AC Furnace Air Filter, MPR 300, 16 x 25 x 1-Inches, 6-Pack
'B005ESP0VM', # Nordic Pure 20x20x4M13-2 20x20x4 MERV 13 Pleated AC Furnace Air Filter, Box of 2, 4-Inch
'B00LCRXPIY' # Idylis Furnace Humidifier Filter Fits Aprilaire
]

extracted_data = []

counter = 0

for i in AsinList:
	counter = counter + 1
	print("Processing: " + i)
	extracted_data.append(Parse_Amazon(i))
	print(str(int((counter / len(AsinList)) * 100)) + "% done.")
	sleep(3)

df = pd.DataFrame.from_dict(extracted_data)
df["RATINGS"] = df["RATINGS"].str.split(' ').str.get(0).str.replace(',', '').apply(int)


# Save the results to file
currentPath = os.getcwd()
csv_file = currentPath + '/amazon_data - ' + format(date.today(), '%Y-%m-%d') + '.csv'

df.to_csv(csv_file)