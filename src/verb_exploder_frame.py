from PyQt5.QtWidgets import QMessageBox, QLabel, QHBoxLayout, QLineEdit, QCheckBox, QTreeWidgetItem
from PyQt5.QtCore import pyqtSignal, QRegExp
from PyQt5.QtGui import QRegExpValidator
import pandas as pd
from generating_frame import GeneratingFrameQt
import sys
sys.path.append("../utils/")
from utils.text_generating_functions import generate_text
from utils.audio_generating_functions import generate_audio
from utils.anki_connect_functions import *

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
        self.prompt = f""" 
            I need your help to output a .csv file containing new Hindi sentences based on a student's existing vocabulary, 
            following Anki Cloze formatting and with a single HTML tag according to a structure I will show you.
            Your output must be only a .csv file, with no other content.  
            Imagine you are a Hindi teacher, helping a native English speaker who has just started learning Hindi. 
            So far the student has learned the following words, which we can call the 'learned words', and are as follows: 
            {", ".join(self.controller.learned_deck_tokens)} 
            \n
            Today the student is trying to learn all the conjugations of a certain verb, which we can call the 'Target Verb':
            {self.verb_input.text()}
            \n
            Based on the above information, a new Hindi sentence for all possible conjugations (and, if applicable, gender forms) of the Target Verb, and return them as a .csv file with a column titled 'sentence'. Each sentence must meet all of the following criteria:
            - Each sentence includes _exactly one_ possible conjugation of the Target Verb;
            - All of the other words in each sentence (besides the Target Verb) must appear in the list of 'learned words';
            - Each sentence must include a unique, interesting situational context to help motivate the conjugation. Try to use a unique situational context that is different for each of the sentences, while remember to only use words from the above 'learned words';
            - The sentences should each follow normal punctuation, but the Target Verb word should be encased in Anki Cloze notation, where the clue is the infinitive of the target verb, with elipses '...' on either side of it to help indicate that it is the infinitive. For example, if the target verb were होना and the generated sentence were जब हम त्योहार में जाएँगे, तब हम खुश, the sentence would be written as हम खुश जब हम त्योहार में जाएँगे, तब हम खुश <span class=target_verb>{{{{c1::होंगे::…होना…}}}}</span>
            - The Target Verb Word, i.e. the full cloze including its curly braces, MUST be encased in an HTML <span> tag of class target_verb. The entire cloze for the Target Verb word must be inside this tag. This is very important!
            Please use correct grammar and formal sentence structure when writing the sentences, and always respect Hindi's standard subject-object-verb structure.  
            The output format of the new sentences you generate should be a .csv with a column for the Hindi sentence, 
            a column for the English translation called 'translation', and a column called 'target_verb' specifying the infinitive of the target verb, and a column called 'conjugation' containing the technical name of the conjugation the sentence is demonstrating. 
            Remember: other than the conjugation of the Target Verb, the rest of the words in each sentence must all already be present in the 'learned words' list above.
            Be careful to declare the HTML class properly in the span: it should be simply `class="target_verb"`, and you should NEVER include extra characters such as &quot; or / in this class declaration.
            The output MUST be a .csv file with columns exactly as specified above. 
            Do NOT say anything else, just output the raw .csv file and say nothing else. Do not wrap in ```, just output the raw .csv text.
            """ 
            
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

       # self.animation.stop()
       # self.loading_label.hide()
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
        
        # If the 'audio' checkbox is checked then generate the audio files and pack them into Anki's media folder
        if self.audio_checkbox.isChecked():
            export_df = generate_audio(export_df, self.controller.selected_language, self.controller.selected_profile_name)
    
        else: export_df['audio'] = ' '
        
        # Create the cards in Anki
        result = export_df.apply(lambda row: create_new_card(
            gpt_model=self.model_picklist.currentText(), 
            audio_provider=self.audio_source_picklist.currentText(), 
            anki_model="Spoonfed Verb Exploder",
            functionality="Verb Exploder",
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
        