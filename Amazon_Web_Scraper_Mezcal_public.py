from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from urllib.parse import quote

def get_title(soup):
    try:
        title = soup.find("span", attrs={"id": 'productTitle'})
        title_value = title.text
        title_string = title_value.strip()
    except AttributeError:
        title_string = ""
    return title_string

def get_price(soup):
    try:
        # Look for the price within the specific widget
        price_tag = soup.find("div", {"data-csa-c-type": "widget", "data-csa-c-slot-id": "apex_dp_offer_display"})
        price_str = price_tag.find("span", class_="a-offscreen").get_text(strip=True)

        # Extract the numerical part of the price string
        price_value = ''.join(char for char in price_str if char.isdigit() or char in ['.', ','])

        # Convert the cleaned price string to a float and round to 2 decimal places
        price = round(float(price_value.replace(',', '')), 2)
    except AttributeError:
        price = None
    return price



def get_rating(soup):
    try:
        rating = soup.find("i", attrs={"class": 'a-icon-alt'}).string.strip()
    except AttributeError:
        try:
            rating = soup.find("span", attrs={"class": 'a-icon-alt'}).string.strip()
        except:
            rating = ""
    return rating

def get_review_count(soup):
    try:
        review_count = soup.find("span", attrs={"id": 'acrCustomerReviewText'}).string.strip()
    except AttributeError:
        review_count = ""
    return review_count

#Enter your user-agent below

HEADERS = {
    'User-Agent': 'ENTER YOUR USER AGENT HERE',
    'Accept-Language': 'en-GB, en;q=0.5'
}

URL = "https://www.amazon.co.uk/s?k=mezcal&crid=3P6XL9STVD8RR&sprefix=mezcal%2Caps%2C104&ref=nb_sb_ss_ts-doa-p_1_6"

webpage = requests.get(URL, headers=HEADERS)
soup = BeautifulSoup(webpage.content, "html.parser")

links = soup.find_all("a", attrs={'class': 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})
links_list = []

for link in links:
    links_list.append(link.get('href'))

d = {"title": [], "price": [], "rating": [], "reviews": [], "url": []}

for link in links_list:
    if not link.startswith(('http://', 'https://')):
        link = "https://www.amazon.co.uk" + link

    encoded_link = quote(link, safe='/:?=&')
    new_webpage = requests.get(encoded_link, headers=HEADERS)
    new_soup = BeautifulSoup(new_webpage.content, "html.parser")

    d['title'].append(get_title(new_soup))
    d['price'].append(get_price(new_soup))
    d['rating'].append(get_rating(new_soup))
    d['reviews'].append(get_review_count(new_soup))
    d['url'].append(link)

amazon_df = pd.DataFrame.from_dict(d)
amazon_df['title'].replace('', np.nan, inplace=True)
amazon_df = amazon_df.dropna(subset=['title'])

amazon_df.to_csv("amazon_data_with_url.csv", header=True, index=False)
