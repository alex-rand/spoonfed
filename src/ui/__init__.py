"""
UI Package for Spoonfed Application
Contains enhanced UI components and styling utilities
"""

from .style_manager import StyleManager, style_manager
from .components import *
from .animations import *
from .navigation import *
from .feedback import *
from .layout import *

__all__ = [
    # Style Management
    'StyleManager',
    'style_manager',
    
    # Components
    'ModernButton',
    'ModernInput',
    'ModernComboBox',
    'ModernCard',
    'LoadingSpinner',
    'ProgressIndicator',
    'ToastNotification',
    'NavigationHeader',
    'ModernTreeWidget',
    'ModernProgressBar',
    'SkeletonLoader',
    'Breadcrumb',
    
    # Animations
    'AnimationManager',
    'animation_manager',
    'FadeAnimation',
    'SlideAnimation',
    'ScaleAnimation',
    
    # Navigation
    'NavigationManager',
    'nav_manager',
    'EnhancedNavigationHeader',
    'StepIndicator',
    'PageTransition',
    
    # Feedback
    'NotificationManager',
    'LoadingOverlay',
    'ProgressDialog',
    'StatusBar',
    'InlineValidation',
    'show_success_notification',
    'show_error_notification',
    'show_loading_overlay',
    'hide_loading_overlay',
    
    # Layout
    'ResponsiveContainer',
    'FlexLayout',
    'GridResponsive',
    'SpacingManager',
    'ResponsiveCard',
    'AdaptiveScrollArea',
    'LayoutBreakpoints',
    'TwoColumnLayout',
    'create_responsive_form',
    'make_responsive'
]