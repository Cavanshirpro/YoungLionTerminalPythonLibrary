import sys
from typing import Union

class LoaderBar:
    """
    A simple terminal-based progress bar.

    Attributes:
        length (float): The total length of the progress bar.
        full_part (float): The current progress value.
        bar_length (int): The number of characters in the visual bar.
    """

    def __init__(self, length: int | float, full_part: int | float, bar_length: int = 10):
        """
        Initializes the LoaderBar with given parameters.

        Args:
            length (int | float): The total length of the progress bar.
            full_part (int | float): The current progress value.
            bar_length (int): The number of characters in the visual bar (default: 10).
        """
        self.length = max(1, length)  
        self.full_part = max(0, min(full_part, self.length))  
        self.bar_length = max(1, bar_length)  

    @property
    def percent(self) -> float:
        """Returns the progress percentage."""
        return (self.full_part * 100) / self.length

    def __str__(self) -> str:
        """
        Returns the formatted progress bar as a string.

        Example:
            [#####-----] 50.00%
        """
        fill_count = int((self.percent / 100) * self.bar_length)
        empty_count = self.bar_length - fill_count
        bar_fill = "#" * fill_count
        bar_empty = "-" * empty_count
        return f"[{bar_fill}{bar_empty}] {self.percent:.2f}%"

    def __repr__(self) -> str:
        """Returns a string representation of the LoaderBar object."""
        return f"LoaderBar(length={self.length}, full_part={self.full_part}, bar_length={self.bar_length})"

    def __add__(self, value: Union[int,float,"LoaderBar"]) -> "LoaderBar":
        """
        Adds a value to the progress bar.

        If the value is an int or float, it is added to `full_part`.
        If the value is another `LoaderBar`, all attributes are added.

        Args:
            value (int | float | LoaderBar): The value to add.

        Returns:
            LoaderBar: A new instance with updated values.
        """
        if isinstance(value, (int, float)):
            return LoaderBar(self.length, min(self.length, self.full_part + value), self.bar_length)
        elif isinstance(value, LoaderBar):
            new_length = self.length + value.length
            new_full_part = self.full_part + value.full_part
            new_bar_length = max(self.bar_length, value.bar_length)
            return LoaderBar(new_length, new_full_part, new_bar_length)
        else:
            raise TypeError("Unsupported operand type for +: 'LoaderBar' and '{}'".format(type(value).__name__))

    def __sub__(self, value:Union[int,float,"LoaderBar"]) -> "LoaderBar":
        """
        Subtracts a value from the progress bar.

        If the value is an int or float, it is subtracted from `full_part`.
        If the value is another `LoaderBar`, all attributes are subtracted.

        Args:
            value (int | float | LoaderBar): The value to subtract.

        Returns:
            LoaderBar: A new instance with updated values.
        """
        if isinstance(value, (int, float)):
            return LoaderBar(self.length, max(0, self.full_part - value), self.bar_length)
        elif isinstance(value, LoaderBar):
            new_length = max(1, self.length - value.length)
            new_full_part = max(0, self.full_part - value.full_part)
            new_bar_length = max(1, self.bar_length - value.bar_length)
            return LoaderBar(new_length, new_full_part, new_bar_length)
        else:
            raise TypeError("Unsupported operand type for -: 'LoaderBar' and '{}'".format(type(value).__name__))

    def __iadd__(self, value:Union[int,float,"LoaderBar"]) -> "LoaderBar":
        """
        Performs an in-place addition.

        Args:
            value (int | float | LoaderBar): The value to add.

        Returns:
            LoaderBar: The modified instance.
        """
        if isinstance(value, (int, float)):
            self.full_part = min(self.length, self.full_part + value)
        elif isinstance(value, LoaderBar):
            self.length += value.length
            self.full_part += value.full_part
            self.bar_length = max(self.bar_length, value.bar_length)
        else:
            raise TypeError("Unsupported operand type for +=: 'LoaderBar' and '{}'".format(type(value).__name__))
        return self

    def __isub__(self, value:Union[int,float,"LoaderBar"]) -> "LoaderBar":
        """
        Performs an in-place subtraction.

        Args:
            value (int | float | LoaderBar): The value to subtract.

        Returns:
            LoaderBar: The modified instance.
        """
        if isinstance(value, (int, float)):
            self.full_part = max(0, self.full_part - value)
        elif isinstance(value, LoaderBar):
            self.length = max(1, self.length - value.length)
            self.full_part = max(0, self.full_part - value.full_part)
            self.bar_length = max(1, self.bar_length - value.bar_length)
        else:
            raise TypeError("Unsupported operand type for -=: 'LoaderBar' and '{}'".format(type(value).__name__))
        return self

    def __eq__(self, other: "LoaderBar") -> bool:
        """Checks if two LoaderBar objects are equal."""
        if not isinstance(other, LoaderBar):
            return NotImplemented
        return (self.length, self.full_part, self.bar_length) == (other.length, other.full_part, other.bar_length)

    def __ne__(self, other: "LoaderBar") -> bool:
        """Checks if two LoaderBar objects are not equal."""
        return not self.__eq__(other)

    def __lt__(self, other: "LoaderBar") -> bool:
        """Checks if self is less than other based on percent completion."""
        if not isinstance(other, LoaderBar):
            return NotImplemented
        return self.percent < other.percent

    def __le__(self, other: "LoaderBar") -> bool:
        """Checks if self is less than or equal to other based on percent completion."""
        if not isinstance(other, LoaderBar):
            return NotImplemented
        return self.percent <= other.percent

    def __gt__(self, other: "LoaderBar") -> bool:
        """Checks if self is greater than other based on percent completion."""
        if not isinstance(other, LoaderBar):
            return NotImplemented
        return self.percent > other.percent

    def __ge__(self, other: "LoaderBar") -> bool:
        """Checks if self is greater than or equal to other based on percent completion."""
        if not isinstance(other, LoaderBar):
            return NotImplemented
        return self.percent >= other.percent

class TerminalLoader:
    """
    A terminal-based progress loader with real-time updates.

    Attributes:
        bar (LoaderBar): The progress bar object.
        valueName (str): The name of the value being tracked.
    """

    def __init__(self, bar: LoaderBar, valueName: str):
        """
    Initializes the TerminalLoader.

    Args:
        bar (LoaderBar): The progress bar to track.
        valueName (str): The label for the progress value.
    """
        self.bar = bar
        self.valueName = valueName
        self.clear_finish = False

        
        self.barStartPart = "YoungLion Terminal Bar: |"
        self.barEndPart = "| {percent:.2f}%"
        self.barFullPart = "\033[1;40;32m━\033[0m"
        self.barEmptyPart = "\033[1;40;37m━\033[0m"

        self.finishStartPart = "\033[1;32m✔\033[0m Completed: |"
        self.finishEndPart = "| 100% 🎉"

    def update(self):
        """Updates the progress bar in the terminal."""
        sys.stdout.write("\r" + str(self) + " ")
        sys.stdout.flush()

    def setStyle(self, barStartPart: str = None, barEndPart: str = None,
                 barFullPart: str = None, barEmptyPart: str = None,
                 finishStartPart: str = None, finishEndPart: str = None):
        """
    Updates the style of the progress bar.

    You can use placeholders in the following text parts:
        - "percent": The current percentage of the progress bar.
        - "value": The name or description associated with the progress bar.
        - "length": The total length of the progress bar.
        - "full_part": The current progress value.
        - "bar_length": The number of characters used for the visual representation of the bar.

    Example usage for the text parts:
        - barStartPart: "{full_part}/{length} {value} {percent}%"
        - barEndPart: "[{full_part}/{length}] {percent}% - {value}"

    Args:
        barStartPart (str): The starting text of the bar (use placeholders like {full_part}, {length}, etc.).
        barEndPart (str): The ending text of the bar (use placeholders like {percent}, {value}, etc.).
        barFullPart (str): The character used for the filled portion of the bar (e.g., "█").
        barEmptyPart (str): The character used for the empty portion of the bar (e.g., "-").
        finishStartPart (str): The text shown when the bar is completed (use placeholders like {percent}, {value}, etc.).
        finishEndPart (str): The text shown at the end of the bar when completed (use placeholders like {percent}, {value}, etc.).
"""
        if barStartPart is not None: self.barStartPart = barStartPart
        if barEndPart is not None: self.barEndPart = barEndPart
        if barFullPart is not None: self.barFullPart = barFullPart
        if barEmptyPart is not None: self.barEmptyPart = barEmptyPart
        if finishStartPart is not None: self.finishStartPart = finishStartPart
        if finishEndPart is not None: self.finishEndPart = finishEndPart

    def __str__(self) -> str:
        """Returns the formatted progress bar as a string."""
        fill_count = int((self.bar.percent / 100) * self.bar.bar_length)
        empty_count = self.bar.bar_length - fill_count
        bar_fill = self.barFullPart * fill_count
        bar_empty = self.barEmptyPart * empty_count
        formatMap={
            "percent":self.bar.percent,
            "value":self.valueName,
            "length":self.bar.length,
            "full_part":self.bar.full_part,
            "bar_length":self.bar.bar_length,
        }
        if self.bar.percent >= 100:
            return f"\033[2K{self.finishStartPart.format(**formatMap)}{bar_fill}{bar_empty}{self.finishEndPart.format(**formatMap)}"
        return f"\033[2K{self.barStartPart.format(**formatMap)}{bar_fill}{bar_empty}{self.barEndPart.format(**formatMap)}"

    def __add__(self, value: int | float | LoaderBar):
        """Increments the progress bar using `+` operator."""
        if isinstance(value, (int, float)):
            self.bar.full_part = min(self.bar.length, self.bar.full_part + value)
        elif isinstance(value, LoaderBar):
            self.bar += value
        else:
            raise TypeError(f"Unsupported operand type for +: 'TerminalLoader' and '{type(value).__name__}'")
        self.update()
        return self

    def upgrade(self, value: LoaderBar | int | float):
        """Upgrades the progress bar dynamically."""
        self.__add__(value)

    def finish(self):
        """Marks the progress as complete and optionally clears the line."""
        self.bar.full_part = self.bar.length  
        output = str(self)  
        
        if self.clear_finish:
            sys.stdout.write("\r" + " " * len(output) + "\r")  
            sys.stdout.flush()
        
        print("\r" + output)

    def setClearFinish(self, status: bool):
        """Sets whether to clear the progress bar upon completion."""
        self.clear_finish = status
