"""
Feedback and notification system for Spoonfed Application
Provides consistent visual feedback, loading states, and notifications
"""

from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget,
    QGraphicsOpacityEffect, QApplication
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QRect
from PyQt5.QtGui import QColor, QPainter, QBrush, QPen
from .components import ModernButton, LoadingSpinner
import time


class NotificationManager:
    """Manages application-wide notifications"""
    
    def __init__(self, parent_widget):
        self.parent_widget = parent_widget
        self.active_notifications = []
        self.notification_spacing = 8
        self.notification_width = 400
        
    def show_success(self, message, duration=3000):
        """Show a success notification"""
        return self.show_notification(message, "success", duration)
        
    def show_error(self, message, duration=5000):
        """Show an error notification"""
        return self.show_notification(message, "error", duration)
        
    def show_warning(self, message, duration=4000):
        """Show a warning notification"""
        return self.show_notification(message, "warning", duration)
        
    def show_info(self, message, duration=3000):
        """Show an info notification"""
        return self.show_notification(message, "info", duration)
        
    def show_notification(self, message, type="info", duration=3000):
        """Show a notification of specified type"""
        notification = ToastNotification(message, type, duration, self.parent_widget)
        notification.closed.connect(lambda: self.remove_notification(notification))
        
        # Position notification
        self.position_notification(notification)
        
        # Add to active notifications
        self.active_notifications.append(notification)
        
        # Show with animation
        notification.show_with_animation()
        
        return notification
        
    def position_notification(self, notification):
        """Position notification in the top-right corner"""
        parent_rect = self.parent_widget.rect()
        
        # Calculate position
        x = parent_rect.width() - self.notification_width - 24
        y = 24 + len(self.active_notifications) * (notification.height() + self.notification_spacing)
        
        notification.setGeometry(x, y, self.notification_width, notification.height())
        
    def remove_notification(self, notification):
        """Remove notification and reposition others"""
        if notification in self.active_notifications:
            self.active_notifications.remove(notification)
            notification.deleteLater()
            
            # Reposition remaining notifications
            self.reposition_notifications()
            
    def reposition_notifications(self):
        """Reposition all notifications after removal"""
        for i, notification in enumerate(self.active_notifications):
            new_y = 24 + i * (notification.height() + self.notification_spacing)
            
            # Animate to new position
            animation = QPropertyAnimation(notification, b"pos")
            animation.setDuration(200)
            animation.setStartValue(notification.pos())
            animation.setEndValue(notification.pos().x(), new_y)
            animation.setEasingCurve(QEasingCurve.OutCubic)
            animation.start()


class ToastNotification(QFrame):
    """Modern toast notification widget"""
    
    closed = pyqtSignal()
    
    def __init__(self, message, type="info", duration=3000, parent=None):
        super().__init__(parent)
        self.message = message
        self.type = type
        self.duration = duration
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the notification UI"""
        self.setFixedSize(400, 80)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        
        # Icon
        icon_label = QLabel()
        icon_label.setFixedSize(24, 24)
        icon_label.setText(self.get_icon())
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"color: {self.get_icon_color()}; font-size: 18px; font-weight: bold;")
        layout.addWidget(icon_label)
        
        # Message
        message_label = QLabel(self.message)
        message_label.setProperty("class", "body")
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: #212529;")
        layout.addWidget(message_label, 1)
        
        # Close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                color: #6C757D;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #212529;
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 12px;
            }
        """)
        close_btn.clicked.connect(self.close_notification)
        layout.addWidget(close_btn)
        
        # Apply type-specific styling
        self.setStyleSheet(self.get_notification_style())
        
    def get_icon(self):
        """Get icon for notification type"""
        icons = {
            "success": "✓",
            "warning": "⚠",
            "error": "✗",
            "info": "ℹ"
        }
        return icons.get(self.type, "ℹ")
        
    def get_icon_color(self):
        """Get icon color for notification type"""
        colors = {
            "success": "#28A745",
            "warning": "#FFC107",
            "error": "#DC3545",
            "info": "#17A2B8"
        }
        return colors.get(self.type, "#17A2B8")
        
    def get_notification_style(self):
        """Get style for notification type"""
        styles = {
            "success": """
                QFrame {
                    background-color: #D4EDDA;
                    border: 1px solid #C3E6CB;
                    border-radius: 8px;
                }
            """,
            "warning": """
                QFrame {
                    background-color: #FFF3CD;
                    border: 1px solid #FFEAA7;
                    border-radius: 8px;
                }
            """,
            "error": """
                QFrame {
                    background-color: #F8D7DA;
                    border: 1px solid #F5C6CB;
                    border-radius: 8px;
                }
            """,
            "info": """
                QFrame {
                    background-color: #D1ECF1;
                    border: 1px solid #BEE5EB;
                    border-radius: 8px;
                }
            """
        }
        return styles.get(self.type, styles["info"])
        
    def show_with_animation(self):
        """Show notification with slide-in animation"""
        self.show()
        
        # Slide in from right
        start_pos = self.pos()
        start_pos.setX(start_pos.x() + self.width())
        end_pos = self.pos()
        
        self.move(start_pos)
        
        self.slide_animation = QPropertyAnimation(self, b"pos")
        self.slide_animation.setDuration(300)
        self.slide_animation.setStartValue(start_pos)
        self.slide_animation.setEndValue(end_pos)
        self.slide_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.slide_animation.start()
        
        # Auto-hide after duration
        if self.duration > 0:
            QTimer.singleShot(self.duration, self.close_notification)
            
    def close_notification(self):
        """Close notification with fade-out animation"""
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation.finished.connect(self.closed.emit)
        self.fade_animation.start()


class LoadingOverlay(QFrame):
    """Loading overlay with spinner and message"""
    
    def __init__(self, parent=None, message="Loading..."):
        super().__init__(parent)
        self.message = message
        self.setup_ui()
        
    def setup_ui(self):
        """Setup loading overlay UI"""
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 0.5);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Loading container
        container = QFrame()
        container.setFixedSize(200, 120)
        container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #E9ECEF;
            }
        """)
        
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignCenter)
        container_layout.setSpacing(16)
        
        # Spinner
        self.spinner = LoadingSpinner(48)
        container_layout.addWidget(self.spinner, alignment=Qt.AlignCenter)
        
        # Message
        message_label = QLabel(self.message)
        message_label.setProperty("class", "body text-secondary")
        message_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(message_label)
        
        layout.addWidget(container, alignment=Qt.AlignCenter)
        
    def show_overlay(self):
        """Show loading overlay"""
        if self.parent():
            self.resize(self.parent().size())
        self.show()
        self.spinner.start_animation()
        
    def hide_overlay(self):
        """Hide loading overlay"""
        self.spinner.stop_animation()
        self.hide()
        
    def set_message(self, message):
        """Update loading message"""
        self.message = message
        # Find and update message label
        for child in self.findChildren(QLabel):
            if child.property("class") == "body text-secondary":
                child.setText(message)
                break


class ProgressDialog(QFrame):
    """Progress dialog with progress bar and cancel button"""
    
    cancelled = pyqtSignal()
    
    def __init__(self, title="Processing...", cancellable=True, parent=None):
        super().__init__(parent)
        self.title = title
        self.cancellable = cancellable
        self.setup_ui()
        
    def setup_ui(self):
        """Setup progress dialog UI"""
        self.setFixedSize(400, 180)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #CED4DA;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setProperty("class", "h2")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Progress info
        self.status_label = QLabel("Initializing...")
        self.status_label.setProperty("class", "body text-secondary")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Progress bar
        from .components import ModernProgressBar
        self.progress_bar = ModernProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)
        
        # Cancel button
        if self.cancellable:
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            
            cancel_button = ModernButton("Cancel", variant="secondary")
            cancel_button.clicked.connect(self.cancelled.emit)
            button_layout.addWidget(cancel_button)
            
            layout.addLayout(button_layout)
            
    def update_progress(self, value, status=""):
        """Update progress value and status"""
        self.progress_bar.setValue(value)
        if status:
            self.status_label.setText(status)
            
    def set_indeterminate(self, indeterminate=True):
        """Set progress bar to indeterminate mode"""
        if indeterminate:
            self.progress_bar.setRange(0, 0)
        else:
            self.progress_bar.setRange(0, 100)


class StatusBar(QFrame):
    """Application status bar with status messages and indicators"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup status bar UI"""
        self.setFixedHeight(32)
        self.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border-top: 1px solid #E9ECEF;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 4, 16, 4)
        
        # Status message
        self.status_label = QLabel("Ready")
        self.status_label.setProperty("class", "caption text-secondary")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Right side indicators
        self.connection_indicator = QLabel("●")
        self.connection_indicator.setProperty("class", "caption")
        self.connection_indicator.setStyleSheet("color: #28A745;")  # Green for connected
        layout.addWidget(self.connection_indicator)
        
        connection_label = QLabel("Connected")
        connection_label.setProperty("class", "caption text-secondary")
        layout.addWidget(connection_label)
        
    def set_status(self, message):
        """Set status message"""
        self.status_label.setText(message)
        
    def set_connection_status(self, connected=True):
        """Set connection status"""
        if connected:
            self.connection_indicator.setStyleSheet("color: #28A745;")  # Green
        else:
            self.connection_indicator.setStyleSheet("color: #DC3545;")  # Red


class InlineValidation:
    """Provides inline validation feedback for form fields"""
    
    @staticmethod
    def show_error(field, message):
        """Show error state on field"""
        field.setStyleSheet("""
            QLineEdit, QTextEdit, QComboBox {
                border: 2px solid #DC3545;
                background-color: #FDF2F2;
            }
        """)
        
        # Add error message if not already present
        error_label = field.parent().findChild(QLabel, "error_label")
        if not error_label:
            error_label = QLabel(message)
            error_label.setObjectName("error_label")
            error_label.setProperty("class", "caption text-error")
            error_label.setStyleSheet("color: #DC3545; margin-top: 4px;")
            
            # Insert after the field
            layout = field.parent().layout()
            if layout:
                field_index = layout.indexOf(field)
                layout.insertWidget(field_index + 1, error_label)
        else:
            error_label.setText(message)
            
    @staticmethod
    def show_success(field, message=""):
        """Show success state on field"""
        field.setStyleSheet("""
            QLineEdit, QTextEdit, QComboBox {
                border: 2px solid #28A745;
                background-color: #F2FDF5;
            }
        """)
        
        # Remove error message
        InlineValidation.clear_validation(field)
        
        # Add success message if provided
        if message:
            success_label = QLabel(message)
            success_label.setObjectName("success_label")
            success_label.setProperty("class", "caption text-success")
            success_label.setStyleSheet("color: #28A745; margin-top: 4px;")
            
            layout = field.parent().layout()
            if layout:
                field_index = layout.indexOf(field)
                layout.insertWidget(field_index + 1, success_label)
                
    @staticmethod
    def clear_validation(field):
        """Clear validation state"""
        field.setStyleSheet("")
        
        # Remove validation messages
        parent = field.parent()
        if parent:
            error_label = parent.findChild(QLabel, "error_label")
            if error_label:
                error_label.deleteLater()
                
            success_label = parent.findChild(QLabel, "success_label")
            if success_label:
                success_label.deleteLater()


# Helper functions for easy access
def show_success_notification(parent, message, duration=3000):
    """Show success notification"""
    manager = getattr(parent, '_notification_manager', None)
    if not manager:
        manager = NotificationManager(parent)
        parent._notification_manager = manager
    return manager.show_success(message, duration)

def show_error_notification(parent, message, duration=5000):
    """Show error notification"""
    manager = getattr(parent, '_notification_manager', None)
    if not manager:
        manager = NotificationManager(parent)
        parent._notification_manager = manager
    return manager.show_error(message, duration)

def show_loading_overlay(parent, message="Loading..."):
    """Show loading overlay"""
    overlay = getattr(parent, '_loading_overlay', None)
    if not overlay:
        overlay = LoadingOverlay(parent, message)
        parent._loading_overlay = overlay
    overlay.set_message(message)
    overlay.show_overlay()
    return overlay

def hide_loading_overlay(parent):
    """Hide loading overlay"""
    overlay = getattr(parent, '_loading_overlay', None)
    if overlay:
        overlay.hide_overlay()