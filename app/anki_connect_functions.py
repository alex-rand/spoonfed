import json
import urllib.request
import urllib.error
import pandas as pd
import re

def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

# Function to send requests to Ankiconnect
def ankiconnect_invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    try:
        response = json.load(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8765', requestJson)))
    except urllib.error.URLError as e:
        raise Exception("Failed to establish connection with Anki. Make sure you have Anki open on your desktop.") from e
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']


# def load_vocab_from_deck(deck, card_types_and_fields):
#     """
#     Load vocabulary words from Anki cards based on specified deck, card types, and fields.
#     
#     Parameters:
#     - deck (str): The name of the Anki deck.
#     - card_types_and_fields (dict): A dictionary where keys are card types and values are lists of fields.
#     
#     Returns:
#     - pd.Series: A series of unique vocabulary words.
#     """
#     
#     all_words = []
#     
#     for card_type, fields in card_types_and_fields.items():
#         # Construct the query for the card type
#         query = f'"deck:{deck}" "note:{card_type}"'
#         
#         # Retrieve note IDs for the card type
#         note_ids = ankiconnect_invoke('findNotes', query=query)
#         
#         # Retrieve note content for the card type
#         note_content = pd.json_normalize(ankiconnect_invoke('notesInfo', notes=note_ids))
#         
#         # Remove non-Devanagari text for all specified fields
#         for field in fields:
#             col_name = f"fields.{field}.value"
#             if col_name in note_content.columns:
#                 note_content[col_name] = note_content[col_name].astype(str).apply(remove_non_devanagari)
#         
#         # Extract words from all specified fields
#         for field in fields:
#             col_name = f"fields.{field}.value"
#             if col_name in note_content.columns:
#                 words = (note_content[col_name].str.split(expand=True)
#                          .stack()
#                          .reset_index(level=1, drop=True))
#                 all_words.append(words)
#     
#     # Combine all words and remove duplicates
#     combined = pd.concat(all_words, ignore_index=True).drop_duplicates(keep='first')
#     
#     return combined
#     
# def remove_non_devanagari(text):
#     pattern = "[^\u0900-\u097F \n]"
#     return re.sub(pattern, '', text)

def create_new_card(dat, gpt_model, audio_provider):
    
    # The AnkiConnect API needs a particular nestedd structure to create a new note, 
    # as documented under 'addNote' here: https://github.com/FooSoft/anki-connect 
    
    # Define the fields for the Anki card
    fields = {
        'Front': dat['sentence'],
        'Back': dat['translation'],
        'Definition': dat['audio']
    }

    # Structure the note according to AnkiConnect's requirements
    note = {
        'deckName': "देवनागरी::मैंने सीखा",
        'modelName': "Basic-10b04",
        'fields': fields,
        'tags': ["spoonfed", gpt_model, audio_provider]
    }
 
    # Call
    ankiconnect_invoke('addNote', note=note)

    
    
        
    
    
   
