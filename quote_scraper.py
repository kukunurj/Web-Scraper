# Author: Jai Reddy Kukunuru
# Program: Asynchronous Web Scraping

import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
import ssl
import certifi
import logging


# logging to monitor scraping process
logging.basicConfig(level=logging.INFO)


# asynchronous operations   
async def fetch(session, url):

    # creating ssl context
    # default settings configuration
    # certifi: verifying ssl certificates of servers 
    context = ssl.create_default_context(cafile=certifi.where())
    try:
        async with session.get(url, ssl=context) as response:
            return await response.text()
    except Exception as e:
        logging.error(f"Error fetching {url}: {e}")
        return None

# extracting data
def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    quotes = soup.find_all('div', class_='quote')
    data = []
    for quote in quotes:
        text = quote.find('span', class_='text').text
        author = quote.find('small', class_='author').text
        data.append({'text': text, 'author': author})

    # pagination: finding next page url
    next_page = soup.find('li', class_='next')
    if next_page:
        next_page_url = next_page.find('a')['href']
    else:
        next_page_url = None

    return data, next_page_url

async def main():
    base_url = 'https://quotes.toscrape.com'
    url = base_url
    all_data = []

    # asynchronous http session
    async with aiohttp.ClientSession() as session:
        while url:
            html = await fetch(session, url)
            if html:
                data, next_page = parse_html(html)
                all_data.extend(data)
                
                if next_page:
                    url = base_url + next_page
                else:
                    url = None

            await asyncio.sleep(1)  # delay between requests

    # save data to json
    with open('quotes.json', 'w') as file:
        json.dump(all_data, file, indent=4)

if __name__ == "__main__":
    asyncio.run(main())
