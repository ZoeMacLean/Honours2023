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


driver, mainpage = scraper('https://www.nswnationals.org.au/state-team/')

div_of_interest = mainpage.find('div', class_='wf-container-main')

for image in div_of_interest.find_all('img', class_='vc_single_image-img attachment-full'):
    img_url = image['src']
    name = image['alt']
    if name == '':
        name = img_url.split('/')[-1].split('.')[0].split('-')[:2]
        name = ' '.join(name)
        name = name.title()
    img_name = 'nat-nsw_' + name.replace(' ', '')
    imgfile = open(os.path.join(imgpath, img_name + '.jpg'), 'wb')
    imgfile.write(urlopen(img_url).read())
    imgfile.close()
    ind_page_url = 'https://www.nswnationals.org.au/state-team/' + \
        name.replace(' ', '').lower()
    data.append({'name': name, 'image_url': img_url,
                'party': 'nat-nsw', 'ind_page_url': ind_page_url})
    datatowrite = pd.DataFrame(data)
    datatowrite.to_csv(os.path.join(
        partypath, '03_pol-face-scraper_nat-nsw.csv'), index=False)


print("NSW Nats collected")

# Note: the final MP, Scott Barrett, was collected as '1 2' so have to manually
# updated his name and page in the csv file
# Note: Dave Lyzell got 'circle' for his last name, have to manually fix
