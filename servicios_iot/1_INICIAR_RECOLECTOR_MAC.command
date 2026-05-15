#!/bin/bash
# Navegar a la carpeta donde está este script
cd cd.."$(dirname "$0")"

echo "Activando entorno virtual..."
source .venv/bin/activate

echo "Iniciando motor IoT en segundo plano..."
# 'nohup' hace que Python corra de forma invisible
nohup python3 recolector.py > /dev/null 2>&1 &

echo "✅ Listo. Ya puedes cerrar esta ventana. El programa seguira leyendo datos."