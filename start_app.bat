@echo off
title Prakriti AI - Web Server
cd /d "%~dp0"

echo ======================================================================
echo              Prakriti AI - Smart Women's Health Assistant
echo ======================================================================
echo.
echo Starting Flask web server at http://127.0.0.1:5000 ...
echo Opening your web browser...
echo.

start http://127.0.0.1:5000

"%~dp0.venv\Scripts\python.exe" app.py

pause
