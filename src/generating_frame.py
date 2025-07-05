from PyQt5.QtWidgets import QAbstractItemView, QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QComboBox, QPushButton, QTreeWidget, QTreeWidgetItem, QScrollBar
from PyQt5.QtCore import Qt, QPropertyAnimation, QSequentialAnimationGroup, pyqtSignal, pyqtProperty
from PyQt5.QtGui import QColor, QPalette
import pandas as pd
from utils.text_generating_functions import generate_text
from utils.audio_generating_functions import generate_audio
from utils.anki_connect_functions import create_new_card

class GeneratingFrameQt(QWidget):
    """Superclass for all GUI frames that involve generating sentences or audio"""
    update_ui_signal = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = parent
        self.initUI()
        
    def showEvent(self, event):
        """Override the showEvent"""
        super().showEvent(event)

    def initUI(self):
        self.main_layout = QVBoxLayout(self)
        
        # Back button 
        top_layout = QHBoxLayout()
        self.back_button = QPushButton("Back", self)
        self.back_button.setFixedSize(100, 30)  # Example size, adjust as needed
        self.back_button.setStyleSheet("QPushButton { font-size: 10pt; }")  # Example style, adjust as needed
        self.back_button.clicked.connect(self.on_press_back)
        top_layout.addWidget(self.back_button)
        top_layout.addStretch()  # This will push the button to the left
        self.main_layout.addLayout(top_layout)

        # Model Selection UI
        self.model_layout = QHBoxLayout()
        self.model_label = QLabel('Model:', self)
        self.model_picklist = QComboBox(self)
        self.model_picklist.addItems(['gpt-4o', 'o1-mini', 'o1-preview', 'o4-mini'])
        self.model_layout.addWidget(self.model_label)
        self.model_layout.addWidget(self.model_picklist)
        self.main_layout.addLayout(self.model_layout)

        # Selection Criterion UI
        self.selection_layout = QHBoxLayout()
        self.selection_criterion_label = QLabel('Selection Criterion:', self)
        self.selection_criterion_picklist = QComboBox(self)
        self.selection_criterion_picklist.addItems(['n+1 with rogue', 'n+1 no rogue', 'n+2 with rogue', 'n+2 no rogue', 'None'])
        self.selection_layout.addWidget(self.selection_criterion_label)
        self.selection_layout.addWidget(self.selection_criterion_picklist)
        self.main_layout.addLayout(self.selection_layout)

        # Label and Picklist for N sentences
        self.nsentences_layout = QHBoxLayout()
        self.nsentences_label = QLabel('N sentences to generate:', self)
        self.nsentences_picklist = QComboBox(self)
        self.nsentences_picklist.addItems(['5', '10', '15', '20', '25', '30', '35', '40', '45', '50'])
        self.nsentences_picklist.setCurrentIndex(0)
        self.nsentences_layout.addWidget(self.nsentences_label)
        self.nsentences_layout.addWidget(self.nsentences_picklist)
        self.main_layout.addLayout(self.nsentences_layout)

        # Generate button
        self.generate_button = QPushButton("Generate Sentences", self)
        self.generate_button.clicked.connect(self.on_press_generate)
        self.main_layout.addWidget(self.generate_button)
        
        # Loading Indicator
        self.loading_label = FadeLabel('Generating Sentences...', self)
        self.loading_label.setAlignment(Qt.AlignCenter)
        palette = self.loading_label.palette()
        palette.setColor(QPalette.WindowText, QColor('red'))
        self.loading_label.setPalette(palette)
        self.loading_label.hide()
        self.main_layout.addWidget(self.loading_label)

        # Fade-out animation
        fade_out = QPropertyAnimation(self.loading_label, b"opacity")
        fade_out.setDuration(1000)
        fade_out.setStartValue(1)
        fade_out.setEndValue(0)

        # Fade-in animation
        fade_in = QPropertyAnimation(self.loading_label, b"opacity")
        fade_in.setDuration(1000)
        fade_in.setStartValue(0)
        fade_in.setEndValue(1)

        # Sequential animation group
        self.animation = QSequentialAnimationGroup()
        self.animation.addAnimation(fade_out)
        self.animation.addAnimation(fade_in)
        self.animation.setLoopCount(-1)  # Loop indefinitely

        # Scrollable table
        self.table = QTreeWidget(self)
        self.table.setColumnCount(9)  
        self.table.setHeaderLabels([
            'Export', 'Sentence', 'Translation', 'New Word', 
            'Total Words', 'Known Words', 'New Words',
            'Rogue Words', 'Meets Criteria'
        ])  
        
        # Set selection mode to allow multiple row selection
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # Set selection behavior to select whole rows
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        # See this video for multiple selection: https://www.youtube.com/watch?v=RwjYTXeUlKg
        
        table_layout = QHBoxLayout()
        table_layout.addWidget(self.table)

        # Add scrollbar
        scrollbar = QScrollBar(Qt.Vertical, self)
        scrollbar.valueChanged.connect(self.table.verticalScrollBar().setValue)
        table_layout.addWidget(scrollbar)

        self.main_layout.addLayout(table_layout)
        
         # Export button
        self.export_button = QPushButton("Export to Anki", self)
        self.export_button.clicked.connect(self.export_to_anki)
        self.export_button.hide() 
        self.main_layout.addWidget(self.export_button)
        
        # Audio-related widgets sub-frame
        self.audio_frame = QFrame(self)
        self.audio_frame.hide() 
        self.main_layout.addWidget(self.audio_frame)
        audio_layout = QVBoxLayout(self.audio_frame)

        # Checkbox for 'with audio'
        self.audio_checkbox = QCheckBox('with audio', self.audio_frame)
        self.audio_checkbox.setChecked(True)
        self.audio_checkbox.stateChanged.connect(self.toggle_audio_options)
        audio_layout.addWidget(self.audio_checkbox)

        # Label and Picklist for 'choose audio source'
        self.audio_source_label = QLabel('Choose audio source:', self.audio_frame)
        self.audio_source_picklist = QComboBox(self.audio_frame)
        self.audio_source_picklist.addItems(['ElevenLabs', 'Narakeet'])
        self.audio_source_picklist.setCurrentIndex(0)
        self.toggle_audio_options()

        audio_layout.addWidget(self.audio_source_label)
        audio_layout.addWidget(self.audio_source_picklist)
        
        return self.main_layout

    def hide_widgets(self, layout):
        """useful function for inheriting classes to customize the layout of the superclass"""
        if layout is not None:
            for i in range(layout.count()):  
                widget = layout.itemAt(i).widget()
                if widget is not None:
                    widget.hide()
        
    def on_press_back(self):
        from decks_homepage import DecksHomepageQt
        self.controller.show_frame(DecksHomepageQt)
        
    def toggle_audio_options(self):
        if self.audio_checkbox.isChecked():
            self.audio_source_label.show()
            self.audio_source_picklist.show()
        else:
            self.audio_source_label.hide()
            self.audio_source_picklist.hide()

    def on_press_generate(self):
        """Stub function for inheriting frame classes"""
        pass

    def update_ui_after_generation(self, sentences, checkbox_column):

        if sentences is not None:
            self.populate_treeview(sentences.sort_values(by=checkbox_column, ascending=False))
        self.loading_label.hide()
        self.generate_button.setEnabled(True)
        self.export_button.show()
        self.audio_frame.show()

    def populate_treeview(self, data_frame):
        pass

    def clear_treeview(self):
        """Clear all entries in the treeview."""
        self.table.clear()

    def create_export_buttons(self):
        """Create 'Export to Anki' buttons."""
        self.export_button_frame = QFrame(self)
        export_button_layout = QHBoxLayout(self.export_button_frame)

        # Export to Anki button
        self.export_to_anki_button = QPushButton("Export to Anki", self.export_button_frame)
        self.export_to_anki_button.clicked.connect(self.export_to_anki)
        export_button_layout.addWidget(self.export_to_anki_button)

        # Cancel button
        self.cancel_export_button = QPushButton("Cancel", self.export_button_frame)
        self.cancel_export_button.clicked.connect(self.cancel_export)
        export_button_layout.addWidget(self.cancel_export_button)

        self.layout().addWidget(self.export_button_frame)

    def export_to_anki(self):
        pass

class FadeLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._opacity = 1

    def getOpacity(self):
        return self._opacity

    def setOpacity(self, opacity):
        self._opacity = opacity
        palette = self.palette()
        color = palette.color(QPalette.WindowText)
        color.setAlphaF(opacity)
        palette.setColor(QPalette.WindowText, color)
        self.setPalette(palette)

    opacity = pyqtProperty(float, getOpacity, setOpacity)

