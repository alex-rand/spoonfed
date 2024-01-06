from PyQt5.QtWidgets import QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTreeWidget, QTreeWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
import sqlite3
import pandas as pd
from anki_connect_functions import *
from iplusone import IPlusOneFrameQt
import re

class DecksHomepageQt(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = parent
        self.create_deck_display_frame()
        
      # c.execute("SELECT id FROM users WHERE profile_name=?", (user_name,))
      # self.controller.selected_user_id = c.fetchone()[0]

    def showEvent(self, event):
        """Override the showEvent to fetch configuration when the frame is shown."""
        super().showEvent(event)
        configuration_data = self.fetch_user_configuration(self.controller.selected_user_id, self.controller.configuration_name)

        if configuration_data:
            self.controller.learned_deck_tokens = self.load_vocab_from_deck('learned_deck', configuration_data)
            self.controller.new_deck_tokens = self.load_vocab_from_deck('new_deck', configuration_data)
            
            # Remove 'new' tokens that actually already occur in the learned tokens
            self.controller.new_deck_tokens = self.controller.new_deck_tokens[~self.controller.new_deck_tokens.isin(self.controller.learned_deck_tokens)]
            
            # Update the tables
            self.insert_vocab_into_treeview(self.learned_deck_treeview, self.controller.learned_deck_tokens)
            self.insert_vocab_into_treeview(self.new_deck_treeview, self.controller.new_deck_tokens)

    def create_deck_display_frame(self):
        main_layout = QVBoxLayout(self)

        # Frames for the treeviews and counts
        upper_frame = QHBoxLayout()
        main_layout.addLayout(upper_frame)

        # Learned deck frame and treeview
        self.learned_frame = QFrame()
        self.learned_deck_treeview = QTreeWidget()
        self.learned_deck_treeview.setHeaderLabels(["Learned Vocabulary"])
        self.learned_deck_treeview.setColumnCount(1)

        learned_layout = QVBoxLayout(self.learned_frame)
        learned_layout.addWidget(self.learned_deck_treeview)

        # New deck frame and treeview
        self.new_frame = QFrame()
        self.new_deck_treeview = QTreeWidget()
        self.new_deck_treeview.setHeaderLabels(["New Vocabulary"])
        self.new_deck_treeview.setColumnCount(1)

        new_layout = QVBoxLayout(self.new_frame)
        new_layout.addWidget(self.new_deck_treeview)

        # Add frames to upper frame
        upper_frame.addWidget(self.learned_frame)
        upper_frame.addWidget(self.new_frame)

        # Labels for item counts
        self.learned_count_label = QLabel("Items: 0")
        self.new_count_label = QLabel("Items: 0")
        learned_layout.addWidget(self.learned_count_label)
        new_layout.addWidget(self.new_count_label)

        # Lower frame for buttons
        lower_frame = QHBoxLayout()
        main_layout.addLayout(lower_frame)

        # Buttons
        add_sentence_btn = QPushButton("Add Custom Sentence", self)
        generate_iplus1_btn = QPushButton("Generate i+1", self)
        generate_sentences_btn = QPushButton("Generate Sentences for Selected Token", self)

        add_sentence_btn.clicked.connect(self.add_custom_sentence)
        generate_iplus1_btn.clicked.connect(self.generate_iplus1)
        generate_sentences_btn.clicked.connect(self.generate_sentences_for_selected_token)

        lower_frame.addWidget(add_sentence_btn)
        lower_frame.addWidget(generate_iplus1_btn)
        lower_frame.addWidget(generate_sentences_btn)

    # Placeholder methods for button commands
    def add_custom_sentence(self):
        # Implement functionality here
        pass
    
    def generate_iplus1(self):
        # Assuming IPlusOneFrameQt is already converted
        self.controller.show_frame(IPlusOneFrameQt)

    def generate_sentences_for_selected_token(self):
        # Implement functionality here
        pass
    
    def insert_vocab_into_treeview(self, treeview, vocab_tokens):
        treeview.clear()

        for token in vocab_tokens:
            QTreeWidgetItem(treeview, [token])
        
        self.update_deck_counts()

    def update_deck_counts(self):
        self.learned_count_label.setText(f"Items: {self.learned_deck_treeview.topLevelItemCount()}")
        self.new_count_label.setText(f"Items: {self.new_deck_treeview.topLevelItemCount()}")
        
    def fetch_user_configuration(self, user_id, configuration_name):
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
                QMessageBox.warning(self, "Configuration Error", "No configuration found for the given user_id and configuration_name")
                return None

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Database error: {e}")
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
        configuration_language = raw_config_data.get('configuration_language', None)

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
                    note_content[col_name] = note_content[col_name].astype(str).apply(lambda text: self.remove_non_language_tokens(text, configuration_language))
                    pass
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

    def remove_non_language_tokens(self, text, language):
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
