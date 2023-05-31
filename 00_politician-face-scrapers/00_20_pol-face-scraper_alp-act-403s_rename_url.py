import os
import pandas as pd


basepath = os.path.dirname(os.path.realpath(__file__))
partypath = os.path.join(basepath, '01a_party-info')
folder = os.path.join(partypath, '403_alp-wa-faces')


data = pd.read_csv(os.path.join(
    partypath, '15_pol-face-scraper_alp-act.csv'), sep=',')
data = data.T.to_dict().values()


for entry in data:
    # entry['old_img_filename'] = entry['image_url'].split('/')[-1].split('?')[0]
    # Shit no, the WA faces were saved with a different file name somehow...
    # Okay, WA faces can be re-downloaded with the right files names, I just need to
    # loop through the csv file and split the URL on the ? and remove all the junk after.
    # This will work for alp-act as well and as a bonus, the file is bigger size and therefore better quality.

    entry['better_image_url'] = entry['image_url'].split('?')[0]
    datatowrite = pd.DataFrame(data)
    datatowrite.to_csv(os.path.join(
        partypath, '15_pol-face-scraper_alp-act.csv'), index=False)
