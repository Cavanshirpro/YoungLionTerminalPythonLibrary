"""
utils.py

Advanced utility functions for ansi.py terminal control library.

Provides:
 - clear_screen(): clear screen & move cursor home
 - styled(): wrap text with multiple ANSI styles
 - print_styled(): print styled text
 - get_terminal_size(): get (columns, rows)
 - print_boxed(): draw a bordered box around text
 - progress_bar(): generate a progress bar string
 - Spinner: context‑manager spinner for long tasks
 - prompt(): styled input prompt
 - print_dict(): pretty‑print dicts with colors
 - Logger: simple colored logging (info, success, warning, error)
"""
import re
import sys
import shutil
import time
import threading
import traceback
from .ansi import *


def clear_screen() -> str:
    """
    Return ANSI sequence to clear the screen and move cursor to (1,1).
    """
    return ScreenControl.clear_screen + CursorControl.move_top_left_corner


def styled(text: str, *styles: str) -> str:
    """
    Wrap `text` with one or more ANSI SGR codes in `styles`, then reset all.
    
    Example:
        styled("Hello", Color.RED, TextStyle.BOLD)
    """
    return "".join(styles) + text + Color.RESET_ALL


def print_styled(
    *parts: str,
    styles: tuple = (),
    sep: str = " ",
    end: str = "\n",
    file=sys.stdout,
    flush: bool = False
):
    """
    Print one or more strings with ANSI styles applied.
    
    Args:
        parts: strings to print
        styles: tuple of ANSI codes (e.g. (Color.GREEN, TextStyle.UNDERLINE))
    """
    text = sep.join(parts)
    styled_text = styled(text, *styles)
    print(styled_text, end=end, file=file, flush=flush)


def get_terminal_size() -> tuple[int,int]:
    """
    Return terminal size as (columns, rows). Defaults to (80, 24).
    """
    size = shutil.get_terminal_size(fallback=(80, 24))
    return size.columns, size.lines


def print_boxed(
    text: str,
    width: int = None,
    padding: int = 1,
    border_style: str = Decoration.FRAME,
    border_color: str = Color.BRIGHT_BLUE,
    text_style: str = TextStyle.BOLD
):
    """
    Print `text` inside a box with borders.
    
    Args:
        text: multi-line string
        width: total inner width (auto if None)
        padding: spaces on left/right of text
        border_style: Decoration.FRAME or custom
        border_color: Color.* code
        text_style: TextStyle.* code
    """
    lines = text.splitlines() or [""]
    content_width = max(len(line) for line in lines)
    inner_width = width or content_width
    total_width = inner_width + padding * 2
    hline = "─" * total_width

    top = f"{border_color}┌{hline}┐{Color.RESET_ALL}"
    bottom = f"{border_color}└{hline}┘{Color.RESET_ALL}"
    print(top)
    for line in lines:
        trimmed = line[:inner_width].ljust(inner_width)
        print(
            f"{border_color}│{Color.RESET_ALL}"
            + " " * padding
            + styled(trimmed, text_style)
            + " " * padding
            + f"{border_color}│{Color.RESET_ALL}"
        )
    print(bottom)

class Spinner:
    """
    A context‑manager terminal spinner.

    Usage:
        with Spinner("Loading", style=Color.BRIGHT_YELLOW):
            long_running_task()
    """
    _cycle = ["|", "/", "-", "\\"]
    
    def __init__(self, text: str = "", delay: float = 0.1, style: str = Color.BRIGHT_CYAN):
        self.text = text
        self.delay = delay
        self.style = style
        self._running = False
        self._thread = None

    def _spinner_task(self):
        idx = 0
        while self._running:
            frame = self._cycle[idx % len(self._cycle)]
            sys.stdout.write(f"\r{styled(frame, self.style)} {self.text}")
            sys.stdout.flush()
            time.sleep(self.delay)
            idx += 1
        sys.stdout.write("\r" + " " * (len(self.text) + 2) + "\r")
        sys.stdout.flush()

    def __enter__(self):
        self._running = True
        self._thread = threading.Thread(target=self._spinner_task)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._running = False
        self._thread.join()


def prompt(text: str, *styles: str, end: str = ": ") -> str:
    """
    Display a styled prompt and return user input.
    
    Example:
        name = prompt("Enter your name", Color.BRIGHT_MAGENTA, TextStyle.BOLD)
    """
    prompt_text = styled(text, *styles) + end
    return input(prompt_text)


def print_dict(
    d: dict,
    key_style: str = Color.BRIGHT_MAGENTA,
    val_style: str = Color.BRIGHT_GREEN,
    indent: int = 0
):
    """
    Pretty‑print a nested dictionary with colored keys and values.
    """
    for k, v in d.items():
        key_str = " " * indent + styled(str(k), key_style)
        if isinstance(v, dict):
            print(f"{key_str}:")
            print_dict(v, key_style, val_style, indent + 2)
        else:
            print(f"{key_str}: {styled(str(v), val_style)}")


class Logger:
    """
    Advanced colored logger with levels and optional file output.

    Features:
      - Levels: DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL
      - Timestamp prefix (configurable format)
      - Optional logger name/context
      - Level filtering (only messages ≥ min_level are emitted)
      - Color on/off toggle
      - Thread‑safe
      - File logging (ANSI codes stripped)
      - Exception logging with traceback
    """

    # level_name: (numeric_level, color, label)
    LEVELS = {
        "DEBUG":    (10, Color.CYAN,          "[DEBUG]"),
        "INFO":     (20, Color.BRIGHT_BLUE,   "[INFO]"),
        "SUCCESS":  (25, Color.BRIGHT_GREEN,  "[SUCCESS]"),
        "WARNING":  (30, Color.BRIGHT_YELLOW, "[WARNING]"),
        "ERROR":    (40, Color.BRIGHT_RED,    "[ERROR]"),
        "CRITICAL": (50, Color.BRIGHT_MAGENTA,"[CRITICAL]"),
    }

    # regex to strip ANSI sequences when writing to file
    ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*[mK]')

    def __init__(
        self,
        name: str = None,
        level: str = "DEBUG",
        *,
        show_time: bool = True,
        timestamp_format: str = "%Y-%m-%d %H:%M:%S",
        show_level: bool = True,
        show_name: bool = False,
        use_colors: bool = True,
        log_to_file: bool = False,
        file_path: str = "app.log",
        stream = None
    ):
        """
        Args:
          name: optional logger name (e.g. module or app name)
          level: minimum level name (DEBUG, INFO, …)
          show_time: prepend timestamp
          timestamp_format: strftime format for timestamp
          show_level: include level label
          show_name: include logger name
          use_colors: wrap labels in ANSI colors
          log_to_file: also append plain text to file_path
          file_path: path to logfile (appended)
          stream: output stream for console (defaults to stdout for ≤WARNING, stderr for ERROR+)
        """
        self.name = name
        lvl = level.upper()
        if lvl not in self.LEVELS:
            raise ValueError(f"Unknown log level: {level}")
        self.level_name = lvl
        self.level_num = self.LEVELS[lvl][0]

        self.show_time = show_time
        self.timestamp_format = timestamp_format
        self.show_level = show_level
        self.show_name = show_name
        self.use_colors = use_colors

        self.log_to_file = log_to_file
        self.file_path = file_path

        self.stream = stream  # if None, determined per‑message
        self._lock = threading.Lock()

    def set_level(self, level: str):
        """Change the minimum level at runtime."""
        lvl = level.upper()
        if lvl not in self.LEVELS:
            raise ValueError(f"Unknown log level: {level}")
        self.level_name = lvl
        self.level_num = self.LEVELS[lvl][0]

    def enable_colors(self):   self.use_colors = True
    def disable_colors(self):  self.use_colors = False

    def _should_log(self, msg_level_num: int) -> bool:
        return msg_level_num >= self.level_num

    def _format(self, level_name: str, message: str) -> str:
        parts = []
        # timestamp
        if self.show_time:
            now = time.strftime(self.timestamp_format)
            parts.append(f"[{now}]")
        # level label
        if self.show_level:
            _, color, label = self.LEVELS[level_name]
            if self.use_colors:
                parts.append(styled(label, color, TextStyle.BOLD))
            else:
                parts.append(label)
        # logger name
        if self.show_name and self.name:
            parts.append(f"[{self.name}]")
        # the actual message
        parts.append(message)
        return " ".join(parts)

    def _write(self, text: str, level_name: str):
        # choose stream if not explicitly set
        out = self.stream
        if out is None:
            # errors and above to stderr, others to stdout
            lvl_num = self.LEVELS[level_name][0]
            out = sys.stderr if lvl_num >= self.LEVELS["ERROR"][0] else sys.stdout

        with self._lock:
            print(text, file=out)
            out.flush()

            # file logging (strip ANSI)
            if self.log_to_file:
                plain = self.ANSI_ESCAPE.sub("", text)
                with open(self.file_path, "a", encoding="utf-8") as f:
                    f.write(plain + "\n")

    def _log(self, level_name: str, message: str):
        lvl_num, _, _ = self.LEVELS[level_name]
        if not self._should_log(lvl_num):
            return
        formatted = self._format(level_name, message)
        self._write(formatted, level_name)

    # convenience methods:
    def debug(self, message: str):    self._log("DEBUG", message)
    def info(self, message: str):     self._log("INFO", message)
    def success(self, message: str):  self._log("SUCCESS", message)
    def warning(self, message: str):  self._log("WARNING", message)
    def error(self, message: str):    self._log("ERROR", message)
    def critical(self, message: str): self._log("CRITICAL", message)

    def exception(self, message: str):
        """
        Log an ERROR with traceback. Should be called from an except block.
        """
        tb = traceback.format_exc()
        full = f"{message}\n{tb}"
        self._log("ERROR", full)
