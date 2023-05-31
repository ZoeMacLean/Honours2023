from spacy import displacy
import spacy
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
import os
from datetime import datetime
import nltk
from datetime import datetime
start_time = datetime.now()
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()
NER = spacy.load("en_core_web_sm")

basepath = os.path.dirname(os.path.realpath(__file__))

df = pd.read_csv(os.path.join(basepath, 'overall_all_cleaned_3.csv'), sep=',')
data = df.T.to_dict().values()

for entry in data:
    try:
        score_dictionary = sia.polarity_scores(entry['post_text'])
        entry['valence_overall'] = score_dictionary['compound']
        entry['val_neg'] = score_dictionary['neg']
        entry['val_neu'] = score_dictionary['neu']
        entry['val_pos'] = score_dictionary['pos']
        print('Post text: \n', entry['post_text'],
              '\nValence scores:\n', score_dictionary)
        text = NER(entry['post_text'])
        organisations = []
        people = []
        places = []
        for word in text.ents:
            print(word.text, word.label_)
            if word.label_ == 'ORG':
                organisations.append(word.text)
            elif word.label_ == 'PERSON':
                people.append(word.text)
            elif word.label_ == 'GPE':
                places.append(word.text)
        entry['organisations'] = ' '.join(organisations)
        entry['people'] = ' '.join(people)
        entry['places'] = ' '.join(places)

    except:
        print('There was an error with the following text:\n',
              entry['post_text'])
        entry['valence_overall'] = ''
        entry['val_neg'] = ''
        entry['val_neu'] = ''
        entry['val_pos'] = ''

data = pd.DataFrame(data)
data.to_csv(os.path.join(basepath, '72k_valence-and-NER.csv'),
            index=False, sep=',')

end_time = datetime.now()
print('Duration: {}'.format(end_time - start_time))


# Sources to cite
# https://comp.social.gatech.edu/papers/icwsm14.vader.hutto.pdf
# This is the study that created the VADER resource

# https://www.geeksforgeeks.org/python-sentiment-analysis-using-vader/
# This geeks for geeks post helped explain how to use VADER

# https://www.nltk.org/howto/sentiment.html
# As did of course, the official documentation

# https://www.analyticsvidhya.com/blog/2021/06/nlp-application-named-entity-recognition-ner-in-python-with-spacy/
# This was to explain how NER worked

# May have to download the following packages via the terminal:
# The first one you have to do each time you open a new terminal to run this script. Not sure why
# python3 -m spacy download en_core_web_sm
# pip3 install nltk
# pip3 install spacy==2.3.5
# pip3 install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.3.1/en_core_web_sm-2.3.1.tar.gz
# pip3 install pyresparser
