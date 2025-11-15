@echo off
echo ============================================================
echo TDS PROJECT 1 - QUICK TEST
echo ============================================================
echo.

echo Step 1: Verifying setup...
python verify_setup.py
if errorlevel 1 (
    echo.
    echo ERROR: Setup verification failed!
    pause
    exit /b 1
)

echo.
echo Step 2: Starting server...
start "TDS Server" cmd /k "uvicorn app.main:app --reload"
timeout /t 5 /nobreak >nul

echo.
echo Step 3: Running comprehensive test...
python test_all_tasks.py

echo.
echo ============================================================
echo Test complete! Check results above.
echo.
echo To stop server: Switch to "TDS Server" window and press Ctrl+C
echo.
echo Check GitHub repos: https://github.com/subhuchan?tab=repositories
echo ============================================================
pause
