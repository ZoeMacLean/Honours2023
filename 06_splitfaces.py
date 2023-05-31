import os
from PIL import Image, ImageDraw
from datetime import datetime
start_time = datetime.now()

basepath = os.path.dirname(os.path.realpath(__file__))
facepath_inrange = os.path.join(basepath, '02_facecrops_inrange')
facepath_inrange_split = os.path.join(basepath, '02_facecrops_inrange_split')

counter = 0
files = os.listdir(facepath_inrange)

while counter < len(files):
    batch_start = counter
    batch_end = counter + 5000
    print('Batch starts at:',batch_start, 'and ends at:', batch_end)
    batch_folder_name = f'{batch_start}-{batch_end}'
    os.mkdir(os.path.join(facepath_inrange_split, batch_folder_name))
    for i in range(counter, min(batch_end, len(files))):
        file_name = files[i]
        print(file_name)
        img = Image.open(os.path.join(facepath_inrange, file_name))
        img.save(os.path.join(facepath_inrange_split, batch_folder_name, file_name))

    counter +=5000

end_time = datetime.now()
print('Duration: {}'.format(end_time - start_time))


#####
# This is the command line to run the face matching using all available CPUs
# face_recognition --cpus -1 --show-distance true --tolerance 0.55 '/home/uqccour1_local/Desktop/Honours-Project/Project-Data/04_politician-facecrops' unknown_faces

# These were the politicians faces that weren't detected by the face_recognition module:
# WARNING: No faces found in /home/uqccour1_local/Desktop/Honours-Project/Project-Data/04_politician-facecrops/alp-nt_LaurenMoss.jpg. Ignoring file.
# WARNING: No faces found in /home/uqccour1_local/Desktop/Honours-Project/Project-Data/04_politician-facecrops/alp-wa_ChristineTonkin.jpg. Ignoring file.
# WARNING: No faces found in /home/uqccour1_local/Desktop/Honours-Project/Project-Data/04_politician-facecrops/alp-wa_AyorMakurChuot.jpg. Ignoring file.
# WARNING: No faces found in /home/uqccour1_local/Desktop/Honours-Project/Project-Data/04_politician-facecrops/alp-tas_JanieFinlay.jpg. Ignoring file.
# WARNING: No faces found in /home/uqccour1_local/Desktop/Honours-Project/Project-Data/04_politician-facecrops/alp-fed_MiltonDick.jpg. Ignoring file.
