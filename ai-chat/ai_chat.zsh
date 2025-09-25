#!/usr/bin/env zsh

# AI Chat Terminal - Main Function
# Beautiful interactive AI chat with language support and game-style menu

ai_chat_function() {
    # Load configuration
    local CONFIG_DIR="$HOME/.config/ai-chat"
    local SCRIPT_DIR="${0:A:h}"

    # Default configuration
    local COMMAND_CHAR="${AI_CHAT_COMMAND:-q}"
    local LANGUAGE="${AI_CHAT_LANGUAGE:-en}"
    local TIMEOUT_SECONDS="${AI_CHAT_TIMEOUT:-120}"

    # Load language file
    local LANG_FILE="$SCRIPT_DIR/languages/${LANGUAGE}.conf"
    if [[ ! -f "$LANG_FILE" ]]; then
        LANG_FILE="$SCRIPT_DIR/languages/en.conf"  # Fallback to English
    fi
    source "$LANG_FILE"

    # Chat configuration
    local CHAT_NAME="${COMMAND_CHAR}_chat"
    local TIMEOUT_FILE="$CONFIG_DIR/chat_sessions/last_time"

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

    # Create directories if needed
    mkdir -p "$CONFIG_DIR/chat_sessions"

    # Get current timestamp
    local CURRENT_TIME=$(date +%s)

    # Check for existing session
    if [[ -f "$TIMEOUT_FILE" ]]; then
        local LAST_TIME=$(cat "$TIMEOUT_FILE")
        local TIME_DIFF=$((CURRENT_TIME - LAST_TIME))

        if [[ $TIME_DIFF -gt $TIMEOUT_SECONDS ]]; then
            rm -f "/tmp/chat_cache/${CHAT_NAME}.json" 2>/dev/null
            local SESSION_STATUS="${YELLOW}🔄 ${LANG_HEADER_NEW_CHAT}${RESET}"
        else
            local SESSION_STATUS="${GREEN}💬 ${LANG_HEADER_CONTINUE} (${TIME_DIFF}${LANG_STATUS_SECONDS})${RESET}"
        fi
    else
        rm -f "/tmp/chat_cache/${CHAT_NAME}.json" 2>/dev/null
        local SESSION_STATUS="${CYAN}🚀 ${LANG_HEADER_NEW_SESSION}${RESET}"
    fi

    # Single query mode
    if [[ $# -gt 0 ]]; then
        echo "$CURRENT_TIME" > "$TIMEOUT_FILE"

        # Show header
        echo -e "\n${BOLD}${PURPLE}╭─────────────────────────────────────╮${RESET}"
        echo -e "${BOLD}${PURPLE}│${RESET}  🤖 ${BOLD}AI Chat${RESET} ${SESSION_STATUS}  ${PURPLE}│${RESET}"
        echo -e "${BOLD}${PURPLE}╰─────────────────────────────────────╯${RESET}\n"

        # Show user input
        echo -e "${BLUE}👤 ${LANG_LABEL_YOU}:${RESET} $*\n"

        # Get and show response
        echo -e "${GREEN}🤖 ${LANG_LABEL_AI}:${RESET}"
        sgpt --chat "$CHAT_NAME" "$*"

        # Show hint
        local HINT="${LANG_HINT_INTERACTIVE//COMMAND_CHAR/$COMMAND_CHAR}"
        echo -e "\n${PURPLE}────────────────────────────────────${RESET}"
        echo -e "${CYAN}💡 ${HINT}${RESET}"
        echo -e "${PURPLE}────────────────────────────────────${RESET}\n"

        return
    fi

    # Interactive mode with game-style menu
    clear

    # Show splash screen
    echo -e "${BOLD}${CYAN}"
    echo "     ___   ____    _____ _           _   "
    echo "    / _ \\ |_ _|   / ____| |         | |  "
    echo "   / /_\\ \\ | |   | |    | |__   __ _| |_ "
    echo "   |  _  | | |   | |    | '_ \\ / _\` | __|"
    echo "   | | | |_| |_  | |____| | | | (_| | |_ "
    echo "   \\_| |_/\\___/  \\_____|_| |_|\\__,_|\\__|"
    echo -e "${RESET}"
    echo -e "${DIM}${CYAN}          Terminal Edition v2.0${RESET}\n"

    # Main menu
    echo -e "${BOLD}${PURPLE}╔══════════════════════════════════════════════╗${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}     🎮 ${BOLD}${CYAN}MAIN MENU${RESET}                           ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}     ${SESSION_STATUS}                    ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}╠══════════════════════════════════════════════╣${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}                                              ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}  ${GREEN}[1]${RESET} 💬 Start Chat                          ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}  ${GREEN}[2]${RESET} ⚙️  Settings                            ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}  ${GREEN}[3]${RESET} 🌍 Language: ${YELLOW}$LANGUAGE${RESET}                        ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}  ${GREEN}[4]${RESET} 📖 Help                                ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}  ${GREEN}[5]${RESET} 🚪 Exit                                ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}                                              ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}  ${DIM}Command: ${COMMAND_CHAR} | Timeout: ${TIMEOUT_SECONDS}s${RESET}            ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}                                              ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}╚══════════════════════════════════════════════╝${RESET}"
    echo ""

    # Read menu choice
    echo -ne "${CYAN}Select option [1-5]: ${RESET}"
    read -r MENU_CHOICE

    case $MENU_CHOICE in
        1)
            # Start chat
            clear
            echo -e "${BOLD}${PURPLE}╭═══════════════════════════════════════════╮${RESET}"
            echo -e "${BOLD}${PURPLE}║${RESET}     🤖 ${BOLD}${CYAN}${LANG_HEADER_TITLE}${RESET}             ${PURPLE}║${RESET}"
            echo -e "${BOLD}${PURPLE}║${RESET}     ${SESSION_STATUS}                    ${PURPLE}║${RESET}"
            echo -e "${BOLD}${PURPLE}╠═══════════════════════════════════════════╣${RESET}"
            echo -e "${BOLD}${PURPLE}║${RESET}  ${YELLOW}[Ctrl+C]${RESET} ${LANG_INST_EXIT}                   ${PURPLE}║${RESET}"
            echo -e "${BOLD}${PURPLE}║${RESET}  ${YELLOW}/menu${RESET} return to menu                    ${PURPLE}║${RESET}"
            echo -e "${BOLD}${PURPLE}║${RESET}  ${YELLOW}exit/quit/bye${RESET} ${LANG_INST_LEAVE}            ${PURPLE}║${RESET}"
            echo -e "${BOLD}${PURPLE}╰═══════════════════════════════════════════╯${RESET}\n"

            # Interactive chat loop
            while true; do
                echo "$CURRENT_TIME" > "$TIMEOUT_FILE"

                # Prompt
                echo -ne "${BLUE}👤 ${LANG_LABEL_YOU} ▶ ${RESET}"

                # Read input
                read -r INPUT

                # Skip empty input
                if [[ -z "$INPUT" ]]; then
                    continue
                fi

                # Special commands
                if [[ "$INPUT" == "/menu" ]]; then
                    # Return to menu
                    ai_chat_function
                    return
                fi

                if [[ "$INPUT" == "clear" ]] || [[ "$INPUT" == "cls" ]]; then
                    clear
                    echo -e "${BOLD}${PURPLE}╭═══════════════════════════════════════════╮${RESET}"
                    echo -e "${BOLD}${PURPLE}║${RESET}     🤖 ${BOLD}${CYAN}${LANG_HEADER_TITLE}${RESET}             ${PURPLE}║${RESET}"
                    echo -e "${BOLD}${PURPLE}╠═══════════════════════════════════════════╣${RESET}"
                    echo -e "${BOLD}${PURPLE}║${RESET}  ${YELLOW}[Ctrl+C]${RESET} ${LANG_INST_EXIT}                   ${PURPLE}║${RESET}"
                    echo -e "${BOLD}${PURPLE}║${RESET}  ${YELLOW}/menu${RESET} return to menu                    ${PURPLE}║${RESET}"
                    echo -e "${BOLD}${PURPLE}║${RESET}  ${YELLOW}exit/quit/bye${RESET} ${LANG_INST_LEAVE}            ${PURPLE}║${RESET}"
                    echo -e "${BOLD}${PURPLE}╰═══════════════════════════════════════════╯${RESET}\n"
                    continue
                fi

                if [[ "$INPUT" == "exit" ]] || [[ "$INPUT" == "quit" ]] || [[ "$INPUT" == "bye" ]]; then
                    echo -e "\n${YELLOW}👋 ${LANG_MSG_GOODBYE}${RESET}\n"
                    return
                fi

                # Process with sgpt
                echo -e "${GREEN}🤖 ${LANG_LABEL_AI} ▶ ${RESET}"
                sgpt --chat "$CHAT_NAME" "$INPUT"
                echo -e "${PURPLE}───────────────────────────────────────────${RESET}\n"

                # Update timestamp
                CURRENT_TIME=$(date +%s)
            done
            ;;

        2)
            # Settings menu
            ai_chat_settings_menu
            ai_chat_function  # Return to main menu
            ;;

        3)
            # Quick language toggle
            if [[ "$LANGUAGE" == "en" ]]; then
                echo "AI_CHAT_LANGUAGE=\"de\"" >> "$CONFIG_DIR/config"
                echo -e "${GREEN}✅ Language changed to German (Deutsch)${RESET}"
            else
                echo "AI_CHAT_LANGUAGE=\"en\"" >> "$CONFIG_DIR/config"
                echo -e "${GREEN}✅ Language changed to English${RESET}"
            fi
            echo -e "${YELLOW}Reload your shell: source ~/.zshrc${RESET}"
            sleep 2
            ai_chat_function  # Restart with new language
            ;;

        4)
            # Help screen
            clear
            echo -e "${BOLD}${CYAN}📖 HELP${RESET}\n"
            echo -e "${YELLOW}Commands:${RESET}"
            echo -e "  ${GREEN}${COMMAND_CHAR} <question>${RESET} - Quick question mode"
            echo -e "  ${GREEN}${COMMAND_CHAR}${RESET}           - Interactive chat menu"
            echo -e "  ${GREEN}ai-chat-config${RESET}  - Configuration tool"
            echo ""
            echo -e "${YELLOW}In Chat:${RESET}"
            echo -e "  ${GREEN}/menu${RESET}     - Return to main menu"
            echo -e "  ${GREEN}clear${RESET}     - Clear screen"
            echo -e "  ${GREEN}exit${RESET}      - Exit chat"
            echo -e "  ${GREEN}Ctrl+C${RESET}    - Force exit"
            echo ""
            echo -e "${YELLOW}Tips:${RESET}"
            echo -e "  • Context is maintained for ${TIMEOUT_SECONDS} seconds"
            echo -e "  • Use arrow keys to navigate history"
            echo -e "  • Create custom aliases for different uses"
            echo ""
            echo -e "${DIM}Press Enter to continue...${RESET}"
            read
            ai_chat_function  # Return to menu
            ;;

        5|"")
            # Exit
            echo -e "\n${YELLOW}👋 Goodbye!${RESET}\n"
            return
            ;;

        *)
            echo -e "${RED}Invalid option!${RESET}"
            sleep 1
            ai_chat_function  # Return to menu
            ;;
    esac
}

# Settings submenu
ai_chat_settings_menu() {
    local CONFIG_DIR="$HOME/.config/ai-chat"
    local CONFIG_FILE="$CONFIG_DIR/config"

    clear
    echo -e "${BOLD}${CYAN}"
    echo "     ⚙️  SETTINGS"
    echo -e "${RESET}"

    echo -e "${BOLD}${PURPLE}╔══════════════════════════════════════════════╗${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}     🎮 ${BOLD}${CYAN}CONFIGURATION${RESET}                       ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}╠══════════════════════════════════════════════╣${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}                                              ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}  Current Settings:                          ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}  ├─ Command: ${YELLOW}${AI_CHAT_COMMAND:-q}${RESET}                           ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}  ├─ Language: ${YELLOW}${AI_CHAT_LANGUAGE:-en}${RESET}                         ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}  └─ Timeout: ${YELLOW}${AI_CHAT_TIMEOUT:-120}s${RESET}                        ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}                                              ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}  ${GREEN}[1]${RESET} Change command character               ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}  ${GREEN}[2]${RESET} Change language                        ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}  ${GREEN}[3]${RESET} Change timeout                         ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}  ${GREEN}[4]${RESET} Change AI model                        ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}  ${GREEN}[5]${RESET} Reset to defaults                      ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}  ${GREEN}[6]${RESET} Back to main menu                      ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}                                              ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}╚══════════════════════════════════════════════╝${RESET}"
    echo ""

    echo -ne "${CYAN}Select option [1-6]: ${RESET}"
    read -r choice

    case $choice in
        1)
            echo -ne "${CYAN}Enter new command character: ${RESET}"
            read -r cmd
            if [[ ! -z "$cmd" ]]; then
                echo "AI_CHAT_COMMAND=\"$cmd\"" > "$CONFIG_FILE"
                echo -e "${GREEN}✅ Command changed to: $cmd${RESET}"
                echo -e "${YELLOW}Reload shell to apply: source ~/.zshrc${RESET}"
                sleep 2
            fi
            ;;
        2)
            echo -e "${CYAN}Available languages:${RESET}"
            echo "  en - English"
            echo "  de - German"
            echo -ne "${CYAN}Enter language code: ${RESET}"
            read -r lang
            if [[ "$lang" == "en" ]] || [[ "$lang" == "de" ]]; then
                echo "AI_CHAT_LANGUAGE=\"$lang\"" >> "$CONFIG_FILE"
                echo -e "${GREEN}✅ Language changed to: $lang${RESET}"
                sleep 2
            fi
            ;;
        3)
            echo -ne "${CYAN}Enter timeout in seconds: ${RESET}"
            read -r timeout
            if [[ "$timeout" =~ ^[0-9]+$ ]]; then
                echo "AI_CHAT_TIMEOUT=\"$timeout\"" >> "$CONFIG_FILE"
                echo -e "${GREEN}✅ Timeout changed to: ${timeout}s${RESET}"
                sleep 2
            fi
            ;;
        4)
            echo -e "${CYAN}Available models:${RESET}"
            echo "  1) gpt-4o-mini (fast, cheap)"
            echo "  2) gpt-4o (powerful)"
            echo "  3) gpt-3.5-turbo (legacy)"
            echo -ne "${CYAN}Select model [1-3]: ${RESET}"
            read -r model_choice
            case $model_choice in
                1) model="gpt-4o-mini" ;;
                2) model="gpt-4o" ;;
                3) model="gpt-3.5-turbo" ;;
                *) model="" ;;
            esac
            if [[ ! -z "$model" ]]; then
                # Update sgpt config
                sed -i '' "s/DEFAULT_MODEL=.*/DEFAULT_MODEL=$model/" ~/.config/shell_gpt/.sgptrc
                echo -e "${GREEN}✅ Model changed to: $model${RESET}"
                sleep 2
            fi
            ;;
        5)
            rm -f "$CONFIG_FILE"
            echo -e "${GREEN}✅ Reset to defaults${RESET}"
            sleep 2
            ;;
        6)
            return
            ;;
        *)
            echo -e "${RED}Invalid option${RESET}"
            sleep 1
            ;;
    esac

    ai_chat_settings_menu  # Show menu again
}

# Legacy config function for compatibility
ai_chat_config() {
    ai_chat_settings_menu
}