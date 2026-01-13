@echo off
chcp 65001 >nul
cd /d "%~dp0scripts"
python iniciar_sesion_azure.py
pause
