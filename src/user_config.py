from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QInputDialog, QFrame
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QCursor, QFont, QFontDatabase
import sqlite3
import webbrowser
import os
import random

from language_config import LanguageConfigFrameQt
from ui.components import ModernButton, ModernComboBox, ModernCard, NavigationHeader, Breadcrumb
from ui.animations import animation_manager

# Assuming LanguageConfigFrame is also converted to PyQt5
# from language_config_qt import LanguageConfigFrameQt

class UserConfigFrameQt(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = parent
        self.create_user_config_frame()
        self.load_all_saved_users()

    def showEvent(self, event):
        """Override the show event to refresh the dropdown each time the frame is shown."""
        super().showEvent(event)
        self.load_all_saved_users()
        
    def create_user_config_frame(self):
        """Create the modern user configuration frame"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(24)
        
        # Create centered container
        container = QFrame()
        container.setMaximumWidth(400)
        container.setProperty("class", "card")
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(24)
        container_layout.setContentsMargins(32, 32, 32, 32)
        
        # Add custom font for title
        font_path = "assets/fonts/PlantinMTStd-Italic.otf"
        absolute_font_path = os.path.abspath(font_path)
        if os.path.exists(absolute_font_path):
            font_id = QFontDatabase.addApplicationFont(absolute_font_path)
            if font_id != -1:
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                if font_families:
                    font_family = font_families[0]
                else:
                    font_family = "Arial"
            else:
                font_family = "Arial"
        else:
            font_family = "Arial"
        
        # App title
        app_title = QLabel("Spoonfed", self)
        app_title.setAlignment(Qt.AlignCenter)
        app_title.setProperty("class", "display accent")
        font = QFont(font_family, 36)
        app_title.setFont(font)
        container_layout.addWidget(app_title)
        
        # Subtitle
        subtitle = QLabel("AI-Powered Language Learning", self)
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setProperty("class", "body text-secondary")
        container_layout.addWidget(subtitle)
        
        # Form section
        form_section = QFrame()
        form_layout = QVBoxLayout(form_section)
        form_layout.setSpacing(16)
        
        # Profile selection label
        self.anki_profile_label = QLabel("Select Anki Profile:", self)
        self.anki_profile_label.setProperty("class", "h3")
        form_layout.addWidget(self.anki_profile_label)
        
        # Modern dropdown
        self.saved_users_dropdown = ModernComboBox(self)
        form_layout.addWidget(self.saved_users_dropdown)
        
        container_layout.addWidget(form_section)
        
        # Button section
        button_section = QFrame()
        button_layout = QVBoxLayout(button_section)
        button_layout.setSpacing(12)
        
        # Continue button
        continue_button = ModernButton("Continue", variant="primary", parent=self)
        continue_button.clicked.connect(self.proceed_with_selected_user)
        button_layout.addWidget(continue_button)
        
        # Add new user button
        add_user_button = ModernButton("Add New User", variant="secondary", parent=self)
        add_user_button.clicked.connect(self.add_new_user)
        button_layout.addWidget(add_user_button)
        
        container_layout.addWidget(button_section)
        
        # Center the container
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(container)
        center_layout.addStretch()
        
        main_layout.addStretch()
        main_layout.addLayout(center_layout)
        main_layout.addStretch()
        
        # Add background image
        self.display_background_image()

    def load_all_saved_users(self):
        """Load saved users into the dropdown"""
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("SELECT profile_name FROM users")
        user_profiles = [row[0] for row in c.fetchall()]

        # Clear existing items
        self.saved_users_dropdown.clear()
        
        # Add items
        if user_profiles:
            self.saved_users_dropdown.addItems(user_profiles)
            self.saved_users_dropdown.setCurrentIndex(0)
        else:
            self.saved_users_dropdown.addItem("No profiles found")

        conn.close()

    def add_new_user(self):
        """Add a new user profile"""
        new_user, ok = QInputDialog.getText(
            self, 
            "Add New Profile", 
            "Enter new user profile name:",
            text=""
        )
        if ok and new_user.strip():
            self.set_user_configuration(new_user.strip())
            self.load_all_saved_users()
            # Set the new user as selected
            index = self.saved_users_dropdown.findText(new_user.strip())
            if index >= 0:
                self.saved_users_dropdown.setCurrentIndex(index)

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
        """Proceed with the selected user profile"""
        selected_user = self.saved_users_dropdown.currentText()
        if selected_user and selected_user != "No profiles found":
            self.set_user_configuration(selected_user)
            self.controller.show_frame(LanguageConfigFrameQt)
            
    def display_background_image(self):
        """Display a subtle background image"""
        image_folder = 'assets/images'
        if os.path.exists(image_folder):
            images = [img for img in os.listdir(image_folder) if img.endswith('.png')]
            if images:
                selected_image = random.choice(images)
                pixmap = QPixmap(os.path.join(image_folder, selected_image))
                
                # Create a subtle background effect
                self.setStyleSheet(f"""
                    UserConfigFrameQt {{
                        background-image: url({os.path.join(image_folder, selected_image)});
                        background-repeat: no-repeat;
                        background-position: center;
                        background-attachment: fixed;
                    }}
                    UserConfigFrameQt:before {{
                        content: "";
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background-color: rgba(248, 249, 250, 0.85);
                        pointer-events: none;
                    }}
                """)
        
    def on_image_click(self):
        """Open GitHub repository"""
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