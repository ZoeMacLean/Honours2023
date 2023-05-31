import pandas as pd
import os

basepath = os.path.dirname(os.path.realpath(__file__))
datapath = os.path.join(basepath, 'Politician Face Scraper/01a_party-info')

politician_fullname = []
politician_lastname = []


def party_split(party):
    party = party.split('-')[0]
    if party == 'lib':
        keep = 'coa'
    elif party == 'nat':
        keep = 'coa'
    else:
        keep = party
    return keep


# Add official names from scraped list of politicians/photos Include last name only
for file in os.listdir(datapath):
    if '.csv' in file:
        df = pd.read_csv(os.path.join(datapath, file), sep=',')
        df['keep'] = df['party'].apply(lambda x: party_split(x))
        data = df.T.to_dict().values()
        for entry in data:
            lastname = entry['name'].split(' ')[-1]
            print(lastname)
            politician_fullname.append(
                {'keyword': entry['name'], 'party': entry['party'], 'keep': entry['keep']})
            politician_lastname.append(
                {'keyword': lastname, 'party': entry['party'], 'keep': entry['keep']})


# Add nicknames for the two party leaders: Scomo and Albo
nicknames = [{'keyword': 'Scomo', 'keep': 'coa'},
             {'keyword': 'Scotty', 'keep': 'coa'},
             {'keyword': 'Scotty from Marketing', 'keep': 'coa'},
             {'keyword': 'Albo', 'keep': 'alp'},
             {'keyword': 'Albanese', 'keep': 'alp'},
             {'keyword': 'Morrison', 'keep': 'coa'}
             ]

# Add nicknames to list
for dict in nicknames:
    politician_fullname.append(dict)

df1 = pd.DataFrame(politician_fullname)
#df2 = pd.DataFrame(politician_lastname)

# Check for duplicate full names. Then remove duplicates keeping the first instance
print('\n# Full name duplicates:', df1.duplicated(subset=['keyword']).sum())
df1 = df1.drop_duplicates(subset=['keyword'], keep='first')

# Check for duplicate surnames. Then remove all instances of duplicates
# print('\n# Surname duplicates:', df2.duplicated(subset=['keyword']).sum())
#df2 = df2.drop_duplicates(subset=['keyword'], keep=False)

# Combine the two dataframes and save as a csv file
#df3 = pd.concat([df1, df2], ignore_index=True)
df1.to_csv(os.path.join(basepath, 'pol_politician-names.csv'),
           index=False, sep=',')

# Surnames is problematic because of names like "Li" that get found in "Australia" and then become a false positive
# Therefore, include only full names, and Albo and Scomo's last name
