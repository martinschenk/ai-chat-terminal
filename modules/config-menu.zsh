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
        echo -e "${PURPLE}│${RESET}  ├─ ${LANG_CONFIG_ESC}: ${YELLOW}$ENABLE_ESC${RESET}"
        echo -e "${PURPLE}│${RESET}  └─ Ollama always-on: ${YELLOW}${OLLAMA_ALWAYS_ON:-false}${RESET}"
        echo -e "${PURPLE}├─────────────────────────────────────${RESET}"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[1]${RESET} ${LANG_CONFIG_OPT1}"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[2]${RESET} ${LANG_CONFIG_OPT2}"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[3]${RESET} ${LANG_CONFIG_OPT4}"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[4]${RESET} ${LANG_CONFIG_OPT5}"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[5]${RESET} 💬 ${LANG_CONTEXT_SET:-Set context window}"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[6]${RESET} 🔑 Set OpenAI API key"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[7]${RESET} 🔒 Privacy & AI Models"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[8]${RESET} ⚡ Toggle Ollama always-on"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[9]${RESET} 🧹 ${LANG_CONFIG_OPT7}"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[10]${RESET} ℹ️  ${LANG_CONFIG_ABOUT:-About & Version}"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[11]${RESET} ${LANG_CONFIG_OPT6}"
        echo -e "${PURPLE}│${RESET}"
        echo -e "${PURPLE}│${RESET}  ${RED}[12]${RESET} 🗑️  ${LANG_CONFIG_OPT9}"
        echo -e "${PURPLE}└─────────────────────────────────────${RESET}"
        echo ""

        echo -ne "${CYAN}${LANG_CONFIG_SELECT_OPTION:-Select [1-12]:} ${RESET}"

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
            7)  # Privacy & AI Models
                privacy_models_menu
                ;;
            8)  # Toggle Ollama always-on
                toggle_ollama_always_on
                ;;
            9)  # Clear cache
                clear_chat_cache
                ;;
            10)  # About & Version
                show_about_info
                ;;
            11)  # Back to chat
                return
                ;;
            12)  # Uninstall
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
    echo "  [1] 🇬🇧 English"
    echo "  [2] 🇩🇪 Deutsch"
    echo "  [3] 🇪🇸 Español"
    echo -n "Select [1-3]: "
    read -r lang_choice

    local new_lang=""
    case "$lang_choice" in
        1) new_lang="en" ;;
        2) new_lang="de" ;;
        3) new_lang="es" ;;
        *) echo -e "${RED}${LANG_SELECT_INVALID:-Invalid choice}${RESET}"; sleep 2; return ;;
    esac

    if [[ ! -z "$new_lang" ]]; then
        # Update config
        sed -i '' "s/AI_CHAT_LANGUAGE=.*/AI_CHAT_LANGUAGE=\"$new_lang\"/" "$CONFIG_FILE"

        # Clear chat history cache to force new language (CRITICAL!)
        echo -e "${YELLOW}🧹 Clearing chat cache to apply new language...${RESET}"
        rm -f "$SCRIPT_DIR"/chat_history_*.db 2>/dev/null
        rm -f "$SCRIPT_DIR"/memory.db 2>/dev/null

        # Restart daemon to reload language setting
        pkill -f chat_daemon.py 2>/dev/null
        echo -e "${GREEN}✅ Cache cleared, daemon restarted${RESET}"

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

# Toggle Ollama always-on function
toggle_ollama_always_on() {
    echo -e "\n${CYAN}⚡ Ollama Daemon Management${RESET}"
    echo ""
    echo "Current mode: ${YELLOW}${OLLAMA_ALWAYS_ON:-false}${RESET}"
    echo ""
    echo -e "${BOLD}Modes:${RESET}"
    echo "  • ${GREEN}false${RESET} (managed) - Ollama starts/stops with chat (saves RAM)"
    echo "  • ${YELLOW}true${RESET}  (always-on) - Ollama runs continuously"
    echo ""

    local current="${OLLAMA_ALWAYS_ON:-false}"
    local new_val="true"
    [[ "$current" == "true" ]] && new_val="false"

    if grep -q "OLLAMA_ALWAYS_ON" "$CONFIG_FILE"; then
        sed -i '' "s/OLLAMA_ALWAYS_ON=.*/OLLAMA_ALWAYS_ON=\"$new_val\"/" "$CONFIG_FILE"
    else
        echo "OLLAMA_ALWAYS_ON=\"$new_val\"" >> "$CONFIG_FILE"
    fi

    echo -e "${GREEN}✅ Ollama mode changed to: $new_val${RESET}"

    if [[ "$new_val" == "false" ]]; then
        echo -e "${CYAN}ℹ️  Ollama will now start/stop with chat sessions (saves RAM)${RESET}"
    else
        echo -e "${CYAN}ℹ️  Ollama will run continuously in background${RESET}"
    fi

    sleep 3
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

    # Clear AI Chat Terminal memory database (v9.0.0+)
    if [[ -f "$SCRIPT_DIR/memory.db" ]]; then
        rm -f "$SCRIPT_DIR/memory.db" 2>/dev/null
        echo -e "  ${GREEN}✓${RESET} Cleared memory.db (chat history)"
        cache_cleared=true
    fi

    # Clear any session-specific DB files
    local session_dbs=$(find "$SCRIPT_DIR" -name "chat_history_*.db" 2>/dev/null | wc -l)
    if [[ $session_dbs -gt 0 ]]; then
        rm -f "$SCRIPT_DIR"/chat_history_*.db 2>/dev/null
        echo -e "  ${GREEN}✓${RESET} Cleared $session_dbs session databases"
        cache_cleared=true
    fi

    # Restart daemon to reload fresh state
    pkill -f chat_daemon.py 2>/dev/null
    echo -e "  ${GREEN}✓${RESET} Daemon restarted"

    # Clear shell-gpt chat cache (legacy)
    if [[ -d "/tmp/chat_cache" ]]; then
        local count=$(find /tmp/chat_cache -name "${AI_CHAT_COMMAND:-chat}_*" -type f 2>/dev/null | wc -l)
        if [[ $count -gt 0 ]]; then
            find /tmp/chat_cache -name "${AI_CHAT_COMMAND:-chat}_*" -type f -delete 2>/dev/null
            echo -e "  ${GREEN}✓${RESET} Cleared $count legacy chat sessions"
            cache_cleared=true
        fi
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
    echo -e "  • ${GREEN}Hybrid daemon architecture${RESET}"
    echo -e "  • ${GREEN}95% faster responses${RESET}"
    echo ""

    echo -e "${DIM}Powered by OpenAI GPT-4, Phi-3 & Ollama${RESET}"
    echo -e "${DIM}Copyright © 2025 Martin Schenk${RESET}"
    echo ""
    echo -e "${CYAN}Press any key to return...${RESET}"
    read -r
}

# Privacy & AI Models Configuration Menu
privacy_models_menu() {
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
        echo -e "${BOLD}${CYAN}🔒 ${LANG_PRIVACY_TITLE}${RESET}\n"

        # Load current settings
        local PRIVACY_LEVEL="${PRIVACY_LEVEL:-enhanced}"
        local PRESIDIO_ENABLED="${PRESIDIO_ENABLED:-true}"
        local PHI3_ENABLED="${PHI3_ENABLED:-false}"
        local RESPONSE_MODE="${RESPONSE_MODE:-template}"

        # Check installed models
        local presidio_status="${RED}${LANG_PRIVACY_NOT_INSTALLED}${RESET}"
        if python3 -c "import presidio_analyzer" 2>/dev/null; then
            presidio_status="${GREEN}${LANG_PRIVACY_INSTALLED}${RESET}"
        fi

        local phi3_status="${RED}${LANG_PRIVACY_NOT_INSTALLED}${RESET}"
        if command -v ollama &> /dev/null && ollama list | grep -q "phi3"; then
            phi3_status="${GREEN}${LANG_PRIVACY_INSTALLED}${RESET}"
        fi

        local spacy_models=$(python3 -c "import spacy; print(len(spacy.util.get_installed_models()))" 2>/dev/null || echo "0")

        echo -e "${PURPLE}┌─────────────────────────────────────${RESET}"
        echo -e "${PURPLE}│${RESET}  ${BOLD}${LANG_PRIVACY_CURRENT_CONFIG}${RESET}"
        echo -e "${PURPLE}│${RESET}  ├─ ${LANG_PRIVACY_LEVEL} ${YELLOW}$PRIVACY_LEVEL${RESET}"
        echo -e "${PURPLE}│${RESET}  ├─ ${LANG_PRIVACY_PRESIDIO} ${YELLOW}$PRESIDIO_ENABLED${RESET} ($presidio_status)"
        echo -e "${PURPLE}│${RESET}  ├─ ${LANG_PRIVACY_PHI3} ${YELLOW}$PHI3_ENABLED${RESET} ($phi3_status)"
        echo -e "${PURPLE}│${RESET}  ├─ ${LANG_PRIVACY_RESPONSE_MODE} ${YELLOW}$RESPONSE_MODE${RESET}"
        echo -e "${PURPLE}│${RESET}  └─ ${LANG_PRIVACY_SPACY_MODELS} ${YELLOW}$spacy_models ${LANG_PRIVACY_INSTALLED}${RESET}"
        echo -e "${PURPLE}├─────────────────────────────────────${RESET}"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[1]${RESET} ${LANG_PRIVACY_OPT1}"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[2]${RESET} ${LANG_PRIVACY_OPT2}"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[3]${RESET} ${LANG_PRIVACY_OPT3}"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[4]${RESET} ${LANG_PRIVACY_OPT4}"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[5]${RESET} ${LANG_PRIVACY_OPT5}"
        echo -e "${PURPLE}│${RESET}  ${GREEN}[6]${RESET} ${LANG_PRIVACY_OPT6}"
        echo -e "${PURPLE}└─────────────────────────────────────${RESET}"
        echo ""

        echo -ne "${CYAN}${LANG_PRIVACY_SELECT} ${RESET}"
        read -r choice

        case $choice in
            1)  # Change Privacy Level
                echo -e "\n${CYAN}Select Privacy Level:${RESET}"
                echo "  [1] Enhanced - AI + Presidio (best protection)"
                echo "  [2] Basic - AI-based only"
                echo "  [3] Off - No privacy protection"
                echo -n "Select [1-3]: "
                read -r privacy_choice

                case "$privacy_choice" in
                    1)
                        sed -i '' "s/PRIVACY_LEVEL=.*/PRIVACY_LEVEL=\"enhanced\"/" "$CONFIG_FILE"
                        echo -e "${GREEN}✅ Privacy level set to: enhanced${RESET}"
                        ;;
                    2)
                        sed -i '' "s/PRIVACY_LEVEL=.*/PRIVACY_LEVEL=\"basic\"/" "$CONFIG_FILE"
                        echo -e "${GREEN}✅ Privacy level set to: basic${RESET}"
                        ;;
                    3)
                        sed -i '' "s/PRIVACY_LEVEL=.*/PRIVACY_LEVEL=\"off\"/" "$CONFIG_FILE"
                        echo -e "${YELLOW}⚠️  Privacy protection disabled${RESET}"
                        ;;
                esac
                sleep 2
                ;;

            2)  # Install/Remove Presidio
                if python3 -c "import presidio_analyzer" 2>/dev/null; then
                    echo -e "\n${RED}${BOLD}${LANG_DELETE_WARNING_TITLE}${RESET}"
                    echo -e "${YELLOW}${LANG_DELETE_WARNING_SHARED}${RESET}"
                    echo -e "${DIM}${LANG_DELETE_WARNING_CHECK}${RESET}"
                    echo -e "${DIM}${LANG_DELETE_WARNING_PRESIDIO}${RESET}"
                    echo ""
                    echo -n "${LANG_PRIVACY_PRESIDIO_REMOVE} "
                    read -r confirm
                    if [[ "$confirm" =~ ^[Yy]$ ]]; then
                        pip3 uninstall -y presidio-analyzer presidio-anonymizer
                        sed -i '' "s/PRESIDIO_ENABLED=.*/PRESIDIO_ENABLED=\"false\"/" "$CONFIG_FILE"
                        echo -e "${GREEN}✅ ${LANG_PRIVACY_PRESIDIO_REMOVED}${RESET}"
                    fi
                else
                    echo -e "\n${CYAN}Install Microsoft Presidio (350MB)?${RESET}"
                    echo -e "${DIM}Detects 50+ PII types (credit cards, emails, names, etc.)${RESET}"
                    echo -n "Install? (Y/n): "
                    read -r confirm
                    if [[ "$confirm" =~ ^[Yy]?$ ]]; then
                        echo "Installing Presidio..."
                        pip3 install --user presidio-analyzer presidio-anonymizer && {
                            python3 -m spacy download en_core_web_sm
                            python3 -m spacy download de_core_news_sm
                            sed -i '' "s/PRESIDIO_ENABLED=.*/PRESIDIO_ENABLED=\"true\"/" "$CONFIG_FILE"
                            echo -e "${GREEN}✅ Presidio installed successfully${RESET}"
                        } || {
                            echo -e "${RED}❌ Installation failed${RESET}"
                        }
                    fi
                fi
                sleep 2
                ;;

            3)  # Install/Remove Phi-3
                if command -v ollama &> /dev/null && ollama list | grep -q "phi3"; then
                    echo -e "\n${RED}${BOLD}${LANG_DELETE_WARNING_TITLE}${RESET}"
                    echo -e "${YELLOW}${LANG_DELETE_WARNING_SHARED}${RESET}"
                    echo -e "${DIM}${LANG_DELETE_WARNING_CHECK}${RESET}"
                    echo -e "${DIM}${LANG_DELETE_WARNING_PHI3}${RESET}"
                    echo ""
                    echo -n "${LANG_PRIVACY_PRESIDIO_REMOVE} "
                    read -r confirm
                    if [[ "$confirm" =~ ^[Yy]$ ]]; then
                        ollama rm phi3
                        sed -i '' "s/PHI3_ENABLED=.*/PHI3_ENABLED=\"false\"/" "$CONFIG_FILE"
                        sed -i '' "s/RESPONSE_MODE=.*/RESPONSE_MODE=\"template\"/" "$CONFIG_FILE"
                        echo -e "${GREEN}✅ ${LANG_PRIVACY_PHI3_REMOVED}${RESET}"
                    fi
                else
                    echo -e "\n${CYAN}Install Phi-3 for natural responses (2.3GB)?${RESET}"
                    echo -e "${DIM}Generates natural language responses for private data${RESET}"
                    echo -n "Install? (Y/n): "
                    read -r confirm
                    if [[ "$confirm" =~ ^[Yy]?$ ]]; then
                        # Install Ollama if needed
                        if ! command -v ollama &> /dev/null; then
                            echo "Installing Ollama..."
                            curl -fsSL https://ollama.ai/install.sh | sh
                        fi

                        echo "Downloading Phi-3 (2.3GB)..."
                        ollama pull phi3 && {
                            sed -i '' "s/PHI3_ENABLED=.*/PHI3_ENABLED=\"true\"/" "$CONFIG_FILE"
                            sed -i '' "s/RESPONSE_MODE=.*/RESPONSE_MODE=\"natural\"/" "$CONFIG_FILE"
                            echo -e "${GREEN}✅ Phi-3 installed successfully${RESET}"
                        } || {
                            echo -e "${RED}❌ Installation failed${RESET}"
                        }
                    fi
                fi
                sleep 2
                ;;

            4)  # Manage spaCy models
                echo -e "\n${CYAN}spaCy Language Models:${RESET}"
                echo ""
                echo "Installed models:"
                python3 -c "import spacy; [print(f'  • {m}') for m in spacy.util.get_installed_models()]" 2>/dev/null || echo "  None"
                echo ""
                echo "Available for installation:"
                echo "  [1] Spanish (es_core_news_sm)"
                echo "  [2] French (fr_core_news_sm)"
                echo "  [3] Italian (it_core_news_sm)"
                echo "  [4] Portuguese (pt_core_news_sm)"
                echo "  [5] Chinese (zh_core_web_sm)"
                echo "  [6] Japanese (ja_core_news_sm)"
                echo "  [0] Back"
                echo ""
                echo -n "Install model [0-6]: "
                read -r model_choice

                case "$model_choice" in
                    1) python3 -m spacy download es_core_news_sm && echo -e "${GREEN}✅ Spanish installed${RESET}" ;;
                    2) python3 -m spacy download fr_core_news_sm && echo -e "${GREEN}✅ French installed${RESET}" ;;
                    3) python3 -m spacy download it_core_news_sm && echo -e "${GREEN}✅ Italian installed${RESET}" ;;
                    4) python3 -m spacy download pt_core_news_sm && echo -e "${GREEN}✅ Portuguese installed${RESET}" ;;
                    5) python3 -m spacy download zh_core_web_sm && echo -e "${GREEN}✅ Chinese installed${RESET}" ;;
                    6) python3 -m spacy download ja_core_news_sm && echo -e "${GREEN}✅ Japanese installed${RESET}" ;;
                esac
                sleep 2
                ;;

            5)  # Toggle Response Mode
                if [[ "$RESPONSE_MODE" == "natural" ]]; then
                    sed -i '' "s/RESPONSE_MODE=.*/RESPONSE_MODE=\"template\"/" "$CONFIG_FILE"
                    echo -e "${GREEN}✅ Switched to template-based responses${RESET}"
                else
                    if [[ "$PHI3_ENABLED" == "true" ]]; then
                        sed -i '' "s/RESPONSE_MODE=.*/RESPONSE_MODE=\"natural\"/" "$CONFIG_FILE"
                        echo -e "${GREEN}✅ Switched to natural language responses${RESET}"
                    else
                        echo -e "${RED}❌ Phi-3 must be installed for natural responses${RESET}"
                    fi
                fi
                sleep 2
                ;;

            6)  # Back
                return
                ;;

            *)
                echo -e "${RED}Invalid option${RESET}"
                sleep 1
                ;;
        esac
    done
}