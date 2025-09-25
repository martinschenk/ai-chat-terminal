#!/usr/bin/env zsh

# Interactive Chat Mode for sgpt with beautiful UI
# Press Ctrl+C to exit anytime

f_function() {
    local CHAT_NAME="f_chat"
    local TIMEOUT_FILE="$HOME/.config/shell_gpt/chat_sessions/last_time"
    local TIMEOUT_SECONDS=120

    # Colors and icons
    local BLUE='\033[0;34m'
    local GREEN='\033[0;32m'
    local YELLOW='\033[1;33m'
    local PURPLE='\033[0;35m'
    local CYAN='\033[0;36m'
    local RESET='\033[0m'
    local BOLD='\033[1m'

    # Create directory if needed
    mkdir -p "$HOME/.config/shell_gpt/chat_sessions"

    # Get current timestamp
    local CURRENT_TIME=$(date +%s)

    # Check for existing session
    if [[ -f "$TIMEOUT_FILE" ]]; then
        local LAST_TIME=$(cat "$TIMEOUT_FILE")
        local TIME_DIFF=$((CURRENT_TIME - LAST_TIME))

        if [[ $TIME_DIFF -gt $TIMEOUT_SECONDS ]]; then
            rm -f "/var/folders/wm/g387kdx54r79r8t48tfy9tgc0000gn/T/chat_cache/f_chat.json" 2>/dev/null
            local SESSION_STATUS="${YELLOW}🔄 Neue Chat-Session${RESET}"
        else
            local SESSION_STATUS="${GREEN}💬 Fortsetzen (${TIME_DIFF}s)${RESET}"
        fi
    else
        rm -f "/var/folders/wm/g387kdx54r79r8t48tfy9tgc0000gn/T/chat_cache/f_chat.json" 2>/dev/null
        local SESSION_STATUS="${CYAN}🚀 Neue Session${RESET}"
    fi

    # If called with arguments, execute single query
    if [[ $# -gt 0 ]]; then
        echo "$CURRENT_TIME" > "$TIMEOUT_FILE"

        # Show header
        echo -e "\n${BOLD}${PURPLE}╭─────────────────────────────────────╮${RESET}"
        echo -e "${BOLD}${PURPLE}│${RESET}  🤖 ${BOLD}AI Chat${RESET} ${SESSION_STATUS}  ${PURPLE}│${RESET}"
        echo -e "${BOLD}${PURPLE}╰─────────────────────────────────────╯${RESET}\n"

        # Show user input
        echo -e "${BLUE}👤 You:${RESET} $*\n"

        # Get and show response
        echo -e "${GREEN}🤖 AI:${RESET}"
        sgpt --chat "$CHAT_NAME" "$*"

        echo -e "\n${PURPLE}────────────────────────────────────${RESET}"
        echo -e "${CYAN}💡 Tipp: Gib nur 'f' ein für interaktiven Chat-Modus${RESET}"
        echo -e "${PURPLE}────────────────────────────────────${RESET}\n"

        return
    fi

    # Interactive mode
    clear
    echo -e "${BOLD}${PURPLE}╭═══════════════════════════════════════════╮${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}     🤖 ${BOLD}${CYAN}Interaktiver AI Chat${RESET}             ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}     ${SESSION_STATUS}                    ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}╠═══════════════════════════════════════════╣${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}  ${YELLOW}[Ctrl+C]${RESET} zum Beenden                   ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}║${RESET}  ${YELLOW}exit/quit/bye${RESET} zum Verlassen            ${PURPLE}║${RESET}"
    echo -e "${BOLD}${PURPLE}╰═══════════════════════════════════════════╯${RESET}\n"

    # Start interactive loop
    while true; do
        echo "$CURRENT_TIME" > "$TIMEOUT_FILE"

        # Simple prompt
        echo -ne "${BLUE}👤 Du ▶ ${RESET}"

        # Read full line of input
        read -r INPUT

        # Skip if empty input
        if [[ -z "$INPUT" ]]; then
            continue
        fi

        # Special commands
        if [[ "$INPUT" == "clear" ]] || [[ "$INPUT" == "cls" ]]; then
            clear
            echo -e "${BOLD}${PURPLE}╭═══════════════════════════════════════════╮${RESET}"
            echo -e "${BOLD}${PURPLE}║${RESET}     🤖 ${BOLD}${CYAN}Interaktiver AI Chat${RESET}             ${PURPLE}║${RESET}"
            echo -e "${BOLD}${PURPLE}╠═══════════════════════════════════════════╣${RESET}"
            echo -e "${BOLD}${PURPLE}║${RESET}  ${YELLOW}[Ctrl+C]${RESET} zum Beenden                   ${PURPLE}║${RESET}"
            echo -e "${BOLD}${PURPLE}║${RESET}  ${YELLOW}exit/quit/bye${RESET} zum Verlassen            ${PURPLE}║${RESET}"
            echo -e "${BOLD}${PURPLE}╰═══════════════════════════════════════════╯${RESET}\n"
            continue
        fi

        if [[ "$INPUT" == "exit" ]] || [[ "$INPUT" == "quit" ]] || [[ "$INPUT" == "bye" ]]; then
            echo -e "\n${YELLOW}👋 Chat beendet. Bis bald!${RESET}\n"
            return
        fi

        # Process with sgpt
        echo -e "${GREEN}🤖 AI ▶ ${RESET}"
        sgpt --chat "$CHAT_NAME" "$INPUT"
        echo -e "${PURPLE}───────────────────────────────────────────${RESET}\n"

        # Update timestamp for next iteration
        CURRENT_TIME=$(date +%s)
    done
}

# Export the function
export -f f_function