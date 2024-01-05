from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QInputDialog
from PyQt5.QtCore import Qt
import sqlite3
from language_config import LanguageConfigFrameQt

# Assuming LanguageConfigFrame is also converted to PyQt5
# from language_config_qt import LanguageConfigFrameQt

class UserConfigFrameQt(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = parent
        self.create_user_config_frame()
        self.load_all_saved_users()

    def create_user_config_frame(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("User Configuration", self)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Grid for inputs and labels
        grid_layout = QGridLayout()
        layout.addLayout(grid_layout)

        # Label and ComboBox for user profiles
        self.anki_profile_label = QLabel("Anki Profile:", self)
        grid_layout.addWidget(self.anki_profile_label, 0, 0)

        self.saved_users_dropdown = QComboBox(self)
        grid_layout.addWidget(self.saved_users_dropdown, 0, 1)

        # Continue button
        continue_button = QPushButton("Continue", self)
        continue_button.clicked.connect(self.proceed_with_selected_user)
        layout.addWidget(continue_button)

        # Add new user button
        add_user_button = QPushButton("Add New User", self)
        add_user_button.clicked.connect(self.add_new_user)
        layout.addWidget(add_user_button)

    def load_all_saved_users(self):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("SELECT profile_name FROM users")
        user_profiles = [row[0] for row in c.fetchall()]

        self.saved_users_dropdown.addItems(user_profiles)
        if user_profiles:
            self.saved_users_dropdown.setCurrentIndex(0)

        conn.close()

    def add_new_user(self):
        new_user, ok = QInputDialog.getText(self, "Input", "Enter new user profile name:")
        if ok and new_user:
            self.set_user_configuration(new_user)
            self.load_all_saved_users()

    def set_user_configuration(self, user_name):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("INSERT OR IGNORE INTO users (profile_name) VALUES (?)", (user_name,))
        conn.commit()

        c.execute("SELECT id FROM users WHERE profile_name=?", (user_name,))
        self.controller.selected_user_id = c.fetchone()[0]

        conn.close()

    def proceed_with_selected_user(self):
        selected_user = self.saved_users_dropdown.currentText()
        if selected_user:
            self.set_user_configuration(selected_user)
            self.controller.show_frame(LanguageConfigFrameQt)
