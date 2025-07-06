"""
Micro-interactions and smooth transitions for Spoonfed Application
Adds polish and delight to user interactions
"""

from PyQt5.QtWidgets import QWidget, QFrame, QPushButton, QLabel, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QRect, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QBrush, QPen, QPixmap, QTransform
import math


class HoverEffect:
    """Adds hover effects to widgets"""
    
    @staticmethod
    def lift_on_hover(widget, lift_amount=2):
        """Add subtle lift effect on hover"""
        original_y = widget.y()
        
        def on_enter():
            if hasattr(widget, '_lift_animation'):
                widget._lift_animation.stop()
            
            widget._lift_animation = QPropertyAnimation(widget, b"pos")
            widget._lift_animation.setDuration(150)
            widget._lift_animation.setStartValue(widget.pos())
            end_pos = widget.pos()
            end_pos.setY(original_y - lift_amount)
            widget._lift_animation.setEndValue(end_pos)
            widget._lift_animation.setEasingCurve(QEasingCurve.OutCubic)
            widget._lift_animation.start()
            
        def on_leave():
            if hasattr(widget, '_lift_animation'):
                widget._lift_animation.stop()
                
            widget._lift_animation = QPropertyAnimation(widget, b"pos")
            widget._lift_animation.setDuration(150)
            widget._lift_animation.setStartValue(widget.pos())
            end_pos = widget.pos()
            end_pos.setY(original_y)
            widget._lift_animation.setEndValue(end_pos)
            widget._lift_animation.setEasingCurve(QEasingCurve.OutCubic)
            widget._lift_animation.start()
            
        # Override enter/leave events
        original_enter = widget.enterEvent if hasattr(widget, 'enterEvent') else lambda e: None
        original_leave = widget.leaveEvent if hasattr(widget, 'leaveEvent') else lambda e: None
        
        def new_enter(event):
            original_enter(event)
            on_enter()
            
        def new_leave(event):
            original_leave(event)
            on_leave()
            
        widget.enterEvent = new_enter
        widget.leaveEvent = new_leave
        
    @staticmethod
    def scale_on_hover(widget, scale_factor=1.05):
        """Add subtle scale effect on hover"""
        original_size = widget.size()
        
        def on_enter():
            if hasattr(widget, '_scale_animation'):
                widget._scale_animation.stop()
                
            widget._scale_animation = QPropertyAnimation(widget, b"size")
            widget._scale_animation.setDuration(200)
            widget._scale_animation.setStartValue(widget.size())
            new_size = original_size
            new_size.setWidth(int(original_size.width() * scale_factor))
            new_size.setHeight(int(original_size.height() * scale_factor))
            widget._scale_animation.setEndValue(new_size)
            widget._scale_animation.setEasingCurve(QEasingCurve.OutCubic)
            widget._scale_animation.start()
            
        def on_leave():
            if hasattr(widget, '_scale_animation'):
                widget._scale_animation.stop()
                
            widget._scale_animation = QPropertyAnimation(widget, b"size")
            widget._scale_animation.setDuration(200)
            widget._scale_animation.setStartValue(widget.size())
            widget._scale_animation.setEndValue(original_size)
            widget._scale_animation.setEasingCurve(QEasingCurve.OutCubic)
            widget._scale_animation.start()
            
        # Override enter/leave events
        original_enter = widget.enterEvent if hasattr(widget, 'enterEvent') else lambda e: None
        original_leave = widget.leaveEvent if hasattr(widget, 'leaveEvent') else lambda e: None
        
        def new_enter(event):
            original_enter(event)
            on_enter()
            
        def new_leave(event):
            original_leave(event)
            on_leave()
            
        widget.enterEvent = new_enter
        widget.leaveEvent = new_leave
        
    @staticmethod
    def glow_on_hover(widget, glow_color=QColor(74, 144, 226, 100)):
        """Add glow effect on hover"""
        def on_enter():
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setColor(glow_color)
            shadow.setOffset(0, 0)
            widget.setGraphicsEffect(shadow)
            
        def on_leave():
            widget.setGraphicsEffect(None)
            
        # Override enter/leave events
        original_enter = widget.enterEvent if hasattr(widget, 'enterEvent') else lambda e: None
        original_leave = widget.leaveEvent if hasattr(widget, 'leaveEvent') else lambda e: None
        
        def new_enter(event):
            original_enter(event)
            on_enter()
            
        def new_leave(event):
            original_leave(event)
            on_leave()
            
        widget.enterEvent = new_enter
        widget.leaveEvent = new_leave


class ClickFeedback:
    """Provides visual feedback for clicks"""
    
    @staticmethod
    def ripple_effect(widget, click_pos=None):
        """Add ripple effect on click"""
        if not click_pos:
            click_pos = widget.rect().center()
            
        # Create ripple widget
        ripple = RippleWidget(widget)
        ripple.start_ripple(click_pos)
        
    @staticmethod
    def press_animation(widget):
        """Add press down animation"""
        def on_press():
            if hasattr(widget, '_press_animation'):
                widget._press_animation.stop()
                
            widget._press_animation = QPropertyAnimation(widget, b"size")
            widget._press_animation.setDuration(100)
            widget._press_animation.setStartValue(widget.size())
            pressed_size = widget.size()
            pressed_size.setWidth(int(pressed_size.width() * 0.95))
            pressed_size.setHeight(int(pressed_size.height() * 0.95))
            widget._press_animation.setEndValue(pressed_size)
            widget._press_animation.setEasingCurve(QEasingCurve.OutCubic)
            widget._press_animation.start()
            
        def on_release():
            if hasattr(widget, '_press_animation'):
                widget._press_animation.stop()
                
            widget._press_animation = QPropertyAnimation(widget, b"size")
            widget._press_animation.setDuration(100)
            widget._press_animation.setStartValue(widget.size())
            widget._press_animation.setEndValue(widget.size())  # Back to original
            widget._press_animation.setEasingCurve(QEasingCurve.OutBounce)
            widget._press_animation.start()
            
        # Override mouse events
        original_press = widget.mousePressEvent if hasattr(widget, 'mousePressEvent') else lambda e: None
        original_release = widget.mouseReleaseEvent if hasattr(widget, 'mouseReleaseEvent') else lambda e: None
        
        def new_press(event):
            original_press(event)
            on_press()
            
        def new_release(event):
            original_release(event)
            on_release()
            
        widget.mousePressEvent = new_press
        widget.mouseReleaseEvent = new_release


class RippleWidget(QWidget):
    """Widget that creates ripple effects"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(parent.size())
        
        self.ripple_radius = 0
        self.ripple_center = None
        self.max_radius = 0
        
        self.animation = QPropertyAnimation(self, b"ripple_radius")
        self.animation.finished.connect(self.deleteLater)
        
    def start_ripple(self, center):
        """Start ripple animation"""
        self.ripple_center = center
        self.max_radius = max(self.width(), self.height()) * 0.7
        
        self.animation.setDuration(400)
        self.animation.setStartValue(0)
        self.animation.setEndValue(self.max_radius)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()
        
        self.show()
        
    def get_ripple_radius(self):
        return self.ripple_radius
        
    def set_ripple_radius(self, radius):
        self.ripple_radius = radius
        self.update()
        
    ripple_radius = property(get_ripple_radius, set_ripple_radius)
    
    def paintEvent(self, event):
        """Paint the ripple effect"""
        if self.ripple_center is None:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate opacity based on radius
        opacity = 1.0 - (self.ripple_radius / self.max_radius)
        
        # Create ripple brush
        color = QColor(74, 144, 226, int(opacity * 100))
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        
        # Draw ripple
        painter.drawEllipse(
            self.ripple_center.x() - self.ripple_radius,
            self.ripple_center.y() - self.ripple_radius,
            self.ripple_radius * 2,
            self.ripple_radius * 2
        )


class LoadingDots(QWidget):
    """Animated loading dots"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dots = []
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_dots)
        self.current_dot = 0
        
        self.setFixedSize(60, 20)
        
    def start_animation(self):
        """Start the loading animation"""
        self.animation_timer.start(200)
        
    def stop_animation(self):
        """Stop the loading animation"""
        self.animation_timer.stop()
        self.current_dot = 0
        self.update()
        
    def animate_dots(self):
        """Animate the dots"""
        self.current_dot = (self.current_dot + 1) % 4
        self.update()
        
    def paintEvent(self, event):
        """Paint the loading dots"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        dot_radius = 4
        spacing = 15
        start_x = (self.width() - 3 * spacing) // 2
        center_y = self.height() // 2
        
        for i in range(3):
            x = start_x + i * spacing
            
            # Calculate opacity and size based on animation
            if i == self.current_dot % 3:
                opacity = 255
                radius = dot_radius + 2
            elif i == (self.current_dot - 1) % 3:
                opacity = 180
                radius = dot_radius + 1
            else:
                opacity = 100
                radius = dot_radius
                
            color = QColor(74, 144, 226, opacity)
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            
            painter.drawEllipse(x - radius, center_y - radius, radius * 2, radius * 2)


class ProgressRing(QWidget):
    """Animated progress ring"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress = 0
        self.animation_enabled = True
        self.ring_color = QColor(74, 144, 226)
        self.background_color = QColor(241, 243, 244)
        self.line_width = 4
        
        self.setFixedSize(40, 40)
        
    def set_progress(self, progress):
        """Set progress (0-100)"""
        self.progress = max(0, min(100, progress))
        self.update()
        
    def animate_to_progress(self, target_progress, duration=500):
        """Animate to target progress"""
        self.animation = QPropertyAnimation(self, b"progress")
        self.animation.setDuration(duration)
        self.animation.setStartValue(self.progress)
        self.animation.setEndValue(target_progress)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()
        
    def paintEvent(self, event):
        """Paint the progress ring"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect().adjusted(self.line_width // 2, self.line_width // 2, 
                                   -self.line_width // 2, -self.line_width // 2)
        
        # Draw background ring
        painter.setPen(QPen(self.background_color, self.line_width))
        painter.drawEllipse(rect)
        
        # Draw progress arc
        if self.progress > 0:
            painter.setPen(QPen(self.ring_color, self.line_width, Qt.SolidLine, Qt.RoundCap))
            span_angle = int(360 * 16 * (self.progress / 100))
            painter.drawArc(rect, 90 * 16, -span_angle)  # Start from top, go clockwise


class FloatingActionButton(QPushButton):
    """Material Design style floating action button"""
    
    def __init__(self, icon_text="", parent=None):
        super().__init__(icon_text, parent)
        self.setup_style()
        self.add_interactions()
        
    def setup_style(self):
        """Setup FAB styling"""
        self.setFixedSize(56, 56)
        self.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                border: none;
                border-radius: 28px;
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
    def add_interactions(self):
        """Add micro-interactions"""
        HoverEffect.lift_on_hover(self, 4)
        ClickFeedback.press_animation(self)


class StaggeredAnimation:
    """Creates staggered animations for multiple widgets"""
    
    @staticmethod
    def fade_in_sequence(widgets, delay=100, duration=300):
        """Fade in widgets in sequence"""
        animations = []
        
        for i, widget in enumerate(widgets):
            animation = QPropertyAnimation(widget, b"windowOpacity")
            animation.setDuration(duration)
            animation.setStartValue(0.0)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.OutCubic)
            
            # Delay each animation
            QTimer.singleShot(i * delay, animation.start)
            animations.append(animation)
            
        return animations
        
    @staticmethod
    def slide_in_sequence(widgets, direction="up", delay=100, duration=300):
        """Slide in widgets in sequence"""
        animations = []
        
        for i, widget in enumerate(widgets):
            original_pos = widget.pos()
            
            # Set start position based on direction
            if direction == "up":
                start_pos = original_pos
                start_pos.setY(start_pos.y() + 50)
            elif direction == "down":
                start_pos = original_pos
                start_pos.setY(start_pos.y() - 50)
            elif direction == "left":
                start_pos = original_pos
                start_pos.setX(start_pos.x() + 50)
            elif direction == "right":
                start_pos = original_pos
                start_pos.setX(start_pos.x() - 50)
                
            widget.move(start_pos)
            
            animation = QPropertyAnimation(widget, b"pos")
            animation.setDuration(duration)
            animation.setStartValue(start_pos)
            animation.setEndValue(original_pos)
            animation.setEasingCurve(QEasingCurve.OutCubic)
            
            # Delay each animation
            QTimer.singleShot(i * delay, animation.start)
            animations.append(animation)
            
        return animations


class MorphingButton(QPushButton):
    """Button that morphs between states"""
    
    state_changed = pyqtSignal(str)
    
    def __init__(self, states=None, parent=None):
        super().__init__(parent)
        self.states = states or ["default"]
        self.current_state_index = 0
        self.morph_duration = 300
        
        self.setup_morphing()
        
    def setup_morphing(self):
        """Setup morphing animations"""
        self.clicked.connect(self.morph_to_next_state)
        
    def morph_to_next_state(self):
        """Morph to the next state"""
        self.current_state_index = (self.current_state_index + 1) % len(self.states)
        new_state = self.states[self.current_state_index]
        
        # Animate text change
        self.animate_text_change(new_state)
        self.state_changed.emit(new_state)
        
    def animate_text_change(self, new_text):
        """Animate text change with scale effect"""
        # Scale down
        scale_down = QPropertyAnimation(self, b"size")
        scale_down.setDuration(self.morph_duration // 2)
        scale_down.setStartValue(self.size())
        smaller_size = self.size()
        smaller_size.setWidth(int(smaller_size.width() * 0.8))
        scale_down.setEndValue(smaller_size)
        scale_down.setEasingCurve(QEasingCurve.OutCubic)
        
        # Change text in the middle
        def change_text():
            self.setText(new_text)
            
        scale_down.finished.connect(change_text)
        
        # Scale back up
        scale_up = QPropertyAnimation(self, b"size")
        scale_up.setDuration(self.morph_duration // 2)
        scale_up.setStartValue(smaller_size)
        scale_up.setEndValue(self.size())
        scale_up.setEasingCurve(QEasingCurve.OutBounce)
        
        scale_down.finished.connect(scale_up.start)
        scale_down.start()


def add_micro_interactions(widget):
    """Add subtle micro-interactions to any widget"""
    if isinstance(widget, QPushButton):
        HoverEffect.scale_on_hover(widget, 1.02)
        ClickFeedback.press_animation(widget)
    elif isinstance(widget, QFrame):
        HoverEffect.lift_on_hover(widget, 1)
    elif isinstance(widget, QLabel):
        if widget.cursor().shape() == Qt.PointingHandCursor:
            HoverEffect.glow_on_hover(widget)


def animate_widget_entrance(widget, animation_type="fade", delay=0):
    """Animate widget entrance with various effects"""
    def start_animation():
        if animation_type == "fade":
            widget.setWindowOpacity(0.0)
            widget.show()
            
            animation = QPropertyAnimation(widget, b"windowOpacity")
            animation.setDuration(400)
            animation.setStartValue(0.0)
            animation.setEndValue(1.0)
            animation.setEasingCurve(QEasingCurve.OutCubic)
            animation.start()
            
        elif animation_type == "scale":
            original_size = widget.size()
            widget.resize(0, 0)
            widget.show()
            
            animation = QPropertyAnimation(widget, b"size")
            animation.setDuration(400)
            animation.setStartValue(widget.size())
            animation.setEndValue(original_size)
            animation.setEasingCurve(QEasingCurve.OutBack)
            animation.start()
            
        elif animation_type == "slide_up":
            original_pos = widget.pos()
            start_pos = original_pos
            start_pos.setY(start_pos.y() + 50)
            widget.move(start_pos)
            widget.show()
            
            animation = QPropertyAnimation(widget, b"pos")
            animation.setDuration(400)
            animation.setStartValue(start_pos)
            animation.setEndValue(original_pos)
            animation.setEasingCurve(QEasingCurve.OutCubic)
            animation.start()
    
    if delay > 0:
        QTimer.singleShot(delay, start_animation)
    else:
        start_animation()


# Convenience functions for common micro-interactions
def make_hoverable(widget, effect="lift"):
    """Make widget respond to hover"""
    if effect == "lift":
        HoverEffect.lift_on_hover(widget)
    elif effect == "scale":
        HoverEffect.scale_on_hover(widget)
    elif effect == "glow":
        HoverEffect.glow_on_hover(widget)


def make_clickable(widget, feedback="ripple"):
    """Add click feedback to widget"""
    if feedback == "ripple":
        widget.mousePressEvent = lambda e: ClickFeedback.ripple_effect(widget, e.pos())
    elif feedback == "press":
        ClickFeedback.press_animation(widget)