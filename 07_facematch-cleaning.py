import pandas as pd
import os
from PIL import Image, ImageDraw
from datetime import datetime

start_time = datetime.now()
print('Start time:', start_time)

basepath = os.path.dirname(os.path.realpath(__file__))
newsimgpath = os.path.join(basepath, '01_images')
poliimgpath = os.path.join(basepath, '04_clean-politician-faces')
fmatchpath = os.path.join(basepath, '05_pic_matches')

# Read in csv file with the face matches
df = pd.read_csv(os.path.join(basepath, 'facematchdistances.csv'), sep=',')

# Get the info printed to the console
print('Full dataframe information')
print(df.info())
print()


# Subset the data to remove images where no face was found (even though it is an
# image of a face, quality and size sometimes meant that a face couldn't be found
# for matching purposes)
df_faces = df[df['facematch'] != 'no_persons_found']

# Print the updated df
print('No Persons Found removed dataframe information')
print(df_faces.info())
print()

# Subset the data removing faces that don't match any of the politicians
df_poli = df_faces[df_faces['facematch'] != 'unknown_person']
# And convert the distance variable into a numeric type
df_poli['distance'] = df_poli['distance'].astype(float)

# Print the updated df
print('Non politicians removed dataframe information')
print(df_poli.info())
print()

# Now create new variable that splits the filepath into the file name
df_poli['facecropfile'] = df_poli['filepath'].str.split('/').str[-1]

# Print overview of the new variable
print('Overview of file name variable')
print(df_poli['facecropfile'])
print()

# Sort and remove the duplicates, keeping only the closest match available
df_poli_clean = df_poli.sort_values('distance').drop_duplicates(
    subset='facecropfile', keep='first')

# Print the updated df
print('Duplicates removed, closest match kept')
print(df_poli_clean.info())
print()
print('Overview of match distance variable')
print(df_poli_clean['distance'].describe())
print()

# Now subset by distance increments to determine the best threshold to cut off


def categorisation(distance):
    if distance <= 0.45:
        category = 1
    elif 0.45 < distance <= 0.46:
        category = 2
    elif 0.46 < distance <= 0.47:
        category = 3
    elif 0.47 < distance <= 0.48:
        category = 4
    elif 0.48 < distance <= 0.49:
        category = 5
    elif 0.49 < distance <= 0.50:
        category = 6
    else:
        category = 7
    return category


df_poli_clean['distance-category'] = df_poli_clean['distance'].apply(
    lambda x: categorisation(x))

# Print the updated df
print('Categorisation applied')
print(df_poli_clean.info())
print()
print('Overview of match distance variable')
print(df_poli_clean['distance-category'].describe())
print()

counts = df_poli_clean.groupby('distance-category').size()
print(counts)

# Convert to dictionary for looping through
data = df_poli_clean.T.to_dict().values()

# Create a way to save the photocollages


def save_img_match(im1, im2):
    if im1.width > im2.width:
        dst = Image.new('RGB', (im1.width, im1.height + im2.height))
        dst.paste(im1, (0, 0))
        dst.paste(im2, (0, im1.height))
    else:
        dst = Image.new('RGB', (im2.width, im1.height + im2.height))
        dst.paste(im1, (0, 0))
        dst.paste(im2, (0, im1.height))
    return dst


# List to store error files
errorf = []

for entry in data:
    for i in range(1, 8):
        if entry['distance-category'] == i:
            fmatchfolder = os.path.join(fmatchpath, str(i))
            try:
                newsfile = entry['facecropfile'].split('_')[0] + '.jpg'
                newsfile_ind = entry['facecropfile'].split('.')[0]
                polifile = entry['facematch'] + '.jpg'
                im1 = Image.open(os.path.join(newsimgpath, newsfile))
                im2 = Image.open(os.path.join(poliimgpath, polifile))

                save_img_match(im1, im2).save(os.path.join(
                    fmatchfolder, newsfile_ind + '+' + polifile))
                print('Image saved:', newsfile_ind + '+' + polifile)
            except:
                try:
                    newsfile = entry['facecropfile'].split('_')[0] + '.jpeg'
                    newsfile_ind = entry['facecropfile'].split('.')[0]
                    polifile = entry['facematch'] + '.jpg'
                    im1 = Image.open(os.path.join(newsimgpath, newsfile))
                    im2 = Image.open(os.path.join(poliimgpath, polifile))

                    save_img_match(im1, im2).save(os.path.join(
                        fmatchfolder, newsfile_ind + '+' + polifile))
                    print('Image saved:', newsfile_ind + '+' + polifile)
                except:
                    try:
                        newsfile = entry['facecropfile'].split('_')[0] + '.png'
                        newsfile_ind = entry['facecropfile'].split('.')[0]
                        polifile = entry['facematch'] + '.jpg'
                        im1 = Image.open(os.path.join(newsimgpath, newsfile))
                        im2 = Image.open(os.path.join(poliimgpath, polifile))

                        save_img_match(im1, im2).save(os.path.join(
                            fmatchfolder, newsfile_ind + '+' + polifile))
                        print('Image saved:', newsfile_ind + '+' + polifile)
                    except:
                        errorf.append(entry['facecropfile'].split('_')[0])
                        print('Error for file:',
                              entry['facecropfile'].split('_')[0])


print()
print('All error files:')
for error in errorf:
    print(error)

end_time = datetime.now()
print('Duration: {}'.format(end_time - start_time))
