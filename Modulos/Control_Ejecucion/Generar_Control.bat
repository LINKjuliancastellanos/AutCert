@echo off
chcp 65001 > nul
title Generar Archivo de Control - AutCert

echo ============================================================
echo    GENERADOR DE ARCHIVO DE CONTROL DE EJECUCION
echo    AutCert - Automatizacion de Certificaciones QA
echo ============================================================
echo.

cd /d "%~dp0"

echo Verificando Python...
python --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    echo Por favor instale Python 3.8 o superior
    pause
    exit /b 1
)

echo Verificando dependencias...
python -c "import pandas; import openpyxl" > nul 2>&1
if errorlevel 1 (
    echo [AVISO] Instalando dependencias necesarias...
    pip install pandas openpyxl
    echo.
)

echo.
echo Ejecutando generador de archivo de control...
echo.

python generar_control.py

echo.
echo ============================================================
if errorlevel 1 (
    echo [ERROR] Ocurrio un error durante la generacion
) else (
    echo [OK] Proceso completado
    echo.
    echo El archivo se encuentra en:
    echo %~dp0datos\control_ejecucion.xlsx
)
echo ============================================================
echo.
pause
