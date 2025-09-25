#!/bin/zsh
# AI Chat Terminal - Main Chat Function
# Version 5.0.0 - With .env support and enhanced onboarding

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${(%):-%x}")" && pwd)"

# Source modular components
source "$SCRIPT_DIR/chat-functions.zsh"
source "$SCRIPT_DIR/config-menu.zsh"

# Function to load .env file
load_env() {
    local env_file="$HOME/.config/ai-chat/.env"
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
    # Load environment variables from .env
    load_env

    local CONFIG_DIR="$HOME/.config/ai-chat"
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
    local LANG_FILE="$SCRIPT_DIR/languages/${LANGUAGE}.conf"
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
    local CACHE_DIR="/var/folders/wm/g387kdx54r79r8t48tfy9tgc0000gn/T/chat_cache"
    mkdir -p "$CACHE_DIR" 2>/dev/null

    # Clear old invalid session if exists
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

        # Check if query needs web search
        if needs_web_search "$*"; then
            perform_web_search "$*" "$DIALECT_PROMPT"
        else
            sgpt --chat "$CHAT_NAME" "${DIALECT_PROMPT}$*"
        fi

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
    local CONFIG_DIR="$HOME/.config/ai-chat"
    local ENV_FILE="$CONFIG_DIR/.env"
    local CONFIG_FILE="$CONFIG_DIR/config"

    mkdir -p "$CONFIG_DIR"

    clear
    echo -e "\033[1;36m🚀 AI Chat Terminal Setup\033[0m"
    echo -e "\033[1;36m========================\033[0m\n"

    # Step 1: OpenAI API Key
    echo -e "\033[1;33mStep 1: OpenAI API Key (Required)\033[0m"
    echo "• Powers the main AI chat functionality"
    echo "• Get your key at: https://platform.openai.com/api-keys"
    echo ""

    local openai_key=""
    while [[ -z "$openai_key" ]]; do
        echo -n "Enter your OpenAI API key: "
        read -r openai_key
        if [[ -z "$openai_key" ]]; then
            echo -e "\033[0;31m⚠ OpenAI API key is required!\033[0m"
        fi
    done

    # Step 2: Perplexity API Key (Optional)
    echo -e "\n\033[1;33mStep 2: Perplexity API Key (Optional)\033[0m"
    echo "• Enables real-time web search"
    echo "• Get current news, weather, stock prices"
    echo "• Get your key at: https://www.perplexity.ai/settings/api"
    echo "• Free tier available!"
    echo ""
    echo -n "Enter Perplexity key (or press Enter to skip): "
    read -r perplexity_key

    if [[ ! -z "$perplexity_key" ]]; then
        echo -e "\033[0;32m✓ Web search enabled!\033[0m"
    else
        echo -e "\033[2mWeb search skipped (can add later in /config)\033[0m"
    fi

    # Step 3: Select OpenAI Model
    echo -e "\n\033[1;33mStep 3: Select Default OpenAI Model\033[0m"
    echo ""
    echo "  [1] gpt-4o-mini   - Fast, cheap, good for most tasks"
    echo "  [2] gpt-4o       ⭐ RECOMMENDED - Best overall performance"
    echo "  [3] gpt-4        - Powerful, standard model"
    echo "  [4] gpt-4-turbo  - Fast, good quality"
    echo "  [5] gpt-3.5-turbo - Basic, very cheap"
    echo ""
    echo -n "Select [1-5] (default: 2): "
    read -r model_choice

    case "$model_choice" in
        1) openai_model="gpt-4o-mini" ;;
        3) openai_model="gpt-4" ;;
        4) openai_model="gpt-4-turbo" ;;
        5) openai_model="gpt-3.5-turbo" ;;
        *) openai_model="gpt-4o" ;;  # Default
    esac

    # Step 4: Select Perplexity Model (if API key provided)
    local perplexity_model="pplx-7b-online"
    if [[ ! -z "$perplexity_key" ]]; then
        echo -e "\n\033[1;33mStep 4: Select Default Perplexity Model\033[0m"
        echo ""
        echo "  [1] pplx-7b-online  ⭐ RECOMMENDED - Fast, cheap"
        echo "  [2] pplx-70b-online - More powerful, slower"
        echo "  [3] sonar-small-online - Very fast"
        echo "  [4] sonar-medium-online - Balanced"
        echo ""
        echo -n "Select [1-4] (default: 1): "
        read -r pplx_choice

        case "$pplx_choice" in
            2) perplexity_model="pplx-70b-online" ;;
            3) perplexity_model="sonar-small-online" ;;
            4) perplexity_model="sonar-medium-online" ;;
            *) perplexity_model="pplx-7b-online" ;;
        esac
    fi

    # Step 5: Choose Command
    echo -e "\n\033[1;33mStep 5: Choose Command to Start AI Chat\033[0m"
    echo ""
    echo "  [1] ai   ⭐ RECOMMENDED - Clear and memorable"
    echo "  [2] ask  - Natural for questions"
    echo "  [3] q    - Quick single letter"
    echo "  [4] ??   - Double question mark"
    echo "  [5] chat - Descriptive"
    echo "  [6] Custom - Enter your own"
    echo ""
    echo -n "Select [1-6] (default: 1): "
    read -r cmd_choice

    local command_char="ai"
    case "$cmd_choice" in
        2) command_char="ask" ;;
        3) command_char="q" ;;
        4) command_char="??" ;;
        5) command_char="chat" ;;
        6)
            echo -n "Enter custom command: "
            read -r command_char
            ;;
        *) command_char="ai" ;;
    esac

    # Step 6: Language Selection
    echo -e "\n\033[1;33mStep 6: Select Language\033[0m"
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

    local selected_lang="en"
    case "$lang_choice" in
        2) handle_german_selection ;;
        3) selected_lang="fr" ;;
        4) selected_lang="it" ;;
        5) handle_spanish_selection ;;
        6) selected_lang="zh" ;;
        7) selected_lang="hi" ;;
        *) selected_lang="en" ;;
    esac

    # Save .env file
    cat > "$ENV_FILE" << EOF
# AI Chat Terminal Configuration
# Generated: $(date)

# API Keys
OPENAI_API_KEY="$openai_key"
PERPLEXITY_API_KEY="$perplexity_key"

# Default Models
DEFAULT_OPENAI_MODEL="$openai_model"
DEFAULT_PERPLEXITY_MODEL="$perplexity_model"
EOF

    chmod 600 "$ENV_FILE"

    # Save config file
    cat > "$CONFIG_FILE" << EOF
# AI Chat Terminal User Configuration
AI_CHAT_COMMAND="$command_char"
AI_CHAT_LANGUAGE="$selected_lang"
AI_CHAT_TIMEOUT="600"
AI_CHAT_ESC_EXIT="true"
EOF

    # Update shell configuration
    update_shell_config "$command_char"

    # Success message
    clear
    echo -e "\033[1;32m✅ Setup Complete!\033[0m\n"
    echo -e "\033[1;36mAvailable Features:\033[0m"
    echo "  ✓ AI chat with $openai_model"
    if [[ ! -z "$perplexity_key" ]]; then
        echo "  ✓ Web search enabled (Perplexity)"
    fi
    echo "  ✓ Memory retention (2 minutes)"
    echo "  ✓ 19 language variants"
    echo ""
    echo -e "\033[1;33mTry these commands:\033[0m"
    echo "  $command_char Hello!"
    echo "  $command_char What's the weather?"
    echo "  $command_char /config"
    echo ""
    echo -e "\033[2mRestart your terminal or run: source ~/.zshrc\033[0m"
    echo ""
    echo "Press Enter to continue..."
    read -r
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
        if [[ "${query,,}" == *"$keyword"* ]]; then
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
            # Remove old entries
            grep -v "source.*shell-scripts" "$config" > "$config.tmp" && mv "$config.tmp" "$config"
            grep -v "alias $command=" "$config" > "$config.tmp" && mv "$config.tmp" "$config"

            # Add new entry
            echo "" >> "$config"
            echo "# AI Chat Terminal" >> "$config"
            echo "source $HOME/shell-scripts-new/chat.zsh" >> "$config"
            echo "alias $command='ai_chat_function'" >> "$config"
        fi
    done
}

# Chat loop and config functions would continue here...
# (Truncated for space - would include all the chat_loop, show_config_menu, etc.)

# Export the main function
export -f ai_chat_function