@echo off
:: Entramos a la carpeta del bat y luego retrocedemos a la raiz del proyecto
cd /d "%~dp0"
cd ..

call .venv1\Scripts\activate.bat
start pythonw servicios_iot\recolector.py