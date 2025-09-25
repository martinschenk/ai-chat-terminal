#!/bin/bash

# AI Chat Terminal - Installation Script
# This script safely installs the AI chat function without exposing API keys

set -e  # Exit on error

echo "🤖 AI Chat Terminal Installer"
echo "=============================="
echo ""

# Check for zsh
if ! command -v zsh &> /dev/null; then
    echo "❌ Error: zsh is required but not installed."
    echo "   On macOS: zsh comes pre-installed"
    echo "   On Linux: sudo apt install zsh"
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed."
    echo "   Visit: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Prerequisites checked"
echo ""

# Install shell-gpt if not installed
if ! command -v sgpt &> /dev/null; then
    echo "📦 Installing Shell GPT..."
    pip3 install shell-gpt || {
        echo "❌ Failed to install shell-gpt"
        echo "   Try: pip3 install --user shell-gpt"
        exit 1
    }
    echo "✅ Shell GPT installed"
else
    echo "✅ Shell GPT already installed"
fi

echo ""

# Setup directories
INSTALL_DIR="$HOME/ai-chat-terminal"
echo "📁 Setting up directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR/ai-chat"
cp -r ai-chat/* "$INSTALL_DIR/ai-chat/" 2>/dev/null || true

# Check for API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo ""
    echo "⚠️  No OpenAI API key found in environment!"
    echo ""
    echo "To set your API key, add this to ~/.zshrc:"
    echo ""
    echo "   export OPENAI_API_KEY=\"sk-your-key-here\""
    echo ""
    echo "Get your key at: https://platform.openai.com/api-keys"
    echo ""
    read -p "Enter your OpenAI API key (or press Enter to skip): " api_key

    if [ ! -z "$api_key" ]; then
        echo "" >> ~/.zshrc
        echo "# OpenAI API Key for AI Chat Terminal" >> ~/.zshrc
        echo "export OPENAI_API_KEY=\"$api_key\"" >> ~/.zshrc
        echo "✅ API key added to ~/.zshrc"
    fi
else
    echo "✅ OpenAI API key found"
fi

# Add to zshrc if not already there
if ! grep -q "f_function.zsh" ~/.zshrc 2>/dev/null; then
    echo "" >> ~/.zshrc
    echo "# AI Chat Terminal" >> ~/.zshrc
    echo "source $INSTALL_DIR/ai-chat/f_function.zsh" >> ~/.zshrc
    echo 'alias f="noglob f_function"' >> ~/.zshrc
    echo "✅ Added to ~/.zshrc"
else
    echo "✅ Already configured in ~/.zshrc"
fi

# Create config directory
mkdir -p ~/.config/shell_gpt

# Configure sgpt if not configured
if [ ! -f ~/.config/shell_gpt/.sgptrc ]; then
    cat > ~/.config/shell_gpt/.sgptrc << 'EOF'
CHAT_CACHE_PATH=/tmp/chat_cache
CACHE_PATH=/tmp/cache
CHAT_CACHE_LENGTH=100
CACHE_LENGTH=100
REQUEST_TIMEOUT=60
DEFAULT_MODEL=gpt-4o-mini
DEFAULT_COLOR=magenta
ROLE_STORAGE_PATH=$HOME/.config/shell_gpt/roles
DEFAULT_EXECUTE_SHELL_CMD=false
DISABLE_STREAMING=false
CODE_THEME=dracula
EOF
    echo "✅ Configured Shell GPT"
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "To start using AI Chat Terminal:"
echo ""
echo "  1. Reload your shell:  source ~/.zshrc"
echo "  2. Quick mode:         f What is the weather?"
echo "  3. Interactive mode:   f"
echo ""
echo "Enjoy! 🚀"