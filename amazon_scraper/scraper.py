from bs4 import BeautifulSoup
from random import randint
from typing import Optional
from header import *
from proxy import *
from numpy import nan
from datetime import datetime

import time
import pandas as pd


def get_soup(URL: str) -> BeautifulSoup:
    """Returns a soup from <URL>

    WARNING: Make sure to use time.sleep randomly 
    when using this function repeatedly
    """
    try:
        html_text = generate_req(URL)
        return BeautifulSoup(html_text.content, 'html.parser')
    except Exception as error:
        print(f"Error getting URL: {error}")


def first_num(string: str) -> int:
    """Helper function returns the occurence of number character
    
    <string> must contain a number
    """
    for i, char in enumerate(string):
        if char.isnumeric():
            return i


def get_prefix(URL: str) -> str:
    """Return the correct URL prefix"""

    ending = URL.split('.')
    ending[-1] = ending[-1][:ending[-1].index('/')]
    url_prefix = '.'.join(ending)
    return url_prefix


def parse_products(soup: BeautifulSoup, prefix: str) -> Optional[list[list]]:
    """Returns the info of the product: price, title and rating"""
    product_info = []
    products = soup.find_all('div', class_="sg-col-20-of-24 "
                             "s-result-item s-asin sg-col-0-of-12 "
                             "sg-col-16-of-20 sg-col s-widget-spacing-small"
                             " sg-col-12-of-16")

    if not products:
        products = soup.find_all('div', class_="_octopus-search-result-card"
                                 "_style_apbSearchResultItem__2-mx4")
    if not products:
        products = soup.find_all('div', class_="sg-col-4-of-24 "
                                 "sg-col-4-of-12 s-result-item s-asin sg-col-4"
                                 "-of-16 sg-col s-widget-spacing-small sg-col"
                                 "-4-of-20")
        sponsored_product = soup.find_all('d_iv', class_="sg-col-4-of-24 "
                                      "sg-col-4-of-12 "
                                      "s-result-item s-asin sg-col-4-of-16 "
                                      "AdHolder sg-col s-widget-spacing-small "
                                      "sg-col-4-of-20")
        if sponsored_product:
            products.extend(sponsored_product)
    
    if not products:
        products = soup.find_all('div', class_="sg-col-20-of-24 "
                                 "s-result-item s-asin sg-col-0-of-12 "
                                 "sg-col-16-of-20 sg-col s-widget-spacing-smal"
                                 "l gsx-ies-anchor sg-col-12-of-16")

    if not products:
        print('No products on pge')
        return None

    for product in products:
        p_title = product.find('span', class_="a-size-medium "
                                     "a-color-base a-text-normal").get_text()
        price = product.find('span', class_='a-offscreen')
        price_index = first_num(price.text) if price else None
        p_price = float(price.text[price_index:].replace(',', '', 1)) if price else nan
        rating = product.find('span', class_='a-icon-alt')
        p_rating = float(rating.text[:3]) if rating else None
        p_url = f"{prefix}/dp/{product['data-asin']}"
        product_info.append([p_title, p_price, p_rating, p_url])
    return product_info


def get_next(soup: BeautifulSoup, prefix: str) -> Optional[BeautifulSoup]:
    """Returns the next page soup. If no next page, returns None

    WARNING: Use time.sleep randomly when repeatedly calling this function
    """
    link = soup.find('a', class_='s-pagination-item s-pagination-next '
                     's-pagination-button s-pagination-separator')
    if link:
        return get_soup(f"{prefix}{link['href']}")
    return None


def get_review_page(URL: str) -> BeautifulSoup:
    """Return the review page of an amazon product page"""
    link = get_soup(URL.replace('dp', 'product-reviews', 1))
    return link


def get_next_review_page(soup: BeautifulSoup, prefix: str) -> BeautifulSoup:
    """Return the next review page of given URL review page"""
    navigation = soup.find('ul', class_='a-pagination')
    URL = navigation.find('a')
    if URL:
        print(f"{URL['href']}")
        return get_soup(f"{URL['href']}")
    print('No more reviews')
    return None


def get_last_three_words(s):
    """Helper function to get the date"""
    words = s.split()
    last_three_words = words[-3:]
    return ' '.join(last_three_words)


def parse_reviews(soup: BeautifulSoup) -> list:
    """Gather reviews for products"""
    review_section = soup.find('div', class_='a-section a-spacing-none '
                     'reviews-content a-size-base')
    reviews = review_section.find_all('div', attrs={'data-hook':'review'})

    if not reviews:
        print('No reviews')
        return None

    d_format = "%d %B %Y"
    review_info = []

    for review in reviews:
        date_sent = review.find('span', attrs={'data-hook':'review-date'}).text
        date = get_last_three_words(date_sent)
        r_date = datetime.strptime(date, d_format)
        r_body = review.find('span', 
                             attrs={'data-hook':'review-body'}).span.text
        title_block = review.find('a', attrs={'data-hook':'review-title'})
        r_title = title_block.find_all('span')[-1].text
        r_rating = float(title_block.find('span', 
                                          class_='a-icon-alt').text[:3])
        review_info.append([r_title, r_body, r_rating, r_date])
    return review_info


def getN_product_pages(soup: BeautifulSoup) -> int:
    """Get the number of product pages"""
    navigation = soup.find('div', 
                           attrs={'class':
                                  'a-section a-text-center '
                                  's-pagination-container', 
                                  'role':'navigation'})
    if navigation:
        return int(
            navigation.find('span', 
                            attrs={'class':'s-pagination-item '
                                   's-pagination-disabled',
                            'aria-disabled':'true'}).text.replace(',', '', 1))
    return 1


def getN_review_pages(soup: BeautifulSoup) -> int:
    """Get the number of review pages"""
    pages = soup.find('div', 
                      attrs={'data-hook':'cr-filter-info-review-rating-count',
                             'class':'a-row a-spacing-base a-size-base'})
    if pages:
        return (int(pages.text.strip().split(' ')[3].replace(',', '', 1)) 
                // 10 + 1)
    return 1


def scrape_products(URL: str) -> list:
    """Scrapes all products of a given URL 
    product page and writes them to an excel file"""
    soup = get_soup(URL)
    prefix = get_prefix(URL)
    products = parse_products(soup, prefix)
    Npages = getN_product_pages(soup)
    
    for _ in range(Npages):
        time.sleep(randint(1, 3))
        soup = get_next(soup, prefix)
        if not soup: # Incase, get_next fails
            break
        new_products = parse_products(soup, prefix)
        products.extend(new_products)

    data = pd.DataFrame(products, columns=['Title', 'Price', 'Rating', 'URL'])
    with pd.ExcelWriter('data.xlsx', engine='xlsxwriter') as xl_writer:
        data.to_excel(xl_writer, sheet_name='Amazon Product Info', 
                      index=False)


def scrape_reviews(URL: str) -> list:
    """Scrapes all reviews of a product given product
    page URL"""
    soup = get_review_page(URL)
    prefix = get_prefix(URL)
    if not soup:
        print('No reviews on this page')
        return

    reviews = []
    Npages = getN_review_pages(soup)

    for _ in range(Npages):
        time.sleep(randint(1, 5))
        new_reviews = parse_reviews(soup)
        soup = get_next_review_page(soup, prefix)
        print(len(new_reviews), f'Page no: {_}')
        reviews.extend(new_reviews)

    data = pd.DataFrame(reviews, columns=['Title', 
                                           'Body', 'Rating', 
                                           'Date'])

    with pd.ExcelWriter('review_data.xlsx', engine='xlsxwriter') as xl_writer:
        data.to_excel(xl_writer, sheet_name='Amazon Product Review Info', 
                      index=False)


if __name__ == '__main__':
    scrape_products(URL='https://www.amazon.com/s?k=oculus&i=electronics-intl-ship&pf_rd_i=23508887011&pf_rd_m=ATVPDKIKX0DER&pf_rd_p=434db2ed-6d53-4c59-b173-e8cd550a2e4f&pf_rd_r=MG3AXD9V0FGCM7KZ5N1W&pf_rd_s=merchandised-search-5&pf_rd_t=101&ref=nb_sb_noss')
    scrape_reviews(URL='')
