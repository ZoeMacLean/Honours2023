import pandas as pd
import face_recognition
import os
import time
from PIL import Image, ImageDraw
from datetime import datetime
import warnings
start_time = datetime.now()

# I get a warning about image transparency, ignore them for now:
warnings.filterwarnings('ignore', category=UserWarning, module='PIL.Image')

# This create an image collage of the two faces
def get_concat_v(im1, im2):
    if im1.width > im2.width:
        dst = Image.new('RGB', (im1.width, im1.height + im2.height))
        dst.paste(im1, (0, 0))
        dst.paste(im2, (0, im1.height))
    else:
        dst = Image.new('RGB', (im2.width, im1.height + im2.height))
        dst.paste(im1, (0, 0))
        dst.paste(im2, (0, im1.height))
    return dst

basepath = os.path.dirname(os.path.realpath(__file__))
imgpath = os.path.join(basepath, '01_images')
facepath = os.path.join(basepath, '02_facecrops')
pollpath = os.path.join(basepath, '04_pollie_named_faces')
pmatchpath = os.path.join(basepath, '05_pic_matches')
fmatchpath = os.path.join(basepath, '06_face_matches')

# Open cleanded csv file to only look at faces from my dataset
data = pd.read_csv(os.path.join(basepath, 'overall_all_cleaned_5.csv'), sep=',')
data['poll_face'] = 0
data = data.T.to_dict().values()

#Loop through df and for each post, get the faces and compare them to the politicians faces
for entry in data:
    print('Searching for post id:', entry['postid'])
    for sourcefile in os.listdir(facepath):
        if entry['postid'] in sourcefile:
            print('Faces found, searching for match...')
            sourcefilef = os.path.join(facepath, sourcefile)
            sourceimg = face_recognition.load_image_file(sourcefilef)
            source_encoding = face_recognition.face_encodings(sourceimg)

            for targetfile in os.listdir(pollpath):
                targetfilef = os.path.join(pollpath, targetfile)
                targetimg = face_recognition.load_image_file(os.path.join(pollpath, targetfilef))
                target_encoding = face_recognition.face_encodings(targetimg)

                if len(source_encoding)>0 and len(target_encoding)>0:

                    result = face_recognition.compare_faces([source_encoding[0]], target_encoding[0], tolerance=0.50)[0]

                    if result == True:
                        print('Found match:',sourcefile,targetfile)
                        entry['poll_face'] +=1

                        im1 = Image.open(os.path.join(facepath, sourcefile))
                        im2 = Image.open(os.path.join(pollpath, targetfile))

                        get_concat_v(im1, im2).save(os.path.join(fmatchpath, sourcefile.replace('.jpg','')+'+'+targetfile))

                        # Hashing out the below during the test, can add the images back with each other in full later

                        #sf = '_'.join(sourcefile.split('_')[:2])
                        #tf = '_'.join(targetfile.split('_')[:2])
                        #im1 = Image.open(os.path.join(imgpath, sf+'.jpg'))
                        #im2 = Image.open(os.path.join(pollpath, targetfile))

                        #get_concat_v(im1, im2).save(os.path.join(pmatchpath, sf+'_'+tf+'.jpg'))
    save = pd.DataFrame(data)
    save.to_csv(os.path.join(
        basepath, 'overall_all_cleaned_6.csv'), index=False, sep=',')

end_time = datetime.now()
print('Duration: {}'.format(end_time - start_time))
