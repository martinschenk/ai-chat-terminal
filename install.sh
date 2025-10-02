#!/usr/bin/env bash
# AI Chat Terminal - Smart Interactive Installer v9.0.0
# Licensed under MIT License - https://opensource.org/licenses/MIT
# Requires: Bash 4+ or ZSH (for associative arrays)

set -e

# ═══════════════════════════════════════════════════════════════════
# System Requirements Check
# ═══════════════════════════════════════════════════════════════════

check_system_requirements() {
    # Check macOS
    if [[ "$OSTYPE" != "darwin"* ]]; then
        echo "❌ This installer requires macOS"
        echo ""
        echo "   Your system: $OSTYPE"
        echo "   Linux/Windows support: Coming soon"
        echo ""
        exit 1
    fi

    # Check macOS version (Catalina = 10.15 minimum)
    local macos_version=$(sw_vers -productVersion 2>/dev/null || echo "unknown")
    local major=$(echo $macos_version | cut -d. -f1)
    local minor=$(echo $macos_version | cut -d. -f2)

    if [[ "$macos_version" == "unknown" ]]; then
        echo "⚠️  Warning: Could not detect macOS version"
    elif [[ $major -lt 10 ]] || [[ $major -eq 10 && $minor -lt 15 ]]; then
        echo "❌ Requires macOS Catalina (10.15) or newer"
        echo ""
        echo "   Your macOS: $macos_version"
        echo "   Required: 10.15+"
        echo ""
        echo "   Please upgrade macOS first"
        exit 1
    fi

    # Check ZSH
    if ! command -v zsh &> /dev/null; then
        echo "❌ ZSH not found"
        echo ""
        echo "   ZSH should be default on macOS Catalina+"
        echo "   Please install ZSH first"
        exit 1
    fi

    # Check disk space
    local free_space=$(df -h ~ 2>/dev/null | awk 'NR==2 {print $4}' | sed 's/Gi//' | sed 's/G//')
    if [[ -n "$free_space" ]] && (( $(echo "$free_space < 5" | bc -l 2>/dev/null || echo "0") )); then
        echo "⚠️  Warning: Only ${free_space}GB free disk space"
        echo "   Recommended: 5-10 GB free"
        echo ""
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Installation cancelled"
            exit 1
        fi
    fi

    return 0
}

# Run system requirements check
check_system_requirements

# Check for Bash 4+ or ZSH (for associative arrays)
if [[ -n "$BASH_VERSION" ]]; then
    BASH_MAJOR="${BASH_VERSION%%.*}"
    if [[ "$BASH_MAJOR" -lt 4 ]]; then
        echo "Error: This script requires Bash 4+ or ZSH"
        echo "Your Bash version: $BASH_VERSION"
        echo ""
        echo "Please run with ZSH instead:"
        echo "  curl -fsSL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | zsh"
        exit 1
    fi
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RESET='\033[0m'
BOLD='\033[1m'
DIM='\033[2m'

# Installation directory
INSTALL_DIR="$HOME/.aichat"
CONFIG_DIR="$HOME/.aichat"

# ═══════════════════════════════════════════════════════════════════
# System Analysis Functions
# ═══════════════════════════════════════════════════════════════════

get_system_ram() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        echo $(($(sysctl -n hw.memsize) / 1024 / 1024 / 1024))
    elif [[ -f /proc/meminfo ]]; then
        # Linux
        echo $(($(grep MemTotal /proc/meminfo | awk '{print $2}') / 1024 / 1024))
    else
        echo "8"  # Default fallback
    fi
}

get_cpu_cores() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sysctl -n hw.ncpu
    else
        nproc 2>/dev/null || echo "4"
    fi
}

check_installed_models() {
    local models_found=()

    # Check Ollama models
    if command -v ollama &> /dev/null; then
        local ollama_models=$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}' || true)
        if [[ -n "$ollama_models" ]]; then
            while IFS= read -r model; do
                models_found+=("ollama:$model")
            done <<< "$ollama_models"
        fi
    fi

    # Check Python packages
    local python_packages=(
        "sentence-transformers:multilingual-e5-base"
        "spacy:spaCy NLP"
    )

    for pkg_check in "${python_packages[@]}"; do
        IFS=':' read -r pkg_name pkg_desc <<< "$pkg_check"
        if python3 -c "import ${pkg_name//-/_}" 2>/dev/null; then
            models_found+=("python:$pkg_desc")
        fi
    done

    # Check spaCy models
    if python3 -c "import spacy" 2>/dev/null; then
        local spacy_models=$(python3 -c "import spacy; print(' '.join(spacy.util.get_installed_models()))" 2>/dev/null || true)
        if [[ -n "$spacy_models" ]]; then
            for model in $spacy_models; do
                models_found+=("spacy:$model")
            done
        fi
    fi

    printf '%s\n' "${models_found[@]}"
}

# ═══════════════════════════════════════════════════════════════════
# Progress Bar Function
# ═══════════════════════════════════════════════════════════════════

show_progress() {
    local current=$1
    local total=$2
    local width=50
    local percentage=$((current * 100 / total))
    local completed=$((width * current / total))
    local remaining=$((width - completed))

    printf "\r  ["
    printf "%${completed}s" | tr ' ' '█'
    printf "%${remaining}s" | tr ' ' '░'
    printf "] %3d%%" "$percentage"
}

download_with_progress() {
    local url=$1
    local output=$2
    local desc=$3

    echo -n "  • $desc... "

    if command -v curl &> /dev/null; then
        curl -# -L "$url" -o "$output" 2>&1 | while IFS= read -r line; do
            if [[ $line =~ ([0-9]+\.[0-9]+)% ]]; then
                local pct=${BASH_REMATCH[1]%.*}
                show_progress "$pct" 100
            fi
        done
        echo -e " ${GREEN}✓${RESET}"
    else
        curl -sL "$url" -o "$output"
        echo -e "${GREEN}✓${RESET}"
    fi
}

# ═══════════════════════════════════════════════════════════════════
# Multilingual Support
# ═══════════════════════════════════════════════════════════════════

declare -A LANG_STRINGS

load_language() {
    local lang=$1

    case $lang in
        de)
            LANG_STRINGS[TITLE]="🤖 AI Chat Terminal Installation"
            LANG_STRINGS[SYSTEM_ANALYSIS]="Systemanalyse..."
            LANG_STRINGS[RAM_DETECTED]="Arbeitsspeicher erkannt"
            LANG_STRINGS[CPU_DETECTED]="CPU-Kerne erkannt"
            LANG_STRINGS[MODELS_FOUND]="Bereits installierte Modelle gefunden"
            LANG_STRINGS[NO_MODELS]="Keine Modelle gefunden - Neuinstallation"
            LANG_STRINGS[CHOOSE_INSTALL]="Wähle Installationsart"
            LANG_STRINGS[FRESH_INSTALL]="Neuinstallation (empfohlen für ersten Start)"
            LANG_STRINGS[UPDATE]="Update (behält Einstellungen)"
            LANG_STRINGS[CANCEL]="Abbrechen"
            LANG_STRINGS[DOWNLOADING]="Lade Dateien herunter..."
            LANG_STRINGS[MODEL_RECOMMENDATION]="Modell-Empfehlungen basierend auf deinem System"
            LANG_STRINGS[SMALL_MODELS]="Kleine Modelle (<100MB) werden automatisch installiert"
            LANG_STRINGS[LARGE_MODELS]="Große Modelle - Installation optional"
            LANG_STRINGS[RECOMMENDED]="Empfohlen"
            LANG_STRINGS[OPTIONAL]="Optional"
            LANG_STRINGS[SIZE]="Größe"
            LANG_STRINGS[INSTALL_QUESTION]="Installieren?"
            LANG_STRINGS[PRIVACY_TITLE]="Datenschutz-Konfiguration"
            LANG_STRINGS[PRIVACY_DESC]="Wie sollen sensible Daten behandelt werden?"
            LANG_STRINGS[PRIVACY_ENHANCED]="Erweitert - KI-basiert + Microsoft Presidio (empfohlen)"
            LANG_STRINGS[PRIVACY_BASIC]="Basis - Nur KI-basierte Erkennung"
            LANG_STRINGS[PRIVACY_OFF]="Aus - Kein Datenschutz (nicht empfohlen)"
            LANG_STRINGS[PRIVACY_WHY]="Warum erweitert? Presidio erkennt über 50 PII-Typen (Namen, E-Mails, Kreditkarten, etc.)"
            LANG_STRINGS[COMPLETE]="Installation abgeschlossen!"
            LANG_STRINGS[CONFIG_LATER]="Du kannst alle Einstellungen später mit '/config' ändern"
            ;;
        en)
            LANG_STRINGS[TITLE]="🤖 AI Chat Terminal Installation"
            LANG_STRINGS[SYSTEM_ANALYSIS]="System Analysis..."
            LANG_STRINGS[RAM_DETECTED]="RAM detected"
            LANG_STRINGS[CPU_DETECTED]="CPU cores detected"
            LANG_STRINGS[MODELS_FOUND]="Already installed models found"
            LANG_STRINGS[NO_MODELS]="No models found - fresh installation"
            LANG_STRINGS[CHOOSE_INSTALL]="Choose installation type"
            LANG_STRINGS[FRESH_INSTALL]="Fresh install (recommended for first use)"
            LANG_STRINGS[UPDATE]="Update (keeps settings)"
            LANG_STRINGS[CANCEL]="Cancel"
            LANG_STRINGS[DOWNLOADING]="Downloading files..."
            LANG_STRINGS[MODEL_RECOMMENDATION]="Model recommendations based on your system"
            LANG_STRINGS[SMALL_MODELS]="Small models (<100MB) will be installed automatically"
            LANG_STRINGS[LARGE_MODELS]="Large models - installation optional"
            LANG_STRINGS[RECOMMENDED]="Recommended"
            LANG_STRINGS[OPTIONAL]="Optional"
            LANG_STRINGS[SIZE]="Size"
            LANG_STRINGS[INSTALL_QUESTION]="Install?"
            LANG_STRINGS[PRIVACY_TITLE]="Privacy Configuration"
            LANG_STRINGS[PRIVACY_DESC]="How should sensitive data be handled?"
            LANG_STRINGS[PRIVACY_ENHANCED]="Enhanced - AI + Microsoft Presidio (recommended)"
            LANG_STRINGS[PRIVACY_BASIC]="Basic - AI-based detection only"
            LANG_STRINGS[PRIVACY_OFF]="Off - No privacy protection (not recommended)"
            LANG_STRINGS[PRIVACY_WHY]="Why enhanced? Presidio detects 50+ PII types (names, emails, credit cards, etc.)"
            LANG_STRINGS[COMPLETE]="Installation complete!"
            LANG_STRINGS[CONFIG_LATER]="You can change all settings later with '/config'"
            ;;
        es)
            LANG_STRINGS[TITLE]="🤖 Instalación AI Chat Terminal"
            LANG_STRINGS[SYSTEM_ANALYSIS]="Análisis del sistema..."
            LANG_STRINGS[RAM_DETECTED]="RAM detectada"
            LANG_STRINGS[CPU_DETECTED]="Núcleos CPU detectados"
            LANG_STRINGS[MODELS_FOUND]="Modelos ya instalados encontrados"
            LANG_STRINGS[NO_MODELS]="No se encontraron modelos - instalación nueva"
            LANG_STRINGS[CHOOSE_INSTALL]="Elige tipo de instalación"
            LANG_STRINGS[FRESH_INSTALL]="Instalación nueva (recomendado para primer uso)"
            LANG_STRINGS[UPDATE]="Actualizar (mantiene configuración)"
            LANG_STRINGS[CANCEL]="Cancelar"
            LANG_STRINGS[DOWNLOADING]="Descargando archivos..."
            LANG_STRINGS[MODEL_RECOMMENDATION]="Recomendaciones de modelos según tu sistema"
            LANG_STRINGS[SMALL_MODELS]="Modelos pequeños (<100MB) se instalarán automáticamente"
            LANG_STRINGS[LARGE_MODELS]="Modelos grandes - instalación opcional"
            LANG_STRINGS[RECOMMENDED]="Recomendado"
            LANG_STRINGS[OPTIONAL]="Opcional"
            LANG_STRINGS[SIZE]="Tamaño"
            LANG_STRINGS[INSTALL_QUESTION]="¿Instalar?"
            LANG_STRINGS[PRIVACY_TITLE]="Configuración de Privacidad"
            LANG_STRINGS[PRIVACY_DESC]="¿Cómo manejar datos sensibles?"
            LANG_STRINGS[PRIVACY_ENHANCED]="Mejorado - IA + Microsoft Presidio (recomendado)"
            LANG_STRINGS[PRIVACY_BASIC]="Básico - Solo detección con IA"
            LANG_STRINGS[PRIVACY_OFF]="Desactivado - Sin protección (no recomendado)"
            LANG_STRINGS[PRIVACY_WHY]="¿Por qué mejorado? Presidio detecta +50 tipos PII (nombres, emails, tarjetas, etc.)"
            LANG_STRINGS[COMPLETE]="¡Instalación completa!"
            LANG_STRINGS[CONFIG_LATER]="Puedes cambiar todo con '/config' más tarde"
            ;;
        *)
            # Default to English for all other languages (ar, da, fi, fr, hi, it, ja, ko, nl, no, pl, pt, ru, sv, tr, zh)
            # Chat will use proper translations from lang/*.conf files
            LANG_STRINGS[TITLE]="🤖 AI Chat Terminal Installation"
            LANG_STRINGS[SYSTEM_ANALYSIS]="System Analysis..."
            LANG_STRINGS[RAM_DETECTED]="RAM detected"
            LANG_STRINGS[CPU_DETECTED]="CPU cores detected"
            LANG_STRINGS[MODELS_FOUND]="Already installed models found"
            LANG_STRINGS[NO_MODELS]="No models found - fresh installation"
            LANG_STRINGS[CHOOSE_INSTALL]="Choose installation type"
            LANG_STRINGS[FRESH_INSTALL]="Fresh install (recommended for first use)"
            LANG_STRINGS[UPDATE]="Update (keeps settings)"
            LANG_STRINGS[CANCEL]="Cancel"
            LANG_STRINGS[DOWNLOADING]="Downloading files..."
            LANG_STRINGS[MODEL_RECOMMENDATION]="Model recommendations based on your system"
            LANG_STRINGS[SMALL_MODELS]="Small models (<100MB) will be installed automatically"
            LANG_STRINGS[LARGE_MODELS]="Large models - installation optional"
            LANG_STRINGS[RECOMMENDED]="Recommended"
            LANG_STRINGS[OPTIONAL]="Optional"
            LANG_STRINGS[SIZE]="Size"
            LANG_STRINGS[INSTALL_QUESTION]="Install?"
            LANG_STRINGS[PRIVACY_TITLE]="Privacy Configuration"
            LANG_STRINGS[PRIVACY_DESC]="How should sensitive data be handled?"
            LANG_STRINGS[PRIVACY_ENHANCED]="Enhanced - AI + Microsoft Presidio (recommended)"
            LANG_STRINGS[PRIVACY_BASIC]="Basic - AI-based detection only"
            LANG_STRINGS[PRIVACY_OFF]="Off - No privacy protection (not recommended)"
            LANG_STRINGS[PRIVACY_WHY]="Why enhanced? Presidio detects 50+ PII types (names, emails, credit cards, etc.)"
            LANG_STRINGS[COMPLETE]="Installation complete!"
            LANG_STRINGS[CONFIG_LATER]="You can change all settings later with '/config'"
            ;;
    esac
}

# ═══════════════════════════════════════════════════════════════════
# Main Installation Flow
# ═══════════════════════════════════════════════════════════════════

clear

# Step 1: Language Selection
echo -e "${CYAN}${BOLD}"
echo "╔═══════════════════════════════════════╗"
echo "║   🌍 Language / Sprache / Idioma     ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${RESET}\n"
echo "  [1]  🇦🇪 Arabic (العربية)"
echo "  [2]  🇩🇰 Danish (Dansk)"
echo "  [3]  🇩🇪 Deutsch (German)"
echo "  [4]  🇬🇧 English (default)"
echo "  [5]  🇪🇸 Español (Spanish)"
echo "  [6]  🇫🇮 Finnish (Suomi)"
echo "  [7]  🇫🇷 Français (French)"
echo "  [8]  🇮🇳 हिन्दी (Hindi)"
echo "  [9]  🇮🇹 Italiano (Italian)"
echo "  [10] 🇯🇵 日本語 (Japanese)"
echo "  [11] 🇰🇷 한국어 (Korean)"
echo "  [12] 🇳🇱 Nederlands (Dutch)"
echo "  [13] 🇳🇴 Norsk (Norwegian)"
echo "  [14] 🇵🇱 Polski (Polish)"
echo "  [15] 🇵🇹 Português (Portuguese)"
echo "  [16] 🇷🇺 Русский (Russian)"
echo "  [17] 🇸🇪 Svenska (Swedish)"
echo "  [18] 🇹🇷 Türkçe (Turkish)"
echo "  [19] 🇨🇳 中文 (Chinese)"
echo ""
echo -n "Select language [1-19, default=4]: "
read -r lang_choice < /dev/tty

case "$lang_choice" in
    1)  SELECTED_LANG="ar" ;;
    2)  SELECTED_LANG="da" ;;
    3)  SELECTED_LANG="de" ;;
    4)  SELECTED_LANG="en" ;;
    5)  SELECTED_LANG="es" ;;
    6)  SELECTED_LANG="fi" ;;
    7)  SELECTED_LANG="fr" ;;
    8)  SELECTED_LANG="hi" ;;
    9)  SELECTED_LANG="it" ;;
    10) SELECTED_LANG="ja" ;;
    11) SELECTED_LANG="ko" ;;
    12) SELECTED_LANG="nl" ;;
    13) SELECTED_LANG="no" ;;
    14) SELECTED_LANG="pl" ;;
    15) SELECTED_LANG="pt" ;;
    16) SELECTED_LANG="ru" ;;
    17) SELECTED_LANG="sv" ;;
    18) SELECTED_LANG="tr" ;;
    19) SELECTED_LANG="zh" ;;
    *)  SELECTED_LANG="en" ;;
esac

load_language "$SELECTED_LANG"

clear

# Step 2: System Analysis
echo -e "${CYAN}${BOLD}"
echo "╔═══════════════════════════════════════╗"
echo "║   ${LANG_STRINGS[TITLE]}"
echo "╚═══════════════════════════════════════╝"
echo -e "${RESET}\n"

echo -e "${BLUE}${LANG_STRINGS[SYSTEM_ANALYSIS]}${RESET}"

SYSTEM_RAM=$(get_system_ram)
SYSTEM_CORES=$(get_cpu_cores)
MACOS_VERSION=$(sw_vers -productVersion 2>/dev/null || echo "unknown")
FREE_SPACE=$(df -h ~ 2>/dev/null | awk 'NR==2 {print $4}' || echo "unknown")

echo -e "  ${GREEN}✓${RESET} macOS ${MACOS_VERSION}"
echo -e "  ${GREEN}✓${RESET} ${SYSTEM_CORES} CPU cores"
echo -e "  ${GREEN}✓${RESET} ${SYSTEM_RAM} GB RAM"
echo -e "  ${GREEN}✓${RESET} ${FREE_SPACE} free space"
echo -e "  ${GREEN}✓${RESET} ZSH available"

# Check for existing models (ZSH compatible)
echo -en "\n${BLUE}Checking installed AI models...${RESET} "
EXISTING_MODELS=()
while IFS= read -r line; do
    EXISTING_MODELS+=("$line")
done < <(check_installed_models)
echo -e "${GREEN}✓${RESET}"

if [ ${#EXISTING_MODELS[@]} -gt 0 ]; then
    echo -e "\n${GREEN}${LANG_STRINGS[MODELS_FOUND]}:${RESET}"
    for model in "${EXISTING_MODELS[@]}"; do
        IFS=':' read -r type name <<< "$model"
        echo -e "  ${DIM}•${RESET} ${name}"
    done
else
    echo -e "\n${YELLOW}${LANG_STRINGS[NO_MODELS]}${RESET}"
fi

# Step 3: Installation Type
if [[ -d "$INSTALL_DIR" ]] && [[ -f "$CONFIG_DIR/config" ]]; then
    echo -e "\n${YELLOW}${LANG_STRINGS[CHOOSE_INSTALL]}:${RESET}"
    echo "  [1] ${LANG_STRINGS[FRESH_INSTALL]}"
    echo "  [2] ${LANG_STRINGS[UPDATE]}"
    echo "  [3] ${LANG_STRINGS[CANCEL]}"
    echo ""
    echo -n "Select [1-3, default=2]: "
    read -r install_choice < /dev/tty

    case "$install_choice" in
        1)
            rm -rf "$INSTALL_DIR"
            rm -rf "$CONFIG_DIR"
            ;;
        3)
            exit 0
            ;;
    esac
fi

# Create directories
mkdir -p "$INSTALL_DIR/modules"
mkdir -p "$INSTALL_DIR/lang"
mkdir -p "$CONFIG_DIR"

# Step 4: Download Core Files
echo -e "\n${BLUE}${LANG_STRINGS[DOWNLOADING]}${RESET}"

BASE_URL="https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main"

# Download with simple progress
echo -n "  • Core files... "
curl -sL "$BASE_URL/aichat.zsh" -o "$INSTALL_DIR/aichat.zsh" && \
curl -sL "$BASE_URL/modules/functions.zsh" -o "$INSTALL_DIR/modules/functions.zsh" && \
curl -sL "$BASE_URL/modules/config-menu.zsh" -o "$INSTALL_DIR/modules/config-menu.zsh" && \
curl -sL "$BASE_URL/modules/language-utils.zsh" -o "$INSTALL_DIR/modules/language-utils.zsh" && \
curl -sL "$BASE_URL/memory_system.py" -o "$INSTALL_DIR/memory_system.py" && \
curl -sL "$BASE_URL/chat_system.py" -o "$INSTALL_DIR/chat_system.py" && \
curl -sL "$BASE_URL/local_storage_detector.py" -o "$INSTALL_DIR/local_storage_detector.py" && \
curl -sL "$BASE_URL/phi3_intent_parser.py" -o "$INSTALL_DIR/phi3_intent_parser.py" && \
curl -sL "$BASE_URL/response_generator.py" -o "$INSTALL_DIR/response_generator.py" && \
curl -sL "$BASE_URL/encryption_manager.py" -o "$INSTALL_DIR/encryption_manager.py" && \
curl -sL "$BASE_URL/db_migration.py" -o "$INSTALL_DIR/db_migration.py" && \
chmod +x "$INSTALL_DIR"/*.py && \
echo -e "${GREEN}✓${RESET}" || echo -e "${RED}✗${RESET}"

# Download v9.0.0 modules (db_actions, lang_manager)
mkdir -p "$INSTALL_DIR/db_actions"
mkdir -p "$INSTALL_DIR/lang_manager"

echo -n "  • DB action handlers... "
curl -sL "$BASE_URL/db_actions/__init__.py" -o "$INSTALL_DIR/db_actions/__init__.py" && \
curl -sL "$BASE_URL/db_actions/save_handler.py" -o "$INSTALL_DIR/db_actions/save_handler.py" && \
curl -sL "$BASE_URL/db_actions/retrieve_handler.py" -o "$INSTALL_DIR/db_actions/retrieve_handler.py" && \
curl -sL "$BASE_URL/db_actions/delete_handler.py" -o "$INSTALL_DIR/db_actions/delete_handler.py" && \
curl -sL "$BASE_URL/db_actions/list_handler.py" -o "$INSTALL_DIR/db_actions/list_handler.py" && \
curl -sL "$BASE_URL/db_actions/update_handler.py" -o "$INSTALL_DIR/db_actions/update_handler.py" && \
echo -e "${GREEN}✓${RESET}" || echo -e "${RED}✗${RESET}"

echo -n "  • Language manager... "
curl -sL "$BASE_URL/lang_manager/__init__.py" -o "$INSTALL_DIR/lang_manager/__init__.py" && \
echo -e "${GREEN}✓${RESET}" || echo -e "${RED}✗${RESET}"

# Download language files (all 19 languages from v9.0.0)
LANGUAGES=(en de de-schwaebisch de-bayerisch de-saechsisch fr it es pt nl pl ru ja zh ko ar hi tr sv da fi no ca)
echo -n "  • Language packs (19 languages)... "
for lang in "${LANGUAGES[@]}"; do
    curl -sL "$BASE_URL/lang/${lang}.conf" -o "$INSTALL_DIR/lang/${lang}.conf" 2>/dev/null || true
done
echo -e "${GREEN}✓${RESET}"

# Check Python and dependencies
if ! command -v python3 &> /dev/null; then
    echo -e "\n${YELLOW}Installing Python3...${RESET}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install python3
    elif command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y python3 python3-pip
    fi
fi

# Install OpenAI SDK
pip3 install --user --quiet openai requests 2>/dev/null || pip3 install --user openai requests

# ═══════════════════════════════════════════════════════════════════
# MANDATORY: Phi-3 Requirement Check (v9.0.0 KO Criterion)
# ═══════════════════════════════════════════════════════════════════

echo -e "\n${CYAN}${BOLD}⚡ AI Chat Terminal v9.0.0 - Phi-3 Smart Intent System${RESET}"
echo -e "${DIM}Phi-3 is MANDATORY for v9.0.0. No installation possible without it.${RESET}\n"

# Check if Ollama is installed
echo -n "  • Checking Ollama... "
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}not found${RESET}"
    echo -e "\n${YELLOW}❌ Ollama is required for Phi-3!${RESET}"
    echo ""
    echo "  Installing Ollama via Homebrew..."

    if ! command -v brew &> /dev/null; then
        echo -e "\n${RED}❌ INSTALLATION FAILED${RESET}"
        echo ""
        echo "  Homebrew not found. Please install:"
        echo "  1. Install Homebrew: https://brew.sh"
        echo "  2. Run: brew install ollama"
        echo "  3. Run this installer again"
        echo ""
        exit 1
    fi

    brew install ollama 2>&1 | grep -v "^=" || true

    if ! command -v ollama &> /dev/null; then
        echo -e "\n${RED}❌ INSTALLATION FAILED${RESET}"
        echo ""
        echo "  Ollama installation failed."
        echo "  Please install manually: https://ollama.ai/download"
        echo ""
        exit 1
    fi
    echo -e "  ${GREEN}✓${RESET} Ollama installed"
else
    echo -e "${GREEN}✓${RESET}"
fi

# Start Ollama service
echo -n "  • Starting Ollama service... "
if command -v brew &> /dev/null; then
    brew services start ollama &>/dev/null || true
fi

# Wait for Ollama HTTP server (port 11434) - max 30 seconds
wait_count=0
while ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1 && [ $wait_count -lt 30 ]; do
    sleep 1
    ((wait_count++))
done

if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo -e "${RED}✗${RESET}"
    echo -e "\n${RED}❌ INSTALLATION FAILED${RESET}"
    echo ""
    echo "  Ollama service not responding after 30 seconds."
    echo "  Please check Ollama installation and try again."
    echo ""
    exit 1
fi
echo -e "${GREEN}✓${RESET}"

# Check/Install Phi-3 model
echo -n "  • Checking Phi-3 model... "
if ollama list 2>/dev/null | grep -q "phi3"; then
    echo -e "${GREEN}✓ already installed${RESET}"
else
    echo -e "${YELLOW}not found${RESET}"
    echo ""
    echo "  📥 Downloading Phi-3 (2.3GB) - This is MANDATORY..."
    echo "     ${DIM}Phi-3 powers the v9.0.0 Smart Intent System${RESET}"
    echo ""

    # Run ollama pull with live output
    if ollama pull phi3; then
        echo -e "\n  ${GREEN}✓${RESET} Phi-3 downloaded successfully"
    else
        echo -e "\n${RED}❌ INSTALLATION FAILED${RESET}"
        echo ""
        echo "  Phi-3 download/installation failed."
        echo ""
        echo "  Possible reasons:"
        echo "  • Network connection issues"
        echo "  • Insufficient disk space (need ~2.3GB free)"
        echo "  • Ollama service issues"
        echo ""
        echo "  Please fix the issue and run installer again."
        exit 1
    fi
fi

# Skip inference test - it can hang on first model load
# chat_system.py will test Phi-3 when first starting
echo -e "  • Phi-3 model ready ${GREEN}✓${RESET}"

# Save Phi-3 status to config
echo "PHI3_ENABLED=true" >> "$INSTALL_DIR/config"
echo "RESPONSE_MODE=natural" >> "$INSTALL_DIR/config"

echo -e "\n${GREEN}✅ Phi-3 Smart Intent System ready!${RESET}\n"
sleep 2

# Step 5: Installation Locations Info
echo -e "\n${CYAN}${BOLD}${LANG_STRINGS[INSTALL_LOCATION_TITLE]:-📦 Installation Locations}${RESET}"
echo -e "${DIM}${LANG_STRINGS[INSTALL_LOCATION_LOCAL]:-Local (only this app):}${RESET}"
echo -e "  ${LANG_STRINGS[INSTALL_LOCATION_LOCAL_PATH]:-~/.aichat/ - Scripts, config, your data}"
echo -e "${DIM}${LANG_STRINGS[INSTALL_LOCATION_GLOBAL]:-Global (shared with other apps):}${RESET}"
echo -e "  ${LANG_STRINGS[INSTALL_LOCATION_GLOBAL_MODELS]:-AI models, Python packages}"
echo -e ""
echo -e "${GREEN}${LANG_STRINGS[INSTALL_LOCATION_BENEFIT]:-✨ Benefit: Global models can be used by other applications!}${RESET}"
echo -e "${YELLOW}${LANG_STRINGS[INSTALL_LOCATION_WARNING]:-⚠️  If you uninstall, global models remain for other apps}${RESET}"
echo ""
sleep 3

# Step 6: Database Encryption (v8.1.0)
echo -e "\n${BLUE}🔐 Database Encryption${RESET}"

# Check if SQLCipher is installed
echo -n "  • SQLCipher (AES-256)... "
if command -v sqlcipher &> /dev/null; then
    echo -e "${GREEN}✓${RESET}"
else
    echo -e "${YELLOW}installing...${RESET}"
    if command -v brew &> /dev/null; then
        brew install sqlcipher &> /dev/null && echo -e "    ${GREEN}✓ installed${RESET}" || echo -e "    ${RED}✗ failed${RESET}"
    else
        echo -e "    ${RED}✗ Homebrew not found${RESET}"
        echo -e "    ${YELLOW}Install manually: brew install sqlcipher${RESET}"
    fi
fi

# Install Python bindings for SQLCipher
echo -n "  • sqlcipher3-binary (Python)... "
pip3 install --user --quiet sqlcipher3-binary 2>/dev/null && echo -e "${GREEN}✓${RESET}" || echo -e "${YELLOW}⚠${RESET}"

# Step 7: AI Models - Small Models (Auto-Install)
echo -e "\n${BLUE}${LANG_STRINGS[SMALL_MODELS]}${RESET}"

echo -n "  • sentence-transformers (60MB)... "
pip3 install --user --quiet sentence-transformers 2>/dev/null && echo -e "${GREEN}✓${RESET}" || echo -e "${YELLOW}⚠${RESET}"

echo -n "  • sqlite-vec (5MB)... "
pip3 install --user --quiet sqlite-vec 2>/dev/null && echo -e "${GREEN}✓${RESET}" || echo -e "${YELLOW}⚠${RESET}"

# Step 6: Large Models - Interactive Choice
echo -e "\n${CYAN}${BOLD}${LANG_STRINGS[MODEL_RECOMMENDATION]}${RESET}"
echo -e "${DIM}${LANG_STRINGS[LARGE_MODELS]}${RESET}\n"

# Model recommendations based on RAM
declare -A MODEL_RECOMMENDATIONS

if [ $SYSTEM_RAM -ge 16 ]; then
    MODEL_RECOMMENDATIONS[presidio]="recommended"
    MODEL_RECOMMENDATIONS[spacy_multi]="recommended"
elif [ $SYSTEM_RAM -ge 8 ]; then
    MODEL_RECOMMENDATIONS[presidio]="recommended"
    MODEL_RECOMMENDATIONS[spacy_multi]="optional"
else
    MODEL_RECOMMENDATIONS[presidio]="optional"
    MODEL_RECOMMENDATIONS[spacy_multi]="skip"
fi

# Note: Phi-3 already installed as mandatory requirement above

# Step 7: Privacy Level Configuration (automatic based on installed components)
# Check if Presidio was installed and set privacy level accordingly
if grep -q "PRESIDIO_ENABLED=true" "$INSTALL_DIR/config" 2>/dev/null; then
    echo "PRIVACY_LEVEL=enhanced" >> "$INSTALL_DIR/config"
    echo -e "\n${GREEN}✓${RESET} Privacy: Enhanced (Presidio + AI Classifier)"
else
    echo "PRIVACY_LEVEL=basic" >> "$INSTALL_DIR/config"
    echo -e "\n${GREEN}✓${RESET} Privacy: Basic (AI Classifier only)"
fi

# Save language preference and other AI_CHAT_* settings
cat >> "$INSTALL_DIR/config" << EOF
AI_CHAT_LANGUAGE="$SELECTED_LANG"
AI_CHAT_COMMAND="chat"
AI_CHAT_MODEL="gpt-4o-mini"
AI_CHAT_ESC_EXIT="true"
AI_CHAT_CONTEXT_WINDOW="20"
OLLAMA_ALWAYS_ON="false"
EOF

# Step 8: Configure OpenAI API Key
echo -e "\n${CYAN}${BOLD}Konfiguriere OpenAI API Key...${RESET}"

# Try to load from macOS Keychain
OPENAI_KEY=$(security find-generic-password -s "OpenAI API" -a "openai" -w 2>/dev/null || echo "")

if [[ -n "$OPENAI_KEY" ]]; then
    echo "OPENAI_API_KEY=$OPENAI_KEY" > "$INSTALL_DIR/.env"
    chmod 600 "$INSTALL_DIR/.env"
    echo -e "  ${GREEN}✓${RESET} API Key aus Keychain geladen"
    echo -e "     ${DIM}Gespeichert in: ~/.aichat/.env${RESET}"
    # Show first/last 4 chars for verification
    local key_preview="${OPENAI_KEY:0:7}...${OPENAI_KEY: -4}"
    echo -e "     ${DIM}Key: $key_preview${RESET}"
else
    echo -e "  ${YELLOW}⚠${RESET} Kein API Key im Keychain gefunden"
    echo -e "     ${DIM}Beim ersten Start von 'chat' wirst du danach gefragt${RESET}"
    echo -e "     ${DIM}Oder speichere ihn im Keychain:${RESET}"
    echo -e "     ${DIM}security add-generic-password -a \"openai\" -s \"OpenAI API\" -w \"sk-...\"${RESET}"
fi

# Step 8: Migrate existing database to encrypted (v8.1.0)
if [ -f "$INSTALL_DIR/memory.db" ]; then
    echo -e "\n${BLUE}🔐 Database Migration${RESET}"
    echo -n "  • Migrating to encrypted database... "

    # Check if encryption available
    python3 -c "import sqlcipher3" 2>/dev/null
    if [ $? -eq 0 ]; then
        # Backup existing database
        cp "$INSTALL_DIR/memory.db" "$INSTALL_DIR/memory.db.pre-v8.1.backup" 2>/dev/null

        # Run migration
        python3 "$INSTALL_DIR/db_migration.py" migrate \
            "$INSTALL_DIR/memory.db.pre-v8.1.backup" \
            "$INSTALL_DIR/memory.db.encrypted" \
            "$(python3 -c 'from encryption_manager import EncryptionManager; m = EncryptionManager(); print(m.get_or_create_key())')" \
            2>/dev/null

        if [ $? -eq 0 ] && [ -f "$INSTALL_DIR/memory.db.encrypted" ]; then
            # Success - replace old DB with encrypted one
            mv "$INSTALL_DIR/memory.db.encrypted" "$INSTALL_DIR/memory.db"
            echo -e "${GREEN}✓${RESET}"
            echo -e "     ${DIM}Backup: memory.db.pre-v8.1.backup${RESET}"
        else
            # Migration failed - keep original
            rm -f "$INSTALL_DIR/memory.db.encrypted" 2>/dev/null
            echo -e "${YELLOW}⚠ keeping unencrypted${RESET}"
        fi
    else
        echo -e "${YELLOW}⚠ SQLCipher not available${RESET}"
    fi
fi

# Step 9: Initialize Models
echo -e "\n${BLUE}Initializing AI models...${RESET}"

echo -n "  • Downloading e5-base (278MB)... "
python3 -c "
import warnings, os
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('intfloat/multilingual-e5-base')
print('OK')
" 2>/dev/null | tail -1 | grep -q "OK" && echo -e "${GREEN}✓${RESET}" || echo -e "${YELLOW}⚠ First-use download${RESET}"

# Step 9: Shell Integration
echo -e "\n${BLUE}Setting up shell integration...${RESET}"

# Detect shell and update config
current_shell=$(basename "$SHELL" 2>/dev/null)
case "$current_shell" in
    zsh) primary_config="$HOME/.zshrc" ;;
    bash) primary_config="$HOME/.bashrc" ;;
    *) primary_config="$HOME/.zshrc" ;;
esac

# Clean old installations
grep -v "# AI Chat Terminal" "$primary_config" > "$primary_config.tmp" 2>/dev/null && mv "$primary_config.tmp" "$primary_config" || true
grep -v "source.*aichat.zsh" "$primary_config" > "$primary_config.tmp" 2>/dev/null && mv "$primary_config.tmp" "$primary_config" || true

# Add new configuration
echo "" >> "$primary_config"
echo "# AI Chat Terminal" >> "$primary_config"
echo "source $INSTALL_DIR/aichat.zsh" >> "$primary_config"
echo "alias chat='noglob ai_chat_function'" >> "$primary_config"

echo -e "  ${GREEN}✓${RESET} Updated $(basename "$primary_config")"

# Installation Complete
echo -e "\n${GREEN}${BOLD}${LANG_STRINGS[COMPLETE]}${RESET}\n"
echo -e "${CYAN}Next steps:${RESET}"
echo -e "  ${BOLD}source ~/$(basename "$primary_config")${RESET}  ${DIM}# or restart terminal${RESET}"
echo -e "  ${BOLD}chat${RESET}"
echo ""
echo -e "${DIM}${LANG_STRINGS[CONFIG_LATER]}${RESET}"