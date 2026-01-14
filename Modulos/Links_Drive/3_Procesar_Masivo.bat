@echo off
chcp 65001 > nul
title Procesamiento Masivo de Certificaciones

echo ============================================================
echo       PROCESAMIENTO MASIVO DE CERTIFICACIONES
echo ============================================================
echo.
echo Este script procesara TODAS las certificaciones:
echo   - Escanea AyN, RyC y Transversal
echo   - Busca carpetas de HU en Drive
echo   - Extrae links de CPs
echo   - Actualiza cada Excel automaticamente
echo.
echo IMPORTANTE: Asegurate de haber ejecutado 1_Iniciar_Sesion.bat
echo             al menos una vez para tener sesion activa.
echo.
echo ============================================================
echo.

cd /d "%~dp0..\.."
py Modulos\Links_Drive\scripts\procesar_certificaciones_masivo.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] El script termino con errores
    echo.
)

pause
