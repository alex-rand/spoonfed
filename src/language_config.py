from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QComboBox, QVBoxLayout, QGridLayout, QMessageBox, QDialog, QHBoxLayout, QLineEdit, QInputDialog, QScrollArea
from PyQt5.QtCore import Qt
import sqlite3
from decks_homepage import DecksHomepageQt

class LanguageConfigFrameQt(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = parent
        self.create_language_config_frame()
        self.setFixedSize(500, 200)
        
    def showEvent(self, event):
        """Override the show event to refresh the dropdown each time the frame is shown."""
        self.load_language_configurations_to_dropdown()
        super().showEvent(event)
        self.controller.resize(500, 200)

    def create_language_config_frame(self):
        layout = QVBoxLayout(self)
        
        # Back button 
        top_layout = QHBoxLayout()
        self.back_button = QPushButton("Back", self)
        self.back_button.setFixedSize(100, 30)  # Example size, adjust as needed
        self.back_button.setStyleSheet("QPushButton { font-size: 10pt; }")  # Example style, adjust as needed
        self.back_button.clicked.connect(self.back_to_user_config)
        top_layout.addWidget(self.back_button)
        top_layout.addStretch()  # This will push the button to the left
        layout.addLayout(top_layout)
        top_layout.addStretch(1)  # This will push the button to the left

        # Title
        title = QLabel("Language Configuration", self)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Grid layout for form
        grid_layout = QGridLayout()
        layout.addLayout(grid_layout)

        # Dropdown for language configurations
        self.configuration_dropdown = QComboBox(self)
        grid_layout.addWidget(self.configuration_dropdown, 1, 0, 1, 2)

        # Buttons
        add_button = QPushButton("Add New Configuration", self)
        add_button.clicked.connect(self.add_new_configuration)
        grid_layout.addWidget(add_button, 2, 0)

        delete_button = QPushButton("Delete Configuration", self)
        delete_button.clicked.connect(self.delete_language_configuration)
        grid_layout.addWidget(delete_button, 2, 1)

        load_decks_button = QPushButton("Load Decks", self)
        load_decks_button.clicked.connect(self.execute_ankiconnect)
        layout.addWidget(load_decks_button)
        
    def back_to_user_config(self):
        from user_config import UserConfigFrameQt
        self.controller.show_frame(UserConfigFrameQt)
        
    def load_language_configurations_to_dropdown(self):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        # Access selected_user_id from the MainApp instance
        c.execute("SELECT configuration_name FROM language_configurations WHERE user_id=?", (self.controller.selected_user_id,))
        configurations = [row[0] for row in c.fetchall()]

        self.configuration_dropdown.clear()
        self.configuration_dropdown.addItems(configurations)

        conn.close()

    def add_new_configuration(self):
        # Create and show the dialog for new configuration
        dialog = NewLanguageConfigurationWindow(parent=self, lang_config_frame=None, selected_user_id=self.controller.selected_user_id)
        dialog.exec_()  # This will show the dialog modally

        # Refresh the dropdown after the dialog is closed
        self.load_language_configurations_to_dropdown()

    def delete_language_configuration(self):
        configuration_name = self.configuration_dropdown.currentText()
        if configuration_name:
            reply = QMessageBox.question(self, "Delete Configuration", "Are you sure you want to delete this language configuration?", QMessageBox.Yes | QMessageBox.No)

            if reply == QMessageBox.Yes:
                conn = sqlite3.connect('database.db')
                c = conn.cursor()
        
                try:
                    c.execute("DELETE FROM language_configurations WHERE configuration_name=? AND user_id=?", (configuration_name, self.controller.selected_user_id))
                    conn.commit()
                except sqlite3.Error as e:
                    QMessageBox.warning(self, "Error", f"Error deleting configuration from database: {e}")
                finally:
                    conn.close()

                # Refresh the dropdown to reflect the change
                self.load_language_configurations_to_dropdown()

    def execute_ankiconnect(self):
        # Get the selected configuration name from the dropdown
        self.controller.configuration_name = self.configuration_dropdown.currentText()

        # Establish database connection
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        # Retrieve the configuration_language for the selected user_id and configuration name
        c.execute("""
            SELECT configuration_language
            FROM language_configurations
            WHERE user_id = ? AND configuration_name = ?
        """, (self.controller.selected_user_id, self.controller.configuration_name))
        
        # Fetch the result and save as a 'global' variable
        configuration_language = c.fetchone()
        self.controller.selected_language = configuration_language[0]
        conn.close()

        self.controller.show_frame(DecksHomepageQt)
        self.close() 
                
class NewLanguageConfigurationWindow(QDialog):
    def __init__(self, parent=None, lang_config_frame=None, selected_user_id=None):
        super().__init__(parent)
        self.controller = parent.controller
        self.lang_config_frame = lang_config_frame
        self.selected_user_id = selected_user_id  
  
        self.learned_card_entries = []
        self.learned_field_entries = []
        self.new_card_entries = []
        self.new_field_entries = []

        self.setWindowTitle("Add New Configuration")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Learned vocab section with scroll area
        self.learned_scroll_area = QScrollArea(self)
        self.learned_scroll_widget = QWidget()
        self.learned_layout = QVBoxLayout(self.learned_scroll_widget)
        self.learned_scroll_area.setWidgetResizable(True)
        self.learned_scroll_area.setWidget(self.learned_scroll_widget)
        layout.addWidget(self.learned_scroll_area)

        self.add_learned_deck_name()
        self.add_learned_card_button = QPushButton("Add Learned Card Type & Fields", self)
        self.add_learned_card_button.clicked.connect(self.add_learned_card_field)
        self.learned_layout.addWidget(self.add_learned_card_button)

        # New vocab section with scroll area
        self.new_scroll_area = QScrollArea(self)
        self.new_scroll_widget = QWidget()
        self.new_layout = QVBoxLayout(self.new_scroll_widget)
        self.new_scroll_area.setWidgetResizable(True)
        self.new_scroll_area.setWidget(self.new_scroll_widget)
        layout.addWidget(self.new_scroll_area)

        self.add_new_deck_name()
        self.add_new_card_button = QPushButton("Add New Card Type & Fields", self)
        self.add_new_card_button.clicked.connect(self.add_new_card_field)
        self.new_layout.addWidget(self.add_new_card_button)

        # Language Selection
        self.add_language_selection(layout)

        # Save button
        self.add_save_button(layout)

    def add_learned_deck_name(self):
        deck_name_layout = QHBoxLayout()
        deck_name_layout.addWidget(QLabel("Learned Deck Name:", self))
        self.learned_deck_entry = QLineEdit(self)
        deck_name_layout.addWidget(self.learned_deck_entry)
        self.learned_layout.addLayout(deck_name_layout)

    def add_new_deck_name(self):
        deck_name_layout = QHBoxLayout()
        deck_name_layout.addWidget(QLabel("New Deck Name:", self))
        self.new_deck_entry = QLineEdit(self)
        deck_name_layout.addWidget(self.new_deck_entry)
        self.new_layout.addLayout(deck_name_layout)

    def add_language_selection(self, layout):
        language_layout = QHBoxLayout()
        language_layout.addWidget(QLabel("Select Language:", self))
        self.language_combobox = QComboBox(self)
        self.language_combobox.addItems(["Arabic", "Hindi", "Mandarin"])
        language_layout.addWidget(self.language_combobox)
        layout.addLayout(language_layout)

    def add_save_button(self, layout):
        save_button = QPushButton("Save Configuration", self)
        save_button.clicked.connect(self.save_language_configuration)
        layout.addWidget(save_button)

    def add_learned_card_field(self):
        self.add_card_field(self.learned_layout, self.learned_card_entries, self.learned_field_entries)

    def add_new_card_field(self):
        self.add_card_field(self.new_layout, self.new_card_entries, self.new_field_entries)

    def add_card_field(self, layout, card_entries, field_entries):
        frame = QHBoxLayout()
        card_entry = QLineEdit(self)
        field_entry = QLineEdit(self)

        frame.addWidget(QLabel("Card Type:", self))
        frame.addWidget(card_entry)
        frame.addWidget(QLabel("Fields (comma separated):", self))
        frame.addWidget(field_entry)

        layout.insertLayout(layout.count() - 1, frame)
        card_entries.append(card_entry)
        field_entries.append(field_entry)
        
    def save_language_configuration(self):
        configuration_name, ok = QInputDialog.getText(self, "Input", "Enter name for this configuration:")
        if ok and configuration_name:
            # Load all the user inputs
            learned_deck = self.learned_deck_entry.text()
            new_deck = self.new_deck_entry.text()
            configuration_language = self.language_combobox.currentText()

            # Connect to the database and append all the info
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            try:
                # Insert into language_configurations table
                c.execute("INSERT INTO language_configurations (user_id, configuration_language, configuration_name, learned_deck, new_deck) VALUES (?, ?, ?, ?, ?)",
                          (self.selected_user_id, configuration_language, configuration_name, learned_deck, new_deck))
                configuration_id = c.lastrowid  # Get the ID of the newly inserted row

                # Insert card types and fields for learned vocab
                for card_entry in self.learned_card_entries:
                    card_type = card_entry.text()
                    if card_type:
                        c.execute("INSERT INTO card_types (configuration_id, card_type_name) VALUES (?, ?)", (configuration_id, card_type))
                        card_type_id = c.lastrowid
                        field_entry = self.learned_field_entries[self.learned_card_entries.index(card_entry)]
                        fields = field_entry.text().split(',')
                        for field in fields:
                            if field:
                                c.execute("INSERT INTO card_fields (card_type_id, field_name) VALUES (?, ?)", (card_type_id, field.strip()))

                # Insert card types and fields for new vocab
                for card_entry in self.new_card_entries:
                    card_type = card_entry.text()
                    if card_type:
                        c.execute("INSERT INTO card_types (configuration_id, card_type_name) VALUES (?, ?)", (configuration_id, card_type))
                        card_type_id = c.lastrowid
                        field_entry = self.new_field_entries[self.new_card_entries.index(card_entry)]
                        fields = field_entry.text().split(',')
                        for field in fields:
                            if field:
                                c.execute("INSERT INTO card_fields (card_type_id, field_name) VALUES (?, ?)", (card_type_id, field.strip()))

                conn.commit()
                QMessageBox.information(self, "Success", "Configuration saved successfully")
            except sqlite3.Error as e:
                QMessageBox.warning(self, "Error", f"Error saving configuration to database: {e}")
            finally:
                conn.close()

            # Refresh dropdown in LanguageConfigFrame
            if self.lang_config_frame:
                self.lang_config_frame.load_language_configurations_to_dropdown()
            self.accept()  # This will close the dialog window


            