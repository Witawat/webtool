@echo off
setlocal
cd /d "%~dp0"
echo [1/2] Creating virtual environment...
python -m venv .venv || goto :error
echo [2/2] Installing dependencies...
.venv\Scripts\pip install -r requirements.txt || goto :error
echo.
echo Setup complete. Run with: run-dev.bat
exit /b 0

:error
echo Setup failed.
exit /b 1
