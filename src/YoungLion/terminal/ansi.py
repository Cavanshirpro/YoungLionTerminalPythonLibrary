"""
ansi.py

A comprehensive ANSI terminal control library for styling and managing the terminal.
Provides:

— SGR Styling (Select Graphic Rendition):
   • Color: standard & bright foreground + extended 256‑color / TrueColor methods  
   • BackgroundColor: standard & bright background + extended 256‑color / TrueColor methods  
   • TextStyle: bold, faint, italic, underline, blink, reverse, conceal, crossed‑out with on/off codes  
   • Decoration: framing, encircling, overlining with on/off codes  
   • Ideographic: ideogram annotations (underline, double‑underline, overline, double‑overline, stress)  
   • Font: primary & alternative fonts (10–19) with reset  

— CursorControl:
   • Movement: up/down/forward/back, next/previous line, absolute positioning  
   • Save/restore position, report position, hide/show cursor  

— ScreenControl:
   • Clear entire screen, before/after cursor, scrollback buffer  
   • Clear current line, before/after cursor  
   • Define/reset scroll region, scroll up/down  

— BufferControl:
   • Switch between main and alternate screen buffers (DEC & legacy)  

— LegacyCursorControl:
   • Legacy save/restore cursor (DECSC/DECRC)  

— Utility:
   • clear(): clear screen and move cursor to top‑left  

"""
from YoungLion.DataModel import enable_ansi

class Color:
    """Standard and bright foreground colors, plus extended color methods."""
    BLACK        = "\033[30m"  # Standard black
    RED          = "\033[31m"  # Standard red
    GREEN        = "\033[32m"  # Standard green
    YELLOW       = "\033[33m"  # Standard yellow
    BLUE         = "\033[34m"  # Standard blue
    MAGENTA      = "\033[35m"  # Standard magenta
    CYAN         = "\033[36m"  # Standard cyan
    WHITE        = "\033[37m"  # Standard white

    BRIGHT_BLACK   = "\033[90m"  # Bright black (gray)
    BRIGHT_RED     = "\033[91m"  # Bright red
    BRIGHT_GREEN   = "\033[92m"  # Bright green
    BRIGHT_YELLOW  = "\033[93m"  # Bright yellow
    BRIGHT_BLUE    = "\033[94m"  # Bright blue
    BRIGHT_MAGENTA = "\033[95m"  # Bright magenta
    BRIGHT_CYAN    = "\033[96m"  # Bright cyan
    BRIGHT_WHITE   = "\033[97m"  # Bright white

    RESET_ALL     = "\033[0m"   # Reset all attributes (color, style, decoration, etc.)
    RESET_FG      = "\033[39m"  # Reset foreground color to default

    @staticmethod
    def extended_256(code: int) -> str:
        """
        256‐color mode: select from palette index 0–255.
        Usage: print(Color.extended_256(202) + "Hello" + Color.RESET_ALL)
        """
        return f"\033[38;5;{code}m"

    @staticmethod
    def truecolor(r: int, g: int, b: int) -> str:
        """
        24‐bit TrueColor mode: specify RGB.
        Usage: print(Color.truecolor(255,100,0) + "Hello" + Color.RESET_ALL)
        """
        return f"\033[38;2;{r};{g};{b}m"


class BackgroundColor:
    """Standard and bright background colors, plus extended color methods."""
    BLACK        = "\033[40m"  # Standard black
    RED          = "\033[41m"  # Standard red
    GREEN        = "\033[42m"  # Standard green
    YELLOW       = "\033[43m"  # Standard yellow
    BLUE         = "\033[44m"  # Standard blue
    MAGENTA      = "\033[45m"  # Standard magenta
    CYAN         = "\033[46m"  # Standard cyan
    WHITE        = "\033[47m"  # Standard white

    BRIGHT_BLACK   = "\033[100m"  # Bright black (gray)
    BRIGHT_RED     = "\033[101m"  # Bright red
    BRIGHT_GREEN   = "\033[102m"  # Bright green
    BRIGHT_YELLOW  = "\033[103m"  # Bright yellow
    BRIGHT_BLUE    = "\033[104m"  # Bright blue
    BRIGHT_MAGENTA = "\033[105m"  # Bright magenta
    BRIGHT_CYAN    = "\033[106m"  # Bright cyan
    BRIGHT_WHITE   = "\033[107m"  # Bright white

    RESET_ALL     = "\033[0m"   # Reset all attributes
    RESET_BG      = "\033[49m"  # Reset background color to default

    @staticmethod
    def extended_256(code: int) -> str:
        """
        256‐color mode for background: palette index 0–255.
        """
        return f"\033[48;5;{code}m"

    @staticmethod
    def truecolor(r: int, g: int, b: int) -> str:
        """
        24‐bit TrueColor mode for background.
        """
        return f"\033[48;2;{r};{g};{b}m"


class TextStyle:
    """Text styling: intensity, emphasis, blinking, reversal, concealment, and strike."""
    BOLD            = "\033[1m"   # Bold / increased intensity
    FAINT           = "\033[2m"   # Faint / decreased intensity
    ITALIC          = "\033[3m"   # Italic text
    UNDERLINE       = "\033[4m"   # Underlined text
    SLOW_BLINK      = "\033[5m"   # Slow blinking text
    RAPID_BLINK     = "\033[6m"   # Rapid blinking text
    REVERSE         = "\033[7m"   # Swap foreground/background
    CONCEAL         = "\033[8m"   # Conceal (hide) text
    CROSSED_OUT     = "\033[9m"   # Strikethrough

    # Reset / turn‐off codes for each style
    RESET_ALL            = "\033[0m"  # All styles off
    RESET_INTENSITY      = "\033[22m" # Normal intensity (turn off bold/faint)
    RESET_ITALIC         = "\033[23m" # Turn off italic
    RESET_UNDERLINE      = "\033[24m" # Turn off underline
    RESET_BLINK          = "\033[25m" # Turn off blinking
    RESET_REVERSE        = "\033[27m" # Turn off reverse video
    RESET_CONCEAL        = "\033[28m" # Turn off conceal
    RESET_CROSSED_OUT    = "\033[29m" # Turn off strikethrough


class Decoration:
    """
    Box‐drawing decorations: framing, encircling, overlining.
    Note: not all terminals support these.
    """
    FRAME         = "\033[51m"  # Frame text
    ENCIRCLE      = "\033[52m"  # Encircle text
    OVERLINE      = "\033[53m"  # Overline text

    RESET_ALL         = "\033[0m"  # All decorations off
    RESET_FRAME_ENC   = "\033[54m" # Turn off frame/encircle
    RESET_OVERLINE    = "\033[55m" # Turn off overline


class Ideographic:
    """
    Ideogram annotations (JIS): underline, double‐underline, overline, double‐overline, stress.
    Support varies by terminal.
    """
    IDEO_UNDERLINE           = "\033[60m"  # Ideogram underline or right side line
    IDEO_DOUBLE_UNDERLINE    = "\033[61m"  # Ideogram double underline or right side double line
    IDEO_OVERLINE            = "\033[62m"  # Ideogram overline or left side line
    IDEO_DOUBLE_OVERLINE     = "\033[63m"  # Ideogram double overline or left side double line
    IDEO_STRESS_MARKING      = "\033[64m"  # Ideogram stress marking

    RESET_ALL         = "\033[0m"  # All ideographic features off
    # Note: specific off‐codes for ideographic are not standardized beyond RESET_ALL.


class Font:
    """
    Select alternate fonts (rarely supported in modern emulators).
    """
    DEFAULT      = "\033[10m"  # Primary (default) font
    ALT_1        = "\033[11m"  # Alternative font 1
    ALT_2        = "\033[12m"  # Alternative font 2
    ALT_3        = "\033[13m"  # Alternative font 3
    ALT_4        = "\033[14m"  # Alternative font 4
    ALT_5        = "\033[15m"  # Alternative font 5
    ALT_6        = "\033[16m"  # Alternative font 6
    ALT_7        = "\033[17m"  # Alternative font 7
    ALT_8        = "\033[18m"  # Alternative font 8
    ALT_9        = "\033[19m"  # Alternative font 9

    RESET_ALL    = "\033[0m"   # Reset to default font


class CursorControl:
    """
    ANSI escape sequences for cursor movement and positioning.
    """

    @staticmethod
    def up(n=1): return f"\033[{n}A"              # Move cursor up by n lines
    @staticmethod
    def down(n=1): return f"\033[{n}B"            # Move cursor down by n lines
    @staticmethod
    def forward(n=1): return f"\033[{n}C"         # Move cursor right by n columns
    @staticmethod
    def back(n=1): return f"\033[{n}D"            # Move cursor left by n columns
    @staticmethod
    def next_line(n=1): return f"\033[{n}E"       # Move cursor down n lines and to the beginning
    @staticmethod
    def previous_line(n=1): return f"\033[{n}F"   # Move cursor up n lines and to the beginning
    @staticmethod
    def horizontal(n=1): return f"\033[{n}G"      # Move cursor to column n in the current row
    @staticmethod
    def position(row=1, col=1): return f"\033[{row};{col}H"  # Move cursor to (row, col)
    save_position = "\033[s"                      # Save current cursor position
    restore_position = "\033[u"                   # Restore saved cursor position
    report_position = "\033[6n"                   # Request cursor position (will be sent by terminal)
    hide = "\033[?25l"                            # Hide cursor
    show = "\033[?25h"                            # Show cursor
    move_top_left_corner = "\033[f"                  # Move cursor to top-left corner (1,1)


class ScreenControl:
    """
    ANSI escape sequences for clearing the screen and lines.
    """

    clear_screen = "\033[2J"                      # Clear entire screen
    clear_screen_before = "\033[1J"               # Clear screen before cursor
    clear_screen_after = "\033[0J"                # Clear screen after cursor
    clear_line = "\033[2K"                        # Clear entire current line
    clear_line_before = "\033[1K"                 # Clear line before cursor
    clear_line_after = "\033[0K"                  # Clear line after cursor
    clear_all = "\033[3J"                         # Clear entire screen including scrollback

    @staticmethod
    def scroll_region(top=1, bottom=24): return f"\033[{top};{bottom}r"  # Define scroll region
    reset_scroll = "\033[r"                       # Reset scroll region to full screen
    scroll_up = "\033M"                           # Scroll display up one line
    scroll_down = "\033D"                         # Scroll display down one line


class BufferControl:
    """
    ANSI escape sequences for switching between screen buffers.
    Useful for full-screen applications.
    """

    enable_alternate = "\033[?1049h"              # Switch to alternate screen buffer
    disable_alternate = "\033[?1049l"             # Return to main screen buffer
    enable_alternate_legacy = "\033[?47h"         # Legacy alternate screen (older support)
    disable_alternate_legacy = "\033[?47l"        # Legacy return to main screen


class LegacyCursorControl:
    """
    Legacy cursor save and restore, equivalent to `\033[s` and `\033[u`.
    """

    save = "\0337"                                # Save cursor (legacy)
    restore = "\0338"                             # Restore cursor (legacy)

if __name__=="__main__":enable_ansi()