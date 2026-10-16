@echo off
title Invernadero Galego - Libro de Campo
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================================
echo   🌱 INVERNADERO GALEGO • LIBRO DE CAMPO DIGITAL
echo ========================================================
echo Iniciando entorno y abriendo aplicacion de escritorio...

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" desktop_launcher.py
) else (
    echo [Error] No se encontro el entorno virtual en .venv.
    echo Ejecuta: python -m venv .venv ^&^& .venv\Scripts\activate ^&^& pip install -r requirements.txt
    pause
)
