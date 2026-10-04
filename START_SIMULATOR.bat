@echo off
setlocal
cd /d "%~dp0"

REM Prefer Python 3.11 through the Windows py launcher when available.
py -3.11 --version >nul 2>&1
if not errorlevel 1 (
    py -3.11 start.py
    if errorlevel 1 pause
    exit /b %errorlevel%
)

REM Fall back to python from PATH if it is Python 3.11+.
python --version >nul 2>&1
if errorlevel 1 (
    echo Python 3.11 or newer was not found.
    echo Install Python 3.11+ and reopen VS Code.
    pause
    exit /b 1
)

python start.py
if errorlevel 1 pause
