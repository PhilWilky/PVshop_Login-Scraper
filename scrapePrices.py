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

RED='\033[0;31m'
NC='\033[0m'


#context manager
with sync_playwright() as p:
    print("Spider initialized, and is crawling away!")
    #instantiate the browser
    # browser = p.chromium.launch(headless=False)
    # browser = p.webkit.launch(headless=False)
    browser = p.chromium.launch()
    #page object
    page = browser.new_page()
    page.route("/common/ImageWidthHeight*", lambda route: route.abort()) 


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
    total_rows = str(df.size / 2)
    
    results = open("results.csv", "w")
    results.write('code,expected,actual,status\n')
    for index, row in df.iterrows():

        url = page.locator("[placeholder=\"Type to search \\.\\.\\.\"]").fill(
            row['name'])
        page.locator("[placeholder=\"Type to search \\.\\.\\.\"]").press(
            "Enter")
        page.wait_for_load_state('domcontentloaded')
        html = page.content()
        soup = BeautifulSoup(html, 'lxml')


        try:
          price = soup.find_all('div', {'class': "productItemWide"})
 	  
        except:
            price = ''

 
        actual_price = '£0'
        for product in price:
            try:
               code = product.find('ul', {'class': 'introList'}).find('li').text
            except:
               code = ''

            expected_code = 'Code: ' + row['name']
            if code == expected_code:
               actual_price = product.find('span', {'class': "yourprice"}).text
               break
            else:
               continue

        expected_price = '£' + str(row['price'])


        results.write(row['name'] + ',' + str(row['price']) + ',' + actual_price[1:] + ',' + str( (actual_price == expected_price) ) + '\n')
        results.flush()

        if actual_price == expected_price:
           print(row['name'] + ' is correct at ' + actual_price + ' (' + str(index+1) + '/' + total_rows + ')')
        else:
           failed_load_screenshot = "failed_" + row['name'] + ".jpg"
           page.screenshot(path=failed_load_screenshot)
           print(RED + row['name'] + ' is incorrect at ' + actual_price + ' != ' + expected_price + NC + ' (' + str(index+1) + '/' + total_rows + ')')



    results.close()

