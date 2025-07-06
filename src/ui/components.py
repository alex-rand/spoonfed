"""
Enhanced UI Components for Spoonfed Application
Modern, consistent components with proper styling
"""

from PyQt5.QtWidgets import (
    QPushButton, QLineEdit, QComboBox, QFrame, QLabel, QVBoxLayout, 
    QHBoxLayout, QWidget, QGraphicsDropShadowEffect, QTreeWidget,
    QProgressBar, QTextEdit, QPlainTextEdit
)
from PyQt5.QtCore import Qt, QTimer, QRect, QPropertyAnimation, QEasingCurve, pyqtSignal
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
        # Set base properties
        self.setProperty("class", self.variant)
        if self.size != "medium":
            self.setProperty("class", f"{self.variant} {self.size}")
        
        # Set cursor
        self.setCursor(Qt.PointingHandCursor)
        
        # Set focus policy
        self.setFocusPolicy(Qt.TabFocus)
        
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
        
    def add_separator(self):
        """Add a separator item"""
        self.addItem("─" * 20)
        self.setItemData(self.count() - 1, 0, Qt.UserRole - 1)


class ModernCard(QFrame):
    """Modern card component with shadow and hover effects"""
    
    def __init__(self, parent=None, shadow=True):
        super().__init__(parent)
        self.has_shadow = shadow
        self.setup_style()
        
    def setup_style(self):
        """Apply card styling"""
        self.setProperty("class", "card")
        
        if self.has_shadow:
            # Add drop shadow effect
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(10)
            shadow.setColor(QColor(0, 0, 0, 50))
            shadow.setOffset(0, 2)
            self.setGraphicsEffect(shadow)
            
    def set_hover_effect(self, enabled=True):
        """Enable/disable hover effect"""
        if enabled:
            self.setProperty("class", "card card-hover")
        else:
            self.setProperty("class", "card")


class LoadingSpinner(QLabel):
    """Animated loading spinner"""
    
    def __init__(self, size=32, parent=None):
        super().__init__(parent)
        self.size = size
        self.angle = 0
        self.setup_animation()
        
    def setup_animation(self):
        """Setup rotation animation"""
        self.setFixedSize(self.size, self.size)
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate)
        
    def start_animation(self):
        """Start the spinning animation"""
        self.timer.start(50)  # Update every 50ms
        
    def stop_animation(self):
        """Stop the spinning animation"""
        self.timer.stop()
        self.angle = 0
        self.update()
        
    def rotate(self):
        """Rotate the spinner"""
        self.angle = (self.angle + 10) % 360
        self.update()
        
    def paintEvent(self, event):
        """Paint the spinner"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw loading spinner
        painter.translate(self.size // 2, self.size // 2)
        painter.rotate(self.angle)
        
        # Draw spinner arcs
        painter.setPen(QColor(74, 144, 226, 100))
        painter.drawArc(-self.size // 4, -self.size // 4, self.size // 2, self.size // 2, 0, 270 * 16)
        
        painter.setPen(QColor(74, 144, 226, 255))
        painter.drawArc(-self.size // 4, -self.size // 4, self.size // 2, self.size // 2, 0, 90 * 16)


class ProgressIndicator(QFrame):
    """Progress indicator with steps"""
    
    def __init__(self, steps=[], current_step=0, parent=None):
        super().__init__(parent)
        self.steps = steps
        self.current_step = current_step
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the progress indicator UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        for i, step in enumerate(self.steps):
            # Step circle
            circle = QLabel()
            circle.setFixedSize(32, 32)
            circle.setAlignment(Qt.AlignCenter)
            circle.setStyleSheet(self.get_step_style(i))
            circle.setText(str(i + 1))
            layout.addWidget(circle)
            
            # Step label
            label = QLabel(step)
            label.setProperty("class", "caption")
            layout.addWidget(label)
            
            # Add connector line (except for last step)
            if i < len(self.steps) - 1:
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setProperty("class", "divider")
                layout.addWidget(line)
                
    def get_step_style(self, step_index):
        """Get style for a step based on its status"""
        if step_index < self.current_step:
            return """
                QLabel {
                    background-color: #28A745;
                    border-radius: 16px;
                    color: white;
                    font-weight: bold;
                }
            """
        elif step_index == self.current_step:
            return """
                QLabel {
                    background-color: #4A90E2;
                    border-radius: 16px;
                    color: white;
                    font-weight: bold;
                }
            """
        else:
            return """
                QLabel {
                    background-color: #E9ECEF;
                    border-radius: 16px;
                    color: #6C757D;
                    font-weight: bold;
                }
            """
            
    def set_current_step(self, step):
        """Update the current step"""
        self.current_step = step
        # Recreate UI
        self.setup_ui()


class ToastNotification(QFrame):
    """Toast notification widget"""
    
    closed = pyqtSignal()
    
    def __init__(self, message, type="info", duration=3000, parent=None):
        super().__init__(parent)
        self.message = message
        self.type = type
        self.duration = duration
        self.setup_ui()
        self.setup_animation()
        
    def setup_ui(self):
        """Setup the toast UI"""
        layout = QHBoxLayout(self)
        
        # Icon
        icon = QLabel()
        icon.setFixedSize(24, 24)
        icon.setText(self.get_icon())
        layout.addWidget(icon)
        
        # Message
        message_label = QLabel(self.message)
        message_label.setProperty("class", "body")
        layout.addWidget(message_label, 1)
        
        # Close button
        close_btn = ModernButton("×", variant="tertiary", size="small")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        # Apply styling
        self.setProperty("class", f"toast toast-{self.type}")
        
    def get_icon(self):
        """Get icon for notification type"""
        icons = {
            "success": "✓",
            "warning": "⚠",
            "error": "✗",
            "info": "ℹ"
        }
        return icons.get(self.type, "ℹ")
        
    def setup_animation(self):
        """Setup slide-in animation"""
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
    def show_notification(self):
        """Show the notification with animation"""
        self.show()
        
        # Auto-hide after duration
        QTimer.singleShot(self.duration, self.close)
        
    def close(self):
        """Close the notification"""
        self.closed.emit()
        self.hide()


class NavigationHeader(QFrame):
    """Navigation header with back button and title"""
    
    back_clicked = pyqtSignal()
    
    def __init__(self, title="", show_back=True, parent=None):
        super().__init__(parent)
        self.title = title
        self.show_back = show_back
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the navigation header UI"""
        layout = QHBoxLayout(self)
        
        if self.show_back:
            # Back button
            back_btn = ModernButton("← Back", variant="tertiary", size="small")
            back_btn.clicked.connect(self.back_clicked.emit)
            layout.addWidget(back_btn)
            
        # Title
        title_label = QLabel(self.title)
        title_label.setProperty("class", "h2")
        layout.addWidget(title_label, 1)
        
        # Apply styling
        self.setProperty("class", "nav-header")
        
    def set_title(self, title):
        """Update the title"""
        self.title = title
        # Find and update the title label
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QLabel) and widget.property("class") == "h2":
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
        
        # Custom styling
        self.setStyleSheet("""
            QTreeWidget {
                background-color: white;
                border: 1px solid #E9ECEF;
                border-radius: 8px;
                selection-background-color: #4A90E2;
                alternate-background-color: #F8F9FA;
            }
            
            QTreeWidget::item {
                padding: 8px;
                border-bottom: 1px solid #F1F3F4;
            }
            
            QTreeWidget::item:hover {
                background-color: #F8F9FA;
            }
            
            QTreeWidget::item:selected {
                background-color: #4A90E2;
                color: white;
            }
        """)


class ModernProgressBar(QProgressBar):
    """Enhanced progress bar with modern styling"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_style()
        
    def setup_style(self):
        """Apply modern styling"""
        self.setTextVisible(False)
        self.setStyleSheet("""
            QProgressBar {
                background-color: #F1F3F4;
                border: none;
                border-radius: 4px;
                height: 8px;
            }
            
            QProgressBar::chunk {
                background-color: #4A90E2;
                border-radius: 4px;
            }
        """)


class SkeletonLoader(QFrame):
    """Skeleton loader for content placeholders"""
    
    def __init__(self, width=200, height=20, parent=None):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.setup_animation()
        
    def setup_animation(self):
        """Setup shimmer animation"""
        self.setStyleSheet("""
            QFrame {
                background-color: #F1F3F4;
                border-radius: 4px;
            }
        """)
        
        # Shimmer effect will be handled with timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_shimmer)
        self.opacity = 0.3
        self.direction = 1
        
    def start_animation(self):
        """Start the shimmer animation"""
        self.timer.start(100)
        
    def stop_animation(self):
        """Stop the shimmer animation"""
        self.timer.stop()
        
    def update_shimmer(self):
        """Update shimmer effect"""
        self.opacity += 0.1 * self.direction
        if self.opacity >= 1.0:
            self.direction = -1
        elif self.opacity <= 0.3:
            self.direction = 1
            
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(241, 243, 244, {self.opacity});
                border-radius: 4px;
            }}
        """)


class Breadcrumb(QFrame):
    """Breadcrumb navigation component"""
    
    def __init__(self, items=[], parent=None):
        super().__init__(parent)
        self.items = items
        self.setup_ui()
        
    def setup_ui(self):
        """Setup breadcrumb UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        for i, item in enumerate(self.items):
            # Item label
            label = QLabel(item)
            label.setProperty("class", "caption")
            if i == len(self.items) - 1:
                label.setProperty("class", "caption text-primary")
            layout.addWidget(label)
            
            # Separator (except for last item)
            if i < len(self.items) - 1:
                separator = QLabel("/")
                separator.setProperty("class", "caption text-muted")
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