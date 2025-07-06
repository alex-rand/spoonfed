# Spoonfed Design System

## Color Palette

### Primary Colors
- **Primary**: #4A90E2 (Blue - Trust, Learning, Intelligence)
- **Primary Light**: #6BA4EA
- **Primary Dark**: #3A7BD5

### Secondary Colors
- **Secondary**: #7ED321 (Green - Success, Progress, Growth)
- **Secondary Light**: #95E942
- **Secondary Dark**: #6BC218

### Neutral Colors
- **Background**: #F8F9FA (Light Gray - Clean, Minimal)
- **Surface**: #FFFFFF (White - Content Areas)
- **Surface Dark**: #F1F3F4 (Light Gray - Borders, Dividers)
- **Text Primary**: #212529 (Dark Gray - Main Text)
- **Text Secondary**: #6C757D (Medium Gray - Secondary Text)
- **Text Muted**: #ADB5BD (Light Gray - Disabled Text)

### Semantic Colors
- **Success**: #28A745 (Green - Completed Actions)
- **Warning**: #FFC107 (Yellow - Caution States)
- **Error**: #DC3545 (Red - Error States)
- **Info**: #17A2B8 (Cyan - Information)

## Typography

### Font Families
- **Primary**: 'Segoe UI', 'Roboto', 'Arial', sans-serif
- **Accent**: 'PlantinMTStd-Italic' (for headers and branding)
- **Monospace**: 'Consolas', 'Monaco', 'Courier New', monospace

### Font Scale
- **Display**: 28px / 34px (Large headers)
- **H1**: 24px / 30px (Page titles)
- **H2**: 20px / 26px (Section headers)
- **H3**: 18px / 24px (Subsection headers)
- **Body**: 14px / 20px (Main content)
- **Caption**: 12px / 16px (Small text, labels)
- **Small**: 10px / 14px (Micro text)

### Font Weights
- **Light**: 300
- **Regular**: 400
- **Medium**: 500
- **Bold**: 700

## Spacing System

### Base Unit: 8px
- **XS**: 4px (0.5 units)
- **SM**: 8px (1 unit)
- **MD**: 16px (2 units)
- **LG**: 24px (3 units)
- **XL**: 32px (4 units)
- **XXL**: 48px (6 units)

### Component Spacing
- **Button Padding**: 12px 24px
- **Input Padding**: 12px 16px
- **Card Padding**: 24px
- **Section Margin**: 32px
- **Element Margin**: 16px

## Component Specifications

### Buttons
- **Primary Button**: Blue background, white text, 8px border radius
- **Secondary Button**: White background, blue border, blue text
- **Tertiary Button**: Transparent background, blue text, no border
- **Danger Button**: Red background, white text
- **Height**: 40px (regular), 32px (small), 48px (large)

### Input Fields
- **Border**: 1px solid #CED4DA
- **Border Radius**: 4px
- **Focus Border**: 2px solid Primary color
- **Height**: 40px
- **Padding**: 12px 16px

### Cards
- **Background**: White
- **Border**: 1px solid #E9ECEF
- **Border Radius**: 8px
- **Shadow**: 0 2px 4px rgba(0,0,0,0.1)
- **Padding**: 24px

### Navigation
- **Back Button**: Icon + text, left aligned
- **Breadcrumb**: Text with separators, small font
- **Progress Bar**: Blue fill, light gray background

## Layout Grid

### Container Widths
- **Small**: 480px
- **Medium**: 768px
- **Large**: 1024px
- **X-Large**: 1200px

### Grid System
- **Columns**: 12-column grid
- **Gutter**: 24px
- **Margins**: 32px (desktop), 16px (mobile)

## Interaction States

### Hover States
- **Opacity**: 0.8 for most elements
- **Background**: Lighten by 10%
- **Border**: Darken by 20%

### Focus States
- **Outline**: 2px solid Primary color
- **Outline Offset**: 2px

### Active States
- **Background**: Darken by 10%
- **Transform**: scale(0.98)

### Disabled States
- **Opacity**: 0.5
- **Cursor**: not-allowed

## Animation Guidelines

### Timing
- **Fast**: 150ms (micro-interactions)
- **Medium**: 300ms (transitions)
- **Slow**: 500ms (major changes)

### Easing
- **Standard**: cubic-bezier(0.4, 0.0, 0.2, 1)
- **Decelerate**: cubic-bezier(0.0, 0.0, 0.2, 1)
- **Accelerate**: cubic-bezier(0.4, 0.0, 1, 1)

### Properties to Animate
- **opacity** (fade effects)
- **transform** (movement, scaling)
- **background-color** (color changes)
- **border-color** (state changes)

## Accessibility

### Color Contrast
- **AA Standard**: 4.5:1 for normal text
- **AA Standard**: 3:1 for large text
- **AAA Standard**: 7:1 for normal text (preferred)

### Focus Management
- **Visible Focus**: All interactive elements
- **Keyboard Navigation**: Logical tab order
- **Screen Reader**: Proper ARIA labels

### Text Scaling
- **Support**: Up to 200% zoom
- **Relative Units**: Use em/rem for text
- **Minimum Size**: 16px for touch targets

## Icon System

### Style
- **Type**: Outline icons
- **Weight**: 1.5px stroke
- **Size**: 16px, 20px, 24px variants
- **Color**: Inherit from parent element

### Usage
- **Buttons**: Left-aligned icon + text
- **Navigation**: Icon only with tooltip
- **Status**: Color-coded semantic icons

## Loading States

### Spinners
- **Size**: 20px (small), 32px (medium), 48px (large)
- **Color**: Primary color
- **Animation**: Smooth rotation

### Progress Bars
- **Height**: 4px (thin), 8px (medium)
- **Background**: Light gray
- **Fill**: Primary color
- **Animation**: Smooth progress

### Skeleton Screens
- **Background**: Light gray gradient
- **Animation**: Shimmer effect
- **Duration**: 1.5s loop

## Error Handling

### Message Types
- **Success**: Green background, checkmark icon
- **Warning**: Yellow background, warning icon
- **Error**: Red background, error icon
- **Info**: Blue background, info icon

### Positioning
- **Toast**: Top-right corner
- **Inline**: Below form fields
- **Modal**: Center overlay

## Responsive Design

### Breakpoints
- **Mobile**: 320px - 767px
- **Tablet**: 768px - 1023px
- **Desktop**: 1024px+

### Adaptive Layouts
- **Mobile**: Single column, larger touch targets
- **Tablet**: Two columns, medium spacing
- **Desktop**: Multi-column, compact spacing