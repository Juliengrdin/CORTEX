"""
CORTEX Style Definitions
Refactored for clarity, completeness, and maintainability.
Usage:
    from csstyle import Style
    
    # 1. Apply Global Theme first
    app.setStyleSheet(Style.Default.light)
    
    # 2. Apply specific styles to widgets
    my_frame.setStyleSheet(Style.Frame.container_light)
"""

class Palette:
    """Centralized color definitions."""
    
    # Fonts
    FONT_MAIN = "Ubuntu"
    FONT_SIZE = "12px"
    
    # --- Light Theme Palette ---
    L_BG_MAIN       = "#F2F2F2"   # Main window background
    L_BG_FRAME_1    = "#FFFFFF"   # Pure white (Standard frames/inputs)
    L_BG_FRAME_2    = "#F6F6F6"   # Off-white (Button containers)
    L_TEXT_MAIN     = "#000000"
    L_TEXT_SEC      = "#333333"
    L_BORDER        = "#DDDDDD"
    
    # --- Dark Theme Palette ---
    D_BG_MAIN       = "#2E2E2E"   # Main window background
    D_BG_FRAME_1    = "#3A3A3A"   # Standard grey (Standard frames)
    D_BG_FRAME_2    = "#222222"   # Darker grey (Button containers)
    D_TEXT_MAIN     = "#FFFFFF"
    D_TEXT_SEC      = "#E0E0E0"
    D_BORDER        = "#555555"

    # --- Component Colors ---
    # Buttons (Light)
    L_BTN_BG        = "#E0E0E0"
    L_BTN_HOVER     = "#D5D5D5"
    L_BTN_PRESS     = "#B8B8B8"
    
    # Buttons (Dark)
    D_BTN_BG        = "#444444"
    D_BTN_HOVER     = "#555555"
    D_BTN_PRESS     = "#333333"

    # Status & Accents
    ACCENT_BLUE     = "rgb(70, 120, 250)"
    ACCENT_TEAL     = "rgb(90, 200, 170)"
    STATUS_GREEN    = "#4CAF50"   # Start/On
    STATUS_RED      = "#F44336"   # Stop/Off
    STATUS_YELLOW   = "#FFC107"   # Reset
    STATUS_GREY     = "#CCCCCC"   # Disabled/Toggle Off
    
    
    
    
    
    # --- Light Theme Palette ---
    L_BG_MAIN       = "#F2F2F2"   # Main window background
    L_BG_FRAME      = "#FFFFFF"   # Pure white
    L_TEXT_MAIN     = "#000000"
    L_TEXT_SEC      = "#333333"   # Used for Input text
    
    # --- Dark Theme Palette ---
    D_BG_MAIN       = "#2E2E2E"   # Main window background
    D_BG_FRAME      = "#3A3A3A"   # Standard grey
    D_TEXT_MAIN     = "#FFFFFF"
    D_TEXT_SEC      = "#E0E0E0"
    
    # --- Component Colors (Light) ---
    L_BTN_BG        = "#F2F2F2"
    L_BTN_HOVER     = "#DFDFDF"
    L_BTN_PRESS     = "#8F8F8F"
    L_INPUT_BG      = "#FFFFFF"
    L_INPUT_FOCUS   = "#F9F9F9"
    L_BORDER        = "#DDDDDD"
    L_BORDER_HOVER  = "#BBBBBB"
    L_BORDER_FOCUS  = "#8F8F8F"
    
    # --- Component Colors (Dark) ---
    D_BTN_BG        = "#444444"
    D_BTN_HOVER     = "#555555"
    D_BTN_PRESS     = "#333333"
    D_INPUT_BG      = "#5A5A5A"
    D_BORDER        = "#555555"
    D_BORDER_HOVER  = "#BBBBBB"
    D_BORDER_FOCUS  = "#8F8F8F"
    
class Style:
    """Static container for all QSS style strings."""

    # =========================================================
    # 1. GLOBAL DEFAULTS (Apply this to the Main Window/App)
    # =========================================================
    class Default:
        light = f"""
            QWidget {{
                background-color: {Palette.L_BG_MAIN};
                color: {Palette.L_TEXT_MAIN};
                font-family: '{Palette.FONT_MAIN}';
                font-size: {Palette.FONT_SIZE};
            }}
            QFrame {{
                border: 0px solid #444444;
                border-radius: 6px;
                background-color: {Palette.L_BG_FRAME};
            }}
            QPushButton {{
                background-color: {Palette.L_BTN_BG};
                color: {Palette.L_TEXT_MAIN};
                border-radius: 6px;
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: {Palette.L_BTN_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {Palette.L_BTN_PRESS};
            }}
            QLineEdit {{
                background-color: {Palette.L_BG_FRAME_2};
                color: {Palette.L_TEXT_SEC};
                padding: 8px;
                border-radius: 6px;
                border: 0px solid {Palette.L_BORDER};
            }}
            QLabel {{
                color: {Palette.L_TEXT_MAIN};
            }}
            QPlainTextEdit {{
                background-color: {Palette.L_INPUT_BG};
                color: {Palette.L_TEXT_MAIN};
                font-family: '{Palette.FONT_MAIN}';
                font-size: {Palette.FONT_SIZE};
                border: 0px solid {Palette.L_BORDER};
                border-radius: 6px;
                padding: 8px;
            }}
            QPlainTextEdit:hover {{
                border: 1px solid {Palette.L_BORDER_HOVER};
            }}
            QPlainTextEdit:focus {{
                border: 1px solid {Palette.L_BORDER_FOCUS};
                background-color: {Palette.L_INPUT_FOCUS};
            }}
        """
        
        dark = f"""
            QWidget {{
                background-color: {Palette.D_BG_MAIN};
                color: {Palette.D_TEXT_MAIN};
                font-family: '{Palette.FONT_MAIN}';
                font-size: {Palette.FONT_SIZE};
            }}
            QFrame {{
                border: 0px solid #444444;
                border-radius: 6px;
                background-color: {Palette.D_BG_FRAME};
            }}
            QPushButton {{
                background-color: {Palette.D_BTN_BG};
                color: {Palette.D_TEXT_SEC};
                border-radius: 6px;
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: {Palette.D_BTN_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {Palette.D_BTN_PRESS};
            }}
            QLineEdit {{
                background-color: {Palette.D_INPUT_BG};
                color: {Palette.D_TEXT_SEC};
                padding: 8px;
                border-radius: 6px;
                border: 0px solid {Palette.D_BORDER};
            }}
            QLabel {{
                color: {Palette.D_TEXT_SEC};
            }}
            QPlainTextEdit {{
                background-color: {Palette.D_INPUT_BG};
                color: {Palette.D_TEXT_SEC};
                font-family: '{Palette.FONT_MAIN}';
                font-size: {Palette.FONT_SIZE};
                border: 0px solid {Palette.L_BORDER};
                border-radius: 6px;
                padding: 8px;
            }}
            QPlainTextEdit:hover {{
                border: 1px solid {Palette.D_BORDER_HOVER};
            }}
            QPlainTextEdit:focus {{
                border: 1px solid {Palette.D_BORDER_FOCUS};
                background-color: {Palette.D_INPUT_BG};
            }}
        """

    # =========================================================
    # 2. FRAMES
    # =========================================================
    class Frame:
        # 1. Standard Background Frame (Light Mode - White)
        # Old Name: frameBckgStyle
        content_light = f'''
            QFrame {{
                background-color: {Palette.L_BG_FRAME_1};
                border: 0px solid #CCCCCC;
                border-radius: 12px;
            }}
        '''

        # 2. Container/Button Frame (Light Mode - Off-White)
        # Old Name: frameButtonStyle
        container_light = f'''
            QFrame {{
                background-color: {Palette.L_BG_FRAME_2};
                border: 0px solid #BBBBBB;
                border-radius: 12px;
            }}
        '''

        # 3. Standard Background Frame (Dark Mode - Grey)
        # Old Name: DframeBckgStyle
        content_dark = f'''
            QFrame {{
                background-color: {Palette.D_BG_FRAME_1};
                border: 0px solid {Palette.D_BORDER};
                border-radius: 12px;
            }}
        '''

        # 4. Container/Button Frame (Dark Mode - Darker Grey)
        # Old Name: DframeButtonStyle
        container_dark = f'''
            QFrame {{
                background-color: {Palette.D_BG_FRAME_2};
                border: 0px solid #BBBBBB;
                border-radius: 12px;
            }}
        '''

    # =========================================================
    # 3. BUTTONS
    # =========================================================
    class Button:
        # Standard Grey Button (Light Mode)
        simple_light = f'''
            QPushButton {{
                background-color: {Palette.L_BTN_BG};
                color: {Palette.L_TEXT_SEC};
                border-radius: 6px;
                padding: 8px;
                border: 0px solid #CCCCCC;
            }}
            QPushButton:hover {{ background-color: {Palette.L_BTN_HOVER}; }}
            QPushButton:pressed {{ background-color: {Palette.L_BTN_PRESS}; }}
        '''
        
        # Pure White Button (Light Mode)
        white_light = f'''
            QPushButton {{
                background-color: {Palette.L_BG_FRAME_1};
                color: {Palette.L_TEXT_SEC};
                border-radius: 3px;
                padding: 4px;
                border: 0px solid #CCCCCC;
            }}
            QPushButton:hover {{ background-color: {Palette.L_BTN_HOVER}; }}
            QPushButton:pressed {{ background-color: {Palette.L_BTN_PRESS}; }}
        '''

        # Standard Grey Button (Dark Mode)
        simple_dark = f'''
            QPushButton {{
                background-color: {Palette.D_BTN_BG};
                color: {Palette.D_TEXT_SEC};
                border-radius: 3px;
                padding: 4px;
                border: 0px solid {Palette.D_BORDER};
            }}
            QPushButton:hover {{ background-color: {Palette.D_BTN_HOVER}; }}
            QPushButton:pressed {{ background-color: {Palette.D_BTN_PRESS}; }}
        '''

        # --- Functional Status Buttons ---
        start = f'''
            QPushButton {{
                background-color: {Palette.STATUS_GREEN};
                color: #FFFFFF;
                border-radius: 4px;
                padding: 8px;
                border: none;
            }}
            QPushButton:hover {{ background-color: #45A049; }}
            QPushButton:pressed {{ background-color: #388E3C; }}
        '''

        stop = f'''
            QPushButton {{
                background-color: {Palette.STATUS_RED};
                color: #FFFFFF;
                border-radius: 4px;
                padding: 8px;
                border: none;
            }}
            QPushButton:hover {{ background-color: #E53935; }}
            QPushButton:pressed {{ background-color: #D32F2F; }}
        '''

        reset = f'''
            QPushButton {{
                background-color: {Palette.STATUS_YELLOW};
                color: #FFFFFF;
                border-radius: 4px;
                padding: 8px;
                border: none;
            }}
            QPushButton:hover {{ background-color: #FFB300; }}
            QPushButton:pressed {{ background-color: #FFA000; }}
        '''
        
        disabled = f'''
            QPushButton {{
                background-color: {Palette.L_BG_FRAME_1};
                color: {Palette.L_TEXT_MAIN};
                border-radius: 4px;
                padding: 8px;
                border: none;
            }}
            ACCENT_BLUE
        '''
        
        suggested = f'''
            QPushButton {{
                background-color: #00ADFB;
                color: #FFFFFF;
                border-radius: 4px;
                padding: 8px;
                border: none;
            }}
            QPushButton:hover {{ background-color: #7FD7FF; }}
            QPushButton:pressed {{ background-color: #008BD9; }}
        '''

    # =========================================================
    # 4. INPUTS & TEXT
    # =========================================================
    class Input:
        # Line Edit (Single line)
        line_edit_light = f'''
            QLineEdit {{
                background-color: {Palette.L_BG_FRAME_1};
                color: {Palette.L_TEXT_SEC};
                padding: 8px;
                border-radius: 6px;
                border: 0px solid {Palette.L_BORDER};
            }}
        '''

        line_edit_dark = f'''
            QLineEdit {{
                background-color: #5A5A5A;
                color: {Palette.D_TEXT_SEC};
                padding: 8px;
                border-radius: 6px;
                border: 0px solid {Palette.D_BORDER};
            }}
        '''

        # Plain Text Edit (Multi line)
        text_area_light = f'''
            QPlainTextEdit {{
                background-color: {Palette.L_BG_FRAME_1};
                color: {Palette.L_TEXT_MAIN};
                font-family: '{Palette.FONT_MAIN}';
                font-size: {Palette.FONT_SIZE};
                border: 0px solid {Palette.L_BORDER};
                border-radius: 6px;
                padding: 8px;
            }}
            QPlainTextEdit:hover {{ border: 1px solid #BBBBBB; }}
            QPlainTextEdit:focus {{ border: 1px solid #8F8F8F; background-color: #F9F9F9; }}
        '''
        
        text_area_dark = f'''
            QPlainTextEdit {{
                background-color: #5A5A5A;
                color: {Palette.D_TEXT_SEC};
                font-family: '{Palette.FONT_MAIN}';
                font-size: {Palette.FONT_SIZE};
                border: 0px solid {Palette.L_BORDER};
                border-radius: 6px;
                padding: 8px;
            }}
            QPlainTextEdit:hover {{ border: 1px solid #BBBBBB; }}
            QPlainTextEdit:focus {{ border: 1px solid #8F8F8F; background-color: #5A5A5A; }}
        '''

        # Spinbox & Combobox
        spinbox_light = f'''
            QSpinBox {{
                background-color: {Palette.L_BG_FRAME_1};
                color: {Palette.L_TEXT_SEC};
                padding: 8px;
                border-radius: 6px;
                border: 0px solid {Palette.L_BORDER};
            }}
        '''
        spinbox_dark = f'''
            QSpinBox {{
                background-color: {Palette.D_BG_FRAME_1};
                color: {Palette.D_TEXT_SEC};
                padding: 8px;
                border-radius: 6px;
                border: 0px solid {Palette.D_BORDER};
            }}
        '''
        
        combobox_light = f'''
            QComboBox {{
                background-color: #F8F8F8;
                color: {Palette.L_TEXT_SEC};
                border-radius: 3px;
                padding: 4px;
                border: 1px solid #CCCCCC;
            }}
        '''
        combobox_dark = f'''
            QComboBox {{
                background-color: {Palette.D_BG_FRAME_1};
                color: {Palette.D_TEXT_SEC};
                border-radius: 3px;
                padding: 4px;
                border: 1px solid {Palette.D_BORDER};
            }}
        '''

    # =========================================================
    # 5. SLIDERS & TOGGLES
    # =========================================================
    class Slider:
        # Standard Slider (Blue/Teal)
        standard_light = f'''
            QSlider::groove:horizontal {{
                border: 0px solid #999999;
                height: 12px;
                background: rgb(225, 225, 235);
                margin: 2px 0;
                border-radius: 7px;
            }}
            QSlider::handle:horizontal {{
                background: {Palette.ACCENT_BLUE};
                border: 0px;
                width: 24px;
                height: 24px;
                margin: -5px 0; 
                border-radius: 12px;
            }}
            QSlider::sub-page:horizontal {{
                background: {Palette.ACCENT_TEAL};
                border: 0px solid #999999;
                height: 12px;
                margin: 2px 0;
                border-radius: 7px;
            }}
        '''

        standard_dark = f'''
            QSlider::groove:horizontal {{
                border: 0px solid #444444;
                height: 12px;
                background: #444444;
                margin: 2px 0;
                border-radius: 7px;
            }}
            QSlider::handle:horizontal {{
                background: #666666;
                width: 24px;
                height: 24px;
                margin: -5px 0;
                border-radius: 12px;
            }}
            QSlider::sub-page:horizontal {{
                background: {Palette.ACCENT_TEAL};
                border: 0px solid #999999;
                height: 12px;
                margin: 2px 0;
                border-radius: 7px;
            }}
        '''

        # On/Off Toggle Switch Style
        toggle_switch = f'''
            QCheckBox::indicator {{
                width: 40px;
                height: 20px;
                border-radius: 10px;
                background-color: {Palette.STATUS_GREY};
                border: 1px solid #AAAAAA;
            }}
            QCheckBox::indicator:checked {{
                background-color: {Palette.STATUS_GREEN};
                border: 1px solid #AAAAAA;
            }}
            QCheckBox::indicator:checked:hover {{
                background-color: #45A049;
            }}
            QCheckBox::indicator::unchecked:hover {{
                background-color: #D0D0D0;
            }}
            QCheckBox::indicator:before {{
                content: '';
                position: absolute;
                width: 18px;
                height: 18px;
                background-color: #FFFFFF;
                border-radius: 9px;
                top: 1px;
                left: 1px;
                transition: all 0.3s ease;
            }}
            QCheckBox::indicator:checked:before {{
                left: 20px;
            }}
        '''

    # =========================================================
    # 6. LABELS & UTILS
    # =========================================================
    class Label:
        title_light = f'''
            QLabel {{
                font-size: 12px;
                font-weight: bold;
                color: {Palette.L_TEXT_SEC};
                letter-spacing: 0px;
                padding: 5px;
                margin: 1px 0;
            }}
        '''
        
        title_dark = f'''
            QLabel {{
                font-size: 12px;
                font-weight: bold;
                color: {Palette.D_TEXT_MAIN};
                letter-spacing: 0px;
                padding: 5px;
                margin: 1px 0;
            }}
        '''
        
        frequency_big = f'''
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {Palette.L_TEXT_SEC};
                letter-spacing: 0px;
                padding: 5px;
                margin: 1px 0;
            }}
        '''

    class Scroll:
        transparent = '''
            QScrollArea { background: transparent; border: none; }
            QScrollArea > QWidget { background: transparent; }
            QScrollArea > QWidget > QWidget { background: transparent; }
            
            QScrollBar:vertical {
                background-color: transparent;
                width: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #8F8F8F;
                min-height: 20px;
                max-height: 100px;
                border-radius: 3px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
        '''
        
        Htransparent = '''
            QScrollArea { background: transparent; border: none; }
            QScrollArea > QWidget { background: transparent; }
            QScrollArea > QWidget > QWidget { background: transparent; }
            
            QScrollBar:horizontal {
                background-color: transparent;
                height: 6px;       /* Changed width to height */
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background-color: #8F8F8F;
                min-width: 20px;   /* Changed min-height to min-width */
                border-radius: 3px;
            }
            /* Fixed selectors to :horizontal */
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }
        '''
