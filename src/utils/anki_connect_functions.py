import json
import urllib.request
import urllib.error
import sqlite3
import re
from PyQt5.QtWidgets import QMessageBox


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

def check_suspended_status(note_ids):
    # The request for 'areSuspended' requires a list of card IDs
    params = {
        'cards': note_ids
    }

    # Call ankiconnect_invoke with the 'areSuspended' action and the card IDs
    result = ankiconnect_invoke('areSuspended', **params)

    return result

def fetch_user_configuration(calling_frame, user_id, configuration_name):
        """
        Fetches the user's language learning configurations from the database.
        """
        conn = None
        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()

            # Fetch basic configuration details
            c.execute("""
                SELECT id, configuration_language, learned_deck, new_deck
                FROM language_configurations
                WHERE user_id=? AND configuration_name=?
            """, (user_id, configuration_name))
            config = c.fetchone()

            if config:
                config_id, config_language, learned_deck, new_deck = config

                # Fetch card types and fields
                c.execute("""
                    SELECT card_type_name, field_name
                    FROM card_types
                    JOIN card_fields ON card_types.card_type_id = card_fields.card_type_id
                    WHERE configuration_id=?
                """, (config_id,))
                cards_fields = c.fetchall()

                card_types_and_fields = {}
                for card_type, field in cards_fields:
                    if card_type not in card_types_and_fields:
                        card_types_and_fields[card_type] = []
                    card_types_and_fields[card_type].append(field)

                return {
                    'configuration_language': config_language,
                    'learned_deck': learned_deck,
                    'new_deck': new_deck,
                    'card_types_and_fields': card_types_and_fields
                }
            else:
                QMessageBox.warning(calling_frame, "Configuration Error", "No configuration found for the given user_id and configuration_name")
                return None

        except sqlite3.Error as e:
            QMessageBox.critical(calling_frame, "Database Error", f"Database error: {e}")
            return None
        finally:
            if conn:
                conn.close()
                
def remove_non_language_tokens(text, language):
        """
        Removes all characters not belonging to the specified language from the given text.

        Parameters:
        - text (str): The text to be filtered.
        - language (str): The language based on which the filtering is to be done.

        Returns:
        - str: The filtered text containing only characters of the specified language.
        """
        if language == 'Hindi':
            pattern = "[^\u0900-\u097F \n]"
        elif language == 'Arabic':
            pattern = "[^\u0600-\u06FF \n]"
        elif language == 'Mandarin':
            pattern = "[^\u4e00-\u9fff \n]"
        else:
            raise ValueError("Unsupported language")

        return re.sub(pattern, '', text)
    
def add_audio_flag(df):
    """
    Adds a 'no_audio' column to the dataframe. 
    This column is a boolean that indicates whether, for that row, 
    at least one existing text column contains the specific substring pattern '[sound:--othercharacters---.mp3]'.

    Args:
    df (pandas.DataFrame): The input dataframe.

    Returns:
    pandas.DataFrame: The dataframe with the 'no_audio' column added.
    """

    # Regular expression pattern to match the audio file string
    audio_pattern = re.compile(r'\[sound:[^\]]+\.mp3\]')

    # Function to check if a cell contains the specific substring pattern
    def contains_audio_string(x):
        if isinstance(x, str) and audio_pattern.search(x):
            return True
        return False

    # Apply the function across all text columns and check if any returns True
    df['no_audio'] = df.applymap(contains_audio_string).any(axis=1)
    
    # Inverting the boolean value as we need 'True' for 'no_audio'
    df['no_audio'] = ~df['no_audio']

    return df

def append_audio_file_to_notes(df, last_fields):
    
    success_count = 0
    error_list = []

    for index, row in df.iterrows():
        note_id = int(row['Note Id'])
        card_type = row['Card Type']
        audio_content = row['audio']

        if card_type in last_fields:
            field_to_update = last_fields[card_type]

            # Fetch current note content
            current_note_info = ankiconnect_invoke("notesInfo", notes=[note_id])
            current_field_content = current_note_info[0]['fields'][field_to_update]['value']

            # Append audio content to the current content
            updated_content = current_field_content + audio_content

            # Prepare note_details for update
            note_details = {
                "note": {
                    "id": note_id,
                    "fields": {
                        field_to_update: updated_content
                    }
                }
            }

            # Make the update call
            ankiconnect_invoke("updateNoteFields", **note_details)
            success_count += 1

    return {
        "success_count": success_count,
        "errors": error_list
    }
    
    