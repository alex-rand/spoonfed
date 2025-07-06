"""
Style Manager for Spoonfed Application
Handles loading and applying QSS styles with theme support
"""

import os
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication


class StyleManager(QObject):
    """Manages application styling and themes"""
    
    theme_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_theme = "light"
        self.styles_dir = Path(__file__).parent.parent / "styles"
        self.loaded_styles = {}
        
    def load_style_file(self, filename):
        """Load a QSS file and return its contents"""
        style_path = self.styles_dir / filename
        if style_path.exists():
            with open(style_path, 'r', encoding='utf-8') as file:
                return file.read()
        return ""
    
    def get_base_styles(self):
        """Get base application styles"""
        if 'base' not in self.loaded_styles:
            self.loaded_styles['base'] = self.load_style_file('base.qss')
        return self.loaded_styles['base']
    
    def get_component_styles(self):
        """Get component-specific styles"""
        if 'components' not in self.loaded_styles:
            self.loaded_styles['components'] = self.load_style_file('components.qss')
        return self.loaded_styles['components']
    
    def get_animation_styles(self):
        """Get animation-related styles"""
        if 'animations' not in self.loaded_styles:
            self.loaded_styles['animations'] = self.load_style_file('animations.qss')
        return self.loaded_styles['animations']
    
    def get_theme_styles(self, theme='light'):
        """Get theme-specific styles"""
        theme_file = f'theme_{theme}.qss'
        if theme_file not in self.loaded_styles:
            self.loaded_styles[theme_file] = self.load_style_file(theme_file)
        return self.loaded_styles[theme_file]
    
    def get_complete_stylesheet(self, theme='light'):
        """Combine all stylesheets into one"""
        styles = [
            self.get_base_styles(),
            self.get_component_styles(),
            self.get_animation_styles(),
            self.get_theme_styles(theme)
        ]
        return '\n\n'.join(filter(None, styles))
    
    def apply_theme(self, theme='light'):
        """Apply a theme to the application"""
        self.current_theme = theme
        app = QApplication.instance()
        if app:
            stylesheet = self.get_complete_stylesheet(theme)
            app.setStyleSheet(stylesheet)
            self.theme_changed.emit(theme)
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        new_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.apply_theme(new_theme)
    
    def refresh_styles(self):
        """Reload and reapply all styles"""
        self.loaded_styles.clear()
        self.apply_theme(self.current_theme)
    
    def add_custom_style(self, style_name, style_content):
        """Add custom style content"""
        self.loaded_styles[style_name] = style_content
    
    def get_color_palette(self, theme='light'):
        """Get color palette for the current theme"""
        if theme == 'light':
            return {
                'primary': '#4A90E2',
                'primary_light': '#6BA4EA',
                'primary_dark': '#3A7BD5',
                'secondary': '#7ED321',
                'secondary_light': '#95E942',
                'secondary_dark': '#6BC218',
                'background': '#F8F9FA',
                'surface': '#FFFFFF',
                'surface_dark': '#F1F3F4',
                'text_primary': '#212529',
                'text_secondary': '#6C757D',
                'text_muted': '#ADB5BD',
                'success': '#28A745',
                'warning': '#FFC107',
                'error': '#DC3545',
                'info': '#17A2B8'
            }
        else:  # dark theme
            return {
                'primary': '#5BA0F2',
                'primary_light': '#7BB4F5',
                'primary_dark': '#4A8BDF',
                'secondary': '#8EE431',
                'secondary_light': '#A5F552',
                'secondary_dark': '#7CD228',
                'background': '#1A1A1A',
                'surface': '#2D2D2D',
                'surface_dark': '#404040',
                'text_primary': '#FFFFFF',
                'text_secondary': '#B0B0B0',
                'text_muted': '#808080',
                'success': '#38B755',
                'warning': '#FFD317',
                'error': '#EC4555',
                'info': '#27B2C8'
            }
    
    def get_spacing_values(self):
        """Get standardized spacing values"""
        return {
            'xs': 4,
            'sm': 8,
            'md': 16,
            'lg': 24,
            'xl': 32,
            'xxl': 48
        }
    
    def get_font_sizes(self):
        """Get standardized font sizes"""
        return {
            'display': 28,
            'h1': 24,
            'h2': 20,
            'h3': 18,
            'body': 14,
            'caption': 12,
            'small': 10
        }
    
    def get_border_radius_values(self):
        """Get standardized border radius values"""
        return {
            'small': 4,
            'medium': 8,
            'large': 12,
            'pill': 9999
        }
    
    def get_shadow_values(self):
        """Get standardized shadow values (for programmatic shadows)"""
        return {
            'small': '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
            'medium': '0 3px 6px rgba(0,0,0,0.16), 0 3px 6px rgba(0,0,0,0.23)',
            'large': '0 10px 20px rgba(0,0,0,0.19), 0 6px 6px rgba(0,0,0,0.23)',
            'xlarge': '0 14px 28px rgba(0,0,0,0.25), 0 10px 10px rgba(0,0,0,0.22)'
        }


# Global style manager instance
style_manager = StyleManager()