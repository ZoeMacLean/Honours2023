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
    input('Pretend to be human. Wait for the page to load. Press enter to continue')
    src_html = driver.page_source
    soup = BeautifulSoup(src_html, 'html.parser')
    return driver, soup


driver, mainpage = scraper(
    'https://queenslandlabor.org/category/people/state/')

div_of_interest = mainpage.find(
    'div', class_='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8')

for entry in div_of_interest.find_all('div', class_='bg-white shadow-2xl rounded-lg flex flex-col'):
    name = entry.find(
        'div', class_='text-2xl text-black font-bold mb-2').getText().strip()
    name = name.replace(' MLC', '').replace('Hon ', '')
    img_url = entry.find('img', class_='rounded-t-lg')
    img_url = img_url['src']
    img_name = 'alp-qld_' + name.replace(' ', '').replace('’', '')
    imgfile = open(os.path.join(imgpath, img_name + '.jpg'), 'wb')
    imgfile.write(urlopen(img_url).read())
    imgfile.close()
    bio = entry.find(
        'div', class_='mb-2 text-gray-500 text-sm').getText().strip()
    data.append({'name': name, 'image_url': img_url,
                'party': 'alp-qld', 'bio': bio})
    datatowrite = pd.DataFrame(data)
    datatowrite.to_csv(os.path.join(
        partypath, '12_pol-face-scraper_alp-qld.csv'), index=False)


print("Queensland Labour collected")
