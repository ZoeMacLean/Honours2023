import pandas as pd
import os
import re
from datetime import datetime
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import nltk
from collections import Counter, OrderedDict
nltk.download('stopwords')
nltk.download('punkt')
set(stopwords.words('english'))

start_time = datetime.now()
print('Start time:', start_time)

basepath = os.path.dirname(os.path.realpath(__file__))
#facematchpath = os.path.join(basepath, '05_pic_matches')
#datapath = os.path.join(basepath, 'Politician Face Scraper/01a_party-info')

# first, open the 72k file as a df and convert to dict?
df = pd.read_csv(os.path.join(basepath, '72k_valence-and-NER.csv'), sep=',')
df = df.assign(alp_mention=0)
df = df.assign(coa_mention=0)
df = df.assign(gre_mention=0)
data = df.T.to_dict().values()

# For each entry in the 72k, we need to do the word matching and create a new variable for
# each party mention. Variables over the size of 1 get counted as yes, 0 as no
# That way multiple mentions are only counted once
# BUT Martin said that the unit of analysis should be each mention, not each post
# that's going to be tricky to figure out because multiple mentions as picked up
# by the algorithm might not be multiple mentions in acutality
# e.g., text that says "Liberal Leader Scott Morrison" will get counted for
# liberal, scott morrison, morrison so three times, even though there's only really one mention
# I'm going to try it my way with each post and only counting mention as yes or no
# and ignorning multiple mentions in the one post

# So, for each entry in the 72k set we need to word match the text with the dictionaries
# set up lists with each of the party mentions (party names and mp names)
list_alp = []
list_coa = []
list_gre = []

# open the csv files to populate the lists
df2 = pd.read_csv(os.path.join(basepath, 'pol_party-names.csv'), sep=',')
df3 = pd.read_csv(os.path.join(basepath, 'pol_politician-names.csv'), sep=',')
df4 = pd.concat([df2, df3], ignore_index=True)
poldict = df4.T.to_dict().values()

for item in poldict:
    if item['keep'] == 'coa':
        list_coa.append(item['keyword'].lower())
    elif item['keep'] == 'alp':
        list_alp.append(item['keyword'].lower())
    elif item['keep'] == 'gre':
        list_gre.append(item['keyword'].lower())

print(list_alp)
print(list_coa)
print(list_gre)

# Now loop through the 72k dataset and match:
for entry in data:
    text = str(entry['post_text']).lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Remove more punctuation, these are missed by the automatic removal
    punct = ['“', '’', '”', '‘', '–', '—']
    for p in punct:
        text = text.replace(p, '')
    print('Raw text:', text)
    # Tokenise text (i.e., split up in list of words)
    text_tokens = word_tokenize(text)
    # Remove stopwords from the tokenised text
    wordlist = [word for word in text_tokens if not word in stopwords.words()]
    # Make the worlist back into a single string
    wordstring = ' '.join(wordlist)
    print('Wordstring:', wordstring)
    for keyword in list_alp:
        if keyword in wordstring:
            entry['alp_mention'] += 1
            print('ALP mention found:', keyword, '\n', entry['post_text'])
    for keyword in list_coa:
        if keyword in wordstring:
            entry['coa_mention'] += 1
            print('COA mention found:', keyword, '\n', entry['post_text'])
    for keyword in list_gre:
        if keyword in wordstring:
            entry['gre_mention'] += 1
            print('GRE mention found:', keyword, '\n', entry['post_text'])
    if entry['alp_mention'] == 0 and entry['coa_mention'] == 0 and entry['gre_mention'] == 0:
        print('No party mentions found in:/n', entry['post_text'])

df = pd.DataFrame(data)
print(df.info())

# Save the data to a csv file
df.to_csv(os.path.join(basepath, 'text_mentions_72k.csv'), index=False, sep=',')


end_time = datetime.now()
print('Duration: {}'.format(end_time - start_time))

# Using last names only might flag too many false positives
# maybe use last names of only the very top pollies (albo, scomo) same as nicknames
# And leave the rest as full names
# This is otherwise quite messy
# This script also takes ages to run, so need to watch out for that
# About 1hr 3 mins according to the log of the one I let finish
