import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
import sqlite3
import uuid
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

def selenium_way(product, map, ismaster, price):
        driver.get(product)
        html_content = driver.page_source
        soup=BeautifulSoup(html_content,'html.parser')        
        soup_find(soup, map, ismaster, price)
        driver.quit()

def soup_find(soup,map,ismaster,price):
        params = {}
        print('in soup')
        if ismaster is True:
            params["class"] = 'master'
        else:
            params["class"] = 'default'
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
        print('in soup2', params)
        entry_to_db(params)

def soup_html_way(product,map,ismaster,price):
    response = requests.get(product, headers=header)
    soup = BeautifulSoup(response.content, 'html.parser')
    print('amz')
    soup_find(soup, map, ismaster, price)

def entry_to_db(params):
    product_id = str(uuid.uuid4())
    cursor.execute('''
        INSERT or replace INTO products (id, product_url, product_name, class, price, product_identifier, shopping_site)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (product_id, 'xxx', params['title'] + ' ' + params['name'], params['class'], params["price"], 'init test', 'myntra'))
    conn.commit()

#def products_create(product_url, price, email):

def  entry_from_web(product,ismaster,price):
    o={}

    if contains(product, 'myntra') :
        map = {'title' : {'external' : 'h1', 'internal': 'class', 'value' : 'pdp-title'}, 'name' : {'external' : 'h1', 'internal': 'class', 'value' : 'pdp-name'}, 'price' : {'external' : 'span', 'internal': 'class', 'value' : 'pdp-price'}}
        selenium_way(product,map,ismaster,price)

    elif contains(product, 'amazon') :
        map = {'title' : {}, 'name' : {'external' : 'span', 'internal': 'id', 'value' : 'productTitle'}, 'price' : {'external' : 'span', 'internal': 'class', 'value' : 'a-price-whole'}} 
        soup_html_way(product, map)

    elif contains(product, 'ajio') :
        response = requests.get(product, headers=header)
        soup = BeautifulSoup(response.content, 'html.parser')
        scripts = soup.find_all('script', type='application/ld+json')
        
        # Look for the script containing product details
        for script in scripts:
            data = json.loads(script.text)
                # Check if the JSON object is a product
            #print(data)
            if data.get('@type') == 'ProductGroup':
                print(data)
                product_id = str(uuid.uuid4())
                print('')
                try:
                    o["name"]=data['name']
                    print('here',o['name'])
                except:
                    o["name"]=None

                try:
                    if price is None:
                        o["price"]=data['offers']['price'] 
                    else:
                        o["price"] = price
                    print(o['price'])
                    o['price'] = clean_price(o['price'])
                except:
                    o["price"]=None
                print('here2')
                if ismaster is True:
                    o["class"] = 'master'
                else:
                    o["class"] = 'default'
                cursor.execute('''
                INSERT or replace INTO products (id, product_url, product_name, class, price, product_identifier, shopping_site)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (product_id, product, o['name'], o["class"], o["price"], 'init test3', 'ajio'))
        conn.commit()

    elif contains(product, 'flipkart') :
        map = {'title' : {'external' : 'span', 'internal': 'class', 'value' : 'mEh187'}, 'name' : {'external' : 'span', 'internal': 'class', 'value' : 'VU-ZEz'}, 'price' : {'external' : 'span', 'internal': 'class', 'value' : 'Nx9bqj CxhGGd'}}
        selenium_way(product,map,ismaster,price)

#fetch master data and urls from database
#urls = [#'https://www.myntra.com/formal-shoes/aldo/aldo-men-ferro-leather-formal-loafers/26706862/buy', 
        #'https://www.amazon.in/Nike-Downshifter-White-DK-Grey-Pure-Platinum/dp/B0B571DN9F?pd_rd_w=2ZjSF&content-id=amzn1.sym.fa0aca50-60f7-47ca-a90e-c40e2f4b46a9%3Aamzn1.symc.ca948091-a64d-450e-86d7-c161ca33337b&pf_rd_p=fa0aca50-60f7-47ca-a90e-c40e2f4b46a9&pf_rd_r=D6B252KAV3SKDPM51RZT&pd_rd_wg=3orFB&pd_rd_r=c7762b20-3238-43bf-b9da-e54c2e2e0741&pd_rd_i=B0B571DN9F&th=1&psc=1',
        #'https://www.ajio.com/adidas-men-ultraboost-light-low-top-running-shoes/p/469584431_blue',
        #'https://www.flipkart.com/asics-gel-contend-4b-running-shoes-men/p/itmacfd40d92e6bb?pid=SHOFT8Q4AGF2D7RE&lid=LSTSHOFT8Q4AGF2D7RERUMIVN&marketplace=FLIPKART&sattr[]=color&sattr[]=size&st=size&otracker=search'
#       ]

def get_product(urls, ismaster):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8'
    }
    PATH = 'chromedriver.exe'

    service = Service(executable_path=PATH)
    options = webdriver.ChromeOptions()

    driver = webdriver.Chrome(service=service, options=options)
    price = None
    for product in urls :
        entry_from_web(product, ismaster, price)

    conn.close()