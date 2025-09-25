# 🤖 AI Chat Terminal

A beautiful, interactive AI chat interface for your terminal with multi-language support and customizable commands.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Shell](https://img.shields.io/badge/shell-zsh-green)
![License](https://img.shields.io/badge/license-MIT-purple)
![Languages](https://img.shields.io/badge/languages-EN%20|%20DE-orange)

## ✨ Features

- 🎨 **Beautiful Terminal UI** - Colorful interface with emoji icons
- 🌍 **Multi-language Support** - English and German included, easily extensible
- ⚙️ **Configurable Command** - Choose your own trigger character (default: `q`)
- 💬 **Smart Context Management** - Maintains conversation for 2 minutes
- 🚀 **Two Modes**:
  - **Quick Mode**: `q your question here` for single queries
  - **Interactive Mode**: Just type `q` to enter chat mode
- 🔄 **Auto Session Management** - Automatically starts new sessions after timeout
- ⚡ **Fast & Lightweight** - Pure shell script, no heavy dependencies

## 📸 Screenshots

### Quick Mode
```
╭─────────────────────────────────────╮
│  🤖 AI Chat 💬 Continue (13s)      │
╰─────────────────────────────────────╯

👤 You: What is 2+2?

🤖 AI:
2 + 2 equals 4.

────────────────────────────────────
💡 Tip: Type just 'q' to enter interactive chat mode
────────────────────────────────────
```

### Interactive Mode
```
╭═══════════════════════════════════════════╮
║     🤖 Interactive AI Chat                ║
║     💬 Continue (5s)                      ║
╠═══════════════════════════════════════════╣
║  [Ctrl+C] to exit                         ║
║  exit/quit/bye to leave                   ║
╰═══════════════════════════════════════════╯

👤 You ▶ Hello!
🤖 AI ▶
Hello! How can I help you today?
───────────────────────────────────────────
```

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/martinschenk/ai-chat-terminal.git
cd ai-chat-terminal
./install.sh

# Start chatting!
q Hello AI!
```

## 📦 Installation

### Prerequisites

1. **zsh** shell (comes with macOS)
2. **Python 3.8+**
3. **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))

### Automatic Installation

The installer will guide you through setup:

```bash
./install.sh
```

During installation, you can:
- Choose your command character (default: `q`)
- Select your language (English or German)
- Enter your OpenAI API key

### Manual Installation

```bash
# 1. Install Shell GPT
pip install shell-gpt

# 2. Clone this repo
git clone https://github.com/martinschenk/ai-chat-terminal.git

# 3. Copy files
cp -r ai-chat-terminal/ai-chat ~/ai-chat-terminal/

# 4. Add to ~/.zshrc
echo 'source ~/ai-chat-terminal/ai-chat/config.sh' >> ~/.zshrc
echo 'source ~/ai-chat-terminal/ai-chat/ai_chat.zsh' >> ~/.zshrc
echo 'alias q="noglob ai_chat_function"' >> ~/.zshrc
echo 'alias ai-chat-config="ai_chat_config"' >> ~/.zshrc

# 5. Set API key
echo 'export OPENAI_API_KEY="your-key-here"' >> ~/.zshrc

# 6. Reload
source ~/.zshrc
```

## 🎮 Usage

### Quick Questions
```bash
q what is the weather in Berlin?
q translate "Hello" to Spanish
q explain quantum computing
```

### Interactive Chat Mode
```bash
# Start interactive mode
q

# Then just type naturally:
> Hello!
> What's 2+2?
> Tell me a joke
> exit  # or press Ctrl+C to quit
```

### Configuration Menu
```bash
ai-chat-config
```

This opens an interactive menu to:
- Change command character
- Switch language
- Adjust timeout settings
- Reset to defaults

## ⚙️ Configuration

### Change Command Character

Want to use `ai` instead of `q`? Run:
```bash
ai-chat-config
# Select option 1
# Enter: ai
```

### Available Languages

- **English** (`en`) - Default
- **German** (`de`) - Deutsch

Switch language:
```bash
ai-chat-config
# Select option 2
# Enter: de
```

### Add Your Own Language

1. Copy an existing language file:
```bash
cp ai-chat/languages/en.conf ai-chat/languages/es.conf
```

2. Edit the translations in `es.conf`

3. Set your language:
```bash
ai-chat-config
# Select option 2
# Enter: es
```

## 🌍 Language Development

Contributing a new language is easy! Create a new file in `ai-chat/languages/` with your language code (e.g., `fr.conf` for French) and translate these keys:

```bash
# UI Headers
LANG_HEADER_TITLE="Interactive AI Chat"
LANG_HEADER_NEW_SESSION="New Session"
LANG_HEADER_CONTINUE="Continue"
LANG_HEADER_NEW_CHAT="New Chat Session"

# UI Labels
LANG_LABEL_YOU="You"
LANG_LABEL_AI="AI"

# Instructions
LANG_INST_EXIT="to exit"
LANG_INST_SEND="to send"
LANG_INST_LEAVE="to leave"
LANG_HINT_INTERACTIVE="Tip: Type just 'COMMAND_CHAR' to enter interactive chat mode"

# Messages
LANG_MSG_GOODBYE="Chat ended. Goodbye!"
LANG_MSG_CLEARED="Screen cleared"

# Status Messages
LANG_STATUS_SECONDS="s"
LANG_STATUS_AGO="ago"
```

## 🗂️ Project Structure

```
ai-chat-terminal/
├── README.md                 # This file
├── LICENSE                   # MIT License
├── install.sh               # Installation script
├── .env.example            # Example environment variables
├── .gitignore             # Git ignore file
└── ai-chat/
    ├── ai_chat.zsh        # Main chat function
    ├── config.sh          # Configuration loader
    └── languages/         # Language packs
        ├── en.conf        # English
        └── de.conf        # German
```

## 🔒 Security

- **Never commit API keys!**
- API keys are stored in environment variables
- The `.env.example` shows the format without real keys
- User configuration is stored locally in `~/.config/ai-chat/`

## 🐛 Troubleshooting

### "Command not found: q"
```bash
source ~/.zshrc
```

### "API key not set"
```bash
export OPENAI_API_KEY="your-key-here"
# Add to ~/.zshrc to make permanent
```

### Change the command after installation
```bash
ai-chat-config
# Or manually edit ~/.config/ai-chat/config
```

### Reset everything
```bash
rm -rf ~/.config/ai-chat
rm -rf ~/ai-chat-terminal
# Remove lines from ~/.zshrc
```

## 🤝 Contributing

Contributions are welcome! Especially:
- New language translations
- UI improvements
- Bug fixes

### How to Contribute

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/NewLanguage`)
3. Commit changes (`git commit -m 'Add French language support'`)
4. Push to branch (`git push origin feature/NewLanguage`)
5. Open a Pull Request

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Credits

- [Shell GPT](https://github.com/TheR1D/shell_gpt) - The AI backend
- OpenAI for GPT API
- Contributors and translators

## 💡 Tips

- Keep conversations contextual by responding within 2 minutes
- Use `clear` in chat mode to clean the screen
- Customize timeout in config: `AI_CHAT_TIMEOUT=300` for 5 minutes
- Create aliases for different personalities:
  ```bash
  alias code="q write code for"
  alias explain="q explain simply"
  ```

## 🚦 Requirements

- **OS**: macOS, Linux
- **Shell**: zsh
- **Python**: 3.8+
- **Network**: Internet connection for API calls

## 📊 Performance

- ⚡ Response time: ~1-2 seconds
- 💾 Cache size: <1MB per session
- 🔋 CPU usage: Minimal
- 🌐 Bandwidth: ~1KB per message

---

Made with ❤️ for the terminal community

**⭐ Star this repo if you find it useful!**

## 🎯 Roadmap

- [ ] More languages (Spanish, French, Japanese)
- [ ] Vim mode support
- [ ] Custom themes
- [ ] Conversation export
- [ ] Offline mode with local models
- [ ] Plugin system

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/martinschenk/ai-chat-terminal/issues)
- **Discussions**: [GitHub Discussions](https://github.com/martinschenk/ai-chat-terminal/discussions)