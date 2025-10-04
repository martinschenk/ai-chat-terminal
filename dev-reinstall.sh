#!/usr/bin/env bash
# AI Chat Terminal - Developer Reinstallation Script
# Syncs all files from dev directory to ~/.aichat with DB backup & rotation
# Usage: ./dev-reinstall.sh [-y]  (use -y to keep config without asking)

set -e

# Parse args
AUTO_YES=false
if [[ "$1" == "-y" ]]; then
    AUTO_YES=true
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

# Paths
DEV_DIR="$HOME/Development/ai-chat-terminal"
INSTALL_DIR="$HOME/.aichat"
BACKUP_DIR="$INSTALL_DIR/backups"
DAEMON_PORT=5555

clear
echo -e "${CYAN}${BOLD}╔═══════════════════════════════════════════╗${RESET}"
echo -e "${CYAN}${BOLD}║  🔧 AI Chat - Dev Reinstallation        ║${RESET}"
echo -e "${CYAN}${BOLD}╚═══════════════════════════════════════════╝${RESET}\n"

# Step 1: Stop Daemon
echo -e "${BLUE}1. Daemon Management${RESET}"
echo -n "  • Checking daemon on port $DAEMON_PORT... "
if lsof -ti:$DAEMON_PORT >/dev/null 2>&1; then
    DAEMON_PID=$(lsof -ti:$DAEMON_PORT)
    echo -e "${YELLOW}running (PID: $DAEMON_PID)${RESET}"

    echo -n "  • Stopping daemon... "
    kill $DAEMON_PID 2>/dev/null || true
    sleep 1

    if lsof -ti:$DAEMON_PORT >/dev/null 2>&1; then
        echo -e "${RED}✗ Failed to stop${RESET}"
        echo -e "\n  ${RED}Please stop manually:${RESET} kill -9 $DAEMON_PID"
        exit 1
    fi
    echo -e "${GREEN}✓${RESET}"
else
    echo -e "${DIM}not running${RESET}"
fi

# Step 2: Database Backup & Rotation
echo -e "\n${BLUE}2. Database Backup${RESET}"

if [[ -f "$INSTALL_DIR/memory.db" ]]; then
    # Create backup directory
    mkdir -p "$BACKUP_DIR"

    # Create timestamped backup
    TIMESTAMP=$(date +%Y-%m-%d-%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/memory-$TIMESTAMP.db"

    echo -n "  • Creating backup... "
    cp "$INSTALL_DIR/memory.db" "$BACKUP_FILE"
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | awk '{print $1}')
    echo -e "${GREEN}✓${RESET} ($BACKUP_SIZE)"
    echo -e "    ${DIM}$BACKUP_FILE${RESET}"

    # Backup rotation - keep only 10 newest
    echo -n "  • Rotating backups (keep 10 newest)... "
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/memory-*.db 2>/dev/null | wc -l | tr -d ' ')

    if [[ $BACKUP_COUNT -gt 10 ]]; then
        # Delete oldest backups
        ls -1t "$BACKUP_DIR"/memory-*.db | tail -n +11 | xargs rm -f
        DELETED=$((BACKUP_COUNT - 10))
        echo -e "${GREEN}✓${RESET} (${DELETED} old backups removed)"
    else
        echo -e "${GREEN}✓${RESET} (${BACKUP_COUNT} total)"
    fi
else
    echo -e "  ${DIM}• No database found${RESET}"
fi

# Step 3: Config Handling
echo -e "\n${BLUE}3. Configuration${RESET}"

OVERWRITE_CONFIG=false
if [[ -f "$INSTALL_DIR/config" ]]; then
    if [[ "$AUTO_YES" == "true" ]]; then
        echo -e "  ${GREEN}→ Keeping existing config (-y flag)${RESET}"
    else
        echo -e "  ${YELLOW}⚠${RESET}  Existing config found"
        echo -n "  Overwrite config? [y/N, default=N]: "

        read -r config_choice

        if [[ "$config_choice" =~ ^[Yy]$ ]]; then
            OVERWRITE_CONFIG=true
            echo -e "    ${YELLOW}→ Will overwrite config${RESET}"
        else
            echo -e "    ${GREEN}→ Will keep existing config${RESET}"
        fi
    fi
else
    OVERWRITE_CONFIG=true
    echo -e "  ${DIM}• No config found - will copy from dev${RESET}"
fi

# Step 4: Sync Files
echo -e "\n${BLUE}4. Syncing Files${RESET}"

# Python core files
echo -n "  • Python core files... "
for file in chat_system.py memory_system.py chat_daemon.py daemon_manager.py \
            ollama_manager.py local_storage_detector.py phi3_intent_parser.py \
            response_generator.py encryption_manager.py db_migration.py; do
    if [[ -f "$DEV_DIR/$file" ]]; then
        cp "$DEV_DIR/$file" "$INSTALL_DIR/"
    fi
done
echo -e "${GREEN}✓${RESET}"

# Shell files
echo -n "  • Shell scripts... "
for file in aichat.zsh; do
    if [[ -f "$DEV_DIR/$file" ]]; then
        cp "$DEV_DIR/$file" "$INSTALL_DIR/"
    fi
done
echo -e "${GREEN}✓${RESET}"

# Modules
echo -n "  • Modules... "
if [[ -d "$DEV_DIR/modules" ]]; then
    mkdir -p "$INSTALL_DIR/modules"
    cp -r "$DEV_DIR/modules/"* "$INSTALL_DIR/modules/" 2>/dev/null || true
fi
echo -e "${GREEN}✓${RESET}"

# DB Actions
echo -n "  • DB action handlers... "
if [[ -d "$DEV_DIR/db_actions" ]]; then
    mkdir -p "$INSTALL_DIR/db_actions"
    cp -r "$DEV_DIR/db_actions/"* "$INSTALL_DIR/db_actions/" 2>/dev/null || true
fi
echo -e "${GREEN}✓${RESET}"

# Lang Manager
echo -n "  • Language manager... "
if [[ -d "$DEV_DIR/lang_manager" ]]; then
    mkdir -p "$INSTALL_DIR/lang_manager"
    cp -r "$DEV_DIR/lang_manager/"* "$INSTALL_DIR/lang_manager/" 2>/dev/null || true
fi
echo -e "${GREEN}✓${RESET}"

# Language files
echo -n "  • Language files... "
if [[ -d "$DEV_DIR/lang" ]]; then
    mkdir -p "$INSTALL_DIR/lang"
    cp -r "$DEV_DIR/lang/"* "$INSTALL_DIR/lang/" 2>/dev/null || true
fi
echo -e "${GREEN}✓${RESET}"

# Config (conditional)
if [[ "$OVERWRITE_CONFIG" == "true" ]] && [[ -f "$DEV_DIR/config" ]]; then
    echo -n "  • Config... "
    cp "$DEV_DIR/config" "$INSTALL_DIR/"
    echo -e "${GREEN}✓ overwritten${RESET}"
fi

# Make scripts executable
chmod +x "$INSTALL_DIR"/*.py 2>/dev/null || true

# Step 5: Start Daemon
echo -e "\n${BLUE}5. Starting Daemon${RESET}"
echo -n "  • Starting daemon on port $DAEMON_PORT... "

cd "$INSTALL_DIR"
nohup python3 chat_daemon.py > /tmp/daemon.log 2>&1 &
sleep 2

if lsof -ti:$DAEMON_PORT >/dev/null 2>&1; then
    NEW_PID=$(lsof -ti:$DAEMON_PORT)
    echo -e "${GREEN}✓${RESET} (PID: $NEW_PID)"
else
    echo -e "${RED}✗${RESET}"
    echo -e "\n  ${RED}Failed to start daemon!${RESET}"
    echo -e "  Check logs: tail -20 /tmp/daemon.log"
    exit 1
fi

# Complete!
echo -e "\n${GREEN}${BOLD}✅ Dev Reinstallation Complete!${RESET}\n"

# Show summary
echo -e "${CYAN}📊 Summary:${RESET}"
echo -e "  • DB Backups: ${BACKUP_COUNT}/10 (in ~/.aichat/backups/)"
echo -e "  • Config: $(if [[ "$OVERWRITE_CONFIG" == "true" ]]; then echo "Overwritten"; else echo "Kept existing"; fi)"
echo -e "  • Daemon: Running on port $DAEMON_PORT"
echo ""

# Test commands
echo -e "${CYAN}🧪 Test Commands:${RESET}"
echo -e "  ${BOLD}chat speichere lokal: test@example.com${RESET}"
echo -e "    ${DIM}→ Should show varied Phi-3: \"💾 Hab's gemerkt!\"${RESET}"
echo ""
echo -e "  ${BOLD}chat was hab ich gespeichert?${RESET}"
echo -e "    ${DIM}→ Should show playful: \"🔍 Rausgekramt: test@example.com\"${RESET}"
echo ""
echo -e "  ${BOLD}chat lösche test${RESET}"
echo -e "    ${DIM}→ Should show correct count: \"🗑️ Weg damit! (1x)\"${RESET}"
echo ""

echo -e "${DIM}Logs: tail -f /tmp/daemon.log${RESET}"
echo ""
