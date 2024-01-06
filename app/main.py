import sys
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
        #self.selected_language = 
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
        # Database setup code remains mostly unchanged

# Rest of the code remains unchanged

# Running the Application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainApp = MainApp()
    mainApp.show()
    sys.exit(app.exec_())
