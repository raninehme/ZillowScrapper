import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import numpy as np
import re
import time


# Use to get all pages
def ifnull(var, val):
    if var is None:
        return val
    return var


class ZillowScraper:
    def __init__(self, city, start_page=1, max_page=None, sort_by='newest'):
        # Request Prep
        self.base_url = 'https://www.zillow.com'
        self.city = city
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'cookie': 'zguid=23|%24d14f0059-d03b-4422-9f57-5862fcd13490; _ga=GA1.2.1741285320.1590755697; zjs_user_id=null; zjs_anonymous_id=%22d14f0059-d03b-4422-9f57-5862fcd13490%22; __gads=ID=1050523ba93d593d:T=1590755700:S=ALNI_MZlJJ_xqSbd51oJisV_HY4g017Ehw; _gcl_au=1.1.2000298647.1590755705; KruxPixel=true; _fbp=fb.1.1590755705919.1815197270; _pxvid=d6c5ec75-a1a8-11ea-b8a9-0242ac120009; KruxAddition=true; JSESSIONID=3E7EBDB1F8931DF7D0DE9992546AE0B3; zgsession=1|200e23e0-9534-4d27-931f-caa3de6b483b; _gid=GA1.2.1328942480.1590858452; _gat=1; DoubleClickSession=true; GASession=true; _uetsid=fdde22d5-862a-8a7d-93e4-a16c574edf91; _pin_unauth=YzUyOGQ2OGMtMmQ3YS00NGZkLTg3MmEtOGJlODM1YWMwMTA1; _px3=026336d3721eec42bcdec3278ad2d3ac2014d5e65707b21624fb2e743d9a89be:mq3WRz2RNL5PBIvbYNHCxq5VfXHXy2YKC+8Lqn97pIw8MiKppH7Cx7AjKzbAFi1zcehKGY36aIgsnE9NiPKwlw==:1000:4U1o3ogIQ0KzfyMd2QYEFGDnD1augezy5bJlzEn9ZHE89B2uEIxDg8BmsGj8szPwyIz1Yv15S2V0TV5P+0jCFisfGk92XM4DM7K13GCtNr0HXhNGftVBFxVrCv8ApRphw/Qwj7AcagCh9i6FPiQGLFruxVASJXLsNpFeWimekVY=; AWSALB=ZKAGBcH2BwM6D1bRKOPynbOqyclySGz5U/fZB+wO3MYQ91UR9A5rFVtFsmjOkrMASUJguhtsJRZDM7IlBiWVT/pGw2S0BjxgEZmpFPrBZEqU2lWTE2NMArtecZD2; AWSALBCORS=ZKAGBcH2BwM6D1bRKOPynbOqyclySGz5U/fZB+wO3MYQ91UR9A5rFVtFsmjOkrMASUJguhtsJRZDM7IlBiWVT/pGw2S0BjxgEZmpFPrBZEqU2lWTE2NMArtecZD2; search=6|1593450465587%7Crect%3D40.843698984643765%252C-73.50417109960938%252C40.567821651427245%252C-74.45174190039063%26rid%3D6181%26disp%3Dmap%26mdm%3Dauto%26p%3D2%26z%3D0%26lt%3Dfsbo%26fs%3D1%26fr%3D0%26mmm%3D0%26rs%3D0%26ah%3D0%26singlestory%3D0%26housing-connector%3D0%26abo%3D0%26garage%3D0%26pool%3D0%26ac%3D0%26waterfront%3D0%26finished%3D0%26unfinished%3D0%26cityview%3D0%26mountainview%3D0%26parkview%3D0%26waterview%3D0%26hoadata%3D1%26zillow-owned%3D0%263dhome%3D0%09%096181%09%09%09%09%09%09',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
        }
        self.sort = sort_by
        self.is_valid = True
        self.sleep_sec = 20

        # Page Manipulation
        self.start_page = start_page
        self.current_page = start_page
        self.max_page = max_page  # None for all pages
        self.NextPage = True

        self.result_list = []

        init_msg = f'Attempting to Scrape {self.city}'.upper()
        print(init_msg.center(200, '='), end="\n")

    def detect_captcha(self, soup, url, params=None):
        captcha = soup.find('h5')

        while captcha:
            if "Please verify you're a human to continue" in captcha.text:

                print(f'Captcha Detected; Retrying in {self.sleep_sec} seconds')

                time.sleep(self.sleep_sec)

                logger = f'Scraping Page {self.current_page}'
                print(logger.ljust(50, '.'), end="")

                response = requests.get(url=url, headers=self.headers, params=params)

                soup = BeautifulSoup(response.text, 'lxml')
                captcha = soup.find('h5')
            else:
                captcha = None

    def generate_urls(self):
        logger = f'Scraping Page {self.current_page}'
        print(logger.ljust(50, '.'), end="")

        url = f'{self.base_url}/{self.city}/{self.sort}/{self.current_page}_p/'.lower()

        params = {
            # 'searchQueryState': '{"pagination":{"currentPage": %s}, "isMapVisible":false,"filterState":{"isForSaleByAgent":{"value":false},"isNewConstruction":{"value":false},"isForSaleForeclosure":{"value":false},"isComingSoon":{"value":false},"isAuction":{"value":false}},"isListVisible":true}' % self.current_page
        }

        response = requests.get(url=url, headers=self.headers, params=params)

        # Catch Last Page Route
        if response.url.lower() == f'{self.base_url}/{self.city}/{self.sort}/'.lower() and self.current_page != 1:
            self.NextPage = False
            return None

        try:
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'lxml')
            # print(soup)

            # Check for Captcha
            self.detect_captcha(soup=soup, url=url, params=params)

            # landing page
            soup = BeautifulSoup(response.text, 'lxml')
            properties = soup.find(
                class_='photo-cards photo-cards_wow photo-cards_short photo-cards_extra-attribution')

            if properties:
                for house in properties.contents:
                    primary_data = house.find('script', {'type': 'application/ld+json'})

                    if primary_data:
                        # Get url
                        url = json.loads(primary_data.contents[0])['url']

                        # Get Author
                        listing_card = house.find('div', class_='list-card-footer')
                        listed_by = re.sub(r'\([^()]*\)', '',
                                           listing_card.text.replace('Listing by:', '')).strip()

                        yield url, listed_by
            else:
                self.NextPage = False

        except requests.exceptions.HTTPError:
            print('Error 404 - Page Not Found.')
            self.is_valid = False

    def fetch_listing(self, listing_url):
        response = requests.get(url=listing_url, headers=self.headers)

        try:
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'lxml')

            # Check for Captcha
            self.detect_captcha(soup=soup, url=listing_url)

            return response
        except requests.exceptions.HTTPError:
            return None

    def parse_listing(self, listing_url, by):
        response = self.fetch_listing(listing_url=listing_url)
        soup = BeautifulSoup(response.text, 'lxml')

        # Get Data from JS
        house = soup.find(class_='ds-data-col ds-white-bg ds-data-col-data-forward')

        while not house:
            time.sleep(20)
            response = self.fetch_listing(listing_url=listing_url)
            soup = BeautifulSoup(response.text, 'lxml')

            # Get Data from JS
            house = soup.find(class_='ds-data-col ds-white-bg ds-data-col-data-forward')
        else:
            main_info = house.find_all('script', {'type': 'application/ld+json'})[0]
            secondary_info = house.find_all('script', {'type': 'application/ld+json'})[1]
            on_zillow = house.find('div', {'class': 'Text-c11n-8-18-0__aiai24-0 einFCw'}).text

            status_details = house.find_all('span', class_='sc-pYA-dN ivRwcz ds-status-details')[1]
            ad_type = status_details.find('span', {'class': 'ds-status-icon'}).next_sibling

            if main_info and secondary_info:
                main_data = json.loads(main_info.contents[0])
                secondary_data = json.loads(secondary_info.contents[0])

                # Get Beds & Bathrooms
                description = secondary_data.get('description', ', ,').split(',')
                bedrooms = re.sub("[^0-9]", "", description[0])
                bathrooms = re.sub("[^0-9]", "", description[1])

                # Avoid Errors on missing elements
                if secondary_data.get('offers'):
                    price = secondary_data['offers'].get('price', np.nan)
                else:
                    price = np.nan

                # Fill List
                self.result_list.append({
                    'page': self.current_page,
                    'url': listing_url,
                    'address': main_data['name'],
                    'area': main_data['floorSize']['value'],
                    'price': price,
                    'bedrooms': bedrooms,
                    'bathrooms': bathrooms,
                    'on_zillow': on_zillow,
                    'listed_by': by,
                    'ad_type': ad_type
                })

    def calc_result(self):
        zillow_df = pd.DataFrame(self.result_list)

        print(zillow_df)

        # get total number of properties
        total = len(zillow_df.index)

        # Clean Area and replace None with 0
        zillow_df['area'].replace(r'[a-zA-Z,%]', '', regex=True, inplace=True)
        zillow_df['area'] = zillow_df['area'].fillna(0).astype(int)

        # Get avg prices and deal with zeroes
        zillow_df['price_per_sqft'] = zillow_df['price'].div(zillow_df['area']).replace(np.inf, np.NaN)

        avg_price_sqft = zillow_df["price_per_sqft"].mean()
        avg_price = zillow_df["price"].mean()

        # Get counts per Columns
        adtype_df = zillow_df['ad_type'].value_counts()
        listedby_df = zillow_df['listed_by'].value_counts()

        print('\n')
        print(adtype_df)

        print('\n')
        print(listedby_df)

        print(f'\nTotal Number of Properties = {total}')
        print(f'Total Average Price = {avg_price}')
        print(f'Average Price per sqft = {avg_price_sqft}')

        end_msg = f'Scraping {self.city.upper()} Finished'.upper()
        print(end_msg.center(200, '='), end="\n\n")

    def run(self):
        while self.NextPage and self.is_valid and self.current_page <= ifnull(self.max_page, 99999):
            for listing, listed_by in self.generate_urls():                 # iterate on each url
                self.parse_listing(listing_url=listing, by=listed_by)  # Scrape Details

            self.current_page += 1

            if self.is_valid:
                print('Done!')
            else:
                return None

        if self.result_list and self.is_valid:
            self.calc_result()
        else:
            print('No Result Found')
            end_msg = f'Scraping {self.city.upper()} Finished'.upper()
            print(end_msg.center(200, '='), end="\n\n")


if __name__ == '__main__':
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1500)
    pd.set_option('display.max_colwidth', None)

    test_invalid = ZillowScraper(city='test_invalid')
    test_invalid.run()

    NewYork = ZillowScraper(city='new-york-ny')
    NewYork.run()

    Florida = ZillowScraper(city='FL')
    Florida.run()
