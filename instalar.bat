@echo off
cd /d "%~dp0"
if not exist ".env" copy ".env.example" ".env" >nul
echo Projeto WMK configurado. Instale Python 3.10+ e execute iniciar.bat
pause
