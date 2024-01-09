from PyQt5.QtWidgets import QMessageBox, QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QComboBox, QPushButton, QTreeWidget, QTreeWidgetItem, QScrollBar
from PyQt5.QtCore import Qt, QPropertyAnimation, QSequentialAnimationGroup, pyqtSignal, pyqtProperty
from PyQt5.QtGui import QColor, QPalette
import pandas as pd
from text_generating_functions import generate_text
from audio_generating_functions import generate_audio
from anki_connect_functions import create_new_card
from generating_frame import GeneratingFrameQt

class PreviousCardsAudioFrameQt(GeneratingFrameQt):
    update_ui_signal = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def showEvent(self, event):
        """Override the showEvent"""
        super().showEvent(event)

    def initUI(self):
        super().initUI()
        
        self.hide_widgets(self.model_layout)
        self.hide_widgets(self.selection_layout)
        self.hide_widgets(self.nsentences_layout)
        self.main_layout.removeWidget(self.generate_button)
        self.main_layout.removeWidget(self.audio_checkbox)
        
        # Add a new frame-specific generate button
        self.generate_button = QPushButton("Generate Audio", self)
        self.generate_button.clicked.connect(self.on_press_generate)
        self.main_layout.addWidget(self.generate_button)
        
        # Lazy but declare brand new audio source picklist
        audio_layout = QHBoxLayout()  # Create a horizontal layout for audio controls
        self.audio_source_label = QLabel('Choose audio source:', self)
        self.audio_source_picklist = QComboBox(self)
        self.audio_source_picklist.addItems(['Narakeet', 'Fake'])
        self.audio_source_picklist.setCurrentIndex(0)

        audio_layout.addWidget(self.audio_source_label)
        audio_layout.addWidget(self.audio_source_picklist)

        self.main_layout.addLayout(audio_layout)

        

        

        