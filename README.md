# AI Chat Terminal

A ChatGPT-powered terminal interface with integrated web search and AI-powered vector database.

**🚀 Transform your terminal into an intelligent AI assistant with memory that never forgets!**

[![Version](https://img.shields.io/badge/version-5.3.0-blue.svg)](https://github.com/martinschenk/ai-chat-terminal)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20|%20Linux-lightgrey.svg)](https://github.com/martinschenk/ai-chat-terminal)

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage Examples](#usage-examples)
- [Smart Memory System](#-ai-powered-vector-database-system)
- [Configuration](#configuration-options)
- [Requirements](#requirements)
- [Supported Languages](#supported-languages)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Features

- **🤖 ChatGPT Integration** - Powered by OpenAI's latest models (GPT-4o, GPT-4o-mini, etc.)
- **🌐 Integrated Web Search** - Real-time information via ChatGPT search capabilities
- **🧠 Smart Memory System** - Dual-layer memory: short-term context + long-term SQLite database
- **🔍 AI Semantic Search** - Find past conversations using natural language queries
- **💰 Cost-Optimized Context** - Prevents token cost explosion by limiting chat history sent to API
- **🌍 Multi-Language Support** - 19 languages with regional dialects
- **⚙️ Customizable Commands** - Use `chat`, `ai`, `ask`, or custom aliases
- **🛡️ Zero Configuration** - Works out of the box on any macOS/Linux system

## Quick Start

**1-minute setup:**
```bash
# Install
curl -sL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | bash

# Reload shell
source ~/.zshrc

# Start chatting
chat
```

Then enter your [OpenAI API key](https://platform.openai.com/api-keys) and start chatting!

## Installation

```bash
curl -sL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | bash
```

**After installation:**
1. Reload your shell: `source ~/.zshrc` (or restart terminal)
2. Start the chat: `chat`
3. Enter your OpenAI API key when prompted
4. **Optional**: Choose gpt-3.5-turbo for 10x lower costs than GPT-4

## Usage Examples

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
│  [6] 🧠 Memory system
│  [7] 🧹 Clear chat cache
│  [8] ℹ️  About & Version
│  [9] Back to chat
│
│  [10] 🗑️  Uninstall completely
└─────────────────────────────────────

Select [1-10]:
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

💡 How Chat History Affects Costs:
   • Every API call sends ENTIRE chat history as context
   • 5-10 messages  = 500-1000 tokens per request = Ultra-low cost (~$0.005/msg)
   • 15-25 messages = 1500-2500 tokens per request = Balanced cost (~$0.01/msg)
   • 30-50 messages = 3000-5000 tokens per request = Higher cost (~$0.025/msg)
   • Without limits = Exponentially growing costs as conversation continues!

🎯 Default: 20 messages (perfect balance of memory + cost)
💰 Cost Protection: System automatically truncates old messages before each API call
```

### 🧠 AI-Powered Vector Database System

AI Chat Terminal features a revolutionary dual-layer memory architecture with AI-powered semantic search:

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
│           (SQLite + Vector Embeddings)                 │
│  • AI semantic search with sentence-transformers       │
│  • 384-dimensional vector embeddings                   │
│  • Understands meaning, not just keywords              │
│  • Persistent storage (~1KB per message)               │
│  • Smart cleanup: keeps important messages forever     │
└─────────────────────────────────────────────────────────┘

🔍 AI Search Examples (finds meaning, not just keywords):
   • "Docker problems" → finds "container startup issues"
   • "Python bugs" → finds "script errors", "debugging sessions"
   • "API failures" → finds "timeout errors", "connection issues"

🤖 How Vector Search Works:
   • Each message converted to 384 numbers (embedding)
   • AI model (all-MiniLM-L6-v2) understands context
   • Search finds similar meanings, not just exact words
   • Falls back to text search if AI unavailable

💾 What's Stored in Database:
   • Message content and metadata (JSON)
   • Conversation timestamps and session IDs
   • AI-generated importance scores (0.0-2.0)
   • 384-dimensional vector embeddings per message
   • Automatic background saves (non-blocking)
```

#### 🛡️ Graceful Degradation & Compatibility

**System works everywhere, even without AI features:**

- **Full AI Mode**: Vector search with semantic understanding
- **Fallback Mode**: Basic text search when AI unavailable
- **No Dependencies**: Works on any macOS/Linux regardless of system SQLite
- **Zero Setup**: Database created automatically on first use
- **Robust Error Handling**: Continues working if embeddings fail

**Why this matters:**
```bash
# Scenario 1: Full AI system (optimal)
Search: "Docker problems" → Finds: "container won't start", "image issues"

# Scenario 2: Fallback mode (still useful)
Search: "Docker" → Finds: any message containing "Docker"

# System never breaks, always provides some search functionality
```

#### 🧹 Smart Cleanup System

**Intelligent memory management that keeps what matters:**

```bash
🎯 Automatic Triggers:
   • 5000+ messages OR 50MB+ database size

🧠 Smart Deletion Priority:
   1. Low importance messages (< 1.5 score)
   2. Oldest timestamps first
   3. Never deletes: names, TODOs, important keywords

📊 Cleanup Target:
   • Reduces to 4500 messages (90% of limit)
   • Maintains optimal performance
   • Keeps important conversations forever

🔒 Protected Content:
   • Messages containing: "name", "heißt", "bin", "remember"
   • High importance scores (> 1.5)
   • Recent important conversations
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

### Required
- **OpenAI API Key** - Get yours at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Python 3** (usually pre-installed on macOS/Linux)
- **Minimum $5 OpenAI credit** (gpt-3.5-turbo recommended for cost efficiency)

### Auto-Installed Dependencies
- **Shell-GPT** - Core chat functionality
- **sentence-transformers** (~80MB) - AI semantic search
- **sqlite-vec** - Vector embeddings in SQLite
- **jq** - JSON processing

## Supported Languages

**19 languages with regional dialects:**
- **English** 🇬🇧
- **German** 🇩🇪 (+ Schwäbisch, Bayerisch, Sächsisch)
- **Spanish** 🇪🇸 (+ Mexican, Argentinian, Colombian, Venezuelan, Chilean, Andaluz)
- **Romance Languages**: French 🇫🇷, Italian 🇮🇹, Catalan, Galician
- **Regional**: Basque (Euskera)
- **Asian**: Chinese (Mandarin) 🇨🇳, Hindi 🇮🇳
- **And more** - Full list available during installation

### Language Selection with Dialects
Interactive language setup during installation:
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

## Troubleshooting

### Command already exists
If `chat` conflicts with existing commands, the installer will suggest alternatives like `ai`, `ask`, or `aic`.

### API Key Issues
Ensure your OpenAI account has sufficient credit. Start `chat` then use `/config` to update your API key.

### Shell-GPT Not Found
```bash
pip3 install --user shell-gpt
```

### Memory System Not Working
If vector search features aren't available:
```bash
pip3 install --user sentence-transformers sqlite-vec
```
The system will automatically fall back to text search if needed.

## Uninstall

Start `chat`, then type `/config` and select option 10 (Uninstall).

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