from PyQt5.QtWidgets import QComboBox, QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTreeWidget, QTreeWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
import pandas as pd
from utils.anki_connect_functions import *
from iplusone import IPlusOneFrameQt
from previous_cards_audio_frame import PreviousCardsAudioFrameQt
from ui.components import ModernButton, ModernComboBox, ModernCard, NavigationHeader, ModernTreeWidget, Breadcrumb
from ui.animations import animation_manager

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
        """Create the modern deck display interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)
        
        # Navigation header with breadcrumb
        self.nav_header = NavigationHeader("Vocabulary Dashboard", show_back=True)
        self.nav_header.back_clicked.connect(self.on_press_back)
        main_layout.addWidget(self.nav_header)
        
        # Breadcrumb
        breadcrumb = Breadcrumb(["Profile", "Language", "Dashboard"])
        main_layout.addWidget(breadcrumb)
        
        # Main content card
        content_card = ModernCard(shadow=True)
        content_layout = QVBoxLayout(content_card)
        content_layout.setSpacing(24)
        
        # Vocabulary overview section
        vocab_section = self.create_vocabulary_section()
        content_layout.addWidget(vocab_section)
        
        # Actions section
        actions_section = self.create_actions_section()
        content_layout.addWidget(actions_section)
        
        main_layout.addWidget(content_card)
        
    def create_vocabulary_section(self):
        """Create the vocabulary overview section"""
        section = QFrame()
        layout = QVBoxLayout(section)
        
        # Section title
        title = QLabel("Vocabulary Overview")
        title.setProperty("class", "h1")
        layout.addWidget(title)
        
        # Dual-pane vocabulary display
        vocab_panes = QHBoxLayout()
        
        # Learned vocabulary pane
        learned_pane = self.create_vocab_pane("Learned Vocabulary", "learned")
        vocab_panes.addWidget(learned_pane)
        
        # New vocabulary pane
        new_pane = self.create_vocab_pane("New Vocabulary", "new")
        vocab_panes.addWidget(new_pane)
        
        layout.addLayout(vocab_panes)
        return section
        
    def create_vocab_pane(self, title, vocab_type):
        """Create a vocabulary pane"""
        pane = ModernCard()
        layout = QVBoxLayout(pane)
        
        # Pane header
        header_layout = QHBoxLayout()
        
        pane_title = QLabel(title)
        pane_title.setProperty("class", "h2")
        header_layout.addWidget(pane_title)
        
        # Count badge
        count_label = QLabel("0")
        count_label.setProperty("class", "badge")
        header_layout.addWidget(count_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Tree widget
        if vocab_type == "learned":
            self.learned_deck_treeview = ModernTreeWidget()
            self.learned_deck_treeview.setHeaderLabels(["Learned Words"])
            self.learned_count_label = count_label
            layout.addWidget(self.learned_deck_treeview)
        else:
            self.new_deck_treeview = ModernTreeWidget()
            self.new_deck_treeview.setHeaderLabels(["New Words"])
            self.new_count_label = count_label
            layout.addWidget(self.new_deck_treeview)
        
        return pane
        
    def create_actions_section(self):
        """Create the actions section"""
        section = QFrame()
        layout = QVBoxLayout(section)
        
        # Section title
        title = QLabel("Available Actions")
        title.setProperty("class", "h2")
        layout.addWidget(title)
        
        # Action selection
        action_layout = QHBoxLayout()
        
        action_label = QLabel("Choose an action:")
        action_label.setProperty("class", "body")
        action_layout.addWidget(action_label)
        
        self.action_dropdown = ModernComboBox()
        action_layout.addWidget(self.action_dropdown, 2)
        
        # Continue button
        continue_button = ModernButton("Continue", variant="primary", size="large")
        continue_button.clicked.connect(self.on_press_continue)
        action_layout.addWidget(continue_button)
        
        layout.addLayout(action_layout)
        
        # Populate action dropdown
        self.action_dropdown.addItems([
            "Generate i+1 Sentences",
            "Verb Exploder",
            "Add Audio to Existing Cards",
            "Generate Sentences for Selected Token"
        ])
        
        return section
        
    def on_press_continue(self):
        """Handle the continue button press"""
        selected_action = self.action_dropdown.currentText()
        self.execute_selected_action(selected_action)
        
    def execute_selected_action(self, action=None):
        """Execute the selected action"""
        if action is None:
            action = self.action_dropdown.currentText()
            
        if action == "Verb Exploder":
            self.verb_exploder()
        elif action == "Generate i+1 Sentences":
            self.generate_iplus1()
        elif action == "Generate Sentences for Selected Token":
            self.generate_sentences_for_selected_token()
        elif action == "Add Audio to Existing Cards":
            self.generate_audio_for_existing_cards()

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
        """Insert vocabulary tokens into the treeview"""
        treeview.clear()

        for token in vocab_tokens:
            QTreeWidgetItem(treeview, [token])
        
        self.update_deck_counts()
        
        # Animation disabled to prevent QPainter conflicts
        # animation_manager.fade_in(treeview, duration=300)

    def update_deck_counts(self):
        """Update the count badges for vocabulary"""
        learned_count = self.learned_deck_treeview.topLevelItemCount()
        new_count = self.new_deck_treeview.topLevelItemCount()
        
        self.learned_count_label.setText(str(learned_count))
        self.new_count_label.setText(str(new_count))

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
        combined = pd.concat(all_words, ignore_index=True).drop_duplicates(keep='first')

        return combined
