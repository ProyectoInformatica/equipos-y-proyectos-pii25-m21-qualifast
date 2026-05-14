#!/bin/bash
echo "Deteniendo los procesos de Python en segundo plano..."

pkill -f recolector.py

echo "🛑 El recolector ha sido apagado."