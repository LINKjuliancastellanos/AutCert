@echo off
chcp 65001 > nul
title Iniciar Sesion - Playwright

echo ============================================================
echo       INICIAR SESION EN GOOGLE DRIVE (PLAYWRIGHT)
echo ============================================================
echo.
echo Este script usa un perfil aislado de Chrome.
echo NO necesitas cerrar tu Chrome actual.
echo.
echo Tendras 120 segundos (2 minutos) para iniciar sesion.
echo.
echo ============================================================
echo.

cd /d "%~dp0..\.."
py Modulos\Links_Drive\scripts\iniciar_sesion_playwright.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] El script termino con errores
    echo.
    echo Si Playwright no esta instalado, ejecuta:
    echo   pip install playwright
    echo   playwright install chromium
    echo.
)

pause
