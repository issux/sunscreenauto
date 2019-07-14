#!/usr/bin/env python
# *-* coding: utf-8 *-*

import requests
from bs4 import BeautifulSoup
from pathlib import Path
import csv

class MifarmaFetcher():

    DATA_SOURCE = 'https://www.mifarma.es/cosmetica-y-belleza/sol/protectores-solares/'
    IMAGES_PATH = '../../data/mifarma/'
    CSV_PATH = '../../data/mifarma.csv'

    def __init__(self):
        self.data = []
        self.global_counter = 0

    def export_csv(self):
        with open(self.CSV_PATH, mode='w+', encoding='utf-8-sig') as csv_file:

            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            csv_writer.writerow(['title','link','old_price','special_price','after_special_price','discount_price','picture_image'])

            for row in self.data:
                csv_writer.writerow([row['title'],row['link'],row['old_price'],row['special_price'],row['after_special_price'],row['discount_price'],row['picture_image']])

    def fetch(self, page_link = None):

        if not page_link:
            page_link = self.DATA_SOURCE

        page = requests.get(page_link)

        if page.status_code == 200:

            soup = BeautifulSoup(page.content.decode('utf-8', 'ignore'), 'html.parser')

            listing = soup.find('div', attrs={'class' : 'listado-completo'})

            if listing:
                elements = listing.find_all('li', attrs={'class' : 'item'})

                if elements:
                    for counter, element in enumerate(elements):
                        self.global_counter += 1
                        print('Global: ' + str(self.global_counter) + ' Element in page ' + str(counter) + ' found:')

                        (data_link, data_title) = self.fetch_title_link(element)

                        data_old_price = self.fetch_old_price(element)
                        
                        data_special_price = self.fetch_special_price(element)
                        
                        data_discount_price = self.fetch_discount_price(element)
                        
                        data_after_special_price = self.fetch_after_special_price(element)

                        data_picture_image = self.fetch_picture_image(element)

                        self.data.append(
                            {
                                'title': data_title,
                                'link': data_link,
                                'picture_image': data_picture_image,
                                'old_price': data_old_price if data_old_price is not None else '0',
                                'special_price': data_special_price if data_special_price is not None else '0',
                                'after_special_price': data_after_special_price if data_after_special_price is not None else '0',
                                'discount_price': data_discount_price if data_discount_price is not None else '0',
                            })

                        print

                self.check_next_page(soup)

    def fetch_title_link(self, element):
        title = element.find('h2', attrs={'class' : 'product-name'})

        if title:
            data_title = title.find('a').text
            data_link = title.find('a').get('href')
            print('Link: ' + data_link)
            print('Title: ' + data_title)
            return (data_link, data_title)
        else:
            print('No title')
            return (None, None)
        
    def fetch_old_price(self, element):
        old_price = element.find('p', attrs={'class': 'old-price'})
        
        if old_price:
            old_price_value = old_price.find('span',attrs={'class': 'price'})
            
            if old_price_value:
                data_old_price = old_price_value.text.strip()
                print("Old price: " + data_old_price)
                return data_old_price
            else:
                return None
        else:
            return None
        
    def fetch_special_price(self, element):
        special_price = element.find('p', attrs={'class': 'special-price'})
        
        if special_price:
            special_price_value = special_price.find('span',attrs={'class': 'price'})
            
            if special_price_value:
                data_special_price = special_price_value.text.strip()
                print("Special price: " + data_special_price)
                return data_special_price
            else:
                return None
        else:
            return None
    
    def fetch_discount_price(self, element):
        discount_price = element.find('span', attrs={'class': 'descuento'})
        
        if discount_price:
            data_discount_price = discount_price.text.strip()
            print("Discount price: " + data_discount_price)
            return data_discount_price
        else:
            return None
        
    def fetch_after_special_price(self, element):
        price_wrapper = element.find('div', attrs={'class': 'price-wrapper'})
        
        if price_wrapper:
        
            after_special_price = price_wrapper.find('span', attrs={'class': 'after-special'})
        
            if after_special_price:
                data_after_special_price = after_special_price.text.strip()
                print("After special price: " + data_after_special_price)
                return data_after_special_price
            else:
                return None
        else:
            return None
        
    def download_file_image(self, image_url):
        page_image = requests.get(image_url, stream=True)
        if page_image.status_code == 200:
            print(Path(image_url).stem)
            with open(self.IMAGES_PATH + Path(image_url).stem + '.jpg', 'wb') as image_file:
                for chunk in page_image:
                    image_file.write(chunk)
                    
    def fetch_picture_image(self, element):
        picture_image = element.find('a', attrs={'class' : 'product-image'})

        if picture_image:
            data_picture_image = picture_image.find('img').get('src').strip()
            print('Picture Image: ' + data_picture_image)
            self.download_file_image(data_picture_image)

        return data_picture_image

    def check_next_page(self, soup):
        next_page =soup.find('a', attrs={'class' : 'i-next'})

        if next_page:
            next_page_link = next_page.get('href')
            print('Processing next page: ' + next_page_link)
            self.fetch(next_page_link)

    def run(self):
        print('Running Mifarma Fetcher')
        self.fetch(None)

        print('Data to store')
        print(self.data)

        print('Exporting to CSV')
        self.export_csv()
        print('Done')


MifarmaFetcher().run()