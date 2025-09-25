#!/bin/zsh
# AI Chat Terminal - Configuration Menu
# Part 3 - Config and Uninstall functions

# Configuration menu function
show_config_menu() {
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
    local TIMEOUT="${AI_CHAT_TIMEOUT:-600}"
    local ENABLE_ESC="${AI_CHAT_ESC_EXIT:-true}"
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
    echo -e "${PURPLE}║${RESET}  ${GREEN}[8]${RESET} 🔍 ${LANG_CONFIG_OPT8}         ${PURPLE}║${RESET}"
    echo -e "${PURPLE}║${RESET}                                       ${PURPLE}║${RESET}"
    echo -e "${PURPLE}║${RESET}  ${RED}[9]${RESET} 🗑️  ${LANG_CONFIG_OPT9}        ${PURPLE}║${RESET}"
    echo -e "${PURPLE}╚═══════════════════════════════════════╝${RESET}"
    echo ""

    echo -ne "${CYAN}${LANG_CONFIG_SELECT} ${RESET}"
    read -r choice

    case $choice in
        1)  # Change command
            change_command
            ;;
        2)  # Change language
            change_language
            ;;
        3)  # Change timeout
            change_timeout
            ;;
        4)  # Toggle ESC
            toggle_esc
            ;;
        5)  # Change AI model
            change_ai_model
            ;;
        6)  # Back to chat
            return
            ;;
        7)  # Clear cache
            clear_chat_cache
            ;;
        8)  # Configure web search
            configure_web_search
            ;;
        9)  # Uninstall
            uninstall_terminal
            ;;
    esac
}

# Change command function
change_command() {
    echo -e "\n${CYAN}Choose new command:${RESET}"
    echo "  [1] ai   - Clear and memorable"
    echo "  [2] ask  - Natural for questions"
    echo "  [3] q    - Quick single letter"
    echo "  [4] ??   - Double question mark"
    echo "  [5] chat - Descriptive"
    echo "  [6] Custom"
    echo -n "Select [1-6]: "
    read -r cmd_choice

    local new_cmd=""
    case "$cmd_choice" in
        1) new_cmd="ai" ;;
        2) new_cmd="ask" ;;
        3) new_cmd="q" ;;
        4) new_cmd="??" ;;
        5) new_cmd="chat" ;;
        6)
            echo -n "Enter custom command: "
            read -r new_cmd
            ;;
    esac

    if [[ ! -z "$new_cmd" ]]; then
        # Update config
        sed -i '' "s/AI_CHAT_COMMAND=.*/AI_CHAT_COMMAND=\"$new_cmd\"/" "$CONFIG_FILE"

        # Update shell alias
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

    # Clear from temp directory
    if [[ -d "/var/folders" ]]; then
        find /var/folders -name "*_chat" -type f 2>/dev/null | while read cache_file; do
            if [[ -w "$cache_file" ]]; then
                rm -f "$cache_file" 2>/dev/null && cache_cleared=true
                echo -e "  ${GREEN}✓${RESET} Cleared: $(basename $cache_file)"
            fi
        done
    fi

    # Clear from ~/.config/shell_gpt/chat_sessions
    if [[ -d "$HOME/.config/shell_gpt/chat_sessions" ]]; then
        find "$HOME/.config/shell_gpt/chat_sessions" -type f ! -name ".gitkeep" -delete 2>/dev/null
        cache_cleared=true
    fi

    if [[ "$cache_cleared" == "true" ]]; then
        echo -e "\n${GREEN}✅ Cache cleared successfully!${RESET}"
    else
        echo -e "\n${YELLOW}No cache files found.${RESET}"
    fi
    sleep 2
}

# Configure web search
configure_web_search() {
    echo -e "\n${CYAN}Web Search Configuration:${RESET}\n"

    if [[ -z "$PERPLEXITY_API_KEY" ]]; then
        echo "Enable real-time web search for current information!"
        echo ""
        echo "1. Get your API key at: https://perplexity.ai/settings/api"
        echo "2. Free tier available!"
        echo ""
        echo -n "Enter your Perplexity API key (or press Enter to skip): "
        read -r pplx_key

        if [[ ! -z "$pplx_key" ]]; then
            # Update .env file
            if grep -q "PERPLEXITY_API_KEY" "$ENV_FILE"; then
                sed -i '' "s/PERPLEXITY_API_KEY=.*/PERPLEXITY_API_KEY=\"$pplx_key\"/" "$ENV_FILE"
            else
                echo "PERPLEXITY_API_KEY=\"$pplx_key\"" >> "$ENV_FILE"
            fi

            # Select model
            echo -e "\n${CYAN}Select Perplexity Model:${RESET}"
            echo "  [1] pplx-7b-online  ⭐ RECOMMENDED"
            echo "  [2] pplx-70b-online"
            echo "  [3] sonar-small-online"
            echo "  [4] sonar-medium-online"
            echo -n "Select [1-4] (default: 1): "
            read -r model_choice

            local pplx_model="pplx-7b-online"
            case "$model_choice" in
                2) pplx_model="pplx-70b-online" ;;
                3) pplx_model="sonar-small-online" ;;
                4) pplx_model="sonar-medium-online" ;;
            esac

            # Update model in .env
            if grep -q "DEFAULT_PERPLEXITY_MODEL" "$ENV_FILE"; then
                sed -i '' "s/DEFAULT_PERPLEXITY_MODEL=.*/DEFAULT_PERPLEXITY_MODEL=\"$pplx_model\"/" "$ENV_FILE"
            else
                echo "DEFAULT_PERPLEXITY_MODEL=\"$pplx_model\"" >> "$ENV_FILE"
            fi

            echo -e "${GREEN}✅ Web search enabled!${RESET}"
        fi
    else
        echo -e "${GREEN}✅ Web search is already configured!${RESET}"
        echo ""
        echo "Current model: ${DEFAULT_PERPLEXITY_MODEL:-pplx-7b-online}"
        echo ""
        echo -n "Remove web search? (y/N): "
        read -r remove

        if [[ "$remove" == "y" ]] || [[ "$remove" == "Y" ]]; then
            sed -i '' '/PERPLEXITY_API_KEY/d' "$ENV_FILE"
            sed -i '' '/DEFAULT_PERPLEXITY_MODEL/d' "$ENV_FILE"
            echo -e "${YELLOW}Web search disabled.${RESET}"
        fi
    fi
    sleep 2
}

# Uninstall function with translations
uninstall_terminal() {
    clear
    echo -e "${RED}${BOLD}⚠️  ${LANG_CONFIG_OPT9}${RESET}"
    echo ""
    echo "${LANG_UNINSTALL_WARNING}"
    echo ""
    echo "• AI Chat Terminal"
    echo "• ~/shell-scripts-new"
    echo "• ~/.config/ai-chat"
    echo ""
    echo -e "${YELLOW}${LANG_UNINSTALL_WARNING}${RESET}"
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

        # Remove from shell configs
        local configs=("$HOME/.zshrc" "$HOME/.bashrc" "$HOME/.profile")
        for config in "${configs[@]}"; do
            if [[ -f "$config" ]]; then
                grep -v "source.*shell-scripts" "$config" > "$config.tmp" && mv "$config.tmp" "$config"
                grep -v "alias.*ai_chat_function" "$config" > "$config.tmp" && mv "$config.tmp" "$config"
                echo "  ✓ ${LANG_UNINSTALL_CLEANED} $config"
            fi
        done

        # Remove directories
        if [[ -d "$HOME/shell-scripts-new" ]]; then
            rm -rf "$HOME/.aichat"
            echo "  ✓ ${LANG_UNINSTALL_REMOVED} ~/shell-scripts-new"
        fi

        if [[ -d "$HOME/.config/ai-chat" ]]; then
            rm -rf "$HOME/.aichat"
            echo "  ✓ ${LANG_UNINSTALL_REMOVED} ~/.config/ai-chat"
        fi

        echo ""
        echo -e "${GREEN}✓ ${LANG_UNINSTALL_SUCCESS}${RESET}"
        echo ""
        echo "${LANG_UNINSTALL_RESTART}"
        echo "  source ~/.zshrc"
        echo ""
        echo "${LANG_UNINSTALL_GOODBYE}"
        echo ""
        echo "${LANG_UNINSTALL_ANYKEY}"
        read -n1 -r
        exit 0
    else
        echo -e "${GREEN}Cancelled.${RESET}"
        sleep 2
    fi
}