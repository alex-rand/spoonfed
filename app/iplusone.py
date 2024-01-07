from PyQt5.QtWidgets import QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QComboBox, QPushButton, QTreeWidget, QTreeWidgetItem, QScrollBar
from PyQt5.QtCore import Qt
from generating_functions import generate
import pandas as pd

class IPlusOneFrameQt(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = parent  # Set controller to parent, which is an instance of MainApp
        self.initUI()

    def showEvent(self, event):
        """Override the showEvent"""
        super().showEvent(event)
        
        # Your existing logic here
        # Example: print to test if controller is set correctly
        print("Controller in IPlusOneFrameQt:", self.controller)

    def initUI(self):
        main_layout = QVBoxLayout(self)

        # Label and Picklist for 'choose model'
        self.model_label = QLabel('Choose model:', self)
        self.model_picklist = QComboBox(self)
        self.model_picklist.addItems(['gpt-4-1106-preview', 'gpt-3.5-turbo-1106', 'gpt-3.5-turbo'])
        self.model_picklist.setCurrentIndex(0)

        main_layout.addWidget(self.model_label)
        main_layout.addWidget(self.model_picklist)

        # Label and Picklist for N sentences
        self.nsentences_label = QLabel('N sentences to generate:', self)
        self.nsentences_picklist = QComboBox(self)
        self.nsentences_picklist.addItems(['5', '10', '15', '20', '25', '30', '35', '40', '45', '50'])
        self.nsentences_picklist.setCurrentIndex(0)

        main_layout.addWidget(self.nsentences_label)
        main_layout.addWidget(self.nsentences_picklist)

        # Generate button
        self.generate_button = QPushButton("Generate Sentences", self)
        self.generate_button.clicked.connect(self.on_press_generate)
        main_layout.addWidget(self.generate_button)

        # Scrollable table
        self.table = QTreeWidget(self)
        self.table.setColumnCount(8)  # Set to 11 for the number of columns you have
        self.table.setHeaderLabels([
            'Sentence', 'Translation', 'New Word', 
            'Number of Words', 'Number of Known Words', 'Number of New Words',
            'Number of Rogue Words', 'Meets Criteria'
        ])  

        table_layout = QHBoxLayout()
        table_layout.addWidget(self.table)

        # Add scrollbar
        scrollbar = QScrollBar(Qt.Vertical, self)
        scrollbar.valueChanged.connect(self.table.verticalScrollBar().setValue)
        table_layout.addWidget(scrollbar)

        main_layout.addLayout(table_layout)
        
        # Audio-related widgets sub-frame
        self.audio_frame = QFrame(self)
        main_layout.addWidget(self.audio_frame)
        audio_layout = QVBoxLayout(self.audio_frame)

        # Checkbox for 'with audio'
        self.audio_checkbox = QCheckBox('with audio', self.audio_frame)
        self.audio_checkbox.setChecked(True)
        self.audio_checkbox.stateChanged.connect(self.toggle_audio_options)
        audio_layout.addWidget(self.audio_checkbox)

        # Label and Picklist for 'choose audio source'
        self.audio_source_label = QLabel('Choose audio source:', self.audio_frame)
        self.audio_source_picklist = QComboBox(self.audio_frame)
        self.audio_source_picklist.addItems(['Narakeet', 'Fake'])
        self.audio_source_picklist.setCurrentIndex(0)
        self.toggle_audio_options()

        audio_layout.addWidget(self.audio_source_label)
        audio_layout.addWidget(self.audio_source_picklist)


    def toggle_audio_options(self):
        if self.audio_checkbox.isChecked():
            self.audio_source_label.show()
            self.audio_source_picklist.show()
        else:
            self.audio_source_label.hide()
            self.audio_source_picklist.hide()

    def on_press_generate(self):
        # Call the generate function and handle the returned data
        generated_sentences = generate(self.controller, self)
        if generated_sentences is not None:
           self.populate_treeview(generated_sentences)

    def populate_treeview(self, data_frame):
        self.table.clear()
        for row in data_frame.itertuples():
            QTreeWidgetItem(self.table, [
                str(row.sentence), 
                str(row.translation), 
                str(row.new_word), 
                str(row.n_words),
                str(row.n_known_words), 
                str(row.n_new_words), 
                str(row.n_rogue_words), 
                str(row.meets_criteria)
            ])

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
        # Implement the functionality to export to Anki
        pass

    def cancel_export(self):
        # Implement functionality to cancel export
        pass

    # ... rest of the class ...