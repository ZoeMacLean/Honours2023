import pandas as pd
import os
from datetime import datetime

start_time = datetime.now()
print('Start time:', start_time)

basepath = os.path.dirname(os.path.realpath(__file__))

# Open the csv file with the text mentions
df1 = pd.read_csv(os.path.join(basepath, 'text_mentions_72k.csv'), sep=',')

# Open the file with the face matches
df2 = pd.read_csv(os.path.join(basepath, 'matches_and_emotions.csv'), sep=',')

# FILTER THE DATASET TO ONLY INCLUDE MATCHES ABOVE THE THRESHOLD!!
df2 = df2[df2['distance'] <= 0.47]

# Add party_mentioned and postid to the df

# turn df2 into a dictionary for looping. I know that's not the most
# efficient, but it works
data2 = df2.T.to_dict().values()
# Loop through and add new variables
# Also create the happy_binary conditional variable
for entry in data2:
    entry['postid'] = entry['filepath'].split('/')[-1].split('_')[0]
    party = entry['facematch'].split('_')[0].split('-')[0]
    if party == 'lib':
        party = 'coa'
    if party == 'nat':
        party = 'coa'
    entry['party_mentioned'] = party
    if entry['dominant_emotion'] == 'happy' and entry['emotion_score'] >= 0.98:
        entry['happy_bin'] = 1
    else:
        entry['happy_bin'] = 0

# turn the dictionary back into a dataframe
df2 = pd.DataFrame(data2)

# Then use mapping to add the ownership and nmo_title variables to the data

# First create a dictionary where the key is the posid
# and the value of the key is the thing I want to map
dict_ownership = {}
dict_nmo = {}
dict_valence = {}

# Then we turn df1 into a dictionary, loop through, and add the information to
# the empty dictionaries above

data1 = df1.T.to_dict().values()
for entry in data1:
    postid = entry['postid']
    dict_ownership[postid] = entry['ownership']
    dict_nmo[postid] = entry['title']
    dict_valence[postid] = entry['valence_overall']

# Now map these to the corresponding postids in our face data in df2
df2['ownership'] = df2['postid'].map(dict_ownership)
df2['nmo_title'] = df2['postid'].map(dict_nmo)
df2['valence'] = df2['postid'].map(dict_valence)


# And tidy up the final dataset so that we only have the information we're going to need
# first get an overview of the df to see what we want to keep and drop
print('\nDf2 Before tidy:\n')
print(df2.info())

# Then drop columns we don't need in our analysis
df2.drop(columns=['Unnamed: 0', 'filepath', 'facematch', 'facecropfile',
         'distance', 'distance-category'], inplace=True)


print('\nDf2 After tidy:\n')
print(df2.info())
# Then save df2 as a csv file ready to import into R for analysis
# Saving just to check wtf for now
df2.to_csv(os.path.join(basepath, 'emotions_faces.csv'), index=False, sep=',')

# Now I need to create the dataset that has the valence scores
# I'm going to start by filtering the face mentions down
# remove the duplicate mentions and mentions without valence

# Remove duplicated mentions from the face dataset. This is any rows with the
# same postid AND party_mentioned
df3 = df2.drop_duplicates(subset=['postid', 'party_mentioned'], keep='first')
print('\nDf3 Duplicates removed:\n')
print(df3.info())

# Now drop the 31 posts that don't have a valence score
df3 = df3.dropna(subset=['valence'])
print('\nDf3 Non-valence posts dropped:\n')
print(df3.info())

# Drop the columns that won't be used in the text analysis
df3.drop(columns=['dominant_emotion', 'emotion_score',
         'happy_bin'], inplace=True)
print('\nDf3 Columns dropped\n')
print(df3.info())

# Now add a column with the type_mentioned info
df3 = df3.assign(type_mention='img')
# print(df3.info())

# Now we need to get the type_mention = 'text' data into this df3
# Loop through data1 which holds the text_mentions_72k.csv data
# And on each loop, append the entry to a dictionary containing the df3 data
data3 = df3.T.to_dict().values()
# Convert dict_values to a list of dictionaries
data3_list = list(data3)

for entry in data1:
    if entry['alp_mention'] > 0:
        data3_list.append({
            'postid': entry['postid'],
            'party_mentioned': 'alp',
            'ownership': entry['ownership'],
            'nmo_title': entry['title'],
            'valence': entry['valence_overall'],
            'type_mention': 'text'
        })
    if entry['coa_mention'] > 0:
        data3_list.append({
            'postid': entry['postid'],
            'party_mentioned': 'coa',
            'ownership': entry['ownership'],
            'nmo_title': entry['title'],
            'valence': entry['valence_overall'],
            'type_mention': 'text'
        })
    if entry['gre_mention'] > 0:
        data3_list.append({
            'postid': entry['postid'],
            'party_mentioned': 'gre',
            'ownership': entry['ownership'],
            'nmo_title': entry['title'],
            'valence': entry['valence_overall'],
            'type_mention': 'text'
        })

# Then transform data3 back into df3 and check the result
df3 = pd.DataFrame(data3_list)
print('\nDf3 Complete:\n')
print(df3.info())
print('\nDf3 Tail:\n')
print(df3.tail(20))

# Once again, I need to delete duplicate mentions, each mention only needs to be in the dataset once
# Also, the type_mention column can be removed because deleting duplicates makes this column
# invalid for further analysis as you can't compare the two fairly
df3 = df3.drop_duplicates(
    subset=['postid', 'party_mentioned'], keep='first')

df4 = df3[df3['type_mention'] == 'text']
uniqie_postid_val4 = df4['postid'].nunique()
print('Unique postids, for text posts:', uniqie_postid_val4)

df5 = df3[df3['type_mention'] == 'img']
uniqie_postid_val5 = df5['postid'].nunique()
print('Unique postids, for image posts:', uniqie_postid_val5)

df3.drop(columns=['type_mention'], inplace=True)
print('\nDf3 Duplicates and type mentioned dropped:\n')
print(df3.info())

# And finally, print the number of unique postids for the valence dataset
uniqie_postid_val = df3['postid'].nunique()
print('Unique postids:', uniqie_postid_val)


# Lets save df3 to manually inspect again
df3.to_csv(os.path.join(basepath, 'text_valence.csv'),
           index=False, sep=',')


end_time = datetime.now()
print('Duration: {}'.format(end_time - start_time))
