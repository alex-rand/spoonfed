from PyQt5.QtWidgets import QAbstractItemView, QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QComboBox, QPushButton, QTreeWidget, QTreeWidgetItem, QScrollBar
from PyQt5.QtCore import Qt, QPropertyAnimation, QSequentialAnimationGroup, pyqtSignal, pyqtProperty
from PyQt5.QtGui import QColor, QPalette
import pandas as pd
from utils.text_generating_functions import generate_text
from utils.audio_generating_functions import generate_audio
from utils.anki_connect_functions import create_new_card
try:
    from ui.components import ModernButton, ModernComboBox, ModernCard, NavigationHeader, LoadingSpinner, ModernTreeWidget, ModernProgressBar
    from ui.animations import animation_manager
    UI_AVAILABLE = True
except ImportError:
    UI_AVAILABLE = False

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
        """Initialize the modern UI components"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(24)
        
        # Navigation header
        if UI_AVAILABLE:
            self.nav_header = NavigationHeader("Content Generation", show_back=True)
            self.nav_header.back_clicked.connect(self.on_press_back)
            self.main_layout.addWidget(self.nav_header)
        else:
            # Fallback: simple back button
            back_button = QPushButton("← Back")
            back_button.clicked.connect(self.on_press_back)
            self.main_layout.addWidget(back_button)
        
        # Main content card
        if UI_AVAILABLE:
            self.content_card = ModernCard(shadow=True)
        else:
            self.content_card = QFrame()
        content_layout = QVBoxLayout(self.content_card)
        content_layout.setSpacing(20)
        
        # Configuration section
        config_section = self.create_config_section()
        content_layout.addWidget(config_section)
        
        # Generation controls
        controls_section = self.create_controls_section()
        content_layout.addWidget(controls_section)
        
        # Results section
        results_section = self.create_results_section()
        content_layout.addWidget(results_section)
        
        self.main_layout.addWidget(self.content_card)
        
    def create_config_section(self):
        """Create the configuration section"""
        section = QFrame()
        layout = QVBoxLayout(section)
        
        # Section title
        title = QLabel("Generation Settings")
        title.setProperty("class", "h2")
        layout.addWidget(title)
        
        # Model selection
        model_row = QHBoxLayout()
        model_label = QLabel('AI Model:')
        if UI_AVAILABLE:
            self.model_picklist = ModernComboBox()
        else:
            self.model_picklist = QComboBox()
        self.model_picklist.addItems(['gpt-4o', 'o1-mini', 'o1-preview', 'o4-mini'])
        model_row.addWidget(model_label)
        model_row.addWidget(self.model_picklist, 2)
        layout.addLayout(model_row)

        # Selection criterion
        criterion_row = QHBoxLayout()
        criterion_label = QLabel('Selection Criterion:')
        if UI_AVAILABLE:
            self.selection_criterion_picklist = ModernComboBox()
        else:
            self.selection_criterion_picklist = QComboBox()
        self.selection_criterion_picklist.addItems(['n+1 with rogue', 'n+1 no rogue', 'n+2 with rogue', 'n+2 no rogue', 'None'])
        criterion_row.addWidget(criterion_label)
        criterion_row.addWidget(self.selection_criterion_picklist, 2)
        layout.addLayout(criterion_row)

        # Number of sentences
        sentences_row = QHBoxLayout()
        sentences_label = QLabel('Sentences to generate:')
        if UI_AVAILABLE:
            self.nsentences_picklist = ModernComboBox()
        else:
            self.nsentences_picklist = QComboBox()
        self.nsentences_picklist.addItems(['5', '10', '15', '20', '25', '30', '35', '40', '45', '50'])
        self.nsentences_picklist.setCurrentIndex(0)
        sentences_row.addWidget(sentences_label)
        sentences_row.addWidget(self.nsentences_picklist, 2)
        layout.addLayout(sentences_row)
        
        return section
        
    def create_controls_section(self):
        """Create the controls section"""
        section = QFrame()
        layout = QVBoxLayout(section)
        
        # Generate button
        if UI_AVAILABLE:
            self.generate_button = ModernButton("Generate Sentences", variant="primary", size="large")
        else:
            self.generate_button = QPushButton("Generate Sentences")
        self.generate_button.clicked.connect(self.on_press_generate)
        layout.addWidget(self.generate_button)
        
        # Loading components
        if UI_AVAILABLE:
            self.loading_spinner = LoadingSpinner(32)
        else:
            self.loading_spinner = QLabel("●")  # Simple loading indicator
        self.loading_label = QLabel('Generating sentences...')
        self.loading_label.setProperty("class", "body text-secondary")
        self.loading_label.setAlignment(Qt.AlignCenter)
        
        loading_layout = QHBoxLayout()
        loading_layout.addStretch()
        loading_layout.addWidget(self.loading_spinner)
        loading_layout.addWidget(self.loading_label)
        loading_layout.addStretch()
        
        self.loading_widget = QFrame()
        self.loading_widget.setLayout(loading_layout)
        self.loading_widget.hide()
        layout.addWidget(self.loading_widget)
        
        # Progress bar
        if UI_AVAILABLE:
            self.progress_bar = ModernProgressBar()
        else:
            from PyQt5.QtWidgets import QProgressBar
            self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        return section
        
    def create_results_section(self):
        """Create the results section"""
        section = QFrame()
        layout = QVBoxLayout(section)
        
        # Results title
        title = QLabel("Generated Content")
        title.setProperty("class", "h2")
        layout.addWidget(title)
        
        # Results table
        if UI_AVAILABLE:
            self.table = ModernTreeWidget()
        else:
            from PyQt5.QtWidgets import QTreeWidget
            self.table = QTreeWidget()
        self.table.setColumnCount(9)
        self.table.setHeaderLabels([
            'Export', 'Sentence', 'Translation', 'New Word', 
            'Total Words', 'Known Words', 'New Words',
            'Rogue Words', 'Meets Criteria'
        ])
        
        # Set selection mode to allow multiple row selection
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        layout.addWidget(self.table)
        
        # Export section
        export_section = QFrame()
        export_layout = QVBoxLayout(export_section)
        
        # Audio controls
        audio_controls = QFrame()
        audio_controls_layout = QHBoxLayout(audio_controls)
        
        self.audio_checkbox = QCheckBox('Include audio')
        self.audio_checkbox.setChecked(True)
        self.audio_checkbox.stateChanged.connect(self.toggle_audio_options)
        audio_controls_layout.addWidget(self.audio_checkbox)
        
        self.audio_source_label = QLabel('Audio source:')
        self.audio_source_label.setProperty("class", "body")
        if UI_AVAILABLE:
            self.audio_source_picklist = ModernComboBox()
        else:
            self.audio_source_picklist = QComboBox()
        self.audio_source_picklist.addItems(['ElevenLabs', 'Narakeet'])
        self.audio_source_picklist.setCurrentIndex(0)
        
        audio_controls_layout.addWidget(self.audio_source_label)
        audio_controls_layout.addWidget(self.audio_source_picklist)
        audio_controls_layout.addStretch()
        
        export_layout.addWidget(audio_controls)
        
        # Export button
        if UI_AVAILABLE:
            self.export_button = ModernButton("Export to Anki", variant="success", size="large")
        else:
            self.export_button = QPushButton("Export to Anki")
        self.export_button.clicked.connect(self.export_to_anki)
        self.export_button.hide()
        export_layout.addWidget(self.export_button)
        
        layout.addWidget(export_section)
        
        # Initialize audio options visibility
        self.toggle_audio_options()
        
        return section

    def hide_widgets(self, layout):
        """useful function for inheriting classes to customize the layout of the superclass"""
        if layout is not None:
            for i in range(layout.count()):  
                widget = layout.itemAt(i).widget()
                if widget is not None:
                    widget.hide()
        
    def on_press_back(self):
        # Avoid circular import by importing only when needed
        from decks_homepage import DecksHomepageQt
        self.controller.show_frame(DecksHomepageQt)
        
    def toggle_audio_options(self):
        """Toggle visibility of audio options based on checkbox state"""
        if self.audio_checkbox.isChecked():
            self.audio_source_label.show()
            self.audio_source_picklist.show()
        else:
            self.audio_source_label.hide()
            self.audio_source_picklist.hide()

    def start_generation_loading(self):
        """Start the modern loading animation"""
        self.generate_button.setEnabled(False)
        self.loading_widget.show()
        if UI_AVAILABLE:
            self.loading_spinner.start_animation()
        else:
            self.loading_spinner.setText("●●●")  # Simple loading indicator
        self.progress_bar.show()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

    def stop_generation_loading(self):
        """Stop the loading animation and hide the widgets"""
        if UI_AVAILABLE:
            self.loading_spinner.stop_animation()
        else:
            self.loading_spinner.setText("●")  # Reset loading indicator
        self.loading_widget.hide()
        self.progress_bar.hide()
        self.generate_button.setEnabled(True)

    def on_press_generate(self):
        """Stub function for inheriting frame classes"""
        self.start_generation_loading()

    def update_ui_after_generation(self, sentences, checkbox_column):
        """Update UI after generation is complete"""
        self.stop_generation_loading()
        
        if sentences is not None:
            self.populate_treeview(sentences.sort_values(by=checkbox_column, ascending=False))
            self.export_button.show()
            # Animate the results table
            if UI_AVAILABLE:
                animation_manager.fade_in(self.table, duration=300)

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
        """Stub function for inheriting frame classes"""
        pass

