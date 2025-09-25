# 🤖 AI Chat Terminal

A beautiful, interactive AI chat interface for your terminal using Shell GPT (sgpt). Features a clean UI with colors, emoji icons, and smart session management.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Shell](https://img.shields.io/badge/shell-zsh-green)
![License](https://img.shields.io/badge/license-MIT-purple)

## ✨ Features

- 🎨 **Beautiful Terminal UI** - Colorful interface with emoji icons
- 💬 **Smart Context Management** - Maintains conversation context for 2 minutes
- 🚀 **Two Modes**:
  - **Quick Mode**: `f your question here` for single queries
  - **Interactive Mode**: Just type `f` to enter chat mode
- 🔄 **Auto Session Management** - Automatically starts new sessions after timeout
- ⚡ **Fast & Lightweight** - Pure shell script, no heavy dependencies
- 🎯 **GPT-4 Mini** - Uses OpenAI's fast and cost-effective model

## 📸 Screenshots

### Quick Mode
```
╭─────────────────────────────────────╮
│  🤖 AI Chat 💬 Fortsetzen (13s)    │
╰─────────────────────────────────────╯

👤 You: What is 2+2?

🤖 AI:
2 + 2 equals 4.

────────────────────────────────────
💡 Tipp: Gib nur 'f' ein für interaktiven Chat-Modus
────────────────────────────────────
```

### Interactive Mode
```
╭═══════════════════════════════════════════╮
║     🤖 Interaktiver AI Chat               ║
║     💬 Fortsetzen (5s)                    ║
╠═══════════════════════════════════════════╣
║  [Ctrl+C] zum Beenden                     ║
║  exit/quit/bye zum Verlassen              ║
╰═══════════════════════════════════════════╯

👤 Du ▶ Hello!
🤖 AI ▶
Hello! How can I help you today?
───────────────────────────────────────────

👤 Du ▶ _
```

## 🚀 Installation

### Prerequisites

1. **zsh** shell (comes with macOS)
2. **Python 3.8+**
3. **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))

### Quick Install

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/ai-chat-terminal.git
cd ai-chat-terminal

# 2. Run the installer
./install.sh

# 3. Set your OpenAI API key
export OPENAI_API_KEY="your-key-here"

# 4. Reload your shell
source ~/.zshrc

# 5. Start chatting!
f Hello AI!
```

### Manual Installation

```bash
# 1. Install Shell GPT
pip install shell-gpt

# 2. Clone this repo
git clone https://github.com/yourusername/ai-chat-terminal.git

# 3. Add to your ~/.zshrc
echo 'source ~/ai-chat-terminal/ai-chat/f_function.zsh' >> ~/.zshrc
echo 'alias f="noglob f_function"' >> ~/.zshrc

# 4. Set OpenAI API key in ~/.zshrc
echo 'export OPENAI_API_KEY="your-key-here"' >> ~/.zshrc

# 5. Reload
source ~/.zshrc
```

## 🎮 Usage

### Quick Questions
```bash
f what is the weather in Berlin?
f translate "Hello" to Spanish
f explain quantum computing in simple terms
```

### Interactive Chat Mode
```bash
# Start interactive mode
f

# Then just type naturally:
> Hello!
> What's 2+2?
> Tell me a joke
> exit  # or press Ctrl+C to quit
```

### Special Commands in Interactive Mode
- `clear` or `cls` - Clear the screen
- `exit`, `quit`, `bye` - Exit chat mode
- `Ctrl+C` - Quick exit

## ⚙️ Configuration

### Customize Timeout
Edit `~/ai-chat-terminal/ai-chat/f_function.zsh`:
```bash
local TIMEOUT_SECONDS=120  # Change to desired seconds (default: 2 minutes)
```

### Change AI Model
Create/edit `~/.config/shell_gpt/.sgptrc`:
```bash
DEFAULT_MODEL=gpt-4o-mini  # Options: gpt-4o, gpt-4o-mini, gpt-3.5-turbo
CHAT_CACHE_LENGTH=100       # Number of messages to keep in history
```

### Customize Colors
The script uses ANSI color codes. You can modify them in the script:
```bash
local BLUE='\033[0;34m'    # User messages
local GREEN='\033[0;32m'   # AI messages
local PURPLE='\033[0;35m'  # Borders
local YELLOW='\033[1;33m'  # Warnings
```

## 🗂️ File Structure

```
ai-chat-terminal/
├── README.md               # This file
├── LICENSE                 # MIT License
├── install.sh             # Installation script
├── .env.example           # Example environment variables
├── .gitignore            # Git ignore file
└── ai-chat/
    └── f_function.zsh    # Main chat function
```

## 🔒 Security

- **Never commit API keys!** Use environment variables
- API keys should be in `~/.zshrc` or `~/.env`, never in the script
- The `.gitignore` excludes sensitive files

## 🐛 Troubleshooting

### "Command not found: f"
```bash
source ~/.zshrc
```

### "API key not set"
```bash
export OPENAI_API_KEY="your-key-here"
```

### Colors not showing correctly
Make sure your terminal supports ANSI colors. Try:
- iTerm2 (macOS)
- Terminal.app (macOS)
- Windows Terminal (Windows)

### Chat history not persisting
Check the cache directory:
```bash
ls -la ~/.config/shell_gpt/chat_sessions/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Shell GPT](https://github.com/TheR1D/shell_gpt) - The awesome tool that powers this chat
- OpenAI for providing the GPT API
- The zsh community for the great shell

## 💡 Tips & Tricks

- Use `f` for quick questions during coding
- Keep context alive by asking follow-up questions within 2 minutes
- Use interactive mode for longer conversations
- Clear chat history: `rm -rf /tmp/chat_cache/f_chat`

## 📊 Stats

- ⚡ Response time: ~1-2 seconds
- 💾 Cache size: <1MB
- 🔋 Resource usage: Minimal
- 🌍 Works offline: No (requires API connection)

---

Made with ❤️ for the terminal lovers

**Star ⭐ this repo if you find it useful!**