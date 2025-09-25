#!/usr/bin/env zsh
# AI Chat Terminal - Ultra Simple Version
# Version: 3.5.0
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
    # Fixed path instead of dynamic resolution
    local SCRIPT_DIR="$HOME/shell-scripts"

    # Create config dir if needed
    mkdir -p "$CONFIG_DIR"

    # First run check - ask for language preference
    if [[ ! -f "$CONFIG_FILE" ]]; then
        clear
        echo -e "\033[1;36m🌍 Welcome to AI Chat Terminal!\033[0m"
        echo ""
        echo "Please select your language / Bitte Sprache wählen / Choisissez votre langue:"
        echo ""
        echo "  [1] 🇬🇧 English (default)"
        echo "  [2] 🇩🇪 Deutsch"
        echo "  [3] 🇫🇷 Français"
        echo "  [4] 🇮🇹 Italiano"
        echo "  [5] 🇪🇸 Español"
        echo "  [6] 🇨🇳 中文 (Mandarin)"
        echo "  [7] 🇮🇳 हिन्दी (Hindi)"
        echo ""
        echo -n "Select [1-7] (press Enter for English): "
        read -r lang_choice

        case "$lang_choice" in
            2)
                # German - ask for dialect
                echo ""
                echo "Möchten Sie einen Dialekt?"
                echo "  [1] Hochdeutsch (Standard)"
                echo "  [2] Schwäbisch"
                echo "  [3] Bayerisch"
                echo "  [4] Sächsisch"
                echo ""
                echo -n "Auswahl [1-4]: "
                read -r dialect_choice
                case "$dialect_choice" in
                    2) selected_lang="de-schwaebisch" ;;
                    3) selected_lang="de-bayerisch" ;;
                    4) selected_lang="de-saechsisch" ;;
                    *) selected_lang="de" ;;
                esac
                ;;
            3) selected_lang="fr" ;;
            4) selected_lang="it" ;;
            5)
                # Spanish - ask for variant
                echo ""
                echo "¿Qué variante de español prefieres?"
                echo "  [1] 🇪🇸 Español (Estándar)"
                echo "  [2] 🇲🇽 Mexicano (Órale, güey)"
                echo "  [3] 🇦🇷 Argentino (Che, vos)"
                echo "  [4] 🇨🇴 Colombiano (Parce)"
                echo "  [5] 🇻🇪 Venezolano (Pana, épale)"
                echo "  [6] 🇨🇱 Chileno (Po, wena)"
                echo "  [7] 🇪🇸 Andaluz (Quillo)"
                echo ""
                echo -n "Selección [1-7]: "
                read -r spanish_choice
                case "$spanish_choice" in
                    2) selected_lang="es-mexicano" ;;
                    3) selected_lang="es-argentino" ;;
                    4) selected_lang="es-colombiano" ;;
                    5) selected_lang="es-venezolano" ;;
                    6) selected_lang="es-chileno" ;;
                    7) selected_lang="es-andaluz" ;;
                    *) selected_lang="es" ;;
                esac
                ;;
            6) selected_lang="zh" ;;
            7) selected_lang="hi" ;;
            *) selected_lang="en" ;;
        esac

        # Save initial config
        echo "AI_CHAT_COMMAND=\"q\"" > "$CONFIG_FILE"
        echo "AI_CHAT_LANGUAGE=\"$selected_lang\"" >> "$CONFIG_FILE"
        echo "AI_CHAT_TIMEOUT=\"120\"" >> "$CONFIG_FILE"
        echo "AI_CHAT_ESC_EXIT=\"true\"" >> "$CONFIG_FILE"

        echo ""
        echo -e "\033[0;32m✓ Language set to: $selected_lang\033[0m"
        echo ""
        sleep 2
        clear
    fi

    # Load user config
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
        echo -e "\n${CYAN}/config${RESET} = settings ${DIM}|${RESET} ${YELLOW}ESC${RESET}/${YELLOW}exit${RESET} = quit ${SESSION_STATUS}"
        echo -e "${DIM}─────────────────────────────────────────────────────${RESET}\n"

        echo -e "${BLUE}👤 ${LANG_LABEL_YOU}:${RESET} $*\n"
        echo -e "${GREEN}🤖 ${LANG_LABEL_AI}:${RESET}"

        # Add dialect/language instruction if needed
        local DIALECT_PROMPT=""
        case "$LANGUAGE" in
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
            es-chileno)
                DIALECT_PROMPT="[SYSTEM: Responde en español chileno] "
                ;;
            es-andaluz)
                DIALECT_PROMPT="[SYSTEM: Responde en andaluz] "
                ;;
            es-venezolano)
                DIALECT_PROMPT="[SYSTEM: Responde en español venezolano] "
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

        sgpt --chat "$CHAT_NAME" "${DIALECT_PROMPT}$*"
        echo -e "\n${DIM}─────────────────────────────────────────────────────${RESET}\n"

        # Continue in chat mode
        chat_loop
        return
    fi

    # Instant chat mode (just 'q' entered)
    clear
    echo -e "${CYAN}/config${RESET} = settings ${DIM}|${RESET} ${YELLOW}ESC${RESET}/${YELLOW}exit${RESET} = quit ${SESSION_STATUS}"
    echo -e "${DIM}─────────────────────────────────────────────────────${RESET}\n"

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

    # Fixed path for language files
    local SCRIPT_DIR="$HOME/shell-scripts"

    # Load language file
    local LANG_FILE="$SCRIPT_DIR/languages/${LANGUAGE}.conf"
    if [[ ! -f "$LANG_FILE" ]]; then
        # Fallback to embedded English
        LANG_LABEL_YOU="You"
        LANG_LABEL_AI="AI"
        LANG_MSG_GOODBYE="Goodbye!"
    else
        source "$LANG_FILE"
    fi

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
        if [[ "$ENABLE_ESC" == "true" ]] && [[ -t 0 ]]; then
            # Try char-by-char reading with proper terminal handling
            local OLD_STTY=$(stty -g 2>/dev/null)

            # Set terminal to raw mode for proper char reading
            stty raw -echo 2>/dev/null || {
                # Fallback if stty fails
                read -r INPUT
                echo ""
            }

            # Read char by char
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
                    # Normal character (including /)
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
                echo -e "${CYAN}/config${RESET} = settings ${DIM}|${RESET} ${YELLOW}ESC${RESET}/${YELLOW}exit${RESET} = quit"
                echo -e "${DIM}─────────────────────────────────────────────────────${RESET}\n"
                continue
                ;;

            clear|cls)
                clear
                echo -e "${CYAN}/config${RESET} = settings ${DIM}|${RESET} ${YELLOW}ESC${RESET}/${YELLOW}exit${RESET} = quit"
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

        # Add dialect/language instruction if needed
        local DIALECT_PROMPT=""
        case "$LANGUAGE" in
            de-schwaebisch)
                DIALECT_PROMPT="[SYSTEM: Antworte auf Schwäbisch mit typischen schwäbischen Ausdrücken wie 'isch', 'au', 'gell', 'Griaß Gott', 'ha noi', etc.] "
                ;;
            de-bayerisch)
                DIALECT_PROMPT="[SYSTEM: Antworte auf Bayerisch mit typischen bayerischen Ausdrücken wie 'mei', 'a bisserl', 'Servus', 'pfiat di', 'a Gaudi', etc.] "
                ;;
            de-saechsisch)
                DIALECT_PROMPT="[SYSTEM: Antworte auf Sächsisch mit typischen sächsischen Ausdrücken wie 'nu', 'mor', 'Gudn Dach', etc.] "
                ;;
            es-mexicano)
                DIALECT_PROMPT="[SYSTEM: Responde en español mexicano usando expresiones como 'órale', 'güey', 'chido', 'padre', 'ándale', etc.] "
                ;;
            es-argentino)
                DIALECT_PROMPT="[SYSTEM: Respondé en español argentino usando el voseo y expresiones como 'che', 'boludo', 'bárbaro', 'dale', etc.] "
                ;;
            es-colombiano)
                DIALECT_PROMPT="[SYSTEM: Responde en español colombiano usando expresiones como 'parce', 'bacano', 'chévere', 'qué más', etc.] "
                ;;
            es-chileno)
                DIALECT_PROMPT="[SYSTEM: Responde en español chileno usando expresiones como 'po', 'cachai', 'wena', 'bacán', 'altiro', etc.] "
                ;;
            es-andaluz)
                DIALECT_PROMPT="[SYSTEM: Responde en andaluz usando expresiones como 'quillo', 'arfavó', 'illo', 'ozú', etc.] "
                ;;
            es-venezolano)
                DIALECT_PROMPT="[SYSTEM: Responde en español venezolano usando expresiones como 'pana', 'épale', 'chamo', 'fino', 'arrecho', etc.] "
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

        sgpt --chat "$CHAT_NAME" "${DIALECT_PROMPT}$INPUT"
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
    local SCRIPT_DIR="$HOME/shell-scripts"

    # Load language file for config menu
    local LANG_FILE="$SCRIPT_DIR/languages/${LANGUAGE}.conf"
    if [[ ! -f "$LANG_FILE" ]]; then
        # Fallback to English
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
        LANG_CONFIG_OPT9="Uninstall completely"
        LANG_CONFIG_SELECT="Select [1-7,9]:"
        LANG_CONFIG_ENTER_CMD="Enter new command (current: "
        LANG_CONFIG_ENTER_LANG="Enter code:"
        LANG_CONFIG_ENTER_TIMEOUT="Timeout in seconds (current: "
        LANG_CONFIG_CHANGED="changed to:"
        LANG_CONFIG_RESTART="Restart shell to apply"
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
    echo -e "${PURPLE}║${RESET}  ${GREEN}[6]${RESET} ${LANG_CONFIG_OPT6}                   ${PURPLE}║${RESET}"
    echo -e "${PURPLE}║${RESET}  ${GREEN}[7]${RESET} 🧹 ${LANG_CONFIG_OPT7}              ${PURPLE}║${RESET}"
    echo -e "${PURPLE}║${RESET}                                       ${PURPLE}║${RESET}"
    echo -e "${PURPLE}║${RESET}  ${RED}[9]${RESET} 🗑️  ${LANG_CONFIG_OPT9}        ${PURPLE}║${RESET}"
    echo -e "${PURPLE}╚═══════════════════════════════════════╝${RESET}"
    echo ""

    echo -ne "${CYAN}${LANG_CONFIG_SELECT} ${RESET}"
    read -r choice

    case $choice in
        1)
            echo -ne "${CYAN}${LANG_CONFIG_ENTER_CMD}$COMMAND_CHAR): ${RESET}"
            read -r new_cmd
            if [[ ! -z "$new_cmd" ]]; then
                echo "AI_CHAT_COMMAND=\"$new_cmd\"" > "$CONFIG_FILE"
                echo "AI_CHAT_LANGUAGE=\"$LANGUAGE\"" >> "$CONFIG_FILE"
                echo "AI_CHAT_TIMEOUT=\"$TIMEOUT\"" >> "$CONFIG_FILE"
                echo "AI_CHAT_ESC_EXIT=\"$ENABLE_ESC\"" >> "$CONFIG_FILE"
                echo -e "${GREEN}✅ ${LANG_CONFIG_COMMAND} ${LANG_CONFIG_CHANGED} $new_cmd${RESET}"
                echo -e "${YELLOW}${LANG_CONFIG_RESTART}${RESET}"
                sleep 2
            fi
            ;;

        2)
            echo -e "${CYAN}${LANG_CONFIG_LANGUAGE}:${RESET}"
            echo "  en - English"
            echo "  de - Deutsch"
            echo "  fr - Français"
            echo "  it - Italiano"
            echo "  es - Español"
            echo "  zh - 中文 (Chinese)"
            echo "  hi - हिन्दी (Hindi)"
            echo -ne "${CYAN}${LANG_CONFIG_ENTER_LANG} ${RESET}"
            read -r new_lang

            # Handle German dialects
            if [[ "$new_lang" == "de" ]]; then
                echo ""
                echo -e "${CYAN}Deutscher Dialekt:${RESET}"
                echo "  [1] Hochdeutsch (Standard)"
                echo "  [2] Schwäbisch"
                echo "  [3] Bayerisch"
                echo "  [4] Sächsisch"
                echo -n "Auswahl [1-4]: "
                read -r dialect
                case "$dialect" in
                    2) new_lang="de-schwaebisch" ;;
                    3) new_lang="de-bayerisch" ;;
                    4) new_lang="de-saechsisch" ;;
                    *) new_lang="de" ;;
                esac
            fi

            # Handle Spanish variants
            if [[ "$new_lang" == "es" ]]; then
                echo ""
                echo -e "${CYAN}Variante española:${RESET}"
                echo "  [1] 🇪🇸 Español (Estándar)"
                echo "  [2] 🇲🇽 Mexicano"
                echo "  [3] 🇦🇷 Argentino"
                echo "  [4] 🇨🇴 Colombiano"
                echo "  [5] 🇻🇪 Venezolano"
                echo "  [6] 🇨🇱 Chileno"
                echo "  [7] 🇪🇸 Andaluz"
                echo -n "Selección [1-7]: "
                read -r variant
                case "$variant" in
                    2) new_lang="es-mexicano" ;;
                    3) new_lang="es-argentino" ;;
                    4) new_lang="es-colombiano" ;;
                    5) new_lang="es-venezolano" ;;
                    6) new_lang="es-chileno" ;;
                    7) new_lang="es-andaluz" ;;
                    *) new_lang="es" ;;
                esac
            fi

            if [[ "$new_lang" == "en" ]] || [[ "$new_lang" == "de" ]] || [[ "$new_lang" == "de-"* ]] || [[ "$new_lang" == "fr" ]] || [[ "$new_lang" == "it" ]] || [[ "$new_lang" == "es" ]] || [[ "$new_lang" == "es-"* ]] || [[ "$new_lang" == "zh" ]] || [[ "$new_lang" == "hi" ]]; then
                echo "AI_CHAT_COMMAND=\"$COMMAND_CHAR\"" > "$CONFIG_FILE"
                echo "AI_CHAT_LANGUAGE=\"$new_lang\"" >> "$CONFIG_FILE"
                echo "AI_CHAT_TIMEOUT=\"$TIMEOUT\"" >> "$CONFIG_FILE"
                echo "AI_CHAT_ESC_EXIT=\"$ENABLE_ESC\"" >> "$CONFIG_FILE"
                echo -e "${GREEN}✅ ${LANG_CONFIG_LANGUAGE}: $new_lang${RESET}"
                sleep 2
            fi
            ;;

        3)
            echo -ne "${CYAN}${LANG_CONFIG_ENTER_TIMEOUT}$TIMEOUT): ${RESET}"
            read -r new_timeout
            if [[ "$new_timeout" =~ ^[0-9]+$ ]]; then
                echo "AI_CHAT_COMMAND=\"$COMMAND_CHAR\"" > "$CONFIG_FILE"
                echo "AI_CHAT_LANGUAGE=\"$LANGUAGE\"" >> "$CONFIG_FILE"
                echo "AI_CHAT_TIMEOUT=\"$new_timeout\"" >> "$CONFIG_FILE"
                echo "AI_CHAT_ESC_EXIT=\"$ENABLE_ESC\"" >> "$CONFIG_FILE"
                echo -e "${GREEN}✅ ${LANG_CONFIG_TIMEOUT}: ${new_timeout}s${RESET}"
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
            echo -e "${GREEN}✅ ${LANG_CONFIG_ESC}: $new_esc${RESET}"
            sleep 2
            ;;

        5)
            echo -e "${CYAN}AI Models:${RESET}"
            echo "  1) gpt-4o-mini (fast, cheap, good for dialects)"
            echo "  2) gpt-4o (best for dialects! 🌍)"
            echo "  3) gpt-4 (powerful, standard)"
            echo "  4) gpt-4-turbo (fast)"
            echo "  5) gpt-3.5-turbo (basic, cheap)"

            # Show dialect recommendation if using dialect
            if [[ "$LANGUAGE" == *"-"* ]]; then
                echo ""
                echo -e "${YELLOW}💡 Tip: For dialects, GPT-4o works best!${RESET}"
            fi

            echo -ne "${CYAN}Select [1-5]: ${RESET}"
            read -r model_choice

            case $model_choice in
                1) model="gpt-4o-mini" ;;
                2) model="gpt-4o" ;;
                3) model="gpt-4" ;;
                4) model="gpt-4-turbo" ;;
                5) model="gpt-3.5-turbo" ;;
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

        7)
            # Clear chat cache
            echo -e "${YELLOW}Clearing chat cache...${RESET}"

            # Clear sgpt chat sessions
            local cache_cleared=false

            # Clear from temp directory (main cache location)
            if [[ -d "/var/folders" ]]; then
                find /var/folders -name "*_chat" -type f 2>/dev/null | while read cache_file; do
                    if [[ -w "$cache_file" ]]; then
                        rm -f "$cache_file" 2>/dev/null && cache_cleared=true
                        echo -e "  ${GREEN}✓${RESET} Cleared: $(basename $cache_file)"
                    fi
                done
            fi

            # Clear from ~/.config/shell_gpt/chat_sessions if exists
            if [[ -d "$HOME/.config/shell_gpt/chat_sessions" ]]; then
                find "$HOME/.config/shell_gpt/chat_sessions" -type f -name "*" ! -name ".gitkeep" -delete 2>/dev/null
                cache_cleared=true
            fi

            # Clear sgpt's cached chats (alternative location)
            local sgpt_cache_dir="$HOME/.cache/sgpt"
            if [[ -d "$sgpt_cache_dir" ]]; then
                rm -rf "$sgpt_cache_dir"/* 2>/dev/null && cache_cleared=true
            fi

            # Clear our session timestamp
            if [[ -f "$SESSION_FILE" ]]; then
                rm -f "$SESSION_FILE" 2>/dev/null && cache_cleared=true
            fi

            if [[ "$cache_cleared" == "true" ]]; then
                echo -e "\n${GREEN}✅ Chat cache cleared successfully!${RESET}"
            else
                echo -e "\n${YELLOW}No cache files found or already clear.${RESET}"
            fi
            sleep 2
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