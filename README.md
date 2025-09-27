# AI Chat Terminal

A ChatGPT-powered terminal interface with integrated web search and AI-powered vector database.

**🚀 Transform your terminal into an intelligent AI assistant with memory that never forgets!**

[![Version](https://img.shields.io/badge/version-5.3.0-blue.svg)](https://github.com/martinschenk/ai-chat-terminal)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20|%20Linux-lightgrey.svg)](https://github.com/martinschenk/ai-chat-terminal)

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage Examples](#usage-examples)
- [Smart Memory System](#-ai-powered-vector-database-system)
- [Configuration](#configuration-options)
- [Supported Languages](#supported-languages)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Features

- **🤖 ChatGPT Integration** - Powered by OpenAI's latest models (GPT-4o, GPT-4o-mini, etc.)
- **🌐 Integrated Web Search** - Real-time information via ChatGPT search capabilities
- **🧠 Smart Memory System** - Dual-layer memory: short-term context + long-term SQLite database
- **🔍 AI Semantic Search** - Find past conversations using natural language queries
- **🔒 Transparent Privacy System** - Personal data stays local; OpenAI never sees sensitive information
- **🌐 Cross-Language Search** - Query in any language, find content in any other with multilingual E5 model
- **🗣️ Language Detection** - Automatic detection and storage per message for all 19 supported languages
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

## Requirements

### Required
- **OpenAI API Key** - Get yours at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Python 3** (usually pre-installed on macOS/Linux)
- **Minimum $5 OpenAI credit** (gpt-3.5-turbo recommended for cost efficiency)

### Auto-Installed Dependencies
- **OpenAI Python SDK** - Direct API integration
- **sentence-transformers** (~80MB) - AI semantic search
- **sqlite-vec** - Vector embeddings in SQLite
- **jq** - JSON processing

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

### Personal Memory Example
Shows how AI remembers your preferences and details:
```
/config = settings | ESC/exit = quit
─────────────────────────────────────────────────────

👤 You ▶ My name is Sara
🤖 AI ▶
Nice to meet you, Sara! I'll remember that.
─────────────────────────────────────────────────────

# Days later...

👤 You ▶ What's my name?
🤖 AI ▶
Your name is Sara! How can I help you today?
─────────────────────────────────────────────────────

👤 You ▶
```

### Everyday Help Example
AI assistance with daily tasks and planning:
```
/config = settings | ESC/exit = quit
─────────────────────────────────────────────────────

👤 You ▶ I need to plan a birthday party for my 8-year old
🤖 AI ▶
Fun! Here's a simple party plan for an 8-year-old:

🎂 **Food**: Pizza, cake, juice boxes, fruit
🎮 **Activities**: Musical chairs, treasure hunt, crafts station
🎁 **Party favors**: Small toys, stickers, candy bags
⏰ **Duration**: 2-3 hours is perfect for this age

What's their favorite theme or character?
─────────────────────────────────────────────────────

👤 You ▶ She loves unicorns!
🤖 AI ▶
Perfect! Unicorn theme ideas:
- Pink/purple decorations with rainbow colors
- Unicorn cake or cupcakes with horns
- "Pin the horn on the unicorn" game
- Unicorn headbands as party favors
- Face painting with glitter and rainbows

Would you like specific recipes or decoration ideas?
─────────────────────────────────────────────────────

👤 You ▶
```

### Quick Help Example
Get instant answers to everyday questions:
```
/config = settings | ESC/exit = quit
─────────────────────────────────────────────────────

👤 You ▶ what's a good recipe for chocolate chip cookies?
🤖 AI ▶
Here's a simple recipe:

**Ingredients:**
- 2¼ cups flour
- 1 cup butter, softened
- ¾ cup each: brown & white sugar
- 2 eggs, 2 tsp vanilla
- 1 tsp baking soda, 1 tsp salt
- 2 cups chocolate chips

**Steps:** Mix wet ingredients, add dry ingredients, fold in chips,
bake at 375°F for 9-11 minutes. Makes about 48 cookies!
─────────────────────────────────────────────────────

👤 You ▶ how do I know when they're done?
🤖 AI ▶
Look for golden brown edges but centers still look slightly underbaked.
They'll continue cooking on the hot pan for a few minutes after removing
from oven. This gives you that perfect chewy texture!
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


### 🧠 AI-Powered Vector Database System

AI Chat Terminal features a revolutionary dual-layer memory architecture with multilingual AI-powered semantic search:

```
                   🧠 DUAL-LAYER MEMORY SYSTEM

┌─────────────────────────────────────────────────────────┐
│                 SHORT-TERM MEMORY                       │
│               (Python Chat System)                     │
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
│  • AI semantic search with multilingual E5 model      │
│  • 384-dimensional vector embeddings                   │
│  • Cross-language search across 19 supported languages│
│  • Language detection per message                      │
│  • Understands meaning, not just keywords              │
│  • Persistent storage (~1KB per message)               │
│  • Smart cleanup: keeps important messages forever     │
└─────────────────────────────────────────────────────────┘

🔍 AI Search Examples (finds meaning, not just keywords):
   • "Docker problems" → finds "container startup issues"
   • "Python bugs" → finds "script errors", "debugging sessions"
   • "API failures" → finds "timeout errors", "connection issues"

🌐 Cross-Language Search Magic:
   • Query in English: "Docker problems" → finds German: "Docker Container Probleme"
   • Query in German: "Python Fehler" → finds English: "Python script errors"
   • UI in English, chat in German → search works perfectly across languages

🤖 How Multilingual Vector Search Works:
   • Each message converted to 384 numbers (embedding)
   • AI model (multilingual-e5-small) understands context across 19 languages
   • Search finds similar meanings, not just exact words
   • Language detection per message enables cross-language search
   • Falls back to text search if AI unavailable

💾 What's Stored in Database:
   • Message content and metadata (JSON)
   • Conversation timestamps and session IDs
   • AI-generated importance scores (0.0-2.0)
   • Language detection per message (19 supported languages)
   • 384-dimensional vector embeddings per message
   • Universal human memory keywords (150+ per language)
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

#### 🔒 Transparent Privacy System

**Your personal data never leaves your computer - here's how we guarantee it:**

```
🔐 PRIVACY-FIRST ARCHITECTURE

┌─────────────────────────────────────────────────────┐
│                  YOUR QUESTION                      │
│          "What's my phone number?"                  │
└─────────────────┬───────────────────────────────────┘
                  │
          ┌───────▼──────┐
          │  To OpenAI:  │
          │  Question +  │ ← Only question + template instruction
          │  Template    │   NO personal data sent!
          └───────┬──────┘
                  │
       ┌──────────▼──────────┐
       │   OpenAI Response:  │
       │   {{SEARCH_DB}}     │ ← Template instead of refusal
       └──────────┬──────────┘
                  │
    ┌─────────────▼─────────────┐
    │    LOCAL DB SEARCH        │
    │  Uses YOUR question to    │ ← Searches local SQLite only
    │  find YOUR stored data    │   OpenAI never sees results!
    └─────────────┬─────────────┘
                  │
       ┌──────────▼──────────┐
       │    YOUR ANSWER:     │
       │   "669686832"       │ ← Complete data from local storage
       └─────────────────────┘
```

**What OpenAI sees vs. what stays local:**

| OpenAI Sees | Stays Local Only |
|-------------|------------------|
| ✅ "What's my phone number?" | ❌ Actual phone number |
| ✅ Template: `{{SEARCH_DB}}` | ❌ Your personal data |
| ✅ System instructions | ❌ Database contents |
| ✅ Public conversation context | ❌ Sensitive information |

**Technical Implementation:**
- **Step 1**: User asks for sensitive info
- **Step 2**: OpenAI gets question + template system (no personal data)
- **Step 3**: OpenAI responds with `{{SEARCH_DB}}` instead of refusing
- **Step 4**: Our system searches local database with original question
- **Step 5**: Template gets replaced with actual data from your local storage

**Why this matters:**
- Your phone numbers, emails, addresses stay on YOUR computer only
- OpenAI's safety training can't block access to YOUR own data
- Complete transparency: you control what gets stored and retrieved
- Works for any type of personal information, not just predefined categories


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

### OpenAI SDK Not Found
```bash
pip3 install --user openai requests
```

### Memory System Not Working
If vector search features aren't available:
```bash
pip3 install --user sentence-transformers sqlite-vec
```
The system will automatically fall back to text search if needed.

### urllib3 SSL Warning (macOS)
If you see `NotOpenSSLWarning` about LibreSSL compatibility:
- This is a cosmetic warning only - functionality works correctly
- The warning is automatically suppressed in v5.4.0+
- More info: [urllib3/urllib3#3020](https://github.com/urllib3/urllib3/issues/3020)

### Uninstall
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

Direct OpenAI API integration with native Python implementation.