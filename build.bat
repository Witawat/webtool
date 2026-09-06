@echo off
setlocal
cd /d "%~dp0"
if "%UPX_DIR%"=="" set UPX_DIR=tools\upx
if exist "%UPX_DIR%\upx.exe" set PATH=%UPX_DIR%;%PATH%
if not exist ".venv\Scripts\pyinstaller.exe" (
    echo Missing .venv. Run setup.bat first.
    exit /b 1
)
echo Building webtool.exe (this can take a few minutes)...
.venv\Scripts\pyinstaller -y webtool.spec
if errorlevel 1 (
    echo Build failed.
    exit /b 1
)
echo.
echo Done. Run with: run-exe.bat
