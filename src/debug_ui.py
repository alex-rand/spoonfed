#!/usr/bin/env python3
"""
Debug script to identify UI revamp issues
"""

import sys
import os
import traceback

print("=== Spoonfed UI Debug Script ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# Test basic PyQt5 import
try:
    from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
    from PyQt5.QtCore import Qt
    print("✓ PyQt5 basic imports successful")
except Exception as e:
    print(f"✗ PyQt5 import failed: {e}")
    sys.exit(1)

# Test if we can create a basic app
try:
    app = QApplication(sys.argv)
    print("✓ QApplication created successfully")
except Exception as e:
    print(f"✗ QApplication creation failed: {e}")
    sys.exit(1)

# Test our UI module imports
print("\n--- Testing UI module imports ---")

try:
    from ui.style_manager import StyleManager
    print("✓ StyleManager imported")
except Exception as e:
    print(f"✗ StyleManager import failed: {e}")
    traceback.print_exc()

try:
    from ui.components import ModernButton
    print("✓ ModernButton imported")
except Exception as e:
    print(f"✗ ModernButton import failed: {e}")
    traceback.print_exc()

try:
    from ui.animations import animation_manager
    print("✓ animation_manager imported")
except Exception as e:
    print(f"✗ animation_manager import failed: {e}")
    traceback.print_exc()

# Test style file loading
print("\n--- Testing style file loading ---")

styles_dir = "styles"
if os.path.exists(styles_dir):
    print(f"✓ Styles directory exists: {styles_dir}")
    
    style_files = ["base.qss", "components.qss", "theme_light.qss"]
    for file in style_files:
        path = os.path.join(styles_dir, file)
        if os.path.exists(path):
            print(f"✓ {file} exists")
            try:
                with open(path, 'r') as f:
                    content = f.read()
                    print(f"  - Size: {len(content)} characters")
            except Exception as e:
                print(f"  - Read error: {e}")
        else:
            print(f"✗ {file} missing")
else:
    print(f"✗ Styles directory missing: {styles_dir}")

# Test creating a simple modern widget
print("\n--- Testing widget creation ---")

try:
    # Create a simple test widget
    widget = QWidget()
    layout = QVBoxLayout(widget)
    
    label = QLabel("Test Label")
    layout.addWidget(label)
    
    widget.setWindowTitle("UI Debug Test")
    widget.resize(300, 200)
    widget.show()
    
    print("✓ Basic widget created and shown")
    
    # Test our modern components
    try:
        from ui.components import ModernButton, ModernCard
        
        button = ModernButton("Test Button")
        layout.addWidget(button)
        
        card = ModernCard()
        card_layout = QVBoxLayout(card)
        card_layout.addWidget(QLabel("Test Card"))
        layout.addWidget(card)
        
        print("✓ Modern components created")
        
    except Exception as e:
        print(f"✗ Modern component creation failed: {e}")
        traceback.print_exc()
    
except Exception as e:
    print(f"✗ Widget creation failed: {e}")
    traceback.print_exc()

# Test style manager
print("\n--- Testing style manager ---")

try:
    from ui.style_manager import style_manager
    
    # Test loading styles
    base_styles = style_manager.get_base_styles()
    print(f"✓ Base styles loaded: {len(base_styles)} characters")
    
    component_styles = style_manager.get_component_styles()
    print(f"✓ Component styles loaded: {len(component_styles)} characters")
    
    complete_styles = style_manager.get_complete_stylesheet('light')
    print(f"✓ Complete stylesheet: {len(complete_styles)} characters")
    
    # Try applying theme
    style_manager.apply_theme('light')
    print("✓ Light theme applied")
    
except Exception as e:
    print(f"✗ Style manager test failed: {e}")
    traceback.print_exc()

print("\n=== Debug complete ===")
print("\nTo run the debug window, use: python debug_ui.py --show-window")

if "--show-window" in sys.argv:
    print("Showing debug window...")
    app.exec_()