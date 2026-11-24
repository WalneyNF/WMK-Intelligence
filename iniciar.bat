@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (py -3 -m wmk.server) else (python -m wmk.server)
pause
