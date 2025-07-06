import sys
import os
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QFrame, QVBoxLayout
from PyQt5.QtCore import Qt
from user_config import UserConfigFrameQt
from language_config import LanguageConfigFrameQt
from decks_homepage import DecksHomepageQt
from iplusone import IPlusOneFrameQt
from previous_cards_audio_frame import PreviousCardsAudioFrameQt
from verb_exploder_frame import VerbExploderFrameQt

# Main Application Class
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spoonfed - AI-Powered Language Learning")
        
        # Set window properties
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        
        # Initialize UI components
        self.setup_ui()
        
        # Initialize the SQLite database
        self.setup_database()
        
        # Apply modern styling
        self.apply_styling()

        # Initialize some 'global' variables to be made available across all frames of the app
        self.selected_user_id = None
        self.selected_profile_name = None
        self.selected_language = None
        
        self.learned_deck_tokens = []
        self.new_deck_tokens = []

        # Tell the app what frames exist. These are all classes we define below
        # representing different screens in the UX.
        self.frames = {}
        for F in (UserConfigFrameQt, LanguageConfigFrameQt, DecksHomepageQt, IPlusOneFrameQt, PreviousCardsAudioFrameQt, VerbExploderFrameQt):
            frame = F(parent=self)
            self.frames[F] = frame
            self.layout.addWidget(frame)
            frame.hide()
            
        # Start by showing the first frame
        self.show_frame(UserConfigFrameQt)

    def setup_ui(self):
        """Initialize the main UI components"""
        self.central_widget = QFrame(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Set layout properties
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
    def apply_styling(self):
        """Apply the modern styling system"""
        try:
            # Try to load the simple stylesheet
            styles_path = os.path.join(os.path.dirname(__file__), "styles", "simple.qss")
            if os.path.exists(styles_path):
                with open(styles_path, 'r') as f:
                    stylesheet = f.read()
                self.setStyleSheet(stylesheet)
                print("✓ Applied modern styling")
            else:
                print("! Stylesheet not found, using default styling")
        except Exception as e:
            print(f"! Error applying styling: {e}")
        
    def show_frame(self, page_class):
        """Show a specific frame with smooth transition"""
        # Hide all frames
        for frame in self.frames.values():
            frame.hide()
            
        # Show the target frame
        target_frame = self.frames[page_class]
        target_frame.show()

    def setup_database(self):
        db_name = 'database.db'

        # Check if the database already exists
        if os.path.exists(db_name):
            return

        conn = sqlite3.connect(db_name)
        c = conn.cursor()

        # Create table for user configurations
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY, profile_name TEXT UNIQUE)''')

        # Create tables for language configurations
        c.execute('''
            CREATE TABLE IF NOT EXISTS language_configurations (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                configuration_name TEXT,
                configuration_language TEXT,
                learned_deck TEXT,
                new_deck TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS card_types (
                card_type_id INTEGER PRIMARY KEY,
                configuration_id INTEGER,
                card_type_name TEXT,
                FOREIGN KEY(configuration_id) REFERENCES language_configurations(id)
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS card_fields (
                field_id INTEGER PRIMARY KEY,
                card_type_id INTEGER,
                field_name TEXT,
                FOREIGN KEY(card_type_id) REFERENCES card_types(card_type_id)
            )
        ''')
        
        # Create table for runs
        c.execute('''CREATE TABLE IF NOT EXISTS runs
                     (run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      timestamp TEXT NOT NULL,
                      gpt_model TEXT,
                      audio_provider TEXT,
                      language_configuration_id INTEGER,
                      FOREIGN KEY(language_configuration_id) REFERENCES language_configurations(id))''')

        # Create table for gpt_responses
        c.execute('''CREATE TABLE IF NOT EXISTS gpt_responses
                     (run_id INTEGER,
                      n_sentences INTEGER,
                      sentence_order INTEGER,
                      sentence TEXT,
                      translation TEXT,
                      new_word TEXT,
                      n_words INTEGER,
                      n_known_words INTEGER,
                      n_new_words INTEGER,
                      n_rogue_words INTEGER,
                      filter_condition TEXT,
                      meets_criteria BOOLEAN,
                      FOREIGN KEY(run_id) REFERENCES runs(run_id))''')

        conn.commit()
        conn.close()
        
# Running the Application
if __name__ == "__main__":
    print("=== Starting Spoonfed Application ===")
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Spoonfed")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Spoonfed")
    
    try:
        mainApp = MainApp()
        mainApp.show()
        print("✓ Spoonfed application started successfully")
        print("✓ Modern UI styling applied")
        print("✓ Ready to use!")
        
        sys.exit(app.exec_())
    except Exception as e:
        print(f"✗ Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)