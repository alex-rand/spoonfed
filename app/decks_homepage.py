import tkinter as tk
from tkinter import ttk
import sqlite3
import pandas as pd
from anki_connect_functions import * 
from iplusone import IPlusOneFrame

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

        # Load and tokenize the two decks from Anki
        self.controller.learned_deck_tokens = self.load_vocab_from_deck('learned_deck', configuration_data)
        self.controller.new_deck_tokens = self.load_vocab_from_deck('new_deck', configuration_data)
        
        # Remove 'new' tokens that actually already occur in the learned tokens
        self.controller.new_deck_tokens = self.controller.new_deck_tokens[~self.controller.new_deck_tokens.isin(self.controller.learned_deck_tokens)]
        
        # Update the tables
        self.insert_vocab_into_treeview(self.learned_deck_treeview, self.controller.learned_deck_tokens)
        self.insert_vocab_into_treeview(self.new_deck_treeview, self.controller.new_deck_tokens)
        
    ### CREATE THE WINDOW and ELEMENTS
    def create_deck_display_frame(self):
        # Main frame for content
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        # Upper frame for treeviews and counts
        upper_frame = tk.Frame(main_frame)
        upper_frame.pack(fill="both", expand=True)

        # Lower frame for buttons
        lower_frame = tk.Frame(main_frame)
        lower_frame.pack(fill="x")

        # Frames for the tables
        self.learned_frame = tk.Frame(upper_frame)
        self.new_frame = tk.Frame(upper_frame)
        self.learned_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.new_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Create the Treeview widgets
        self.learned_deck_treeview = ttk.Treeview(self.learned_frame)
        self.new_deck_treeview = ttk.Treeview(self.new_frame)
        
        # Define columns for Treeview widgets
        self.learned_deck_treeview['columns'] = ("learned_vocab")
        self.new_deck_treeview['columns'] = ("new_vocab")
    
        # Configure column headings
        self.learned_deck_treeview.heading("#0", text="", anchor="w")
        self.learned_deck_treeview.heading("learned_vocab", text="Learned Vocabulary")
        self.new_deck_treeview.heading("#0", text="", anchor="w")
        self.new_deck_treeview.heading("new_vocab", text="New Vocabulary")
    
        # Configure column display
        self.learned_deck_treeview.column("#0", width=0, stretch="no")
        self.learned_deck_treeview.column("learned_vocab", anchor="center")
        self.new_deck_treeview.column("#0", width=0, stretch="no")
        self.new_deck_treeview.column("new_vocab", anchor="center")

        # Scrollbars for Treeviews
        learned_scrollbar = ttk.Scrollbar(self.learned_frame, orient="vertical", command=self.learned_deck_treeview.yview)
        new_scrollbar = ttk.Scrollbar(self.new_frame, orient="vertical", command=self.new_deck_treeview.yview)
        self.learned_deck_treeview.configure(yscrollcommand=learned_scrollbar.set)
        self.new_deck_treeview.configure(yscrollcommand=new_scrollbar.set)

        # Labels for item counts
        self.learned_count_label = tk.Label(self.learned_frame, text="Items: 0")
        self.new_count_label = tk.Label(self.new_frame, text="Items: 0")
        self.learned_count_label.pack(pady=(0, 10))
        self.new_count_label.pack(pady=(0, 10))

        # Buttons
        add_sentence_btn = tk.Button(lower_frame, text="Add Custom Sentence", command=self.add_custom_sentence)
        generate_iplus1_btn = tk.Button(lower_frame, text="Generate i+1", command=self.generate_iplus1)
        generate_sentences_btn = tk.Button(lower_frame, text="Generate Sentences for Selected Token", command=self.generate_sentences_for_selected_token)

        add_sentence_btn.pack(side="left", padx=10, pady=10)
        generate_iplus1_btn.pack(side="left", padx=10, pady=10)
        generate_sentences_btn.pack(side="left", padx=10, pady=10)

        # Packing the widgets
        learned_scrollbar.pack(side="right", fill="y")
        new_scrollbar.pack(side="right", fill="y")
        self.learned_deck_treeview.pack(side="left", fill="both", expand=True)
        self.new_deck_treeview.pack(side="left", fill="both", expand=True)
        
        # Bind Ctrl+C to copy function for Treeviews
        self.learned_deck_treeview.bind("<Command-c>", lambda e: self.copy_to_clipboard(e, self.learned_deck_treeview))
        self.new_deck_treeview.bind("<Command-c>", lambda e: self.copy_to_clipboard(e, self.new_deck_treeview))

            
    def update_learned_deck_count(self):
        # Count items in the learned deck Treeview
        count = len(self.learned_deck_treeview.get_children())
        self.learned_count_label.config(text=f"Items: {count}")

    def update_new_deck_count(self):
        # Count items in the new deck Treeview
        count = len(self.new_deck_treeview.get_children())
        self.new_count_label.config(text=f"Items: {count}")
        
    # Placeholder methods for button commands
    def add_custom_sentence(self):
        # Implement functionality here
        pass
    
    def generate_iplus1(self):
        # Move to the Language Configuration frame
        self.controller.show_frame(IPlusOneFrame)
    
    def generate_sentences_for_selected_token(self):
        # Implement functionality here
        pass
    
    def copy_to_clipboard(self, event, treeview):
        # Get the selected item in the Treeview
        selected_item = treeview.focus()
        if selected_item:
            # Extract the value from the selected item
            value = treeview.item(selected_item, "values")
            if value:
                # Copy the value to the clipboard
                self.clipboard_clear()
                self.clipboard_append(value[0])
    
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
    def load_vocab_from_deck(self, deck, raw_config_data):
        """
        Load vocabulary words from Anki cards based on specified deck, card types, and fields.

        Parameters:
        - deck (str): The name of the Anki deck.
        - card_types_and_fields (dict): A dictionary where keys are card types and values are lists of fields.

        Returns:
        - pd.Series: A series of unique vocabulary words.
        """
        
        # Extract deck and card_types_and_fields from raw_config_data
        deck = raw_config_data.get(deck, None)
        raw_card_types_and_fields = raw_config_data.get('card_types_and_fields', {})

        # Transform card_types_and_fields into the required format
        card_types_and_fields = {}
        for card_type, fields in raw_card_types_and_fields.items():
            # Split and clean the fields
            clean_fields = [field.strip() for field in fields[0].split(',')]
            card_types_and_fields[card_type] = clean_fields

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
                    note_content[col_name] = note_content[col_name].astype(str).apply(self.remove_non_devanagari)

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
    
    # This could be more general with conditional logic based on the 'language' field of the language configuration
    def remove_non_devanagari(self, text):
        pattern = "[^\u0900-\u097F \n]"
        return re.sub(pattern, '', text)
    
    def insert_vocab_into_treeview(self, treeview, vocab_tokens):
        # Clear existing content in the Treeview
        for item in treeview.get_children():
            treeview.delete(item)

        # Insert new vocab tokens
        for token in vocab_tokens:
            treeview.insert('', 'end', values=(token,))

        # Update the count labels
        self.update_learned_deck_count()
        self.update_new_deck_count()

