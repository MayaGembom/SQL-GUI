import tkinter.font as tk_font

class WindowVariables:
    WINDOW_SIZE_W = 890
    WINDOW_SIZE_H = 685
    WINDOW_SIZE = f"{WINDOW_SIZE_W}x{WINDOW_SIZE_H}"
    WINDOW_LEFT_CORNER_X = int(WINDOW_SIZE_W*0.30)
    WINDOW_LEFT_CORNER_Y = int(WINDOW_SIZE_H* 0.08)
    WINDOW_TITLE = 'Sql Queries Gui'

class Fonts:
    _FONT_FAMILY = 'Calibri'
    BUTTONS_FONT: tk_font.Font
    H1_FONT: tk_font.Font
    H2_FONT: tk_font.Font
    LABELS_FONT: tk_font.Font

    @staticmethod
    def initialize_fonts():
        """
        Function that initializes the fonts instances.

        This function is required because it is not possible to create `tkinter.font.Font`
        instance before `tkinter.Tk` instance is created.
        """
        # global BUTTONS_FONT, H1_FONT, H2_FONT, LABELS_FONT
        Fonts.BUTTONS_FONT = tk_font.Font(family=Fonts._FONT_FAMILY, size=14, weight=tk_font.BOLD)
        Fonts.H1_FONT = tk_font.Font(family=Fonts._FONT_FAMILY, size=20, weight=tk_font.BOLD)
        Fonts.H2_FONT = tk_font.Font(family=Fonts._FONT_FAMILY, size=16)
        Fonts.LABELS_FONT = tk_font.Font(family=Fonts._FONT_FAMILY, size=14)
        # Headers of the TreeView
        tk_font.nametofont("TkHeadingFont").configure(family=Fonts._FONT_FAMILY, size=18, weight=tk_font.BOLD)
        # Cells in the TreeView
        tk_font.nametofont("TkDefaultFont").configure(family=Fonts._FONT_FAMILY, size=14)


class Colors:
    WINDOW_BACKGROUND = '#e0f8f2'
    BUTTON_BACKGROUND = '#fdf9f7'
    EXCEPTION_FOREGROUND = 'red'
