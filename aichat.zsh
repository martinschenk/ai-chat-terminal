#!/bin/zsh
# AI Chat Terminal - Main Chat Function
# Version 5.2.0 - Clean directory structure, web search, conflict detection

# Get the directory of this script (should be ~/.aichat)
SCRIPT_DIR="$(cd "$(dirname "${(%):-%x}")" && pwd)"

# Source modular components from modules directory
source "$SCRIPT_DIR/modules/functions.zsh"
source "$SCRIPT_DIR/modules/config-menu.zsh"

# Function to load .env file
load_env() {
    local env_file="$HOME/.aichat/.env"
    if [[ -f "$env_file" ]]; then
        while IFS='=' read -r key value; do
            # Skip comments and empty lines
            [[ "$key" =~ ^#.*$ ]] && continue
            [[ -z "$key" ]] && continue

            # Remove quotes from value
            value="${value%\"}"
            value="${value#\"}"
            value="${value%\'}"
            value="${value#\'}"

            # Export the variable
            export "$key=$value"
        done < "$env_file"
    fi
}

# Main chat function
ai_chat_function() {
    # Check for setup commands
    if [[ "$1" == "setup" ]] || [[ "$1" == "--setup" ]]; then
        first_run_setup
        return
    fi

    # Load environment variables from .env
    load_env

    local CONFIG_DIR="$HOME/.aichat"
    local CONFIG_FILE="$CONFIG_DIR/config"
    local ENV_FILE="$CONFIG_DIR/.env"
    # Use the global SCRIPT_DIR set at the top of the file

    # Create config dir if needed
    mkdir -p "$CONFIG_DIR"

    # First run check - comprehensive onboarding
    if [[ ! -f "$ENV_FILE" ]] || [[ ! -f "$CONFIG_FILE" ]]; then
        first_run_setup
        return
    fi

    # Load user config
    if [[ -f "$CONFIG_FILE" ]]; then
        source "$CONFIG_FILE"
    fi

    # Defaults from config or fallback
    local COMMAND_CHAR="${AI_CHAT_COMMAND:-ai}"
    local LANGUAGE="${AI_CHAT_LANGUAGE:-en}"
    local TIMEOUT_SECONDS="${AI_CHAT_TIMEOUT:-600}"
    local ENABLE_ESC="${AI_CHAT_ESC_EXIT:-true}"

    # Load language file
    local LANG_FILE="$SCRIPT_DIR/lang/${LANGUAGE}.conf"
    if [[ ! -f "$LANG_FILE" ]]; then
        # Fallback to embedded English
        setup_default_language
    else
        source "$LANG_FILE"
    fi

    # Chat configuration
    local CHAT_NAME="${COMMAND_CHAR}_chat"
    local TIMEOUT_FILE="$CONFIG_DIR/last_time"

    # Initialize sgpt chat session if needed
    local CACHE_DIR="/tmp/chat_cache"
    mkdir -p "$CACHE_DIR" 2>/dev/null

    # Ensure sgpt config exists
    mkdir -p ~/.config/shell_gpt

    # Initialize chat session if needed
    if [[ ! -f "$CACHE_DIR/${CHAT_NAME}" ]] || [[ ! -s "$CACHE_DIR/${CHAT_NAME}" ]]; then
        rm -f "$CACHE_DIR/${CHAT_NAME}" 2>/dev/null
        echo '[]' > "$CACHE_DIR/${CHAT_NAME}" 2>/dev/null
    fi

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

    # Handle direct questions (ai "question here")
    if [[ $# -gt 0 ]]; then
        # Special commands
        if [[ "$1" == "--config" ]] || [[ "$1" == "-c" ]]; then
            show_config_menu
            return
        fi

        # Direct question mode
        echo -e "\n${CYAN}/config${RESET} = settings ${DIM}|${RESET} ${YELLOW}ESC${RESET}/${YELLOW}exit${RESET} = quit ${SESSION_STATUS}"
        echo -e "${DIM}─────────────────────────────────────────────────────${RESET}\n"

        echo -e "${BLUE}👤 ${LANG_LABEL_YOU}:${RESET} $*\n"
        echo -e "${GREEN}🤖 ${LANG_LABEL_AI}:${RESET}"

        # Add dialect/language instruction if needed
        local DIALECT_PROMPT=""
        get_dialect_prompt "$LANGUAGE"

        # Use ChatGPT with web search capabilities
        sgpt --chat "$CHAT_NAME" "${DIALECT_PROMPT}$*"

        echo -e "\n${DIM}─────────────────────────────────────────────────────${RESET}\n"

        # Continue in chat mode
        chat_loop
        return
    fi

    # Instant chat mode
    clear
    echo -e "${CYAN}/config${RESET} = settings ${DIM}|${RESET} ${YELLOW}ESC${RESET}/${YELLOW}exit${RESET} = quit ${SESSION_STATUS}"
    echo -e "${DIM}─────────────────────────────────────────────────────${RESET}\n"

    chat_loop
}

# First run setup function
first_run_setup() {
    local CONFIG_DIR="$HOME/.aichat"
    local ENV_FILE="$CONFIG_DIR/.env"
    local CONFIG_FILE="$CONFIG_DIR/config"

    mkdir -p "$CONFIG_DIR"

    clear
    echo -e "\033[1;36m\033[1m👋 Welcome to AI Chat Terminal!\033[0m"
    echo -e "\033[1;36m================================\033[0m\n"
    echo -e "\033[0;37mLet's get you set up with your personal AI assistant.\033[0m"
    echo -e "\033[0;37mThis will only take a minute...\033[0m\n"

    # Step 1: Language Selection
    echo -e "\033[1;33mStep 1/4: Select Your Language\033[0m"
    echo "────────────────────────────────────"
    echo ""
    echo "  [1] 🇬🇧 English (default)"
    echo "  [2] 🇩🇪 Deutsch"
    echo "  [3] 🇫🇷 Français"
    echo "  [4] 🇮🇹 Italiano"
    echo "  [5] 🇪🇸 Español"
    echo "  [6] 🇨🇳 中文 (Mandarin)"
    echo "  [7] 🇮🇳 हिन्दी (Hindi)"
    echo ""
    echo -n "Select [1-7] (default: 1): "
    read -r lang_choice

    local language="en"
    case "$lang_choice" in
        2)
            language="de"
            handle_german_selection
            language="$selected_lang"
            ;;
        3) language="fr" ;;
        4) language="it" ;;
        5)
            language="es"
            handle_spanish_selection
            language="$selected_lang"
            ;;
        6) language="zh" ;;
        7) language="hi" ;;
        *) language="en" ;;
    esac
    echo -e "\033[0;32m✓ Language set to: $language\033[0m\n"

    # Step 2: OpenAI API Key
    echo -e "\033[1;33mStep 2/3: OpenAI API Key (Required)\033[0m"
    echo "────────────────────────────────────"
    echo -e "Get your key at: \033[0;36mhttps://platform.openai.com/api-keys\033[0m"
    echo ""

    local openai_key=""
    while [[ -z "$openai_key" ]]; do
        echo -n "Enter your OpenAI API key: "
        read -r openai_key
        if [[ -z "$openai_key" ]]; then
            echo -e "\033[0;31m⚠ API key is required to continue!\033[0m"
            echo -e "\033[2mPress Ctrl+C to cancel setup\033[0m"
        elif [[ ${#openai_key} -lt 20 ]]; then
            echo -e "\033[0;31m⚠ That doesn't look like a valid API key\033[0m"
            openai_key=""
        fi
    done
    echo -e "\033[0;32m✓ OpenAI API key configured (includes web search)\033[0m\n"

    # Step 3: Select OpenAI Model
    echo -e "\033[1;33mStep 3/3: Select AI Model\033[0m"
    echo "────────────────────────────────────"
    echo ""
    echo -e "  [1] gpt-4o       \033[0;32m⭐ RECOMMENDED\033[0m - Best performance (\$2.50/1M tokens)"
    echo -e "  [2] gpt-4o-mini   - \033[0;32mFast & cheap\033[0m (\$0.15/1M tokens)"
    echo -e "  [3] gpt-4-turbo  - Fast, good quality (\$10/1M tokens)"
    echo -e "  [4] gpt-4        - Classic powerful model (\$30/1M tokens)"
    echo -e "  [5] gpt-3.5-turbo - \033[0;33m💰 CHEAPEST\033[0m (\$0.50/1M tokens)"
    echo ""
    echo -n "Select [1-5] (default: 1): "
    read -r model_choice

    local openai_model="gpt-4o"
    case "$model_choice" in
        2) openai_model="gpt-4o-mini" ;;
        3) openai_model="gpt-4-turbo" ;;
        4) openai_model="gpt-4" ;;
        5) openai_model="gpt-3.5-turbo" ;;
        *) openai_model="gpt-4o" ;;  # Default
    esac
    echo -e "\033[0;32m✓ Model selected: $openai_model\033[0m\n"

    local command_char="ai"
    # Create configuration files
    echo -e "\033[0;34mSaving configuration...\033[0m"

    # Save .env file
    cat > "$ENV_FILE" << EOF
# AI Chat Terminal Configuration
# Generated: $(date)

# API Keys
OPENAI_API_KEY="$openai_key"

# Default Models
DEFAULT_OPENAI_MODEL="$openai_model"
EOF

    chmod 600 "$ENV_FILE"

    # Save config file
    cat > "$CONFIG_FILE" << EOF
# AI Chat Terminal User Configuration
AI_CHAT_COMMAND="$command_char"
AI_CHAT_LANGUAGE="$language"
AI_CHAT_TIMEOUT="600"
AI_CHAT_ESC_EXIT="true"
EOF

    # Configure Shell-GPT
    mkdir -p ~/.config/shell_gpt
    cat > ~/.config/shell_gpt/.sgptrc << EOF
DEFAULT_MODEL=$openai_model
CHAT_CACHE_LENGTH=20
CHAT_CACHE_PATH=/tmp/chat_cache
REQUEST_TIMEOUT=60
DEFAULT_COLOR=green
# Note: OPENAI_API_KEY is loaded from ~/.aichat/.env for security
EOF

    # Success message
    clear
    echo -e "\033[1;32m\033[1m🎉 Setup Complete!\033[0m"
    echo -e "\033[1;32m==================\033[0m\n"

    echo -e "\033[0;37mYour AI Chat Terminal is ready to use!\033[0m"
    echo ""
    echo -e "\033[1mConfiguration:\033[0m"
    echo -e "  • Language: \033[0;36m$language\033[0m"
    echo -e "  • AI Model: \033[0;36m$openai_model\033[0m"
    echo -e "  • Web Search: \033[0;32m✓ Enabled (ChatGPT)\033[0m"
    echo -e "  • Command: \033[0;36m$command_char\033[0m"
    echo ""

    echo -e "\033[1mTry it out:\033[0m"
    echo -e "  \033[0;32m$command_char\033[0m Hello!"
    echo -e "  \033[0;32m$command_char\033[0m What's the weather today?"
    echo -e "  \033[0;32m$command_char\033[0m What's in the news?"
    echo -e "  \033[0;32m$command_char\033[0m /config  \033[2m(to modify settings)\033[0m"
    echo ""

    echo -e "\033[2mStarting your first chat session...\033[0m"
    sleep 2
}

# Helper functions for language selection
handle_german_selection() {
    echo ""
    echo "Möchten Sie einen Dialekt?"
    echo "  [1] Hochdeutsch (Standard)"
    echo "  [2] Schwäbisch"
    echo "  [3] Bayerisch"
    echo "  [4] Sächsisch"
    echo -n "Auswahl [1-4]: "
    read -r dialect

    case "$dialect" in
        2) selected_lang="de-schwaebisch" ;;
        3) selected_lang="de-bayerisch" ;;
        4) selected_lang="de-saechsisch" ;;
        *) selected_lang="de" ;;
    esac
}

handle_spanish_selection() {
    echo ""
    echo "¿Qué variante prefieres?"
    echo "  [1] 🇪🇸 Español (Estándar)"
    echo "  [2] 🇲🇽 Mexicano"
    echo "  [3] 🇦🇷 Argentino"
    echo "  [4] 🇨🇴 Colombiano"
    echo "  [5] 🇻🇪 Venezolano"
    echo "  [6] 🇨🇱 Chileno"
    echo "  [7] 🇪🇸 Andaluz"
    echo "  [8] Català"
    echo "  [9] Euskera"
    echo "  [10] Galego"
    echo -n "Selección [1-10]: "
    read -r variant

    case "$variant" in
        2) selected_lang="es-mexicano" ;;
        3) selected_lang="es-argentino" ;;
        4) selected_lang="es-colombiano" ;;
        5) selected_lang="es-venezolano" ;;
        6) selected_lang="es-chileno" ;;
        7) selected_lang="es-andaluz" ;;
        8) selected_lang="ca" ;;
        9) selected_lang="eu" ;;
        10) selected_lang="gl" ;;
        *) selected_lang="es" ;;
    esac
}

# Function to check if query needs web search
needs_web_search() {
    local query="$1"
    local keywords=("aktuelle" "neueste" "heute" "gestern" "news" "nachrichten"
                    "current" "latest" "today" "yesterday" "wetter" "weather"
                    "stock" "aktien" "2024" "2025")

    for keyword in "${keywords[@]}"; do
        if [[ "$(echo "$query" | tr '[:upper:]' '[:lower:]')" == *"$keyword"* ]]; then
            return 0
        fi
    done
    return 1
}

# Function to perform web search
perform_web_search() {
    local query="$1"
    local dialect_prompt="$2"

    if [[ ! -z "$PERPLEXITY_API_KEY" ]]; then
        echo -e "${DIM}🔍 Searching for current information...${RESET}"

        local response=$(curl -s -X POST https://api.perplexity.ai/chat/completions \
            -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
            -H "Content-Type: application/json" \
            -d "{
                \"model\": \"${DEFAULT_PERPLEXITY_MODEL:-pplx-7b-online}\",
                \"messages\": [
                    {\"role\": \"system\", \"content\": \"${dialect_prompt}Answer in the language requested.\"},
                    {\"role\": \"user\", \"content\": \"$query\"}
                ]
            }" | jq -r '.choices[0].message.content' 2>/dev/null)

        if [[ ! -z "$response" ]] && [[ "$response" != "null" ]]; then
            echo "$response"
        else
            # Fallback to regular GPT
            sgpt --chat "$CHAT_NAME" "${dialect_prompt}$query"
        fi
    else
        # No Perplexity key, use regular GPT
        sgpt --chat "$CHAT_NAME" "${dialect_prompt}$query"
    fi
}

# Update shell configuration
update_shell_config() {
    local command="$1"
    local shell_configs=("$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.profile")

    for config in "${shell_configs[@]}"; do
        if [[ -f "$config" ]]; then
            # Remove ALL old AI Chat Terminal entries (regardless of alias name)
            grep -v "source.*shell-scripts" "$config" > "$config.tmp" && mv "$config.tmp" "$config"
            grep -v "source.*/\.aichat/aichat\.zsh" "$config" > "$config.tmp" && mv "$config.tmp" "$config"
            # Remove ANY alias pointing to ai_chat_function (smart cleanup)
            grep -v "alias.*=.*ai_chat_function" "$config" > "$config.tmp" && mv "$config.tmp" "$config"
            grep -v "# AI Chat Terminal" "$config" > "$config.tmp" && mv "$config.tmp" "$config"

            # Add new entry
            echo "" >> "$config"
            echo "# AI Chat Terminal" >> "$config"
            echo "source $HOME/.aichat/aichat.zsh" >> "$config"
            echo "alias $command='ai_chat_function'" >> "$config"
        fi
    done
}

# Chat loop and config functions would continue here...
# (Truncated for space - would include all the chat_loop, show_config_menu, etc.)

# Export the main function (quietly)
export -f ai_chat_function >/dev/null 2>&1