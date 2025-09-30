#!/bin/bash
# AI Chat Terminal - Smart Installer v5.4.0
# Licensed under MIT License - https://opensource.org/licenses/MIT
# Native OpenAI API integration without shell-gpt dependency

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RESET='\033[0m'
BOLD='\033[1m'

# Installation directory (following Unix standards like .vim, .zsh)
INSTALL_DIR="$HOME/.aichat"
CONFIG_DIR="$HOME/.aichat"

# Clear screen for clean start
clear

echo -e "${CYAN}${BOLD}"
echo "╔═══════════════════════════════════════╗"
echo "║                                       ║"
echo "║    🤖 AI Chat Terminal Installer     ║"
echo "║          Version 5.4.0                ║"
echo "║                                       ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${RESET}\n"

# Check if already installed
if [[ -d "$INSTALL_DIR" ]] && [[ -f "$CONFIG_DIR/config" ]]; then
    echo -e "${YELLOW}AI Chat Terminal is already installed.${RESET}"
    echo ""
    echo "Options:"
    echo "  [1] Reinstall (keeps your settings)"
    echo "  [2] Fresh install (removes everything)"
    echo "  [3] Cancel"
    echo ""
    echo -n "Select [1-3]: "
    read -r install_choice

    case "$install_choice" in
        2)
            echo "Removing old installation..."
            rm -rf "$INSTALL_DIR"
            rm -rf "$CONFIG_DIR"
            ;;
        3)
            echo "Installation cancelled."
            exit 0
            ;;
    esac
fi

# Create directories with proper structure
echo -e "${BLUE}Setting up directories...${RESET}"
mkdir -p "$INSTALL_DIR/modules"
mkdir -p "$INSTALL_DIR/lang"
mkdir -p "$CONFIG_DIR"

# Download files from GitHub
echo -e "${BLUE}Downloading files...${RESET}"

# Base URL
BASE_URL="https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main"

# Download main files
echo -n "  • Main script... "
curl -sL "$BASE_URL/aichat.zsh" -o "$INSTALL_DIR/aichat.zsh"
echo -e "${GREEN}✓${RESET}"

echo -n "  • Functions module... "
curl -sL "$BASE_URL/modules/functions.zsh" -o "$INSTALL_DIR/modules/functions.zsh"
echo -e "${GREEN}✓${RESET}"

echo -n "  • Config menu module... "
curl -sL "$BASE_URL/modules/config-menu.zsh" -o "$INSTALL_DIR/modules/config-menu.zsh"
echo -e "${GREEN}✓${RESET}"

echo -n "  • Chat & Memory system... "
curl -sL "$BASE_URL/memory_system.py" -o "$INSTALL_DIR/memory_system.py"
chmod +x "$INSTALL_DIR/memory_system.py"
curl -sL "$BASE_URL/chat_system.py" -o "$INSTALL_DIR/chat_system.py"
chmod +x "$INSTALL_DIR/chat_system.py"
echo -e "${GREEN}✓${RESET}"

# Download language files
LANGUAGES=(
    "en" "de" "de-schwaebisch" "de-bayerisch" "de-saechsisch"
    "fr" "it" "es" "es-mexicano" "es-argentino" "es-colombiano"
    "es-venezolano" "es-chileno" "es-andaluz" "ca" "eu" "gl"
    "zh" "hi"
)

echo -n "  • Language packs... "
for lang in "${LANGUAGES[@]}"; do
    curl -sL "$BASE_URL/lang/${lang}.conf" -o "$INSTALL_DIR/lang/${lang}.conf" 2>/dev/null || true
done
echo -e "${GREEN}✓${RESET}"

# Check for dependencies
echo -e "\n${BLUE}Checking dependencies...${RESET}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}  ⚠ Python3 not found. Installing...${RESET}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install python3
    elif command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y python3 python3-pip
    fi
fi

# Install OpenAI Python SDK and requests
pip3 install --user openai requests &>/dev/null || {
    echo -e "${YELLOW}  Installing OpenAI SDK...${RESET}"
    pip3 install --user openai requests
}
echo -e "${GREEN}  ✓ OpenAI SDK ready${RESET}"

# Install jq if not installed (for JSON parsing)
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}  Installing jq...${RESET}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install jq
    elif command -v apt-get &> /dev/null; then
        sudo apt-get install -y jq
    fi
fi

# Install enhanced memory system with PII protection
echo -e "\n${BLUE}Installing Enhanced Privacy Protection...${RESET}"

# Core memory system
echo -n "  • Enhanced Memory System (e5-base)... "
pip3 install --user sentence-transformers sqlite-vec &>/dev/null && echo -e "${GREEN}✓${RESET}" || echo -e "${YELLOW}⚠ Install manually with: pip3 install sentence-transformers sqlite-vec${RESET}"

# PII Detection with Presidio
echo -n "  • PII Detection (Presidio)... "
pip3 install --user presidio-analyzer presidio-anonymizer &>/dev/null && echo -e "${GREEN}✓${RESET}" || {
    echo -e "${YELLOW}⚠${RESET}"
    echo "    Manual install required: pip3 install presidio-analyzer presidio-anonymizer"
}

# spaCy language models for PII detection
echo -n "  • Language models (EN/DE)... "
python3 -m spacy download en_core_web_sm &>/dev/null 2>&1 && \
python3 -m spacy download de_core_news_sm &>/dev/null 2>&1 && \
echo -e "${GREEN}✓${RESET}" || echo -e "${YELLOW}⚠ Run manually: python3 -m spacy download en_core_web_sm${RESET}"

# Optional additional languages
echo -e "\n${CYAN}Additional Language Support for PII Detection:${RESET}"
echo "${BOLD}European Languages:${RESET}"
echo "  [1] Spanish (es_core_news_sm)"
echo "  [2] French (fr_core_news_sm)"
echo "  [3] Italian (it_core_news_sm)"
echo "  [4] Portuguese (pt_core_news_sm)"
echo "  [5] Dutch (nl_core_news_sm)"
echo "  [6] Polish (pl_core_news_sm)"
echo "  [7] Danish (da_core_news_sm)"
echo "  [8] Swedish (sv_core_news_sm)"
echo "  [9] Norwegian (nb_core_news_sm)"
echo "  [10] Finnish (fi_core_news_sm)"
echo "  [11] Russian (ru_core_news_sm)"
echo "  [12] Catalan (ca_core_news_sm)"

echo "${BOLD}Asian Languages:${RESET}"
echo "  [13] Chinese (zh_core_web_sm)"
echo "  [14] Japanese (ja_core_news_sm)"
echo "  [15] Korean (ko_core_news_sm)"

echo ""
echo "  [0] Skip additional languages"
echo ""
echo -n "Install languages (comma-separated, e.g., 1,3,13 or 'all' for all): "
read -r extra_langs

# Function to install a language model
install_lang_model() {
    local lang_name=$1
    local model_name=$2
    echo -n "  • Installing ${lang_name}... "
    python3 -m spacy download ${model_name} &>/dev/null && echo -e "${GREEN}✓${RESET}" || echo -e "${YELLOW}⚠${RESET}"
}

if [[ "$extra_langs" == "all" ]]; then
    # Install all available models
    install_lang_model "Spanish" "es_core_news_sm"
    install_lang_model "French" "fr_core_news_sm"
    install_lang_model "Italian" "it_core_news_sm"
    install_lang_model "Portuguese" "pt_core_news_sm"
    install_lang_model "Dutch" "nl_core_news_sm"
    install_lang_model "Polish" "pl_core_news_sm"
    install_lang_model "Danish" "da_core_news_sm"
    install_lang_model "Swedish" "sv_core_news_sm"
    install_lang_model "Norwegian" "nb_core_news_sm"
    install_lang_model "Finnish" "fi_core_news_sm"
    install_lang_model "Russian" "ru_core_news_sm"
    install_lang_model "Catalan" "ca_core_news_sm"
    install_lang_model "Chinese" "zh_core_web_sm"
    install_lang_model "Japanese" "ja_core_news_sm"
    install_lang_model "Korean" "ko_core_news_sm"
elif [[ -n "$extra_langs" && "$extra_langs" != "0" ]]; then
    IFS=',' read -ra LANG_ARRAY <<< "$extra_langs"
    for lang_num in "${LANG_ARRAY[@]}"; do
        case ${lang_num// /} in
            1) install_lang_model "Spanish" "es_core_news_sm" ;;
            2) install_lang_model "French" "fr_core_news_sm" ;;
            3) install_lang_model "Italian" "it_core_news_sm" ;;
            4) install_lang_model "Portuguese" "pt_core_news_sm" ;;
            5) install_lang_model "Dutch" "nl_core_news_sm" ;;
            6) install_lang_model "Polish" "pl_core_news_sm" ;;
            7) install_lang_model "Danish" "da_core_news_sm" ;;
            8) install_lang_model "Swedish" "sv_core_news_sm" ;;
            9) install_lang_model "Norwegian" "nb_core_news_sm" ;;
            10) install_lang_model "Finnish" "fi_core_news_sm" ;;
            11) install_lang_model "Russian" "ru_core_news_sm" ;;
            12) install_lang_model "Catalan" "ca_core_news_sm" ;;
            13) install_lang_model "Chinese" "zh_core_web_sm" ;;
            14) install_lang_model "Japanese" "ja_core_news_sm" ;;
            15) install_lang_model "Korean" "ko_core_news_sm" ;;
        esac
    done
fi

# Optional Phi-3 for natural responses
echo -e "\n${YELLOW}═══════════════════════════════════════${RESET}"
echo -e "${BOLD}Enhanced Response Generation (Optional)${RESET}"
echo -e "${YELLOW}═══════════════════════════════════════${RESET}"
echo ""
echo "Phi-3 enables natural language responses for your private data."
echo "Without it, the system uses templates (works great, less natural)."
echo -e "${DIM}• Download size: ~2GB${RESET}"
echo -e "${DIM}• Installs globally via Ollama (can be used for other projects)${RESET}"
echo -e "${DIM}• Optional - system works perfectly without it${RESET}"
echo ""
echo -n "Install Phi-3 for enhanced responses? [y/N]: "
read -r install_phi3

if [[ "$install_phi3" =~ ^[Yy]$ ]]; then
    # Check if Ollama is installed
    if ! command -v ollama &> /dev/null; then
        echo "Installing Ollama (AI model manager)..."
        curl -fsSL https://ollama.ai/install.sh | sh
        echo -e "${GREEN}✓ Ollama installed${RESET}"
    else
        echo -e "${GREEN}✓ Ollama already installed${RESET}"
    fi

    echo "Downloading Phi-3 model (this may take a few minutes)..."
    ollama pull phi3 && {
        echo -e "${GREEN}✓ Phi-3 ready for natural response generation${RESET}"
        echo "PHI3_ENABLED=true" >> "$INSTALL_DIR/config"
        echo "RESPONSE_MODE=natural" >> "$INSTALL_DIR/config"
    } || {
        echo -e "${YELLOW}⚠ Phi-3 installation failed - templates will be used${RESET}"
        echo "PHI3_ENABLED=false" >> "$INSTALL_DIR/config"
        echo "RESPONSE_MODE=template" >> "$INSTALL_DIR/config"
    }
else
    echo "PHI3_ENABLED=false" >> "$INSTALL_DIR/config"
    echo "RESPONSE_MODE=template" >> "$INSTALL_DIR/config"
    echo -e "${BLUE}Using template-based responses (lightweight, works excellent!)${RESET}"
fi

# Privacy protection level configuration
echo -e "\n${CYAN}Privacy Protection Configuration:${RESET}"
echo "  [1] Enhanced (recommended) - Presidio + Semantic classification"
echo "  [2] Basic - Semantic classification only"
echo "  [3] Disabled - No privacy protection (not recommended)"
echo ""
echo -n "Select privacy level [1-3, default=1]: "
read -r privacy_level

case "$privacy_level" in
    2)
        echo "PRIVACY_LEVEL=basic" >> "$INSTALL_DIR/config"
        echo "PRESIDIO_ENABLED=false" >> "$INSTALL_DIR/config"
        echo -e "${YELLOW}Basic privacy protection enabled (semantic only)${RESET}"
        ;;
    3)
        echo "PRIVACY_LEVEL=off" >> "$INSTALL_DIR/config"
        echo "PRESIDIO_ENABLED=false" >> "$INSTALL_DIR/config"
        echo -e "${YELLOW}⚠ Privacy protection disabled${RESET}"
        ;;
    *)
        echo "PRIVACY_LEVEL=enhanced" >> "$INSTALL_DIR/config"
        echo "PRESIDIO_ENABLED=true" >> "$INSTALL_DIR/config"
        echo -e "${GREEN}✓ Enhanced privacy protection enabled${RESET}"
        ;;
esac

# Initialize AI models (download and training)
echo -e "\n${BLUE}Initializing AI Models...${RESET}"

# Download multilingual-e5-base model
echo -n "  • Downloading e5-base model (278MB)... "
python3 -c "
import warnings
import os
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'
try:
    from sentence_transformers import SentenceTransformer
    print('Downloading multilingual-e5-base...', flush=True)
    model = SentenceTransformer('intfloat/multilingual-e5-base')
    print('OK')
except Exception as e:
    print('SKIP')
" 2>/dev/null | tail -1 | grep -q "OK" && echo -e "${GREEN}✓${RESET}" || echo -e "${YELLOW}⚠ Will download on first use${RESET}"

# Train privacy classifier
echo -n "  • Training privacy classifier... "
python3 -c "
import sys
import warnings
import os
# Suppress all warnings and output
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'
sys.path.insert(0, '$INSTALL_DIR')
try:
    from privacy_classifier_fast import FastPrivacyClassifier
    classifier = FastPrivacyClassifier()
    classifier.train_fast()
    print('OK')
except Exception as e:
    print('SKIP')
" 2>/dev/null | grep -q "OK" && echo -e "${GREEN}✓${RESET}" || echo -e "${YELLOW}⚠ Will train on first start${RESET}"

# Test PII detection if available
echo -n "  • Testing PII detection... "
python3 -c "
import sys
import warnings
import os
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'
sys.path.insert(0, '$INSTALL_DIR')
try:
    from pii_detector import PIIDetector
    detector = PIIDetector()
    has_pii, types, details = detector.check_for_pii('test@example.com')
    if has_pii:
        print('OK')
    else:
        print('PARTIAL')
except Exception as e:
    print('SKIP')
" 2>/dev/null | grep -q "OK" && echo -e "${GREEN}✓${RESET}" || echo -e "${YELLOW}⚠ Will initialize on first use${RESET}"

# Skip interactive setup - will be handled by first run of 'ai' command
echo -e "${BLUE}Setting up shell integration...${RESET}"

# Professional shell configuration (writes only to primary shell config)
update_shell_config() {
    local command_name="${1:-ai}"

    # Detect current shell
    local current_shell=$(basename "$SHELL" 2>/dev/null)
    local primary_config=""
    local cleanup_configs=()

    # Determine primary config file
    case "$current_shell" in
        zsh)
            primary_config="$HOME/.zshrc"
            cleanup_configs=("$HOME/.bashrc" "$HOME/.profile")
            ;;
        bash)
            primary_config="$HOME/.bashrc"
            cleanup_configs=("$HOME/.zshrc" "$HOME/.profile")
            ;;
        fish)
            primary_config="$HOME/.config/fish/config.fish"
            cleanup_configs=("$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.profile")
            ;;
        *)
            # Fallback: prefer .zshrc if exists, otherwise .bashrc
            if [[ -f "$HOME/.zshrc" ]]; then
                primary_config="$HOME/.zshrc"
            elif [[ -f "$HOME/.bashrc" ]]; then
                primary_config="$HOME/.bashrc"
            else
                primary_config="$HOME/.profile"
            fi
            cleanup_configs=("$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.profile")
            ;;
    esac

    # Clean up from all config files (remove old installations)
    for config_file in "${cleanup_configs[@]}" "$primary_config"; do
        if [[ -f "$config_file" ]]; then
            grep -v "# AI Chat Terminal" "$config_file" > "$config_file.tmp" && mv "$config_file.tmp" "$config_file"
            grep -v "source.*aichat.zsh" "$config_file" > "$config_file.tmp" && mv "$config_file.tmp" "$config_file"
            grep -v "alias.*ai_chat_function" "$config_file" > "$config_file.tmp" && mv "$config_file.tmp" "$config_file"
        fi
    done

    # Install only to primary config
    if [[ ! -z "$primary_config" ]]; then
        # Create config file if it doesn't exist
        touch "$primary_config"

        # Add new configuration to primary config only
        echo "" >> "$primary_config"
        echo "# AI Chat Terminal" >> "$primary_config"
        echo "source $INSTALL_DIR/aichat.zsh" >> "$primary_config"
        echo "alias $command_name='noglob ai_chat_function'" >> "$primary_config"

        echo -e "  ${GREEN}✓${RESET} Updated $(basename "$primary_config")"
        PRIMARY_SHELL_CONFIG="$primary_config"
    fi
}

# Setup shell integration with default 'chat' command
update_shell_config "chat"

# Installation complete message with professional output
echo -e "\n${GREEN}✅ Installation Complete!${RESET}\n"
echo "Next steps:"

# Show only the primary shell config that was updated
if [[ ! -z "$PRIMARY_SHELL_CONFIG" ]]; then
    config_name=$(basename "$PRIMARY_SHELL_CONFIG")
    echo -e "  ${CYAN}source ~/$config_name${RESET}  ${DIM}# or restart terminal${RESET}"
else
    echo -e "  ${CYAN}Restart your terminal${RESET}"
fi

echo -e "  ${CYAN}chat${RESET}"