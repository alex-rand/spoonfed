from PyQt5.QtWidgets import QMessageBox, QLabel, QCheckBox, QTreeWidgetItem, QLineEdit, QHBoxLayout
from PyQt5.QtCore import pyqtSignal, pyqtProperty
from PyQt5.QtGui import QPalette
import pandas as pd
from generating_frame import GeneratingFrameQt
import sys
sys.path.append("../utils/")
from utils.text_generating_functions import generate_text
from utils.audio_generating_functions import generate_audio
from utils.anki_connect_functions import create_new_card, load_known_verbs
from utils.prompt_loader import load_prompt

EXPORT_CONFIG = {
    'Hindi': {
        'anki_model': 'Basic-10b04',
        'fields': lambda row: {
            'Front': row['sentence'],
            'Back': row['translation'],
            'Definition': row.get('audio', ' '),
        },
    },
    'Turkish': {
        'anki_model': 'turkish-back',
        'fields': lambda row: {
            'Front': row['translation'],
            'Back': row['sentence'] + ' ' + row.get('audio', ''),
        },
    },
}

class IPlusOneFrameQt(GeneratingFrameQt):
    update_ui_signal = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def showEvent(self, event):
        """Override the showEvent"""
        super().showEvent(event)
        self.controller.resize(1000, 500)

    def initUI(self):
        super().initUI()

        # Theme input (optional topic to focus generated sentences on)
        theme_layout = QHBoxLayout()
        self.theme_label = QLabel('Theme (optional):', self)
        self.theme_input = QLineEdit(self)
        self.theme_input.setPlaceholderText('e.g. cooking, travel, work')
        self.theme_input.setMaximumWidth(250)
        theme_layout.addWidget(self.theme_label)
        theme_layout.addWidget(self.theme_input)
        theme_layout.addStretch()
        theme_layout.setContentsMargins(0, 4, 0, 0)
        self.main_layout.insertLayout(self.main_layout.indexOf(self.generate_button), theme_layout)

        # Restrict verbs to those drilled (and exported) via the verb exploder
        verb_restrict_layout = QHBoxLayout()
        self.known_verbs_checkbox = QCheckBox('Restrict verbs to verb-exploder verbs', self)
        self.known_verbs_checkbox.setChecked(True)
        verb_restrict_layout.addWidget(self.known_verbs_checkbox)
        verb_restrict_layout.setContentsMargins(0, 4, 0, 0)
        self.main_layout.insertLayout(self.main_layout.indexOf(self.generate_button), verb_restrict_layout)

    def on_press_generate(self):
        n_sentences = int(self.nsentences_picklist.currentText())

        # Build new-words instruction depending on whether the new deck has tokens
        NEW_DECK_THRESHOLD = 5
        new_deck = self.controller.new_deck_tokens

        if len(new_deck) >= NEW_DECK_THRESHOLD:
            sampled_new = new_deck.sample(
                n=min(n_sentences, len(new_deck)), replace=False
            )
            new_words_instruction = (
                "Today the student is trying to learn the following words, "
                "which we can call the 'new words':\n"
                f"{', '.join(sampled_new)}\n\n"
                "Each sentence must include _exactly one_ of these 'new words'."
            )
        else:
            new_words_instruction = (
                "For each sentence, introduce exactly one new word that the "
                "student has NOT learned yet. Choose common, high-frequency "
                "nouns or adjectives appropriate for an intermediate learner. "
                "Try to pick a different new word for each sentence."
            )

        # Build theme instruction if user provided one
        theme = self.theme_input.text().strip()
        if theme:
            theme_instruction = (
                f"The sentences should use situational contexts related to the theme of: {theme}. "
                f"Draw on scenarios, settings, and vocabulary natural to this topic when building each sentence."
            )
        else:
            theme_instruction = ""

        # Build known-verbs constraint: restrict sentences to verbs the student
        # has drilled (and exported) via the verb exploder. The collection is
        # read live from Anki and is scoped per learner and language.
        known_verbs_instruction = ""
        if self.known_verbs_checkbox.isChecked():
            known_verbs = load_known_verbs(self.controller.learned_deck)
            if known_verbs:
                known_verbs_instruction = (
                    "The ONLY verbs you are allowed to use are verbs whose dictionary "
                    "(infinitive) form appears in the following list of 'known verbs'. "
                    "You may conjugate them into any tense, person, or aspect required, "
                    "but you must NOT use any verb whose infinitive is not in this list:\n"
                    f"{', '.join(known_verbs)}\n\n"
                    "The single 'new word' you introduce in each sentence must NOT be a "
                    "verb — it must be a noun, adjective, or adverb. Every verb appearing "
                    "in every sentence must come from the 'known verbs' list above."
                )
            else:
                QMessageBox.information(
                    self, "No known verbs found",
                    "No verb-exploder verbs were found for this deck, so the verb "
                    "restriction will be skipped. Run the verb exploder and export "
                    "some verbs first to build up your 'known verbs'."
                )

        # Declare the prompt
        self.prompt = load_prompt(
            "iplusone",
            self.controller.selected_language,
            language=self.controller.selected_language,
            learned_tokens=", ".join(self.controller.learned_deck_tokens),
            new_words_instruction=new_words_instruction,
            n_sentences=n_sentences,
            theme_instruction=theme_instruction,
            known_verbs_instruction=known_verbs_instruction,
        )
    
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
            export_df = generate_audio(export_df, self.controller.selected_language, self.controller.selected_profile_name, self.audio_source_picklist.currentText())
        else:
            export_df['audio'] = ' '

        # Create the cards in Anki
        config = EXPORT_CONFIG.get(self.controller.selected_language, EXPORT_CONFIG['Hindi'])
        result = export_df.apply(lambda row: create_new_card(
            deck_name=self.controller.learned_deck,
            gpt_model=self.model_picklist.currentText(),
            audio_provider=self.audio_source_picklist.currentText(),
            anki_model=config['anki_model'],
            functionality="i+1",
            fields=config['fields'](row),
        ), axis=1)
        
        if result.eq("success").all():
            QMessageBox.information(self, "Success", "Cards successfully created in Anki.")
        else:
            QMessageBox.warning(self, "Export Error", "Cards could not be created.")
            
        # Return to the decks homepage        
        self.controller.show_frame(DecksHomepageQt)
        
class FadeLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._opacity = 1

    def getOpacity(self):
        return self._opacity

    def setOpacity(self, opacity):
        self._opacity = opacity
        palette = self.palette()
        color = palette.color(QPalette.WindowText)
        color.setAlphaF(opacity)
        palette.setColor(QPalette.WindowText, color)
        self.setPalette(palette)

    opacity = pyqtProperty(float, getOpacity, setOpacity)