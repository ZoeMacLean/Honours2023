import pandas as pd
import os
import re
from datetime import datetime

start_time = datetime.now()
print('Start time:', start_time)

basepath = os.path.dirname(os.path.realpath(__file__))
datapath = os.path.join(basepath, '03_openpostdata')
facepath = os.path.join(basepath, '02_facecrops')

# First, open a single file to have a base df to concatenate with
df = pd.read_csv(os.path.join(
    datapath, '9News_2022-05-24 13_01_37.788331.csv'), sep=',')

for subdir, dirs, files in os.walk(datapath):
    for file in files:
        if file != '9News_2022-05-24 13_01_37.788331.csv':
            df_temp = pd.read_csv(os.path.join(datapath, file), sep=',')
            df = pd.concat([df, df_temp])

# Save the giant df to work on without concatenating every time
data = pd.DataFrame(df)
data.to_csv(os.path.join(
    basepath, 'overall_all_dirty.csv'), index=False, sep=',')

# Get an overview of the data
print(df.info())

# Get unique values for one particular variable: the page name
print('\n# Number of unique values for page name:', len(df['page'].unique()))
print(df['page'].unique())

# There shouldn't be any duplicates based on how the scraper was written, but it doesn't hurt to check
# Print number of exact duplicates
print('\n# Exact duplicates:', df.duplicated().sum())

# Check for post id duplicates
# Print number of local duplicates in variable postid
print('\n# Post id duplicates:', df.duplicated(subset=['postid']).sum())
# Check for post id AND page name duplicates
print('\n# Post id and page duplicates:',
      df.duplicated(subset=['postid', 'page']).sum())

# Drop duplicate rows that have the same postid and page name
# Print the dataframe contents
print('\nDF before:', df.shape)
df = df.drop_duplicates(subset=['postid', 'page'])
# Print the dataframe contents
print('\nDF after:', df.shape)

# Now, we check the duplicated post ids again and manually search them in the
# csv file to see what's happening
# Print number of local duplicates in variable postid
print('\n# Post id duplicates:', df.duplicated(subset=['postid']).sum())
# Print rows with duplicates in variable post_text
print('\nRows with Post id duplicates:\n',
      df[df.duplicated(subset=['postid'])])

# Drop original and duplicate rows that have the same postid
print('\nDF before:', df.shape)
df = df.drop_duplicates(subset=['postid'], keep=False)
print('\nDF after:', df.shape)

# Lets check for post text duplicates, for interest (maybe duplicated between syndicated local papers)
# Print number of local duplicates in variable post_text
print('\n# Post text duplicates:', df.duplicated(subset=['post_text']).sum())
# If there are any, try to print the rows to inspect:
# Print rows with duplicates in variable post_text
print('\nRows with duplicates:\n', df[df.duplicated(subset=['post_text'])])

# Get summary of variables' missing data count
print('\n # Missing data:\n', df.isnull().sum())

# Count the number of unique page names in the subset of duplicated post text
df_dupe = df[df.duplicated(subset=['post_text'])]
print('\n# Number of unique values for page name:',
      len(df_dupe['page'].unique()))
print('\n\n\n')

# Create a new column that holds the date of the post,
# reformatted to fit conventions or marked for deletion


def date_reformat(timestamp, harvested):
    # one entry with Learn More instead of a timestamp
    if '2020' in timestamp or '2019' in timestamp or 'Learn' in timestamp:
        date = '30223022'
    elif 'April' in timestamp:
        day = re.search('^\d+', timestamp).group(0)
        day = str(day).zfill(2)
        date = '202204' + day
    elif 'May' in timestamp:
        day = re.search('^\d+', timestamp).group(0)
        day = int(day)
        if day <= 20:
            day = str(day).zfill(2)
            date = '202205' + day
        else:
            date = '30223022'
    elif 'h' in timestamp and '2022-05-21' in harvested:
        hours = re.search('^\d+', timestamp).group(0)
        hours = int(hours)
        timeofday = re.search('\s(\d+)', harvested).group(0).split(' ')[-1]
        timeofday = int(timeofday)
        if hours > timeofday:
            date = '20220520'
        else:
            date = '30223022'
    elif 'm' in timestamp and '2022-05-21 00:' in harvested:
        minutes = re.search('^\d+', timestamp).group(0)
        minutes = int(minutes)
        minofday = re.search(
            ' 00:\d+', harvested).group(0).split(' 00:')[-1]
        minofday = int(minofday)
        if minutes > timeofday:
            date = '20220520'
        else:
            date = '30223022'
    elif ' d' in timestamp and '2022-05-' in harvested:
        no_of_days = re.search('^\d+', timestamp).group(0)
        no_of_days = int(no_of_days)
        harv_day = re.search(
            '2022-05-(\d+)', harvested).group(0).split('05-')[-1]
        harv_day = int(harv_day)
        day = harv_day - no_of_days
        day = str(day).zfill(2)
        date = '202205' + day
    else:
        date = '30223022'
    return date


df['date_formatted'] = df.apply(lambda x: date_reformat(
    x['timestamp'], x['harvested']), axis=1)

# Get an overview of the data
print(df.info())
# Get overview of the first 20 values of a variable:
print(df['date_formatted'].head(20))
# Get overview of the last 20 values of a variable:
print(df['date_formatted'].tail(20))

# Subset the dataframe to exclude 30223022 date codes
# Subsetting rows with values for popularity higher than 80
df['date_formatted'] = df['date_formatted'].astype('int')
df_dates = df[df['date_formatted'] < 30223022]

# Get an overview of the data
print(df_dates.info())

Read in the original scrapelist file to join the information together.
df2 = pd.read_csv(os.path.join(basepath, 'scrapelist_full.csv'), sep=',')

# Get an overview of the columns for each df
print(df.info(), '\n')
print(df2.info(), '\n')

# Loop through each dataframe and match page to title
# Might have to convert df2 to a dictionary or create a list or something to loop through it properly

# Change df2 into a dictionary
data = df2.T.to_dict().values()

# Create a dictionary where the key is the condensed title and the value is the full title
dict_nmos = {}
dict_ownership = {}
dict_fburl = {}
dict_url = {}
dict_acmurl = {}
dict_notes = {}

for entry in data:
    title_condensed = entry['title'].replace(' ', '')
    title_condensed = title_condensed.replace('(', '')
    title_condensed = title_condensed.replace(')', '')
    title_condensed = title_condensed.replace('/', '')
    dict_nmos[title_condensed] = entry['title']
    dict_ownership[title_condensed] = entry['ownership structure']
    dict_fburl[title_condensed] = entry['updated facebook url']
    dict_url[title_condensed] = entry['url']
    dict_acmurl[title_condensed] = entry['ACMurl']
    dict_notes[title_condensed] = entry['Notes']


# print(dict_of_nmos)

# Map these regular titles to their condensed versions in the big dataset
df['title'] = df['page'].map(dict_nmos)
df['ownership'] = df['page'].map(dict_ownership)
df['fb_url'] = df['page'].map(dict_fburl)
df['web_url'] = df['page'].map(dict_url)
df['ACM_url'] = df['page'].map(dict_acmurl)
df['notes'] = df['page'].map(dict_notes)

print(df.info(), '\n')

# Get overview of the last 50 values of the two variables in question to check if it worked:
print(df[['page', 'title']].tail(50))
# Get overview of the last 50 values the improved dataset:
print(df.tail(50))

# Subset the data based on whether there's any file associated with the post
df_images = df[df['filesize'] > 0]
# setting new variable to 0 to add in the below nested for loop if faces are found
df_images['face_in_image'] = 0
df_images['politicians_faces'] = 0

# converting the df to a dict so I can loop through and assign number of faces
dict_images = df_images.T.to_dict().values()

# list_num_faces = []

for sourcefile in os.listdir(facepath):
    # First, find out the maximum number of faces in a post in my dataset
    # num_faces = sourcefile.split('_')[1].split('.')[0]
    # list_num_faces.append(num_faces)
    # print(max(list_num_faces))

    file_trunk = sourcefile.split('_')[0]
    print(file_trunk)

    # Now, pair face crops with the dataframe: how many faces per post?
    for entry in dict_images:
        if file_trunk in entry['postid']:
            entry['face_in_image'] += 1
            print(entry['face_in_image'])
            # Do something here to face match

# convert dictionary back to dataframe
df_images = pd.DataFrame(dict_images)

# Subset the data again based on a minimum of one face in the image for each post
df_faces = df_images[df_images['face_in_image'] > 0]

print(df.info())
print()
print(df_images.info())
print()
print(df_faces.info())
print()
print(df_faces['face_in_image'].describe())

# Now, we check the duplicated post ids again and manually search them in the
# csv file to see what's happening
# Print number of local duplicates in variable postid
print('\n# Post id duplicates:', df.duplicated(subset=['postid']).sum())
# Print rows with duplicates in variable post_text
print('\nRows with Post id duplicates:\n',
      df[df.duplicated(subset=['postid'])])
# Save rows with duplicated info into a csv file to double check all, not just top and tail

datacheck = df[df.duplicated(subset=['postid'])]
data = pd.DataFrame(datacheck)
data.to_csv(os.path.join(
    basepath, 'duplicated_post_ids.csv'), index=False, sep=',')

# Check for post id duplicates
# Print number of local duplicates in variable postid
print('\n# Post id duplicates:', df.duplicated(subset=['postid']).sum())
# Check for post id AND page name duplicates
print('\n# Post id and page duplicates:',
      df.duplicated(subset=['postid', 'page']).sum())


def categorisation(timestamp):
    if 'May' in timestamp or 'April' in timestamp:
        keep = 'yes'
    elif:

    else:
        covid_mention = 'no'
    return covid_mention


df['date_keep'] = df['timestamp'].apply(lambda x: categorisation(x))


# Drop duplicate rows that have the same postid and page name
# Print the dataframe contents
print('\nDF before:', df.shape)
df = df.drop_duplicates(subset=['postid', 'page'])
# Print the dataframe contents
print('\nDF after:', df.shape)

# Now, we check the duplicated post ids again and manually search them in the
# csv file to see what's happening
# Print number of local duplicates in variable postid
print('\n# Post id duplicates:', df.duplicated(subset=['postid']).sum())
# Print rows with duplicates in variable post_text
print('\nRows with Post id duplicates:\n',
      df[df.duplicated(subset=['postid'])])


# Lets check for post text duplicates, for interest (maybe duplicated between syndicated local papers)
# Print number of local duplicates in variable post_text
print('\n# Post text duplicates:', df.duplicated(subset=['post_text']).sum())
# If there are any, try to print the rows to inspect:
# Print rows with duplicates in variable post_text
print('\nRows with duplicates:\n', df[df.duplicated(subset=['post_text'])])

# Get summary of variables' missing data count
print('\n # Missing data:\n', df.isnull().sum())
# Print rows with missing data (add variable you want to inspect - here 'Song')
# isolatemissing = pd.isnull(df['Song'])
# print('\n Rows with missing data:\n',df[isolatemissing])

# Transform the timestamp variable
# Basically, if it's Anytime in April or up to May 27th I want to keep it
# Otherwise I want to drop it.
# The below works:


def categorisation(timestamp):
    to_ignore = ['h', 'ye', 'ju', '28 m', '29 m', '30 m', '31 m']
    time_cat = 0
    for i in to_ignore:
        if i in timestamp.lower():
            time_cat += 1
    return time_cat


df['time_cat'] = df['timestamp'].apply(lambda x: categorisation(x))

# Check the lambada worked with an overview of the data
print(df)
# Get overview of the first 20 values of a variable:
print(df.head(20))
# Get overview of the last 20 values of a variable:
print(df.tail(20))


def pagetitle(page):
    for entry in df2['title']:
        for i in [' ', '(', ')', '/']:
            title_condensed = entry.replace(i, '')
        if page == title_condensed:
            page_title = entry

    return page_title


df['page_title'] = df['page'].apply(lambda x: pagetitle(x))

print(df, '\n')


def get_concat_v(im1, im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst


# Create collages of matched images
datapath = os.path.join(basepath, '03_openpostdata')
facepath = os.path.join(basepath, '02_facecrops')
polliepath = os.path.join(basepath, '04_pollie_named_faces')
pmatchpath = os.path.join(basepath, '05_pic_matches')
fmatchpath = os.path.join(basepath, '06_face_matches')


# Subset the data based on whether there's any file associated with the post
df_images = df[df['filesize'] > 0]
# setting new variable to 0 to add in the below nested for loop if faces are found
df_images['face_in_image'] = 0
df_images['politicians_faces'] = 0

# converting the df to a dict so I can loop through and assign number of faces
dict_images = df_images.T.to_dict().values()

# list_num_faces = []

for sourcefile in os.listdir(facepath):
    # First, find out the maximum number of faces in a post in my dataset
    # num_faces = sourcefile.split('_')[1].split('.')[0]
    # list_num_faces.append(num_faces)
    # print(max(list_num_faces))

    file_trunk = sourcefile.split('_')[0]
    print(file_trunk)

    # Now, pair face crops with the dataframe: how many faces per post?
    for entry in dict_images:
        if file_trunk in entry['postid']:
            entry['face_in_image'] += 1
            print(entry['face_in_image'])
            # Do something here to face match
            for targetfile in os.listdir(polliepath):
                if '.DS+Store' not in targetfile:
                    targetfilef = os.path.join(polliepath, targetfile)
                    targetimg = face_recognition.load_image_file(
                        os.path.join(polliepath, targetfilef))
                    target_encoding = face_recognition.face_encodings(
                        targetimg)

                    if len(source_encoding) > 0 and len(target_encoding) > 0:

                        result = face_recognition.compare_faces(
                            [source_encoding[0]], target_encoding[0], tolerance=0.50)[0]

                        if result == True:
                            entry['politicians_faces'] += 1
                            print(sourcefile, targetfile)

                            im1 = Image.open(
                                os.path.join(facepath, sourcefile))
                            im2 = Image.open(os.path.join(
                                polliepath, targetfile))

                            get_concat_v(im1, im2).save(os.path.join(
                                fmatchpath, sourcefile.replace('.jpg', '') + '+' + targetfile))

                            sf = '_'.join(sourcefile.split('_')[:2])
                            tf = '_'.join(targetfile.split('_')[:2])
                            im1 = Image.open(
                                os.path.join(imgpath, sf + '.jpg'))
                            im2 = Image.open(
                                os.path.join(imgpath, tf + '.jpg'))

                            get_concat_v(im1, im2).save(os.path.join(
                                pmatchpath, sf + '_' + tf + '.jpg'))
            # if there's a match with a politician, then add 1 to new variable
            # entry['politicians_faces'] += 1

            # Add the politician's name/party to the dictionary
            # Check for emotion on pollies face/s
            # Add the emotion to the dictionary

# convert dictionary back to dataframe
df_images = pd.DataFrame(dict_images)

# Subset the data again based on a minimum of one face in the image for each post
df_faces = df_images[df_images['face_in_image'] > 0]

print(df.info())
print()
print(df_images.info())
print()
print(df_faces.info())
print()
print(df_faces['face_in_image'].describe())

# Save all the dataframes as new csv files
data = pd.DataFrame(df_images)
data.to_csv(os.path.join(
    basepath, 'overall_all_cleaned_4.csv'), index=False, sep=',')

data = pd.DataFrame(df_faces)
data.to_csv(os.path.join(
    basepath, 'overall_all_cleaned_5.csv'), index=False, sep=',')

# Making photo collages scrap code
# Now, save each category as it's own df then convert to dictionary for looping
df1 = df_poli_clean[df_poli_clean['distance-category'] == 1]
dict1 = df1.T.to_dict().values()
df2 = df_poli_clean[df_poli_clean['distance-category'] == 2]
dict1 = df1.T.to_dict().values()
df3 = df_poli_clean[df_poli_clean['distance-category'] == 3]
dict1 = df1.T.to_dict().values()
df4 = df_poli_clean[df_poli_clean['distance-category'] == 4]
dict1 = df1.T.to_dict().values()
df5 = df_poli_clean[df_poli_clean['distance-category'] == 5]
dict1 = df1.T.to_dict().values()
df6 = df_poli_clean[df_poli_clean['distance-category'] == 6]
dict1 = df1.T.to_dict().values()
df7 = df_poli_clean[df_poli_clean['distance-category'] == 7]

end_time = datetime.now()
print('Duration: {}'.format(end_time - start_time))
