import os
import pandas as pd
from datetime import datetime
from PIL import Image, ImageDraw
from random import shuffle

start_time = datetime.now()
print('Start time:', start_time)

basepath = os.path.dirname(os.path.realpath(__file__))
fmatchpath = os.path.join(basepath, '05_pic_matches')
validationpath = os.path.join(basepath, '06_validation-checks')
facecroppath = os.path.join(basepath, '02_facecrops_inrange')
facecropmatchpath = os.path.join(facecroppath, 'facecrop_matches')
emotioncheckpath = os.path.join(validationpath, 'emotion_check')

# Read in csv file with the face matches and emotions
df1 = pd.read_csv(os.path.join(basepath, 'matches_and_emotions.csv'), sep=',')

# Read in csv file with all the post information
df2 = pd.read_csv(os.path.join(basepath, 'overall_all_cleaned_5.csv'), sep=',')

# print the info about both df so I can create a new df easily
print(df1.info())
print(df2.info())

# First, subset the matches based on category 1-3 only
df1 = df1[df1['distance-category'] < 4]
print(df1.info())
# 5131 faces, 4934 emotion scores

# First, inspect the matched data: how many politicians per post?
data = df1.T.to_dict().values()

for entry in data:

    img = Image.open(os.path.join(facecroppath, entry['facecropfile']))
    img.save(os.path.join(facecropmatchpath, entry['facecropfile']))

    entry['postid'] = entry['facecropfile'].split('_')[0]
    entry['faceid'] = entry['facecropfile'].split('_')[-1].split('.')[0]
    entry['party'] = entry['facematch'].split('_')[0]
    entry['partyid'] = entry['party'].split('-')[0]
    if entry['partyid'] == 'alp':
        entry['partyid'] = 'Labour'
    elif entry['partyid'] == 'lib':
        entry['partyid'] = 'Coalition'
    elif entry['partyid'] == 'nat':
        entry['partyid'] = 'Coalition'
    elif entry['partyid'] == 'gre':
        entry['partyid'] = 'Greens'

df1 = pd.DataFrame(data)

for c in df1.columns.tolist():
    print('\n', len(df1[c].unique()), 'unique values in', c)
    print(df1[c].unique())

print('\n', df1['postid'].describe())
print('\n', df1['emotion_score'].describe())

# Save df1 as a new csv file and then random sample the emotions to get an idea of accuracy
df1.to_csv(os.path.join(basepath, 'matches_and_emotions_cat1-3.csv'),
           index=False, sep=',')

# Subset based on emotions 98 and above only:
df_98emo = df1[df1['emotion_score'] >= 0.98]
print('\n', df_98emo.info())
print('\n', df_98emo['emotion_score'].describe())
print('\n', df_98emo['dominant_emotion'].describe())

# Subset based on 98 and above, only happiness:
df_98hap = df_98emo[df_98emo['dominant_emotion'] == 'happy']
print('\n', df_98hap.info())


# Subset based on emotions 80 and above only:
df_80emo = df1[df1['emotion_score'] >= 0.80]
print('\n', df_80emo.info())
print('\n', df_80emo['emotion_score'].describe())
print('\n', df_80emo['dominant_emotion'].describe())

# Subset based on 80 and above, only happiness:
df_80hap = df_80emo[df_80emo['dominant_emotion'] == 'happy']
print('\n', df_80hap.info())

# Subset based on 80 and above, only happiness:
df_80ang = df_80emo[df_80emo['dominant_emotion'] == 'angry']
print('\n', df_80ang.info())

end_time = datetime.now()
print('\nDuration: {}'.format(end_time - start_time))
