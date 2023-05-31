import os
import pandas as pd
from random import shuffle
from datetime import datetime
from PIL import Image, ImageDraw

start_time = datetime.now()
print('Start time:', start_time)

basepath = os.path.dirname(os.path.realpath(__file__))
fmatchpath = os.path.join(basepath, '05_pic_matches')
validationpath = os.path.join(basepath, '06_validation-checks')

# Read in csv file with the face matches and emotions
df = pd.read_csv(os.path.join(basepath, 'matches_and_emotions.csv'), sep=',')
# Convert to dictionary
data = df.T.to_dict().values()

def save_random_img(sourcefolder, destinationfolder):
    list_images = os.listdir(sourcefolder)
    shuffle(list_images)
    x = 0
    random_images = []
    while x < 100:
        image = list_images[x]
        newimagef = str(x+1).zfill(2)+'+'+list_images[x]
        random_images.append(newimagef)
        img = Image.open(os.path.join(sourcefolder, image))
        img.save(os.path.join(destinationfolder, newimagef))
        x += 1
    return random_images

check_data = []

# Loop through the 7 folders and save the random selection of images
# Then create a csv file p folder that can be used for manual checks
for i in range(1,8):
    sourcefolder = os.path.join(fmatchpath, str(i))
    destinationfolder = os.path.join(validationpath, str(i))
    os.makedirs(destinationfolder, exist_ok=True)
    random_images = save_random_img(sourcefolder, destinationfolder)
    for image in random_images:
        postid = image.split('+')[1]+'.jpg'
        for entry in data:
            if postid == entry['facecropfile']:
                entry['man_match_chk'] = ''
                entry['man_emo_chk'] = ''
                entry['img_collage'] = image
                check_data.append(entry)

                print('Entry saved:', entry)

                data2 = pd.DataFrame(check_data)
                data2.to_csv(os.path.join(
                    basepath, 'check_matches.csv'), index=False, sep=',')


end_time = datetime.now()
print('Duration: {}'.format(end_time - start_time))
