@echo off
chcp 65001 >nul
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --clean --windowed --name FotoSecim --add-data "assets;assets" foto_secim.py
pause
