#!/bin/bash
# AI Chat Terminal - Smart Installer v5.1.0
# Enhanced onboarding with language-first approach

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RESET='\033[0m'
BOLD='\033[1m'

# Installation directory
INSTALL_DIR="$HOME/shell-scripts-new"
CONFIG_DIR="$HOME/.config/ai-chat"

# Clear screen for clean start
clear

echo -e "${CYAN}${BOLD}"
echo "╔═══════════════════════════════════════╗"
echo "║                                       ║"
echo "║    🤖 AI Chat Terminal Installer     ║"
echo "║          Version 5.1.0                ║"
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

# Create directories
echo -e "${BLUE}Setting up directories...${RESET}"
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/languages"
mkdir -p "$CONFIG_DIR"

# Download files from GitHub
echo -e "${BLUE}Downloading files...${RESET}"

# Base URL
BASE_URL="https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main"

# Download main files
echo -n "  • chat.zsh... "
curl -sL "$BASE_URL/chat.zsh" -o "$INSTALL_DIR/chat.zsh"
echo -e "${GREEN}✓${RESET}"

echo -n "  • chat-functions.zsh... "
curl -sL "$BASE_URL/chat-functions.zsh" -o "$INSTALL_DIR/chat-functions.zsh"
echo -e "${GREEN}✓${RESET}"

echo -n "  • config-menu.zsh... "
curl -sL "$BASE_URL/config-menu.zsh" -o "$INSTALL_DIR/config-menu.zsh"
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
    curl -sL "$BASE_URL/languages/${lang}.conf" -o "$INSTALL_DIR/languages/${lang}.conf" 2>/dev/null || true
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

# Install shell-gpt if not installed
if ! command -v sgpt &> /dev/null; then
    echo -e "${YELLOW}  Installing shell-gpt...${RESET}"
    pip3 install --user shell-gpt
    echo -e "${GREEN}  ✓ shell-gpt installed${RESET}"
else
    echo -e "${GREEN}  ✓ shell-gpt already installed${RESET}"
fi

# Install jq if not installed (for JSON parsing)
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}  Installing jq...${RESET}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install jq
    elif command -v apt-get &> /dev/null; then
        sudo apt-get install -y jq
    fi
fi

# First-time setup
if [[ ! -f "$CONFIG_DIR/.env" ]]; then
    echo -e "\n${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo -e "${CYAN}${BOLD}        🚀 First-Time Setup${RESET}"
    echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}\n"

    # Step 1: Language Selection (FIRST!)
    echo -e "${YELLOW}Step 1/6: Select Your Language${RESET}"
    echo "────────────────────────────────────"
    echo ""
    echo "  [1] 🇬🇧 English (default)"
    echo "  [2] 🇩🇪 Deutsch"
    echo "  [3] 🇫🇷 Français"
    echo "  [4] 🇮🇹 Italiano"
    echo "  [5] 🇪🇸 Español"
    echo "  [6] 🇨🇳 中文 (Mandarin)"
    echo "  [7] 🇮🇳 हिन्दी (Hindi)"
    echo ""
    echo -n "Select [1-7] (default: 1): "
    read -r LANG_CHOICE

    LANGUAGE="en"
    case "$LANG_CHOICE" in
        2)
            echo -e "\n${YELLOW}Möchten Sie einen Dialekt?${RESET}"
            echo "  [1] Hochdeutsch (Standard)"
            echo "  [2] Schwäbisch"
            echo "  [3] Bayerisch"
            echo "  [4] Sächsisch"
            echo -n "Auswahl [1-4]: "
            read -r DIALECT
            case "$DIALECT" in
                2) LANGUAGE="de-schwaebisch" ;;
                3) LANGUAGE="de-bayerisch" ;;
                4) LANGUAGE="de-saechsisch" ;;
                *) LANGUAGE="de" ;;
            esac
            ;;
        3) LANGUAGE="fr" ;;
        4) LANGUAGE="it" ;;
        5)
            echo -e "\n${YELLOW}¿Qué variante prefieres?${RESET}"
            echo "  [1] 🇪🇸 Español (Estándar)"
            echo "  [2] 🇲🇽 Mexicano"
            echo "  [3] 🇦🇷 Argentino"
            echo "  [4] 🇨🇴 Colombiano"
            echo "  [5] 🇻🇪 Venezolano"
            echo "  [6] 🇨🇱 Chileno"
            echo "  [7] 🇪🇸 Andaluz"
            echo "  [8] Català"
            echo "  [9] Euskera"
            echo "  [10] Galego"
            echo -n "Selección [1-10]: "
            read -r VARIANT
            case "$VARIANT" in
                2) LANGUAGE="es-mexicano" ;;
                3) LANGUAGE="es-argentino" ;;
                4) LANGUAGE="es-colombiano" ;;
                5) LANGUAGE="es-venezolano" ;;
                6) LANGUAGE="es-chileno" ;;
                7) LANGUAGE="es-andaluz" ;;
                8) LANGUAGE="ca" ;;
                9) LANGUAGE="eu" ;;
                10) LANGUAGE="gl" ;;
                *) LANGUAGE="es" ;;
            esac
            ;;
        6) LANGUAGE="zh" ;;
        7) LANGUAGE="hi" ;;
        *) LANGUAGE="en" ;;
    esac
    echo -e "${GREEN}✓ Language: $LANGUAGE${RESET}\n"

    # Load language strings for the rest of the installer
    # (We'll use English as fallback for installer messages, but could enhance this)

    # Step 2: OpenAI API Key
    echo -e "${YELLOW}Step 2/6: OpenAI API Key${RESET} ${RED}(Required)${RESET}"
    echo "────────────────────────────────────"
    echo ""
    echo -e "${CYAN}ℹ️  About OpenAI API:${RESET}"
    echo "• ${GREEN}Pay-per-use${RESET} - No monthly subscription!"
    echo "• Start with just ${YELLOW}\$5-10 credit${RESET}"
    echo "• Average cost: ${GREEN}\$0.01-0.10 per conversation${RESET}"
    echo "• One-time \$5 credit lasts weeks for casual use"
    echo ""
    echo -e "${BOLD}How to get your API key:${RESET}"
    echo "1. Create account at: ${CYAN}https://platform.openai.com${RESET}"
    echo "2. Add \$5-10 credit to your account"
    echo "3. Generate API key at: ${CYAN}https://platform.openai.com/api-keys${RESET}"
    echo ""

    OPENAI_KEY=""
    while [[ -z "$OPENAI_KEY" ]]; do
        echo -n "Enter your OpenAI API key: "
        read -r OPENAI_KEY
        if [[ -z "$OPENAI_KEY" ]]; then
            echo -e "${RED}⚠ OpenAI API key is required for the app to work!${RESET}"
        fi
    done
    echo -e "${GREEN}✓ OpenAI API configured${RESET}\n"

    # Step 3: Perplexity API Key
    echo -e "${YELLOW}Step 3/6: Perplexity API Key${RESET} ${GREEN}(Optional - For Web Search)${RESET}"
    echo "────────────────────────────────────"
    echo ""
    echo -e "${CYAN}ℹ️  About Perplexity API:${RESET}"
    echo "• ${GREEN}FREE tier available!${RESET} Limited requests/month"
    echo "• Pro tier: ${YELLOW}\$5/month${RESET} for more requests"
    echo "• Enables: Current news, weather, stock prices, sports scores"
    echo ""
    echo -e "${BOLD}Benefits of adding Perplexity:${RESET}"
    echo "✨ Real-time information (news, weather, stocks)"
    echo "✨ Current events and recent discoveries"
    echo "✨ Live sports scores and statistics"
    echo ""
    echo "Get your key at: ${CYAN}https://www.perplexity.ai/settings/api${RESET}"
    echo ""
    echo -n "Enter Perplexity key (or press Enter to skip): "
    read -r PERPLEXITY_KEY

    if [[ ! -z "$PERPLEXITY_KEY" ]]; then
        echo -e "${GREEN}✓ Web search enabled!${RESET}\n"
    else
        echo -e "${YELLOW}⊘ Web search skipped (can add later via /config)${RESET}\n"
    fi

    # Step 4: OpenAI Model Selection
    echo -e "${YELLOW}Step 4/6: Select Default OpenAI Model${RESET}"
    echo "────────────────────────────────────"
    echo ""
    echo "  [1] gpt-4o-mini   - ${GREEN}Fast & cheap${RESET} (\$0.15/1M tokens)"
    echo "  [2] gpt-4o       ${GREEN}⭐ RECOMMENDED${RESET} - Best performance (\$2.50/1M tokens)"
    echo "  [3] gpt-4        - Classic powerful model (\$30/1M tokens)"
    echo "  [4] gpt-4-turbo  - Fast, good quality (\$10/1M tokens)"
    echo "  [5] gpt-3.5-turbo - Basic, very cheap (\$0.50/1M tokens)"
    echo ""
    echo -e "${CYAN}Tip: Start with gpt-4o for best experience${RESET}"
    echo -n "Select [1-5] (default: 2): "
    read -r MODEL_CHOICE

    case "$MODEL_CHOICE" in
        1) OPENAI_MODEL="gpt-4o-mini" ;;
        3) OPENAI_MODEL="gpt-4" ;;
        4) OPENAI_MODEL="gpt-4-turbo" ;;
        5) OPENAI_MODEL="gpt-3.5-turbo" ;;
        *) OPENAI_MODEL="gpt-4o" ;;
    esac
    echo -e "${GREEN}✓ Model selected: $OPENAI_MODEL${RESET}\n"

    # Step 5: Perplexity Model (if API key provided)
    PERPLEXITY_MODEL="pplx-7b-online"
    if [[ ! -z "$PERPLEXITY_KEY" ]]; then
        echo -e "${YELLOW}Step 5/6: Select Default Perplexity Model${RESET}"
        echo "────────────────────────────────────"
        echo ""
        echo "  [1] pplx-7b-online  ${GREEN}⭐ RECOMMENDED${RESET} - Fast, efficient"
        echo "  [2] pplx-70b-online - More powerful, slower"
        echo "  [3] sonar-small-online - Ultra-fast"
        echo "  [4] sonar-medium-online - Balanced"
        echo ""
        echo -n "Select [1-4] (default: 1): "
        read -r PPLX_CHOICE

        case "$PPLX_CHOICE" in
            2) PERPLEXITY_MODEL="pplx-70b-online" ;;
            3) PERPLEXITY_MODEL="sonar-small-online" ;;
            4) PERPLEXITY_MODEL="sonar-medium-online" ;;
            *) PERPLEXITY_MODEL="pplx-7b-online" ;;
        esac
        echo -e "${GREEN}✓ Perplexity model: $PERPLEXITY_MODEL${RESET}\n"

        # Adjust step numbering
        FINAL_STEP="6/6"
    else
        FINAL_STEP="5/6"
    fi

    # Step 6: Command Selection
    echo -e "${YELLOW}Step ${FINAL_STEP}: Choose Command to Start AI Chat${RESET}"
    echo "────────────────────────────────────"
    echo "This is the command you'll type to start chatting."
    echo ""
    echo "  [1] ai   ${GREEN}⭐ RECOMMENDED${RESET} - Clear and memorable"
    echo "  [2] ask  - Natural for questions"
    echo "  [3] q    - Quick single letter"
    echo "  [4] ??   - Double question mark"
    echo "  [5] chat - Descriptive"
    echo "  [6] Custom - Choose your own"
    echo ""
    echo -n "Select [1-6] (default: 1): "
    read -r CMD_CHOICE

    case "$CMD_CHOICE" in
        2) COMMAND="ask" ;;
        3) COMMAND="q" ;;
        4) COMMAND="??" ;;
        5) COMMAND="chat" ;;
        6)
            echo -n "Enter custom command: "
            read -r COMMAND
            ;;
        *) COMMAND="ai" ;;
    esac
    echo -e "${GREEN}✓ Command set: $COMMAND${RESET}\n"

    # Create .env file
    cat > "$CONFIG_DIR/.env" << EOF
# AI Chat Terminal Configuration
# Generated: $(date)

# API Keys
OPENAI_API_KEY="$OPENAI_KEY"
PERPLEXITY_API_KEY="$PERPLEXITY_KEY"

# Default Models
DEFAULT_OPENAI_MODEL="$OPENAI_MODEL"
DEFAULT_PERPLEXITY_MODEL="$PERPLEXITY_MODEL"
EOF

    chmod 600 "$CONFIG_DIR/.env"

    # Create config file (with improved timeout)
    cat > "$CONFIG_DIR/config" << EOF
# AI Chat Terminal User Configuration
AI_CHAT_COMMAND="$COMMAND"
AI_CHAT_LANGUAGE="$LANGUAGE"
AI_CHAT_TIMEOUT="600"
AI_CHAT_ESC_EXIT="true"
EOF

    # Configure sgpt
    mkdir -p ~/.config/shell_gpt
    cat > ~/.config/shell_gpt/.sgptrc << EOF
DEFAULT_MODEL=$OPENAI_MODEL
OPENAI_API_KEY=$OPENAI_KEY
CHAT_CACHE_LENGTH=20
CHAT_CACHE_PATH=/tmp/chat_cache
REQUEST_TIMEOUT=60
DEFAULT_COLOR=green
EOF

fi

# Update shell configuration
echo -e "\n${BLUE}Updating shell configuration...${RESET}"

SHELL_CONFIGS=("$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.profile")
COMMAND="${COMMAND:-ai}"

for CONFIG in "${SHELL_CONFIGS[@]}"; do
    if [[ -f "$CONFIG" ]]; then
        # Remove old entries
        grep -v "source.*shell-scripts" "$CONFIG" > "$CONFIG.tmp" && mv "$CONFIG.tmp" "$CONFIG" 2>/dev/null || true
        grep -v "alias.*ai_chat_function" "$CONFIG" > "$CONFIG.tmp" && mv "$CONFIG.tmp" "$CONFIG" 2>/dev/null || true

        # Add new entry
        echo "" >> "$CONFIG"
        echo "# AI Chat Terminal" >> "$CONFIG"
        echo "source $INSTALL_DIR/chat.zsh" >> "$CONFIG"
        echo "alias $COMMAND='ai_chat_function'" >> "$CONFIG"

        echo -e "  ${GREEN}✓${RESET} Updated $(basename $CONFIG)"
    fi
done

# Success message
clear
echo -e "${GREEN}${BOLD}"
echo "╔═══════════════════════════════════════╗"
echo "║                                       ║"
echo "║      ✅ Installation Complete!        ║"
echo "║                                       ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${RESET}\n"

echo -e "${CYAN}Available Features:${RESET}"
echo "  ✓ AI chat with ${OPENAI_MODEL:-gpt-4o}"
if [[ ! -z "$PERPLEXITY_KEY" ]]; then
    echo "  ✓ Web search enabled (Perplexity)"
fi
echo "  ✓ Session memory (10 minutes)"
echo "  ✓ 19 language variants"
echo "  ✓ Configuration menu (/config)"
echo ""

echo -e "${YELLOW}Try these commands:${RESET}"
echo "  $COMMAND Hello!"
echo "  $COMMAND What's the weather?"
echo "  $COMMAND /config"
echo ""

echo -e "${BOLD}Next step:${RESET}"
echo "  Restart your terminal or run:"
echo -e "  ${CYAN}source ~/.zshrc${RESET}"
echo ""

echo "Enjoy your AI Chat Terminal! 🚀"