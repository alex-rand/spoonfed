"""
Accessibility utilities for Spoonfed Application
Provides keyboard navigation, screen reader support, and accessibility enhancements
"""

from PyQt5.QtWidgets import QWidget, QFrame, QApplication, QToolTip
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QKeySequence, QFontMetrics, QFont, QPalette
import math


class AccessibilityManager(QObject):
    """Manages accessibility features across the application"""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.high_contrast_mode = False
        self.large_text_mode = False
        self.keyboard_navigation_enabled = True
        self.screen_reader_mode = False
        self.focus_indicator_enabled = True
        
        self.setup_accessibility()
        
    def setup_accessibility(self):
        """Setup accessibility features"""
        # Set application properties for accessibility
        self.app.setAttribute(Qt.AA_SynthesizeMouseForUnhandledTabletEvents, True)
        
        # Enable keyboard navigation by default
        self.enable_keyboard_navigation()
        
    def toggle_high_contrast(self):
        """Toggle high contrast mode"""
        self.high_contrast_mode = not self.high_contrast_mode
        self.apply_high_contrast()
        
    def apply_high_contrast(self):
        """Apply high contrast styling"""
        if self.high_contrast_mode:
            high_contrast_style = """
                * {
                    background-color: black;
                    color: white;
                    border-color: white;
                }
                
                QPushButton {
                    background-color: #000080;
                    color: white;
                    border: 2px solid white;
                }
                
                QPushButton:hover {
                    background-color: #0000FF;
                }
                
                QPushButton:focus {
                    border: 3px solid yellow;
                }
                
                QLineEdit, QTextEdit, QComboBox {
                    background-color: white;
                    color: black;
                    border: 2px solid black;
                }
                
                QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                    border: 3px solid yellow;
                }
            """
            self.app.setStyleSheet(high_contrast_style)
        else:
            # Reset to normal theme
            from .style_manager import style_manager
            style_manager.refresh_styles()
            
    def toggle_large_text(self):
        """Toggle large text mode"""
        self.large_text_mode = not self.large_text_mode
        self.apply_text_scaling()
        
    def apply_text_scaling(self, scale_factor=None):
        """Apply text scaling"""
        if scale_factor is None:
            scale_factor = 1.25 if self.large_text_mode else 1.0
            
        font = self.app.font()
        base_size = 14  # Base font size
        new_size = int(base_size * scale_factor)
        font.setPointSize(new_size)
        self.app.setFont(font)
        
    def enable_keyboard_navigation(self):
        """Enable enhanced keyboard navigation"""
        self.keyboard_navigation_enabled = True
        
        # Install application-wide event filter for keyboard navigation
        self.app.installEventFilter(KeyboardNavigationFilter())
        
    def set_screen_reader_mode(self, enabled):
        """Enable/disable screen reader optimizations"""
        self.screen_reader_mode = enabled
        
        if enabled:
            # Disable animations that might interfere with screen readers
            self.app.setEffectEnabled(Qt.UI_AnimateMenu, False)
            self.app.setEffectEnabled(Qt.UI_AnimateCombo, False)
            self.app.setEffectEnabled(Qt.UI_AnimateTooltip, False)
        else:
            # Re-enable animations
            self.app.setEffectEnabled(Qt.UI_AnimateMenu, True)
            self.app.setEffectEnabled(Qt.UI_AnimateCombo, True)
            self.app.setEffectEnabled(Qt.UI_AnimateTooltip, True)
            
    def announce_to_screen_reader(self, text):
        """Announce text to screen reader"""
        if self.screen_reader_mode:
            # Use tooltip as a way to communicate with screen readers
            # This is a simple approach; more sophisticated solutions would
            # integrate with platform-specific accessibility APIs
            QToolTip.showText(QApplication.activeWindow().pos(), text, 
                            QApplication.activeWindow(), QApplication.activeWindow().rect(), 100)


class KeyboardNavigationFilter(QObject):
    """Event filter for enhanced keyboard navigation"""
    
    def eventFilter(self, obj, event):
        """Filter events for keyboard navigation"""
        if event.type() == event.KeyPress:
            # Handle special keyboard shortcuts
            if event.key() == Qt.Key_F6:
                # Cycle through main areas
                self.cycle_focus_areas(obj)
                return True
            elif event.modifiers() == Qt.AltModifier and event.key() == Qt.Key_Tab:
                # Alternative tab navigation
                self.alternative_tab_navigation(obj)
                return True
                
        return super().eventFilter(obj, event)
        
    def cycle_focus_areas(self, widget):
        """Cycle focus through main application areas"""
        # Find the main window
        main_window = widget
        while main_window.parent():
            main_window = main_window.parent()
            
        # Define focus areas (customize based on your app structure)
        focus_areas = [
            'navigation',
            'content',
            'sidebar',
            'footer'
        ]
        
        # Implementation would depend on specific app structure
        pass
        
    def alternative_tab_navigation(self, widget):
        """Provide alternative tab navigation"""
        # Move focus to next focusable widget in reverse order
        QApplication.focusWidget().nextInFocusChain().setFocus(Qt.TabFocusReason)


class FocusIndicator(QFrame):
    """Enhanced focus indicator for better visibility"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.target_widget = None
        self.setup_indicator()
        
    def setup_indicator(self):
        """Setup focus indicator appearance"""
        self.setStyleSheet("""
            QFrame {
                border: 3px solid #4A90E2;
                border-radius: 4px;
                background-color: transparent;
                pointer-events: none;
            }
        """)
        self.hide()
        
    def show_for_widget(self, widget):
        """Show focus indicator for specific widget"""
        self.target_widget = widget
        
        if widget and widget.isVisible():
            # Position indicator around the widget
            widget_rect = widget.geometry()
            self.setGeometry(
                widget_rect.x() - 3,
                widget_rect.y() - 3,
                widget_rect.width() + 6,
                widget_rect.height() + 6
            )
            self.show()
            self.raise_()
        else:
            self.hide()
            
    def hide_indicator(self):
        """Hide focus indicator"""
        self.hide()
        self.target_widget = None


class AccessibleWidget(QWidget):
    """Base class for accessible widgets"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_accessibility()
        
    def setup_accessibility(self):
        """Setup accessibility features for this widget"""
        # Enable focus by tab
        self.setFocusPolicy(Qt.TabFocus)
        
        # Set up accessible name and description
        self.update_accessibility_info()
        
    def update_accessibility_info(self):
        """Update accessibility information"""
        # Override in subclasses to provide specific accessibility info
        pass
        
    def set_accessible_name(self, name):
        """Set accessible name for screen readers"""
        self.setAccessibleName(name)
        
    def set_accessible_description(self, description):
        """Set accessible description for screen readers"""
        self.setAccessibleDescription(description)
        
    def announce_change(self, message):
        """Announce changes to screen readers"""
        # Get accessibility manager
        app = QApplication.instance()
        if hasattr(app, 'accessibility_manager'):
            app.accessibility_manager.announce_to_screen_reader(message)


class KeyboardShortcuts:
    """Manages keyboard shortcuts for accessibility"""
    
    SHORTCUTS = {
        # Navigation shortcuts
        'next_tab': 'Tab',
        'previous_tab': 'Shift+Tab',
        'next_area': 'F6',
        'previous_area': 'Shift+F6',
        
        # Action shortcuts
        'activate': 'Return',
        'activate_alt': 'Space',
        'cancel': 'Escape',
        'help': 'F1',
        
        # Application shortcuts
        'new': 'Ctrl+N',
        'open': 'Ctrl+O',
        'save': 'Ctrl+S',
        'quit': 'Ctrl+Q',
        
        # Accessibility shortcuts
        'high_contrast': 'Ctrl+Shift+H',
        'large_text': 'Ctrl+Shift+T',
        'focus_mode': 'Ctrl+Shift+F'
    }
    
    @classmethod
    def get_shortcut(cls, action):
        """Get keyboard shortcut for action"""
        return cls.SHORTCUTS.get(action, '')
        
    @classmethod
    def format_shortcut(cls, shortcut):
        """Format shortcut for display"""
        if not shortcut:
            return ''
            
        # Convert to user-friendly format
        shortcut = shortcut.replace('Ctrl+', '⌘' if QApplication.instance().platformName() == 'cocoa' else 'Ctrl+')
        shortcut = shortcut.replace('Shift+', '⇧')
        shortcut = shortcut.replace('Alt+', '⌥' if QApplication.instance().platformName() == 'cocoa' else 'Alt+')
        
        return shortcut


class ColorContrastChecker:
    """Utility to check color contrast for accessibility"""
    
    @staticmethod
    def get_luminance(color):
        """Calculate relative luminance of a color"""
        # Convert to RGB values between 0 and 1
        r, g, b = color.red() / 255.0, color.green() / 255.0, color.blue() / 255.0
        
        # Apply gamma correction
        def gamma_correct(c):
            if c <= 0.03928:
                return c / 12.92
            else:
                return math.pow((c + 0.055) / 1.055, 2.4)
                
        r = gamma_correct(r)
        g = gamma_correct(g)
        b = gamma_correct(b)
        
        # Calculate luminance
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
    @staticmethod
    def get_contrast_ratio(color1, color2):
        """Calculate contrast ratio between two colors"""
        lum1 = ColorContrastChecker.get_luminance(color1)
        lum2 = ColorContrastChecker.get_luminance(color2)
        
        # Ensure lighter color is in numerator
        if lum1 < lum2:
            lum1, lum2 = lum2, lum1
            
        return (lum1 + 0.05) / (lum2 + 0.05)
        
    @staticmethod
    def meets_wcag_aa(contrast_ratio, large_text=False):
        """Check if contrast ratio meets WCAG AA standards"""
        threshold = 3.0 if large_text else 4.5
        return contrast_ratio >= threshold
        
    @staticmethod
    def meets_wcag_aaa(contrast_ratio, large_text=False):
        """Check if contrast ratio meets WCAG AAA standards"""
        threshold = 4.5 if large_text else 7.0
        return contrast_ratio >= threshold


class MotionReducedChecker:
    """Check for reduced motion preferences"""
    
    @staticmethod
    def prefers_reduced_motion():
        """Check if user prefers reduced motion"""
        # This would ideally check system preferences
        # For now, we'll provide a way to set this programmatically
        app = QApplication.instance()
        return getattr(app, '_prefers_reduced_motion', False)
        
    @staticmethod
    def set_reduced_motion_preference(reduced):
        """Set reduced motion preference"""
        app = QApplication.instance()
        app._prefers_reduced_motion = reduced


def make_accessible(widget, name=None, description=None, role=None):
    """Make any widget more accessible"""
    if name:
        widget.setAccessibleName(name)
    if description:
        widget.setAccessibleDescription(description)
        
    # Ensure widget can receive focus if it's interactive
    if hasattr(widget, 'clicked') or hasattr(widget, 'textChanged'):
        widget.setFocusPolicy(Qt.TabFocus)
        
    # Add keyboard support for clickable widgets
    if hasattr(widget, 'clicked'):
        def handle_key_press(event):
            if event.key() in (Qt.Key_Return, Qt.Key_Space):
                widget.clicked.emit()
                event.accept()
            else:
                widget.__class__.keyPressEvent(widget, event)
        widget.keyPressEvent = handle_key_press
        
    return widget


def setup_application_accessibility(app):
    """Setup accessibility features for the entire application"""
    # Create accessibility manager
    accessibility_manager = AccessibilityManager(app)
    app.accessibility_manager = accessibility_manager
    
    # Set application attributes for accessibility
    app.setAttribute(Qt.AA_SynthesizeTouchForUnhandledMouseEvents, True)
    app.setAttribute(Qt.AA_SynthesizeMouseForUnhandledTouchEvents, True)
    
    # Setup global keyboard shortcuts for accessibility
    def toggle_high_contrast():
        accessibility_manager.toggle_high_contrast()
        
    def toggle_large_text():
        accessibility_manager.toggle_large_text()
        
    # These would be connected to actual QShortcut objects in practice
    app.toggle_high_contrast = toggle_high_contrast
    app.toggle_large_text = toggle_large_text
    
    return accessibility_manager


# Helper functions
def announce(text, widget=None):
    """Announce text to screen reader"""
    app = QApplication.instance()
    if hasattr(app, 'accessibility_manager'):
        app.accessibility_manager.announce_to_screen_reader(text)


def check_color_accessibility(foreground_color, background_color, large_text=False):
    """Check if color combination is accessible"""
    contrast_ratio = ColorContrastChecker.get_contrast_ratio(foreground_color, background_color)
    
    return {
        'contrast_ratio': contrast_ratio,
        'wcag_aa': ColorContrastChecker.meets_wcag_aa(contrast_ratio, large_text),
        'wcag_aaa': ColorContrastChecker.meets_wcag_aaa(contrast_ratio, large_text)
    }