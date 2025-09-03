@echo off
REM Build script for CoTag 1.1 using PyInstaller (project root)

:: Usage: build_exe.bat [fast]
::   fast = incremental build (reuse cache, faster)

:: Activate the virtual environment (adjust path if necessary)
call "%~dp0.venv\Scripts\Activate.bat"
:check_pyinstaller
python -m pip show pyinstaller >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo PyInstaller not found, installing into venv...
    python -m pip install pyinstaller
)

set "MODE=%1"
if /I "%MODE%"=="fast" (
    set "CLEAN_FLAG="
    set "CLEAN_TEXT= (fast/incremental)"
    set "REMOVE_OLD=0"
    set "LOGLEVEL=INFO"
) else (
    set "CLEAN_FLAG=--clean"
    set "CLEAN_TEXT= (clean)"
    set "REMOVE_OLD=1"
    set "LOGLEVEL=INFO"
)

echo Building CoTag_1.1.exe%CLEAN_TEXT%...

REM Remove previous build artifacts only for clean mode to avoid stale icon resources
if %REMOVE_OLD%==1 (
    if exist "%~dp0build" (
        echo Removing old build folder...
        rmdir /s /q "%~dp0build"
    )
    if exist "%~dp0dist" (
        echo Removing old dist folder...
        rmdir /s /q "%~dp0dist"
    )
    if exist "%~dp0__pycache__" (
        rmdir /s /q "%~dp0__pycache__"
    )
)

if not exist dist mkdir dist
if not exist build mkdir build

REM Ensure the provided icon exists and use it (resource\CoTag.ico in project root)
set "ICON_PATH=%~dp0resource\CoTag.ico"
if not exist "%ICON_PATH%" (
    echo ERROR: resource\CoTag.ico not found. Please place your CoTag.ico at "%~dp0resource\CoTag.ico" and re-run.
    pause
    exit /b 1
)

echo Using icon: %ICON_PATH% (size:)
for %%I in ("%ICON_PATH%") do echo    %%~zI bytes, modified=%%~tI

REM PyInstaller options: keep output concise and allow fast/incremental builds
echo Running PyInstaller (this may take a while)...
pyinstaller %CLEAN_FLAG% --noconfirm --log-level=%LOGLEVEL% --onefile --windowed --icon "%ICON_PATH%" --add-data "%ICON_PATH%;." --name "CoTag_1.1" "%~dp0src\main.py"

echo Build finished. The executable is in the dist folder as CoTag_1.1.exe
