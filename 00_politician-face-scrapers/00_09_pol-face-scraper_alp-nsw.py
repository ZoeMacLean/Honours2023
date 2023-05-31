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


driver, mainpage = scraper('https://www.nswlabor.org.au/state_mps')

div_of_interest = mainpage.find('div', class_='row justify-content-center')

for entry in div_of_interest.find_all('div', class_='item-content text-center'):
    ind_page_url = entry.find('a')
    ind_page_url = ind_page_url['href']
    ind_page_url = 'https://www.nswlabor.org.au/' + ind_page_url
    name = entry.find('h4').getText().strip()
    bio = entry.find('p').getText().strip()
    data.append({'name': name, 'bio': bio, 'party': 'alp-nsw',
                'ind_page_url': ind_page_url})
    datatowrite = pd.DataFrame(data)
    datatowrite.to_csv(os.path.join(
        partypath, '09_pol-face-scraper_alp-nsw.csv'), index=False)

for page in data:
    driver, single_page = scraper(page['ind_page_url'])
    div_of_interest = single_page.find('div', class_='col-md-12 pt-4')
    img_url = div_of_interest.find('img')
    img_url = img_url['src']
    img_url = img_url.split('?')[0]
    img_name = 'alp-nsw_' + page['name'].replace(' ', '')
    #imgfile = open(os.path.join(imgpath, img_name + '.jpg'), 'wb')
    #imgfile.write(urlopen(img_url, timeout=10).read())
    # imgfile.close()
    page['image_url'] = img_url
    datatowrite = pd.DataFrame(data)
    datatowrite.to_csv(os.path.join(
        partypath, '09_pol-face-scraper_alp-nsw.csv'), index=False)
    time.sleep(3)

print('NSW Labour collected')


###
# Note: the images can't be collected because I keep hitting a 403 error.
# Image urls have been saved into the csv file, will come back to collecting
# the actual images themselves later
