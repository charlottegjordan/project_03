import argparse
import requests
from bs4 import BeautifulSoup
import json


def parse_itemssold(text):
    digits = ''
    rtn_number = 3
    if 'sold' in text:
        for char in text:
            if char in '1234567890':
                digits += char
        rtn_number = int(digits)
    return rtn_number


def parse_itemshipping(text):
    shipping_deets = ''
    if "Free Delivery" in text or "Free delivery" in text:
        return 0
    if "Freight" in text:
        return "Freight"

    shipping_deets = ''.join([char for char in text if char.isdigit()])

    if shipping_deets:  
        return int(shipping_deets)


def parse_itemprice(text):
    numbers = ''
    price_picker = 0
    if 'to' in text:
        price_picker = text.split(" to ")
        tbc = price_picker[0]
    else:
        tbc = text
    for char in tbc:
        if char.isdigit():
            numbers += char
    return int(numbers)


#get command line arguments
parser = argparse.ArgumentParser(description='Download information from ebay and convert to JSON.')
parser.add_argument('search_term')
args = parser.parse_args()
print('args.search_term=', args.search_term)



# build the url
for page_number in range(1, 11):
    url = "https://www.ebay.com/sch/i.html?_nkw=" 
    url += args.search_term 
    url += "&_sacat=0&_from=R40&_pgn="
    url += str(page_number)
    url += "&rt=nc"
    print('url=', url)

# download the html
r = requests.get(url)
status = r.status_code
print('status=', status)
html = r.text

# process the html
soup = BeautifulSoup(html, 'html.parser')
items = []
tags_items = soup.select('.s-item')
for tag_item in tags_items:

    name = None
    tags_name = tag_item.select('.s-item__title')
    for tag in tags_name:
        name = tag.text

    free_returns = False
    tags_freereturns = tag_item.select('.s-item__free-returns')
    for tag in tags_freereturns:
        free_returns = True
    
    items_sold = 0
    tags_itemssold = tag_item.select('.s-item__quantitySold')
    for tag in tags_itemssold:
        items_sold = parse_itemssold(tag.text)
        #items_sold = tag.text
    
    item_status = ''
    tags_status = tag_item.select('.s-item__subtitle')
    for tag in tags_status:
        item_status = tag.text

    item_shipping = ''
    tags_shipping = tag_item.select('.s-item__logisticsCost') + tag_item.select('.s-item__freeXDays')
    for tag in tags_shipping:
        item_shipping = parse_itemshipping(tag.text)
    
    item_price = 0
    tags_price = tag_item.select(".s-item__price")
    for tag in tags_price:
        item_price = parse_itemprice(tag.text)
    
    item = {
        'name': name,
        'free_returns': free_returns,
        'items_sold': items_sold,
        'status': item_status,
        'shipping': item_shipping,
        'price': item_price
    }
    if name and "Shop on eBay" not in name:
        items.append(item)
for item in items:
    print(item)


#open json file
filename = args.search_term+'.json'
with open(filename, 'w', encoding='ascii') as f:
    f.write(json.dumps(items))