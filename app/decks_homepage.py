import tkinter as tk
from tkinter import ttk
import sqlite3
from anki_connect_functions import * 

class DecksHomepage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_deck_display_frame()
    
    def tkraise(self, aboveThis=None):
        """Override the tkraise method to fetch configuration when the frame is shown."""
        super().tkraise(aboveThis)  # Call the original tkraise method

        # Fetch the configuration only if it has not been fetched yet and a user is selected
        configuration_data = self.fetch_user_configuration(self.controller.selected_user_id, self.controller.configuration_name)
        print(configuration_data)
        learned_deck_data = self.load_vocab_from_deck(configuration_data['learned_deck'], configuration_data['card_types_and_fields'])
        
    ### CREATE THE WINDOW and ELEMENTS
    def create_deck_display_frame(self):
        # Create two frames for the tables
        self.learned_frame = tk.Frame(self)
        self.new_frame = tk.Frame(self)
        self.learned_frame.pack(side="left", fill="both", expand=True)
        self.new_frame.pack(side="right", fill="both", expand=True)

        # Create the Treeview widgets
        self.learned_deck_treeview = ttk.Treeview(self.learned_frame)
        self.new_deck_treeview = ttk.Treeview(self.new_frame)

        # Scrollbars for Treeviews
        learned_scrollbar = ttk.Scrollbar(self.learned_frame, orient="vertical", command=self.learned_deck_treeview.yview)
        new_scrollbar = ttk.Scrollbar(self.new_frame, orient="vertical", command=self.new_deck_treeview.yview)
        self.learned_deck_treeview.configure(yscrollcommand=learned_scrollbar.set)
        self.new_deck_treeview.configure(yscrollcommand=new_scrollbar.set)

        # Packing the widgets
        learned_scrollbar.pack(side="right", fill="y")
        new_scrollbar.pack(side="right", fill="y")
        self.learned_deck_treeview.pack(side="left", fill="both", expand=True)
        self.new_deck_treeview.pack(side="left", fill="both", expand=True)
    
    ### LOAD THE DB FIELDS FOR THE SELECTED LANGUAGE CONFIGURATION
    def fetch_user_configuration(self, user_id, configuration_name):
        """
        Fetches the user's language learning configurations from the database based on user_id and configuration_name.

        :param user_id: ID of the user whose configurations are to be fetched.
        :param configuration_name: Name of the language configuration.
        :return: A dictionary containing the configuration details.
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

                # Fetch card types and fields for learned_deck and new_deck
                c.execute("""
                    SELECT card_type_name, field_name
                    FROM card_types
                    JOIN card_fields ON card_types.card_type_id = card_fields.card_type_id
                    WHERE configuration_id=?
                """, (config_id,))
                cards_fields = c.fetchall()

                # Transform cards and fields into the required format
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
                print("No configuration found for the given user_id and configuration_name")
                return None

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            if conn:
                conn.close()

    ### LOAD THE DATA VIA ANKICONNECT USING THE FIELDS RETRIEVED ABOVE
    def load_vocab_from_deck(self, deck, card_types_and_fields):
        """
        Load vocabulary words from Anki cards based on specified deck, card types, and fields.

        Parameters:
        - deck (str): The name of the Anki deck.
        - card_types_and_fields (dict): A dictionary where keys are card types and values are lists of fields.

        Returns:
        - pd.Series: A series of unique vocabulary words.
        """

        all_words = []

        for card_type, fields in card_types_and_fields.items():
            # Construct the query for the card type
            query = f'"deck:{deck}" "note:{card_type}"'

            # Retrieve note IDs for the card type
            note_ids = ankiconnect_invoke('findNotes', query=query)

            # Retrieve note content for the card type
            note_content = pd.json_normalize(ankiconnect_invoke('notesInfo', notes=note_ids))

            # Remove non-Devanagari text for all specified fields
            for field in fields:
                col_name = f"fields.{field}.value"
                if col_name in note_content.columns:
                    note_content[col_name] = note_content[col_name].astype(str).apply(remove_non_devanagari)

            # Extract words from all specified fields
            for field in fields:
                col_name = f"fields.{field}.value"
                if col_name in note_content.columns:
                    words = (note_content[col_name].str.split(expand=True)
                             .stack()
                             .reset_index(level=1, drop=True))
                    all_words.append(words)

        # Combine all words and remove duplicates
        combined = pd.concat(all_words, ignore_index=True).drop_duplicates(keep='first')

        return combined
#
#
#    # Additional code to populate the Treeview widgets in DecksHomepage
#    # Assuming 'self.learned_deck_treeview' and 'self.new_deck_treeview' are the Treeview widgets
#    for field in fields:
#        col_name = f"fields.{field}.value"
#        if col_name in note_content.columns:
#            # Insert each word into the appropriate Treeview
#            for word in note_content[col_name]:
#                self.learned_deck_treeview.insert('', 'end', text=word)
    
    
