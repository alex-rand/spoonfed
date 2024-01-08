from PyQt5.QtWidgets import QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QComboBox, QPushButton, QTreeWidget, QTreeWidgetItem, QScrollBar
from PyQt5.QtCore import Qt, QPropertyAnimation, QSequentialAnimationGroup, pyqtSignal, pyqtProperty, QThread
from PyQt5.QtGui import QColor, QPalette
from text_generating_functions import generate_text
from audio_generating_functions import generate_audio

class IPlusOneFrameQt(QWidget):
    update_ui_signal = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = parent
        self.initUI()

    def showEvent(self, event):
        """Override the showEvent"""
        super().showEvent(event)

    def initUI(self):
        main_layout = QVBoxLayout(self)

        # Model Selection UI
        model_layout = QHBoxLayout()
        self.model_label = QLabel('Model:', self)
        self.model_picklist = QComboBox(self)
        self.model_picklist.addItems(['gpt-3.5-turbo-1106', 'gpt-3.5-turbo', 'gpt-4-1106-preview'])
        model_layout.addWidget(self.model_label)
        model_layout.addWidget(self.model_picklist)
        main_layout.addLayout(model_layout)

        # Selection Criterion UI
        selection_layout = QHBoxLayout()
        self.selection_criterion_label = QLabel('Selection Criterion:', self)
        self.selection_criterion_picklist = QComboBox(self)
        self.selection_criterion_picklist.addItems(['n+1 with rogue', 'n+1 no rogue', 'n+2 with rogue', 'n+2 no rogue'])
        selection_layout.addWidget(self.selection_criterion_label)
        selection_layout.addWidget(self.selection_criterion_picklist)
        main_layout.addLayout(selection_layout)

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
        
        # Loading Indicator
        self.loading_label = FadeLabel('Generating Sentences...', self)
        self.loading_label.setAlignment(Qt.AlignCenter)
        palette = self.loading_label.palette()
        palette.setColor(QPalette.WindowText, QColor('red'))
        self.loading_label.setPalette(palette)
        self.loading_label.hide()
        main_layout.addWidget(self.loading_label)

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

        table_layout = QHBoxLayout()
        table_layout.addWidget(self.table)

        # Add scrollbar
        scrollbar = QScrollBar(Qt.Vertical, self)
        scrollbar.valueChanged.connect(self.table.verticalScrollBar().setValue)
        table_layout.addWidget(scrollbar)

        main_layout.addLayout(table_layout)
        
         # Export button
        self.export_button = QPushButton("Export to Anki", self)
        self.export_button.clicked.connect(self.export_to_anki)
        self.export_button.hide() 
        main_layout.addWidget(self.export_button)
        
        # Audio-related widgets sub-frame
        self.audio_frame = QFrame(self)
        self.audio_frame.hide() 
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
        self.loading_label.show()
        self.generate_button.setEnabled(False)
        self.animation.start()

        # Generate sentences directly in this method
        generated_sentences = generate_text(self)

        # Update the UI after generation
        self.update_ui_after_generation(generated_sentences)

        self.animation.stop()
        self.loading_label.hide()
        self.generate_button.setEnabled(True)
        
    def update_ui_after_generation(self, generated_sentences):
        if generated_sentences is not None:
            self.populate_treeview(generated_sentences.sort_values(by='meets_criteria', ascending=False))
        self.loading_label.hide()
        self.generate_button.setEnabled(True)
        self.export_button.show()
        self.audio_frame.show()


    def populate_treeview(self, data_frame):
        self.table.clear()
        self.table.setColumnCount(9)  # Assuming 9 columns including the checkbox column
        self.table.setHeaderLabels([
            'Export', 'Sentence', 'Translation', 'New Word', 
            'Total Words', 'Known Words', 'New Words',
            'Rogue Words', 'Meets Criteria'
        ])

        for row in data_frame.itertuples():
            tree_item = QTreeWidgetItem(self.table)

            # Checkbox in the first column
            checkbox = QCheckBox()
            checkbox.setChecked(row.meets_criteria)
            self.table.setItemWidget(tree_item, 0, checkbox)

            # Set other columns
            tree_item.setText(1, str(row.sentence))
            tree_item.setText(2, str(row.translation))
            tree_item.setText(3, str(row.new_word))
            tree_item.setText(4, str(row.n_words))
            tree_item.setText(5, str(row.n_known_words))
            tree_item.setText(6, str(row.n_new_words))
            tree_item.setText(7, str(row.n_rogue_words))
            tree_item.setText(8, str(row.meets_criteria))

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

