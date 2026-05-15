@echo off
echo Deteniendo los procesos de Python en segundo plano...
taskkill /f /im pythonw.exe
echo El recolector ha sido apagado.
pause