from PyQt5.QtWidgets import QMessageBox, QLabel, QCheckBox, QTreeWidgetItem
from PyQt5.QtCore import pyqtSignal
import pandas as pd
from generating_frame import GeneratingFrameQt
import sys
sys.path.append("../utils/")
from utils.text_generating_functions import generate_text
from utils.audio_generating_functions import generate_audio
from utils.anki_connect_functions import create_new_card

class VerbExploderFrameQt(GeneratingFrameQt):
    update_ui_signal = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def showEvent(self, event):
        """Override the showEvent"""
        super().showEvent(event)
        self.controller.resize(1000, 500)

    def initUI(self):
        super().initUI()
        
        self.hide_widgets(self.selection_layout)
        self.nsentences_label.setText("N sentences per conjugation")
        self.nsentences_picklist.clear()
        self.nsentences_picklist.addItems(['1', '2', '3'])
        self.generate_button.setText("Generate cards")
        
    def on_press_generate(self):
        self.loading_label.show()
        self.generate_button.setEnabled(False)
        self.animation.start()

        try:
            # Generate sentences 
            generated_sentences = generate_text(self)

            # Update the UI after generation
            self.update_ui_after_generation(generated_sentences, 'meets_criteria')

        except ValueError as e:  # Catch the specific error raised in generate_text
            QMessageBox.critical(self, "Generation Error", str(e))
            generated_sentences = None  # Or handle this case as needed

        self.animation.stop()
        self.loading_label.hide()
        self.generate_button.setEnabled(True)
        
    # Override interited method
    def populate_treeview(self, data_frame):
        self.table.clear()
        self.table.setColumnCount(9)  # Assuming 9 columns including the checkbox column
        self.table.setHeaderLabels([
            'Export', 'Sentence', 'Translation', 'New Word', 
            'Total Words', 'Known Words', 'New Words',
            'Rogue Words', 'Meets Criteria'
        ])

        for row in data_frame.itertuples():
            tree_item = QTreeWidgetItem(self.table)

            # Checkbox in the first column
            checkbox = QCheckBox()
            checkbox.setChecked(row.meets_criteria)
            self.table.setItemWidget(tree_item, 0, checkbox)

            # Set other columns
            tree_item.setText(1, str(row.sentence))
            tree_item.setText(2, str(row.translation))
            tree_item.setText(3, str(row.new_word))
            tree_item.setText(4, str(row.n_words))
            tree_item.setText(5, str(row.n_known_words))
            tree_item.setText(6, str(row.n_new_words))
            tree_item.setText(7, str(row.n_rogue_words))
            tree_item.setText(8, str(row.meets_criteria))
            
    def export_to_anki(self):
        from decks_homepage import DecksHomepageQt
        
        # Create a list to hold data for rows where the 'Export' checkbox is checked
        export_data = []

        # Iterate through the tree view items
        for index in range(self.table.topLevelItemCount()):
            item = self.table.topLevelItem(index)
            # Check if the checkbox in the 'Export' column is checked
            if self.table.itemWidget(item, 0).isChecked():
                # Append the data of the row to the export_data list
                export_data.append({
                    'sentence': item.text(1),
                    'translation': item.text(2),
                    'new_word': item.text(3),
                    'total_words': item.text(4),
                    'known_words': item.text(5),
                    'new_words': item.text(6),
                    'rogue_words': item.text(7),
                    'meets_criteria': item.text(8),
                })
                
        if not export_data:
            QMessageBox.warning(self, "Export Error", "Please check at least one item to export.")
            return  # Stop the function execution

        # Create a DataFrame from the collected data
        export_df = pd.DataFrame(export_data)
        
        # If the 'audio' checkbox is checked then generate the audio files and pack them into Anki's media folder
        if self.audio_checkbox.isChecked(): 
            export_df = generate_audio(export_df, self.controller.selected_language, self.controller.selected_profile_name)
    
        # Create the cards in Anki
        result = export_df.apply(create_new_card, args=(self.model_picklist.currentText(), self.audio_source_picklist.currentText()), axis=1)

        if result.eq("success").all():
            QMessageBox.information(self, "Success", "Cards successfully created in Anki.")
        else:
            QMessageBox.warning(self, "Export Error", "Cards could not be created.")
            
        # Return to the decks homepage        
        self.controller.show_frame(DecksHomepageQt)
        