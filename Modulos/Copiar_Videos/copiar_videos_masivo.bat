@echo off
chcp 65001 > nul
cls

REM ============================================================================
REM   COPIAR VIDEOS DE EVIDENCIAS - MODO MASIVO
REM ============================================================================
REM
REM   Este script procesa TODAS las HUs encontradas en una carpeta base.
REM   Ideal para copiar múltiples HUs de una sola vez desde Linktic.
REM
REM ============================================================================

echo.
echo ================================================================================
echo   COPIAR VIDEOS DE EVIDENCIAS - MODO MASIVO
echo ================================================================================
echo.
echo   Este script procesara TODAS las HUs que encuentre en la carpeta base.
echo   Busca automaticamente las carpetas de HU y copia todos los videos.
echo.
echo   Presiona cualquier tecla para continuar...
echo ================================================================================
pause > nul

REM Obtener la ruta del script actual
set "SCRIPT_DIR=%~dp0"

REM Subir dos niveles para llegar a la raíz del proyecto (Copiar_Videos -> Modulos -> AutCert)
cd /d "%SCRIPT_DIR%..\.."

REM Ejecutar el script de Python
python "Modulos\Copiar_Videos\copiar_videos_masivo.py"

REM Pausa final (por si hay errores)
if errorlevel 1 (
    echo.
    echo ================================================================================
    echo   ERROR: El script termino con errores
    echo ================================================================================
    echo.
    pause
)
