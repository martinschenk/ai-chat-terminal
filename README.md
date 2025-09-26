# AI Chat Terminal

A ChatGPT-powered terminal interface with integrated web search and memory.

[![Version](https://img.shields.io/badge/version-5.2.0-blue.svg)](https://github.com/martinschenk/ai-chat-terminal)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20|%20Linux-lightgrey.svg)](https://github.com/martinschenk/ai-chat-terminal)


## Features

- **ChatGPT Integration** - Powered by OpenAI's latest models (GPT-4o, GPT-4o-mini, etc.)
- **Integrated Web Search** - Real-time information via ChatGPT search capabilities
- **Conversational Memory** - Maintains context during chat sessions
- **Multi-Language Support** - 19 languages with regional dialects
- **Customizable Commands** - Use `chat`, `ai`, `ask`, or custom aliases

## Installation

```bash
curl -sL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | bash
```

After installation:
1. Run `source ~/.zshrc` to reload your shell
2. Run `chat` to start the initial setup
3. Enter your OpenAI API key when prompted

## Usage

Start by typing `chat` to enter the interactive terminal:

### Development Examples
```
/config = settings | ESC/exit = quit
─────────────────────────────────────────────────────

👤 You ▶ docker port conflict fix?
🤖 AI ▶
Kill the process using port 3000:
lsof -ti:3000 | xargs kill -9

Or use a different port:
docker run -p 3001:3000 your-app
─────────────────────────────────────────────────────

👤 You ▶ best Python linter?
🤖 AI ▶
For Python, I recommend:
- ruff (fastest, modern)
- black (formatting)
- mypy (type checking)

Install with: pip install ruff black mypy
─────────────────────────────────────────────────────

👤 You ▶ datetime?
🤖 AI ▶
Based on your local information, the current date and time is Saturday, September 27, 2025, at 00:26.
─────────────────────────────────────────────────────

👤 You ▶ latest React version?
🤖 AI ▶
As of September 27, 2025, React 19 RC is the latest version with Server Components, improved concurrent rendering, and better hydration performance.
─────────────────────────────────────────────────────

👤 You ▶ git reset last commit
🤖 AI ▶
To undo the last commit but keep changes:
git reset --soft HEAD~1

To completely remove the last commit:
git reset --hard HEAD~1
─────────────────────────────────────────────────────

👤 You ▶
```

### Quick Commands
You can also ask direct questions without entering the chat:
```bash
chat "Fix this Docker error: port already in use"
chat "Best practices for Python virtual environments"
chat "How to optimize PostgreSQL queries?"
```

### Configuration
Start chat, then type `/config` to open settings menu:

```
⚙️  CONFIGURATION

╔═══════════════════════════════════════╗
║  Current Settings:                ║
║  ├─ Command: chat                  ║
║  ├─ Language: en                 ║
║  ├─ Timeout: 3600s               ║
║  └─ ESC to exit: true          ║
╠═══════════════════════════════════════╣
║  [1] Change command character           ║
║  [2] Change language                  ║
║  [3] Change timeout                  ║
║  [4] Toggle ESC key exit            ║
║  [5] Change AI model                 ║
║  [6] 🧹 Clear chat cache              ║
║  [7] ℹ️  About & Version                ║
║  [8] Back to chat                   ║
║                                       ║
║  [9] 🗑️  Uninstall completely        ║
╚═══════════════════════════════════════╝

Select [1-9]:
```

## Configuration Options

The configuration menu provides these options:

1. **Change Command** - Switch between `chat`, `ai`, `ask`, `q`, or custom
2. **Change Language** - Select from 19 supported languages
3. **Change Timeout** - Adjust session memory duration (60-3600 seconds)
4. **Toggle ESC Exit** - Enable/disable quick exit with ESC key
5. **Change AI Model** - Select OpenAI model (GPT-4o recommended)
6. **Clear Cache** - Reset conversation history
7. **About & Version** - View version and attribution information
8. **Back to Chat** - Return to conversation
9. **Uninstall** - Complete removal with cleanup

## Requirements

- **OpenAI API Key** (required) - Get yours at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Python 3** (usually pre-installed on macOS/Linux)
- **Shell-GPT** (automatically installed)

## Supported Languages

English, German (+ Schwäbisch, Bayerisch, Sächsisch), Spanish (+ Mexican, Argentinian, Colombian, etc.), French, Italian, Catalan, Basque, Galician, Chinese (Mandarin), Hindi, and more.

## Troubleshooting

### Command already exists
If `chat` conflicts with existing commands, the installer will suggest alternatives like `ai`, `ask`, or `aic`.

### API Key Issues
Ensure your OpenAI account has sufficient credit. Start `chat` then use `/config` to update your API key.

### Shell-GPT Not Found
```bash
pip3 install --user shell-gpt
```

## Uninstall

Start `chat`, then type `/config` and select option 8 (Uninstall).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file.

## Attribution

Built on [Shell-GPT](https://github.com/TheR1D/shell_gpt) by TheR1D.