# MCP Server für Tesseract OCR

Ein Model Context Protocol (MCP) Server für Tesseract OCR, optimiert für Windows 11 und VS Code.

## Features

- **Textextraktion aus Bildern**: Unterstützt PNG, JPG, TIFF und andere Bildformate
- **PDF-OCR**: Extrahiert Text aus PDF-Dokumenten mit automatischer OCR-Fallback  
- **Mehrsprachig**: Unterstützt alle verfügbaren Tesseract-Sprachen
- **Windows 11 optimiert**: Automatische Tesseract-Erkennung unter Windows
- **VS Code Integration**: Einfache Ausführung in VS Code

## Installation

### Voraussetzungen

1. **Tesseract OCR installieren**:
   - Download von: https://github.com/UB-Mannheim/tesseract/wiki
   - Während der Installation: "Additional language data" auswählen für Deutsch/andere Sprachen
   - Standard-Installationspfad: `C:\Program Files\Tesseract-OCR\`

2. **Python-Abhängigkeiten installieren**:
   ```bash
   cd mcp_server_tesseract
   python -m venv venv
   venv/Scripts/acivate
   
   # Abhaengigkeiten mit pip und pyproject.toml installieren
   pip install -e .
   ```

### Server starten

```bash
mcp-server-tesseract --project-dir /path/to/project
```

### Kommandozeilen Argumente:

- `--project-dir`: (Required) Directory to serve files from

## Verfügbare Tools

### 1. `extract_text_from_image`
Extrahiert Text aus Bilddateien.

**Parameter:**
- `image_path` (string): Pfad zur Bilddatei
- `language` (string, optional): Sprachcode (Standard: "deu")

### 2. `extract_text_from_pdf`  
Extrahiert Text aus PDF-Dateien mit automatischer OCR-Fallback.

**Parameter:**
- `pdf_path` (string): Pfad zur PDF-Datei
- `language` (string, optional): Sprachcode (Standard: "deu")

### 3. `check_tesseract_languages`
Listet alle verfügbaren Tesseract-Sprachen auf.

## Unterstützte Sprachen

- `deu` - Deutsch
- `eng` - Englisch  
- `fra` - Französisch
- `spa` - Spanisch
- `ita` - Italienisch
- Und viele weitere (abhängig von der Tesseract-Installation)

## Troubleshooting

### Tesseract nicht gefunden
Wenn der Fehler "Tesseract nicht gefunden" auftritt:

1. Überprüfen Sie die Installation von Tesseract OCR
2. Stellen Sie sicher, dass Tesseract im Windows PATH ist
3. Oder installieren Sie es im Standard-Verzeichnis: `C:\Program Files\Tesseract-OCR\`

### Fehlende Sprachpakete
Für bessere OCR-Ergebnisse installieren Sie zusätzliche Sprachpakete:
1. Tesseract erneut herunterladen
2. Bei der Installation "Additional language data" auswählen
3. Gewünschte Sprachen markieren

## VS Code Usage

1. Öffnen Sie das `mcp_server_tesseract` Verzeichnis in VS Code
2. Drücken Sie `F5` oder gehen Sie zu Run > Start Debugging
3. Wählen Sie "Python File" als Konfiguration
4. Der Server startet im integrierten Terminal

## Lizenz

MIT License
