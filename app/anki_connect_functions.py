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