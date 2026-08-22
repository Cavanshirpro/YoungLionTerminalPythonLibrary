"""Composable terminal widgets added in YoungLion Terminal v0.2."""
from __future__ import annotations

import sys
import threading
from collections.abc import Iterable, Mapping, Sequence
from typing import Any, IO

from YoungLion import DDM

from .ansi import Color, supports_ansi, strip_ansi
from .utils import styled, visible_len


def _cell(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _model_mapping(value: Mapping[str, Any] | DDM) -> Mapping[str, Any]:
    return value.to_dict() if isinstance(value, DDM) else value


class Table:
    """Dependency-free Unicode table renderer.

    Rows may be ordinary sequences, mappings, or ``YoungLion.DDM`` instances.
    Mapping/DDM rows are projected using ``headers``.  This is one of the few
    places where DDM integration is useful because terminal rendering is
    naturally data-model-oriented.
    """

    def __init__(
        self,
        headers: Sequence[str] | None = None,
        rows: Iterable[Sequence[Any] | Mapping[str, Any] | DDM] = (),
        *,
        padding: int = 1,
        header_style: str = Color.BRIGHT_CYAN,
        border_style: str = Color.BRIGHT_BLACK,
        max_width: int | None = None,
    ):
        self.headers = [str(value) for value in (headers or [])]
        self.rows: list[list[str]] = []
        self.padding = max(0, int(padding))
        self.header_style = header_style
        self.border_style = border_style
        self.max_width = max_width
        for row in rows:
            self.add_row(row)

    def add_row(self, row: Sequence[Any] | Mapping[str, Any] | DDM) -> "Table":
        if isinstance(row, (DDM, Mapping)):
            mapping = _model_mapping(row)
            if not self.headers:
                self.headers = [str(key) for key in mapping.keys()]
            values = [_cell(mapping.get(header, "")) for header in self.headers]
        else:
            values = [_cell(value) for value in row]
            if self.headers and len(values) != len(self.headers):
                raise ValueError("row length must match headers length")
            if not self.headers and self.rows and len(values) != len(self.rows[0]):
                raise ValueError("all rows must have the same length")
        self.rows.append(values)
        return self

    def add_rows(self, rows: Iterable[Sequence[Any] | Mapping[str, Any] | DDM]) -> "Table":
        for row in rows:
            self.add_row(row)
        return self

    def _column_count(self) -> int:
        if self.headers:
            return len(self.headers)
        return len(self.rows[0]) if self.rows else 0

    def _truncate(self, text: str) -> str:
        if self.max_width is None or self.max_width <= 0 or visible_len(text) <= self.max_width:
            return text
        if self.max_width == 1:
            return "…"
        plain = strip_ansi(text)
        return plain[: self.max_width - 1] + "…"

    def render(self, *, color: bool | None = None, stream: IO[str] | None = None) -> str:
        stream = stream or sys.stdout
        use_color = supports_ansi(stream) if color is None else bool(color)
        column_count = self._column_count()
        if column_count == 0:
            return ""

        headers = [self._truncate(value) for value in self.headers]
        rows = [[self._truncate(value) for value in row] for row in self.rows]
        widths = [0] * column_count
        for index in range(column_count):
            candidates = []
            if headers:
                candidates.append(headers[index])
            candidates.extend(row[index] for row in rows)
            widths[index] = max((visible_len(value) for value in candidates), default=0)

        def border(left: str, middle: str, right: str) -> str:
            raw = left + middle.join("─" * (width + self.padding * 2) for width in widths) + right
            return styled(raw, self.border_style, enabled=use_color)

        def row_line(values: Sequence[str], header: bool = False) -> str:
            parts = []
            for index, value in enumerate(values):
                gap = widths[index] - visible_len(value)
                content = " " * self.padding + value + " " * (gap + self.padding)
                if header:
                    content = styled(content, self.header_style, enabled=use_color)
                parts.append(content)
            divider = styled("│", self.border_style, enabled=use_color)
            return divider + divider.join(parts) + divider

        lines = [border("┌", "┬", "┐")]
        if headers:
            lines.append(row_line(headers, header=True))
            lines.append(border("├", "┼", "┤"))
        for row in rows:
            lines.append(row_line(row))
        lines.append(border("└", "┴", "┘"))
        return "\n".join(lines)

    def print(self, *, file: IO[str] | None = None, color: bool | None = None) -> None:
        file = file or sys.stdout
        print(self.render(color=color, stream=file), file=file)

    def __str__(self) -> str:
        return self.render(color=False)


class Panel:
    """Render a titled bordered block without an external UI dependency."""

    def __init__(
        self,
        content: str,
        title: str | None = None,
        *,
        padding: int = 1,
        border_style: str = Color.BRIGHT_BLUE,
        title_style: str = Color.BRIGHT_CYAN,
    ):
        self.content = str(content)
        self.title = title
        self.padding = max(0, int(padding))
        self.border_style = border_style
        self.title_style = title_style

    def render(self, *, color: bool | None = None, stream: IO[str] | None = None) -> str:
        stream = stream or sys.stdout
        use_color = supports_ansi(stream) if color is None else bool(color)
        lines = self.content.splitlines() or [""]
        content_width = max(visible_len(line) for line in lines)
        title_text = f" {self.title} " if self.title else ""
        width = max(content_width + self.padding * 2, visible_len(title_text))
        top_fill = max(0, width - visible_len(title_text))
        if title_text:
            top = "┌" + styled(title_text, self.title_style, enabled=use_color) + "─" * top_fill + "┐"
        else:
            top = "┌" + "─" * width + "┐"
        border = lambda value: styled(value, self.border_style, enabled=use_color)
        rendered = [border(strip_ansi(top)) if not title_text else border("┌") + styled(title_text, self.title_style, enabled=use_color) + border("─" * top_fill + "┐")]
        for line in lines:
            gap = content_width - visible_len(line)
            rendered.append(border("│") + " " * self.padding + line + " " * (gap + self.padding) + border("│"))
        rendered.append(border("└" + "─" * width + "┘"))
        return "\n".join(rendered)

    def print(self, *, file: IO[str] | None = None, color: bool | None = None) -> None:
        file = file or sys.stdout
        print(self.render(color=color, stream=file), file=file)

    def __str__(self) -> str:
        return self.render(color=False)


class LiveLine:
    """Thread-safe single-line live updater.

    Useful for counters, download status and lightweight dashboards where a full
    progress bar would be excessive.
    """

    def __init__(self, text: str = "", *, stream: IO[str] | None = None, clear_on_exit: bool = False):
        self.text = str(text)
        self.stream = stream or sys.stdout
        self.clear_on_exit = bool(clear_on_exit)
        self._lock = threading.RLock()
        self._last_width = 0

    def update(self, text: str | None = None) -> "LiveLine":
        if text is not None:
            self.text = str(text)
        with self._lock:
            width = visible_len(self.text)
            padding = max(0, self._last_width - width)
            self.stream.write("\r" + self.text + " " * padding)
            self.stream.flush()
            self._last_width = width
        return self

    def clear(self) -> "LiveLine":
        with self._lock:
            self.stream.write("\r" + " " * self._last_width + "\r")
            self.stream.flush()
            self._last_width = 0
        return self

    def finish(self, text: str | None = None) -> "LiveLine":
        if text is not None:
            self.text = str(text)
        self.update()
        self.stream.write("\n")
        self.stream.flush()
        self._last_width = 0
        return self

    def __enter__(self) -> "LiveLine":
        return self.update()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.clear_on_exit:
            self.clear()
        else:
            self.finish()
        return False
