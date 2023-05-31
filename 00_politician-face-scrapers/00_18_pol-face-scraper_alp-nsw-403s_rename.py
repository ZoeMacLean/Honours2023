import os
import pandas as pd


basepath = os.path.dirname(os.path.realpath(__file__))
partypath = os.path.join(basepath, '01a_party-info')
folder = os.path.join(partypath, '403_alp-nsw-faces')



data = pd.read_csv(os.path.join(
    partypath, '09_pol-face-scraper_alp-nsw.csv'), sep=',')
data = data.T.to_dict().values()



for entry in data:
    entry['old_img_filename'] = entry['image_url'].split('/')[-1]
    new_filename_extension = "." + entry['old_img_filename'].split('.')[-1]
    entry['new_img_filename'] = 'alp-nsw_' + entry['name'].replace(' ', '') + new_filename_extension


for image_file in os.listdir(folder):
    # construct the old file name
    old_filename = folder +"/"+ image_file

    # Loop through the csv file to find the politician that file belongs to and create the new file name
    for politician in data:
        if image_file == politician['old_img_filename']:
            new_filename = politician['new_img_filename']

    new_filename = folder +"/"+ new_filename

    # Now save the file with the new name in the new destination
    os.rename(old_filename, new_filename)
    print("File: " + new_filename + " saved to new destination")

### Notes ###
# Created this code with tutorial from http://pynative.com/python-rename-file
# Now I just need to manually move the files from one folder to the other
# And in the other two versions of this script I should be able to do that automatically too
# Now that I've figured out how to actually nme the files using folders.
