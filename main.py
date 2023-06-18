from google_api_functions import *
from openai_api_functions import * 
from data_cleaning_functions import * 

# Get the creds I stored in .venv/bin/activate
my_id = os.getenv('HINDI_SHEET_ID')
my_range = os.getenv('SHEET_RANGE')

# Load the vocab I already know, and the vocab I want to learn
data = pd.DataFrame(read_google_sheet(my_id, my_range), columns=['learned', 'to_learn'])

# Do some cleaning to prepare for GPT request
df = unnest_learned_words(df)

# (display the column of 'words to learn' in the GUI, and possibly make it editable from the GUI?)

# Ask GPT to generate some new sentences
gpt_payload = gpt__generate_new_sentences(df, 10)

print(gpt_payload)

# Export raw payload for debugging
with open("test-payload", 'w') as file:
    for item in gpt_payload:
        file.write(f"{item}\n")

# GPT 3.5 doesn't do great at meeting the criteria. Call some functions to filter the GPT response
# to only include sentences that meet the n+1 criterion. Put those into a dataframe
cleaned_response = evaluate_gpt_response(df, gpt_payload)

# Export cleaned payload for debugging
cleaned_response[0].to_csv('cleaned-response.csv', index=False)
cleaned_response[1].to_csv('response-diagnostics.csv', index=False)
cleaned_response[2].to_csv('response-validated.csv', index=False)






# Call the audio-generating API

# Pack the Hindi, English, and Audio into a shared df 

# Call AnkiConnect to add the new cards to the existing Hindi deck https://foosoft.net/projects/anki-connect/

# Append the new cards to the Google Sheet in the 'vocab' column

