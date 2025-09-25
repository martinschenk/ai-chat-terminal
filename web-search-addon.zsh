#!/bin/zsh
# Web Search Add-on for AI Chat Terminal
# Adds real-time web search capabilities

# Configuration
SEARCH_PROVIDER="${AI_CHAT_SEARCH_PROVIDER:-perplexity}"  # perplexity, tavily, serp
PERPLEXITY_API_KEY="${PERPLEXITY_API_KEY:-}"
TAVILY_API_KEY="${TAVILY_API_KEY:-}"
SERP_API_KEY="${SERP_API_KEY:-}"

# Function to detect if query needs web search
needs_web_search() {
    local query="$1"
    local keywords=(
        "aktuelle" "neueste" "heute" "gestern" "news" "nachrichten"
        "current" "latest" "today" "yesterday" "recent"
        "wetter" "weather" "stock" "aktien" "preis" "price"
        "2024" "2025" "letzte woche" "last week"
    )

    for keyword in "${keywords[@]}"; do
        if [[ "${query,,}" == *"$keyword"* ]]; then
            return 0
        fi
    done
    return 1
}

# Perplexity Search (with real-time data)
search_perplexity() {
    local query="$1"

    if [[ -z "$PERPLEXITY_API_KEY" ]]; then
        echo "⚠️ Perplexity API key not set. Add to ~/.zshrc: export PERPLEXITY_API_KEY='your-key'"
        return 1
    fi

    local response=$(curl -s -X POST https://api.perplexity.ai/chat/completions \
        -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"pplx-7b-online\",
            \"messages\": [
                {\"role\": \"user\", \"content\": \"$query\"}
            ]
        }")

    echo "$response" | jq -r '.choices[0].message.content' 2>/dev/null || echo "$response"
}

# Tavily Search (specialized search API)
search_tavily() {
    local query="$1"

    if [[ -z "$TAVILY_API_KEY" ]]; then
        echo "⚠️ Tavily API key not set. Get one at https://tavily.com"
        return 1
    fi

    local response=$(curl -s -X POST https://api.tavily.com/search \
        -H "Content-Type: application/json" \
        -d "{
            \"api_key\": \"$TAVILY_API_KEY\",
            \"query\": \"$query\",
            \"search_depth\": \"basic\",
            \"include_answer\": true
        }")

    local answer=$(echo "$response" | jq -r '.answer' 2>/dev/null)
    local results=$(echo "$response" | jq -r '.results[:3] | .[] | "• \(.title): \(.snippet)"' 2>/dev/null)

    echo "📊 Web Search Results:"
    echo "$answer"
    echo ""
    echo "$results"
}

# Enhanced chat function with web search
ai_chat_with_search() {
    local query="$1"

    # Check if web search is needed
    if needs_web_search "$query"; then
        echo "🔍 Searching web for current information..."

        case "$SEARCH_PROVIDER" in
            perplexity)
                search_perplexity "$query"
                ;;
            tavily)
                # First get web results
                local web_results=$(search_tavily "$query")
                echo "$web_results"
                echo ""
                echo "🤖 AI Analysis:"
                # Then pass to GPT with context
                sgpt --chat "${COMMAND_CHAR}_chat" "Based on these web results: $web_results\n\nUser question: $query"
                ;;
            *)
                # Fallback to regular GPT
                echo "⚠️ Using standard AI without web search"
                sgpt --chat "${COMMAND_CHAR}_chat" "$query"
                ;;
        esac
    else
        # Regular chat without web search
        sgpt --chat "${COMMAND_CHAR}_chat" "$query"
    fi
}

# Option 2: Using OpenAI with function calling (requires gpt-4)
setup_openai_functions() {
    cat > ~/.config/shell_gpt/functions/web_search.py << 'EOF'
import json
import requests
from datetime import datetime

def web_search(query: str) -> str:
    """Search the web for current information."""
    # This would call your preferred search API
    # For now, returning a placeholder
    return json.dumps({
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "results": [
            "This would contain real search results",
            "You need to implement the actual search API call"
        ]
    })
EOF
}

# Export functions for use in chat.zsh
export -f needs_web_search
export -f search_perplexity
export -f search_tavily
export -f ai_chat_with_search