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


driver, mainpage = scraper('https://greens.org.au/mps')


div_of_interest = mainpage.find('div', class_='row person-box-list')

for entry in div_of_interest.find_all('div', class_='col-12 col-sm-6 col-lg-4 person-box-list__item'):
    ind_page_url = entry.find('a')
    ind_page_url = ind_page_url['href']
    ind_page_url = 'https://greens.org.au' + ind_page_url
    name = entry.find('span', class_='person-box__name-link').getText().strip()
    bio = entry.find('span', class_='person-box__position').getText().strip()
    img_url = entry.find('a')
    img_url = img_url['data-bg']
    img_url = 'https://greens.org.au' + img_url
    img_name = 'gre-fed_' + name.replace(' ', '')
    imgfile = open(os.path.join(imgpath, img_name + '.jpg'), 'wb')
    imgfile.write(urlopen(img_url).read())
    imgfile.close()
    data.append({'name': name, 'bio': bio, 'image_url': img_url,
                'party': 'gre-fed', 'ind_page_url': ind_page_url})
    datatowrite = pd.DataFrame(data)
    datatowrite.to_csv(os.path.join(
        partypath, '06_pol-face-scraper_gre-fed.csv'), index=False)


print("Federal Greens collected")
