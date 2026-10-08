@echo off
rem Сборка исполняемого файла dist\FamilyBudget.exe
cd /d "%~dp0"
pyinstaller --noconfirm --onefile --windowed --name FamilyBudget --icon resources\icon.ico --add-data "resources;resources" main.py
pause
