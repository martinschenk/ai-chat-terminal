#!/bin/zsh
# AI Chat Terminal - Configuration Menu
# Part 3 - Config and Uninstall functions

# Configuration menu function
show_config_menu() {
    while true; do
        local CONFIG_DIR="$HOME/.aichat"
        local CONFIG_FILE="$CONFIG_DIR/config"
        local ENV_FILE="$CONFIG_DIR/.env"

        # Load environment
        load_env

        # Load config
        if [[ -f "$CONFIG_FILE" ]]; then
            source "$CONFIG_FILE"
        fi

        local COMMAND_CHAR="${AI_CHAT_COMMAND:-ai}"
        local LANGUAGE="${AI_CHAT_LANGUAGE:-en}"
        local TIMEOUT="${AI_CHAT_TIMEOUT:-600}"
        local ENABLE_ESC="${AI_CHAT_ESC_EXIT:-true}"
        # Use global SCRIPT_DIR from main script

        # Load language file for config menu
        local LANG_FILE="$SCRIPT_DIR/lang/${LANGUAGE}.conf"
        if [[ ! -f "$LANG_FILE" ]]; then
            setup_default_language
        else
            source "$LANG_FILE"
        fi

        # Colors
        local CYAN='\033[0;36m'
        local GREEN='\033[0;32m'
        local YELLOW='\033[1;33m'
        local PURPLE='\033[0;35m'
        local RED='\033[0;31m'
        local RESET='\033[0m'
        local BOLD='\033[1m'

        clear
        echo -e "${BOLD}${CYAN}⚙️  ${LANG_CONFIG_TITLE}${RESET}\n"

        echo -e "${PURPLE}╔═══════════════════════════════════════╗${RESET}"
        echo -e "${PURPLE}║${RESET}  ${LANG_CONFIG_CURRENT}                ${PURPLE}║${RESET}"
        echo -e "${PURPLE}║${RESET}  ├─ ${LANG_CONFIG_COMMAND}: ${YELLOW}$COMMAND_CHAR${RESET}                  ${PURPLE}║${RESET}"
        echo -e "${PURPLE}║${RESET}  ├─ ${LANG_CONFIG_LANGUAGE}: ${YELLOW}$LANGUAGE${RESET}                 ${PURPLE}║${RESET}"
        echo -e "${PURPLE}║${RESET}  ├─ ${LANG_CONFIG_TIMEOUT}: ${YELLOW}${TIMEOUT}s${RESET}               ${PURPLE}║${RESET}"
        echo -e "${PURPLE}║${RESET}  └─ ${LANG_CONFIG_ESC}: ${YELLOW}$ENABLE_ESC${RESET}          ${PURPLE}║${RESET}"
        echo -e "${PURPLE}╠═══════════════════════════════════════╣${RESET}"
        echo -e "${PURPLE}║${RESET}  ${GREEN}[1]${RESET} ${LANG_CONFIG_OPT1}           ${PURPLE}║${RESET}"
        echo -e "${PURPLE}║${RESET}  ${GREEN}[2]${RESET} ${LANG_CONFIG_OPT2}                  ${PURPLE}║${RESET}"
        echo -e "${PURPLE}║${RESET}  ${GREEN}[3]${RESET} ${LANG_CONFIG_OPT3}                  ${PURPLE}║${RESET}"
        echo -e "${PURPLE}║${RESET}  ${GREEN}[4]${RESET} ${LANG_CONFIG_OPT4}            ${PURPLE}║${RESET}"
        echo -e "${PURPLE}║${RESET}  ${GREEN}[5]${RESET} ${LANG_CONFIG_OPT5}                 ${PURPLE}║${RESET}"
        echo -e "${PURPLE}║${RESET}  ${GREEN}[6]${RESET} 🧹 ${LANG_CONFIG_OPT7}              ${PURPLE}║${RESET}"
        echo -e "${PURPLE}║${RESET}  ${GREEN}[7]${RESET} ${LANG_CONFIG_OPT6}                   ${PURPLE}║${RESET}"
        echo -e "${PURPLE}║${RESET}                                       ${PURPLE}║${RESET}"
        echo -e "${PURPLE}║${RESET}  ${RED}[8]${RESET} 🗑️  ${LANG_CONFIG_OPT9}        ${PURPLE}║${RESET}"
        echo -e "${PURPLE}╚═══════════════════════════════════════╝${RESET}"
        echo ""

        echo -ne "${CYAN}${LANG_CONFIG_SELECT} ${RESET}"
        read -r choice

        case $choice in
            1)  # Change command
                change_command
                ;;
            2)  # Change language
                change_language
                ;;
            3)  # Change timeout
                change_timeout
                ;;
            4)  # Toggle ESC
                toggle_esc
                ;;
            5)  # Change AI model
                change_ai_model
                ;;
            6)  # Clear cache
                clear_chat_cache
                ;;
            7)  # Back to chat
                return
                ;;
            8)  # Uninstall
                uninstall_terminal
                # If uninstall was cancelled, we continue the loop
                # If uninstall succeeded, the script will have exited
                ;;
            *)  # Invalid option
                echo -e "${RED}Invalid option. Please try again.${RESET}"
                sleep 1
                ;;
        esac
    done
}

# Change language function
change_language() {
    echo -e "\n${CYAN}Select Your Language:${RESET}"
    echo "  [1] 🇬🇧 English"
    echo "  [2] 🇩🇪 Deutsch"
    echo "  [3] 🇫🇷 Français"
    echo "  [4] 🇮🇹 Italiano"
    echo "  [5] 🇪🇸 Español"
    echo "  [6] 🇨🇳 中文 (Mandarin)"
    echo "  [7] 🇮🇳 हिन्दी (Hindi)"
    echo -n "Select [1-7]: "
    read -r lang_choice

    local new_lang=""
    case "$lang_choice" in
        1) new_lang="en" ;;
        2) new_lang="de" ;;
        3) new_lang="fr" ;;
        4) new_lang="it" ;;
        5) new_lang="es" ;;
        6) new_lang="zh" ;;
        7) new_lang="hi" ;;
        *) echo -e "${RED}Invalid choice${RESET}"; sleep 2; return ;;
    esac

    if [[ ! -z "$new_lang" ]]; then
        # Update config
        sed -i '' "s/AI_CHAT_LANGUAGE=.*/AI_CHAT_LANGUAGE=\"$new_lang\"/" "$CONFIG_FILE"
        echo -e "${GREEN}✅ Language changed to: $new_lang${RESET}"
        echo -e "${YELLOW}Changes will take effect on next chat session${RESET}"
        sleep 2
    fi
}

# Change timeout function
change_timeout() {
    echo -e "\n${CYAN}Set Session Timeout (in seconds):${RESET}"
    echo "Current: ${AI_CHAT_TIMEOUT:-600} seconds"
    echo -n "Enter new timeout (60-3600): "
    read -r new_timeout

    if [[ "$new_timeout" =~ ^[0-9]+$ ]] && [[ "$new_timeout" -ge 60 ]] && [[ "$new_timeout" -le 3600 ]]; then
        sed -i '' "s/AI_CHAT_TIMEOUT=.*/AI_CHAT_TIMEOUT=\"$new_timeout\"/" "$CONFIG_FILE"
        echo -e "${GREEN}✅ Timeout changed to: $new_timeout seconds${RESET}"
        sleep 2
    else
        echo -e "${RED}Invalid timeout. Must be 60-3600 seconds${RESET}"
        sleep 2
    fi
}

# Toggle ESC exit function
toggle_esc() {
    local current="${AI_CHAT_ESC_EXIT:-true}"
    local new_val="false"
    [[ "$current" == "false" ]] && new_val="true"

    sed -i '' "s/AI_CHAT_ESC_EXIT=.*/AI_CHAT_ESC_EXIT=\"$new_val\"/" "$CONFIG_FILE"
    echo -e "${GREEN}✅ ESC exit toggled to: $new_val${RESET}"
    sleep 2
}

# Change AI model function
change_ai_model() {
    echo -e "\n${CYAN}Select OpenAI Model:${RESET}"
    echo "  [1] gpt-4o       ⭐ RECOMMENDED - Best performance"
    echo "  [2] gpt-4o-mini   - Fast & cheap"
    echo "  [3] gpt-4-turbo  - Fast, good quality"
    echo "  [4] gpt-4        - Classic powerful"
    echo "  [5] gpt-3.5-turbo - Cheapest"
    echo -n "Select [1-5]: "
    read -r model_choice

    local new_model=""
    case "$model_choice" in
        1) new_model="gpt-4o" ;;
        2) new_model="gpt-4o-mini" ;;
        3) new_model="gpt-4-turbo" ;;
        4) new_model="gpt-4" ;;
        5) new_model="gpt-3.5-turbo" ;;
        *) echo -e "${RED}Invalid choice${RESET}"; sleep 2; return ;;
    esac

    # Update .env file
    if grep -q "DEFAULT_OPENAI_MODEL" "$ENV_FILE"; then
        sed -i '' "s/DEFAULT_OPENAI_MODEL=.*/DEFAULT_OPENAI_MODEL=\"$new_model\"/" "$ENV_FILE"
    else
        echo "DEFAULT_OPENAI_MODEL=\"$new_model\"" >> "$ENV_FILE"
    fi

    echo -e "${GREEN}✅ OpenAI Model changed to: $new_model (includes web search)${RESET}"
    sleep 2
}

# Change command function
change_command() {
    echo -e "\n${CYAN}Choose new command:${RESET}"
    echo "  [1] ai   - Clear and memorable"
    echo "  [2] ask  - Natural for questions"
    echo "  [3] q    - Quick single letter"
    echo "  [4] ??   - Double question mark"
    echo "  [5] chat - Descriptive"
    echo "  [6] Custom"
    echo -n "Select [1-6]: "
    read -r cmd_choice

    local new_cmd=""
    case "$cmd_choice" in
        1) new_cmd="ai" ;;
        2) new_cmd="ask" ;;
        3) new_cmd="q" ;;
        4) new_cmd="??" ;;
        5) new_cmd="chat" ;;
        6)
            echo -n "Enter custom command: "
            read -r new_cmd
            ;;
    esac

    if [[ ! -z "$new_cmd" ]]; then
        # Update config
        sed -i '' "s/AI_CHAT_COMMAND=.*/AI_CHAT_COMMAND=\"$new_cmd\"/" "$CONFIG_FILE"

        # Update shell alias
        update_shell_config "$new_cmd"

        echo -e "${GREEN}✅ Command changed to: $new_cmd${RESET}"
        echo -e "${YELLOW}${LANG_CONFIG_RESTART}${RESET}"
        sleep 2
    fi
}

# Clear chat cache function
clear_chat_cache() {
    echo -e "${YELLOW}${LANG_CONFIG_OPT7}...${RESET}"

    local cache_cleared=false

    # Clear from temp directory
    if [[ -d "/var/folders" ]]; then
        find /var/folders -name "*_chat" -type f 2>/dev/null | while read cache_file; do
            if [[ -w "$cache_file" ]]; then
                rm -f "$cache_file" 2>/dev/null && cache_cleared=true
                echo -e "  ${GREEN}✓${RESET} Cleared: $(basename $cache_file)"
            fi
        done
    fi

    # Clear from ~/.config/shell_gpt/chat_sessions
    if [[ -d "$HOME/.config/shell_gpt/chat_sessions" ]]; then
        find "$HOME/.config/shell_gpt/chat_sessions" -type f ! -name ".gitkeep" -delete 2>/dev/null
        cache_cleared=true
    fi

    if [[ "$cache_cleared" == "true" ]]; then
        echo -e "\n${GREEN}✅ Cache cleared successfully!${RESET}"
    else
        echo -e "\n${YELLOW}No cache files found.${RESET}"
    fi
    sleep 2
}

# Note: Web search is now included in ChatGPT - no separate configuration needed

# Uninstall function with translations
uninstall_terminal() {
    clear
    echo -e "${RED}${BOLD}⚠️  ${LANG_CONFIG_OPT9}${RESET}"
    echo ""
    echo "${LANG_UNINSTALL_WARNING}"
    echo ""
    echo "• AI Chat Terminal (~/.aichat)"
    echo "• Shell configuration aliases"
    echo ""
    echo -e "${YELLOW}${LANG_UNINSTALL_WARNING}${RESET}"
    echo ""
    echo "${LANG_UNINSTALL_CONFIRM}"
    echo -n "> "
    read -r confirm

    local delete_word="DELETE"
    # Set language-specific delete word if needed
    case "$LANGUAGE" in
        de*) delete_word="LÖSCHEN" ;;
        es*|ca|gl) delete_word="BORRAR" ;;
        fr) delete_word="SUPPRIMER" ;;
        it) delete_word="ELIMINA" ;;
    esac

    if [[ "$confirm" == "$delete_word" ]] || [[ "$confirm" == "DELETE" ]]; then
        echo ""
        echo "${LANG_UNINSTALL_PROGRESS}"

        # Remove from shell configs - smart detection approach
        local configs=("$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.profile")
        for config in "${configs[@]}"; do
            if [[ -f "$config" ]]; then
                # Remove source lines for aichat
                grep -v "source.*/\.aichat/aichat\.zsh" "$config" > "$config.tmp" && mv "$config.tmp" "$config"
                # Remove ANY alias that points to ai_chat_function (regardless of alias name)
                grep -v "alias.*=.*ai_chat_function" "$config" > "$config.tmp" && mv "$config.tmp" "$config"
                # Remove comments
                grep -v "# AI Chat Terminal" "$config" > "$config.tmp" && mv "$config.tmp" "$config"
                echo "  ✓ ${LANG_UNINSTALL_CLEANED} $config"
            fi
        done

        # Remove main installation directory (deferred to avoid deleting ourselves)
        echo "  ✓ ${LANG_UNINSTALL_REMOVED} ~/.aichat (will be removed after exit)"

        # Create cleanup script that runs after we exit
        cat > "/tmp/aichat_cleanup.sh" << 'EOF'
#!/bin/bash
sleep 1
rm -rf "$HOME/.aichat" 2>/dev/null
rm -f "/tmp/aichat_cleanup.sh" 2>/dev/null
EOF
        chmod +x "/tmp/aichat_cleanup.sh"
        nohup "/tmp/aichat_cleanup.sh" >/dev/null 2>&1 &

        echo ""
        echo -e "${GREEN}✓ ${LANG_UNINSTALL_SUCCESS}${RESET}"
        echo ""
        echo "${LANG_UNINSTALL_RESTART}"
        echo "  source ~/.zshrc"
        echo ""
        echo "${LANG_UNINSTALL_GOODBYE}"
        echo ""
        echo "${LANG_UNINSTALL_ANYKEY}"
        read -r
        echo ""
        echo -e "${GREEN}Uninstall completed. Please restart your terminal or run: source ~/.zshrc${RESET}"
        echo ""
        echo "Returning to normal terminal..."
        cd "$HOME"
        exec "$SHELL"
    else
        echo -e "${GREEN}Cancelled.${RESET}"
        sleep 2
    fi
}