# YoungLion Terminal

Lightweight, well-documented ANSI terminal utilities for Python. This package
## Table of contents

- [Why use this library](#why-use-this-library)
- [Installation](#installation)
# YoungLion Terminal

[![CI](https://github.com/Cavanshirpro/YoungLionTerminalPythonLibrary/actions/workflows/ci.yml/badge.svg)](https://github.com/Cavanshirpro/YoungLionTerminalPythonLibrary/actions)
[![PyPI](https://img.shields.io/pypi/v/YoungLion-terminal.svg?color=gold&logo=python&logoColor=white)](https://pypi.org/project/YoungLion)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![issues](https://img.shields.io/github/issues/Cavanshirpro/YoungLionTerminalPythonLibrary?logo=github&logoColor=white)](https://github.com/Cavanshirpro/YoungLionTerminalPythonLibrary/issues)
[![stars](https://img.shields.io/github/stars/Cavanshirpro/YoungLionTerminalPythonLibrary?logo=github&logoColor=white&style=flat-square)](https://github.com/Cavanshirpro/YoungLionTerminalPythonLibrary/)

Advanced ANSI terminal utilities for Python — colors, text styles, cursor and
screen controls, progress loaders, spinners and a compact colored logger. This
library is focused on clear, consistent terminal output for CLI tools and
small scripts.

Repository: https://github.com/Cavanshirpro/YoungLionTerminalPythonLibrary

## Table of contents

- [Why use this library](#why-use-this-library)
- [Installation](#installation)
- [Quick examples](#quick-examples)
- [API summary](#api-summary)
- [Development & tests](#development--tests)
- [Publishing & GitHub](#publishing--github)
- [Contribution guidelines](#contribution-guidelines)
- [Versioning & changelog](#versioning--changelog)
- [License](#license)
- [Contact](#contact)

## Why use this library

- Lightweight, dependency-free helpers that wrap standard ANSI sequences.
- Small, composable primitives (`LoaderBar`, `TerminalLoader`, `Spinner`) that
	are easy to embed in scripts.
- A simple colored `Logger` and presentation helpers (`print_boxed`,
	`print_styled`) for consistent CLI UX.

## Installation

Development (editable install):

```powershell
python -m pip install -e .
```

Install from GitHub:

```powershell
python -m pip install git+https://github.com/Cavanshirpro/YoungLionTerminalPythonLibrary.git
```

Notes
- Run commands from the repository root (where `pyproject.toml` / `setup.cfg`
	is located).
- Use a terminal that supports ANSI escape codes (Windows Terminal, recent
	PowerShell, macOS Terminal, Linux terminals).

## Quick examples

These examples show common usage patterns.

1) Progress bar

```python
import time
from YoungLion.terminal import LoaderBar, TerminalLoader

bar = LoaderBar(length=10, full_part=0, bar_length=30)
loader = TerminalLoader(bar, "Download")

for _ in range(10):
		loader += 1
		time.sleep(0.12)

loader.finish()
```

2) Styled output

```python
from YoungLion.terminal import print_styled, Color, TextStyle

print_styled("Status:", styles=(Color.BRIGHT_GREEN, TextStyle.BOLD), end=" ")
print_styled("OK", styles=(TextStyle.UNDERLINE,))
```

3) Spinner

```python
import time
from YoungLion.terminal import Spinner, Color

with Spinner("Working…", style=Color.BRIGHT_CYAN):
		time.sleep(2)

print("Done")
```

4) Logger

```python
from YoungLion.terminal import Logger

log = Logger(name="myapp", level="INFO", log_to_file=False)
log.info("Service started")
log.success("Operation completed")
```

## API summary

Short reference to the publicly useful items (see module docstrings for full
details):

- `Color`, `BackgroundColor`, `TextStyle` — SGR constants for styling text.
- `CursorControl`, `ScreenControl`, `BufferControl` — sequences to control the
	terminal cursor and buffers.
- `LoaderBar(length, full_part, bar_length=10)` — progress value container.
	- Supports arithmetic and comparison dunder methods and `.percent`.
- `TerminalLoader(bar, valueName)` — in-place progress renderer.
	- Methods: `.update()`, `.setStyle(...)`, `.finish()`, `.setClearFinish()`.
- `Spinner(text, delay=0.1, style=Color.BRIGHT_CYAN)` — context-manager
	spinner for blocking operations.
- `print_styled`, `print_boxed`, `print_dict` — convenience printing helpers.
- `Logger` — colored logger with `.debug/.info/.success/.warning/.error/.critical/.exception()`.

## Development & tests

Install test dependencies and run tests with `pytest`:

```powershell
python -m pip install pytest
pytest -q
```

This repository includes a basic GitHub Actions workflow (`.github/workflows/ci.yml`)
that installs the package and runs tests on push/PR to `main`.

## Publishing & GitHub

To push the repository to GitHub (replace `<your-username>` / repo if needed):

```powershell
git init
git remote add origin https://github.com/Cavanshirpro/YoungLionTerminalPythonLibrary.git
git branch -M main
git add .
git commit -m "Initial commit"
git push -u origin main
```

Use the included `uploadgithub.bat` to commit and push from Windows:

```powershell
uploadgithub.bat "Your commit message" [branch]
```

To build distributions and upload to PyPI:

```powershell
python -m pip install --upgrade build twine
python -m build
python -m twine upload dist/*
```

# Contributing to YoungLion Terminal

Thank you for considering contributing — your help is appreciated.

Guidelines
- Fork the repository and create a new branch named `feature/<short-desc>` or
  `fix/<short-desc>`.
- Keep PRs focused and include tests for new behaviour when possible.
- Follow the existing code style and docstring conventions.

Workflow
1. Fork the repo and create a branch.
2. Make changes and include tests/examples as appropriate.
3. Commit with clear messages and push your branch.
4. Open a Pull Request describing the change and motivation.

Tests & CI
- This repository uses GitHub Actions for CI. Tests run automatically on PRs.
- Run tests locally with `pytest`.

Communication
- Open issues for feature requests or bugs before large changes — that helps
  to align design decisions.

## LICENSE

This project is licensed under the [MIT](https://choosealicense.com/licenses/mit/) License.

# Authors

## Main Developer
- **Cavanşir Qurbanzadə** - Lead Developer, Project Maintainer

---

If you want, I can now:

- Add more example scripts under `examples/` and include sample outputs.
- Add a minimal `.github/workflows/ci.yml` (already added) or extend it to run
	linting, packaging checks, or release automation.
- Create `CONTRIBUTING.md` & `CHANGELOG.md` (already added) or refine them.

Tell me which of these you'd like next and I'll continue.
	or `setup.cfg` is located.

- On Windows, use Windows Terminal, PowerShell or a modern console that
