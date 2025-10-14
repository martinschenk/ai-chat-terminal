#!/usr/bin/env zsh
# AI Chat Terminal - Uninstaller
# Licensed under MIT License - https://opensource.org/licenses/MIT

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RESET='\033[0m'
BOLD='\033[1m'
DIM='\033[2m'

INSTALL_DIR="$HOME/.aichat"

clear

echo -e "${CYAN}${BOLD}"
echo "╔═══════════════════════════════════════╗"
echo "║   🗑️  AI Chat Terminal Uninstaller   ║"
echo "╚═══════════════════════════════════════╝"
echo -e "${RESET}\n"

# Check if installed
if [[ ! -d "$INSTALL_DIR" ]]; then
    echo -e "${YELLOW}AI Chat Terminal is not installed.${RESET}"
    echo ""
    echo "Nothing to uninstall."
    exit 0
fi

# Show what will be removed
echo -e "${BLUE}What will be removed:${RESET}"
echo -e "  ${GREEN}✓${RESET} Local app files: ~/.aichat/"
echo -e "  ${GREEN}✓${RESET} Shell integration (from ~/.zshrc or ~/.bashrc)"
echo -e "  ${GREEN}✓${RESET} 'chat' command"
echo ""

echo -e "${YELLOW}What will NOT be removed (shared components):${RESET}"
echo -e "  ${DIM}•${RESET} Ollama (may be used by other apps)"
echo -e "  ${DIM}•${RESET} Qwen 2.5 Coder model (~4.5GB)"
echo -e "  ${DIM}•${RESET} Python packages (openai, requests, rich, sqlcipher3-binary)"
echo -e "  ${DIM}•${RESET} SQLCipher"
echo ""

# Backup warning
if [[ -f "$INSTALL_DIR/memory.db" ]]; then
    echo -e "${RED}${BOLD}⚠️  WARNING: Your local database will be deleted!${RESET}"
    echo ""
    echo -e "${CYAN}Database contains:${RESET}"

    # Try to count entries
    if command -v sqlite3 &> /dev/null || command -v sqlcipher &> /dev/null; then
        # Try to get count (works for both encrypted and unencrypted)
        COUNT=$(sqlite3 "$INSTALL_DIR/memory.db" "SELECT COUNT(*) FROM mydata;" 2>/dev/null || \
                sqlcipher "$INSTALL_DIR/memory.db" "SELECT COUNT(*) FROM mydata;" 2>/dev/null || \
                echo "unknown")

        if [[ "$COUNT" != "unknown" ]]; then
            echo -e "  ${BOLD}$COUNT${RESET} stored items"
        else
            echo -e "  ${DIM}(encrypted - cannot read without key)${RESET}"
        fi
    fi

    echo ""
    echo -e "${CYAN}Creating automatic backup...${RESET}"
    BACKUP_FILE="$HOME/ai-chat-backup-$(date +%Y%m%d-%H%M%S).db"
    cp "$INSTALL_DIR/memory.db" "$BACKUP_FILE"
    echo -e "  ${GREEN}✓${RESET} Backup saved: $BACKUP_FILE"
    echo ""
fi

# Confirm uninstall
echo -e "${YELLOW}${BOLD}Continue with uninstall?${RESET}"
echo -e "${DIM}Press [Y] to continue, [N] to cancel (default: Y)${RESET}"
echo -n "Your choice [Y/n]: "
read -r confirmation < /dev/tty

# Default to Y if empty
confirmation=${confirmation:-y}

if [[ ! "$confirmation" =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${CYAN}Uninstall cancelled.${RESET}"
    exit 0
fi

echo ""
echo -e "${BLUE}Uninstalling AI Chat Terminal...${RESET}"

# Step 1: Remove local files
echo -n "  • Removing ~/.aichat/... "
rm -rf "$INSTALL_DIR"
echo -e "${GREEN}✓${RESET}"

# Step 2: Remove shell integration
current_shell=$(basename "$SHELL" 2>/dev/null)
case "$current_shell" in
    zsh) primary_config="$HOME/.zshrc" ;;
    bash) primary_config="$HOME/.bashrc" ;;
    *) primary_config="$HOME/.zshrc" ;;
esac

echo -n "  • Removing from $(basename "$primary_config")... "

# Remove AI Chat Terminal lines
if [[ -f "$primary_config" ]]; then
    # Create temp file without AI Chat Terminal entries
    grep -v "# AI Chat Terminal" "$primary_config" | \
    grep -v "source.*aichat.zsh" | \
    grep -v "alias chat=" > "$primary_config.tmp"

    mv "$primary_config.tmp" "$primary_config"
    echo -e "${GREEN}✓${RESET}"
else
    echo -e "${YELLOW}⚠${RESET}"
fi

# Step 3: Stop any running daemons
echo -n "  • Stopping background processes... "
pkill -f "chat_daemon.py" 2>/dev/null || true
echo -e "${GREEN}✓${RESET}"

echo ""
echo -e "${GREEN}${BOLD}✅ AI Chat Terminal uninstalled successfully!${RESET}"
echo ""

if [[ -f "$BACKUP_FILE" ]]; then
    echo -e "${CYAN}Your data backup:${RESET}"
    echo -e "  📦 $BACKUP_FILE"
    echo ""
fi

echo -e "${CYAN}Global components still installed:${RESET}"
echo -e "  • Ollama: $(which ollama 2>/dev/null || echo 'not found')"
echo -e "  • Qwen model: ~/.ollama/models/"
echo -e "  • Python packages: openai, requests, rich, sqlcipher3-binary"
echo -e "  • SQLCipher: $(which sqlcipher 2>/dev/null || echo 'not found')"
echo ""

echo -e "${DIM}To remove global components (optional):${RESET}"
echo -e "${DIM}  brew uninstall ollama sqlcipher${RESET}"
echo -e "${DIM}  rm -rf ~/.ollama${RESET}"
echo -e "${DIM}  pip3 uninstall openai requests rich sqlcipher3-binary${RESET}"
echo ""

echo -e "${CYAN}Reload your shell:${RESET}"
echo -e "  ${BOLD}source ~/$(basename "$primary_config")${RESET}  ${DIM}# or restart terminal${RESET}"
echo ""
