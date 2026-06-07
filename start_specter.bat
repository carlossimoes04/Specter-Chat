@echo off
title Specter Launcher
color 0B
echo =========================================
echo       SPECTER LOCAL AI NODE LAUNCHER
echo =========================================
echo.
echo [1/3] Iniciando o servidor Backend (FastAPI)...
start "Specter Backend" /min cmd /c "cd backend && .\venv\Scripts\python main.py"

echo [1.5/3] Iniciando o IAEdu Proxy...
start "Specter IAEdu Proxy" /min cmd /c "cd backend && .\venv\Scripts\python iaedu_proxy.py"

echo [2/3] Iniciando o servidor Frontend (Vite)...
start "Specter Frontend" /min cmd /c "cd frontend && npm run dev"

echo [3/3] Aguardando a inicializacao dos servicos...
timeout /t 4 /nobreak > nul

echo.
echo Lancando a App Desktop (Electron)...
cd frontend
call npm run desktop

echo.
echo A fechar os processos filhos...
taskkill /FI "WindowTitle eq Specter Backend*" /T /F > nul 2>&1
taskkill /FI "WindowTitle eq Specter IAEdu Proxy*" /T /F > nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5173" ^| find "LISTENING"') do taskkill /f /t /pid %%a > nul 2>&1
