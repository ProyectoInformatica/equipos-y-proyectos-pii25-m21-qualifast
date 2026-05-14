@echo off
:: Esto asegura que la terminal se abra en la carpeta correcta del proyecto
cd /d "%~dp0"

echo Activando el entorno virtual...
:: Cambia ".venv1" por el nombre de tu entorno si al final lo llamaste distinto
call .venv1\Scripts\activate.bat

echo Arrancando el recolector (Modo visible)...
:: Usamos "python" normal para poder ver si hay algun error
python recolector.py

pause