@echo off
chcp 65001 > nul
title Completar HU - Playwright

echo ============================================================
echo         COMPLETAR UNA HU (PLAYWRIGHT)
echo ============================================================
echo.
echo Version con Playwright para scroll correcto.
echo Usa esto para probar antes del procesamiento masivo.
echo.
echo ============================================================
echo.

cd /d "%~dp0..\.."
py Modulos\Links_Drive\scripts\completar_hu_playwright.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] El script termino con errores
    echo.
)

pause
