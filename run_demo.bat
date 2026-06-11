@echo off
color 0A
echo ========================================================
echo                 RAVEN AI DEMO LAUNCHER
echo ========================================================
echo.

echo [1/3] Starting FastAPI Backend Server in the background...
start "RAVEN Backend" cmd /c "cd backend && .\venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000"

echo Waiting for backend to initialize...
timeout /t 4 /nobreak >nul

echo.
echo [2/3] Opening Live Dashboard in your web browser...
start dashboard\index.html

echo Waiting for dashboard to connect...
timeout /t 3 /nobreak >nul

echo.
echo [3/3] Triggering RAVEN Drone Autonomous Pipeline...
echo --------------------------------------------------------
.\venv_firmware\Scripts\python.exe test_pipeline.py
echo --------------------------------------------------------
echo.
echo Demo run complete! You can run this file again to trigger another incident.
pause
