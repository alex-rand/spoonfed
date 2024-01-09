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
    
    return("success")
