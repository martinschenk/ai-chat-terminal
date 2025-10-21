#!/bin/zsh
# AI Chat Terminal - Additional Functions
# Part 2 of chat.zsh

# Start daemons (Chat + Ollama)
start_daemons() {
    local SCRIPT_DIR="${1:-$HOME/.aichat}"
    # Start both daemons using daemon_manager
    python3 "$SCRIPT_DIR/daemon_manager.py" start 2>&1
}

# Stop daemons (Chat + Ollama if managed mode)
stop_daemons() {
    local SCRIPT_DIR="${1:-$HOME/.aichat}"
    # Stop both daemons
    python3 "$SCRIPT_DIR/daemon_manager.py" stop 2>&1
}

# Send message via daemon
send_message_via_daemon() {
    local SCRIPT_DIR="$1"
    local CHAT_NAME="$2"
    local INPUT="$3"
    local SYSTEM_PROMPT="$4"
    # Use daemon_manager to send message
    python3 "$SCRIPT_DIR/daemon_manager.py" message "$CHAT_NAME" "$INPUT" "$SYSTEM_PROMPT" 2>&1
}

# Main chat loop
chat_loop() {
    local CONFIG_DIR="$HOME/.aichat"
    local CONFIG_FILE="$CONFIG_DIR/config"
    local TIMEOUT_FILE="$CONFIG_DIR/last_time"

    # Reload config for current values
    if [[ -f "$CONFIG_FILE" ]]; then
        source "$CONFIG_FILE"
    fi

    local COMMAND_CHAR="${AI_CHAT_COMMAND:-ai}"
    local LANGUAGE="${AI_CHAT_LANGUAGE:-en}"
    local ENABLE_ESC="${AI_CHAT_ESC_EXIT:-true}"
    local CONTEXT_WINDOW="${AI_CHAT_CONTEXT_WINDOW:-20}"
    # Use global SCRIPT_DIR from main script

    # Load language file for chat
    local LANG_FILE="$SCRIPT_DIR/lang/${LANGUAGE}.conf"
    if [[ ! -f "$LANG_FILE" ]]; then
        setup_default_language
    else
        source "$LANG_FILE"
    fi

    # Professional IDE colors - labels colored, text white (like ChatGPT/Claude)
    local USER_COLOR='\033[38;5;75m'     # Bright blue (#61AFEF) - for 👤 Du ▶
    local AI_COLOR='\033[38;5;114m'      # Green (#98C379) - for 🤖 KI ▶
    local COMMAND_COLOR='\033[38;5;204m' # Coral (#E06C75) - for /config commands
    local WHITE='\033[97m'               # Bright white for text content
    local YELLOW='\033[1;33m'
    local RESET='\033[0m'
    local DIM='\033[2m'

    local INPUT=""

    # Memory system is now integrated directly in chat_system.py

    # Context window management is now handled in Python chat_system.py

    # v11.1.0: Arrow key history navigation (RAM only - current chat session)
    local HISTORY_ITEMS=()      # Stores user prompts during this chat
    local HISTORY_INDEX=-1      # -1 = not in history mode
    local CURRENT_INPUT=""      # Buffer for user's current typing before history navigation

    # Start daemons (Chat + Ollama) - ONCE at chat start
    echo -ne "${DIM}🚀 Starting chat system...${RESET}"
    start_daemons "$SCRIPT_DIR" >/dev/null
    printf "\r                              \r"  # Clear loading message

    # Trap EXIT to stop daemons when chat ends
    trap "stop_daemons '$SCRIPT_DIR' >/dev/null 2>&1" EXIT INT TERM

    while true; do
        echo -ne "${USER_COLOR}👤 ${LANG_LABEL_YOU} ▶ ${RESET}"

        # Handle ESC key detection + Arrow keys (v11.1.0)
        if [[ "$ENABLE_ESC" == "true" ]] && [[ -t 0 ]]; then
            # Save current terminal settings
            OLD_STTY=$(stty -g)
            stty raw -echo min 1 time 0 2>/dev/null

            INPUT=""
            while true; do
                char=$(dd bs=1 count=1 2>/dev/null)

                if [[ $char == $'\e' ]]; then
                    # Could be ESC key OR start of arrow key sequence
                    # Wait 0.01s to see if more bytes follow
                    next_chars=""
                    read -t 0.01 -k 2 next_chars 2>/dev/null || true

                    if [[ -z "$next_chars" ]] || [[ ${#next_chars} -eq 0 ]]; then
                        # Pure ESC (no following bytes) - EXIT
                        stty "$OLD_STTY" 2>/dev/null
                        echo -e "\n\n${YELLOW}👋 ${LANG_MSG_GOODBYE}${RESET}\n"
                        # v11.6.0: Delete chat history on exit (Privacy First!)
                        python3 -c "import sys; sys.path.insert(0, '$SCRIPT_DIR'); from daemon_manager import DaemonManager; DaemonManager().cleanup_chat_history()" 2>/dev/null
                        return
                    elif [[ "$next_chars" == "[A" ]]; then
                        # UP ARROW - navigate to older message
                        if [[ ${#HISTORY_ITEMS[@]} -gt 0 ]]; then
                            # Save current input if not in history mode yet
                            if [[ $HISTORY_INDEX -eq -1 ]]; then
                                CURRENT_INPUT="$INPUT"
                            fi

                            # Move up in history (towards older messages)
                            if [[ $HISTORY_INDEX -lt $((${#HISTORY_ITEMS[@]} - 1)) ]]; then
                                HISTORY_INDEX=$((HISTORY_INDEX + 1))
                                # Clear line and show history item
                                printf '\r\033[K'  # Clear entire line
                                echo -ne "${USER_COLOR}👤 ${LANG_LABEL_YOU} ▶ ${RESET}"
                                INPUT="${HISTORY_ITEMS[-$((HISTORY_INDEX + 1))]}"
                                printf '%s' "$INPUT"
                            fi
                        fi
                    elif [[ "$next_chars" == "[B" ]]; then
                        # DOWN ARROW - navigate to newer message
                        if [[ $HISTORY_INDEX -gt -1 ]]; then
                            HISTORY_INDEX=$((HISTORY_INDEX - 1))
                            # Clear line and show item
                            printf '\r\033[K'  # Clear entire line
                            echo -ne "${USER_COLOR}👤 ${LANG_LABEL_YOU} ▶ ${RESET}"

                            if [[ $HISTORY_INDEX -eq -1 ]]; then
                                # Back to current input (what user was typing before history)
                                INPUT="$CURRENT_INPUT"
                            else
                                INPUT="${HISTORY_ITEMS[-$((HISTORY_INDEX + 1))]}"
                            fi
                            printf '%s' "$INPUT"
                        fi
                    else
                        # Unknown escape sequence (could be left/right arrow, etc.) - ignore for now
                        continue
                    fi
                elif [[ $char == $'\r' ]] || [[ $char == $'\n' ]]; then
                    # Enter pressed
                    stty "$OLD_STTY" 2>/dev/null
                    echo
                    HISTORY_INDEX=-1  # Reset history state
                    break
                elif [[ $char == $'\177' ]] || [[ $char == $'\b' ]]; then
                    # Backspace
                    if [[ -n "$INPUT" ]]; then
                        INPUT="${INPUT%?}"
                        echo -ne "\b \b"
                    fi
                    HISTORY_INDEX=-1  # Exit history mode when user edits
                else
                    # Normal character
                    INPUT="${INPUT}${char}"
                    printf '%s' "$char"  # Use printf instead of echo for safety
                    HISTORY_INDEX=-1  # Exit history mode when user types new char
                fi
            done
        else
            # Simple read without ESC
            read -r INPUT
        fi

        # Skip empty input
        [[ -z "$INPUT" ]] && continue

        # Handle export-db command (v8.1.0)
        if [[ "$INPUT" =~ ^--export-db[[:space:]]+ ]]; then
            local EXPORT_PATH="${INPUT#--export-db }"
            EXPORT_PATH="${EXPORT_PATH// /}"  # Remove spaces

            if [[ -z "$EXPORT_PATH" ]]; then
                echo -e "${YELLOW}Usage: --export-db <output-file>${RESET}"
                echo -e "${DIM}Example: --export-db ~/Desktop/backup.db${RESET}"
                continue
            fi

            # Expand ~ to home directory
            EXPORT_PATH="${EXPORT_PATH/#\~/$HOME}"

            echo -e "${COMMAND_COLOR}📤 Exporting encrypted database...${RESET}"

            # Get encryption key and export
            python3 "$SCRIPT_DIR/db_migration.py" export \
                "$CONFIG_DIR/memory.db" \
                "$EXPORT_PATH" \
                "$(python3 -c 'from encryption_manager import EncryptionManager; m = EncryptionManager(); print(m.get_key_from_keychain() or "")')" \
                2>&1

            if [[ $? -eq 0 ]]; then
                echo -e "${GREEN}✓ Exported to: ${EXPORT_PATH}${RESET}"
                echo -e "${YELLOW}⚠️  WARNING: ${EXPORT_PATH} is NOT encrypted!${RESET}"
            else
                echo -e "${YELLOW}✗ Export failed${RESET}"
            fi
            continue
        fi

        # Handle commands
        case "$INPUT" in
            /help|/?)
                # v11.1.0: Show help screen
                echo -e "\n${COMMAND_COLOR}${LANG_HELP_TITLE:-📖 AI Chat Terminal - Quick Help}${RESET}\n"
                echo -e "${BOLD}${LANG_HELP_COMMANDS:-Commands:}${RESET}"
                echo -e "  ${GREEN}/config${RESET} - ${LANG_HELP_CONFIG:-Open settings menu}"
                echo -e "  ${GREEN}clear${RESET}   - ${LANG_HELP_CLEAR:-Clear screen}"
                echo -e "  ${GREEN}exit${RESET}    - ${LANG_HELP_EXIT:-Quit chat}"
                echo ""
                echo -e "${BOLD}${LANG_HELP_KEYS:-Keyboard Shortcuts:}${RESET}"
                echo -e "  ${DIM}↑${RESET}  - ${LANG_HELP_ARROW_UP:-Previous message}"
                echo -e "  ${DIM}↓${RESET}  - ${LANG_HELP_ARROW_DOWN:-Next message}"
                echo -e "  ${YELLOW}ESC${RESET} - ${LANG_HELP_ESC:-Quick exit}"
                echo ""
                echo -e "${BOLD}${LANG_HELP_DATABASE:-Database Operations:}${RESET}"
                echo -e "  • ${LANG_HELP_SAVE:-save my X - Store data locally}"
                echo -e "  • ${LANG_HELP_SHOW:-show my X - Retrieve data}"
                echo -e "  • ${LANG_HELP_DELETE:-delete my X - Remove data}"
                echo -e "  • ${LANG_HELP_LIST:-list all - Show all data}"
                echo ""
                echo -e "${BOLD}${LANG_HELP_EXAMPLES:-Examples:}${RESET}"
                echo -e "  ${DIM}${LANG_HELP_EX1:-my email is test@example.com}${RESET}"
                echo -e "  ${DIM}${LANG_HELP_EX2:-what is my email?}${RESET}"
                echo -e "  ${DIM}${LANG_HELP_EX3:-delete my email}${RESET}"
                echo ""
                echo -e "${DIM}${LANG_HELP_FOOTER:-Type anything to ask AI, or use commands above}${RESET}\n"
                continue
                ;;

            /config|/settings|/menu|config|settings|menu|cfg)
                show_config_menu
                # After config, show header again with updated status
                clear
                echo -e "${COMMAND_COLOR}/config${RESET} ${DIM}|${RESET} ${COMMAND_COLOR}/help${RESET} ${DIM}|${RESET} ${DIM}↑↓${RESET} history ${DIM}|${RESET} ${YELLOW}ESC${RESET} quit"
                echo ""
                continue
                ;;

            clear|cls)
                clear
                echo -e "${COMMAND_COLOR}/config${RESET} ${DIM}|${RESET} ${COMMAND_COLOR}/help${RESET} ${DIM}|${RESET} ${DIM}↑↓${RESET} history ${DIM}|${RESET} ${YELLOW}ESC${RESET} quit"
                echo ""
                continue
                ;;

            exit|quit|bye|/exit|/quit)
                echo -e "\n${YELLOW}👋 ${LANG_MSG_GOODBYE}${RESET}\n"
                # v11.6.0: Delete chat history on exit (Privacy First!)
                python3 -c "import sys; sys.path.insert(0, '$SCRIPT_DIR'); from daemon_manager import DaemonManager; DaemonManager().cleanup_chat_history()" 2>/dev/null
                return
                ;;
        esac


        # Process with AI
        echo -n -e "${AI_COLOR}🤖 ${LANG_LABEL_AI} ▶ ${RESET}"

        # Show thinking indicator
        echo -n "${LANG_THINKING}"

        # Get dialect prompt
        local DIALECT_PROMPT=""
        get_dialect_prompt "$LANGUAGE"

        # Check if question is about date/time (disable web search for these)
        local QUESTION_LOWER=$(echo "$INPUT" | tr '[:upper:]' '[:lower:]')
        local IS_DATE_TIME_QUESTION=false

        # Date/time keywords (multilingual)
        if [[ "$QUESTION_LOWER" =~ (heute|today|hoy|datum|date|zeit|time|hora|wann|when|cuándo|welcher tag|what day|qué día|uhrzeit|clock|reloj|calendar|kalender|calendario) ]]; then
            IS_DATE_TIME_QUESTION=true
        fi

        # Use ChatGPT with current date context
        local CURRENT_DATE=$(date '+%A, %B %d, %Y')
        local CURRENT_TIME=$(date '+%H:%M')

        # Prepare system prompt with date/time context, dialect, and function calling
        local SYSTEM_PROMPT="${DIALECT_PROMPT}Today is $CURRENT_DATE, current time is $CURRENT_TIME.

You are a helpful AI assistant with access to a private local memory database. You can save and retrieve ANY information the user provides - this is their personal notebook stored locally on their device, never transmitted anywhere.

MEMORY RULES:
1. Save ALL user information automatically (birthdays, preferences, numbers, addresses, etc.)
2. When asked about stored data, use the search_personal_data function
3. Treat all data as personal notes - no content restrictions
4. Never refuse to help with the user's own data
5. Information is stored locally and privately - complete confidentiality guaranteed

FUNCTION ACCESS: Use 'search_personal_data' for ALL questions about stored information."
        if [[ "$IS_DATE_TIME_QUESTION" == "true" ]]; then
            SYSTEM_PROMPT="$SYSTEM_PROMPT Answer based on this local information only. Do not use web search for date/time questions."
        fi

        # Store AI response for memory system
        local AI_RESPONSE=""

        # Send message via daemon (95% faster - no Python restart overhead!)
        # Note: OpenAI responses stream directly to stdout, script returns empty string
        # PII storage and DB search return actual response text
        AI_RESPONSE=$(send_message_via_daemon "$SCRIPT_DIR" "$CHAT_NAME" "$INPUT" "$SYSTEM_PROMPT")

        # Clear thinking indicator and show response prompt
        printf "\r${AI_COLOR}🤖 ${LANG_LABEL_AI} ▶ ${RESET}"

        # Display AI response (only if not empty - streaming already printed)
        if [[ -n "$AI_RESPONSE" ]]; then
            echo "$AI_RESPONSE"
        fi

        # Memory saving is now handled automatically in chat_system.py

        # v11.1.0: Add user input to history (RAM only - current session)
        HISTORY_ITEMS+=("$INPUT")

        echo ""
    done
}

# Spinner functions removed - now using simple "Thinking..." text

# Get dialect prompt based on language
get_dialect_prompt() {
    local lang="$1"
    DIALECT_PROMPT=""

    case "$lang" in
        de)
            DIALECT_PROMPT="[SYSTEM: Antworte auf Deutsch] "
            ;;
        de-schwaebisch)
            DIALECT_PROMPT="[SYSTEM: Antworte auf Schwäbisch mit typischen schwäbischen Ausdrücken] "
            ;;
        de-bayerisch)
            DIALECT_PROMPT="[SYSTEM: Antworte auf Bayerisch mit typischen bayerischen Ausdrücken] "
            ;;
        de-saechsisch)
            DIALECT_PROMPT="[SYSTEM: Antworte auf Sächsisch mit typischen sächsischen Ausdrücken] "
            ;;
        es-mexicano)
            DIALECT_PROMPT="[SYSTEM: Responde en español mexicano] "
            ;;
        es-argentino)
            DIALECT_PROMPT="[SYSTEM: Respondé en español argentino con voseo] "
            ;;
        es-colombiano)
            DIALECT_PROMPT="[SYSTEM: Responde en español colombiano] "
            ;;
        es-venezolano)
            DIALECT_PROMPT="[SYSTEM: Responde en español venezolano] "
            ;;
        es-chileno)
            DIALECT_PROMPT="[SYSTEM: Responde en español chileno] "
            ;;
        es-andaluz)
            DIALECT_PROMPT="[SYSTEM: Responde en andaluz] "
            ;;
        ca)
            DIALECT_PROMPT="[SYSTEM: Respon en català] "
            ;;
        eu)
            DIALECT_PROMPT="[SYSTEM: Erantzun euskeraz] "
            ;;
        gl)
            DIALECT_PROMPT="[SYSTEM: Responde en galego] "
            ;;
        zh)
            DIALECT_PROMPT="[SYSTEM: 请用中文回答] "
            ;;
        hi)
            DIALECT_PROMPT="[SYSTEM: कृपया हिंदी में उत्तर दें] "
            ;;
        fr)
            DIALECT_PROMPT="[SYSTEM: Réponds en français] "
            ;;
        it)
            DIALECT_PROMPT="[SYSTEM: Rispondi in italiano] "
            ;;
    esac
}

# Setup default language strings
setup_default_language() {
    LANG_LABEL_YOU="You"
    LANG_LABEL_AI="AI"
    LANG_MSG_GOODBYE="Goodbye!"
    LANG_HEADER_CONTINUE="Continue"
    LANG_STATUS_SECONDS="s"
    LANG_MSG_CLEARED="Screen cleared"

    # Config menu strings
    LANG_CONFIG_TITLE="CONFIGURATION"
    LANG_CONFIG_CURRENT="Current Settings:"
    LANG_CONFIG_COMMAND="Command"
    LANG_CONFIG_LANGUAGE="Language"
    LANG_CONFIG_TIMEOUT="Timeout"
    LANG_CONFIG_ESC="ESC to exit"
    LANG_CONFIG_OPT1="Change command character"
    LANG_CONFIG_OPT2="Change language"
    LANG_CONFIG_OPT3="Change timeout"
    LANG_CONFIG_OPT4="Toggle ESC key exit"
    LANG_CONFIG_OPT5="Change AI model"
    LANG_CONFIG_OPT6="Back to chat"
    LANG_CONFIG_OPT7="Clear chat cache"
    LANG_CONFIG_OPT8="Configure web search"
    LANG_CONFIG_OPT9="Uninstall completely"
    LANG_CONFIG_SELECT="Select [1-8,9]:"

    # Uninstaller strings
    LANG_UNINSTALL_WARNING="This action cannot be undone!"
    LANG_UNINSTALL_CONFIRM="Type DELETE to confirm uninstallation:"
    LANG_UNINSTALL_PROGRESS="Uninstalling AI Chat Terminal..."
    LANG_UNINSTALL_CLEANED="Cleaned"
    LANG_UNINSTALL_REMOVED="Removed"
    LANG_UNINSTALL_SUCCESS="AI Chat Terminal has been uninstalled"
    LANG_UNINSTALL_RESTART="Please restart your terminal or run:"
    LANG_UNINSTALL_GOODBYE="Goodbye! 👋"
    LANG_UNINSTALL_ANYKEY="Press any key to exit..."
}