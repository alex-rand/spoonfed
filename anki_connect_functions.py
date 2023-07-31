import json
import urllib.request
import urllib.error
import pandas as pd
import re

def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}


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


def load_known_vocab():
    
    ### Need to load and clean different note types separately. 
    ### I'll be using standardized Basic-10b04 from now on,
    ### but what follows is ad-hoc cleaning for older cards
    
    # Load the note content for the two note types
    note_ids_basic = ankiconnect_invoke('findNotes', query='''"deck:देवनागरी::मैंने सीखा" "note:Basic-10b04"''')
    note_ids_memrise = ankiconnect_invoke('findNotes', query='''"deck:देवनागरी::मैंने सीखा" "note:Memrise - ! Hindi Alphabet (Devanagri) (audio) ! - Hindi"''')
    note_content_basic = pd.json_normalize(ankiconnect_invoke('notesInfo', notes = note_ids_basic))
    note_content_memrise = pd.json_normalize(ankiconnect_invoke('notesInfo', notes = note_ids_memrise))

    # Remove non-Devanagari text for both sets of notes
    for col in note_content_basic.columns:
        note_content_basic[col] = note_content_basic[col].astype(str).apply(remove_non_devanagari)
        
    for col in note_content_memrise.columns:
        note_content_memrise[col] = note_content_memrise[col].astype(str).apply(remove_non_devanagari)
        
    # Unpack all hindi values words in the columns corresponding to 'front' and 'back' for each note type
    memrise_unique_words_1 = (note_content_memrise['fields.Hindi.value'].str.split(expand=True)
                        .stack()
                        .reset_index(level=1, drop=True))
    memrise_unique_words_2 = (note_content_memrise['fields.English.value'].str.split(expand=True)
                    .stack()
                    .reset_index(level=1, drop=True))
    
    basic_unique_words_1 = (note_content_basic['fields.Front.value'].str.split(expand=True)
                        .stack()
                        .reset_index(level=1, drop=True))
    basic_unique_words_2 = (note_content_basic['fields.Back.value'].str.split(expand=True)
                    .stack()
                    .reset_index(level=1, drop=True))
    
    # Combine all unique hindi words across the two note types
    combined = pd.concat([memrise_unique_words_1, memrise_unique_words_2, basic_unique_words_1, basic_unique_words_2], ignore_index=True)
    
    # Remove duplicates
    combined = combined.drop_duplicates(keep='first')
    
    return combined
    
def load_new_vocab():
    
    note_ids = ankiconnect_invoke('findNotes', query='''"deck:देवनागरी::मैं सीखना चाहता हूँ" "note:Basic-10b04"''')
    note_content = pd.json_normalize(ankiconnect_invoke('notesInfo', notes = note_ids))
    
    # Remove non-Devanagari text 
    for col in note_content.columns:
        note_content[col] = note_content[col].astype(str).apply(remove_non_devanagari)
        
    # Unpack all hindi values words in the columns corresponding to 'front' and 'back' 
    unique_words_1 = (note_content['fields.Front.value'].str.split(expand=True)
                        .stack()
                        .reset_index(level=1, drop=True))
    unique_words_2 = (note_content['fields.Back.value'].str.split(expand=True)
                    .stack()
                    .reset_index(level=1, drop=True))
    
    # Combine all unique hindi words across the two note types
    combined = pd.concat([unique_words_1, unique_words_2], ignore_index=True)

    # Remove duplicates
    combined = combined.drop_duplicates(keep='first')
    
    return(combined)
    
    
    
    
        
    
    
    


    # Remove duplicate words from the new 'learned' DataFrame
    learned_unique_words = learned_unique_words.drop_duplicates(subset=['learned_unique'], keep='first')
    note_content_basic.to_csv('basic-test.csv', index=False)
    note_content_memrise.to_csv('memrise-test.csv', index=False)
    
    # Extract the hindi content from all notes

def remove_non_devanagari(text):
    pattern = "[^\u0900-\u097F \n]"
    return re.sub(pattern, '', text)

   # return(note_content_basic)
   # note_content = 
    
#invoke('createDeck', deck='test1')
#result = invoke('deckNames')
#print('got list of decks: {}'.format(result))
 

# It's gonnaa be like:
# - # findCards() based on deck name
# {
#     "action": "findCards",
#     "version": 6,
#     "params": {
#         "query": "deck:current"
#     }
# }
# - # cardsInfo() on the cardIDs from the previous step?
 
# Then to write you use addNote()
 