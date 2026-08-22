"""Progress primitives for YoungLion Terminal."""
from __future__ import annotations

import sys
import threading
from collections.abc import Iterable, Iterator
from typing import IO, TypeVar, Union

from .ansi import supports_ansi

T = TypeVar("T")
Number = int | float


class LoaderBar:
    """Progress value container used by :class:`TerminalLoader`.

    The v0.1 arithmetic/comparison API is preserved and v0.2 adds explicit
    mutation helpers that are easier to read in application code.
    """

    def __init__(self, length: Number, full_part: Number, bar_length: int = 10):
        self.length = max(1, length)
        self.full_part = max(0, min(full_part, self.length))
        self.bar_length = max(1, int(bar_length))

    @property
    def percent(self) -> float:
        return (self.full_part * 100) / self.length

    @property
    def ratio(self) -> float:
        return self.full_part / self.length

    @property
    def remaining(self) -> Number:
        return max(0, self.length - self.full_part)

    @property
    def completed(self) -> bool:
        return self.full_part >= self.length

    def set(self, value: Number) -> "LoaderBar":
        self.full_part = max(0, min(value, self.length))
        return self

    def advance(self, value: Number = 1) -> "LoaderBar":
        return self.set(self.full_part + value)

    def reset(self) -> "LoaderBar":
        self.full_part = 0
        return self

    def complete(self) -> "LoaderBar":
        self.full_part = self.length
        return self

    def __str__(self) -> str:
        fill_count = int(self.ratio * self.bar_length)
        empty_count = self.bar_length - fill_count
        return f"[{'#' * fill_count}{'-' * empty_count}] {self.percent:.2f}%"

    def __repr__(self) -> str:
        return f"LoaderBar(length={self.length}, full_part={self.full_part}, bar_length={self.bar_length})"

    def __float__(self) -> float:
        return self.percent

    def __add__(self, value: Union[Number, "LoaderBar"]) -> "LoaderBar":
        if isinstance(value, (int, float)):
            return LoaderBar(self.length, min(self.length, self.full_part + value), self.bar_length)
        if isinstance(value, LoaderBar):
            return LoaderBar(
                self.length + value.length,
                self.full_part + value.full_part,
                max(self.bar_length, value.bar_length),
            )
        raise TypeError(f"Unsupported operand type for +: 'LoaderBar' and '{type(value).__name__}'")

    def __sub__(self, value: Union[Number, "LoaderBar"]) -> "LoaderBar":
        if isinstance(value, (int, float)):
            return LoaderBar(self.length, max(0, self.full_part - value), self.bar_length)
        if isinstance(value, LoaderBar):
            return LoaderBar(
                max(1, self.length - value.length),
                max(0, self.full_part - value.full_part),
                max(1, self.bar_length - value.bar_length),
            )
        raise TypeError(f"Unsupported operand type for -: 'LoaderBar' and '{type(value).__name__}'")

    def __iadd__(self, value: Union[Number, "LoaderBar"]) -> "LoaderBar":
        if isinstance(value, (int, float)):
            self.advance(value)
        elif isinstance(value, LoaderBar):
            self.length += value.length
            self.full_part += value.full_part
            self.bar_length = max(self.bar_length, value.bar_length)
        else:
            raise TypeError(f"Unsupported operand type for +=: 'LoaderBar' and '{type(value).__name__}'")
        return self

    def __isub__(self, value: Union[Number, "LoaderBar"]) -> "LoaderBar":
        if isinstance(value, (int, float)):
            self.set(self.full_part - value)
        elif isinstance(value, LoaderBar):
            self.length = max(1, self.length - value.length)
            self.full_part = max(0, self.full_part - value.full_part)
            self.bar_length = max(1, self.bar_length - value.bar_length)
        else:
            raise TypeError(f"Unsupported operand type for -=: 'LoaderBar' and '{type(value).__name__}'")
        return self

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LoaderBar):
            return NotImplemented
        return (self.length, self.full_part, self.bar_length) == (other.length, other.full_part, other.bar_length)

    def __lt__(self, other: "LoaderBar") -> bool:
        if not isinstance(other, LoaderBar):
            return NotImplemented
        return self.percent < other.percent

    def __le__(self, other: "LoaderBar") -> bool:
        if not isinstance(other, LoaderBar):
            return NotImplemented
        return self.percent <= other.percent

    def __gt__(self, other: "LoaderBar") -> bool:
        if not isinstance(other, LoaderBar):
            return NotImplemented
        return self.percent > other.percent

    def __ge__(self, other: "LoaderBar") -> bool:
        if not isinstance(other, LoaderBar):
            return NotImplemented
        return self.percent >= other.percent


class TerminalLoader:
    """Real-time progress renderer with v0.1-compatible styling methods."""

    def __init__(self, bar: LoaderBar, valueName: str, *, stream: IO[str] | None = None):
        if not isinstance(bar, LoaderBar):
            raise TypeError("bar must be a LoaderBar")
        self.bar = bar
        self.valueName = valueName
        self.clear_finish = False
        self.stream = stream or sys.stdout
        self._lock = threading.RLock()
        self.barStartPart = "YoungLion Terminal Bar: |"
        self.barEndPart = "| {percent:.2f}%"
        self.barFullPart = "\033[1;40;32m━\033[0m"
        self.barEmptyPart = "\033[1;40;37m━\033[0m"
        self.finishStartPart = "\033[1;32m✔\033[0m Completed: |"
        self.finishEndPart = "| 100% 🎉"

    def update(self):
        with self._lock:
            self.stream.write("\r" + str(self) + " ")
            self.stream.flush()
        return self

    def setStyle(
        self,
        barStartPart: str | None = None,
        barEndPart: str | None = None,
        barFullPart: str | None = None,
        barEmptyPart: str | None = None,
        finishStartPart: str | None = None,
        finishEndPart: str | None = None,
    ):
        if barStartPart is not None: self.barStartPart = barStartPart
        if barEndPart is not None: self.barEndPart = barEndPart
        if barFullPart is not None: self.barFullPart = barFullPart
        if barEmptyPart is not None: self.barEmptyPart = barEmptyPart
        if finishStartPart is not None: self.finishStartPart = finishStartPart
        if finishEndPart is not None: self.finishEndPart = finishEndPart
        return self

    def _format_map(self) -> dict[str, object]:
        return {
            "percent": self.bar.percent,
            "value": self.valueName,
            "length": self.bar.length,
            "full_part": self.bar.full_part,
            "bar_length": self.bar.bar_length,
            "remaining": self.bar.remaining,
        }

    def __str__(self) -> str:
        fill_count = int(self.bar.ratio * self.bar.bar_length)
        empty_count = self.bar.bar_length - fill_count
        bar_fill = self.barFullPart * fill_count
        bar_empty = self.barEmptyPart * empty_count
        fmt = self._format_map()
        if self.bar.completed:
            text = f"\033[2K{self.finishStartPart.format(**fmt)}{bar_fill}{bar_empty}{self.finishEndPart.format(**fmt)}"
        else:
            text = f"\033[2K{self.barStartPart.format(**fmt)}{bar_fill}{bar_empty}{self.barEndPart.format(**fmt)}"
        if not supports_ansi(self.stream):
            from .ansi import strip_ansi

            text = strip_ansi(text)
        return text

    def __add__(self, value: Number | LoaderBar):
        if isinstance(value, (int, float)):
            self.bar.advance(value)
        elif isinstance(value, LoaderBar):
            self.bar += value
        else:
            raise TypeError(f"Unsupported operand type for +: 'TerminalLoader' and '{type(value).__name__}'")
        self.update()
        return self

    def __sub__(self, value: Number | LoaderBar):
        if isinstance(value, (int, float)):
            self.bar.set(self.bar.full_part - value)
        elif isinstance(value, LoaderBar):
            self.bar -= value
        else:
            raise TypeError(f"Unsupported operand type for -: 'TerminalLoader' and '{type(value).__name__}'")
        self.update()
        return self

    def upgrade(self, value: LoaderBar | Number):
        return self.__add__(value)

    def advance(self, value: Number = 1):
        return self.__add__(value)

    def finish(self):
        self.bar.complete()
        output = str(self)
        with self._lock:
            if self.clear_finish:
                from .ansi import strip_ansi

                self.stream.write("\r" + " " * len(strip_ansi(output)) + "\r")
            else:
                self.stream.write("\r" + output + "\n")
            self.stream.flush()
        return self

    def setClearFinish(self, status: bool):
        self.clear_finish = bool(status)
        return self

    def __enter__(self) -> "TerminalLoader":
        self.update()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.finish()
        return False

    @classmethod
    def track(
        cls,
        iterable: Iterable[T],
        valueName: str = "Working",
        *,
        total: int | None = None,
        bar_length: int = 30,
        stream: IO[str] | None = None,
    ) -> Iterator[T]:
        """Yield *iterable* while automatically updating a terminal loader."""
        if total is None:
            try:
                total = len(iterable)  # type: ignore[arg-type]
            except TypeError as exc:
                raise ValueError("total is required for iterables without __len__") from exc
        loader = cls(LoaderBar(total, 0, bar_length), valueName, stream=stream)
        loader.update()
        try:
            for item in iterable:
                yield item
                loader.advance(1)
        finally:
            if not loader.bar.completed:
                loader.finish()
