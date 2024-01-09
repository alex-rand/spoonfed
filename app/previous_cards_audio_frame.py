from PyQt5.QtWidgets import QMessageBox, QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QComboBox, QPushButton, QTreeWidget, QTreeWidgetItem, QScrollBar
from PyQt5.QtCore import Qt, QPropertyAnimation, QSequentialAnimationGroup, pyqtSignal, pyqtProperty
from PyQt5.QtGui import QColor, QPalette
import pandas as pd
from anki_connect_functions import *
from generating_frame import GeneratingFrameQt

class PreviousCardsAudioFrameQt(GeneratingFrameQt):
    update_ui_signal = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def showEvent(self, event):
        """Override the showEvent"""
        super().showEvent(event)
        
        # Fetch configuration data
        configuration_data = fetch_user_configuration(self, self.controller.selected_user_id, self.controller.configuration_name)
        
        all_cards = self.load_sentences_from_deck('learned_deck', configuration_data)
        
        print(all_cards)
        
    def initUI(self):
        super().initUI()
        
        self.hide_widgets(self.model_layout)
        self.hide_widgets(self.selection_layout)
        self.hide_widgets(self.nsentences_layout)
        self.main_layout.removeWidget(self.generate_button)
        self.main_layout.removeWidget(self.audio_checkbox)
        
        # Add a new frame-specific generate button
        self.generate_button = QPushButton("Generate Audio", self)
        self.generate_button.clicked.connect(self.on_press_generate)
        self.main_layout.addWidget(self.generate_button)
        
        # Lazy but declare brand new audio source picklist
        audio_layout = QHBoxLayout()  # Create a horizontal layout for audio controls
        self.audio_source_label = QLabel('Choose audio source:', self)
        self.audio_source_picklist = QComboBox(self)
        self.audio_source_picklist.addItems(['Narakeet', 'Fake'])
        self.audio_source_picklist.setCurrentIndex(0)
        audio_layout.addWidget(self.audio_source_label)
        audio_layout.addWidget(self.audio_source_picklist)
        self.main_layout.addLayout(audio_layout)
        
        
    def load_sentences_from_deck(self, deck, raw_config_data):
        """
        Load sentences from Anki cards based on specified deck, card types, and fields.

        Parameters:
        - deck (str): The name of the Anki deck.
        - raw_config_data (dict): A dictionary where keys are card types and values are lists of fields.

        Returns:
        - pd.DataFrame: A DataFrame with sentences from each field and the deck name.
        """

        # Extract deck and card_types_and_fields from raw_config_data
        deck = raw_config_data.get(deck, None)
        raw_card_types_and_fields = raw_config_data.get('card_types_and_fields', {})
        configuration_language = raw_config_data.get('configuration_language', None)

        # Transform card_types_and_fields into the required format
        card_types_and_fields = {}
        for card_type, fields in raw_card_types_and_fields.items():
            clean_fields = [field.strip() for field in fields[0].split(',')]
            card_types_and_fields[card_type] = clean_fields

        all_sentences = []

        for card_type, fields in card_types_and_fields.items():
            # Construct the query for the card type
            query = f'"deck:{deck}" "note:{card_type}"'

            # Retrieve note IDs for the card type
            note_ids = ankiconnect_invoke('findNotes', query=query)

            # Retrieve note content for the card type
            note_content = pd.json_normalize(ankiconnect_invoke('notesInfo', notes=note_ids))

            # Process each field and add it to the DataFrame
            for i, field in enumerate(fields):
                col_name = f"fields.{field}.value"
                if col_name in note_content.columns:
                    note_content[col_name] = note_content[col_name].astype(str).apply(lambda text: remove_non_language_tokens(text, configuration_language))
                    all_sentences.append(note_content[[col_name]].rename(columns={col_name: f'field_{i+1}'}))

        # Combine all sentences into one DataFrame
        combined_df = pd.concat(all_sentences, axis=1)
        combined_df['deck_name'] = deck  # Add a column for the deck name

        return combined_df

        

        

        