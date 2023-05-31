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
import urllib
import requests

chrome_options = Options()
chrome_options.add_argument('--disable-gpu')
chrome_options.page_load_strategy = 'eager'
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
chrome_options.add_argument('user-agent={0}'.format(user_agent))

basepath = os.path.dirname(os.path.realpath(__file__))
imgpath = os.path.join(basepath, '01b_named-faces')
partypath = os.path.join(basepath, '01a_party-info')

data = pd.read_csv(os.path.join(
    partypath, '09_pol-face-scraper_alp-nsw.csv'), sep=',')
data = data.T.to_dict().values()


def scraper(url):

    driver = webdriver.Chrome(
        basepath + '/chromedriver', chrome_options=chrome_options)
    wait = WebDriverWait(driver, 20)
    action = ActionChains(driver)
    driver.get(url)
    src_html = driver.page_source
    soup = BeautifulSoup(src_html, 'html.parser')
    return driver, soup


for entry in data:
    image_page = scraper(entry['image_url'])
    response = requests.get(image_page)
    if response.status_code == 200:
        with open(os.path.join(imgpath, img_name + '.jpg'), 'wb') as file:
            file.write(response.content)
            file.close()
    time.sleep(5)


# Still stuck... this isn't working

    img_url = entry['image_url']
    img_name = entry['name'].replace(' ', '_')
    with open(os.path.join(imgpath, img_name + '.jpg'), 'wb') as file:
        file.write(urllib.request.urlretrieve(img_url))
        #imgfile = open(os.path.join(imgpath, img_name + '.jpg'), 'wb')
        # imgfile.write(urllib.request.urlretrieve(img_url))
        imgfile.close()
    time.sleep(5)
    print(entry['name'], 'collected')

###
# Could run this script, manually save each image to the downloads, then rename
# the images based on the file names. It's a shitty option, but there's only
# 51 of these to do. Plus the two other states I suppose. Hmmm
