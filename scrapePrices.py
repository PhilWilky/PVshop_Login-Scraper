from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from pathlib import Path
import pandas as pd
import os
import creds
from datetime import datetime

#TODO Figure out how to find the item if there is more than one result from search.
#TODO Time elapsed from start to finish might be handy.

cwd = Path.cwd()

#context manager
with sync_playwright() as p:
    print("Spider initialized, and is crawling away!")
    #instantiate the browser
    browser = p.chromium.launch()
    #page object
    page = browser.new_page()
    creds.domain

    #goto login page and login
    print(f'login into website' + ' as: ' + creds.user + ' on: ' +
          creds.domain)
    page.goto(creds.domain + 'login')
    page.fill('//*[@id="j_idt49"]/div/div[2]/label/input', creds.user)
    page.fill('//*[@id="j_idt49"]/div/div[3]/label/input', creds.password)
    page.click('//*[@id="j_idt49:loginButton"]')

    page.goto(creds.domain)

    print('Reading products list...')
    df = pd.read_csv(cwd / 'input_file.csv')

    items = list(df['name'])
    counter = 1

    print(len(items), 'product(s) found.')
    df.set_index('name', inplace=True)
    for item in items:
        ## Returns a datetime object containing the local date and time
        #dateTimeObj = datetime.now()
        ## get the time object from datetime object
        # timeObj = dateTimeObj.time()
        print(
            #f'{timeObj}- Extracting price for product {item} ({counter}/{len(items)})...'
            f'Extracting price for product {item} ({counter}/{len(items)})...'
        )
        url = page.locator("[placeholder=\"Type to search \\.\\.\\.\"]").fill(
            item)
        page.locator("[placeholder=\"Type to search \\.\\.\\.\"]").press(
            "Enter")
        page.wait_for_load_state('')
        page.wait_for_selector('.infoBlock')
        html = page.content()
        soup = BeautifulSoup(html, 'lxml')
        soup = BeautifulSoup(html, 'lxml')
        try:
            price = soup.find('span', {'class': "yourprice"}).text
        except:
            price = ''
        df.loc[item, 'Price'] = price
        print(price)
        counter += 1

    df.to_csv(cwd /'output_file.csv', encoding='utf-8-sig')
    print(
        'Extraction Completed and output file saved in the current directory.')
