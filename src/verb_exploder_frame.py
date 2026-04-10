from PyQt5.QtWidgets import QMessageBox, QLabel, QHBoxLayout, QLineEdit, QCheckBox, QTreeWidgetItem
from PyQt5.QtCore import pyqtSignal, QRegExp
from PyQt5.QtGui import QRegExpValidator
import pandas as pd
from generating_frame import GeneratingFrameQt
import sys
import random
sys.path.append("../utils/")
from utils.text_generating_functions import generate_text
from utils.audio_generating_functions import generate_audio
from utils.anki_connect_functions import *
from utils.prompt_loader import load_prompt

TENSE_EMOJI = {
    'present continuous': '🔔',
    'aorist': '⬇️',
    'future': '➡️',
    'past definite': '⬅️',
    'past narrative': '👂',
    'necessitative': '⚠️',
    'ability': '🔑',
    'conditional': '🔀',
    'imperative': '🙏',
}
NEGATION_EMOJI = '🚫'


def add_tense_emojis(sentence, conjugation):
    """Wrap a sentence with tense and polarity emojis based on its conjugation label."""
    conj_lower = conjugation.lower()
    tense_emoji = ''
    for tense_name, emoji in TENSE_EMOJI.items():
        if tense_name in conj_lower:
            tense_emoji = emoji
            break
    if not tense_emoji:
        return sentence
    is_negative = 'negative' in conj_lower
    if is_negative:
        return f"{tense_emoji}{NEGATION_EMOJI} {sentence} {NEGATION_EMOJI}{tense_emoji}"
    return f"{tense_emoji} {sentence} {tense_emoji}"


class VerbExploderFrameQt(GeneratingFrameQt):
    update_ui_signal = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def showEvent(self, event):
        """Override the showEvent"""
        super().showEvent(event)
        self.controller.resize(1000, 500)
        
        # I think we don't want a filter condition for this functionality,
        # So overwrite the default value of the picklist
        self.selection_criterion_picklist.setCurrentText("None")

    def initUI(self):
        super().initUI()
       
        self.hide_widgets(self.selection_layout)
        self.nsentences_label.setText("N sentences per conjugation")
        self.nsentences_picklist.clear()
        self.nsentences_picklist.addItems(['1', '2', '3'])
        self.generate_button.setText("Generate cards")
        
        # New widgets for Verb input
        verb_layout = QHBoxLayout()  # Create a horizontal layout
        self.verb_label = QLabel('Verb (one word, any tense):', self)  # Create a label
        self.verb_input = QLineEdit(self)  # Create a text field for input
        self.verb_input.setMaximumWidth(100)
        
        # Set up the validator to only allow a single word (no spaces)
        no_space_regexp = QRegExp("\\S+")  # Regular expression for no spaces
        no_space_validator = QRegExpValidator(no_space_regexp, self.verb_input)
        self.verb_input.setValidator(no_space_validator)  # Apply the validator

        verb_layout.addWidget(self.verb_label)  # Add the label to the layout
        verb_layout.addWidget(self.verb_input)  # Add the text field to the layout
        
        verb_layout.setContentsMargins(0, 8, 190, 0)  # Left, Top, Right, Bottom margins
        verb_layout.setSpacing(8)  # Spacing between widgets in the layout
        
        # Set up the validator to only allow a single word (no spaces)
        no_space_regexp = QRegExp("\\S+")  # Regular expression for no spaces
        no_space_validator = QRegExpValidator(no_space_regexp, self.verb_input)
        self.verb_input.setValidator(no_space_validator)  # Apply the validator
       
        # Insert the new layout into the main layout
        self.main_layout.insertLayout(self.main_layout.indexOf(self.generate_button), verb_layout)
        
    def on_press_generate(self):
        
        # Make sure the verb input field is not empty
        if not self.verb_input.text().strip():
            QMessageBox.warning(self, "Input Required", "You forgot to input a verb.")
            return  
        
        self.generate_button.setEnabled(False)
       # self.animation.start()
        
        # Declare the prompt
        self.prompt = load_prompt(
            "verb_exploder",
            self.controller.selected_language,
            language=self.controller.selected_language,
            verb_input=self.verb_input.text(),
        ) 
        
        try:

            # Check whether the 'verb exploder' card type exists.
            has_ve = check_for_ve_card_type()

            # If the 'verb exploder' card type doesn't exist then create it
            if not has_ve:
                create_ve_card_type()

            # Generate sentences with the necessary cloze formatting and HTML tag around the target verb
            generated_sentences = generate_text(self)

            # Update the UI after generation
            self.update_ui_after_generation(generated_sentences, 'meets_criteria')

        except ValueError as e:  # Catch the specific error raised in generate_text
            QMessageBox.critical(self, "Generation Error", str(e))
            generated_sentences = None  # Or handle this case as needed

        self.generate_button.setEnabled(True)
        
    def update_ui_after_generation(self, sentences, checkbox_column):

        if sentences is not None:
            self.populate_treeview(sentences.sort_values(by=checkbox_column, ascending=False))
        self.loading_label.hide()
        self.generate_button.setEnabled(True)
        self.export_button.show()
        self.audio_frame.show()
        
    # Override interited method
    def populate_treeview(self, data_frame):
        self.table.clear()
        self.table.setColumnCount(9)  # Assuming 9 columns including the checkbox column
        self.table.setHeaderLabels([
            'Export', 'Sentence', 'Translation', 'Target Verb',  
            'Conjugation', 'Total Words', 'Known Words', 'New Words',
            'Rogue Words'
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
            tree_item.setText(3, str(row.target_verb))
            tree_item.setText(4, str(row.conjugation))
            tree_item.setText(5, str(row.n_words))
            tree_item.setText(6, str(row.n_known_words))
            tree_item.setText(7, str(row.n_new_words))
            tree_item.setText(8, str(row.n_rogue_words))
            
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
                    'target_verb': item.text(3),
                    'conjugation': item.text(4),
                    'total_words': item.text(5),
                    'known_words': item.text(6),
                    'new_words': item.text(7),
                    'rogue_words': item.text(8),
                })
                
        if not export_data:
            QMessageBox.warning(self, "Export Error", "Please check at least one item to export.")
            return  # Stop the function execution

        # Create a DataFrame from the collected data
        export_df = pd.DataFrame(export_data)
        
        # Add tense/polarity emojis to sentences based on conjugation labels (Turkish only)
        if self.controller.selected_language == "Turkish":
            export_df['sentence'] = export_df.apply(
                lambda row: add_tense_emojis(row['sentence'], row['conjugation']), axis=1
            )

        # If the 'audio' checkbox is checked then generate the audio files and pack them into Anki's media folder
        if self.audio_checkbox.isChecked():
            export_df = generate_audio(export_df, self.controller.selected_language, self.controller.selected_profile_name, self.audio_source_picklist.currentText())
    
        else: export_df['audio'] = ' '
        
        # Create the cards in Anki
        result = export_df.apply(lambda row: create_new_card(
            deck_name=self.controller.learned_deck,
            gpt_model=self.model_picklist.currentText(),
            audio_provider=self.audio_source_picklist.currentText(),
            anki_model="Spoonfed Verb Exploder",
            functionality="verb-exploder",
            fields={
                'Text': row['sentence'], 
                'Translation': row['translation'], 
                'Audio': row['audio']
            }
        ), axis=1)

        if result.eq("success").all():
            QMessageBox.information(self, "Success", "Cards successfully created in Anki.")
        else:
            QMessageBox.warning(self, "Export Error", "Cards could not be created.")
            
        # Return to the decks homepage        
        self.controller.show_frame(DecksHomepageQt)
        