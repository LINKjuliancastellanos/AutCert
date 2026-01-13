@echo off
chcp 65001 > nul
cls

REM ============================================================================
REM   COPIAR VIDEOS DE EVIDENCIAS
REM ============================================================================
REM
REM   Este script ejecuta el copiador interactivo de videos de evidencias.
REM   Te permitirá copiar videos desde carpetas externas (Linktic, etc.)
REM   hacia la estructura organizada en EntregaCerts.
REM
REM ============================================================================

echo.
echo ================================================================================
echo   COPIAR VIDEOS DE EVIDENCIAS A ENTREGACERTS
echo ================================================================================
echo.
echo   Este script te guiara para copiar videos desde carpetas externas
echo   hacia la estructura organizada en EntregaCerts.
echo.
echo   Presiona cualquier tecla para continuar...
echo ================================================================================
pause > nul

REM Obtener la ruta del script actual
set "SCRIPT_DIR=%~dp0"

REM Subir dos niveles para llegar a la raíz del proyecto (Copiar_Videos -> Modulos -> AutCert)
cd /d "%SCRIPT_DIR%..\.."

REM Ejecutar el script de Python
python "Modulos\Copiar_Videos\copiar_videos_evidencias.py"

REM Pausa final (por si hay errores)
if errorlevel 1 (
    echo.
    echo ================================================================================
    echo   ERROR: El script termino con errores
    echo ================================================================================
    echo.
    pause
)
