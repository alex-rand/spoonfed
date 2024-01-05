from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QComboBox, QVBoxLayout, QGridLayout, QMessageBox, QDialog, QHBoxLayout, QLineEdit
from PyQt5.QtCore import Qt
import sqlite3
# Import DecksHomepageQt if converted
# from decks_homepage_qt import DecksHomepageQt

class LanguageConfigFrameQt(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = parent
        self.create_language_config_frame()

    def create_language_config_frame(self):
        layout = QVBoxLayout(self)

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

        back_button = QPushButton("Back", self)
        back_button.clicked.connect(self.back_to_user_config)
        layout.addWidget(back_button)

    def back_to_user_config(self):
        # Assuming UserConfigFrameQt is already converted
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
        dialog = NewLanguageConfigurationWindow(self, self)
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
        # Assuming DecksHomepageQt is already converted
        self.controller.configuration_name = self.configuration_dropdown.currentText()
        if self.controller.configuration_name:
            self.controller.show_frame(DecksHomepageQt)
            self.close()  # Closes the current window
            
class NewLanguageConfigurationWindow(QDialog):
    def __init__(self, parent=None, lang_config_frame=None):
        super().__init__(parent)
        self.main_app = parent
        self.lang_config_frame = lang_config_frame
        self.setWindowTitle("Add New Configuration")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Learned vocab section
        learned_layout = QHBoxLayout()
        layout.addLayout(learned_layout)

        learned_layout.addWidget(QLabel("Learned Deck Name:", self))
        self.learned_deck_entry = QLineEdit(self)
        learned_layout.addWidget(self.learned_deck_entry)

        # New vocab section
        new_layout = QHBoxLayout()
        layout.addLayout(new_layout)

        new_layout.addWidget(QLabel("New Deck Name:", self))
        self.new_deck_entry = QLineEdit(self)
        new_layout.addWidget(self.new_deck_entry)

        # Language Selection
        language_layout = QHBoxLayout()
        layout.addLayout(language_layout)

        language_layout.addWidget(QLabel("Select Language:", self))
        self.language_combobox = QComboBox(self)
        self.language_combobox.addItems(["Arabic", "Hindi", "Mandarin"])
        language_layout.addWidget(self.language_combobox)

        # Save button
        save_button = QPushButton("Save Configuration", self)
        save_button.clicked.connect(self.save_language_configuration)
        layout.addWidget(save_button)
        
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
                # Insert into languages table
                c.execute("INSERT INTO language_configurations (user_id, configuration_language, configuration_name, learned_deck, new_deck) VALUES (?, ?, ?, ?, ?)",
                          (self.main_app.selected_user_id, configuration_language, configuration_name, learned_deck, new_deck))
                configuration_id = c.lastrowid  # Get the ID of the newly inserted row
                # Assuming you have mechanisms to collect card types and fields
                # For each card type and field, you would have similar code as follows:
                # c.execute("INSERT INTO card_types (configuration_id, card_type_name) VALUES (?, ?)", (configuration_id, card_type))
                # card_type_id = c.lastrowid
                # c.execute("INSERT INTO card_fields (card_type_id, field_name) VALUES (?, ?)", (card_type_id, field))
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

            