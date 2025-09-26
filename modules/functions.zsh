#!/bin/zsh
# AI Chat Terminal - Additional Functions
# Part 2 of chat.zsh

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
    # Use global SCRIPT_DIR from main script

    # Load language file for chat
    local LANG_FILE="$SCRIPT_DIR/lang/${LANGUAGE}.conf"
    if [[ ! -f "$LANG_FILE" ]]; then
        setup_default_language
    else
        source "$LANG_FILE"
    fi

    # Colors
    local BLUE='\033[0;34m'
    local GREEN='\033[0;32m'
    local YELLOW='\033[1;33m'
    local CYAN='\033[0;36m'
    local RESET='\033[0m'
    local DIM='\033[2m'

    local INPUT=""

    while true; do
        echo -ne "${BLUE}👤 ${LANG_LABEL_YOU} ▶ ${RESET}"

        # Handle ESC key detection
        if [[ "$ENABLE_ESC" == "true" ]] && [[ -t 0 ]]; then
            # Save current terminal settings
            OLD_STTY=$(stty -g)
            stty raw -echo min 1 time 0 2>/dev/null

            INPUT=""
            while true; do
                char=$(dd bs=1 count=1 2>/dev/null)

                if [[ $char == $'\e' ]]; then
                    # ESC pressed
                    stty "$OLD_STTY" 2>/dev/null
                    echo -e "\n\n${YELLOW}👋 ${LANG_MSG_GOODBYE}${RESET}\n"
                    return
                elif [[ $char == $'\r' ]] || [[ $char == $'\n' ]]; then
                    # Enter pressed
                    stty "$OLD_STTY" 2>/dev/null
                    echo
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
        else
            # Simple read without ESC
            read -r INPUT
        fi

        # Skip empty input
        [[ -z "$INPUT" ]] && continue

        # Handle commands
        case "$INPUT" in
            /config|/settings|/menu|config|settings|menu|cfg)
                show_config_menu
                # After config, show header again
                clear
                echo -e "${CYAN}/config${RESET} = ${LANG_CHAT_SETTINGS:-settings} ${DIM}|${RESET} ${YELLOW}ESC${RESET}/${YELLOW}${LANG_CHAT_EXIT:-exit}${RESET} = ${LANG_CHAT_QUIT:-quit}"
                echo -e "${DIM}─────────────────────────────────────────────────────${RESET}\n"
                continue
                ;;

            clear|cls)
                clear
                echo -e "${CYAN}/config${RESET} = ${LANG_CHAT_SETTINGS:-settings} ${DIM}|${RESET} ${YELLOW}ESC${RESET}/${YELLOW}${LANG_CHAT_EXIT:-exit}${RESET} = ${LANG_CHAT_QUIT:-quit}"
                echo -e "${DIM}─────────────────────────────────────────────────────${RESET}\n"
                continue
                ;;

            exit|quit|bye|/exit|/quit)
                echo -e "\n${YELLOW}👋 ${LANG_MSG_GOODBYE}${RESET}\n"
                return
                ;;
        esac


        # Process with AI
        echo -e "${GREEN}🤖 ${LANG_LABEL_AI} ▶ ${RESET}"

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

        # Initialize chat if this is the first message
        if ! sgpt --list-chats 2>/dev/null | grep -q "^$CHAT_NAME$"; then
            sgpt --chat "$CHAT_NAME" "Hello, I'm starting a new chat session." >/dev/null 2>&1 || true
        fi

        if [[ "$IS_DATE_TIME_QUESTION" == "true" ]]; then
            # Disable web search for date/time questions
            sgpt --chat "$CHAT_NAME" --no-functions "${DIALECT_PROMPT}Today is $CURRENT_DATE, current time is $CURRENT_TIME. Answer based on this local information only. $INPUT"
        else
            # Normal mode with web search capabilities
            sgpt --chat "$CHAT_NAME" "${DIALECT_PROMPT}Today is $CURRENT_DATE, current time is $CURRENT_TIME. $INPUT"
        fi

        echo -e "${DIM}─────────────────────────────────────────────────────${RESET}\n"
    done
}

# Get dialect prompt based on language
get_dialect_prompt() {
    local lang="$1"
    DIALECT_PROMPT=""

    case "$lang" in
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