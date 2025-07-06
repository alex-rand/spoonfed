"""
Responsive layout utilities for Spoonfed Application
Provides responsive design patterns and consistent spacing
"""

from PyQt5.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea,
    QSizePolicy, QApplication
)
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt5.QtGui import QResizeEvent


class ResponsiveContainer(QFrame):
    """Container that adapts layout based on available space"""
    
    layout_changed = pyqtSignal(str)  # Emits: "mobile", "tablet", "desktop"
    
    # Breakpoints
    MOBILE_MAX = 767
    TABLET_MAX = 1023
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_layout_mode = "desktop"
        self.mobile_layout = None
        self.tablet_layout = None
        self.desktop_layout = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup responsive container"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Content area
        self.content_area = QFrame()
        self.main_layout.addWidget(self.content_area)
        
    def set_layouts(self, mobile=None, tablet=None, desktop=None):
        """Set layout configurations for different screen sizes"""
        self.mobile_layout = mobile
        self.tablet_layout = tablet
        self.desktop_layout = desktop
        self.update_layout()
        
    def resizeEvent(self, event):
        """Handle resize events to update layout"""
        super().resizeEvent(event)
        QTimer.singleShot(0, self.update_layout)  # Defer to avoid recursion
        
    def update_layout(self):
        """Update layout based on current size"""
        width = self.width()
        new_mode = self.get_layout_mode(width)
        
        if new_mode != self.current_layout_mode:
            self.current_layout_mode = new_mode
            self.apply_layout(new_mode)
            self.layout_changed.emit(new_mode)
            
    def get_layout_mode(self, width):
        """Determine layout mode based on width"""
        if width <= self.MOBILE_MAX:
            return "mobile"
        elif width <= self.TABLET_MAX:
            return "tablet"
        else:
            return "desktop"
            
    def apply_layout(self, mode):
        """Apply layout for the specified mode"""
        # Clear existing layout
        if self.content_area.layout():
            old_layout = self.content_area.layout()
            while old_layout.count():
                old_layout.takeAt(0)
            old_layout.deleteLater()
            
        # Apply new layout
        if mode == "mobile" and self.mobile_layout:
            self.content_area.setLayout(self.mobile_layout())
        elif mode == "tablet" and self.tablet_layout:
            self.content_area.setLayout(self.tablet_layout())
        elif mode == "desktop" and self.desktop_layout:
            self.content_area.setLayout(self.desktop_layout())
        else:
            # Fallback to desktop layout
            if self.desktop_layout:
                self.content_area.setLayout(self.desktop_layout())


class FlexLayout(QHBoxLayout):
    """Flexible layout that wraps items to new lines when needed"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []
        self.wrap_enabled = True
        self.justify_content = "flex-start"  # flex-start, center, flex-end, space-between, space-around
        
    def addWidget(self, widget, stretch=0, alignment=Qt.Alignment()):
        """Add widget to flex layout"""
        super().addWidget(widget, stretch, alignment)
        self.items.append({
            'widget': widget,
            'stretch': stretch,
            'alignment': alignment
        })
        
    def set_wrap(self, wrap):
        """Enable/disable wrapping"""
        self.wrap_enabled = wrap
        
    def set_justify_content(self, justify):
        """Set content justification"""
        self.justify_content = justify


class GridResponsive(QGridLayout):
    """Responsive grid layout that adjusts columns based on screen size"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mobile_columns = 1
        self.tablet_columns = 2
        self.desktop_columns = 3
        self.items = []
        self.current_columns = self.desktop_columns
        
    def set_breakpoints(self, mobile=1, tablet=2, desktop=3):
        """Set number of columns for each breakpoint"""
        self.mobile_columns = mobile
        self.tablet_columns = tablet
        self.desktop_columns = desktop
        
    def addWidget(self, widget, row=None, column=None, rowSpan=1, columnSpan=1, alignment=Qt.Alignment()):
        """Add widget to responsive grid"""
        item = {
            'widget': widget,
            'rowSpan': rowSpan,
            'columnSpan': columnSpan,
            'alignment': alignment
        }
        self.items.append(item)
        self.relayout()
        
    def update_for_width(self, width):
        """Update grid layout for given width"""
        if width <= ResponsiveContainer.MOBILE_MAX:
            new_columns = self.mobile_columns
        elif width <= ResponsiveContainer.TABLET_MAX:
            new_columns = self.tablet_columns
        else:
            new_columns = self.desktop_columns
            
        if new_columns != self.current_columns:
            self.current_columns = new_columns
            self.relayout()
            
    def relayout(self):
        """Relayout items based on current column count"""
        # Clear existing layout
        while self.count():
            self.takeAt(0)
            
        # Add items back with new grid
        for i, item in enumerate(self.items):
            row = i // self.current_columns
            col = i % self.current_columns
            super().addWidget(
                item['widget'], 
                row, col, 
                item['rowSpan'], 
                item['columnSpan'], 
                item['alignment']
            )


class SpacingManager:
    """Manages consistent spacing throughout the application"""
    
    # Spacing scale based on 8px base unit
    SPACING = {
        'xs': 4,    # 0.5 units
        'sm': 8,    # 1 unit
        'md': 16,   # 2 units
        'lg': 24,   # 3 units
        'xl': 32,   # 4 units
        'xxl': 48   # 6 units
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


class ResponsiveCard(QFrame):
    """Card component that adapts to different screen sizes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mobile_padding = SpacingManager.get('md')
        self.desktop_padding = SpacingManager.get('lg')
        self.setup_ui()
        
    def setup_ui(self):
        """Setup responsive card"""
        self.setProperty("class", "card")
        self.layout = QVBoxLayout(self)
        self.update_padding()
        
    def resizeEvent(self, event):
        """Handle resize to update padding"""
        super().resizeEvent(event)
        self.update_padding()
        
    def update_padding(self):
        """Update padding based on screen size"""
        if self.width() <= ResponsiveContainer.MOBILE_MAX:
            padding = self.mobile_padding
        else:
            padding = self.desktop_padding
            
        self.layout.setContentsMargins(padding, padding, padding, padding)


class AdaptiveScrollArea(QScrollArea):
    """Scroll area that shows/hides scrollbars responsively"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup adaptive scroll area"""
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        
        # Start with auto scrollbars
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
    def set_mobile_scrollbars(self, horizontal=Qt.ScrollBarAlwaysOff, vertical=Qt.ScrollBarAsNeeded):
        """Set scrollbar policy for mobile"""
        self.mobile_h_policy = horizontal
        self.mobile_v_policy = vertical
        
    def set_desktop_scrollbars(self, horizontal=Qt.ScrollBarAsNeeded, vertical=Qt.ScrollBarAsNeeded):
        """Set scrollbar policy for desktop"""
        self.desktop_h_policy = horizontal
        self.desktop_v_policy = vertical
        
    def resizeEvent(self, event):
        """Update scrollbar policy on resize"""
        super().resizeEvent(event)
        
        if hasattr(self, 'mobile_h_policy') and hasattr(self, 'desktop_h_policy'):
            if self.width() <= ResponsiveContainer.MOBILE_MAX:
                self.setHorizontalScrollBarPolicy(self.mobile_h_policy)
                self.setVerticalScrollBarPolicy(self.mobile_v_policy)
            else:
                self.setHorizontalScrollBarPolicy(self.desktop_h_policy)
                self.setVerticalScrollBarPolicy(self.desktop_v_policy)


class LayoutBreakpoints:
    """Utility class for managing responsive breakpoints"""
    
    BREAKPOINTS = {
        'xs': 0,
        'sm': 576,
        'md': 768,
        'lg': 992,
        'xl': 1200,
        'xxl': 1400
    }
    
    @classmethod
    def get_current_breakpoint(cls, width):
        """Get current breakpoint name for given width"""
        for name, min_width in reversed(cls.BREAKPOINTS.items()):
            if width >= min_width:
                return name
        return 'xs'
        
    @classmethod
    def is_mobile(cls, width):
        """Check if width is mobile size"""
        return width < cls.BREAKPOINTS['md']
        
    @classmethod
    def is_tablet(cls, width):
        """Check if width is tablet size"""
        return cls.BREAKPOINTS['md'] <= width < cls.BREAKPOINTS['lg']
        
    @classmethod
    def is_desktop(cls, width):
        """Check if width is desktop size"""
        return width >= cls.BREAKPOINTS['lg']


class TwoColumnLayout(QHBoxLayout):
    """Responsive two-column layout that stacks on mobile"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.left_widget = None
        self.right_widget = None
        self.mobile_threshold = ResponsiveContainer.MOBILE_MAX
        self.is_stacked = False
        
    def set_widgets(self, left_widget, right_widget, left_stretch=1, right_stretch=1):
        """Set the two widgets for the layout"""
        self.left_widget = left_widget
        self.right_widget = right_widget
        self.left_stretch = left_stretch
        self.right_stretch = right_stretch
        
        self.addWidget(left_widget, left_stretch)
        self.addWidget(right_widget, right_stretch)
        
    def update_for_width(self, width):
        """Update layout based on width"""
        should_stack = width <= self.mobile_threshold
        
        if should_stack != self.is_stacked:
            self.is_stacked = should_stack
            self.relayout()
            
    def relayout(self):
        """Relayout widgets"""
        if not self.left_widget or not self.right_widget:
            return
            
        # Clear layout
        while self.count():
            self.takeAt(0)
            
        if self.is_stacked:
            # Stack vertically
            vertical_layout = QVBoxLayout()
            vertical_layout.addWidget(self.left_widget)
            vertical_layout.addWidget(self.right_widget)
            self.addLayout(vertical_layout)
        else:
            # Side by side
            self.addWidget(self.left_widget, self.left_stretch)
            self.addWidget(self.right_widget, self.right_stretch)


def create_responsive_form(fields, columns_desktop=2, columns_tablet=1, columns_mobile=1):
    """Create a responsive form layout"""
    container = ResponsiveContainer()
    
    def create_desktop_layout():
        layout = QGridLayout()
        SpacingManager.apply_spacing(layout, 'md')
        
        for i, field in enumerate(fields):
            row = i // columns_desktop
            col = i % columns_desktop
            
            if isinstance(field, dict):
                label = field.get('label')
                widget = field.get('widget')
                if label:
                    label_widget = QLabel(label)
                    layout.addWidget(label_widget, row * 2, col)
                    layout.addWidget(widget, row * 2 + 1, col)
                else:
                    layout.addWidget(widget, row, col)
            else:
                layout.addWidget(field, row, col)
                
        return layout
        
    def create_tablet_layout():
        layout = QGridLayout()
        SpacingManager.apply_spacing(layout, 'md')
        
        for i, field in enumerate(fields):
            row = i // columns_tablet
            col = i % columns_tablet
            
            if isinstance(field, dict):
                label = field.get('label')
                widget = field.get('widget')
                if label:
                    label_widget = QLabel(label)
                    layout.addWidget(label_widget, row * 2, col)
                    layout.addWidget(widget, row * 2 + 1, col)
                else:
                    layout.addWidget(widget, row, col)
            else:
                layout.addWidget(field, row, col)
                
        return layout
        
    def create_mobile_layout():
        layout = QVBoxLayout()
        SpacingManager.apply_spacing(layout, 'sm')
        
        for field in fields:
            if isinstance(field, dict):
                label = field.get('label')
                widget = field.get('widget')
                if label:
                    label_widget = QLabel(label)
                    layout.addWidget(label_widget)
                layout.addWidget(widget)
            else:
                layout.addWidget(field)
                
        return layout
        
    container.set_layouts(
        mobile=create_mobile_layout,
        tablet=create_tablet_layout,
        desktop=create_desktop_layout
    )
    
    return container


# Utility functions
def make_responsive(widget, mobile_callback=None, tablet_callback=None, desktop_callback=None):
    """Make any widget responsive by providing callbacks for different screen sizes"""
    def on_resize():
        width = widget.width() if hasattr(widget, 'width') else QApplication.instance().primaryScreen().size().width()
        
        if width <= ResponsiveContainer.MOBILE_MAX and mobile_callback:
            mobile_callback(widget)
        elif width <= ResponsiveContainer.TABLET_MAX and tablet_callback:
            tablet_callback(widget)
        elif desktop_callback:
            desktop_callback(widget)
            
    # Connect to resize events if possible
    if hasattr(widget, 'resizeEvent'):
        original_resize = widget.resizeEvent
        def new_resize(event):
            original_resize(event)
            QTimer.singleShot(0, on_resize)
        widget.resizeEvent = new_resize
        
    # Initial call
    QTimer.singleShot(0, on_resize)
    
    return widget