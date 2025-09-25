# 🤖 AI Chat Terminal with Memory

A beautiful interactive AI chat for your terminal that **remembers your conversation** for contextual follow-up questions.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Shell](https://img.shields.io/badge/shell-zsh-green)
![License](https://img.shields.io/badge/license-MIT-purple)
![Languages](https://img.shields.io/badge/languages-EN%20|%20DE-orange)
![Memory](https://img.shields.io/badge/memory-2%20minutes-red)

## ✨ Features

- 🧠 **CONVERSATION MEMORY** - Remembers context for 2 minutes for natural follow-ups
- 🎮 **Game-Style Menu** - Interactive menu system like a retro game
- 🎨 **Beautiful Terminal UI** - Colorful interface with emoji icons
- 🌍 **Multi-language Support** - English and German included, easily extensible
- ⚙️ **Configurable Command** - Choose your trigger character (default: `q`)
- 🚀 **Two Modes**:
  - **Quick Mode with Memory**: Ask follow-up questions naturally
  - **Interactive Mode**: Full chat experience with menu
- ⚡ **Fast & Lightweight** - Pure shell script, no heavy dependencies

## 🧠 Memory Feature Examples

### Quick Mode with Context Memory
```bash
# First question
$ q my name is John and I live in Berlin

🤖 AI: Hello John! It's nice to meet you. How are things in Berlin?

# Follow-up question - AI remembers your name and location!
$ q what's the weather like in my city?

🤖 AI: I'll check the weather for Berlin, John. Currently, Berlin is experiencing...

# Another follow-up - still remembers context!
$ q translate "hello" to the local language there

🤖 AI: In Berlin, Germany, "hello" in the local language (German) is "Hallo" or more formally "Guten Tag".
```

### Interactive Mode Shows Memory Status
```
╭═══════════════════════════════════════════╮
║     🤖 Interactive AI Chat               ║
║     💬 Continue (45s)  <-- Active memory ║
╠═══════════════════════════════════════════╣
║  [Ctrl+C] to exit                        ║
║  /menu return to menu                    ║
╰═══════════════════════════════════════════╯

👤 You ▶ I'm learning Python
🤖 AI ▶
Great! Python is an excellent language to learn. What aspect would you like to focus on?

👤 You ▶ how do I make a loop?  <-- AI knows you mean Python!
🤖 AI ▶
In Python, you can create loops using 'for' and 'while'. Here's a simple for loop:

```python
for i in range(5):
    print(i)
```
───────────────────────────────────────────
```

## 🚀 Quick Start

```bash
# Clone and install
git clone https://github.com/martinschenk/ai-chat-terminal.git
cd ai-chat-terminal
./install.sh

# Start chatting with memory!
q Remember my name is Alice
q What's my name?  # AI responds: "Your name is Alice"
```

## How Memory Works

The AI maintains your conversation context for **2 minutes** after each message. This means:

- ✅ Ask follow-up questions without repeating context
- ✅ Reference previous answers naturally
- ✅ Build complex conversations step by step
- ✅ The AI understands "it", "that", "my", etc. from context

After 2 minutes of inactivity:
- 🔄 Session resets automatically
- 🆕 Start fresh with a new topic
- 💡 Status indicator shows session state

## 📦 Installation

### Prerequisites

1. **zsh** shell (comes with macOS)
2. **Python 3.8+**
3. **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))

### Automatic Installation

The installer guides you through setup:

```bash
./install.sh
```

During installation:
- Choose your command character (default: `q`)
- Select your language (English or German)
- Enter your OpenAI API key
- Memory is automatically configured for 2 minutes

## 🎮 Usage

### Testing Memory Feature

Try this sequence to see memory in action:

```bash
# Introduction
q my favorite color is blue

# Follow-up (within 2 minutes)
q what's my favorite color?
# AI responds: "Your favorite color is blue"

# Another follow-up
q suggest a car in that color
# AI responds: "Here are some great cars that come in blue..."
```

### Interactive Mode with Menu

```bash
# Just type q to enter the game-style menu
q

     ___   ____    _____ _           _
    / _ \ |_ _|   / ____| |         | |
   / /_\ \ | |   | |    | |__   __ _| |_
   |  _  | | |   | |    | '_ \ / _` | __|
   | | | |_| |_  | |____| | | | (_| | |_
   \_| |_/\___/  \_____|_| |_|\__,_|\__|
          Terminal Edition v2.0

╔══════════════════════════════════════════════╗
║     🎮 MAIN MENU                             ║
║     💬 Continue (13s)  <-- Memory active!   ║
╠══════════════════════════════════════════════╣
║                                              ║
║  [1] 💬 Start Chat                          ║
║  [2] ⚙️  Settings                            ║
║  [3] 🌍 Language: en                        ║
║  [4] 📖 Help                                ║
║  [5] 🚪 Exit                                ║
║                                              ║
║  Command: q | Timeout: 120s                 ║
╚══════════════════════════════════════════════╝

Select option [1-5]:
```

### Memory Configuration

Change how long context is remembered:

```bash
ai-chat-config
# Select option 3 (Change timeout)
# Enter 300 for 5 minutes
# Or 60 for 1 minute
```

## ⚙️ Configuration

### Memory Settings

The memory timeout can be customized:

- **Default**: 120 seconds (2 minutes)
- **Quick chats**: 60 seconds (1 minute)
- **Long conversations**: 300 seconds (5 minutes)
- **Extended sessions**: 600 seconds (10 minutes)

Edit timeout in settings menu or manually:
```bash
echo 'AI_CHAT_TIMEOUT="300"' >> ~/.config/ai-chat/config
```

### Understanding Memory Indicators

The UI shows your memory status:

- 🚀 **New Session** - Fresh start, no memory
- 💬 **Continue (Xs)** - Active memory from X seconds ago
- 🔄 **New Chat Session** - Previous memory expired

## 🌍 Language Development

Add your language easily! The system remembers context in any language.

Create `ai-chat/languages/[code].conf`:

```bash
# Memory-aware translations
LANG_HEADER_CONTINUE="Continue"  # Shows when memory is active
LANG_STATUS_SECONDS="s"          # Time indicator
LANG_STATUS_AGO="ago"            # For "X seconds ago"
# ... other translations
```

## 🗂️ Project Structure

```
ai-chat-terminal/
├── README.md                 # This file
├── LICENSE                   # MIT License
├── install.sh               # Installation script
├── .env.example            # Example environment variables
└── ai-chat/
    ├── ai_chat.zsh        # Main function with memory management
    ├── config.sh          # Configuration loader
    └── languages/         # Language packs
        ├── en.conf        # English
        └── de.conf        # German
```

## 🔒 Security

- **No API keys in code** - Uses environment variables
- **Memory stored locally** - In `/tmp/chat_cache/`
- **Auto-cleanup** - Old sessions deleted automatically
- **Private by default** - No data sent except to OpenAI API

## 🐛 Troubleshooting

### Memory not working?

Check if cache directory exists:
```bash
ls -la /tmp/chat_cache/
```

Clear cache to reset:
```bash
rm -rf /tmp/chat_cache/q_chat*
```

### Session expires too quickly?

Increase timeout:
```bash
ai-chat-config
# Option 3 → Enter 300 (5 minutes)
```

### Test if memory works:

```bash
q my name is TestUser
sleep 3
q what is my name?
# Should respond with "TestUser"
```

## 💡 Pro Tips

### Memory Best Practices

1. **Keep conversations flowing** - Respond within 2 minutes
2. **Use references** - Say "it", "that", "the previous"
3. **Build complex queries** - Break them into steps
4. **Check status** - Look for "Continue (Xs)" indicator

### Creative Uses with Memory

```bash
# Code review with context
q review this function: def add(a,b): return a+b
q now make it handle strings too
q add error handling to it

# Language learning
q teach me Spanish colors
q how do I say the first one in a sentence?
q what about the second one?

# Story building
q start a story about a robot
q continue with the robot finding a friend
q how does it end?
```

## 📊 Performance

- ⚡ Response time: ~1-2 seconds
- 🧠 Memory overhead: <1MB per session
- 💾 Cache location: `/tmp/chat_cache/`
- 🔄 Auto-cleanup: After timeout period
- 📝 Context limit: ~100 messages per session

## 🎯 Roadmap

- [ ] Adjustable memory per session
- [ ] Export conversation history
- [ ] Memory persistence across terminal restarts
- [ ] Visual memory indicator in prompt
- [ ] Conversation branching
- [ ] Memory search/replay

## 🤝 Contributing

We especially welcome:
- Memory optimization improvements
- New language translations
- UI enhancements for memory display
- Bug fixes

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Credits

- [Shell GPT](https://github.com/TheR1D/shell_gpt) - Powers the AI backend
- OpenAI for GPT API with context management
- Contributors and translators

---

Made with ❤️ and 🧠 for the terminal community

**⭐ Star this repo if the memory feature helps you!**

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/martinschenk/ai-chat-terminal/issues)
- **Discussions**: [GitHub Discussions](https://github.com/martinschenk/ai-chat-terminal/discussions)