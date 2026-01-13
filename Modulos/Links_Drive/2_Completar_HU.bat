@echo off
chcp 65001 > nul
cls

REM ============================================================================
REM   COMPLETAR CERTIFICACIÓN CON LINKS DE DRIVE
REM ============================================================================

echo.
echo ================================================================================
echo   COMPLETAR CERTIFICACIÓN CON LINKS DE DRIVE
echo ================================================================================
echo.
echo   Este script extrae los links de Drive y los agrega a tu certificación.
echo.
echo ================================================================================
echo.
pause

REM Obtener la ubicación de este .bat
set "BAT_DIR=%~dp0"

REM Subir 2 niveles: Links_Drive -> Modulos -> AutCert
cd /d "%BAT_DIR%..\..\"

REM Ejecutar script Python (ruta relativa desde AutCert)
python "Modulos\Links_Drive\scripts\completar_certificacion_interactivo.py"

REM Pausa final
if errorlevel 1 (
    echo.
    echo ================================================================================
    echo   ERROR: El script termino con errores
    echo ================================================================================
    echo.
)
pause
