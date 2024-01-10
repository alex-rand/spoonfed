from PyQt5.QtWidgets import QMessageBox, QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QComboBox, QPushButton, QTreeWidget, QTreeWidgetItem, QScrollBar
from PyQt5.QtCore import pyqtSignal
import pandas as pd
import numpy as np
from anki_connect_functions import *
from text_generating_functions import generate_text
from generating_frame import GeneratingFrameQt
from IPython.display import display, HTML


class PreviousCardsAudioFrameQt(GeneratingFrameQt):
    update_ui_signal = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def showEvent(self, event):
        """Override the showEvent"""
        super().showEvent(event)
        
        # Fetch configuration data
        configuration_data = fetch_user_configuration(self, self.controller.selected_user_id, self.controller.configuration_name)
        
        # Load the learned cards from anki
        learned_cards = self.load_sentences_from_deck('learned_deck', configuration_data)
  
        # check whether any of the fields point to an audio file in Anki's media colletion
        learned_cards = add_audio_flag(learned_cards)

        if learned_cards is not None:
            self.populate_treeview(learned_cards.sort_values(by='no_audio', ascending=False))
        
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
        
    def on_press_generate(self):
        """Overrides the inherited method, for frame-specific functionality"""
        self.loading_label.show()
        self.generate_button.setEnabled(False)
        self.animation.start()

        try:
            # Generate sentences 
            generated_sentences = generate_text(self)

            # Update the UI after generation
            self.update_ui_after_generation(generated_sentences)

        except ValueError as e:  # Catch the specific error raised in generate_text
            QMessageBox.critical(self, "Generation Error", str(e))
            generated_sentences = None  # Or handle this case as needed

        self.animation.stop()
        self.loading_label.hide()
        self.generate_button.setEnabled(True)
        
    def populate_treeview(self, data_frame):
        """
        Dynamically populate a tree view with data from a pandas DataFrame.
    
        Parameters:
        - data_frame (pd.DataFrame): DataFrame containing the data to be displayed.
        """
    
        # Clear existing data in the tree view
        self.table.clear()
    
        # Define standard and dynamic field headers
        standard_headers = ['deck_name', 'card_type', 'no_audio']
        standard_headers_clean = ['Deck Name', 'Card Type', 'No Audio']
        dynamic_headers = [col for col in data_frame.columns if col.startswith('fields.')]
        dynamic_headers_clean = ['Field: ' + col.split('.')[1].replace('_', ' ').capitalize() for col in dynamic_headers]
        
        # Combine the cleaned headers for display
        all_headers_clean = standard_headers_clean + dynamic_headers_clean
    
        # Set column count and headers using cleaned headers
        self.table.setColumnCount(len(all_headers_clean))
        self.table.setHeaderLabels(all_headers_clean)
    
        # Populate the tree view with data
        for _, row in data_frame.iterrows():
            # Create a new tree item for each row
            tree_item = QTreeWidgetItem(self.table)
    
            # Process standard headers
            for idx, header in enumerate(standard_headers):
                if header in data_frame.columns:
                    if header == 'no_audio':  # Assuming 'no_audio' needs a checkbox
                        checkbox = QCheckBox()
                        checkbox.setChecked(row[header] if not pd.isna(row[header]) else False)
                        self.table.setItemWidget(tree_item, idx, checkbox)
                    else:
                        tree_item.setText(idx, str(row[header]) if not pd.isna(row[header]) else "")
    
            # Process dynamic field headers
            dynamic_col_idx = len(standard_headers)
            for col in dynamic_headers:
                if col in data_frame.columns:
                    tree_item.setText(dynamic_col_idx, str(row[col]) if not pd.isna(row[col]) else "")
                    dynamic_col_idx += 1
                    
        

        
    def load_sentences_from_deck(self, deck, raw_config_data):
        """
        Load sentences from Anki cards based on specified deck, card types, and fields.

        Parameters:
        - deck (str): The name of the Anki deck.
        - raw_config_data (dict): A dictionary where keys are card types and values are lists of fields.

        Returns:
        - pd.DataFrame: A DataFrame with sentences from each field, the deck name, and the card type.
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
        unique_fields = set()  # To store unique fields across all card types

        for card_type, fields in card_types_and_fields.items():
            # Construct the query for the card type
            query = f'"deck:{deck}" "note:{card_type}"'

            # Retrieve note IDs for the card type
            note_ids = ankiconnect_invoke('findNotes', query=query)

            # Retrieve note content for the card type
            note_content = pd.json_normalize(ankiconnect_invoke('notesInfo', notes=note_ids))

            # Accumulate unique field names across all card types
            for col in note_content.columns:
                if '.' in col:  # Assuming field names contain a dot
                    unique_fields.add(col)

            # Append rows to all_sentences list
            for index, row in note_content.iterrows():
                new_row = {field: row[field] if field in row else None for field in unique_fields}
                new_row['deck_name'] = deck
                new_row['card_type'] = card_type
                all_sentences.append(new_row)

        # Convert the list of dictionaries to a DataFrame
        new_df = pd.DataFrame(all_sentences)
        
        # Filter columns to include only those ending with '.value'
        value_columns = [col for col in new_df.columns if col.endswith('.value')]
        final_columns = ['deck_name', 'card_type'] + value_columns

        # Reorder the DataFrame and return
        new_df = new_df[final_columns]
        
      #  new_df.to_csv("delete.csv", index=False)
        return new_df
           
 
        

        

        