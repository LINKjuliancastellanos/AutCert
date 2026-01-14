@echo off
chcp 65001 > nul
title Verificador de Estado de Certificaciones

echo ============================================================
echo       VERIFICADOR DE ESTADO DE CERTIFICACIONES
echo ============================================================
echo.
echo Este script analiza TODAS las certificaciones y muestra:
echo   - Cuantas tienen links completos
echo   - Cuantas tienen links parciales
echo   - Cuantas estan vacias (sin links)
echo.
echo Util para ejecutar ANTES y DESPUES del procesamiento masivo.
echo.
echo ============================================================
echo.

cd /d "%~dp0..\.."
py Modulos\Links_Drive\scripts\verificar_estado_certificaciones.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] El script termino con errores
    echo.
)

pause
