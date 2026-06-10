@echo off
REM ============================================================
REM  Faro - DEMO en vivo (Windows)
REM  Doble clic. Sale un QR; el cliente lo escanea con el movil
REM  (en datos 4G/5G) y ve su web. Cierra la ventana para parar.
REM ============================================================
title Faro - Demo en vivo
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo.
  echo  No se ha encontrado Python. Instalalo desde https://www.python.org/downloads/
  echo  (marca "Add Python to PATH") y vuelve a abrir este fichero.
  echo.
  pause
  exit /b 1
)

echo.
echo  Escribe el negocio y pulsa Enter.
echo    - un negocio del censo:   casa-paco
echo    - una web de ejemplo:     bar
echo    - formulario en blanco:   deja vacio y pulsa Enter
echo.
set /p NEGOCIO="  Negocio: "

echo.
echo  Arrancando la demo. Espera al QR (tarda unos segundos)...
echo.
python -m faro.livedemo %NEGOCIO%

echo.
echo  Demo cerrada.
pause
