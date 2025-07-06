"""
Navigation utilities for Spoonfed Application
Provides consistent navigation patterns and flow indicators
"""

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from .components import ModernButton


class NavigationManager:
    """Manages navigation state and history"""
    
    def __init__(self):
        self.history = []
        self.current_index = -1
        
    def navigate_to(self, frame_class, params=None):
        """Navigate to a new frame"""
        # Remove any forward history if we're not at the end
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
            
        # Add new navigation entry
        entry = {
            'frame_class': frame_class,
            'params': params or {},
            'timestamp': None  # Could add timestamp for analytics
        }
        self.history.append(entry)
        self.current_index += 1
        
    def can_go_back(self):
        """Check if we can navigate back"""
        return self.current_index > 0
        
    def can_go_forward(self):
        """Check if we can navigate forward"""
        return self.current_index < len(self.history) - 1
        
    def go_back(self):
        """Go back to previous frame"""
        if self.can_go_back():
            self.current_index -= 1
            return self.history[self.current_index]
        return None
        
    def go_forward(self):
        """Go forward to next frame"""
        if self.can_go_forward():
            self.current_index += 1
            return self.history[self.current_index]
        return None
        
    def get_current(self):
        """Get current navigation entry"""
        if 0 <= self.current_index < len(self.history):
            return self.history[self.current_index]
        return None
        
    def clear_history(self):
        """Clear navigation history"""
        self.history.clear()
        self.current_index = -1


class EnhancedNavigationHeader(QFrame):
    """Enhanced navigation header with back/forward buttons and breadcrumbs"""
    
    back_clicked = pyqtSignal()
    forward_clicked = pyqtSignal()
    
    def __init__(self, title="", breadcrumbs=None, show_back=True, show_forward=False, parent=None):
        super().__init__(parent)
        self.title = title
        self.breadcrumbs = breadcrumbs or []
        self.show_back = show_back
        self.show_forward = show_forward
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the navigation header UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Navigation buttons
        nav_buttons = QHBoxLayout()
        
        if self.show_back:
            self.back_button = ModernButton("← Back", variant="tertiary", size="small")
            self.back_button.clicked.connect(self.back_clicked.emit)
            nav_buttons.addWidget(self.back_button)
            
        if self.show_forward:
            self.forward_button = ModernButton("Forward →", variant="tertiary", size="small")
            self.forward_button.clicked.connect(self.forward_clicked.emit)
            nav_buttons.addWidget(self.forward_button)
            
        layout.addLayout(nav_buttons)
        
        # Title and breadcrumbs
        title_section = QVBoxLayout()
        
        # Main title
        if self.title:
            title_label = QLabel(self.title)
            title_label.setProperty("class", "h1")
            title_section.addWidget(title_label)
            
        # Breadcrumbs
        if self.breadcrumbs:
            breadcrumb_layout = QHBoxLayout()
            for i, crumb in enumerate(self.breadcrumbs):
                crumb_label = QLabel(crumb)
                crumb_label.setProperty("class", "caption text-secondary")
                breadcrumb_layout.addWidget(crumb_label)
                
                # Add separator (except for last item)
                if i < len(self.breadcrumbs) - 1:
                    separator = QLabel("/")
                    separator.setProperty("class", "caption text-muted")
                    breadcrumb_layout.addWidget(separator)
                    
            breadcrumb_layout.addStretch()
            title_section.addLayout(breadcrumb_layout)
            
        layout.addLayout(title_section, 1)
        
        # Right side actions (can be extended)
        actions_layout = QHBoxLayout()
        layout.addLayout(actions_layout)
        
    def set_title(self, title):
        """Update the header title"""
        self.title = title
        # Find and update title label
        # Could implement more sophisticated update logic
        
    def set_breadcrumbs(self, breadcrumbs):
        """Update breadcrumbs"""
        self.breadcrumbs = breadcrumbs
        # Could implement dynamic breadcrumb updates
        
    def set_back_enabled(self, enabled):
        """Enable/disable back button"""
        if hasattr(self, 'back_button'):
            self.back_button.setEnabled(enabled)
            
    def set_forward_enabled(self, enabled):
        """Enable/disable forward button"""
        if hasattr(self, 'forward_button'):
            self.forward_button.setEnabled(enabled)


class StepIndicator(QFrame):
    """Step indicator for multi-step processes"""
    
    def __init__(self, steps=None, current_step=0, parent=None):
        super().__init__(parent)
        self.steps = steps or []
        self.current_step = current_step
        self.setup_ui()
        
    def setup_ui(self):
        """Setup step indicator UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.step_widgets = []
        
        for i, step in enumerate(self.steps):
            # Step container
            step_container = QVBoxLayout()
            
            # Step circle
            circle = QLabel(str(i + 1))
            circle.setFixedSize(32, 32)
            circle.setAlignment(Qt.AlignCenter)
            circle.setStyleSheet(self.get_step_style(i))
            step_container.addWidget(circle)
            
            # Step label
            label = QLabel(step)
            label.setProperty("class", "caption")
            label.setAlignment(Qt.AlignCenter)
            step_container.addWidget(label)
            
            # Add to layout
            layout.addLayout(step_container)
            self.step_widgets.append((circle, label))
            
            # Add connector line (except for last step)
            if i < len(self.steps) - 1:
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setFixedHeight(2)
                line.setStyleSheet(self.get_line_style(i))
                # Position line between steps
                layout.addWidget(line, 1)
                
    def get_step_style(self, step_index):
        """Get style for a step circle"""
        if step_index < self.current_step:
            # Completed step
            return """
                QLabel {
                    background-color: #28A745;
                    border-radius: 16px;
                    color: white;
                    font-weight: bold;
                }
            """
        elif step_index == self.current_step:
            # Current step
            return """
                QLabel {
                    background-color: #4A90E2;
                    border-radius: 16px;
                    color: white;
                    font-weight: bold;
                }
            """
        else:
            # Future step
            return """
                QLabel {
                    background-color: #E9ECEF;
                    border: 2px solid #CED4DA;
                    border-radius: 16px;
                    color: #6C757D;
                    font-weight: bold;
                }
            """
            
    def get_line_style(self, step_index):
        """Get style for connector line"""
        if step_index < self.current_step:
            return "background-color: #28A745;"
        else:
            return "background-color: #E9ECEF;"
            
    def set_current_step(self, step):
        """Update current step"""
        self.current_step = step
        self.update_styles()
        
    def update_styles(self):
        """Update step styles"""
        for i, (circle, label) in enumerate(self.step_widgets):
            circle.setStyleSheet(self.get_step_style(i))


class PageTransition:
    """Handles page transitions between frames"""
    
    @staticmethod
    def fade_transition(old_frame, new_frame, duration=300):
        """Perform fade transition between frames"""
        from .animations import animation_manager
        
        # Fade out old frame
        if old_frame:
            animation_manager.fade_out(old_frame, duration=duration//2)
            
        # Fade in new frame
        if new_frame:
            animation_manager.fade_in(new_frame, duration=duration//2)
            
    @staticmethod
    def slide_transition(old_frame, new_frame, direction="left", duration=300):
        """Perform slide transition between frames"""
        from .animations import animation_manager
        
        if direction == "left":
            if old_frame:
                animation_manager.slide_out_to_right(old_frame, duration=duration)
            if new_frame:
                animation_manager.slide_in_from_left(new_frame, duration=duration)
        elif direction == "right":
            if old_frame:
                animation_manager.slide_out_to_left(old_frame, duration=duration)
            if new_frame:
                animation_manager.slide_in_from_right(new_frame, duration=duration)


# Global navigation manager instance
nav_manager = NavigationManager()