@echo off
chcp 65001 >nul
cd /d "%~dp0scripts"
python completar_certificacion_interactivo.py
pause
