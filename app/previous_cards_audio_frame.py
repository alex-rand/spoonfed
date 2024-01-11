from PyQt5.QtWidgets import QHBoxLayout, QLabel, QCheckBox, QComboBox, QPushButton, QTreeWidgetItem, QDialog, QVBoxLayout
from PyQt5.QtCore import pyqtSignal
import pandas as pd
from anki_connect_functions import *
from audio_generating_functions import generate_audio
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
        self.export_to_anki()
        
    def load_sentences_from_deck(self, deck, raw_config_data):
        """
        Load sentences from Anki cards based on specified deck, card types, and fields.

        Parameters:
        - deck (str): The name of the Anki deck.
        - raw_config_data (dict): A dictionary where keys are card types and values are lists of fields.

        Returns:
        - pd.DataFrame: A DataFrame with sentences from each field, the deck name, and the card type.
        """

        # Extract deck and card_types_and_fields from the selected language configuration
        deck = raw_config_data.get(deck, None)
        raw_card_types_and_fields = raw_config_data.get('card_types_and_fields', {})

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
                new_row['note_id'] = row['noteId'] 
                new_row['deck_name'] = deck
                new_row['card_type'] = card_type
                all_sentences.append(new_row)

        # Convert the list of dictionaries to a DataFrame
        new_df = pd.DataFrame(all_sentences)
        
        # Filter columns to include only those ending with '.value'
        value_columns = [col for col in new_df.columns if col.endswith('.value')]
        final_columns = ['note_id', 'deck_name', 'card_type'] + value_columns

        # Reorder the DataFrame and return
        new_df = new_df[final_columns]
        
      #  new_df.to_csv("delete.csv", index=False)
        return new_df
    
    def populate_treeview(self, data_frame):
        """
        Dynamically populate a tree view with data from a pandas DataFrame.

        Parameters:
        - data_frame (pd.DataFrame): DataFrame containing the data to be displayed.
        """

        # Clear existing data in the tree view
        self.table.clear()

        # Define standard and dynamic field headers
        standard_headers = ['note_id', 'deck_name', 'card_type', 'no_audio']
        standard_headers_clean = ['Note Id', 'Deck Name', 'Card Type', 'No Audio']
        dynamic_headers = [col for col in data_frame.columns if col.startswith('fields.')]
        dynamic_headers_clean = ['Field: ' + col.split('.')[1].replace('_', ' ').capitalize() for col in dynamic_headers]

        # Combine the cleaned headers for display
        all_headers_clean = ['Generate'] + standard_headers_clean + dynamic_headers_clean

        # Set column count and headers using cleaned headers
        self.table.setColumnCount(len(all_headers_clean))
        self.table.setHeaderLabels(all_headers_clean)

        # Populate the tree view with data
        for _, row in data_frame.iterrows():
            # Create a new tree item for each row
            tree_item = QTreeWidgetItem(self.table)

            # Add a checkbox in the 'Generate' column
            gen_checkbox = QCheckBox()
            no_audio_val = row['no_audio'] if 'no_audio' in data_frame.columns and not pd.isna(row['no_audio']) else False
            gen_checkbox.setChecked(no_audio_val)
            self.table.setItemWidget(tree_item, 0, gen_checkbox)  # Set the checkbox in the first column

            # Process other standard headers
            for idx, header in enumerate(standard_headers):
                if header in data_frame.columns:
                    if header == 'no_audio':  # Non-editable checkbox for 'No Audio'
                        checkbox = QCheckBox()
                        checkbox.setChecked(no_audio_val)
                        checkbox.setEnabled(False)
                        self.table.setItemWidget(tree_item, idx + 1, checkbox)  # Adjusted index due to 'Generate' column
                    else:
                        tree_item.setText(idx + 1, str(row[header]) if not pd.isna(row[header]) else "")  # Adjusted index due to 'Generate' column

            # Process dynamic field headers
            dynamic_col_idx = len(standard_headers) + 1  # Adjust for the added 'Generate' column
            for col in dynamic_headers:
                if col in data_frame.columns:
                    tree_item.setText(dynamic_col_idx, str(row[col]) if not pd.isna(row[col]) else "")
                    dynamic_col_idx += 1

    def export_to_anki(self):
        from decks_homepage import DecksHomepageQt

        tree_data = []
        for index in range(self.table.topLevelItemCount()):
            item = self.table.topLevelItem(index)

            # Check if the checkbox in the 'Generate' column is checked
            if self.table.itemWidget(item, 0).isChecked():
                row_data = {self.table.headerItem().text(i): item.text(i) for i in range(1, self.table.columnCount())}
                tree_data.append(row_data)

        df = pd.DataFrame(tree_data)

        # Get names of non-empty fields for each row. These are the candidate fields for audio generation.
        df['relevant_fields'] = df.apply(lambda row: [col for col in df.columns if col.startswith('Field:') and row[col] != ''], axis=1)

        # Declare a new row to contain the values of the fields to be exported, as selected by the user
        df['sentence'] = None

        # Prior to iteration, calculate some quantities for informative labels 
        total_rows = sum(len(row['relevant_fields']) > 1 for _, row in df.iterrows())
        current_row = 1

        # Keep track of card types for which the user has settled on a default field selection
        already_processed_card_types = set()

        # Go card-by-card, prompting the user to choose which field to generate audio for
        for index, row in df.iterrows():
            if row['relevant_fields'] and row['Card Type'] not in already_processed_card_types:
                if len(row['relevant_fields']) == 1:
                    selected_field, apply_to_all = row['relevant_fields'][0], False
                else:
                    # Prepare a dictionary of field values
                    field_values = {field: row[field] for field in row['relevant_fields']}
                    selected_field, apply_to_all = self.prompt_user_for_field(row['relevant_fields'], field_values, total_rows, current_row)
                    if apply_to_all:
                        already_processed_card_types.add(row['Card Type'])
                    current_row += 1

                if selected_field:  
                    if apply_to_all:
                        df.loc[df['Card Type'] == row['Card Type'], 'sentence'] = df.loc[df['Card Type'] == row['Card Type'], selected_field]
                    else:
                        df.at[index, 'sentence'] = row[selected_field]
        
        # Need to get the 'final' field name for each card type and store it as a column, to be called later.
        
        # call generate_audio to create+export the audio files, based on the text in the card-specific fields selected above                
        export_df = generate_audio(export_df, self.controller.selected_language, self.controller.selected_profile_name)
    
        # Call add_audio_to_existing_card(), adding the name of the generated audio file to the final field (can we do this non-destructively?)
       
        result = export_df.apply(add_audio_to_existing_card, args=(self.model_picklist.currentText(), self.audio_source_picklist.currentText()), axis=1)

        if result.eq("success").all():
            QMessageBox.information(self, "Success", "Cards successfully created in Anki.")
        else:
            QMessageBox.warning(self, "Export Error", "Cards could not be created.")
            
        # Return to the decks homepage        
        self.controller.show_frame(DecksHomepageQt)


    def prompt_user_for_field(self, fields, field_values, total_rows, current_row):
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Field")
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)

        # Information about current row and total rows
        info_label = QLabel(f"Selecting field for row {current_row} of {total_rows} with multiple options")
        layout.addWidget(info_label)

        # Field selection ComboBox
        comboBox = QComboBox(dialog)
        comboBox.addItems(fields)
        layout.addWidget(comboBox)

        # Display area for all field values
        values_layout = QVBoxLayout()
        for field in fields:
            field_label = QLabel(f"{field}: {field_values.get(field, 'No value')}")
            values_layout.addWidget(field_label)
        layout.addLayout(values_layout)

        # OK and Cancel buttons
        buttonLayout = QHBoxLayout()
        okButton = QPushButton("OK", dialog)
        cancelButton = QPushButton("Cancel", dialog)
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)
        layout.addLayout(buttonLayout)

        # Connect buttons to slots
        okButton.clicked.connect(dialog.accept)
        cancelButton.clicked.connect(dialog.reject)

        # Checkbox for applying to all cards of this type
        apply_all_checkbox = QCheckBox("Apply to all cards of this type", dialog)
        layout.addWidget(apply_all_checkbox)

        # Show the dialog and wait for user action
        result = dialog.exec_()

        if result == QDialog.Accepted:
            return comboBox.currentText(), apply_all_checkbox.isChecked()
        else:
            return None, False



    #   # Iterate through the tree view items
    #   for index in range(self.table.topLevelItemCount()):
    #       item = self.table.topLevelItem(index)
    #       # Check if the checkbox in the 'Export' column is checked
    #       if self.table.itemWidget(item, 0).isChecked():
    #           # Append the data of the row to the export_data list
    #           export_data.append({
    #               'sentence': item.text(1),
    #               'translation': item.text(2),
    #               'new_word': item.text(3),
    #               'total_words': item.text(4),
    #               'known_words': item.text(5),
    #               'new_words': item.text(6),
    #               'rogue_words': item.text(7),
    #               'meets_criteria': item.text(8),
    #           })
    #           
    #   if not export_data:
    #       QMessageBox.warning(self, "Export Error", "Please check at least one item to export.")
    #       return  # Stop the function execution

    #   # Create a DataFrame from the collected data
    #   export_df = pd.DataFrame(export_data)
    #   
    #   # If the 'audio' checkbox is checked then generate the audio files and pack them into Anki's media folder
    #   if self.audio_checkbox.isChecked(): 
    #       export_df = generate_audio(export_df, self.controller.selected_language, self.controller.selected_profile_name)
    #
    #   # Create the cards in Anki
    #   result = export_df.apply(create_new_card, args=(self.model_picklist.currentText(), self.audio_source_picklist.currentText()), axis=1)

    #   if result.eq("success").all():
    #       QMessageBox.information(self, "Success", "Cards successfully created in Anki.")
    #   else:
    #       QMessageBox.warning(self, "Export Error", "Cards could not be created.")
    #       
    #   # Return to the decks homepage        
    #   self.controller.show_frame(DecksHomepageQt)
           
 
        

        

        