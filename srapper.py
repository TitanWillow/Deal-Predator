import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
import sqlite3
import re
import json

def contains(str, key):
    if (str.find(key) == -1):
        return False
    else :    
        return True
    
def clean_price(price_str):
    cleaned_price = re.sub(r'[^\d.]', '', price_str)
    if '.' in cleaned_price:
        return float(cleaned_price)
    else:
        return int(cleaned_price)
def get_asin(soup):
    detail_div = soup.find("div", id="detailBullets_feature_div")
    list_items = detail_div.find_all("li")
    asin = None
    for item in list_items:
        bold_text = item.find("span", class_="a-text-bold")
        if bold_text and "ASIN" in bold_text.text:
            asin = item.find_all("span")[-1].text.strip()
            break
    return asin

def selenium_way(product, map, price, params):
    PATH = 'chromedriver.exe'

    service = Service(executable_path=PATH)
    options = webdriver.ChromeOptions()

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(product)
    html_content = driver.page_source
    soup=BeautifulSoup(html_content,'html.parser')        
    soup_find(soup, map, price, params)
    driver.quit()

def soup_find(soup,map,price,params):
        print('in soup', price)
        try:
            if params['site'] == 'ajio' :
                params["product_id"] = soup.find('span',{'aria-label':'Product Code: '}).text.lstrip().rstrip().split(": ")[1]
            elif params['site'] == 'amazon':
                params["product_id"] = get_asin(soup)
            elif params['site'] == 'flipkart':
                params["products_id"] = soup.find(map['name']['external'],{map['name']['internal']:map['name']['value']}).text.lstrip().rstrip() + soup.find('div',{'id':'sellerName',}).find('span').find('span').text.lstrip().rstrip()
            else:
                params["product_id"] = soup.find(map['code']['external'],{map['code']['internal']:map['code']['value']}).text.lstrip().rstrip()
        except:
            params["product_id"]=''
        if params['products_id'] == None:
            raise Exception("Sorry, invalid listing") 
        try:
            params["title"]=soup.find(map['title']['external'],{map['title']['internal']:map['title']['value']}).text.lstrip().rstrip()
        except:
            params["title"]=''
        try:
            params["name"]=soup.find(map['name']['external'],{map['name']['internal']:map['name']['value']}).text.lstrip().rstrip()
        except:
            params["name"]=None
        try:
            if price is None:
                params["price"]=soup.find(map['price']['external'],{map['price']['internal']:map['price']['value']}).text.lstrip().rstrip() 
            else:
                params["price"] = price
            params['price'] = clean_price(params['price'])
        except:
            params["price"]=None
        params['site'] = map['site']
        print('in soup2', params)
        entry_to_db(params)

def soup_html_way(product,map,price,params):
    response = requests.get(product, headers=params['header'])
    soup = BeautifulSoup(response.content, 'html.parser')
    print('amz', price)
    soup_find(soup, map, price,params)

def entry_to_db(params):
    cprice = 0
    if params['classrank'] != 'master':
        params['cursor'].execute('SELECT min(price) FROM products where id = ?', (params['product_id'],))
        cprice = params['cursor'].fetchone()
        if cprice[0] is not None and cprice[0] > params['price']:
            params['classrank'] = 'min'
        else :
            params['classrank'] = 'default'
    else:
        params['classrank'] = 'default'
    params['cursor'].execute('''
        INSERT or replace INTO products (id, product_url, product_name, class, price, product_identifier, shopping_site)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (params['product_id'], params['url'], params['title'] + ' ' + params['name'], params['classrank'], params["price"], params['site']))
    params['conn'].commit()

def  entry_from_web(product,price,params):
    o={}
    if contains(product, 'myntra') :
        map = {'code' : {'external' : 'span', 'internal': 'class', 'value' : 'supplier-styleId'}, 'title' : {'external' : 'h1', 'internal': 'class', 'value' : 'pdp-title'}, 'name' : {'external' : 'h1', 'internal': 'class', 'value' : 'pdp-name'}, 'price' : {'external' : 'span', 'internal': 'class', 'value' : 'pdp-price'}, 'site' : 'myntra'}
        selenium_way(product,map,price, params)

    elif contains(product, 'amazon') :
        map = {'title' : {}, 'name' : {'external' : 'span', 'internal': 'id', 'value' : 'productTitle'}, 'price' : {'external' : 'span', 'internal': 'class', 'value' : 'a-price-whole'}, 'site' : 'amazon'} 
        soup_html_way(product, map, price, params)

    elif contains(product, 'ajio') :
        map = {'title' : {'external' : 'h2', 'internal' : 'class', 'value' : 'brand-name'}, 'name' : {'external' : 'h1', 'internal': 'class', 'value' : 'prod-name'}, 'price' : {'external' : 'div', 'internal': 'class', 'value' : 'prod-sp'}} 
        selenium_way(product,map)

    elif contains(product, 'flipkart') :
        map = {'title' : {'external' : 'span', 'internal': 'class', 'value' : 'mEh187'}, 'name' : {'external' : 'span', 'internal': 'class', 'value' : 'VU-ZEz'}, 'price' : {'external' : 'span', 'internal': 'class', 'value' : 'Nx9bqj CxhGGd'}, 'site' : 'flipkart'}
        selenium_way(product,map,price)

def get_product(urls, classrank, price):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8'
    }
    for product in urls :
        params = {'cursor' : cursor, 'header' : header, 'conn' : conn, 'url' : product, 'classrank' : classrank}
        entry_from_web(product, price, params)

    conn.close()