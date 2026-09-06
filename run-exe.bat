@echo off
setlocal
cd /d "%~dp0"
if not exist "dist\webtool.exe" (
    echo Missing dist\webtool.exe. Run build.bat first.
    exit /b 1
)
start "" /min "dist\webtool.exe" %*
