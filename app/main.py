import sys
import os
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QFrame, QVBoxLayout
from user_config import UserConfigFrameQt
from language_config import LanguageConfigFrameQt
from decks_homepage import DecksHomepageQt
from iplusone import IPlusOneFrameQt

# Import your PyQt converted frames here
# from user_config_qt import UserConfigFrameQt
# from language_config_qt import LanguageConfigFrameQt
# from decks_homepage_qt import DecksHomepageQt
# from iplusone_qt import IPlusOneFrameQt

# Main Application Class
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main App")
        
        self.central_widget = QFrame(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Initialize the SQLite database
        self.setup_database()

        # Initialize some 'global' variables to be made available across all frames of the app
        self.selected_user_id = None
        self.selected_profile_name = None
        self.selected_language = None
        
        
        self.learned_deck_tokens = []
        self.new_deck_tokens = []

        # Tell the app what frames exist. These are all classes we define below
        # representing different screens in the UX.
        self.frames = {}
        for F in (UserConfigFrameQt, LanguageConfigFrameQt, DecksHomepageQt, IPlusOneFrameQt):
            frame = F(parent=self)
            self.frames[F] = frame
            self.layout.addWidget(frame)
            frame.hide()
            
        # Start by showing the first frame
        self.show_frame(UserConfigFrameQt)

    def show_frame(self, page_class):
        for frame in self.frames.values():
            frame.hide()
        self.frames[page_class].show()

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
    app = QApplication(sys.argv)
    mainApp = MainApp()
    mainApp.show()
    sys.exit(app.exec_())
