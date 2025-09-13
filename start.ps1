.\venv\Scripts\activate.ps1
write-Host "MCP Tesseract Server wird gestartet..."

Write-Host "Pruefe Python-Installation..."
python --version
if ($LASTEXITCODE -eq 1) {
    Write-Error "FEHLER: Python ist nicht installiert oder nicht im PATH verfuegbar."
    Read-Host -Prompt "Press Enter to continue"
    exit 1
}

write-Host "Pruefe Abhaengigkeiten..."
$V = pip show pytesseract 2>&1
if (($LASTEXITCODE -eq 1) -or ($V -like "*WARNING*")) {
    Write-Host "Installiere Python-Abhaengigkeiten..."
    pip install -r requirements.txt
    if ($LASTEXITCODE == 1) {
        Write-Error "FEHLER: Installation der Abhaengigkeiten fehlgeschlagen."
        Read-Host -Prompt "Press Enter to continue"
        exit 1
    }
}

write-Host "Starte MCP Server..."
src\mcp_server_tesseract\server.py --project_dir .
