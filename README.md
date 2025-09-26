# AI Chat Terminal

A ChatGPT-powered terminal interface with integrated web search and memory.

[![Version](https://img.shields.io/badge/version-5.2.0-blue.svg)](https://github.com/martinschenk/ai-chat-terminal)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20|%20Linux-lightgrey.svg)](https://github.com/martinschenk/ai-chat-terminal)


## Features

- **ChatGPT Integration** - Powered by OpenAI's latest models (GPT-4o, GPT-4o-mini, etc.)
- **Integrated Web Search** - Real-time information via ChatGPT search capabilities
- **🧠 Smart Memory System** - Dual-layer memory: short-term context + long-term SQLite database
- **🔍 Semantic Search** - Find past conversations using natural language queries
- **💰 Cost-Optimized Context** - Configurable message limits (5-50) to control API costs
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

### Memory Example
Shows how the chat remembers previous context:
```
/config = settings | ESC/exit = quit
─────────────────────────────────────────────────────

👤 You ▶ I need to dockerize my Node.js app
🤖 AI ▶
Create a Dockerfile with node:18-alpine base image, copy package files, run npm install, then copy your app and expose the port.
─────────────────────────────────────────────────────

👤 You ▶ show me that dockerfile
🤖 AI ▶
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
─────────────────────────────────────────────────────

👤 You ▶ what if the port is already in use?
🤖 AI ▶
Change the EXPOSE line to a different port like 3001, or kill the process using port 3000:
lsof -ti:3000 | xargs kill -9
─────────────────────────────────────────────────────

👤 You ▶
```

### DateTime Example
Shows local time awareness:
```
/config = settings | ESC/exit = quit
─────────────────────────────────────────────────────

👤 You ▶ datetime?
🤖 AI ▶
Current date and time: Saturday, September 27, 2025, at 00:26.
─────────────────────────────────────────────────────

👤 You ▶ is it late?
🤖 AI ▶
Yes, 00:26 is quite late for a Saturday night! Time for bed? 😴
─────────────────────────────────────────────────────

👤 You ▶
```

### Fun Example
Shows personality and humor:
```
/config = settings | ESC/exit = quit
─────────────────────────────────────────────────────

👤 You ▶ explain regex in simple terms
🤖 AI ▶
Regex is like a search pattern with superpowers. /\d+/ finds numbers, /[a-z]+/ finds lowercase words. It's basically "find me this weird pattern in text."
─────────────────────────────────────────────────────

👤 You ▶ why is it so cryptic?
🤖 AI ▶
Because regex was invented by people who thought hieroglyphs weren't confusing enough! 😄 But once you learn it, it's incredibly powerful for text processing.
─────────────────────────────────────────────────────

👤 You ▶
```

### Configuration
Start chat, then type `/config` to open settings menu:

```
⚙️  CONFIGURATION

┌─────────────────────────────────────
│  Current Settings:
│  ├─ Command: chat
│  ├─ Language: en
│  ├─ Context Window: 20 messages
│  └─ ESC to exit: true
├─────────────────────────────────────
│  [1] Change command character
│  [2] Change language
│  [3] Toggle ESC key exit
│  [4] Change AI model
│  [5] 💬 Set context window
│  [6] 🧹 Clear chat cache
│  [7] ℹ️  About & Version
│  [8] Back to chat
│
│  [9] 🗑️  Uninstall completely
└─────────────────────────────────────

Select [1-9]:
```

### Smart Context Window Management
Cost-optimized memory system with configurable message limits:

```
                   🧠 SMART MEMORY SYSTEM

┌─────────────────────────────────────────────────────────┐
│                  User Input                             │
└────────────────────┬────────────────────────────────────┘
                     │
              ┌──────▼──────┐
              │  Analyzer   │ (Check if relevant)
              └──────┬──────┘
                     │
          ┌──────────▼──────────┐
          │  Context Manager    │
          │  • Limit to N msgs  │
          │  • Keep last pairs  │
          │  • Cost: ~$0.01     │
          └──────────┬──────────┘
                     │
             ┌───────▼────────┐
             │   ChatGPT API  │
             │   Full Context │
             └───────┬────────┘
                     │
            ┌────────▼────────┐
            │    Response     │
            └─────────────────┘

💡 Context Window Settings:
   • 5-10 messages   = Ultra-low cost (~$0.005/msg)
   • 15-25 messages  = Balanced (~$0.01/msg)
   • 30-50 messages  = High memory (~$0.025/msg)

🎯 Default: 20 messages (perfect balance of memory + cost)
```

### 🧠 Smart Memory System (Phase 2)

AI Chat Terminal features a revolutionary dual-layer memory architecture:

```
                   🧠 DUAL-LAYER MEMORY SYSTEM

┌─────────────────────────────────────────────────────────┐
│                 SHORT-TERM MEMORY                       │
│               (Shell-GPT Context)                       │
│  • Last 5-50 messages (configurable)                   │
│  • Fast API responses                                   │
│  • Cost optimized                                      │
└────────────────────┬────────────────────────────────────┘
                     │
              ┌──────▼──────┐
              │  Auto-Save  │ (Background)
              └──────┬──────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                 LONG-TERM MEMORY                        │
│                (SQLite + Embeddings)                    │
│  • Semantic search across all conversations            │
│  • Vector embeddings for context understanding         │
│  • Persistent storage (~1KB per message)               │
│  • Automatic cleanup after 30+ days                    │
└─────────────────────────────────────────────────────────┘

🔍 Memory Search Examples:
   • "What did we discuss about Docker yesterday?"
   • "Show me Python debugging conversations"
   • "Find solutions for API timeout errors"

💾 Automatic Features:
   • Background saving (non-blocking)
   • Smart importance scoring
   • Semantic similarity search
   • Database cleanup tools
```

### Language Selection with Dialects
Shows 19 languages including regional variants:
```
Select Your Language:
  [1] 🇬🇧 English
  [2] 🇩🇪 Deutsch
  [3] 🇫🇷 Français
  [4] 🇮🇹 Italiano
  [5] 🇪🇸 Español
  [6] 🇨🇳 中文 (Mandarin)
  [7] 🇮🇳 हिन्दी (Hindi)
Select [1-7]: 2

Möchten Sie einen Dialekt?
  [1] Hochdeutsch (Standard)
  [2] Schwäbisch
  [3] Bayerisch
  [4] Sächsisch
Select [1-4]: 2

✓ Language set to: de-schwaebisch
```

## Configuration Options

The configuration menu provides these options:

1. **Change Command** - Switch between `chat`, `ai`, `ask`, `q`, or custom
2. **Change Language** - Select from 19 supported languages
3. **Toggle ESC Exit** - Enable/disable quick exit with ESC key
4. **Change AI Model** - Select OpenAI model (GPT-4o recommended)
5. **💬 Set Context Window** - Configure message limit (5-50) with cost indicators
6. **🧠 Memory System** - Search memories, view stats, cleanup old data
7. **🧹 Clear Cache** - Reset conversation history
8. **ℹ️ About & Version** - View version and attribution information
9. **Back to Chat** - Return to conversation
10. **🗑️ Uninstall** - Complete removal with cleanup

## Requirements

- **OpenAI API Key** (required) - Get yours at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Python 3** (usually pre-installed on macOS/Linux)
- **Shell-GPT** (automatically installed)
- **Memory System Dependencies** (automatically installed):
  - `sentence-transformers` (~80MB, for semantic search)
  - `sqlite-vec` (for vector embeddings in SQLite)

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