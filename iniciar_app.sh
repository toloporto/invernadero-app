#!/bin/bash
# Lanzador para Linux y macOS
cd "$(dirname "$0")"

echo "========================================================"
echo "  🌱 INVERNADERO GALEGO • LIBRO DE CAMPO DIGITAL"
echo "========================================================"

if [ -f ".venv/bin/python" ]; then
    .venv/bin/python desktop_launcher.py
else
    python3 desktop_launcher.py
fi
