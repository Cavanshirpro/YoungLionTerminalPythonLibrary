"""ANSI primitives and terminal capability helpers for YoungLion Terminal.

The module is intentionally self-contained.  YoungLion v0.1 no longer exposes
``enable_ansi`` from ``YoungLion.DataModel``, so terminal capability detection
and the Windows VT-mode compatibility shim live here instead.
"""
from __future__ import annotations

import contextlib
import os
import re
import shutil
import sys
from dataclasses import dataclass
from typing import IO, Iterator

ANSI_ESCAPE_RE = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07]*(?:\x07|\x1b\\))")


def _clamp_byte(value: int, name: str) -> int:
    value = int(value)
    if not 0 <= value <= 255:
        raise ValueError(f"{name} must be between 0 and 255")
    return value


def enable_ansi(stream: IO[str] | None = None) -> bool:
    """Best-effort ANSI/VT enablement without depending on YoungLion internals.

    On POSIX terminals ANSI is already available.  On modern Windows consoles
    this enables ``ENABLE_VIRTUAL_TERMINAL_PROCESSING`` for stdout/stderr.
    The function is idempotent and returns whether ANSI output is usable.
    """
    stream = stream or sys.stdout
    if os.environ.get("NO_COLOR") is not None:
        return False
    if os.name != "nt":
        return bool(getattr(stream, "isatty", lambda: False)()) and os.environ.get("TERM") != "dumb"

    try:
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.windll.kernel32
        handle_id = -12 if stream is sys.stderr else -11
        handle = kernel32.GetStdHandle(handle_id)
        if handle in (0, -1):
            return False
        mode = wintypes.DWORD()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        if not (mode.value & ENABLE_VIRTUAL_TERMINAL_PROCESSING):
            if not kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING):
                return False
        return True
    except Exception:
        return False


def supports_ansi(stream: IO[str] | None = None) -> bool:
    """Return whether *stream* is likely to render ANSI escape sequences."""
    stream = stream or sys.stdout
    if os.environ.get("NO_COLOR") is not None or os.environ.get("TERM") == "dumb":
        return False
    if os.environ.get("FORCE_COLOR") not in (None, "", "0"):
        return True
    if not bool(getattr(stream, "isatty", lambda: False)()):
        return False
    return enable_ansi(stream) if os.name == "nt" else True


def strip_ansi(text: str) -> str:
    """Remove CSI/OSC ANSI escape sequences from *text*."""
    return ANSI_ESCAPE_RE.sub("", str(text))


class Color:
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    RESET_ALL = "\033[0m"
    RESET_FG = "\033[39m"

    @staticmethod
    def extended_256(code: int) -> str:
        return f"\033[38;5;{_clamp_byte(code, 'code')}m"

    @staticmethod
    def truecolor(r: int, g: int, b: int) -> str:
        return f"\033[38;2;{_clamp_byte(r, 'r')};{_clamp_byte(g, 'g')};{_clamp_byte(b, 'b')}m"


class BackgroundColor:
    BLACK = "\033[40m"
    RED = "\033[41m"
    GREEN = "\033[42m"
    YELLOW = "\033[43m"
    BLUE = "\033[44m"
    MAGENTA = "\033[45m"
    CYAN = "\033[46m"
    WHITE = "\033[47m"
    BRIGHT_BLACK = "\033[100m"
    BRIGHT_RED = "\033[101m"
    BRIGHT_GREEN = "\033[102m"
    BRIGHT_YELLOW = "\033[103m"
    BRIGHT_BLUE = "\033[104m"
    BRIGHT_MAGENTA = "\033[105m"
    BRIGHT_CYAN = "\033[106m"
    BRIGHT_WHITE = "\033[107m"
    RESET_ALL = "\033[0m"
    RESET_BG = "\033[49m"

    @staticmethod
    def extended_256(code: int) -> str:
        return f"\033[48;5;{_clamp_byte(code, 'code')}m"

    @staticmethod
    def truecolor(r: int, g: int, b: int) -> str:
        return f"\033[48;2;{_clamp_byte(r, 'r')};{_clamp_byte(g, 'g')};{_clamp_byte(b, 'b')}m"


class TextStyle:
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    SLOW_BLINK = "\033[5m"
    RAPID_BLINK = "\033[6m"
    REVERSE = "\033[7m"
    CONCEAL = "\033[8m"
    CROSSED_OUT = "\033[9m"
    RESET_ALL = "\033[0m"
    RESET_INTENSITY = "\033[22m"
    RESET_ITALIC = "\033[23m"
    RESET_UNDERLINE = "\033[24m"
    RESET_BLINK = "\033[25m"
    RESET_REVERSE = "\033[27m"
    RESET_CONCEAL = "\033[28m"
    RESET_CROSSED_OUT = "\033[29m"


class Decoration:
    FRAME = "\033[51m"
    ENCIRCLE = "\033[52m"
    OVERLINE = "\033[53m"
    RESET_ALL = "\033[0m"
    RESET_FRAME_ENC = "\033[54m"
    RESET_OVERLINE = "\033[55m"


class Ideographic:
    IDEO_UNDERLINE = "\033[60m"
    IDEO_DOUBLE_UNDERLINE = "\033[61m"
    IDEO_OVERLINE = "\033[62m"
    IDEO_DOUBLE_OVERLINE = "\033[63m"
    IDEO_STRESS_MARKING = "\033[64m"
    RESET_ALL = "\033[0m"


class Font:
    DEFAULT = "\033[10m"
    ALT_1 = "\033[11m"
    ALT_2 = "\033[12m"
    ALT_3 = "\033[13m"
    ALT_4 = "\033[14m"
    ALT_5 = "\033[15m"
    ALT_6 = "\033[16m"
    ALT_7 = "\033[17m"
    ALT_8 = "\033[18m"
    ALT_9 = "\033[19m"
    RESET_ALL = "\033[0m"


class CursorControl:
    @staticmethod
    def up(n: int = 1) -> str: return f"\033[{n}A"
    @staticmethod
    def down(n: int = 1) -> str: return f"\033[{n}B"
    @staticmethod
    def forward(n: int = 1) -> str: return f"\033[{n}C"
    @staticmethod
    def back(n: int = 1) -> str: return f"\033[{n}D"
    @staticmethod
    def next_line(n: int = 1) -> str: return f"\033[{n}E"
    @staticmethod
    def previous_line(n: int = 1) -> str: return f"\033[{n}F"
    @staticmethod
    def horizontal(n: int = 1) -> str: return f"\033[{n}G"
    @staticmethod
    def position(row: int = 1, col: int = 1) -> str: return f"\033[{row};{col}H"
    save_position = "\033[s"
    restore_position = "\033[u"
    report_position = "\033[6n"
    hide = "\033[?25l"
    show = "\033[?25h"
    move_top_left_corner = "\033[f"


class ScreenControl:
    clear_screen = "\033[2J"
    clear_screen_before = "\033[1J"
    clear_screen_after = "\033[0J"
    clear_line = "\033[2K"
    clear_line_before = "\033[1K"
    clear_line_after = "\033[0K"
    clear_all = "\033[3J"

    @staticmethod
    def scroll_region(top: int = 1, bottom: int = 24) -> str: return f"\033[{top};{bottom}r"
    reset_scroll = "\033[r"
    scroll_up = "\033M"
    scroll_down = "\033D"


class BufferControl:
    enable_alternate = "\033[?1049h"
    disable_alternate = "\033[?1049l"
    enable_alternate_legacy = "\033[?47h"
    disable_alternate_legacy = "\033[?47l"


class LegacyCursorControl:
    save = "\0337"
    restore = "\0338"


@dataclass(frozen=True, slots=True)
class TerminalCapabilities:
    columns: int
    rows: int
    is_tty: bool
    ansi: bool
    color256: bool
    truecolor: bool
    unicode: bool


def detect_capabilities(stream: IO[str] | None = None) -> TerminalCapabilities:
    """Inspect terminal size and broadly useful rendering capabilities."""
    stream = stream or sys.stdout
    size = shutil.get_terminal_size(fallback=(80, 24))
    is_tty = bool(getattr(stream, "isatty", lambda: False)())
    ansi = supports_ansi(stream)
    term = os.environ.get("TERM", "").lower()
    colorterm = os.environ.get("COLORTERM", "").lower()
    encoding = (getattr(stream, "encoding", None) or "").lower()
    return TerminalCapabilities(
        columns=size.columns,
        rows=size.lines,
        is_tty=is_tty,
        ansi=ansi,
        color256=ansi and ("256color" in term or bool(colorterm)),
        truecolor=ansi and colorterm in {"truecolor", "24bit"},
        unicode="utf" in encoding or encoding == "",
    )


def hyperlink(text: str, url: str, *, enabled: bool = True) -> str:
    """Return an OSC-8 terminal hyperlink, or plain text when disabled."""
    if not enabled:
        return text
    return f"\033]8;;{url}\033\\{text}\033]8;;\033\\"


@contextlib.contextmanager
def hidden_cursor(stream: IO[str] | None = None) -> Iterator[None]:
    stream = stream or sys.stdout
    enabled = supports_ansi(stream)
    if enabled:
        stream.write(CursorControl.hide)
        stream.flush()
    try:
        yield
    finally:
        if enabled:
            stream.write(CursorControl.show)
            stream.flush()


@contextlib.contextmanager
def alternate_buffer(stream: IO[str] | None = None) -> Iterator[None]:
    stream = stream or sys.stdout
    enabled = supports_ansi(stream)
    if enabled:
        stream.write(BufferControl.enable_alternate)
        stream.flush()
    try:
        yield
    finally:
        if enabled:
            stream.write(BufferControl.disable_alternate)
            stream.flush()
