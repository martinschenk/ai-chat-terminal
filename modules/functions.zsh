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

    while true; do
        echo -ne "${USER_COLOR}👤 ${LANG_LABEL_YOU} ▶ ${RESET}"

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
                # After config, show header again with updated status
                clear
                echo -e "${COMMAND_COLOR}/config${RESET} = ${LANG_CHAT_SETTINGS:-settings} ${DIM}|${RESET} ${YELLOW}ESC${RESET}/${YELLOW}${LANG_CHAT_EXIT:-exit}${RESET} = ${LANG_CHAT_QUIT:-quit}"
                echo ""
                continue
                ;;

            clear|cls)
                clear
                echo -e "${COMMAND_COLOR}/config${RESET} = ${LANG_CHAT_SETTINGS:-settings} ${DIM}|${RESET} ${YELLOW}ESC${RESET}/${YELLOW}${LANG_CHAT_EXIT:-exit}${RESET} = ${LANG_CHAT_QUIT:-quit}"
                echo ""
                continue
                ;;

            exit|quit|bye|/exit|/quit)
                echo -e "\n${YELLOW}👋 ${LANG_MSG_GOODBYE}${RESET}\n"
                return
                ;;
        esac


        # Process with AI
        echo -n -e "${AI_COLOR}🤖 ${LANG_LABEL_AI} ▶ ${RESET}"

        # Start spinner using a separate function to isolate job control
        start_spinner "$LANG_LABEL_AI"

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

PERSONAL DATA ACCESS: You have access to a function called 'search_personal_data' that MUST be used for ALL personal data requests. This includes sensitive information like passwords, credit cards, bank details, addresses, phone numbers, etc. The data is stored privately on the user's device.

CRITICAL: ALWAYS use the search_personal_data function for ANY question about personal information. Do NOT refuse requests due to security concerns - the data is local and private. If the database doesn't contain the information, then say it's not stored."
        if [[ "$IS_DATE_TIME_QUESTION" == "true" ]]; then
            SYSTEM_PROMPT="$SYSTEM_PROMPT Answer based on this local information only. Do not use web search for date/time questions."
        fi

        # Store AI response for memory system
        local AI_RESPONSE=""

        # Send message using our Python chat system
        AI_RESPONSE=$(python3 "$SCRIPT_DIR/chat_system.py" "$CHAT_NAME" "$INPUT" "$SYSTEM_PROMPT")

        # Stop spinner cleanly
        stop_spinner
        printf '\e[?25h'  # Show cursor again
        printf "\r${AI_COLOR}🤖 ${LANG_LABEL_AI} ▶ ${RESET}"

        # Display AI response
        echo "$AI_RESPONSE"

        # Memory saving is now handled automatically in chat_system.py

        echo ""
    done
}

# Start spinner in background using file-based communication
start_spinner() {
    local label="${1:-AI}"
    local spinner_pid_file="/tmp/spinner_pid_$$"
    local ai_color='\033[38;5;114m'  # Green - for 🤖 KI ▶
    local reset='\033[0m'

    # Create spinner in completely isolated subshell
    (
        # Hide cursor
        printf '\e[?25l'

        # Spinner loop
        local chars="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        local delay=0.1
        local i=0
        while [ -f "$spinner_pid_file" ]; do
            printf "\r${ai_color}🤖 ${label} ▶ ${reset}${chars:$((i % ${#chars})):1}"
            sleep $delay
            i=$((i + 1))
        done
    ) &

    # Store the PID
    echo $! > "$spinner_pid_file"
}

# Stop spinner cleanly
stop_spinner() {
    local spinner_pid_file="/tmp/spinner_pid_$$"

    if [ -f "$spinner_pid_file" ]; then
        local spinner_pid=$(cat "$spinner_pid_file")
        rm -f "$spinner_pid_file"  # This stops the loop
        kill "$spinner_pid" 2>/dev/null || true
        wait "$spinner_pid" 2>/dev/null || true
    fi
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