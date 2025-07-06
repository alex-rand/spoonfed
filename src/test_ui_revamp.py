#!/usr/bin/env python3
"""
Test script for Spoonfed UI Revamp
Verifies that all new UI components and styling work correctly
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import UI components
from ui import (
    style_manager, ModernButton, ModernInput, ModernComboBox, ModernCard,
    LoadingSpinner, NavigationHeader, ModernTreeWidget, SpacingManager,
    show_success_notification, ResponsiveContainer, make_hoverable
)
from ui.microinteractions import add_micro_interactions, animate_widget_entrance


class UITestWindow(QMainWindow):
    """Test window to showcase the revamped UI components"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spoonfed UI Revamp Test")
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
        nav_header = NavigationHeader("UI Revamp Test", show_back=False)
        layout.addWidget(nav_header)
        
        # Test components card
        components_card = self.create_components_test()
        layout.addWidget(components_card)
        
        # Test interactions card
        interactions_card = self.create_interactions_test()
        layout.addWidget(interactions_card)
        
        # Test notifications
        self.test_notifications()
        
    def create_components_test(self):
        """Create component test section"""
        card = ModernCard(shadow=True)
        layout = QVBoxLayout(card)
        
        # Card title
        title = QLabel("Component Tests")
        title.setProperty("class", "h2")
        layout.addWidget(title)
        
        # Button tests
        button_layout = QHBoxLayout()
        
        primary_btn = ModernButton("Primary Button", variant="primary")
        primary_btn.clicked.connect(lambda: show_success_notification(self, "Primary button clicked!"))
        button_layout.addWidget(primary_btn)
        
        secondary_btn = ModernButton("Secondary Button", variant="secondary")
        secondary_btn.clicked.connect(lambda: self.test_theme_toggle())
        button_layout.addWidget(secondary_btn)
        
        danger_btn = ModernButton("Danger Button", variant="danger")
        button_layout.addWidget(danger_btn)
        
        layout.addLayout(button_layout)
        
        # Input tests
        input_layout = QHBoxLayout()
        
        text_input = ModernInput("Enter some text...")
        input_layout.addWidget(text_input)
        
        combo_box = ModernComboBox()
        combo_box.addItems(["Option 1", "Option 2", "Option 3"])
        input_layout.addWidget(combo_box)
        
        layout.addLayout(input_layout)
        
        # Loading spinner test
        spinner_layout = QHBoxLayout()
        spinner_label = QLabel("Loading Spinner:")
        spinner_label.setProperty("class", "body")
        spinner_layout.addWidget(spinner_label)
        
        spinner = LoadingSpinner(24)
        spinner.start_animation()
        spinner_layout.addWidget(spinner)
        spinner_layout.addStretch()
        
        layout.addLayout(spinner_layout)
        
        return card
        
    def create_interactions_test(self):
        """Create interactions test section"""
        card = ModernCard(shadow=True)
        layout = QVBoxLayout(card)
        
        # Card title
        title = QLabel("Interaction Tests")
        title.setProperty("class", "h2")
        layout.addWidget(title)
        
        # Hoverable elements
        hover_layout = QHBoxLayout()
        
        hover_btn1 = ModernButton("Hover for Lift", variant="tertiary")
        make_hoverable(hover_btn1, "lift")
        hover_layout.addWidget(hover_btn1)
        
        hover_btn2 = ModernButton("Hover for Scale", variant="tertiary")
        make_hoverable(hover_btn2, "scale")
        hover_layout.addWidget(hover_btn2)
        
        hover_btn3 = ModernButton("Hover for Glow", variant="tertiary")
        make_hoverable(hover_btn3, "glow")
        hover_layout.addWidget(hover_btn3)
        
        layout.addLayout(hover_layout)
        
        # Add micro-interactions to all buttons
        for i in range(hover_layout.count()):
            widget = hover_layout.itemAt(i).widget()
            if widget:
                add_micro_interactions(widget)
        
        # Tree widget test
        tree_label = QLabel("Modern Tree Widget:")
        tree_label.setProperty("class", "body")
        layout.addWidget(tree_label)
        
        tree = ModernTreeWidget()
        tree.setHeaderLabels(["Item", "Value"])
        tree.setMaximumHeight(150)
        
        # Add some test data
        from PyQt5.QtWidgets import QTreeWidgetItem
        for i in range(5):
            item = QTreeWidgetItem(tree, [f"Item {i+1}", f"Value {i+1}"])
            
        layout.addWidget(tree)
        
        return card
        
    def test_theme_toggle(self):
        """Test theme switching"""
        current_theme = getattr(style_manager, 'current_theme', 'light')
        new_theme = 'dark' if current_theme == 'light' else 'light'
        style_manager.apply_theme(new_theme)
        show_success_notification(self, f"Switched to {new_theme} theme!")
        
    def test_notifications(self):
        """Test notification system"""
        # Show initial success notification
        show_success_notification(self, "UI Revamp loaded successfully!")
        
    def showEvent(self, event):
        """Animate widgets on show"""
        super().showEvent(event)
        
        # Find all cards and animate them
        cards = self.findChildren(ModernCard)
        for i, card in enumerate(cards):
            animate_widget_entrance(card, "slide_up", delay=i * 100)


def run_ui_tests():
    """Run the UI tests"""
    print("Starting Spoonfed UI Revamp Tests...")
    
    # Test imports
    try:
        from ui import style_manager
        print("✓ Style manager imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import style manager: {e}")
        return False
    
    try:
        from ui.components import ModernButton, ModernCard
        print("✓ Modern components imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import components: {e}")
        return False
    
    try:
        from ui.animations import animation_manager
        print("✓ Animation manager imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import animations: {e}")
        return False
    
    try:
        from ui.feedback import NotificationManager
        print("✓ Feedback system imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import feedback system: {e}")
        return False
    
    # Test style loading
    try:
        styles = style_manager.get_complete_stylesheet('light')
        if styles:
            print("✓ Light theme stylesheet loaded successfully")
        else:
            print("✗ Light theme stylesheet is empty")
            return False
    except Exception as e:
        print(f"✗ Failed to load light theme: {e}")
        return False
    
    try:
        styles = style_manager.get_complete_stylesheet('dark')
        if styles:
            print("✓ Dark theme stylesheet loaded successfully")
        else:
            print("✗ Dark theme stylesheet is empty")
            return False
    except Exception as e:
        print(f"✗ Failed to load dark theme: {e}")
        return False
    
    print("\n✓ All UI revamp tests passed!")
    return True


def main():
    """Main function"""
    # Run tests first
    if not run_ui_tests():
        print("Tests failed, exiting...")
        return 1
    
    # Create application
    app = QApplication(sys.argv)
    
    # Setup accessibility
    from ui.accessibility import setup_application_accessibility
    accessibility_manager = setup_application_accessibility(app)
    
    # Create and show test window
    window = UITestWindow()
    window.show()
    
    print("\nUI Test Window opened. Test the following:")
    print("1. Click buttons to test interactions")
    print("2. Hover over elements to see hover effects")
    print("3. Try the theme toggle button")
    print("4. Check responsive behavior by resizing window")
    print("5. Test keyboard navigation with Tab key")
    print("\nPress Ctrl+C or close window to exit.")
    
    # Run application
    try:
        return app.exec_()
    except KeyboardInterrupt:
        print("\nExiting...")
        return 0


if __name__ == "__main__":
    sys.exit(main())