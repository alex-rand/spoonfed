from PyQt5.QtWidgets import QHBoxLayout, QLabel, QCheckBox, QComboBox, QPushButton, QTreeWidgetItem, QDialog, QVBoxLayout
from PyQt5.QtCore import pyqtSignal
import pandas as pd
from utils.anki_connect_functions import *
from utils.audio_generating_functions import generate_audio
from generating_frame import GeneratingFrameQt

class PreviousCardsAudioFrameQt(GeneratingFrameQt):
    update_ui_signal = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def showEvent(self, event):
        """Override the showEvent"""
        super().showEvent(event)
        self.controller.resize(1000, 500)
        
        # Fetch configuration data
        self.configuration_data = fetch_user_configuration(self, self.controller.selected_user_id, self.controller.configuration_name)
        
        # Load the learned cards from anki
        learned_cards = self.load_sentences_from_deck('learned_deck', self.configuration_data)
  
        # check whether any of the fields point to an audio file in Anki's media colletion
        learned_cards = add_audio_flag(learned_cards)

        if learned_cards is not None:
            
            # Filter for rows where no_audio is True
            learned_cards_no_audio = learned_cards[learned_cards['no_audio'] == True]

            # Pass only the filtered DataFrame to populate_treeview
            self.populate_treeview(learned_cards_no_audio.sort_values(by='no_audio', ascending=False))
        
    def initUI(self):
        super().initUI()
        
        # Hide specific widgets instead of layouts that don't exist
        self.model_picklist.hide()
        self.selection_criterion_picklist.hide()
        self.nsentences_picklist.hide()
        self.audio_checkbox.hide()
        
        # Replace the existing generate button text and functionality
        self.generate_button.setText("Generate Audio")
        # Disconnect the old signal and connect the new one
        self.generate_button.clicked.disconnect()
        self.generate_button.clicked.connect(self.on_press_generate)
        
        # Show the audio source controls that were already created in the parent class
        self.audio_source_label.show()
        self.audio_source_picklist.show()
        self.audio_source_label.setText('Choose audio source:')
        
    def on_press_generate(self):
        self.export_to_anki(self.configuration_data)
        
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
            note_ids = ankiconnect_invoke(self, 'findNotes', query=query)
            
            card_ids = ankiconnect_invoke(self, 'findCards', query=query)

            # Retrieve note content for the card type
            note_content = pd.json_normalize(ankiconnect_invoke(self, 'notesInfo', notes=note_ids))
            
            # Remove suspended cards
            to_suspend = check_suspended_status(card_ids)
            mask = -pd.Series(to_suspend)
            note_content = note_content[mask]
            
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

    def export_to_anki(self, raw_config_data):
        from decks_homepage import DecksHomepageQt
        
        tree_data = []
        for index in range(self.table.topLevelItemCount()):
            item = self.table.topLevelItem(index)
            if self.table.itemWidget(item, 0).isChecked():
                row_data = {self.table.headerItem().text(i): item.text(i) for i in range(1, self.table.columnCount())}
                tree_data.append(row_data)

        df = pd.DataFrame(tree_data)
        df['relevant_fields'] = df.apply(lambda row: [col for col in df.columns if col.startswith('Field:') and row[col] != ''], axis=1)
        df['sentence'] = None

        total_rows = len(df)
        current_row = 1
        already_processed_card_types = set()
        rows_to_drop = []

        # Select the content from the user-specified field and pack it into the 'sentence' field of the df to send to audio API.
        for index, row in df.iterrows():
            if row['relevant_fields'] and row['Card Type'] not in already_processed_card_types:
                field_values = {field: row[field] for field in row['relevant_fields']}
                result = self.prompt_user_for_field(row['relevant_fields'], field_values, total_rows, current_row)
                if result is None:
                    rows_to_drop.append(index)
                    current_row += 1
                    continue
                selected_field, apply_to_all = result
                if apply_to_all:
                    already_processed_card_types.add(row['Card Type'])
                    df.loc[df['Card Type'] == row['Card Type'], 'sentence'] = row[selected_field]
                    current_row += df[df['Card Type'] == row['Card Type']].shape[0]
                    continue
                df.at[index, 'sentence'] = row[selected_field]
            current_row += 1

        df.drop(rows_to_drop, inplace=True)
        
        # Remove HTML headers, which Anki sometimes adds automatically and which confuse Narakeet
        df['sentence'] = df['sentence'].str.replace(r'<[^>]+>', '')
                    
        # Need to get the 'final' field name for each card type and store it as a column, to be called later.
        card_types_and_fields = raw_config_data.get('card_types_and_fields', {})
        last_fields = {card_type: fields[-1] for card_type, fields in card_types_and_fields.items()}

        # Generate the new audio file             
        df = generate_audio(df, self.controller.selected_language, self.controller.selected_profile_name, self.audio_source_picklist.currentText())
    
        # Append the name of the generated audio file to the final field (can we do this non-destructively?)
        result = append_audio_file_to_notes(df, last_fields)

        if result['success_count'] > 0 and not result['errors']:
            QMessageBox.information(self, "Success", f"Cards successfully created in Anki. Total: {result['success_count']}")
        else:
            error_message = "Some cards could not be updated. Check the errors for details."
            if result['errors']:
                error_details = "\n".join([f"Row {index}: {error}" for index, error in result['errors']])
                error_message += "\n\nDetails:\n" + error_details
            QMessageBox.warning(self, "Export Error", error_message)
            
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
        cancelButton = QPushButton("Skip", dialog)
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
        
        if result == 1:
            return comboBox.currentText(), apply_all_checkbox.isChecked()
        else:
            return None
