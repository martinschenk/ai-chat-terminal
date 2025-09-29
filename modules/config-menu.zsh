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
        local ENABLE_ESC="${AI_CHAT_ESC_EXIT:-true}"
        local CONTEXT_WINDOW="${AI_CHAT_CONTEXT_WINDOW:-20}"
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

        echo -e "${PURPLE}┌─────────────────────────────────────${RESET}"
        echo -e "${PURPLE}│${RESET}  ${LANG_CONFIG_CURRENT}"
        echo -e "${PURPLE}│${RESET}  ├─ ${LANG_CONFIG_COMMAND}: ${YELLOW}$COMMAND_CHAR${RESET}"
        echo -e "${PURPLE}│${RESET}  ├─ ${LANG_CONFIG_LANGUAGE}: ${YELLOW}$LANGUAGE${RESET}"
        echo -e "${PURPLE}│${RESET}  ├─ AI Model: ${YELLOW}${AI_CHAT_MODEL}${RESET}"
        echo -e "${PURPLE}│${RESET}  ├─ ${LANG_CONFIG_CONTEXT_WINDOW:-Context Window}: ${YELLOW}$CONTEXT_WINDOW ${LANG_CONTEXT_MESSAGES:-messages}${RESET}"
        echo -e "${PURPLE}│${RESET}  └─ ${LANG_CONFIG_ESC}: ${YELLOW}$ENABLE_ESC${RESET}"
        echo -e "${PURPLE}├─────────────────────────────────────${RESET}"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[1]${RESET} ${LANG_CONFIG_OPT1}"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[2]${RESET} ${LANG_CONFIG_OPT2}"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[3]${RESET} ${LANG_CONFIG_OPT4}"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[4]${RESET} ${LANG_CONFIG_OPT5}"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[5]${RESET} 💬 ${LANG_CONTEXT_SET:-Set context window}"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[6]${RESET} 🔑 Set OpenAI API key"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[7]${RESET} 🧠 ${LANG_CONFIG_MEMORY_SYSTEM:-Memory system}"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[8]${RESET} 🧹 ${LANG_CONFIG_OPT7}"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[9]${RESET} ℹ️  ${LANG_CONFIG_ABOUT:-About & Version}"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[10]${RESET} ${LANG_CONFIG_OPT6}"
        echo -e "${PURPLE}│${RESET}"
        echo -e "${PURPLE}│${RESET}  ${RED}[11]${RESET} 🗑️  ${LANG_CONFIG_OPT9}"
        echo -e "${PURPLE}└─────────────────────────────────────${RESET}"
        echo ""

        echo -ne "${CYAN}${LANG_CONFIG_SELECT_OPTION:-Select [1-11]:} ${RESET}"

        # Handle ESC key detection in config menu
        local choice=""
        if [[ "$ENABLE_ESC" == "true" ]] && [[ -t 0 ]]; then
            # Save current terminal settings
            OLD_STTY=$(stty -g)
            stty raw -echo min 1 time 0 2>/dev/null

            while true; do
                char=$(dd bs=1 count=1 2>/dev/null)

                if [[ $char == $'\e' ]]; then
                    # ESC pressed - return to terminal
                    stty "$OLD_STTY" 2>/dev/null
                    echo -e "\n\n${YELLOW}👋 ${LANG_MSG_GOODBYE:-Goodbye!}${RESET}\n"
                    return
                elif [[ $char == $'\r' ]] || [[ $char == $'\n' ]]; then
                    # Enter pressed
                    stty "$OLD_STTY" 2>/dev/null
                    echo
                    break
                elif [[ $char == $'\177' ]] || [[ $char == $'\b' ]]; then
                    # Backspace
                    if [[ -n "$choice" ]]; then
                        choice="${choice%?}"
                        echo -ne "\b \b"
                    fi
                else
                    # Normal character
                    choice="${choice}${char}"
                    echo -n "$char"
                fi
            done
        else
            # Simple read without ESC
            read -r choice
        fi

        case $choice in
            1)  # Change command
                change_command
                ;;
            2)  # Change language
                change_language
                ;;
            3)  # Toggle ESC
                toggle_esc
                ;;
            4)  # Change AI model
                change_ai_model
                ;;
            5)  # Set context window
                change_context_window
                ;;
            6)  # Set OpenAI API key
                change_openai_api_key
                ;;
            7)  # Memory system
                memory_system_menu
                ;;
            8)  # Clear cache
                clear_chat_cache
                ;;
            9)  # About & Version
                show_about_info
                ;;
            10)  # Back to chat
                return
                ;;
            11)  # Uninstall
                uninstall_terminal
                # If uninstall was cancelled, we continue the loop
                # If uninstall succeeded, the script will have exited
                ;;
            *)  # Invalid option
                echo -e "${RED}${LANG_CONFIG_INVALID:-Invalid option. Please try again.}${RESET}"
                sleep 1
                ;;
        esac
    done
}

# Change language function
change_language() {
    echo -e "\n${CYAN}${LANG_SELECT_LANGUAGE:-Select Your Language:}${RESET}"
    echo ""
    echo -e "${BOLD}Main Languages:${RESET}"
    echo "  [1] 🇬🇧 English"
    echo "  [2] 🇩🇪 Deutsch"
    echo "  [3] 🇪🇸 Español"
    echo "  [4] 🇫🇷 Français"
    echo "  [5] 🇮🇹 Italiano"
    echo "  [6] 🇨🇳 中文 (Mandarin)"
    echo "  [7] 🇮🇳 हिन्दी (Hindi)"
    echo ""
    echo -e "${BOLD}Regional Languages:${RESET}"
    echo "  [8] 🏴 Euskera (Basque)"
    echo "  [9] 🏴 Català (Catalan)"
    echo "  [10] 🏴 Galego (Galician)"
    echo ""
    echo -e "${BOLD}Dialects:${RESET}"
    echo "  [11] 🇩🇪 Schwäbisch"
    echo "  [12] 🇩🇪 Bayerisch"
    echo "  [13] 🇩🇪 Sächsisch"
    echo "  [14] 🇲🇽 Español Mexicano"
    echo "  [15] 🇦🇷 Español Argentino"
    echo "  [16] 🇨🇴 Español Colombiano"
    echo "  [17] 🇻🇪 Español Venezolano"
    echo "  [18] 🇨🇱 Español Chileno"
    echo "  [19] 🇪🇸 Español Andaluz"
    echo -n "Select [1-19]: "
    read -r lang_choice

    local new_lang=""
    case "$lang_choice" in
        1) new_lang="en" ;;
        2) new_lang="de" ;;
        3) new_lang="es" ;;
        4) new_lang="fr" ;;
        5) new_lang="it" ;;
        6) new_lang="zh" ;;
        7) new_lang="hi" ;;
        8) new_lang="eu" ;;
        9) new_lang="ca" ;;
        10) new_lang="gl" ;;
        11) new_lang="de-schwaebisch" ;;
        12) new_lang="de-bayerisch" ;;
        13) new_lang="de-saechsisch" ;;
        14) new_lang="es-mexicano" ;;
        15) new_lang="es-argentino" ;;
        16) new_lang="es-colombiano" ;;
        17) new_lang="es-venezolano" ;;
        18) new_lang="es-chileno" ;;
        19) new_lang="es-andaluz" ;;
        *) echo -e "${RED}${LANG_SELECT_INVALID:-Invalid choice}${RESET}"; sleep 2; return ;;
    esac

    if [[ ! -z "$new_lang" ]]; then
        # Update config
        sed -i '' "s/AI_CHAT_LANGUAGE=.*/AI_CHAT_LANGUAGE=\"$new_lang\"/" "$CONFIG_FILE"

        # Reload language file immediately
        local LANG_FILE="$SCRIPT_DIR/lang/${new_lang}.conf"
        if [[ -f "$LANG_FILE" ]]; then
            source "$LANG_FILE"
            echo -e "${GREEN}✅ Language changed to: $new_lang${RESET}"
            echo -e "${GREEN}Language active immediately!${RESET}"
        else
            # Fallback to default English strings
            setup_default_language
            echo -e "${GREEN}✅ Language changed to: $new_lang (English fallback)${RESET}"
        fi
        sleep 2
    fi
}

# Change context window function
change_context_window() {
    echo -e "\n${CYAN}${LANG_CONTEXT_SET:-Set Context Window Size:}${RESET}"
    echo "Current: ${AI_CHAT_CONTEXT_WINDOW:-20} messages"
    echo ""
    echo "Recommended settings:"
    echo "  ${GREEN}5-10${RESET}    = Very low cost (~\$0.005/msg)"
    echo "  ${YELLOW}15-25${RESET}   = Balanced cost/memory (~\$0.01/msg)"
    echo "  ${RED}30-50${RESET}   = Higher cost but more memory (~\$0.025/msg)"
    echo ""
    echo -n "Enter context window size (5-50): "
    read -r new_window

    if [[ "$new_window" =~ ^[0-9]+$ ]] && [[ "$new_window" -ge 5 ]] && [[ "$new_window" -le 50 ]]; then
        sed -i '' "s/AI_CHAT_CONTEXT_WINDOW=.*/AI_CHAT_CONTEXT_WINDOW=\"$new_window\"/" "$CONFIG_FILE"
        echo -e "${GREEN}✅ Context window changed to: $new_window messages${RESET}"

        # Calculate rough cost estimate
        local cost_estimate=$(echo "scale=3; $new_window * 0.0005" | bc 2>/dev/null || echo "~\$0.01")
        echo -e "${CYAN}Estimated cost per message: ~\$$cost_estimate${RESET}"
        sleep 3
    else
        echo -e "${RED}Invalid size. Must be 5-50 messages${RESET}"
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
        *) echo -e "${RED}${LANG_SELECT_INVALID:-Invalid choice}${RESET}"; sleep 2; return ;;
    esac

    # Update config file (the one chat_system.py actually reads from!)
    if grep -q "AI_CHAT_MODEL" "$CONFIG_FILE"; then
        sed -i '' "s/AI_CHAT_MODEL=.*/AI_CHAT_MODEL=\"$new_model\"/" "$CONFIG_FILE"
    else
        echo "AI_CHAT_MODEL=\"$new_model\"" >> "$CONFIG_FILE"
    fi

    echo -e "${GREEN}✅ OpenAI Model changed to: $new_model${RESET}"
    sleep 2
}

# Change OpenAI API key function
change_openai_api_key() {
    echo -e "\n${CYAN}Set OpenAI API Key:${RESET}"
    echo "Current: ${OPENAI_API_KEY:0:8}..." # Show first 8 chars for verification
    echo ""
    echo -e "${YELLOW}You can get your API key from: https://platform.openai.com/api-keys${RESET}"
    echo ""
    echo -n "Enter new OpenAI API key: "
    read -r new_key

    if [[ -n "$new_key" ]] && [[ "$new_key" != "Enter your OpenAI API key:" ]]; then
        # Validate key format (starts with sk- and has reasonable length)
        if [[ "$new_key" =~ ^sk-[A-Za-z0-9_-]{20,}$ ]]; then
            # Update .env file
            sed -i '' "s/OPENAI_API_KEY=.*/OPENAI_API_KEY=\"$new_key\"/" "$ENV_FILE"
            echo -e "${GREEN}✅ OpenAI API key updated successfully!${RESET}"
            echo -e "${GREEN}Key active immediately for all new chats.${RESET}"
        else
            echo -e "${RED}❌ Invalid API key format. Keys should start with 'sk-'${RESET}"
        fi
        sleep 2
    else
        echo -e "${YELLOW}No changes made.${RESET}"
        sleep 1
    fi
}

# Change command function
change_command() {
    echo -e "\n${CYAN}Choose new command:${RESET}"
    echo "  [1] chat - Clear and descriptive"
    echo "  [2] ai   - Short and memorable"
    echo "  [3] ask  - Natural for questions"
    echo "  [4] q    - Quick single letter"
    echo "  [5] ??   - Double question mark"
    echo "  [6] Custom"
    echo -n "Select [1-6]: "
    read -r cmd_choice

    local new_cmd=""
    case "$cmd_choice" in
        1) new_cmd="chat" ;;
        2) new_cmd="ai" ;;
        3) new_cmd="ask" ;;
        4) new_cmd="q" ;;
        5) new_cmd="??" ;;
        6)
            echo -n "Enter custom command: "
            read -r new_cmd
            ;;
    esac

    if [[ ! -z "$new_cmd" ]]; then
        # Update config
        sed -i '' "s/AI_CHAT_COMMAND=.*/AI_CHAT_COMMAND=\"$new_cmd\"/" "$CONFIG_FILE"

        # Update shell alias with noglob
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

    # Clear shell-gpt chat cache
    if [[ -d "/tmp/chat_cache" ]]; then
        local count=$(find /tmp/chat_cache -name "${AI_CHAT_COMMAND:-chat}_*" -type f 2>/dev/null | wc -l)
        if [[ $count -gt 0 ]]; then
            find /tmp/chat_cache -name "${AI_CHAT_COMMAND:-chat}_*" -type f -delete 2>/dev/null
            echo -e "  ${GREEN}✓${RESET} Cleared $count chat sessions"
            cache_cleared=true
        fi
    fi

    # Clear old session files from other locations
    if [[ -d "/var/folders" ]]; then
        find /var/folders -name "*_chat" -type f 2>/dev/null | while read cache_file; do
            if [[ -w "$cache_file" ]]; then
                rm -f "$cache_file" 2>/dev/null && cache_cleared=true
                echo -e "  ${GREEN}✓${RESET} Cleared: $(basename $cache_file)"
            fi
        done
    fi

    if [[ "$cache_cleared" == "true" ]]; then
        echo -e "\n${GREEN}✅ Cache cleared successfully!${RESET}"
        echo -e "${CYAN}Next chat will start fresh with no memory.${RESET}"
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
    echo -e "${YELLOW}${LANG_UNINSTALL_WARNING}${RESET}"
    echo ""
    echo "• AI Chat Terminal (~/.aichat)"
    echo "• Shell configuration aliases"
    echo "• Chat history & memory database"
    echo "• All personal data and conversations"
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
                grep -v "alias.*noglob.*ai_chat_function" "$config" > "$config.tmp" && mv "$config.tmp" "$config"
                # Remove comments
                grep -v "# AI Chat Terminal" "$config" > "$config.tmp" && mv "$config.tmp" "$config"
                echo "  ✓ ${LANG_UNINSTALL_CLEANED} $config"
            fi
        done

        # Remove chat cache and temporary files
        if [[ -d "/tmp/chat_cache" ]]; then
            rm -rf "/tmp/chat_cache" 2>/dev/null
            echo "  ✓ ${LANG_UNINSTALL_CLEANED} /tmp/chat_cache"
        fi

        # Remove main installation directory (deferred to avoid deleting ourselves)
        echo "  ✓ ${LANG_UNINSTALL_REMOVED} ~/.aichat (will be removed after exit)"

        # Create cleanup script that runs after we exit
        cat > "/tmp/aichat_cleanup.sh" << 'EOF'
#!/bin/bash
sleep 1
# Remove entire .aichat directory including memory database
rm -rf "$HOME/.aichat" 2>/dev/null
# Clean up any remaining temporary files
rm -rf "/tmp/chat_cache" 2>/dev/null
rm -f "/tmp/aichat_cleanup.sh" 2>/dev/null
EOF
        chmod +x "/tmp/aichat_cleanup.sh"
        ( nohup "/tmp/aichat_cleanup.sh" >/dev/null 2>&1 & )

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
        cd "$HOME"
        exec "$SHELL"
    else
        echo -e "${GREEN}Cancelled.${RESET}"
        sleep 2
    fi
}

# Show about and version information
show_about_info() {
    local CYAN='\033[0;36m'
    local GREEN='\033[0;32m'
    local YELLOW='\033[1;33m'
    local BLUE='\033[0;34m'
    local RESET='\033[0m'
    local BOLD='\033[1m'
    local DIM='\033[2m'

    clear
    echo -e "${CYAN}ℹ️  About AI Chat Terminal${RESET}\n"

    echo -e "${CYAN}${BOLD}AI Chat Terminal${RESET}"
    echo -e "${DIM}Version: ${RESET}${AI_CHAT_VERSION}"
    echo ""

    echo -e "${YELLOW}Author:${RESET} ${AI_CHAT_AUTHOR}"
    echo -e "${YELLOW}License:${RESET} ${AI_CHAT_LICENSE}"
    echo -e "${YELLOW}Repository:${RESET} ${DIM}${AI_CHAT_REPOSITORY}${RESET}"
    echo ""

    echo -e "${GREEN}Features:${RESET}"
    echo -e "  • ${GREEN}ChatGPT-powered terminal${RESET}"
    echo -e "  • ${GREEN}AI Vector Database memory${RESET}"
    echo -e "  • ${GREEN}19 languages + dialects${RESET}"
    echo -e "  • ${GREEN}Function calling support${RESET}"
    echo ""

    echo -e "${DIM}Built on Shell-GPT by TheR1D${RESET}"
    echo -e "${DIM}Copyright © 2025 Martin Schenk${RESET}"
    echo ""
    echo -e "${CYAN}Press any key to return...${RESET}"
    read -r
}

# Memory system menu
memory_system_menu() {
    local CYAN='\033[0;36m'
    local GREEN='\033[0;32m'
    local YELLOW='\033[1;33m'
    local PURPLE='\033[0;35m'
    local RED='\033[0;31m'
    local BLUE='\033[0;34m'
    local RESET='\033[0m'
    local BOLD='\033[1m'
    local DIM='\033[2m'

    while true; do
        clear
        echo -e "${BOLD}${CYAN}🧠 ${LANG_MEMORY_TITLE:-Memory System}${RESET}\n"

        # Get memory statistics
        local MEMORY_STATS=""
        if [[ -f "$SCRIPT_DIR/memory_system.py" ]]; then
            MEMORY_STATS=$(python3 "$SCRIPT_DIR/memory_system.py" stats 2>/dev/null)
        fi

        # Parse stats
        local TOTAL_MESSAGES="0"
        local TOTAL_SESSIONS="0"
        local DB_SIZE="0.0"
        local OLDEST_DATE="N/A"
        local NEWEST_DATE="N/A"

        if [[ -n "$MEMORY_STATS" ]]; then
            TOTAL_MESSAGES=$(echo "$MEMORY_STATS" | jq -r '.total_messages // 0' 2>/dev/null)
            TOTAL_SESSIONS=$(echo "$MEMORY_STATS" | jq -r '.total_sessions // 0' 2>/dev/null)
            DB_SIZE=$(echo "$MEMORY_STATS" | jq -r '.db_size_mb // 0' 2>/dev/null)
            OLDEST_DATE=$(echo "$MEMORY_STATS" | jq -r '.oldest_message // "N/A"' 2>/dev/null)
            NEWEST_DATE=$(echo "$MEMORY_STATS" | jq -r '.newest_message // "N/A"' 2>/dev/null)
        fi

        echo -e "${PURPLE}┌─────────────────────────────────────${RESET}"
        echo -e "${PURPLE}│${RESET}  ${BOLD}Memory Database Statistics:${RESET}"
        echo -e "${PURPLE}│${RESET}  ├─ Total Messages: ${YELLOW}$TOTAL_MESSAGES${RESET}"
        echo -e "${PURPLE}│${RESET}  ├─ Chat Sessions: ${YELLOW}$TOTAL_SESSIONS${RESET}"
        echo -e "${PURPLE}│${RESET}  ├─ Database Size: ${YELLOW}${DB_SIZE} MB${RESET}"
        echo -e "${PURPLE}│${RESET}  ├─ Oldest Message: ${YELLOW}$OLDEST_DATE${RESET}"
        echo -e "${PURPLE}│${RESET}  └─ Newest Message: ${YELLOW}$NEWEST_DATE${RESET}"
        echo -e "${PURPLE}├─────────────────────────────────────${RESET}"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[1]${RESET} ${LANG_MEMORY_SEARCH:-Search memories}"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[2]${RESET} Show recent messages"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[3]${RESET} Database statistics"
        echo -e "${PURPLE}│${RESET}  ${YELLOW}[4]${RESET} Smart cleanup (5000+ msgs/50MB)"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[5]${RESET} Back to main menu"
        echo -e "${PURPLE}└─────────────────────────────────────${RESET}"
        echo ""

        echo -ne "${CYAN}Select [1-5]: ${RESET}"

        # Handle ESC key detection in memory menu
        local choice=""
        if [[ "$ENABLE_ESC" == "true" ]] && [[ -t 0 ]]; then
            # Save current terminal settings
            OLD_STTY=$(stty -g)
            stty raw -echo min 1 time 0 2>/dev/null

            while true; do
                char=$(dd bs=1 count=1 2>/dev/null)

                if [[ $char == $'\e' ]]; then
                    # ESC pressed - return to terminal
                    stty "$OLD_STTY" 2>/dev/null
                    echo -e "\n\n${YELLOW}👋 ${LANG_MSG_GOODBYE:-Goodbye!}${RESET}\n"
                    return
                elif [[ $char == $'\r' ]] || [[ $char == $'\n' ]]; then
                    # Enter pressed
                    stty "$OLD_STTY" 2>/dev/null
                    echo
                    break
                elif [[ $char == $'\177' ]] || [[ $char == $'\b' ]]; then
                    # Backspace
                    if [[ -n "$choice" ]]; then
                        choice="${choice%?}"
                        echo -ne "\b \b"
                    fi
                else
                    # Normal character
                    choice="${choice}${char}"
                    echo -n "$char"
                fi
            done
        else
            # Simple read without ESC
            read -r choice
        fi

        case $choice in
            1)  # Search memories
                echo ""
                echo -ne "${CYAN}${LANG_MEMORY_ENTER_QUERY:-Enter search query:} ${RESET}"
                read -r query
                if [[ -n "$query" ]]; then
                    echo -e "\n${YELLOW}Searching memories for: \"$query\"${RESET}\n"
                    if [[ -f "$SCRIPT_DIR/memory_system.py" ]]; then
                        python3 "$SCRIPT_DIR/memory_system.py" search "$query" 2>/dev/null || echo -e "${RED}Error searching memories${RESET}"
                    else
                        echo -e "${RED}Memory system not available${RESET}"
                    fi
                    echo ""
                    echo -e "${CYAN}Press any key to continue...${RESET}"
                    read -r
                fi
                ;;
            2)  # Show recent messages
                echo -e "\n${YELLOW}Recent messages from current session:${RESET}\n"
                # Get current command from config
                local CONFIG_FILE="$HOME/.aichat/config"
                local COMMAND_CHAR="chat"
                if [[ -f "$CONFIG_FILE" ]]; then
                    source "$CONFIG_FILE"
                    COMMAND_CHAR="${AI_CHAT_COMMAND:-chat}"
                fi
                local CHAT_NAME="${COMMAND_CHAR}_session"
                if [[ -f "/tmp/chat_cache/$CHAT_NAME" ]]; then
                    python3 -c "
import json
try:
    with open('/tmp/chat_cache/$CHAT_NAME', 'r') as f:
        messages = json.load(f)
    for msg in messages[-10:]:  # Last 10 messages
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')[:100]
        print(f'{role}: {content}...')
except:
    print('No recent messages found')
"
                else
                    echo "No recent chat session found"
                fi
                echo ""
                echo -e "${CYAN}Press any key to continue...${RESET}"
                read -r
                ;;
            3)  # Database statistics
                echo -e "\n${YELLOW}Detailed Statistics:${RESET}\n"
                if [[ -f "$SCRIPT_DIR/memory_system.py" ]]; then
                    python3 "$SCRIPT_DIR/memory_system.py" stats 2>/dev/null | jq . 2>/dev/null || echo -e "${RED}Error getting statistics${RESET}"
                else
                    echo -e "${RED}Memory system not available${RESET}"
                fi
                echo ""
                echo -e "${CYAN}Press any key to continue...${RESET}"
                read -r
                ;;
            4)  # Smart cleanup
                echo ""
                echo -e "${YELLOW}⚠️  Smart Cleanup: Removes low-priority messages if over 5000 msgs or 50MB${RESET}"
                echo -e "${YELLOW}   Keeps important messages (names, TODOs) forever${RESET}"
                echo -ne "${CYAN}Continue? (y/N): ${RESET}"
                read -r confirm
                if [[ "$confirm" =~ ^[Yy]$ ]]; then
                    if [[ -f "$SCRIPT_DIR/memory_system.py" ]]; then
                        local RESULT=$(python3 "$SCRIPT_DIR/memory_system.py" cleanup force 2>/dev/null)
                        echo -e "${GREEN}$RESULT${RESET}"
                    else
                        echo -e "${RED}Memory system not available${RESET}"
                    fi
                    echo ""
                    echo -e "${CYAN}Press any key to continue...${RESET}"
                    read -r
                fi
                ;;
            5)  # Back
                return
                ;;
            *)
                echo -e "${RED}${LANG_CONFIG_INVALID:-Invalid option. Please try again.}${RESET}"
                sleep 1
                ;;
        esac
    done
}