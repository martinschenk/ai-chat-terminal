#!/bin/bash
# AI Chat Terminal - Smart Universal Installer
# Works with .zshrc, .bashrc, and .profile

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RESET='\033[0m'

echo -e "${CYAN}"
echo "     ___   ____    _____ _           _   "
echo "    / _ \\ |_ _|   / ____| |         | |  "
echo "   / /_\\ \\ | |   | |    | |__   __ _| |_ "
echo "   |  _  | | |   | |    | '_ \\ / _\` | __|"
echo "   | | | |_| |_  | |____| | | | (_| | |_ "
echo "   \\_| |_/\\___/  \\_____|_| |_|\\__,_|\\__|"
echo -e "${RESET}"
echo -e "${CYAN}        Instant AI Chat Terminal${RESET}"
echo -e "${CYAN}          One-Line Installation${RESET}"
echo ""

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
else
    echo -e "${RED}❌ Unsupported OS: $OSTYPE${RESET}"
    echo "This tool requires macOS or Linux"
    exit 1
fi

echo -e "${GREEN}✅ Detected: $OS${RESET}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 required${RESET}"
    echo "Install: https://www.python.org/downloads/"
    exit 1
fi

# Install shell-gpt if needed
if ! command -v sgpt &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Shell GPT...${RESET}"
    pip3 install --user shell-gpt || pip install --user shell-gpt || {
        echo -e "${RED}Failed to install. Try: pip3 install shell-gpt${RESET}"
        exit 1
    }
fi

# Setup directories
INSTALL_DIR="$HOME/ai-chat-terminal"
CONFIG_DIR="$HOME/.config/ai-chat"

echo -e "${CYAN}Setting up AI Chat...${RESET}"
mkdir -p "$INSTALL_DIR/languages"
mkdir -p "$CONFIG_DIR"

# Download files from GitHub
BASE_URL="https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main"

echo "Downloading files..."
curl -sSL "$BASE_URL/chat.zsh" -o "$INSTALL_DIR/chat.zsh" 2>/dev/null || \
    wget -q "$BASE_URL/chat.zsh" -O "$INSTALL_DIR/chat.zsh"

# Download language files
curl -sSL "$BASE_URL/languages/en.conf" -o "$INSTALL_DIR/languages/en.conf" 2>/dev/null || \
    wget -q "$BASE_URL/languages/en.conf" -O "$INSTALL_DIR/languages/en.conf"

curl -sSL "$BASE_URL/languages/de.conf" -o "$INSTALL_DIR/languages/de.conf" 2>/dev/null || \
    wget -q "$BASE_URL/languages/de.conf" -O "$INSTALL_DIR/languages/de.conf"

# Quick configuration
echo ""
echo -e "${CYAN}⚙️  Quick Setup${RESET}"
echo -e "${CYAN}═══════════════${RESET}"

# Command character
echo -ne "Command character [${GREEN}q${RESET}]: "
read -r cmd_char
cmd_char=${cmd_char:-q}

# Language
echo -e "\nLanguages: ${GREEN}en${RESET}=English, ${GREEN}de${RESET}=German"
echo -ne "Select language [${GREEN}en${RESET}]: "
read -r language
language=${language:-en}

# ESC key
echo -ne "\nEnable ESC key to exit? [${GREEN}Y${RESET}/n]: "
read -r esc_key
if [[ "$esc_key" =~ ^[Nn]$ ]]; then
    esc_exit="false"
else
    esc_exit="true"
fi

# Save configuration
cat > "$CONFIG_DIR/config" << EOF
AI_CHAT_COMMAND="$cmd_char"
AI_CHAT_LANGUAGE="$language"
AI_CHAT_TIMEOUT="120"
AI_CHAT_ESC_EXIT="$esc_exit"
EOF

# Detect shell config file
SHELL_CONFIG=""
SHELL_NAME=""

# Priority order: .zshrc > .bashrc > .profile
if [[ -f "$HOME/.zshrc" ]] || [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_CONFIG="$HOME/.zshrc"
    SHELL_NAME="zsh"
elif [[ -f "$HOME/.bashrc" ]] || [[ "$SHELL" == *"bash"* ]]; then
    SHELL_CONFIG="$HOME/.bashrc"
    SHELL_NAME="bash"
else
    SHELL_CONFIG="$HOME/.profile"
    SHELL_NAME="sh"
fi

echo -e "${GREEN}✅ Using: $SHELL_CONFIG${RESET}"

# Remove old aliases if they exist
sed -i.bak '/# AI Chat Terminal/d' "$SHELL_CONFIG" 2>/dev/null || true
sed -i.bak '/ai_chat_function/d' "$SHELL_CONFIG" 2>/dev/null || true
sed -i.bak '/alias.*ai_chat_function/d' "$SHELL_CONFIG" 2>/dev/null || true
sed -i.bak "/alias $cmd_char=/d" "$SHELL_CONFIG" 2>/dev/null || true
sed -i.bak "/alias q=/d" "$SHELL_CONFIG" 2>/dev/null || true
sed -i.bak "/alias f=/d" "$SHELL_CONFIG" 2>/dev/null || true

# Add new configuration
echo "" >> "$SHELL_CONFIG"
echo "# AI Chat Terminal" >> "$SHELL_CONFIG"
echo "source $INSTALL_DIR/chat.zsh" >> "$SHELL_CONFIG"

# Add appropriate alias based on shell
if [[ "$SHELL_NAME" == "zsh" ]]; then
    echo "alias $cmd_char='noglob ai_chat_function'" >> "$SHELL_CONFIG"
else
    echo "alias $cmd_char='ai_chat_function'" >> "$SHELL_CONFIG"
fi

# Configure Shell GPT
mkdir -p ~/.config/shell_gpt
if [[ ! -f ~/.config/shell_gpt/.sgptrc ]]; then
    cat > ~/.config/shell_gpt/.sgptrc << 'EOF'
CHAT_CACHE_PATH=/tmp/chat_cache
CACHE_PATH=/tmp/cache
CHAT_CACHE_LENGTH=100
REQUEST_TIMEOUT=60
DEFAULT_MODEL=gpt-4o-mini
DEFAULT_COLOR=magenta
EOF
fi

# API Key check
echo ""
if [[ -z "$OPENAI_API_KEY" ]]; then
    echo -e "${YELLOW}⚠️  OpenAI API Key needed${RESET}"
    echo "Get one at: https://platform.openai.com/api-keys"
    echo ""
    echo -ne "Enter API key (or Enter to skip): "
    read -r api_key

    if [[ ! -z "$api_key" ]]; then
        echo "" >> "$SHELL_CONFIG"
        echo "export OPENAI_API_KEY=\"$api_key\"" >> "$SHELL_CONFIG"
        echo -e "${GREEN}✅ API key saved${RESET}"
    else
        echo -e "${YELLOW}Add to $SHELL_CONFIG later:${RESET}"
        echo "export OPENAI_API_KEY=\"your-key\""
    fi
else
    echo -e "${GREEN}✅ API key found${RESET}"
fi

# Success!
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════╗${RESET}"
echo -e "${GREEN}║     🎉 Installation Complete! 🎉      ║${RESET}"
echo -e "${GREEN}╚═══════════════════════════════════════╝${RESET}"
echo ""
echo -e "To start using:"
echo -e "  1. Reload shell: ${CYAN}source $SHELL_CONFIG${RESET}"
echo -e "  2. Start chat:   ${CYAN}$cmd_char${RESET}"
echo -e "  3. Quick query:  ${CYAN}$cmd_char What is 2+2?${RESET}"
echo ""
echo -e "In chat: ${YELLOW}/config${RESET} for settings"
echo ""