@echo off
REM ============================================================
REM  Faro - lanzador de un clic (Windows)
REM  Doble clic en este fichero para arrancar la herramienta.
REM ============================================================
title Faro
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo.
  echo  No se ha encontrado Python.
  echo  Instalalo gratis desde https://www.python.org/downloads/
  echo  (marca la casilla "Add Python to PATH" al instalar) y vuelve a abrir este fichero.
  echo.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo  Preparando Faro por primera vez. Esto tarda un par de minutos solo la primera vez...
  python -m venv .venv
  call ".venv\Scripts\activate.bat"
  python -m pip install --upgrade pip >nul
  python -m pip install -e .
) else (
  call ".venv\Scripts\activate.bat"
)

echo.
echo  Faro esta arrancando. Se abrira solo en el navegador.
echo  Para cerrarlo, cierra esta ventana negra.
echo.
start "" http://localhost:8000
python -m faro.server
pause
