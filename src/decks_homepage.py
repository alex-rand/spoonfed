from PyQt5.QtWidgets import QComboBox, QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTreeWidget, QTreeWidgetItem, QMessageBox
import pandas as pd
from utils.anki_connect_functions import *
from iplusone import IPlusOneFrameQt
from previous_cards_audio_frame import PreviousCardsAudioFrameQt

class DecksHomepageQt(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = parent
        self.create_deck_display_frame()

    def showEvent(self, event):
        from language_config import LanguageConfigFrameQt
        
        """Override the showEvent to fetch configuration when the frame is shown."""
        super().showEvent(event)
        self.controller.resize(800, 400)
        
        configuration_data = fetch_user_configuration(self, self.controller.selected_user_id, self.controller.configuration_name)
        
        if configuration_data:
            self.controller.learned_deck_tokens = self.load_vocab_from_deck('learned_deck', configuration_data)
            if self.controller.learned_deck_tokens.isnull().all():
                return self.controller.show_frame(LanguageConfigFrameQt)
            self.controller.new_deck_tokens = self.load_vocab_from_deck('new_deck', configuration_data)
            
            # Remove 'new' tokens that actually already occur in the learned tokens
            self.controller.new_deck_tokens = self.controller.new_deck_tokens[~self.controller.new_deck_tokens.isin(self.controller.learned_deck_tokens)]
            
            # Update the tables
            self.insert_vocab_into_treeview(self.learned_deck_treeview, self.controller.learned_deck_tokens)
            self.insert_vocab_into_treeview(self.new_deck_treeview, self.controller.new_deck_tokens)

    def create_deck_display_frame(self):
        main_layout = QVBoxLayout(self)
        
        # Back button 
        top_layout = QHBoxLayout()
        self.back_button = QPushButton("Back", self)
        self.back_button.setFixedSize(100, 30)  # Example size, adjust as needed
        self.back_button.setStyleSheet("QPushButton { font-size: 10pt; }")  # Example style, adjust as needed
        self.back_button.clicked.connect(self.on_press_back)
        top_layout.addWidget(self.back_button)
        top_layout.addStretch()  # This will push the button to the left
        main_layout.addLayout(top_layout)

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

        # Create Dropdown Menu (Picklist)
        self.action_picklist = QComboBox(self)
        self.action_picklist.addItems([
            "'Verb Exploder'",
            "Generate Audio for Existing Cards",
            "Generate i+1",
            "Generate Sentences for Selected Token"
        ])
        lower_frame.addWidget(self.action_picklist)

        # Create a Single Button
        self.execute_action_button = QPushButton("Go", self)
        self.execute_action_button.clicked.connect(self.execute_selected_action)
        lower_frame.addWidget(self.execute_action_button)
        
    # Implement the method to handle button press
    def execute_selected_action(self):
        selected_action = self.action_picklist.currentText()
        if selected_action == "'Verb Exploder'":
            self.verb_exploder()
        elif selected_action == "Generate i+1":
            self.generate_iplus1()
        elif selected_action == "Generate Sentences for Selected Token":
            self.generate_sentences_for_selected_token()
        elif selected_action == "Generate Audio for Existing Cards":
            self.generate_audio_for_existing_cards()
        elif selected_action == "Add Custom Sentence":
            self.add_custom_sentence()

    def on_press_back(self):
        from language_config import LanguageConfigFrameQt
        self.controller.show_frame(LanguageConfigFrameQt)

    # Placeholder methods for button commands
    def add_custom_sentence(self):
        pass
    
        # Open a new, specific frame? Should I implement a superclass that the other specific generating frames inherit? 

        # Load all cards in the language configuration, subset to only include cards that don't include the [sound...mp3] string in any field

        # User can choose via checkboxes which sentences to do

        # Hard-assign the audio file to the final field of the card. This is potentially destructive!!
        
    def generate_iplus1(self):
        self.controller.show_frame(IPlusOneFrameQt)

    def generate_sentences_for_selected_token(self):
        pass
    
    def generate_audio_for_existing_cards(self):
        self.controller.show_frame(PreviousCardsAudioFrameQt)
    
    def verb_exploder(self):
        from verb_exploder_frame import VerbExploderFrameQt
        self.controller.show_frame(VerbExploderFrameQt)
    
    def insert_vocab_into_treeview(self, treeview, vocab_tokens):
        treeview.clear()

        for token in vocab_tokens:
            QTreeWidgetItem(treeview, [token])
        
        self.update_deck_counts()

    def update_deck_counts(self):
        self.learned_count_label.setText(f"Items: {self.learned_deck_treeview.topLevelItemCount()}")
        self.new_count_label.setText(f"Items: {self.new_deck_treeview.topLevelItemCount()}")

    ### Load the vocab data via ankiconnect using the selected language configuration. 
    def load_vocab_from_deck(self, deck, raw_config_data):
        
        """
        Use AnkiConnect to load vocabulary words from Anki cards based on specified deck, card types, and fields.

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
            note_ids = ankiconnect_invoke(self, 'findNotes', query=query)
            if note_ids == 1:
               print("YES")
               return None
           
            # Retrieve note content for the card type
            note_content = pd.json_normalize(ankiconnect_invoke(self, 'notesInfo', notes=note_ids))

            # Remove non-Devanagari text, HTML tags, and Anki Cloze notation for all specified fields
            for field in fields:
                col_name = f"fields.{field}.value"
                if col_name in note_content.columns:
                    note_content[col_name] = note_content[col_name].astype(str).apply(lambda text: strip_punctuation(text))
                    note_content[col_name] = note_content[col_name].astype(str).apply(lambda text: strip_html_and_cloze(text))
                    note_content[col_name] = note_content[col_name].astype(str).apply(lambda text: remove_non_language_tokens(text, configuration_language))
                    
            # Extract words from all specified fields
            for field in fields:
                col_name = f"fields.{field}.value"
                if col_name in note_content.columns:
                    words = (note_content[col_name].str.split(expand=True)
                             .stack()
                             .reset_index(level=1, drop=True))
                    all_words.append(words)

        # Combine all words and remove duplicates
        if not all_words:
            raise ValueError(
                f"No vocabulary found for deck '{deck}'. "
                f"Check that the deck exists and the configured card types {list(card_types_and_fields.keys())} "
                f"with their fields are correct."
            )

        combined = pd.concat(all_words, ignore_index=True).drop_duplicates(keep='first')

        return combined
