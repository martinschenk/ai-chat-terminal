#!/usr/bin/env zsh
# AI Chat Terminal - Ultra Simple Version
# Version: 3.1.0
# Instant chat with memory and inline configuration

ai_chat_function() {
    # Check for API key first
    if [[ -z "$OPENAI_API_KEY" ]]; then
        echo ""
        echo -e "\033[1;33m⚠️  No OpenAI API Key found!\033[0m"
        echo ""
        echo -e "\033[0;36mTo use this chat, you need an API key from OpenAI.\033[0m"
        echo ""
        echo -e "\033[1mHow to get your API key:\033[0m"
        echo -e "  1. Go to: \033[0;34mhttps://platform.openai.com/api-keys\033[0m"
        echo -e "  2. Sign up or log in"
        echo -e "  3. Click 'Create new secret key'"
        echo -e "  4. Copy the key (starts with sk-...)"
        echo ""
        echo -e "\033[1mHow to set it:\033[0m"
        echo -e "  Add this to your ~/.zshrc or ~/.bashrc:"
        echo -e "  \033[0;32mexport OPENAI_API_KEY=\"sk-your-key-here\"\033[0m"
        echo ""
        echo -e "  Then reload:"
        echo -e "  \033[0;32msource ~/.zshrc\033[0m"
        echo ""
        echo -ne "\033[0;36mEnter your API key now (or press Enter to exit): \033[0m"
        read -r api_key

        if [[ ! -z "$api_key" ]]; then
            export OPENAI_API_KEY="$api_key"

            # Detect shell config
            local SHELL_CONFIG=""
            if [[ -f "$HOME/.zshrc" ]]; then
                SHELL_CONFIG="$HOME/.zshrc"
            elif [[ -f "$HOME/.bashrc" ]]; then
                SHELL_CONFIG="$HOME/.bashrc"
            else
                SHELL_CONFIG="$HOME/.profile"
            fi

            echo "" >> "$SHELL_CONFIG"
            echo "export OPENAI_API_KEY=\"$api_key\"" >> "$SHELL_CONFIG"
            echo -e "\033[0;32m✅ API key saved to $SHELL_CONFIG\033[0m"
            echo -e "\033[0;32m✅ You can now start chatting!\033[0m"
            echo ""
            sleep 2
        else
            echo -e "\033[0;31mExiting. Please set your API key and try again.\033[0m"
            return 1
        fi
    fi
    # Load configuration
    local CONFIG_DIR="$HOME/.config/ai-chat"
    local CONFIG_FILE="$CONFIG_DIR/config"
    local SCRIPT_DIR="${0:A:h}"

    # Create config dir if needed
    mkdir -p "$CONFIG_DIR"

    # Load user config if exists
    if [[ -f "$CONFIG_FILE" ]]; then
        source "$CONFIG_FILE"
    fi

    # Defaults
    local COMMAND_CHAR="${AI_CHAT_COMMAND:-q}"
    local LANGUAGE="${AI_CHAT_LANGUAGE:-en}"
    local TIMEOUT_SECONDS="${AI_CHAT_TIMEOUT:-120}"
    local ENABLE_ESC="${AI_CHAT_ESC_EXIT:-true}"

    # Load language file
    local LANG_FILE="$SCRIPT_DIR/languages/${LANGUAGE}.conf"
    if [[ ! -f "$LANG_FILE" ]]; then
        # Fallback to embedded English
        LANG_LABEL_YOU="You"
        LANG_LABEL_AI="AI"
        LANG_MSG_GOODBYE="Goodbye!"
        LANG_HEADER_CONTINUE="Continue"
        LANG_STATUS_SECONDS="s"
    else
        source "$LANG_FILE"
    fi

    # Chat configuration
    local CHAT_NAME="${COMMAND_CHAR}_chat"
    local TIMEOUT_FILE="$CONFIG_DIR/last_time"

    # Colors
    local BLUE='\033[0;34m'
    local GREEN='\033[0;32m'
    local YELLOW='\033[1;33m'
    local PURPLE='\033[0;35m'
    local CYAN='\033[0;36m'
    local RED='\033[0;31m'
    local RESET='\033[0m'
    local BOLD='\033[1m'
    local DIM='\033[2m'

    # Check session status
    local CURRENT_TIME=$(date +%s)
    local SESSION_STATUS=""

    if [[ -f "$TIMEOUT_FILE" ]]; then
        local LAST_TIME=$(cat "$TIMEOUT_FILE")
        local TIME_DIFF=$((CURRENT_TIME - LAST_TIME))

        if [[ $TIME_DIFF -gt $TIMEOUT_SECONDS ]]; then
            rm -f "/tmp/chat_cache/${CHAT_NAME}.json" 2>/dev/null
            SESSION_STATUS=""
        else
            SESSION_STATUS="${DIM}[${LANG_HEADER_CONTINUE} ${TIME_DIFF}${LANG_STATUS_SECONDS}]${RESET}"
        fi
    else
        rm -f "/tmp/chat_cache/${CHAT_NAME}.json" 2>/dev/null
    fi

    # Update timestamp
    echo "$CURRENT_TIME" > "$TIMEOUT_FILE"

    # Handle direct questions (q "question here")
    if [[ $# -gt 0 ]]; then
        # Special commands
        if [[ "$1" == "--config" ]] || [[ "$1" == "-c" ]]; then
            show_config_menu
            return
        fi

        # Direct question mode - show answer immediately
        echo -e "\n${DIM}╭─────────────────────────────────────────────────────╮${RESET}"
        echo -e "${DIM}│ ${CYAN}/config${RESET}${DIM} settings │ ${YELLOW}ESC${RESET}${DIM} or ${YELLOW}exit${RESET}${DIM} to quit │ ${SESSION_STATUS} ${DIM}│${RESET}"
        echo -e "${DIM}╰─────────────────────────────────────────────────────╯${RESET}\n"

        echo -e "${BLUE}👤 ${LANG_LABEL_YOU}:${RESET} $*\n"
        echo -e "${GREEN}🤖 ${LANG_LABEL_AI}:${RESET}"
        sgpt --chat "$CHAT_NAME" "$*"
        echo -e "\n${DIM}─────────────────────────────────────────────────────${RESET}\n"

        # Continue in chat mode
        chat_loop
        return
    fi

    # Instant chat mode (just 'q' entered)
    clear
    echo -e "${DIM}╭─────────────────────────────────────────────────────╮${RESET}"
    echo -e "${DIM}│ ${CYAN}/config${RESET}${DIM} settings │ ${YELLOW}ESC${RESET}${DIM} or ${YELLOW}exit${RESET}${DIM} to quit │ ${SESSION_STATUS} ${DIM}│${RESET}"
    echo -e "${DIM}╰─────────────────────────────────────────────────────╯${RESET}\n"

    chat_loop
}

# Main chat loop
chat_loop() {
    local CONFIG_DIR="$HOME/.config/ai-chat"
    local CONFIG_FILE="$CONFIG_DIR/config"
    local TIMEOUT_FILE="$CONFIG_DIR/last_time"

    # Reload config for current values
    if [[ -f "$CONFIG_FILE" ]]; then
        source "$CONFIG_FILE"
    fi

    local COMMAND_CHAR="${AI_CHAT_COMMAND:-q}"
    local LANGUAGE="${AI_CHAT_LANGUAGE:-en}"
    local ENABLE_ESC="${AI_CHAT_ESC_EXIT:-true}"
    local CHAT_NAME="${COMMAND_CHAR}_chat"

    # Colors
    local BLUE='\033[0;34m'
    local GREEN='\033[0;32m'
    local YELLOW='\033[1;33m'
    local PURPLE='\033[0;35m'
    local CYAN='\033[0;36m'
    local RESET='\033[0m'
    local DIM='\033[2m'

    while true; do
        # Update timestamp
        echo "$(date +%s)" > "$TIMEOUT_FILE"

        # Prompt
        echo -ne "${BLUE}👤 ${LANG_LABEL_YOU} ▶ ${RESET}"

        # Read input - with or without ESC support
        local INPUT=""
        if [[ "$ENABLE_ESC" == "true" ]]; then
            # Read char by char for ESC detection
            while IFS= read -r -s -k 1 char; do
                if [[ $char == $'\e' ]]; then
                    # ESC pressed
                    echo -e "\n\n${YELLOW}👋 ${LANG_MSG_GOODBYE}${RESET}\n"
                    return
                elif [[ $char == "" ]]; then
                    # Enter pressed
                    break
                elif [[ $char == $'\177' ]] || [[ $char == $'\b' ]]; then
                    # Backspace
                    if [[ -n "$INPUT" ]]; then
                        INPUT="${INPUT%?}"
                        echo -ne "\b \b"
                    fi
                else
                    # Normal character
                    INPUT="${INPUT}${char}"
                    echo -n "$char"
                fi
            done
            echo # New line after input
        else
            # Simple read without ESC
            read -r INPUT
        fi

        # Skip empty input
        [[ -z "$INPUT" ]] && continue

        # Handle commands
        case "$INPUT" in
            /config|/settings|/menu)
                show_config_menu
                # After config, show header again
                clear
                echo -e "${DIM}╭─────────────────────────────────────────────────────╮${RESET}"
                echo -e "${DIM}│ ${CYAN}/config${RESET}${DIM} settings │ ${YELLOW}ESC${RESET}${DIM} or ${YELLOW}exit${RESET}${DIM} to quit │         ${DIM}│${RESET}"
                echo -e "${DIM}╰─────────────────────────────────────────────────────╯${RESET}\n"
                continue
                ;;

            clear|cls)
                clear
                echo -e "${DIM}╭─────────────────────────────────────────────────────╮${RESET}"
                echo -e "${DIM}│ ${CYAN}/config${RESET}${DIM} settings │ ${YELLOW}ESC${RESET}${DIM} or ${YELLOW}exit${RESET}${DIM} to quit │         ${DIM}│${RESET}"
                echo -e "${DIM}╰─────────────────────────────────────────────────────╯${RESET}\n"
                continue
                ;;

            exit|quit|bye|/exit|/quit)
                echo -e "\n${YELLOW}👋 ${LANG_MSG_GOODBYE}${RESET}\n"
                return
                ;;
        esac

        # Process with AI
        echo -e "${GREEN}🤖 ${LANG_LABEL_AI} ▶ ${RESET}"
        sgpt --chat "$CHAT_NAME" "$INPUT"
        echo -e "${DIM}─────────────────────────────────────────────────────${RESET}\n"
    done
}

# Configuration menu (game-style)
show_config_menu() {
    local CONFIG_DIR="$HOME/.config/ai-chat"
    local CONFIG_FILE="$CONFIG_DIR/config"

    # Load current config
    if [[ -f "$CONFIG_FILE" ]]; then
        source "$CONFIG_FILE"
    fi

    local COMMAND_CHAR="${AI_CHAT_COMMAND:-q}"
    local LANGUAGE="${AI_CHAT_LANGUAGE:-en}"
    local TIMEOUT="${AI_CHAT_TIMEOUT:-120}"
    local ENABLE_ESC="${AI_CHAT_ESC_EXIT:-true}"

    # Colors
    local CYAN='\033[0;36m'
    local GREEN='\033[0;32m'
    local YELLOW='\033[1;33m'
    local PURPLE='\033[0;35m'
    local RED='\033[0;31m'
    local RESET='\033[0m'
    local BOLD='\033[1m'

    clear
    echo -e "${BOLD}${CYAN}⚙️  CONFIGURATION${RESET}\n"

    echo -e "${PURPLE}╔═══════════════════════════════════════╗${RESET}"
    echo -e "${PURPLE}║${RESET}  Current Settings:                   ${PURPLE}║${RESET}"
    echo -e "${PURPLE}║${RESET}  ├─ Command: ${YELLOW}$COMMAND_CHAR${RESET}                      ${PURPLE}║${RESET}"
    echo -e "${PURPLE}║${RESET}  ├─ Language: ${YELLOW}$LANGUAGE${RESET}                    ${PURPLE}║${RESET}"
    echo -e "${PURPLE}║${RESET}  ├─ Timeout: ${YELLOW}${TIMEOUT}s${RESET}                  ${PURPLE}║${RESET}"
    echo -e "${PURPLE}║${RESET}  └─ ESC to exit: ${YELLOW}$ENABLE_ESC${RESET}             ${PURPLE}║${RESET}"
    echo -e "${PURPLE}╠═══════════════════════════════════════╣${RESET}"
    echo -e "${PURPLE}║${RESET}  ${GREEN}[1]${RESET} Change command character        ${PURPLE}║${RESET}"
    echo -e "${PURPLE}║${RESET}  ${GREEN}[2]${RESET} Change language                 ${PURPLE}║${RESET}"
    echo -e "${PURPLE}║${RESET}  ${GREEN}[3]${RESET} Change timeout                  ${PURPLE}║${RESET}"
    echo -e "${PURPLE}║${RESET}  ${GREEN}[4]${RESET} Toggle ESC key exit             ${PURPLE}║${RESET}"
    echo -e "${PURPLE}║${RESET}  ${GREEN}[5]${RESET} Change AI model                 ${PURPLE}║${RESET}"
    echo -e "${PURPLE}║${RESET}  ${GREEN}[6]${RESET} Back to chat                    ${PURPLE}║${RESET}"
    echo -e "${PURPLE}║${RESET}                                       ${PURPLE}║${RESET}"
    echo -e "${PURPLE}║${RESET}  ${RED}[9]${RESET} 🗑️  Uninstall completely         ${PURPLE}║${RESET}"
    echo -e "${PURPLE}╚═══════════════════════════════════════╝${RESET}"
    echo ""

    echo -ne "${CYAN}Select [1-6,9]: ${RESET}"
    read -r choice

    case $choice in
        1)
            echo -ne "${CYAN}Enter new command (current: $COMMAND_CHAR): ${RESET}"
            read -r new_cmd
            if [[ ! -z "$new_cmd" ]]; then
                echo "AI_CHAT_COMMAND=\"$new_cmd\"" > "$CONFIG_FILE"
                echo "AI_CHAT_LANGUAGE=\"$LANGUAGE\"" >> "$CONFIG_FILE"
                echo "AI_CHAT_TIMEOUT=\"$TIMEOUT\"" >> "$CONFIG_FILE"
                echo "AI_CHAT_ESC_EXIT=\"$ENABLE_ESC\"" >> "$CONFIG_FILE"
                echo -e "${GREEN}✅ Command changed to: $new_cmd${RESET}"
                echo -e "${YELLOW}Restart shell to apply${RESET}"
                sleep 2
            fi
            ;;

        2)
            echo -e "${CYAN}Languages:${RESET}"
            echo "  en - English"
            echo "  de - German"
            echo -ne "${CYAN}Enter code: ${RESET}"
            read -r new_lang
            if [[ "$new_lang" == "en" ]] || [[ "$new_lang" == "de" ]]; then
                echo "AI_CHAT_COMMAND=\"$COMMAND_CHAR\"" > "$CONFIG_FILE"
                echo "AI_CHAT_LANGUAGE=\"$new_lang\"" >> "$CONFIG_FILE"
                echo "AI_CHAT_TIMEOUT=\"$TIMEOUT\"" >> "$CONFIG_FILE"
                echo "AI_CHAT_ESC_EXIT=\"$ENABLE_ESC\"" >> "$CONFIG_FILE"
                echo -e "${GREEN}✅ Language: $new_lang${RESET}"
                sleep 2
            fi
            ;;

        3)
            echo -ne "${CYAN}Timeout in seconds (current: $TIMEOUT): ${RESET}"
            read -r new_timeout
            if [[ "$new_timeout" =~ ^[0-9]+$ ]]; then
                echo "AI_CHAT_COMMAND=\"$COMMAND_CHAR\"" > "$CONFIG_FILE"
                echo "AI_CHAT_LANGUAGE=\"$LANGUAGE\"" >> "$CONFIG_FILE"
                echo "AI_CHAT_TIMEOUT=\"$new_timeout\"" >> "$CONFIG_FILE"
                echo "AI_CHAT_ESC_EXIT=\"$ENABLE_ESC\"" >> "$CONFIG_FILE"
                echo -e "${GREEN}✅ Timeout: ${new_timeout}s${RESET}"
                sleep 2
            fi
            ;;

        4)
            if [[ "$ENABLE_ESC" == "true" ]]; then
                new_esc="false"
            else
                new_esc="true"
            fi
            echo "AI_CHAT_COMMAND=\"$COMMAND_CHAR\"" > "$CONFIG_FILE"
            echo "AI_CHAT_LANGUAGE=\"$LANGUAGE\"" >> "$CONFIG_FILE"
            echo "AI_CHAT_TIMEOUT=\"$TIMEOUT\"" >> "$CONFIG_FILE"
            echo "AI_CHAT_ESC_EXIT=\"$new_esc\"" >> "$CONFIG_FILE"
            echo -e "${GREEN}✅ ESC to exit: $new_esc${RESET}"
            sleep 2
            ;;

        5)
            echo -e "${CYAN}AI Models:${RESET}"
            echo "  1) gpt-4o-mini (fast)"
            echo "  2) gpt-4o (powerful)"
            echo "  3) gpt-3.5-turbo"
            echo -ne "${CYAN}Select [1-3]: ${RESET}"
            read -r model_choice

            case $model_choice in
                1) model="gpt-4o-mini" ;;
                2) model="gpt-4o" ;;
                3) model="gpt-3.5-turbo" ;;
                *) model="" ;;
            esac

            if [[ ! -z "$model" ]]; then
                # Update sgpt config
                if [[ -f ~/.config/shell_gpt/.sgptrc ]]; then
                    sed -i '' "s/DEFAULT_MODEL=.*/DEFAULT_MODEL=$model/" ~/.config/shell_gpt/.sgptrc 2>/dev/null || \
                    sed -i "s/DEFAULT_MODEL=.*/DEFAULT_MODEL=$model/" ~/.config/shell_gpt/.sgptrc
                fi
                echo -e "${GREEN}✅ Model: $model${RESET}"
                sleep 2
            fi
            ;;

        9)
            # Uninstaller
            clear
            echo -e "${RED}${BOLD}⚠️  UNINSTALL AI CHAT TERMINAL${RESET}"
            echo ""
            echo "This will remove:"
            echo "  • AI Chat Terminal from your shell config"
            echo "  • Installation directory: ~/shell-scripts"
            echo "  • Configuration: ~/.config/ai-chat"
            echo ""
            echo -e "${YELLOW}This action cannot be undone!${RESET}"
            echo ""
            echo "Type DELETE to confirm uninstallation:"
            echo -n "> "
            local confirm
            read confirm

            if [[ "$confirm" == "DELETE" ]]; then
                echo ""
                echo "Uninstalling AI Chat Terminal..."

                # Remove from shell configs
                local configs=("$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.profile")
                for config in "${configs[@]}"; do
                    if [[ -f "$config" ]]; then
                        # Remove source line
                        grep -v "source.*shell-scripts/chat.zsh" "$config" > "$config.tmp" && mv "$config.tmp" "$config"
                        # Remove alias line
                        grep -v "alias ${COMMAND_CHAR}=" "$config" > "$config.tmp" && mv "$config.tmp" "$config"
                        echo "  ✓ Cleaned $config"
                    fi
                done

                # Remove directories
                if [[ -d "$HOME/shell-scripts" ]]; then
                    rm -rf "$HOME/shell-scripts"
                    echo "  ✓ Removed ~/shell-scripts"
                fi

                if [[ -d "$HOME/.config/ai-chat" ]]; then
                    rm -rf "$HOME/.config/ai-chat"
                    echo "  ✓ Removed ~/.config/ai-chat"
                fi

                echo ""
                echo -e "${GREEN}✓ AI Chat Terminal has been uninstalled${RESET}"
                echo ""
                echo "Please restart your terminal or run:"
                echo "  source ~/.zshrc  (or ~/.bashrc)"
                echo ""
                echo "Goodbye! 👋"
                echo ""
                echo "Press any key to exit..."
                read -k 1 -s
                exit 0
            else
                echo ""
                echo -e "${GREEN}✓ Uninstall cancelled${RESET}"
                echo "Press any key to return to config..."
                read -k 1 -s
            fi
            ;;

        6|*)
            return
            ;;
    esac

    # Show menu again unless going back
    if [[ "$choice" != "6" ]]; then
        show_config_menu
    fi
}