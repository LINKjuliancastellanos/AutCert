@echo off
chcp 65001 >nul
cd /d "%~dp0scripts"
python capturar_evidencia_single.py
pause
