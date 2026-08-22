"""High-level terminal utilities for YoungLion Terminal."""
from __future__ import annotations

import re
import sys
import time
import threading
import traceback
from collections.abc import Mapping
from typing import Any, IO, Iterable

from YoungLion import DDM, Debugger as YoungLionDebugger, Logger as YoungLionLogger

from .ansi import (
    Color,
    Decoration,
    ScreenControl,
    CursorControl,
    TextStyle,
    strip_ansi,
    supports_ansi,
)


def clear_screen() -> str:
    """Return ANSI sequence to clear the screen and move cursor home."""
    return ScreenControl.clear_screen + CursorControl.move_top_left_corner


def styled(text: str, *styles: str, enabled: bool = True) -> str:
    """Wrap *text* in ANSI styles and reset afterwards.

    ``enabled=False`` is useful for redirected output while preserving the same
    formatting call sites.
    """
    text = str(text)
    if not enabled or not styles:
        return text
    return "".join(styles) + text + Color.RESET_ALL


def print_styled(
    *parts: str,
    styles: tuple[str, ...] = (),
    sep: str = " ",
    end: str = "\n",
    file: IO[str] = sys.stdout,
    flush: bool = False,
):
    """Print one or more strings with ANSI styles applied when supported."""
    text = sep.join(str(part) for part in parts)
    print(styled(text, *styles, enabled=supports_ansi(file)), end=end, file=file, flush=flush)


def get_terminal_size() -> tuple[int, int]:
    """Return terminal size as ``(columns, rows)`` with an ``80x24`` fallback."""
    import shutil

    size = shutil.get_terminal_size(fallback=(80, 24))
    return size.columns, size.lines


def visible_len(text: str) -> int:
    """Length of terminal text excluding ANSI escape sequences."""
    return len(strip_ansi(str(text)))


def _as_mapping(value: Mapping[str, Any] | DDM) -> Mapping[str, Any]:
    if isinstance(value, DDM):
        return value.to_dict()
    if isinstance(value, Mapping):
        return value
    raise TypeError("value must be a mapping or YoungLion.DDM")


def print_boxed(
    text: str,
    width: int | None = None,
    padding: int = 1,
    border_style: str = Decoration.FRAME,
    border_color: str = Color.BRIGHT_BLUE,
    text_style: str = TextStyle.BOLD,
):
    """Print *text* inside a Unicode box.

    ``border_style`` remains accepted for v0.1 compatibility.  Unicode borders
    are used because SGR frame support is inconsistent across terminals.
    """
    del border_style
    lines = str(text).splitlines() or [""]
    content_width = max(visible_len(line) for line in lines)
    inner_width = max(0, width if width is not None else content_width)
    padding = max(0, int(padding))
    total_width = inner_width + padding * 2
    ansi = supports_ansi(sys.stdout)
    border = lambda value: styled(value, border_color, enabled=ansi)
    top = border("┌" + "─" * total_width + "┐")
    bottom = border("└" + "─" * total_width + "┘")
    print(top)
    for line in lines:
        plain = strip_ansi(line)
        trimmed = plain[:inner_width]
        body = trimmed + " " * max(0, inner_width - visible_len(trimmed))
        print(
            border("│")
            + " " * padding
            + styled(body, text_style, enabled=ansi)
            + " " * padding
            + border("│")
        )
    print(bottom)


class Spinner:
    """Thread-safe context-manager spinner with explicit completion states.

    The original ``Spinner(text, delay, style)`` call remains unchanged.
    Additional behavior is opt-in via keyword-only arguments and ``succeed`` /
    ``fail`` / ``stop``.
    """

    _cycle = ("|", "/", "-", "\\")

    def __init__(
        self,
        text: str = "",
        delay: float = 0.1,
        style: str = Color.BRIGHT_CYAN,
        *,
        frames: Iterable[str] | None = None,
        stream: IO[str] | None = None,
        clear: bool = True,
    ):
        if delay <= 0:
            raise ValueError("delay must be greater than zero")
        self.text = text
        self.delay = float(delay)
        self.style = style
        self.frames = tuple(frames or self._cycle)
        if not self.frames:
            raise ValueError("frames cannot be empty")
        self.stream = stream or sys.stdout
        self.clear = bool(clear)
        self._running = False
        self._thread: threading.Thread | None = None
        self._lock = threading.RLock()
        self._final_text: str | None = None
        self._final_style: str | None = None

    @property
    def running(self) -> bool:
        return self._running

    def _spinner_task(self):
        idx = 0
        ansi = supports_ansi(self.stream)
        while self._running:
            frame = self.frames[idx % len(self.frames)]
            rendered = styled(frame, self.style, enabled=ansi)
            with self._lock:
                self.stream.write(f"\r{rendered} {self.text}")
                self.stream.flush()
            time.sleep(self.delay)
            idx += 1
        with self._lock:
            if self.clear:
                self.stream.write("\r" + " " * (visible_len(self.text) + 4) + "\r")
            if self._final_text is not None:
                final = styled(self._final_text, self._final_style or "", enabled=ansi)
                self.stream.write(final + "\n")
            self.stream.flush()

    def start(self) -> "Spinner":
        if self._running:
            return self
        self._running = True
        self._thread = threading.Thread(target=self._spinner_task, name="YoungLionSpinner", daemon=True)
        self._thread.start()
        return self

    def stop(self, final_text: str | None = None, style: str | None = None) -> "Spinner":
        self._final_text = final_text
        self._final_style = style
        self._running = False
        if self._thread is not None and self._thread is not threading.current_thread():
            self._thread.join()
        return self

    def succeed(self, text: str | None = None) -> "Spinner":
        return self.stop(text or f"✔ {self.text}", Color.BRIGHT_GREEN)

    def fail(self, text: str | None = None) -> "Spinner":
        return self.stop(text or f"✖ {self.text}", Color.BRIGHT_RED)

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.stop()
        else:
            self.fail()
        return False


def prompt(text: str, *styles: str, end: str = ": ") -> str:
    """Display a styled prompt and return user input."""
    prompt_text = styled(text, *styles, enabled=supports_ansi(sys.stdout)) + end
    return input(prompt_text)


def print_dict(
    d: Mapping[str, Any] | DDM,
    key_style: str = Color.BRIGHT_MAGENTA,
    val_style: str = Color.BRIGHT_GREEN,
    indent: int = 0,
):
    """Pretty-print nested mappings or a :class:`YoungLion.DDM`.

    DDM support is intentionally limited to presentation helpers where a data
    model naturally behaves like a mapping; the terminal core itself does not
    depend on DDM semantics.
    """
    mapping = _as_mapping(d)
    ansi = supports_ansi(sys.stdout)
    for key, value in mapping.items():
        key_str = " " * indent + styled(str(key), key_style, enabled=ansi)
        if isinstance(value, DDM):
            value = value.to_dict()
        if isinstance(value, Mapping):
            print(f"{key_str}:")
            print_dict(value, key_style, val_style, indent + 2)
        else:
            print(f"{key_str}: {styled(str(value), val_style, enabled=ansi)}")


class Logger(YoungLionDebugger, YoungLionLogger):
    """
    Advanced colored logger with levels and optional file output.

    This is the original YoungLion Terminal Logger behavior, with compatibility
    aliases layered on top. It is an actual subclass of both YoungLion.Debugger
    and YoungLion.Logger, so it can be supplied wherever either core type is
    expected (including ``File(debug=True, debugger=...)``).

    Features:
      - Levels: DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL
      - Timestamp prefix (configurable format)
      - Optional logger name/context
      - Level filtering (only messages >= min_level are emitted)
      - Color on/off toggle
      - Thread-safe
      - File logging (ANSI codes stripped)
      - Exception logging with traceback
    """

    LEVELS = {
        "DEBUG":    (10, Color.CYAN,          "[DEBUG]"),
        "INFO":     (20, Color.BRIGHT_BLUE,   "[INFO]"),
        "SUCCESS":  (25, Color.BRIGHT_GREEN,  "[SUCCESS]"),
        "WARNING":  (30, Color.BRIGHT_YELLOW, "[WARNING]"),
        "ERROR":    (40, Color.BRIGHT_RED,    "[ERROR]"),
        "CRITICAL": (50, Color.BRIGHT_MAGENTA,"[CRITICAL]"),
    }

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
        # Terminal-owned replacement for the removed YoungLion.DataModel helper.
        from .ansi import enable_ansi
        self.isEnableANSI = enable_ansi(stream or sys.stdout)
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

        self.stream = stream
        self._lock = threading.Lock()

        # Compatibility state required by YoungLion.Debugger / YoungLion.Logger.
        # It does not participate in the Terminal Logger's own formatting logic.
        self.level = 0
        self.DefaultSymbol = False
        self.ansi = self.isEnableANSI
        self.log_file = self.file_path
        self.log_level = self.level_name
        self.console = True
        self.max_bytes = 0
        self.backup_count = 0
        self._context: dict[str, Any] = {}

    def set_level(self, level: str):
        """Change the minimum level at runtime."""
        lvl = level.upper()
        if lvl not in self.LEVELS:
            raise ValueError(f"Unknown log level: {level}")
        self.level_name = lvl
        self.level_num = self.LEVELS[lvl][0]
        self.log_level = lvl
        return self

    def enable_colors(self):
        self.use_colors = True
        return self

    def disable_colors(self):
        self.use_colors = False
        return self

    def _should_log(self, msg_level_num: int) -> bool:
        return msg_level_num >= self.level_num

    def _format(self, level_name: str, message: str) -> str:
        parts = []
        if self.show_time:
            now = time.strftime(self.timestamp_format)
            parts.append(f"[{now}]")
        if self.show_level:
            _, color, label = self.LEVELS[level_name]
            if self.use_colors:
                parts.append(styled(label, color, TextStyle.BOLD))
            else:
                parts.append(label)
        if self.show_name and self.name:
            parts.append(f"[{self.name}]")
        if self._context:
            parts.append("[" + " ".join(f"{k}={v!r}" for k, v in self._context.items()) + "]")
        parts.append(message)
        return " ".join(parts)

    def _write(self, text: str, level_name: str):
        from YoungLion import File
        self.file_path = File()._validate_and_prepare_path(self.file_path)
        self.log_file = self.file_path
        if not self.isEnableANSI:
            text = self.ANSI_ESCAPE.sub("", text)
        out = self.stream
        if out is None:
            lvl_num = self.LEVELS[level_name][0]
            out = sys.stderr if lvl_num >= self.LEVELS["ERROR"][0] else sys.stdout

        with self._lock:
            print(text, file=out)
            out.flush()

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

    # Original Terminal Logger methods remain unchanged in role and behavior.
    def debug(self, message: str):    self._log("DEBUG", message)
    def info(self, message: str):     self._log("INFO", message)
    def success(self, message: str):  self._log("SUCCESS", message)
    def warning(self, message: str):  self._log("WARNING", message)
    def error(self, message: str):    self._log("ERROR", message)
    def critical(self, message: str): self._log("CRITICAL", message)

    def exception(self, message: str):
        """Log an ERROR with traceback. Should be called from an except block."""
        tb = traceback.format_exc()
        full = f"{message}\n{tb}"
        self._log("ERROR", full)

    # ---- YoungLion.Logger aliases ----
    def log_debug(self, message: str, **fields: Any):
        return self.bind(**fields).debug(message) if fields else self.debug(message)

    def log_info(self, message: str, **fields: Any):
        return self.bind(**fields).info(message) if fields else self.info(message)

    def log_warning(self, message: str, **fields: Any):
        return self.bind(**fields).warning(message) if fields else self.warning(message)

    def log_error(self, message: str, **fields: Any):
        return self.bind(**fields).error(message) if fields else self.error(message)

    def log_critical(self, message: str, **fields: Any):
        return self.bind(**fields).critical(message) if fields else self.critical(message)

    def set_log_level(self, level: str):
        return self.set_level(level)

    def bind(self, **context: Any) -> "Logger":
        child = self.__class__(
            name=self.name,
            level=self.level_name,
            show_time=self.show_time,
            timestamp_format=self.timestamp_format,
            show_level=self.show_level,
            show_name=self.show_name,
            use_colors=self.use_colors,
            log_to_file=self.log_to_file,
            file_path=self.file_path,
            stream=self.stream,
        )
        child._context = {**self._context, **context}
        return child

    # ---- YoungLion.Debugger compatibility ----
    # Existing names (info/debug/success/warning/error/critical) already point to
    # the Terminal implementation, so only Debugger-only behavior needs aliases.
    def custom(self, message: str, color_code: str = Color.BRIGHT_MAGENTA, symbol: str = "*"):
        del color_code
        return self.info(f"{symbol} {message}" if symbol else message)

    def set_debugger_level(self, level: int):
        """Explicit alias for Debugger indentation without changing Logger.set_level."""
        return YoungLionDebugger.set_level(self, level)
