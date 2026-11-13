@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Nexa Premium Tweak

net session >nul 2>nul
if errorlevel 1 (
    echo Yonetici izni isteniyor...
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

set PY=
py -3 --version >nul 2>nul && set PY=py -3
if "%PY%"=="" (
    python --version >nul 2>nul && set PY=python
)
if "%PY%"=="" (
    echo Python bulunamadi. python.org adresinden Python 3.10+ kurun.
    pause
    exit /b 1
)

%PY% -c "import customtkinter, PIL" >nul 2>nul
if errorlevel 1 (
    echo Gerekli paketler kuruluyor...
    %PY% -m pip install customtkinter pillow
)

%PY% app.py
if errorlevel 1 (
    echo.
    echo Program hata ile kapandi. Yukaridaki hata mesajinin ekran goruntusunu gonderin.
    pause
)
