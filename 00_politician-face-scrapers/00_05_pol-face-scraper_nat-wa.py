import os
import pandas as pd
from bs4 import BeautifulSoup
import time
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.request import Request, urlopen

chrome_options = Options()
chrome_options.add_argument('--disable-gpu')
chrome_options.page_load_strategy = 'eager'
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36'
chrome_options.add_argument('user-agent={0}'.format(user_agent))

basepath = os.path.dirname(os.path.realpath(__file__))
imgpath = os.path.join(basepath, '01b_named-faces')
partypath = os.path.join(basepath, '01a_party-info')


data = []


def scraper(url):

    driver = webdriver.Chrome(
        basepath + '/chromedriver', chrome_options=chrome_options)
    wait = WebDriverWait(driver, 20)
    action = ActionChains(driver)
    driver.get(url)
    src_html = driver.page_source
    soup = BeautifulSoup(src_html, 'html.parser')
    return driver, soup


driver, mainpage = scraper('https://www.nationalswa.com/our-team/')

# Three divs of interest (doi), loop through:

for doi in mainpage.find_all('div', class_='vc_row wpb_row vc_row-fluid waTeamRow vc_row-no-padding vc_row-o-equal-height vc_row-flex'):
    for entry in doi.find_all('div', class_='wpb_column vc_column_container vc_col-sm-3'):
        img_url = entry.find('img')
        img_url = img_url['src']
        name = entry.find('h3').getText().strip()
        ind_page_url = entry.find('h2')
        ind_page_url = ind_page_url.find('a')
        ind_page_url = ind_page_url['href']
        bio = entry.find('h2').getText().strip()
        img_name = 'nat-wa_' + name.replace(' ', '')
        imgfile = open(os.path.join(imgpath, img_name + '.jpg'), 'wb')
        imgfile.write(urlopen(img_url).read())
        imgfile.close()
        data.append({'name': name, 'bio': bio, 'image_url': img_url,
                    'party': 'nat-wa', 'ind_page_url': ind_page_url})
        datatowrite = pd.DataFrame(data)
        datatowrite.to_csv(os.path.join(
            partypath, '05_pol-face-scraper_nat-wa.csv'), index=False)
    for entry2 in doi.find_all('div', class_='wpb_column vc_column_container vc_col-sm-3 vc_col-has-fill'):
        img_url = entry2.find('img')
        img_url = img_url['src']
        name = entry2.find('h2').getText().strip()
        ind_page_url = entry2.find('h2')
        ind_page_url = ind_page_url.find('a')
        ind_page_url = ind_page_url['href']
        try:
            bio = entry2.find('h3').getText().strip()
            bio = bio.replace(';', '')
        except:
            bio = ''
        img_name = 'nat-wa_' + name.replace(' ', '')
        imgfile = open(os.path.join(imgpath, img_name + '.jpg'), 'wb')
        imgfile.write(urlopen(img_url).read())
        imgfile.close()
        data.append({'name': name, 'bio': bio, 'image_url': img_url,
                    'party': 'nat-wa', 'ind_page_url': ind_page_url})
        datatowrite = pd.DataFrame(data)
        datatowrite.to_csv(os.path.join(
            partypath, '05_pol-face-scraper_nat-wa.csv'), index=False)


print("WA Nats collected")

# Mia davies and Shane Love are on the page twice, duplicates to be manually
# deleted from CSV file (images should overwrite themselves)
