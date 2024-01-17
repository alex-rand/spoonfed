from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QPushButton, QVBoxLayout, QGridLayout, QInputDialog
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QCursor, QFont, QFontDatabase
import sqlite3
import webbrowser
import os
import random

from language_config import LanguageConfigFrameQt

# Assuming LanguageConfigFrame is also converted to PyQt5
# from language_config_qt import LanguageConfigFrameQt

class UserConfigFrameQt(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = parent
        self.create_user_config_frame()
        self.load_all_saved_users()
        self.setFixedSize(300, 450)

    def showEvent(self, event):
        """Override the show event to refresh the dropdown each time the frame is shown."""
        super().showEvent(event)
        self.controller.resize(300, 450)
        
    def create_user_config_frame(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)  
        self.controller.resize(300, 450)
        
        # Add custom font
        font_path = "assets/fonts/PlantinMTStd-Italic.otf"
        absolute_font_path = os.path.abspath(font_path)
        font_id = QFontDatabase.addApplicationFont(absolute_font_path)
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        
        app_title = QLabel("Spoonfed", self)
        app_title.setAlignment(Qt.AlignCenter)
        font = QFont(font_family, 36) 
        app_title.setFont(font)
        layout.addWidget(app_title)
        
        # Grid for inputs and labels
        grid_layout = QGridLayout()
        layout.addLayout(grid_layout)

        # Label and ComboBox for user profiles
        self.anki_profile_label = QLabel("Anki Profile Name:", self)
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
        
        self.display_random_image()
        
        # Style the dropdown and label
        self.anki_profile_label.setStyleSheet("QLabel { color: #555; }")

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
        
        c.execute("SELECT profile_name FROM users WHERE profile_name=?", (user_name,))
        self.controller.selected_profile_name = c.fetchone()[0]

        conn.close()

    def proceed_with_selected_user(self):
        selected_user = self.saved_users_dropdown.currentText()
        if selected_user:
            self.set_user_configuration(selected_user)
            self.controller.show_frame(LanguageConfigFrameQt)
            
    def display_random_image(self):
        image_folder = 'assets/images'
        images = [img for img in os.listdir(image_folder) if img.endswith('.png')]
        if images:
            selected_image = random.choice(images)
            pixmap = QPixmap(os.path.join(image_folder, selected_image))
            image_label = ClickableLabel(self)
            image_label.setPixmap(pixmap.scaled(300, 450)) # Adjust size as needed
            image_label.clicked.connect(self.on_image_click)
            self.layout().addWidget(image_label)
        
    def on_image_click(self):
        url = "https://github.com/alex-rand/spoonfed" 
        webbrowser.open(url)

class ClickableLabel(QLabel):
    clicked = pyqtSignal()  # Signal to be emitted when the label is clicked

    def __init__(self, *args, **kwargs):
        super(ClickableLabel, self).__init__(*args, **kwargs)
        self.setCursor(QCursor(Qt.PointingHandCursor))  # Set cursor initially

    def mousePressEvent(self, event):
        self.clicked.emit()
        self.setCursor(QCursor(Qt.PointingHandCursor))  # Reinstate the cursor after click

    def enterEvent(self, event):
        self.setCursor(QCursor(Qt.PointingHandCursor))  # Ensure cursor is set on re-enter

    def leaveEvent(self, event):
        self.unsetCursor()  # Reset cursor to default