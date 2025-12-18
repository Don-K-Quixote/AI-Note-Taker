@echo off
REM ============================================================
REM AI Meeting Note Taker - Portfolio Setup Script
REM Run this from C:\Users\KhalidSiddiqui\Projects\AI-Note-Taker
REM ============================================================

echo.
echo ============================================================
echo AI Meeting Note Taker - Portfolio Setup
echo ============================================================
echo.

REM Check we're in the right directory
if not exist "meeting_recorder.py" (
    echo ERROR: Please run this script from the AI-Note-Taker directory
    echo        that contains meeting_recorder.py
    pause
    exit /b 1
)

echo Step 1: Creating project structure...
if not exist "src" mkdir src
if not exist "docs" mkdir docs
if not exist "notebooks" mkdir notebooks
if not exist ".github\ISSUE_TEMPLATE" mkdir .github\ISSUE_TEMPLATE
echo    Created: src/, docs/, notebooks/, .github/

echo.
echo Step 2: Moving main code to src/...
if exist "meeting_recorder.py" (
    copy meeting_recorder.py src\meeting_recorder.py
    echo    Copied: meeting_recorder.py to src/
)
if exist "process_meeting.py" (
    copy process_meeting.py src\process_meeting.py
    echo    Copied: process_meeting.py to src/
)

echo.
echo Step 3: Files to add manually...
echo    - README.md (download from Claude)
echo    - LICENSE (download from Claude)
echo    - CONTRIBUTING.md (download from Claude)
echo    - .gitignore (download from Claude)
echo    - docs/ARCHITECTURE.md (download from Claude)
echo    - docs/SETUP.md (download from Claude)
echo    - notebooks/experiments.ipynb (download from Claude)

echo.
echo Step 4: Setting up Git branching...
echo.

REM Create develop branch
git checkout -b develop 2>nul
if errorlevel 1 (
    git checkout develop 2>nul
)
echo    Created/switched to: develop branch

REM Go back to main
git checkout main 2>nul
if errorlevel 1 (
    git checkout master 2>nul
    git branch -m master main 2>nul
)

echo.
echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Next steps:
echo   1. Download files from Claude and place them in this folder
echo   2. Run: git add .
echo   3. Run: git commit -m "chore: restructure project for portfolio"
echo   4. Run: git push origin main
echo   5. Run: git push origin develop
echo   6. Open folder in VS Code: code .
echo.
pause
