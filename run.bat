@echo off
REM ============================================
REM Meeting Note Taker - Quick Launch Scripts
REM ============================================

if "%1"=="record" goto record
if "%1"=="process" goto process
if "%1"=="help" goto help
goto help

:record
echo Starting Meeting Recorder in background...
start "" pythonw meeting_recorder.py
echo Recorder started! Look for the icon in your system tray.
echo Press Ctrl+Alt+R to start/stop recording.
goto end

:process
if "%2"=="" (
    echo Usage: run.bat process ^<audio_file^>
    echo Example: run.bat process recordings\meeting_20241215_140000.wav
    goto end
)
echo Processing: %2
python process_meeting.py "%2"
goto end

:help
echo ============================================
echo Meeting Note Taker - Commands
echo ============================================
echo.
echo   run.bat record              Start the invisible recorder
echo   run.bat process ^<file^>     Process a recording
echo   run.bat help               Show this help
echo.
echo Examples:
echo   run.bat record
echo   run.bat process recordings\meeting_20241215_140000.wav
echo.
goto end

:end
