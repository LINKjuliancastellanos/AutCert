@echo off
chcp 65001 > nul
cls

REM ============================================================================
REM   INICIAR SESIÓN EN GOOGLE DRIVE
REM ============================================================================

echo.
echo ================================================================================
echo   INICIAR SESIÓN EN GOOGLE DRIVE
echo ================================================================================
echo.
echo   Este script guarda tu sesión de Google para usar en otros scripts.
echo.
echo ================================================================================
echo.
pause

REM Obtener la ubicación de este .bat
set "BAT_DIR=%~dp0"

REM Subir 2 niveles: Links_Drive -> Modulos -> AutCert
cd /d "%BAT_DIR%..\..\"

REM Ejecutar script Python (ruta relativa desde AutCert)
python "Modulos\Links_Drive\scripts\iniciar_sesion_drive.py"

REM Pausa final
if errorlevel 1 (
    echo.
    echo ================================================================================
    echo   ERROR: El script termino con errores
    echo ================================================================================
    echo.
)
pause
