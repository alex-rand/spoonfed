from google_api_functions import *

# Declare Google Sheets creds
my_id     = os.environ.get("HINDI_SHEET_ID")
my_range  = os.environ.get("SHEET_RANGE")  # This selects the entire column A in "Sheet1"

# Load the vocab I already know
data = read_google_sheet(my_id, my_range)

# Clean those cols
df = pd.DataFrame(data, columns=['learned', 'to_learn'])

# Remove leading and trailing whitespaces from the 'Name' column
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

print(df)

# (display the column of 'words to learn' in the GUI, and possibly make it editable from the GUI?)

# Call the GPT 3.5 API and ask it the following prompt. Get the hindi sentences and the English translations

# GPT 3.5 doesn't do great at meeting the criteria. Call some functions to filter the GPT response
# to only include sentences that meet the n+1 criterion. Put those into a dataframe

# Call the audio-generating API

# Pack the Hindi, English, and Audio into a shared df 

# Call AnkiConnect to add the new cards to the existing Hindi deck https://foosoft.net/projects/anki-connect/

# Append the new cards to the Google Sheet in the 'vocab' column

# Load the tokens you need
print()
print(df)