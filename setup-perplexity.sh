#!/bin/bash
# Setup script for Perplexity integration

echo "🔧 Setting up Perplexity for real-time web search..."
echo ""

# Check if API key exists
if [[ -z "$PERPLEXITY_API_KEY" ]]; then
    echo "📝 Get your Perplexity API key:"
    echo "1. Go to: https://www.perplexity.ai/settings/api"
    echo "2. Sign up / Sign in"
    echo "3. Generate API key"
    echo ""
    echo -n "Enter your Perplexity API key: "
    read -r api_key

    # Add to shell config
    if [[ -f ~/.zshrc ]]; then
        echo "" >> ~/.zshrc
        echo "# Perplexity API for web search" >> ~/.zshrc
        echo "export PERPLEXITY_API_KEY='$api_key'" >> ~/.zshrc
        echo "✅ Added to ~/.zshrc"
    fi

    if [[ -f ~/.bashrc ]]; then
        echo "" >> ~/.bashrc
        echo "# Perplexity API for web search" >> ~/.bashrc
        echo "export PERPLEXITY_API_KEY='$api_key'" >> ~/.bashrc
        echo "✅ Added to ~/.bashrc"
    fi
fi

echo ""
echo "📦 Installing dependencies..."

# Install jq for JSON parsing
if ! command -v jq &> /dev/null; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install jq
    elif command -v apt-get &> /dev/null; then
        sudo apt-get install -y jq
    fi
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Usage examples:"
echo "  q weather in Berlin"
echo "  q latest news about AI"
echo "  q current stock price of Apple"
echo ""
echo "Reload your shell: source ~/.zshrc"