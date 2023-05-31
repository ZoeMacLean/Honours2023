import pandas as pd
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import random as rd
import re
from datetime import datetime
from urllib.request import Request, urlopen
import ssl
from PIL import Image, ImageDraw
import face_recognition
import cred

ssl._create_default_https_context = ssl._create_unverified_context

# Set Chrome options
chrome_options = Options()
chrome_options.page_load_strategy = 'eager'
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument("--enable-strict-powerful-feature-restrictions")
chrome_options.add_argument("--disable-notifications")

# Paths
basepath = os.path.dirname(os.path.realpath(__file__))
datapath = os.path.join(basepath, '00_postdata')
imgpath = os.path.join(basepath, '01_images')
croppath = os.path.join(basepath, '02_facecrops')

# Load data
todo = pd.read_csv(os.path.join(basepath, 'scrapelist.csv'),sep=',')
todo = todo.T.to_dict().values()

# Initiate driver + log in

driver = webdriver.Chrome(basepath+'/chromedriver',chrome_options=chrome_options)
driver.get('http://www.facebook.com')
time.sleep(1)

element = driver.find_element_by_name("email")
element.send_keys(cred.login)
time.sleep(1)

element = driver.find_element_by_name("pass")
element.send_keys(cred.password)
time.sleep(1)

element = driver.find_element_by_name("login")
element.click()
time.sleep(1)

# Set initial variables
datatotal = []
ids = []

# Start scraping
for num,item in enumerate(todo):

    try:

        # Set initial variables
        data = []
        starttime = datetime.now()

        # Wait in between runs
        if num != 0:
            timesleep = rd.randint(1000,1200)
            print('Time-out until next page:',timesleep,'sec')
            time.sleep(timesleep)

        # Get URL
        url = item['updated facebook url']
        if url[-1] == '/': url = url[:-1]

        print('\n',num+1,'out of',len(todo),url)

        driver.get(url)
        time.sleep(2)

        #################
        # Scrolling mechanism

        pixels = 0
        stop = 0
        counter = 0

        while stop == 0:

            # For testing purposes:S
            #counter += 1
            #if counter == 3: stop = 1

            #################
            # Scrolling mechanism

            count = 0
            countmax = rd.randint(500,750)
            while count <= countmax:
                travel = rd.randint(150,250)
                script = "window.scrollTo({},'{}')".format(pixels,pixels+travel)
                driver.execute_script(script)
                pixels += travel
                print('>> Scrolling to',pixels+travel,'px','-',count,'out of',countmax,end='\r')
                time.sleep(0.10*rd.randint(5,10))
                count += 1

            # Get source
            src_html = driver.page_source
            soup = BeautifulSoup(src_html, 'lxml')
            time.sleep(2)

            # Perform check
            if len(soup.find_all('div',class_='du4w35lb k4urcfbm l9j0dhe7 sjgh65i0')) == 0:

                print('Issue with page source...')

                # Scroll
                travel = rd.randint(150,250)
                script = "window.scrollTo({},'{}')".format(pixels,pixels+travel)
                driver.execute_script(script)
                pixels += travel
                print('>> Scrolling to',pixels+travel,'px','-',count,'out of',countmax,end='\r')

                # Get source
                src_html = driver.page_source
                soup = BeautifulSoup(src_html, 'lxml')
                time.sleep(2)

            # Scroll through posts
            for post in soup.find_all('div',class_='du4w35lb k4urcfbm l9j0dhe7 sjgh65i0'):

                #################
                # Get post date
                timestamp = ''

                ts = post.find('span',class_='t5a262vz nc684nl6 ihxqhq3m l94mrbxd aenfhxwr l9j0dhe7 sdhka5h4')

                if ts == None:
                    try:
                        timestamp = post.find('a',class_='oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw').getText()
                    except:
                        print(post)
                        input()

                else:

                    raw = []

                    for span in ts.find_all('span'):
                        span = str(span).replace(' ','')
                        if 'display:none;' not in span and 'absolute' not in span:
                            try: o = int(re.findall('order:(\d+)"',span)[0])
                            except: o = int(re.findall('order:(\d+);"',span)[0])
                            c = re.findall('>(.+)<',span)[0]
                            c = c.replace('\xa0',' ')
                            raw.append((o,c))

                    raw.sort()
                    for i in raw: timestamp = timestamp + str(i[1])

                #################
                # Get post text
                try: text = post.find('div',class_='kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x c1et5uql ii04i59q').getText()
                except: text = ''

                #################
                # Compose post id

                try:id = str(post).split('/posts/')[1].split('?')[0]
                except:

                    try: id = re.findall('\/photos\/a.+\/(\d+)\/\?',str(post))[0]
                    except: id = url.lower().split('/')[-1][:10] + re.sub(r'[^\w\s]', '', text.replace(' ','').lower())[:25]

                #################
                # Save data >>> When eligible

                if id not in ids:

                    if 'march' not in timestamp.lower() and 'february' not in timestamp.lower() and 'january' not in timestamp.lower() and '2021' not in timestamp.lower():

                        #################
                        # Get post photo link
                        try:
                            imgurl = post.find('div',class_='pmk7jnqg kr520xx4').find('img')['src']

                            # Cleaning
                            for c in [('%3A',':'),('%2F','/'),('%3F','_'),('%3D','?'),('%24','$'),('%25','%')]:
                                imgurl = imgurl.replace(c[0],c[1])

                            imgurl_raw = imgurl

                            try: imgurl = imgurl.split('&url=')[1].split('?')[0]
                            except: pass
                            try: imgurl = imgurl.split('&cfs=')[0]
                            except: pass

                            imgurl = imgurl.replace('_imwidth','')
                            imgurl = imgurl.replace('_resize','')

                        except:

                            try:
                                imgurl = post.find('div',class_='bp9cbjyn i09qtzwb rq0escxv j83agx80 n7fi1qx3 taijpn5t pmk7jnqg j9ispegn kr520xx4').find('img')['src']
                                imgurl_raw = imgurl
                                imgurl = imgurl.replace('&amp;','&')

                            except: imgurl = ''

                        size = 0

                        # Download photo
                        try:
                            if '.png' in imgurl: filename = id + '.png'
                            else: filename = id + '.jpg'

                            imgfile = open(os.path.join(imgpath,filename),'wb')
                            imgfile.write(urlopen(imgurl).read())
                            imgfile.close()

                            size = os.path.getsize(os.path.join(imgpath,filename))

                        except:
                            pass

                        # Crop faces
                        if size != 0:

                            try:
                                # Identify faces
                                image = face_recognition.load_image_file(os.path.join(imgpath,filename))
                                face_locations = face_recognition.face_locations(image)

                                for n,face_location in enumerate(face_locations):
                                    top, right, bottom, left = face_location
                                    face_image = image[top:bottom, left:right]
                                    pil_image = Image.fromarray(face_image)
                                    width, height = pil_image.size

                                    if width >= 50 or height >= 50: pil_image = pil_image.save(os.path.join(croppath, str(id)+'_'+str(n+1)+'.jpg'))
                            except:
                                print('Error in image processing')

                        title = item['title']
                        for i in [' ','(',')','/']: title = title.replace(i,'')

                        try: linktext = post.find('div',class_='bp9cbjyn cwj9ozl2 j83agx80 cbu4d94t ni8dbmo4 stjgntxs l9j0dhe7 k4urcfbm').getText()
                        except: linktext = ''

                        try: linkurl = linkurl = post.find('a',class_='oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 datstx6m k4urcfbm')['href']
                        except: linkurl = ''

                        entry = {
                        'harvested':datetime.now(),
                        'page':title,
                        'postid':id,
                        'timestamp':timestamp,
                        'post_text':text,
                        'linktext':linktext,
                        'linkurl':linkurl,
                        'imgurl_raw':imgurl_raw,
                        'imgurl':imgurl,
                        'filesize':size
                        }

                        datatotal.append(entry)
                        df = pd.DataFrame(datatotal)
                        df.to_pickle(os.path.join(basepath, 'overall.pkl'))

                        data.append(entry)
                        df = pd.DataFrame(data)
                        df.to_pickle(os.path.join(datapath, title+'_'+str(starttime)+'.pkl'))

                        #################
                        print(item['title'],'-',id,'-',timestamp,'-',text[:25],'-',size,'bytes')

                        ################# Add id (avoid duplicate entries)
                        ids.append(id)

                    else:
                        stop = 1

    except:

        print('QUIT UNEXPECTEDLY')
        waittime = rd.randint(3600,5400)
        print('Waiting for',waittime,'seconds')
        time.sleep(waittime)

        driver = webdriver.Chrome(basepath+'/chromedriver',chrome_options=chrome_options)
        driver.get('http://www.facebook.com')
        time.sleep(1)
        element = driver.find_element_by_name("email")
        element.send_keys(cred.login)
        time.sleep(1)
        element = driver.find_element_by_name("pass")
        element.send_keys(cred.password)
        time.sleep(1)
        element = driver.find_element_by_name("login")
        element.click()
        time.sleep(2)
