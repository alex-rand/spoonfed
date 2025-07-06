#!/usr/bin/env python3
"""
Working test script for simplified Spoonfed UI components
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt

# Import simplified UI components
try:
    from ui.style_manager_fixed import style_manager
    from ui.components_simple import (
        ModernButton, ModernInput, ModernComboBox, ModernCard,
        LoadingSpinner, NavigationHeader, ModernTreeWidget, SpacingManager,
        show_success_notification, Breadcrumb
    )
    print("✓ Simplified UI components imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)


class SimpleUITestWindow(QMainWindow):
    """Test window to showcase the working UI components"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spoonfed UI Test - Working Version")
        self.setMinimumSize(800, 600)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup test UI"""
        # Apply modern styling
        style_manager.apply_theme('light')
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        SpacingManager.apply_margins(central_widget, 'lg', 'lg', 'lg', 'lg')
        SpacingManager.apply_spacing(layout, 'lg')
        
        # Test navigation header
        nav_header = NavigationHeader("UI Test - Working Version", show_back=False)
        layout.addWidget(nav_header)
        
        # Test breadcrumb
        breadcrumb = Breadcrumb(["Home", "Test", "UI Components"])
        layout.addWidget(breadcrumb)
        
        # Test components
        components_card = self.create_components_test()
        layout.addWidget(components_card)
        
        # Test interactions
        interactions_card = self.create_interactions_test()
        layout.addWidget(interactions_card)
        
    def create_components_test(self):
        """Create component test section"""
        card = ModernCard(shadow=True)
        layout = QVBoxLayout(card)
        
        # Card title
        title = QLabel("Component Tests")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #212529;
                margin-bottom: 16px;
            }
        """)
        layout.addWidget(title)
        
        # Button tests
        button_layout = QHBoxLayout()
        
        primary_btn = ModernButton("Primary Button", variant="primary")
        primary_btn.clicked.connect(lambda: show_success_notification(self, "Primary button clicked!"))
        button_layout.addWidget(primary_btn)
        
        secondary_btn = ModernButton("Secondary Button", variant="secondary")
        secondary_btn.clicked.connect(lambda: self.test_theme_toggle())
        button_layout.addWidget(secondary_btn)
        
        tertiary_btn = ModernButton("Tertiary Button", variant="tertiary")
        button_layout.addWidget(tertiary_btn)
        
        layout.addLayout(button_layout)
        
        # Input tests
        input_layout = QHBoxLayout()
        
        text_input = ModernInput("Enter some text...")
        input_layout.addWidget(text_input)
        
        combo_box = ModernComboBox()
        combo_box.addItems(["Option 1", "Option 2", "Option 3"])
        input_layout.addWidget(combo_box)
        
        layout.addLayout(input_layout)
        
        return card
        
    def create_interactions_test(self):
        """Create interactions test section"""
        card = ModernCard(shadow=True)
        layout = QVBoxLayout(card)
        
        # Card title
        title = QLabel("Interaction Tests")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #212529;
                margin-bottom: 16px;
            }
        """)
        layout.addWidget(title)
        
        # Loading spinner test
        spinner_layout = QHBoxLayout()
        
        spinner_label = QLabel("Loading Spinner:")
        spinner_label.setStyleSheet("font-size: 14px; color: #6C757D;")
        spinner_layout.addWidget(spinner_label)
        
        spinner = LoadingSpinner(24)
        spinner.start_animation()
        spinner_layout.addWidget(spinner)
        
        # Add button to start/stop spinner
        spinner_btn = ModernButton("Toggle Spinner", variant="tertiary", size="small")
        spinner_btn.clicked.connect(lambda: self.toggle_spinner(spinner))
        spinner_layout.addWidget(spinner_btn)
        
        spinner_layout.addStretch()
        layout.addLayout(spinner_layout)
        
        # Tree widget test
        tree_label = QLabel("Modern Tree Widget:")
        tree_label.setStyleSheet("font-size: 14px; color: #6C757D; margin-top: 16px;")
        layout.addWidget(tree_label)
        
        tree = ModernTreeWidget()
        tree.setHeaderLabels(["Item", "Value"])
        tree.setMaximumHeight(150)
        
        # Add some test data
        from PyQt5.QtWidgets import QTreeWidgetItem
        for i in range(5):
            item = QTreeWidgetItem(tree, [f"Item {i+1}", f"Value {i+1}"])
            
        layout.addWidget(tree)
        
        # Test different button variants
        variant_layout = QHBoxLayout()
        
        danger_btn = ModernButton("Danger", variant="danger", size="small")
        variant_layout.addWidget(danger_btn)
        
        success_btn = ModernButton("Success", variant="success", size="small")
        variant_layout.addWidget(success_btn)
        
        large_btn = ModernButton("Large Button", variant="primary", size="large")
        variant_layout.addWidget(large_btn)
        
        layout.addLayout(variant_layout)
        
        return card
        
    def test_theme_toggle(self):
        """Test theme switching"""
        style_manager.toggle_theme()
        current_theme = style_manager.current_theme
        show_success_notification(self, f"Switched to {current_theme} theme!")
        
    def toggle_spinner(self, spinner):
        """Toggle spinner animation"""
        if hasattr(spinner, '_running') and spinner._running:
            spinner.stop_animation()
            spinner._running = False
            show_success_notification(self, "Spinner stopped")
        else:
            spinner.start_animation()
            spinner._running = True
            show_success_notification(self, "Spinner started")


def main():
    """Main function"""
    print("Starting Spoonfed Simple UI Test...")
    
    # Create application
    app = QApplication(sys.argv)
    
    # Create and show test window
    window = SimpleUITestWindow()
    window.show()
    
    print("\nSimple UI Test Window opened successfully!")
    print("Test the following:")
    print("1. Click buttons to test interactions")
    print("2. Try the theme toggle button (Secondary Button)")
    print("3. Toggle the loading spinner")
    print("4. Try different button variants")
    print("5. Test input fields and combo box")
    print("\nPress Ctrl+C or close window to exit.")
    
    # Run application
    try:
        return app.exec_()
    except KeyboardInterrupt:
        print("\nExiting...")
        return 0


if __name__ == "__main__":
    sys.exit(main())