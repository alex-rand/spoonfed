from google_api_functions import *
from openai_api_functions import * 
from anki_connect_functions import * 
from data_cleaning_functions import * 

# Get the creds I stored in .venv/bin/activate
my_id = os.getenv('HINDI_SHEET_ID')
my_range = os.getenv('SHEET_RANGE')

# Load the anki cards from two decks:
#   - The deck with words or phrases I've learned or know 'known vocab'
#   - The deck with words or phrases I haven't learned yet (and aren't yet contextualized in a sentence) 'new vocab'
known_vocab = load_known_vocab()
new_vocab = load_new_vocab()

# Remove any words that found their way into new_vocab despite already being in known_vocab
new_vocab = new_vocab[~new_vocab.isin(known_vocab)]

# (display the column of 'words to learn' in the GUI, and possibly make it editable from the GUI?)

# Ask GPT to generate some new sentences
gpt_payload = gpt__generate_new_sentences(known_vocab, new_vocab, 10)

# # Export raw payload for debugging
# with open("test-payload", 'w') as file:
#     for item in gpt_payload:
#         file.write(f"{item}\n")
# 

# # GPT 3.5 doesn't do great at meeting the criteria. Call some functions to filter the GPT response
# # to only include sentences that meet the n+1 criterion. Put those into a dataframe
outputs = evaluate_gpt_response(known_vocab, new_vocab, gpt_payload)

outputs[0].to_csv('cleaned_response.csv', index=False)

# Should I call Anki and delete any cards that include a word i just learned/
# # Need to fix up the 'to learn' column so it still includes words that didn't 
# # get included in new sentences this round.
# 
# # Is the end-game that I'd like to be pulling everything directly from anki?
# # What would that look like, like new words would have to exist in their own deck?
# # I think that would be most convenient. 
# 
# # Export cleaned payload for debugging
# cleaned_response[0].to_csv('cleaned-response.csv', index=False)
# cleaned_response[1].to_csv('response-diagnostics.csv', index=False)
# cleaned_response[2].to_csv('response-validated.csv', index=False)






# Call the audio-generating API

# Pack the Hindi, English, and Audio into a shared df 

# Call AnkiConnect to add the new cards to the existing Hindi deck https://foosoft.net/projects/anki-connect/

# Append the new cards to the Google Sheet in the 'vocab' column

