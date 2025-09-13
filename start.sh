#!/bin/bash
# MCP Tesseract Server Startskript für Linux/macOS

echo "MCP Tesseract Server wird gestartet..."
echo

echo "Prüfe Python-Installation..."
if ! command -v python3 &> /dev/null; then
    echo "FEHLER: Python3 ist nicht installiert."
    exit 1
fi

python3 --version
echo

echo "Prüfe Abhängigkeiten..."
if ! python3 -c "import pytesseract" &> /dev/null; then
    echo "Installiere Python-Abhängigkeiten..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "FEHLER: Installation der Abhängigkeiten fehlgeschlagen."
        exit 1
    fi
fi

echo
echo "Starte MCP Server..."
python3 server.py
