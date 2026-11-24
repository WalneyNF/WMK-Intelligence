@echo off
cd /d "%~dp0"
where npm >nul 2>&1 || (echo Instale Node.js primeiro. & pause & exit /b 1)
call npm install --prefix "%TEMP%\wmk-monaco-0522" --no-audit --no-fund monaco-editor@0.52.2 || (pause & exit /b 1)
xcopy "%TEMP%\wmk-monaco-0522\node_modules\monaco-editor\min\vs" "web\vendor\monaco\vs\" /E /I /Y
pause
