"""
Simplified UI Components for Spoonfed Application
Working version with proper QSS compatibility
"""

from PyQt5.QtWidgets import (
    QPushButton, QLineEdit, QComboBox, QFrame, QLabel, QVBoxLayout, 
    QHBoxLayout, QWidget, QTreeWidget, QProgressBar, QTextEdit, QPlainTextEdit
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette, QPainter, QPixmap
import os
from pathlib import Path


class ModernButton(QPushButton):
    """Modern styled button with hover effects and variants"""
    
    def __init__(self, text="", variant="primary", size="medium", parent=None):
        super().__init__(text, parent)
        self.variant = variant
        self.size = size
        self.setup_style()
        
    def setup_style(self):
        """Apply styling based on variant and size"""
        # Set accessible name for QSS targeting
        self.setAccessibleName(self.variant)
        
        # Set cursor
        self.setCursor(Qt.PointingHandCursor)
        
        # Set focus policy
        self.setFocusPolicy(Qt.TabFocus)
        
        # Apply size-specific styling
        if self.size == "small":
            self.setAccessibleName(f"{self.variant} small")
        elif self.size == "large":
            self.setAccessibleName(f"{self.variant} large")
        
    def set_variant(self, variant):
        """Change button variant"""
        self.variant = variant
        self.setup_style()
        
    def set_size(self, size):
        """Change button size"""
        self.size = size
        self.setup_style()


class ModernInput(QLineEdit):
    """Modern styled input field with enhanced features"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self.setup_style()
        
    def setup_style(self):
        """Apply modern styling"""
        self.setFocusPolicy(Qt.ClickFocus)
        
    def set_error_state(self, is_error=True):
        """Set error state styling"""
        if is_error:
            self.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #DC3545;
                    background-color: #FDF2F2;
                }
            """)
        else:
            self.setStyleSheet("")
            
    def set_success_state(self, is_success=True):
        """Set success state styling"""
        if is_success:
            self.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #28A745;
                    background-color: #F2FDF5;
                }
            """)
        else:
            self.setStyleSheet("")


class ModernComboBox(QComboBox):
    """Modern styled combo box with enhanced features"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_style()
        
    def setup_style(self):
        """Apply modern styling"""
        self.setFocusPolicy(Qt.ClickFocus)


class ModernCard(QFrame):
    """Modern card component with shadow effect simulation"""
    
    def __init__(self, parent=None, shadow=True):
        super().__init__(parent)
        self.has_shadow = shadow
        self.setup_style()
        
    def setup_style(self):
        """Apply card styling"""
        self.setAccessibleName("card")
        
        # Add a subtle border for shadow effect simulation
        if self.has_shadow:
            self.setStyleSheet("""
                QFrame[accessibleName="card"] {
                    background-color: white;
                    border: 1px solid #E9ECEF;
                    border-radius: 8px;
                    margin: 2px;
                }
            """)


class LoadingSpinner(QLabel):
    """Simplified loading spinner using text animation"""
    
    def __init__(self, size=32, parent=None):
        super().__init__(parent)
        self.size = size
        self.angle = 0
        self.setup_animation()
        
    def setup_animation(self):
        """Setup rotation animation"""
        self.setFixedSize(self.size, self.size)
        self.setText("●")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                color: #4A90E2;
                font-size: {self.size - 8}px;
                font-weight: bold;
            }}
        """)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        
    def start_animation(self):
        """Start the spinning animation"""
        self.timer.start(200)  # Update every 200ms
        
    def stop_animation(self):
        """Stop the spinning animation"""
        self.timer.stop()
        self.setText("●")
        
    def animate(self):
        """Animate the spinner"""
        symbols = ["●", "○", "◐", "◑", "◒", "◓"]
        current_index = symbols.index(self.text()) if self.text() in symbols else 0
        next_index = (current_index + 1) % len(symbols)
        self.setText(symbols[next_index])


class NavigationHeader(QFrame):
    """Simple navigation header with back button and title"""
    
    back_clicked = pyqtSignal()
    
    def __init__(self, title="", show_back=True, parent=None):
        super().__init__(parent)
        self.title = title
        self.show_back = show_back
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the navigation header UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        if self.show_back:
            # Back button
            self.back_btn = ModernButton("← Back", variant="tertiary", size="small")
            self.back_btn.clicked.connect(self.back_clicked.emit)
            layout.addWidget(self.back_btn)
            
        # Title
        if self.title:
            title_label = QLabel(self.title)
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 20px;
                    font-weight: bold;
                    color: #212529;
                    padding: 8px 0px;
                }
            """)
            layout.addWidget(title_label, 1)
        
    def set_title(self, title):
        """Update the title"""
        self.title = title
        # Find and update the title label
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QLabel):
                widget.setText(title)
                break


class ModernTreeWidget(QTreeWidget):
    """Enhanced tree widget with modern styling"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_style()
        
    def setup_style(self):
        """Apply modern styling"""
        self.setAlternatingRowColors(True)
        self.setRootIsDecorated(True)
        self.setItemsExpandable(True)


class ModernProgressBar(QProgressBar):
    """Enhanced progress bar with modern styling"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_style()
        
    def setup_style(self):
        """Apply modern styling"""
        self.setTextVisible(False)


class Breadcrumb(QFrame):
    """Simple breadcrumb navigation component"""
    
    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        self.items = items or []
        self.setup_ui()
        
    def setup_ui(self):
        """Setup breadcrumb UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        for i, item in enumerate(self.items):
            # Item label
            label = QLabel(item)
            label.setStyleSheet("""
                QLabel {
                    color: #6C757D;
                    font-size: 12px;
                }
            """)
            layout.addWidget(label)
            
            # Separator (except for last item)
            if i < len(self.items) - 1:
                separator = QLabel("/")
                separator.setStyleSheet("""
                    QLabel {
                        color: #ADB5BD;
                        font-size: 12px;
                        margin: 0px 8px;
                    }
                """)
                layout.addWidget(separator)
                
        layout.addStretch()
        
    def set_items(self, items):
        """Update breadcrumb items"""
        self.items = items
        # Clear existing widgets
        while self.layout().count():
            child = self.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        # Recreate UI
        self.setup_ui()


# Simple spacing utility
class SpacingManager:
    """Simple spacing manager"""
    
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 16,
        'lg': 24,
        'xl': 32,
        'xxl': 48
    }
    
    @classmethod
    def get(cls, size):
        """Get spacing value by size name"""
        return cls.SPACING.get(size, cls.SPACING['md'])
        
    @classmethod
    def apply_margins(cls, widget, top=None, right=None, bottom=None, left=None):
        """Apply consistent margins to widget"""
        if isinstance(top, str):
            top = cls.get(top)
        if isinstance(right, str):
            right = cls.get(right)
        if isinstance(bottom, str):
            bottom = cls.get(bottom)
        if isinstance(left, str):
            left = cls.get(left)
            
        # Default values
        top = top if top is not None else 0
        right = right if right is not None else top
        bottom = bottom if bottom is not None else top
        left = left if left is not None else right
        
        widget.setContentsMargins(left, top, right, bottom)
        
    @classmethod
    def apply_spacing(cls, layout, spacing):
        """Apply consistent spacing to layout"""
        if isinstance(spacing, str):
            spacing = cls.get(spacing)
        layout.setSpacing(spacing)


# Simple notification function
def show_success_notification(parent, message, duration=3000):
    """Show a simple success notification"""
    print(f"SUCCESS: {message}")  # For now, just print to console
    # In a real implementation, this would create a toast notification


def show_error_notification(parent, message, duration=5000):
    """Show a simple error notification"""
    print(f"ERROR: {message}")  # For now, just print to console