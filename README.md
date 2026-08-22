# YoungLion Terminal

[![CI](https://github.com/Cavanshirpro/YoungLionTerminalPythonLibrary/actions/workflows/ci.yml/badge.svg)](https://github.com/Cavanshirpro/YoungLionTerminalPythonLibrary/actions)
[![PyPI](https://img.shields.io/pypi/v/YoungLion-terminal.svg?color=gold&logo=python&logoColor=white)](https://pypi.org/project/YoungLion-terminal/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**YoungLion Terminal v0.2** is the terminal/UI companion package for **YoungLion v0.1**. It provides ANSI control, terminal capability detection, styled output, progress bars, spinners, logging/debugging integration and dependency-free terminal widgets.

The package intentionally stays lightweight: it depends only on the main `YoungLion` package and uses no third-party terminal framework.

## What changed in v0.2

- Compatible with `YoungLion>=0.1.0,<0.2.0` and Python 3.10+.
- Removed the obsolete dependency on `YoungLion.DataModel.enable_ansi`.
- `YoungLion.terminal.Logger` is now a real subclass of both `YoungLion.Debugger` and `YoungLion.Logger` while preserving the Terminal Logger API.
- `Logger` can be passed directly to `YoungLion.File(debug=True, debugger=logger)`.
- Added terminal capability detection, ANSI stripping, Windows VT enablement, hidden-cursor and alternate-buffer context managers, and OSC-8 hyperlinks.
- Strengthened `LoaderBar`, `TerminalLoader` and `Spinner` with explicit lifecycle helpers and iterable tracking.
- Added `Table`, `Panel` and `LiveLine` widgets.
- Added targeted DDM support only where data presentation naturally benefits from it (`print_dict` and `Table`).
- Added a real pytest suite and Python 3.10–3.14 CI matrix.
- Added comprehensive runtime docstrings and parameter documentation for every class, function and class method so IDLE/IDE call tips can explain the API while code is being written.

See [`releases.md`](releases.md) for the complete release notes.

## Installation

```bash
python -m pip install "YoungLion-terminal>=0.2,<0.3"
```

For development:

```bash
git clone https://github.com/Cavanshirpro/YoungLionTerminalPythonLibrary.git
cd YoungLionTerminalPythonLibrary
python -m pip install -e ".[dev]"
pytest
```

## Quick start

### Colors and styling

```python
from YoungLion.terminal import Color, TextStyle, styled

print(styled("YoungLion", Color.BRIGHT_YELLOW, TextStyle.BOLD))
```

### ANSI enablement and capability-aware output

`enable_ansi()` is implemented **inside YoungLion Terminal itself**. It does not
depend on the main YoungLion package exposing an `enable_ansi` function.

```python
from YoungLion.terminal import (
    detect_capabilities,
    enable_ansi,
    supports_ansi,
    strip_ansi,
)

enable_ansi()  # Safe to call repeatedly; enables Windows VT mode when possible.

caps = detect_capabilities()
print(caps)
print("ANSI:", supports_ansi())
```

`enable_ansi(stream=None)`:

- uses `sys.stdout` when `stream` is omitted;
- respects `NO_COLOR`;
- enables `ENABLE_VIRTUAL_TERMINAL_PROCESSING` on supported Windows consoles;
- checks terminal usability on POSIX systems;
- returns `True`/`False` instead of requiring a YoungLion-core helper.

### Progress tracking

```python
import time
from YoungLion.terminal import TerminalLoader

for item in TerminalLoader.track(range(25), "Indexing", bar_length=30):
    time.sleep(0.02)
```

The old API remains available:

```python
from YoungLion.terminal import LoaderBar, TerminalLoader

bar = LoaderBar(length=10, full_part=0, bar_length=25)
loader = TerminalLoader(bar, "Download")
loader += 1
loader.upgrade(2)
loader.finish()
```

### Spinner

```python
import time
from YoungLion.terminal import Spinner

with Spinner("Building index") as spinner:
    time.sleep(1)
    spinner.succeed("✔ Index ready")
```

### Logger + YoungLion Debugger/File compatibility

```python
from YoungLion import Debugger, File, Logger as CoreLogger
from YoungLion.terminal import Logger

log = Logger(name="worker", level="DEBUG", show_name=True)

assert isinstance(log, Debugger)
assert isinstance(log, CoreLogger)

files = File(debug=True, debugger=log)
log.info("Worker started")
log.success("Configuration loaded")
```

The Terminal Logger remains the source of truth for formatting and behavior. Core method names are routed into it:

```python
log.log_info("Connected", worker_id=4)   # YoungLion.Logger-compatible alias
log.custom("Protocol trace")             # YoungLion.Debugger-compatible wrapper
log.set_debugger_level(2)                 # YoungLion.Debugger indentation alias
log.set_level("WARNING")                  # Original Terminal Logger threshold
```

### DDM-aware table

```python
from YoungLion import DDM
from YoungLion.terminal import Table

rows = [
    DDM({"name": "alpha", "status": "ready"}),
    DDM({"name": "beta", "status": "working"}),
]

Table(headers=["name", "status"], rows=rows).print()
```

DDM support is intentionally not spread through the whole package. It is used in rendering APIs where treating a model as terminal data is useful.

### Panel and live line

```python
from YoungLion.terminal import LiveLine, Panel

Panel("YoungLion Terminal v0.2", title="Status").print()

with LiveLine("Starting...") as line:
    line.update("Loading configuration...")
    line.update("Ready")
```

## API overview

### ANSI and terminal control

- `Color`, `BackgroundColor`, `TextStyle`, `Decoration`, `Ideographic`, `Font`
- `CursorControl`, `ScreenControl`, `BufferControl`, `LegacyCursorControl`
- `enable_ansi()`, `supports_ansi()`, `strip_ansi()`
- `TerminalCapabilities`, `detect_capabilities()`
- `hidden_cursor()`, `alternate_buffer()`, `hyperlink()`

### Output helpers

- `styled()`, `print_styled()`
- `clear_screen()`, `get_terminal_size()`, `visible_len()`
- `print_boxed()`, `print_dict()`
- `prompt()`

### Dynamic terminal components

- `LoaderBar`
- `TerminalLoader`
- `Spinner`
- `Table`
- `Panel`
- `LiveLine`

### Logging

- `Logger.debug()`
- `Logger.info()`
- `Logger.success()`
- `Logger.warning()`
- `Logger.error()`
- `Logger.critical()`
- `Logger.exception()`
- `Logger.bind()`
- YoungLion core aliases: `log_debug`, `log_info`, `log_warning`, `log_error`, `log_critical`, `set_log_level`, `custom`

## Built-in documentation and IDE / IDLE help

YoungLion Terminal v0.2 treats inline API documentation as part of the public
API. Every library class, function, property and class method has a Python
docstring, and function parameters are described inside those docstrings.

This means users can inspect the package without opening the source code:

```python
from YoungLion.terminal import Logger, TerminalLoader, enable_ansi

help(Logger)
help(Logger.__init__)
help(TerminalLoader.track)
help(enable_ansi)

print(Logger.__init__.__doc__)
```

In IDLE and IDEs that support Python signature/call tips, the type hints provide
the function signature while the docstring explains parameters such as
`stream`, `level`, `show_time`, `bar_length`, `total`, `padding`, and so on.

Examples of the documentation style used throughout the package:

```python
def enable_ansi(stream: IO[str] | None = None) -> bool:
    """Enable ANSI / VT escape-sequence support for a terminal stream.

    Args:
        stream:
            Text output stream whose terminal capability should be enabled.
            When omitted, sys.stdout is used.

    Returns:
        True when ANSI output can be used for the selected stream.
    """
```

A dedicated test (`tests/test_docstrings.py`) parses the source and fails when a
new class/function/method is added without a docstring or when one of its
parameters is not mentioned in the docstring. This keeps the documentation
requirement enforceable instead of relying only on convention.

## Compatibility policy

YoungLion Terminal follows the main YoungLion minor line intentionally:

| YoungLion Terminal | YoungLion core | Python |
|---|---|---|
| 0.2.x | `>=0.1.0,<0.2.0` | 3.10–3.14 |

This prevents silent API drift between the terminal companion and core package.

## Development

```bash
python -m pip install -e ".[dev]"
pytest -q
ruff check .
python -m build
python -m twine check dist/*
```

## License

MIT License. See [`LICENSE`](LICENSE).

## Author

**Cavanşir Qurbanzadə** — [Cavanshirpro](https://github.com/Cavanshirpro)
