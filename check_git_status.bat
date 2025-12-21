@echo off
echo ============================================
echo Checking Git Status for config.json
echo ============================================
echo.

cd /d "%~dp0"

echo Tracked files containing "config":
echo ----------------------------------------
git ls-files | findstr /i "config"

echo.
echo ----------------------------------------
echo If you see "src/config.json" above, run:
echo   git rm --cached src/config.json
echo   git commit -m "chore: remove config.json from version control"
echo.
echo If you see nothing, config.json is NOT tracked (GOOD!)
echo ============================================

pause
