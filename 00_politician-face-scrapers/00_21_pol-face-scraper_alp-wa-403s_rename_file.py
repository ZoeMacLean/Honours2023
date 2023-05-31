import os
import pandas as pd


basepath = os.path.dirname(os.path.realpath(__file__))
partypath = os.path.join(basepath, '01a_party-info')
folder = os.path.join(partypath, '403_alp-wa-faces')


data = pd.read_csv(os.path.join(
    partypath, '13_pol-face-scraper_alp-wa.csv'), sep=',')
data = data.T.to_dict().values()


for entry in data:
    entry['old_img_filename'] = entry['better_image_url'].split('/')[-1]
    new_filename_extension = "." + entry['old_img_filename'].split('.')[-1]
    entry['new_img_filename'] = 'alp-wa_' + \
        entry['name'].replace(' ', '') + new_filename_extension


for image_file in os.listdir(folder):
    # construct the old file name
    old_filename = folder + "/" + image_file

    # Loop through the csv file to find the politician that file belongs to and create the new file name
    for politician in data:
        if image_file == politician['old_img_filename']:
            new_filename = politician['new_img_filename']

    new_filename = folder + "/" + new_filename

    # Now save the file with the new name in the new destination
    os.rename(old_filename, new_filename)
    print("File: " + new_filename + " saved to new destination")

### Notes ###
# Created this code with tutorial from http://pynative.com/python-rename-file
# Now I just need to manually move the files from one folder to the other
# Keeping the manual moving of images, it works and I've had enough of breaking the code
