from google_api_functions import *
from data_cleaning_functions import * 

# Get the creds I stored in .venv/bin/activate
my_id = os.getenv('HINDI_SHEET_ID')
my_range = os.getenv('SHEET_RANGE')

# Load the vocab I already know, and the vocab I want to learn
data = read_google_sheet(my_id, my_range)

# Convert to pandas df
df = pd.DataFrame(data, columns=['learned', 'to_learn'])

# Do some cleaning to prepare for GPT request
df = unnest_learned_words(df)

# Export to manually validate
# df.to_csv('test.csv', index=False)

#print(df.describe())

# (display the column of 'words to learn' in the GUI, and possibly make it editable from the GUI?)

# Ask GPT to generate some new sentences


# GPT 3.5 doesn't do great at meeting the criteria. Call some functions to filter the GPT response
# to only include sentences that meet the n+1 criterion. Put those into a dataframe

# Call the audio-generating API

# Pack the Hindi, English, and Audio into a shared df 

# Call AnkiConnect to add the new cards to the existing Hindi deck https://foosoft.net/projects/anki-connect/

# Append the new cards to the Google Sheet in the 'vocab' column

# Load the tokens you need

