import os
from PIL import Image, ImageDraw
import face_recognition
from datetime import datetime

basepath = os.path.dirname(os.path.realpath(__file__))
facepath = os.path.join(basepath, '04_clean-politician-faces')
croppath = os.path.join(basepath, '04_politician-facecrops')

start_time = datetime.now()
print('Start time:', start_time)

# Crop faces
for face in os.listdir(facepath):

    try:
        # Identify faces
        image = face_recognition.load_image_file(os.path.join(facepath,face))
        face_locations = face_recognition.face_locations(image)

        for n,face_location in enumerate(face_locations):
            top, right, bottom, left = face_location
            face_image = image[top:bottom, left:right]
            pil_image = Image.fromarray(face_image)
            width, height = pil_image.size

            if n ==0:
                pil_image = pil_image.save(os.path.join(croppath, face))
                print(face)
    except:
        print('Error for file:',face)


facefiles = set(os.listdir(facepath))
cropfiles = set(os.listdir(croppath))
missingfiles = facefiles - cropfiles
for item in missingfiles:
    print(item)





end_time = datetime.now()
print('Duration: {}'.format(end_time - start_time))
