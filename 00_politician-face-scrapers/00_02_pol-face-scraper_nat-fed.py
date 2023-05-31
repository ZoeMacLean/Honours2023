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


driver, mainpage = scraper('https://nationals.org.au/our-team/')

div_of_interest = mainpage.find('div', class_='content')

for entry in div_of_interest.find_all('div', class_='wpb_column vc_column_container vc_col-sm-6 vc_col-lg-3 vc_col-md-6'):
    print(entry)
    bio = entry.find(
        'div', class_='ifb-flip-box-section-content ult-responsive')
    bio = bio.find('p').getText().strip()
    ind_page_url = entry.find('div', class_='flip_link')
    ind_page_url = ind_page_url.find('a')
    ind_page_url = ind_page_url['href']
    print(bio, ind_page_url)
    data.append({'bio': bio, 'party': 'nat-fed', 'ind_page_url': ind_page_url})
    datatowrite = pd.DataFrame(data)
    datatowrite.to_csv(os.path.join(
        partypath, '02_pol-face-scraper_nat-fed.csv'), index=False)

for page in data:
    driver, single_page = scraper(page['ind_page_url'])
    div_of_interest = single_page.find(
        'a', class_='dt-btn dt-btn-m dt-btn-submit')
    name = div_of_interest.find('span').getText().strip()
    name = name.replace('Hear more from ', '')
    list_of_img_divs = []
    # images are inconsistent across pages, so can't rely on an index
    for image in single_page.find_all('img', class_='vc_single_image-img attachment-full'):
        list_of_img_divs.append(image['src'])
        for imgdiv in list_of_img_divs:
            if 'Headshot' in imgdiv:
                img_url = imgdiv
                img_name = 'nat-fed_' + name.replace(' ', '')
                imgfile = open(os.path.join(imgpath, img_name + '.jpg'), 'wb')
                imgfile.write(urlopen(img_url).read())
                imgfile.close()
                page['image_url'] = img_url
            else:
                pass
    page['name'] = name
    print(page)
    datatowrite = pd.DataFrame(data)
    datatowrite.to_csv(os.path.join(
        partypath, '02_pol-face-scraper_nat-fed.csv'), index=False)
    time.sleep(3)

print('Federal Nationals collected')
