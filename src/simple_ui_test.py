#!/usr/bin/env python3
"""
Minimal working UI test for Spoonfed
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QLineEdit, QComboBox, QFrame
from PyQt5.QtCore import Qt


class MinimalUITest(QMainWindow):
    """Minimal test window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spoonfed UI Test - Minimal Version")
        self.setGeometry(100, 100, 600, 400)
        self.setup_ui()
        self.apply_simple_styles()
        
    def setup_ui(self):
        """Setup minimal UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Title
        title = QLabel("Spoonfed UI Components Test")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #212529; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Card 1: Buttons
        card1 = QFrame()
        card1.setAccessibleName("card")
        card1_layout = QVBoxLayout(card1)
        
        card1_title = QLabel("Button Tests")
        card1_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        card1_layout.addWidget(card1_title)
        
        button_row = QHBoxLayout()
        
        btn_primary = QPushButton("Primary")
        btn_primary.clicked.connect(lambda: print("Primary button clicked!"))
        button_row.addWidget(btn_primary)
        
        btn_secondary = QPushButton("Secondary")
        btn_secondary.setAccessibleName("secondary")
        btn_secondary.clicked.connect(lambda: print("Secondary button clicked!"))
        button_row.addWidget(btn_secondary)
        
        btn_danger = QPushButton("Danger")
        btn_danger.setAccessibleName("danger")
        btn_danger.clicked.connect(lambda: print("Danger button clicked!"))
        button_row.addWidget(btn_danger)
        
        card1_layout.addLayout(button_row)
        layout.addWidget(card1)
        
        # Card 2: Inputs
        card2 = QFrame()
        card2.setAccessibleName("card")
        card2_layout = QVBoxLayout(card2)
        
        card2_title = QLabel("Input Tests")
        card2_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        card2_layout.addWidget(card2_title)
        
        input_row = QHBoxLayout()
        
        text_input = QLineEdit()
        text_input.setPlaceholderText("Enter text here...")
        input_row.addWidget(text_input)
        
        combo = QComboBox()
        combo.addItems(["Option 1", "Option 2", "Option 3"])
        input_row.addWidget(combo)
        
        card2_layout.addLayout(input_row)
        layout.addWidget(card2)
        
        # Status
        self.status_label = QLabel("Ready - Click buttons to test!")
        self.status_label.setStyleSheet("color: #6C757D; font-style: italic; margin-top: 20px;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
    def apply_simple_styles(self):
        """Apply simple stylesheet"""
        styles_path = os.path.join(os.path.dirname(__file__), "styles", "simple.qss")
        if os.path.exists(styles_path):
            try:
                with open(styles_path, 'r') as f:
                    stylesheet = f.read()
                self.setStyleSheet(stylesheet)
                print("✓ Applied simple stylesheet")
            except Exception as e:
                print(f"Error loading stylesheet: {e}")
        else:
            print(f"Stylesheet not found: {styles_path}")


def main():
    """Main function"""
    print("=== Spoonfed Minimal UI Test ===")
    
    # Create application
    app = QApplication(sys.argv)
    
    # Create window
    window = MinimalUITest()
    window.show()
    
    print("✓ Window created and shown")
    print("✓ Test the buttons and inputs")
    print("✓ Check console for click feedback")
    print("\nClose window or press Ctrl+C to exit.")
    
    # Run
    try:
        return app.exec_()
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())