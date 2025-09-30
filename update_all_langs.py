#!/usr/bin/env python3
"""
Update all language files with missing strings from en.conf (source of truth)
Appends missing sections to each language file.
"""

import os
import re

LANG_DIR = "lang"
SOURCE_FILE = f"{LANG_DIR}/en.conf"

# All language codes
LANGUAGES = [
    "de", "es", "fr", "it", "ca", "eu", "gl", "zh", "hi",
    "de-schwaebisch", "de-bayerisch", "de-saechsisch",
    "es-mexicano", "es-argentino", "es-colombiano", "es-venezolano", "es-chileno", "es-andaluz"
]

# Manual translations for the new strings (key languages)
TRANSLATIONS = {
    "de": {
        "# Installation Locations & Sharing": "# Installation Locations & Sharing",
        "LANG_INSTALL_LOCATION_TITLE": '"📦 Installations-Orte"',
        "LANG_INSTALL_LOCATION_LOCAL": '"Lokal (nur diese App):"',
        "LANG_INSTALL_LOCATION_LOCAL_PATH": '"~/.aichat/ - Skripte, Config, deine Daten"',
        "LANG_INSTALL_LOCATION_GLOBAL": '"Global (geteilt mit anderen Apps):"',
        "LANG_INSTALL_LOCATION_GLOBAL_MODELS": '"KI-Modelle, Python-Pakete"',
        "LANG_INSTALL_LOCATION_BENEFIT": '"✨ Vorteil: Globale Modelle können von anderen Anwendungen genutzt werden!"',
        "LANG_INSTALL_LOCATION_WARNING": '"⚠️  Bei Deinstallation bleiben globale Modelle für andere Apps erhalten"',
        "LANG_INSTALL_SHARED_INFO": '"Dieses Modell ist global installiert und kann von anderen Anwendungen genutzt werden."',
        "LANG_INSTALL_SHARED_BENEFIT": '"Wenn du dieses Modell schon hast, nutzen wir es - kein erneuter Download nötig!"',
        "# Deletion Warnings": "# Deletion Warnings",
        "LANG_DELETE_WARNING_TITLE": '"⚠️  Lösch-Warnung"',
        "LANG_DELETE_WARNING_SHARED": '"Dieses Modell ist global installiert und wird evtl. von anderen Anwendungen verwendet."',
        "LANG_DELETE_WARNING_CHECK": '"Bitte prüfe ob andere Apps dies nutzen, bevor du es entfernst:"',
        "LANG_DELETE_WARNING_PRESIDIO": '"Presidio wird evtl. genutzt von: Datenanalyse-Tools, Datenschutz-Scanner, NLP-Projekten"',
        "LANG_DELETE_WARNING_PHI3": '"Phi-3 wird evtl. genutzt von: Ollama-Projekten, lokalen KI-Assistenten, Coding-Tools"',
        "LANG_DELETE_WARNING_SPACY": '"spaCy-Modelle werden evtl. genutzt von: NLP-Projekten, Textanalyse-Tools, anderen KI-Apps"',
        "LANG_DELETE_WARNING_CONFIRM": '"Bist du sicher dass du dies entfernen willst? Andere Apps könnten es brauchen."',
        "LANG_DELETE_SAFE_LOCAL": '"Sicher zu löschen - wird nur von AI Chat Terminal genutzt"',
        "LANG_DELETE_WARNING_GLOBAL": '"⚠️  Globales Modell - erst andere Apps prüfen!"',
    },
    "es": {
        "# Installation Locations & Sharing": "# Installation Locations & Sharing",
        "LANG_INSTALL_LOCATION_TITLE": '"📦 Ubicaciones de Instalación"',
        "LANG_INSTALL_LOCATION_LOCAL": '"Local (solo esta app):"',
        "LANG_INSTALL_LOCATION_LOCAL_PATH": '"~/.aichat/ - Scripts, config, tus datos"',
        "LANG_INSTALL_LOCATION_GLOBAL": '"Global (compartido con otras apps):"',
        "LANG_INSTALL_LOCATION_GLOBAL_MODELS": '"Modelos IA, paquetes Python"',
        "LANG_INSTALL_LOCATION_BENEFIT": '"✨ Beneficio: ¡Los modelos globales pueden ser usados por otras aplicaciones!"',
        "LANG_INSTALL_LOCATION_WARNING": '"⚠️  Al desinstalar, los modelos globales permanecen para otras apps"',
        "LANG_INSTALL_SHARED_INFO": '"Este modelo está instalado globalmente y puede ser usado por otras aplicaciones."',
        "LANG_INSTALL_SHARED_BENEFIT": '"¡Si ya tienes este modelo, lo usaremos - no es necesario descargarlo otra vez!"',
        "# Deletion Warnings": "# Deletion Warnings",
        "LANG_DELETE_WARNING_TITLE": '"⚠️  Advertencia de Eliminación"',
        "LANG_DELETE_WARNING_SHARED": '"Este modelo está instalado globalmente y puede ser usado por otras aplicaciones."',
        "LANG_DELETE_WARNING_CHECK": '"Por favor verifica si otras apps lo usan antes de eliminarlo:"',
        "LANG_DELETE_WARNING_PRESIDIO": '"Presidio podría ser usado por: herramientas de análisis, escáneres de privacidad, proyectos NLP"',
        "LANG_DELETE_WARNING_PHI3": '"Phi-3 podría ser usado por: proyectos Ollama, asistentes IA locales, herramientas de código"',
        "LANG_DELETE_WARNING_SPACY": '"Modelos spaCy podrían ser usados por: proyectos NLP, herramientas de análisis, otras apps IA"',
        "LANG_DELETE_WARNING_CONFIRM": '"¿Estás seguro de eliminarlo? Otras apps podrían necesitarlo."',
        "LANG_DELETE_SAFE_LOCAL": '"Seguro eliminar - solo usado por AI Chat Terminal"',
        "LANG_DELETE_WARNING_GLOBAL": '"⚠️  Modelo global - ¡verifica otras apps primero!"',
    }
}

def read_source_new_sections():
    """Read the new sections from en.conf"""
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract the new sections (after LANG_PRIVACY_INVALID)
    match = re.search(r'LANG_PRIVACY_INVALID=.*?\n\n(.*)', content, re.DOTALL)
    if match:
        return match.group(1)
    return ""

def check_if_has_new_sections(lang_file):
    """Check if language file already has the new sections"""
    if not os.path.exists(lang_file):
        return False

    with open(lang_file, 'r', encoding='utf-8') as f:
        content = f.read()

    return "LANG_INSTALL_LOCATION_TITLE" in content

def append_new_sections(lang_code):
    """Append new sections to a language file"""
    lang_file = f"{LANG_DIR}/{lang_code}.conf"

    if not os.path.exists(lang_file):
        print(f"  ⚠️  {lang_code}.conf not found, skipping")
        return False

    if check_if_has_new_sections(lang_file):
        print(f"  ✓ {lang_code}.conf already updated")
        return True

    # Get translations for this language (fallback to English)
    translations = TRANSLATIONS.get(lang_code, {})

    # Read English source
    new_sections = read_source_new_sections()

    # If we have specific translations, use them
    if translations:
        for en_key, translated_value in translations.items():
            if en_key.startswith("#"):
                # Comment line
                new_sections = new_sections.replace(en_key, en_key)
            else:
                # Find the English value and replace
                en_match = re.search(f'{en_key}="([^"]*)"', new_sections)
                if en_match:
                    new_sections = new_sections.replace(
                        f'{en_key}="{en_match.group(1)}"',
                        f'{en_key}={translated_value}'
                    )

    # Append to file
    with open(lang_file, 'a', encoding='utf-8') as f:
        f.write("\n")
        f.write(new_sections)

    print(f"  ✅ {lang_code}.conf updated")
    return True

def main():
    print("🌍 Updating all language files with new strings...\n")

    # Check source file
    if not os.path.exists(SOURCE_FILE):
        print(f"❌ Source file {SOURCE_FILE} not found!")
        return

    print(f"📖 Source: {SOURCE_FILE} (English - Source of Truth)\n")

    updated = 0
    skipped = 0

    for lang_code in LANGUAGES:
        if append_new_sections(lang_code):
            updated += 1
        else:
            skipped += 1

    print(f"\n✅ Complete!")
    print(f"   Updated: {updated} files")
    print(f"   Skipped: {skipped} files")

if __name__ == "__main__":
    main()
