"""
Animation utilities for Spoonfed Application
Provides smooth animations and transitions
"""

from PyQt5.QtCore import (
    QPropertyAnimation, QEasingCurve, QRect, QTimer, QObject, 
    pyqtSignal, QParallelAnimationGroup, QSequentialAnimationGroup
)
from PyQt5.QtWidgets import QWidget, QGraphicsOpacityEffect
from PyQt5.QtGui import QTransform


class AnimationManager(QObject):
    """Manages animations for widgets"""
    
    animation_finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animations = {}
        self.groups = {}
        
    def fade_in(self, widget, duration=300, start_opacity=0.0, end_opacity=1.0):
        """Fade in animation"""
        # Check if widget already has an animation running
        widget_id = id(widget)
        animation_key = f"fade_in_{widget_id}"
        
        # Stop any existing animation for this widget
        if animation_key in self.animations:
            self.animations[animation_key].stop()
            
        # Check if widget already has an opacity effect
        effect = widget.graphicsEffect()
        if not effect or not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect()
            widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(start_opacity)
        animation.setEndValue(end_opacity)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Clean up after animation finishes
        def cleanup():
            if animation_key in self.animations:
                del self.animations[animation_key]
            # Remove the graphics effect after animation to prevent painter issues
            widget.setGraphicsEffect(None)
            self.animation_finished.emit()
        
        animation.finished.connect(cleanup)
        
        self.animations[animation_key] = animation
        animation.start()
        
        return animation
        
    def fade_out(self, widget, duration=300, start_opacity=1.0, end_opacity=0.0):
        """Fade out animation"""
        # Check if widget already has an animation running
        widget_id = id(widget)
        animation_key = f"fade_out_{widget_id}"
        
        # Stop any existing animation for this widget
        if animation_key in self.animations:
            self.animations[animation_key].stop()
            
        # Check if widget already has an opacity effect
        effect = widget.graphicsEffect()
        if not effect or not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect()
            widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(start_opacity)
        animation.setEndValue(end_opacity)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Clean up after animation finishes
        def cleanup():
            if animation_key in self.animations:
                del self.animations[animation_key]
            # Remove the graphics effect after animation to prevent painter issues
            widget.setGraphicsEffect(None)
            self.animation_finished.emit()
        
        animation.finished.connect(cleanup)
        
        self.animations[animation_key] = animation
        animation.start()
        
        return animation
        
    def slide_in_left(self, widget, duration=300, distance=None):
        """Slide in from left animation"""
        if distance is None:
            distance = widget.width()
            
        start_pos = widget.pos()
        start_pos.setX(start_pos.x() - distance)
        end_pos = widget.pos()
        
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.animations[f"slide_in_left_{id(widget)}"] = animation
        animation.finished.connect(self.animation_finished.emit)
        animation.start()
        
        return animation
        
    def slide_in_right(self, widget, duration=300, distance=None):
        """Slide in from right animation"""
        if distance is None:
            distance = widget.width()
            
        start_pos = widget.pos()
        start_pos.setX(start_pos.x() + distance)
        end_pos = widget.pos()
        
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.animations[f"slide_in_right_{id(widget)}"] = animation
        animation.finished.connect(self.animation_finished.emit)
        animation.start()
        
        return animation
        
    def slide_in_up(self, widget, duration=300, distance=None):
        """Slide in from bottom animation"""
        if distance is None:
            distance = widget.height()
            
        start_pos = widget.pos()
        start_pos.setY(start_pos.y() + distance)
        end_pos = widget.pos()
        
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.animations[f"slide_in_up_{id(widget)}"] = animation
        animation.finished.connect(self.animation_finished.emit)
        animation.start()
        
        return animation
        
    def slide_in_down(self, widget, duration=300, distance=None):
        """Slide in from top animation"""
        if distance is None:
            distance = widget.height()
            
        start_pos = widget.pos()
        start_pos.setY(start_pos.y() - distance)
        end_pos = widget.pos()
        
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.animations[f"slide_in_down_{id(widget)}"] = animation
        animation.finished.connect(self.animation_finished.emit)
        animation.start()
        
        return animation
        
    def scale_in(self, widget, duration=300, start_scale=0.0, end_scale=1.0):
        """Scale in animation"""
        start_size = widget.size()
        start_size.setWidth(int(start_size.width() * start_scale))
        start_size.setHeight(int(start_size.height() * start_scale))
        
        end_size = widget.size()
        end_size.setWidth(int(end_size.width() * end_scale))
        end_size.setHeight(int(end_size.height() * end_scale))
        
        animation = QPropertyAnimation(widget, b"size")
        animation.setDuration(duration)
        animation.setStartValue(start_size)
        animation.setEndValue(end_size)
        animation.setEasingCurve(QEasingCurve.OutBack)
        
        self.animations[f"scale_in_{id(widget)}"] = animation
        animation.finished.connect(self.animation_finished.emit)
        animation.start()
        
        return animation
        
    def scale_out(self, widget, duration=300, start_scale=1.0, end_scale=0.0):
        """Scale out animation"""
        start_size = widget.size()
        start_size.setWidth(int(start_size.width() * start_scale))
        start_size.setHeight(int(start_size.height() * start_scale))
        
        end_size = widget.size()
        end_size.setWidth(int(end_size.width() * end_scale))
        end_size.setHeight(int(end_size.height() * end_scale))
        
        animation = QPropertyAnimation(widget, b"size")
        animation.setDuration(duration)
        animation.setStartValue(start_size)
        animation.setEndValue(end_size)
        animation.setEasingCurve(QEasingCurve.InBack)
        
        self.animations[f"scale_out_{id(widget)}"] = animation
        animation.finished.connect(self.animation_finished.emit)
        animation.start()
        
        return animation
        
    def bounce_in(self, widget, duration=600):
        """Bounce in animation"""
        # Create a sequence of scale animations
        group = QSequentialAnimationGroup()
        
        # Scale to 1.1
        scale_up = QPropertyAnimation(widget, b"size")
        scale_up.setDuration(duration // 3)
        scale_up.setStartValue(widget.size())
        end_size = widget.size()
        end_size.setWidth(int(end_size.width() * 1.1))
        end_size.setHeight(int(end_size.height() * 1.1))
        scale_up.setEndValue(end_size)
        scale_up.setEasingCurve(QEasingCurve.OutQuad)
        
        # Scale to 0.9
        scale_down = QPropertyAnimation(widget, b"size")
        scale_down.setDuration(duration // 3)
        scale_down.setStartValue(end_size)
        small_size = widget.size()
        small_size.setWidth(int(small_size.width() * 0.9))
        small_size.setHeight(int(small_size.height() * 0.9))
        scale_down.setEndValue(small_size)
        scale_down.setEasingCurve(QEasingCurve.OutQuad)
        
        # Scale to 1.0
        scale_normal = QPropertyAnimation(widget, b"size")
        scale_normal.setDuration(duration // 3)
        scale_normal.setStartValue(small_size)
        scale_normal.setEndValue(widget.size())
        scale_normal.setEasingCurve(QEasingCurve.OutQuad)
        
        group.addAnimation(scale_up)
        group.addAnimation(scale_down)
        group.addAnimation(scale_normal)
        
        self.groups[f"bounce_in_{id(widget)}"] = group
        group.finished.connect(self.animation_finished.emit)
        group.start()
        
        return group
        
    def shake(self, widget, duration=500, intensity=10):
        """Shake animation"""
        original_pos = widget.pos()
        group = QSequentialAnimationGroup()
        
        # Create shake sequence
        shake_count = 8
        shake_duration = duration // shake_count
        
        for i in range(shake_count):
            animation = QPropertyAnimation(widget, b"pos")
            animation.setDuration(shake_duration)
            animation.setStartValue(widget.pos())
            
            # Alternate left and right
            offset = intensity if i % 2 == 0 else -intensity
            shake_pos = original_pos
            shake_pos.setX(shake_pos.x() + offset)
            animation.setEndValue(shake_pos)
            animation.setEasingCurve(QEasingCurve.OutQuad)
            
            group.addAnimation(animation)
            
        # Return to original position
        return_animation = QPropertyAnimation(widget, b"pos")
        return_animation.setDuration(shake_duration)
        return_animation.setStartValue(widget.pos())
        return_animation.setEndValue(original_pos)
        return_animation.setEasingCurve(QEasingCurve.OutQuad)
        group.addAnimation(return_animation)
        
        self.groups[f"shake_{id(widget)}"] = group
        group.finished.connect(self.animation_finished.emit)
        group.start()
        
        return group
        
    def pulse(self, widget, duration=1000, scale_factor=1.05):
        """Pulse animation (continuous)"""
        # Scale up
        scale_up = QPropertyAnimation(widget, b"size")
        scale_up.setDuration(duration // 2)
        scale_up.setStartValue(widget.size())
        end_size = widget.size()
        end_size.setWidth(int(end_size.width() * scale_factor))
        end_size.setHeight(int(end_size.height() * scale_factor))
        scale_up.setEndValue(end_size)
        scale_up.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Scale down
        scale_down = QPropertyAnimation(widget, b"size")
        scale_down.setDuration(duration // 2)
        scale_down.setStartValue(end_size)
        scale_down.setEndValue(widget.size())
        scale_down.setEasingCurve(QEasingCurve.InOutQuad)
        
        group = QSequentialAnimationGroup()
        group.addAnimation(scale_up)
        group.addAnimation(scale_down)
        group.setLoopCount(-1)  # Infinite loop
        
        self.groups[f"pulse_{id(widget)}"] = group
        group.start()
        
        return group
        
    def rotate(self, widget, duration=1000, angle=360):
        """Rotate animation"""
        # Note: QWidget doesn't have native rotation support
        # This would require custom implementation with QGraphicsView
        pass
        
    def stop_animation(self, widget):
        """Stop all animations for a widget"""
        widget_id = id(widget)
        
        # Stop individual animations
        keys_to_remove = []
        for key, animation in self.animations.items():
            if str(widget_id) in key:
                animation.stop()
                keys_to_remove.append(key)
                
        for key in keys_to_remove:
            del self.animations[key]
            
        # Stop animation groups
        keys_to_remove = []
        for key, group in self.groups.items():
            if str(widget_id) in key:
                group.stop()
                keys_to_remove.append(key)
                
        for key in keys_to_remove:
            del self.groups[key]
            
    def stop_all_animations(self):
        """Stop all running animations"""
        for animation in self.animations.values():
            animation.stop()
        for group in self.groups.values():
            group.stop()
            
        self.animations.clear()
        self.groups.clear()


class FadeAnimation(QObject):
    """Convenient fade animation wrapper"""
    
    finished = pyqtSignal()
    
    def __init__(self, widget, parent=None):
        super().__init__(parent)
        self.widget = widget
        self.effect = QGraphicsOpacityEffect()
        self.widget.setGraphicsEffect(self.effect)
        
    def fade_in(self, duration=300):
        """Fade in the widget"""
        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(duration)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.finished.connect(self.finished.emit)
        self.animation.start()
        
    def fade_out(self, duration=300):
        """Fade out the widget"""
        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(duration)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.finished.connect(self.finished.emit)
        self.animation.start()


class SlideAnimation(QObject):
    """Convenient slide animation wrapper"""
    
    finished = pyqtSignal()
    
    def __init__(self, widget, parent=None):
        super().__init__(parent)
        self.widget = widget
        self.original_pos = widget.pos()
        
    def slide_in_from_left(self, duration=300):
        """Slide in from left"""
        start_pos = self.original_pos
        start_pos.setX(start_pos.x() - self.widget.width())
        
        self.animation = QPropertyAnimation(self.widget, b"pos")
        self.animation.setDuration(duration)
        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(self.original_pos)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.finished.connect(self.finished.emit)
        self.animation.start()
        
    def slide_out_to_right(self, duration=300):
        """Slide out to right"""
        end_pos = self.original_pos
        end_pos.setX(end_pos.x() + self.widget.width())
        
        self.animation = QPropertyAnimation(self.widget, b"pos")
        self.animation.setDuration(duration)
        self.animation.setStartValue(self.original_pos)
        self.animation.setEndValue(end_pos)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.finished.connect(self.finished.emit)
        self.animation.start()


class ScaleAnimation(QObject):
    """Convenient scale animation wrapper"""
    
    finished = pyqtSignal()
    
    def __init__(self, widget, parent=None):
        super().__init__(parent)
        self.widget = widget
        self.original_size = widget.size()
        
    def scale_in(self, duration=300):
        """Scale in animation"""
        start_size = self.original_size
        start_size.setWidth(0)
        start_size.setHeight(0)
        
        self.animation = QPropertyAnimation(self.widget, b"size")
        self.animation.setDuration(duration)
        self.animation.setStartValue(start_size)
        self.animation.setEndValue(self.original_size)
        self.animation.setEasingCurve(QEasingCurve.OutBack)
        self.animation.finished.connect(self.finished.emit)
        self.animation.start()
        
    def scale_out(self, duration=300):
        """Scale out animation"""
        end_size = self.original_size
        end_size.setWidth(0)
        end_size.setHeight(0)
        
        self.animation = QPropertyAnimation(self.widget, b"size")
        self.animation.setDuration(duration)
        self.animation.setStartValue(self.original_size)
        self.animation.setEndValue(end_size)
        self.animation.setEasingCurve(QEasingCurve.InBack)
        self.animation.finished.connect(self.finished.emit)
        self.animation.start()


# Global animation manager instance
animation_manager = AnimationManager()