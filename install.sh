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

# Installation directory (following Unix standards like .vim, .zsh)
INSTALL_DIR="$HOME/.aichat"
CONFIG_DIR="$HOME/.aichat"

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

# Skip interactive setup - will be handled by first run of 'ai' command
echo -e "${BLUE}Setting up shell integration...${RESET}"

# Create basic config structure for shell integration
update_shell_config() {
    local command_name="${1:-ai}"

    # Shell configuration files to update
    local shell_configs=("$HOME/.zshrc" "$HOME/.bashrc")

    for config_file in "${shell_configs[@]}"; do
        if [[ -f "$config_file" ]]; then
            # Remove any existing AI Chat Terminal entries
            grep -v "# AI Chat Terminal" "$config_file" > "$config_file.tmp" && mv "$config_file.tmp" "$config_file"
            grep -v "source.*aichat.zsh" "$config_file" > "$config_file.tmp" && mv "$config_file.tmp" "$config_file"
            grep -v "alias.*ai.*ai_chat_function" "$config_file" > "$config_file.tmp" && mv "$config_file.tmp" "$config_file"

            # Add new configuration
            echo "" >> "$config_file"
            echo "# AI Chat Terminal" >> "$config_file"
            echo "source $INSTALL_DIR/aichat.zsh" >> "$config_file"
            echo "alias $command_name='ai_chat_function'" >> "$config_file"

            echo -e "  ${GREEN}✓${RESET} Updated $config_file"
        fi
    done
}

# Setup shell integration with default 'ai' command
update_shell_config "ai"

# Installation complete message
echo -e "\n${CYAN}${BOLD}╔═══════════════════════════════════════╗${RESET}"
echo -e "${CYAN}${BOLD}║                                       ║${RESET}"
echo -e "${CYAN}${BOLD}║      ✅ Installation Complete!        ║${RESET}"
echo -e "${CYAN}${BOLD}║                                       ║${RESET}"
echo -e "${CYAN}${BOLD}╚═══════════════════════════════════════╝${RESET}\n"
echo -e "${CYAN}What's installed:${RESET}"
echo "  ✓ AI Chat Terminal files"
echo "  ✓ Shell integration (ai command)"
echo "  ✓ 19 language support"
echo "  ✓ Configuration system"
echo ""

echo -e "${BOLD}${YELLOW}⚡ Next Step: Configure your AI Chat Terminal${RESET}"
echo ""
echo -e "Run this command to start the interactive setup:"
echo -e "  ${GREEN}ai${RESET}"
echo ""
echo "The setup will guide you through:"
echo "• Language selection"
echo "• OpenAI API key configuration"
echo "• Optional Perplexity API key (for web search)"
echo "• AI model selection"
echo ""
echo -e "${CYAN}Tip: You can also run ${BOLD}ai setup${RESET}${CYAN} anytime to reconfigure${RESET}"
echo ""
echo "Restart your terminal first:"
echo -e "  ${CYAN}source ~/.zshrc${RESET}"