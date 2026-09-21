@echo off
chcp 65001 >nul
python foto_secim.py
if errorlevel 1 pause
