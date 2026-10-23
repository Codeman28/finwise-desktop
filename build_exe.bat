@echo off
REM ==========================================================================
REM  build_exe.bat - Builds dist\FinWise.exe  (double-click this file)
REM
REM  Steps:
REM    1. create a private Python environment in .venv (first time only)
REM    2. install the libraries from requirements.txt
REM    3. draw the icon
REM    4. run "flet pack", which uses PyInstaller to bundle Python, Flet,
REM       our code and the Flutter window into ONE .exe file
REM ==========================================================================
cd /d "%~dp0"

if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv || goto :error
)

echo Installing requirements...
.venv\Scripts\python.exe -m pip install -q -r requirements.txt || goto :error

echo Drawing icon...
.venv\Scripts\python.exe tools\make_icon.py || goto :error

echo Packing FinWise.exe (this takes a few minutes)...
.venv\Scripts\flet.exe pack main.py ^
    --name FinWise ^
    --icon assets\icon.ico ^
    --product-name "FinWise" ^
    --file-description "FinWise - money manager and financial literacy academy" ^
    --product-version "1.0.0" ^
    --file-version "1.0.0.0" ^
    --copyright "FinWise" ^
    -y || goto :error

echo.
echo Done!  Your app is here:  %cd%\dist\FinWise.exe
pause
exit /b 0

:error
echo.
echo Build FAILED - see the messages above.
pause
exit /b 1
