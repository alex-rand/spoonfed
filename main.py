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
# gpt_payload = gpt__generate_new_sentences(known_vocab, new_vocab, 10)

### SCRATCH ###

# # Export raw payload for debugging
# with open("test-payload", 'w') as file:
#     for item in gpt_payload:
#         file.write(f"{item}\n")
# 


# Save a test version so we don't spend money to debug
#with open('test-payload.txt', 'w') as f:
#    f.write(repr(gpt_payload))
import ast
# Open the file in read mode ('r')
with open('test-payload.txt', 'r') as f:
    # Read the entire file to a string
    test_payload = f.read()
gpt_payload = ast.literal_eval(test_payload)

### /END SCRATCH ###

# GPT 3.5 doesn't do great at meeting the criteria. Call some functions to count the number 
# of old, want-to-learn, and 'rogue' words in each sentence, so we can filter later.
gpt_payload_enhanced = evaluate_gpt_response(gpt_payload, known_vocab, new_vocab)

# Filter out sentences that don't meet the N+1 rule, or any other rule you might prefer
output_sentences = flag_bad_sentences(gpt_payload_enhanced, "n+1 with rogue")

# Output for scratch diagnostics
output_sentences.to_csv('cleaned_response.csv', index=False)

# Should I now call Anki and delete any cards in the 'to learn' deck that are included a word that I just generated and that meets criteria?

# Write the output to a SQLite database?

# Call the audio-generating API

# Pack the Hindi, English, and Audio into a shared df 

# Call AnkiConnect to add the new cards to the existing Hindi deck https://foosoft.net/projects/anki-connect/
# Be sure to use an existing card format I've cleaned in the load_known_vocab() function


# Tokenize the new sentenes and  