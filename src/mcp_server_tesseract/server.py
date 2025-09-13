#!/usr/bin/env python3
"""
MCP Server für Tesseract OCR
Unterstützt Textextraktion aus Bildern und PDFs unter Windows 11
"""

import argparse
import asyncio
import json
import sys
import os
import tempfile
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pytesseract
from PIL import Image
import fitz  # PyMuPDF
from mcp.server.fastmcp import FastMCP

# MCP Server initialisieren
mcp = FastMCP("tesseract-ocr")

# Store the project directory as a module-level variable
_project_dir: Optional[Path] = None


def set_project_dir(directory: Path) -> None:
    """Set the project directory for file operations.

    Args:
        directory: The project directory path
    """
    global _project_dir
    _project_dir = Path(directory)


# Tesseract-Pfad für Windows 11 konfigurieren
def setup_tesseract_windows():
    """Konfiguriert Tesseract für Windows 11"""
    possible_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(
            os.getenv("USERNAME", "")
        ),
    ]

    # Prüfe ob Tesseract im PATH ist
    try:
        result = subprocess.run(
            ["tesseract", "--version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Suche in möglichen Installationspfaden
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            return True

    return False


# Tesseract beim Start konfigurieren
if not setup_tesseract_windows():
    print(
        "WARNUNG: Tesseract nicht gefunden. Bitte installieren Sie Tesseract-OCR für Windows."
    )
    print("Download: https://github.com/UB-Mannheim/tesseract/wiki")


@mcp.tool()
def extract_text_from_image(image_path: str, language: str = "deu") -> Dict[str, Any]:
    """
    Extrahiert Text aus einem Bild mittels Tesseract OCR

    Args:
        image_path: Pfad zum Bild (PNG, JPG, TIFF, etc.)
        language: Tesseract Sprachcode (z.B. 'deu' für Deutsch, 'eng' für Englisch)

    Returns:
        Dict mit extrahiertem Text und Metadaten
    """
    try:
        # Überprüfe ob Datei existiert
        if _project_dir is None:
            raise ValueError("Project directory has not been set")

        if not os.path.exists(os.path.join(_project_dir, image_path)):
            return {
                "success": False,
                "error": f"Datei nicht gefunden: {image_path}",
                "text": "",
            }

        # Lade das Bild
        image = Image.open(os.path.join(_project_dir, image_path))

        # Konvertiere zu RGB falls nötig (für PDFs/CMYK Bilder)
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")

        # OCR durchführen
        custom_config = f"--oem 3 --psm 6 -l {language}"
        extracted_text = pytesseract.image_to_string(image, config=custom_config)

        # Zusätzliche Informationen sammeln
        try:
            data = pytesseract.image_to_data(
                image, output_type=pytesseract.Output.DICT, config=custom_config
            )
            confidence_scores = [int(conf) for conf in data["conf"] if int(conf) > 0]
            avg_confidence = (
                sum(confidence_scores) / len(confidence_scores)
                if confidence_scores
                else 0
            )
        except:
            avg_confidence = 0

        return {
            "success": True,
            "text": extracted_text.strip(),
            "language": language,
            "image_path": image_path,
            "image_size": image.size,
            "average_confidence": round(avg_confidence, 2),
            "word_count": len(extracted_text.split()),
        }

    except Exception as e:
        return {"success": False, "error": str(e), "text": "", "image_path": image_path}


@mcp.tool()
def extract_text_from_pdf(pdf_path: str, language: str = "deu") -> Dict[str, Any]:
    """
    Extrahiert Text aus einem PDF mittels OCR

    Args:
        pdf_path: Pfad zur PDF-Datei
        language: Tesseract Sprachcode

    Returns:
        Dict mit extrahiertem Text und Metadaten
    """
    try:
        # Überprüfe ob Datei existiert
        if _project_dir is None:
            raise ValueError("Project directory has not been set")

        if not os.path.exists(os.path.join(_project_dir, pdf_path)):
            return {
                "success": False,
                "error": f"PDF-Datei nicht gefunden: {pdf_path}",
                "text": "",
            }

        # PDF öffnen
        doc = fitz.open(os.path.join(_project_dir, pdf_path))
        all_text = []
        processed_pages = 0

        with tempfile.TemporaryDirectory() as temp_dir:
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)

                # Versuche zuerst Textextraktion ohne OCR
                page_text = page.get_text().strip()

                if len(page_text) > 50:  # Wenn genug Text vorhanden ist
                    all_text.append(f"=== Seite {page_num + 1} ===\n{page_text}")
                else:
                    # OCR verwenden für Seiten ohne Text oder mit wenig Text
                    # PDF-Seite als Bild rendern
                    mat = fitz.Matrix(2.0, 2.0)  # 2x Zoom für bessere OCR-Qualität
                    pix = page.get_pixmap(matrix=mat)

                    # Temporäres Bild speichern
                    img_path = os.path.join(temp_dir, f"page_{page_num}.png")
                    pix.save(img_path)

                    # OCR auf das Bild anwenden
                    result = extract_text_from_image(img_path, language)
                    # print("\n", result)
                    if result["success"] and result["text"]:
                        all_text.append(
                            f"=== Seite {page_num + 1} (OCR) ===\n{result['text']}"
                        )
                    elif page_text:
                        # Fallback auf den ursprünglichen Text
                        all_text.append(f"=== Seite {page_num + 1} ===\n{page_text}")

                processed_pages += 1

        doc.close()

        combined_text = "\n\n".join(all_text)

        return {
            "success": True,
            "text": combined_text,
            "language": language,
            "pdf_path": pdf_path,
            "total_pages": page_num,
            "processed_pages": processed_pages,
            "word_count": len(combined_text.split()),
        }

    except Exception as e:
        return {"success": False, "error": str(e), "text": "", "pdf_path": pdf_path}


@mcp.tool()
def check_tesseract_languages() -> Dict[str, Any]:
    """
    Listet alle verfügbaren Tesseract-Sprachen auf

    Returns:
        Dict mit verfügbaren Sprachen und Statusinformationen
    """
    try:
        # Tesseract-Sprachen abrufen
        languages = pytesseract.get_languages()

        # Tesseract-Version abrufen
        try:
            result = subprocess.run(
                [pytesseract.pytesseract.tesseract_cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            version_info = (
                result.stdout.split("\n")[0] if result.stdout else "Unbekannt"
            )
        except:
            version_info = "Unbekannt"

        # Häufig verwendete Sprachen hervorheben
        common_languages = {
            "deu": "Deutsch",
            "eng": "Englisch",
            "fra": "Französisch",
            "spa": "Spanisch",
            "ita": "Italienisch",
            "por": "Portugiesisch",
            "rus": "Russisch",
            "chi_sim": "Chinesisch (vereinfacht)",
            "chi_tra": "Chinesisch (traditionell)",
            "jpn": "Japanisch",
            "ara": "Arabisch",
        }

        available_common = {
            code: name for code, name in common_languages.items() if code in languages
        }

        return {
            "success": True,
            "tesseract_version": version_info,
            "tesseract_path": pytesseract.pytesseract.tesseract_cmd,
            "available_languages": sorted(languages),
            "language_count": len(languages),
            "common_languages": available_common,
            "recommended_for_german": "deu" in languages,
            "recommended_for_english": "eng" in languages,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "available_languages": [],
            "tesseract_path": pytesseract.pytesseract.tesseract_cmd,
        }


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="MCP tesseract Server")
    parser.add_argument(
        "--project-dir",
        type=str,
        required=True,
        help="Base directory for all file operations (required)",
    )
    return parser.parse_args()

# async def main():
    # """Hauptfunktion zum Starten des MCP-Servers"""
    # Server über stdio starten
    # from mcp.server.stdio import stdio_server

    # async with stdio_server() as (read_stream, write_stream):
    #    await mcp.run(read_stream, write_stream, mcp.create_initialization_options())


def main() -> None:
    args = parse_args()

    # Validate project directory first
    project_dir = Path(args.project_dir)
    if not project_dir.exists() or not project_dir.is_dir():
        print(
            f"Error: Project directory does not exist or is not a directory: {project_dir}"
        )
        sys.exit(1)

    # Convert to absolute path
    project_dir = project_dir.absolute()
    set_project_dir(project_dir)

    mcp.run()


if __name__ == "__main__":
    # asyncio.run(main())
    main()
