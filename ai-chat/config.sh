#!/bin/bash
# Configuration file for AI Chat Terminal

# Default settings - can be overridden by user config
AI_CHAT_COMMAND="q"           # Default command (q for question)
AI_CHAT_LANGUAGE="en"         # Default language (en, de)
AI_CHAT_TIMEOUT=120           # Session timeout in seconds
AI_CHAT_MODEL="gpt-4o-mini"   # Default AI model

# User config file location
USER_CONFIG="$HOME/.config/ai-chat/config"

# Load user config if exists
if [[ -f "$USER_CONFIG" ]]; then
    source "$USER_CONFIG"
fi

# Export for use in main script
export AI_CHAT_COMMAND
export AI_CHAT_LANGUAGE
export AI_CHAT_TIMEOUT
export AI_CHAT_MODEL