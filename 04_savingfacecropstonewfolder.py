import pandas as pd
import os
from datetime import datetime
from PIL import Image

start_time = datetime.now()
print('Start time:', start_time)

basepath = os.path.dirname(os.path.realpath(__file__))
facepath_all = os.path.join(basepath, '02_facecrops')
facepath_inrange = os.path.join(basepath, '02_facecrops_inrange')

# Read in master df as dictionary to loop through
df = pd.read_csv(os.path.join(basepath, 'overall_all_cleaned_5.csv'), sep=',')
data = df.T.to_dict().values()

for entry in data:
    print('Searching for post:', entry['postid'])
    for sourcefile in os.listdir(facepath_all):
        if entry['postid'] in sourcefile:
            print('Saving face', sourcefile)
            img = Image.open(os.path.join(facepath_all, sourcefile))
            img.save(os.path.join(facepath_inrange, sourcefile))

end_time = datetime.now()
print('Duration: {}'.format(end_time - start_time))
