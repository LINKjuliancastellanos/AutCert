@echo off
chcp 65001 > nul
title Procesamiento Masivo - Playwright

echo ============================================================
echo    PROCESAMIENTO MASIVO DE CERTIFICACIONES (PLAYWRIGHT)
echo ============================================================
echo.
echo Version mejorada con Playwright para scroll correcto.
echo.
echo Caracteristicas:
echo   - Scroll incremental en contenedor .PEfnhb
echo   - Forzar foco con hover y click
echo   - Validacion de scroll con scrollTop
echo   - Sesion persistente (solo login una vez)
echo.
echo ============================================================
echo.

cd /d "%~dp0..\.."
py Modulos\Links_Drive\scripts\procesar_certificaciones_playwright.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] El script termino con errores
    echo.
)

pause
