@echo off
setlocal enabledelayedexpansion
REM uploadgithub.bat "Commit message" [branch]
REM Convenience script to add, commit and push changes to origin.

if "%~1"=="" (
  REM No args: attempt interactive read via PowerShell
  for /f "usebackq delims=" %%m in (`powershell -NoProfile -Command "Read-Host 'Enter commit message (leave empty for auto message)'"`) do set "COMMIT_MSG=%%m"
  if "%COMMIT_MSG%"=="" (
    REM Build automatic commit message: use CMD timestamp and git status if available
    set "TS=%DATE% %TIME%"
    set "CHANGES=0"
    for /f "usebackq delims=" %%c in ('git status --porcelain ^| find /c /v "" 2^>nul') do set "CHANGES=%%c"
    if "%CHANGES%"=="" set "CHANGES=0"
    set "COMMIT_MSG=Auto commit: !TS! - !CHANGES! file(s)" 
    echo Using auto commit message: !COMMIT_MSG!
  )
) else (
  REM If message provided as arguments, join all arguments into one message
  set "COMMIT_MSG=%*"
)

if "%~2"=="" (
  set "BRANCH=main"
) else (
  set "BRANCH=%~2"
)

REM Ensure git is installed
git --version >nul 2>&1
if ERRORLEVEL 1 (
  echo Git does not appear to be installed or is not on PATH.
  exit /b 1
)

REM Check whether we're inside a git repository
git rev-parse --is-inside-work-tree >nul 2>&1
if ERRORLEVEL 1 (
  echo No git repository found in this folder.
  set /p "INIT_CHOICE=Initialize a new git repo here and add remote origin (Y/n)? "
  if /i "%INIT_CHOICE%"=="n" (
    echo Aborting: repository not initialized.
    exit /b 1
  )
  REM Initialize repo and set default branch
  git init
  git branch -M main 2>nul
  REM Default origin (your repo) — user can override
  set "DEFAULT_ORIGIN=https://github.com/Cavanshirpro/YoungLionTerminalPythonLibrary.git"
  set /p "ORIGIN_URL=Remote origin URL (leave empty to use %DEFAULT_ORIGIN%): "
  if "%ORIGIN_URL%"=="" (
    set "ORIGIN_URL=%DEFAULT_ORIGIN%"
  )
  git remote add origin "%ORIGIN_URL%" >nul 2>&1
  if ERRORLEVEL 1 (
    echo Warning: failed to add remote origin. You can add it manually later.
  ) else (
    echo Added remote origin: %ORIGIN_URL%
  )
)

REM Ensure a remote named origin exists now
git remote get-url origin >nul 2>&1
if ERRORLEVEL 1 (
  echo No remote named 'origin' found. You can add one with:
  echo   git remote add origin https://github.com/Cavanshirpro/YoungLionTerminalPythonLibrary.git
  echo Continuing without remote; push will be skipped.
  set "NO_ORIGIN=1"
)

echo Adding all changes...
git add --all

echo Committing with message: !COMMIT_MSG!
git commit -m "!COMMIT_MSG!" >nul 2>&1
if ERRORLEVEL 1 (
  echo No changes to commit; continuing to push.
)

if defined NO_ORIGIN (
  echo Skipping push because no remote 'origin' is configured.
  echo You can add a remote with:
  echo   git remote add origin https://github.com/Cavanshirpro/YoungLionTerminalPythonLibrary.git
  exit /b 0
)

echo Pushing to origin/%BRANCH%...
git push origin %BRANCH%

if ERRORLEVEL 1 (
  echo Push returned non-zero exit code. Check credentials and remote repository settings.
  exit /b 1
)

echo Done.
