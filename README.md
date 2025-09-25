# 🤖 AI Chat Terminal - Instant & Simple

**Instant AI chat in your terminal with memory.** No menus, no hassle - just type and chat!

![Version](https://img.shields.io/badge/version-3.0.0-blue)
![Memory](https://img.shields.io/badge/memory-2%20minutes-red)
![Languages](https://img.shields.io/badge/languages-EN%20|%20DE-orange)
![OS](https://img.shields.io/badge/OS-macOS%20|%20Linux-green)

## 🚀 One-Line Installation

```bash
curl -sSL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | bash
```

That's it! The installer will:
- ✅ Auto-detect your shell (.zshrc/.bashrc/.profile)
- ✅ Ask for your preferred command (default: `q`)
- ✅ Set your language (English/German)
- ✅ Configure everything automatically

## 💬 Instant Chat - No Menus!

### Start chatting immediately:
```bash
q
# You're now in chat mode! Just type...
```

### Ask a quick question:
```bash
q What's the capital of France?
# Get instant answer and continue chatting
```

### The AI remembers context:
```bash
q My name is Alice
# "Hello Alice! Nice to meet you."

q What's my name?
# "Your name is Alice."
```

## ⚡ Features

- **🧠 Memory** - Remembers your conversation for 2 minutes
- **⚡ Instant** - No menus, starts immediately
- **🎮 Game-Style Config** - Type `/config` in chat for settings
- **🚪 Quick Exit** - Press `ESC` or type `exit`
- **🌍 Multi-Language** - English & German (extensible)
- **📱 Simple** - One command does everything

## 🎮 In-Chat Commands

While chatting, use these commands:

| Command | Action |
|---------|--------|
| `/config` | Open settings menu |
| `clear` | Clear screen |
| `exit` | Exit chat |
| `ESC` key | Quick exit (if enabled) |

## ⚙️ Configuration

Type `/config` while in chat to see this menu:

```
⚙️  CONFIGURATION

╔═══════════════════════════════════════╗
║  Current Settings:                   ║
║  ├─ Command: q                       ║
║  ├─ Language: en                     ║
║  ├─ Timeout: 120s                    ║
║  └─ ESC to exit: true                ║
╠═══════════════════════════════════════╣
║  [1] Change command character        ║
║  [2] Change language                 ║
║  [3] Change timeout                  ║
║  [4] Toggle ESC key exit             ║
║  [5] Change AI model                 ║
║  [6] Back to chat                    ║
╚═══════════════════════════════════════╝
```

## 📋 Requirements

- **OS**: macOS or Linux (sorry, no Windows yet)
- **Shell**: zsh, bash, or sh
- **Python**: 3.8+
- **API Key**: OpenAI API key ([get one here](https://platform.openai.com/api-keys))

## 🪟 Windows Users

Options for Windows:
1. **WSL** - Windows Subsystem for Linux (recommended)
2. **Git Bash** - May work with limitations
3. **Cygwin** - Unix-like environment for Windows

## 🔧 Manual Installation

If you prefer to see what's happening:

```bash
# 1. Clone repo
git clone https://github.com/martinschenk/ai-chat-terminal.git
cd ai-chat-terminal

# 2. Run installer
./install.sh

# 3. Reload shell
source ~/.zshrc  # or ~/.bashrc or ~/.profile

# 4. Start chatting!
q
```

## 🧩 Project Structure

Super simple - just 3 files:

```
ai-chat-terminal/
├── chat.zsh          # Main chat function
├── install.sh        # Smart installer
└── languages/        # Language packs
    ├── en.conf       # English
    └── de.conf       # German
```

## 🌍 Add Your Language

Create `languages/your-lang.conf`:

```bash
LANG_LABEL_YOU="You"
LANG_LABEL_AI="AI"
LANG_MSG_GOODBYE="Goodbye!"
LANG_HEADER_CONTINUE="Continue"
LANG_STATUS_SECONDS="s"
```

Then set it: `/config` → Option 2 → Enter your language code

## 🐛 Troubleshooting

### "Command not found"
```bash
source ~/.zshrc  # or ~/.bashrc
```

### API Key Issues
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### Test Memory Feature
```bash
q my favorite color is blue
q what's my favorite color?
# Should respond: "Your favorite color is blue"
```

## 🎯 Pro Tips

1. **Quick workflow**: `q` → chat → `ESC` to exit
2. **Context matters**: Stay within 2 minutes for memory
3. **Custom commands**: Create aliases
   ```bash
   alias code="q write code for"
   alias fix="q find the bug in"
   ```

## 📝 License

MIT - Use it, modify it, share it!

## 🙏 Credits

- Powered by [Shell GPT](https://github.com/TheR1D/shell_gpt)
- OpenAI for the API
- You for using it!

---

**⭐ If this makes your terminal smarter, star the repo!**

## Quick Start Examples

```bash
# Install (30 seconds)
curl -sSL https://raw.githubusercontent.com/martinschenk/ai-chat-terminal/main/install.sh | bash

# Configure your shell
source ~/.zshrc

# Start chatting
q

# That's it! You're chatting with AI!
```