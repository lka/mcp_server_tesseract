#!/usr/bin/env python3
"""
Tessskript für den MCP Tesseract Server
"""

import os
import sys
# import asyncio
from server import (
    check_tesseract_languages,
    extract_text_from_image,
    extract_text_from_pdf,
    set_project_dir,
    extract_images_from_pdf,
)


def test_tesseract_installation():
    set_project_dir(".")
    """Testet die Tesseract-Installation"""
    print("=== Tesseract Installation Test ===")
    result = check_tesseract_languages()

    if result["success"]:
        print("✓ Tesseract wurde erfolgreich gefunden!")
        print(f"  Version: {result['tesseract_version']}")
        print(f"  Pfad: {result['tesseract_path']}")
        print(f"  Verfügbare Sprachen: {result['language_count']}")
        print(
            f"  Deutsch verfügbar: {'✓' if result['recommended_for_german'] else '✗'}"
        )
        print(
            f"  Englisch verfügbar: {'✓' if result['recommended_for_english'] else '✗'}"
        )

        if result["common_languages"]:
            print("  Häufige Sprachen:")
            for code, name in result["common_languages"].items():
                print(f"    - {code}: {name}")
    else:
        print("✗ Tesseract-Installation fehlerhaft!")
        print(f"  Fehler: {result['error']}")
        return False

    return True


def test_image_ocr():
    """Testet OCR mit einem Beispielbild (falls vorhanden)"""
    print("\n=== Bild-OCR Test ===")

    # Suche nach Testbildern im aktuellen Verzeichnis
    test_files = [
        "test.png",
        "test.jpg",
        "test.jpeg",
        "test.tiff",
        "sample.png",
        "sample.jpg",
        "beispiel.png",
        "beispiel.jpg",
    ]

    for filename in test_files:
        if os.path.exists(filename):
            print(f"Teste OCR mit: {filename}")
            result = extract_text_from_image(filename, "deu")

            if result["success"]:
                print("✓ OCR erfolgreich!")
                print(f"  Extrahierte Zeichen: {len(result['text'])}")
                print(f"  Wörter: {result['word_count']}")
                print(f"  Durchschnittliche Konfidenz: {result['average_confidence']}%")
                if result["text"]:
                    print(f"  Vorschau: {result['text'][:100]}...")
                return True
            else:
                print(f"✗ OCR fehlgeschlagen: {result['error']}")
                return False

    print(
        "ℹ Kein Testbild gefunden. Legen Sie ein Bild mit dem Namen 'test.png' in diesen Ordner."
    )
    return True


def test_images_extract():
    """Testet Image extraction mit einem Beispiel PDF (falls vorhanden)"""
    print("\n=== PDF-Extraction Test ===")

    # Suche nach Test PDF im aktuellen Verzeichnis
    test_files = [
        "test.pdf",
        "beispiel.pdf",
    ]

    for filename in test_files:
        if os.path.exists(filename):
            print(f"Teste Image Extraction mit: {filename}")
            result = extract_images_from_pdf(filename)

            if result["success"]:
                print("✓ Extraction erfolgreich!")
                print(f"  Extrahierte Images: {len(result['extracted_images'])}")
                print(f"  Processed Pages: {result['processed_pages']}")
                print(f"  Seitenanzahl: {result['total_pages']}")
                return True
            else:
                print(f"✗ Extraction fehlgeschlagen: {result['error']}")
                return False

    print(
        "ℹ Kein Test PDF gefunden. Legen Sie eine PDF mit dem Namen 'test.pdf' in diesen Ordner."
    )
    return True


def test_pdf_ocr():
    """Testet OCR mit einem Beispiel PDF (falls vorhanden)"""
    print("\n=== PDF-OCR Test ===")

    # Suche nach Test PDF im aktuellen Verzeichnis
    test_files = [
        "test.pdf",
        "beispiel.pdf",
    ]

    for filename in test_files:
        if os.path.exists(filename):
            print(f"Teste OCR mit: {filename}")
            result = extract_text_from_pdf(filename, "deu")

            if result["success"]:
                print("✓ OCR erfolgreich!")
                print(f"  Extrahierte Zeichen: {len(result['text'])}")
                print(f"  Wörter: {result['word_count']}")
                print(f"  Seitenanzahl: {result['processed_pages']}")
                if result["text"]:
                    print(f"  Vorschau: {result['text'][:100]}...")
                return True
            else:
                print(f"✗ OCR fehlgeschlagen: {result['error']}")
                return False

    print(
        "ℹ Kein Test PDF gefunden. Legen Sie eine PDF mit dem Namen 'test.pdf' in diesen Ordner."
    )
    return True


def main():
    """Hauptfunktion für den Test"""
    print("MCP Tesseract Server - Systemtest")
    print("=" * 50)

    # Test 1: Tesseract Installation
    if not test_tesseract_installation():
        print(
            "\n❌ Tesseract Installation fehlerhaft. Bitte installieren Sie Tesseract OCR."
        )
        print("Download: https://github.com/UB-Mannheim/tesseract/wiki")
        return 1

    # Test 2: Bild-OCR (optional)
    test_image_ocr()

    # Test 3: PDF-OCR (optional)
    test_pdf_ocr()

    # Test 4: extract image(s) from PDF (optional)
    test_images_extract()

    print("\n" + "=" * 50)
    print("✓ Tests abgeschlossen! Der MCP Server sollte funktionieren.")
    print("\nStarten Sie den Server mit:")
    print("  mcp-server-tesseract --project-dir /path/to/project")
    print("\nOder verwenden Sie das Startskript:")
    print("  start.ps1 (Windows)")
    # print("  ./start.sh (Linux/macOS)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
